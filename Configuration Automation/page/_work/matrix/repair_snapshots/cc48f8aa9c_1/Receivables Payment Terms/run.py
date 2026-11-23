"""Manage Receivables Payment Terms (AR_MANAGE_RECEIVABLES_PAYMENT_TERMS): new terms with their installments,
discounts and base-language name, through Oracle's setup task process without a browser (as Business Units).

  python "Receivables Payment Terms/run.py" --check                     # read-only: layout, sets, language
  python "Receivables Payment Terms/run.py" --plan '<JSON list or one request>'      # read-only, the preview
  python "Receivables Payment Terms/run.py" --run-batch '<JSON list>'   # every term of an upload in one go
  python "Receivables Payment Terms/run.py" --spec | --options FIELD | --run '<JSON>'   # page interface
  python "Receivables Payment Terms/run.py"                             # the terms in request.json

Order, the same for --plan and --run-batch (nothing is sent for a term unless all its checks pass):
  1. rules without Oracle (rpt_rules.py: name 15, sums, due dates, discounts, the choices never defaulted);
  2. read-only Oracle reads: the task's own empty template (setupTaskCSVTemplateExports; the data file as
     fallback), the task's data file (existing names, the base language), the reference data sets;
  3. --run-batch only: the names read again from a fresh data file, ONE file of all new terms built from the
     pod's template (rpt_package.py) and sent as a setup task process (setupTaskCSVImports, Basic auth), Oracle's
     result and log read, and every sent term compared field by field with a fresh data file (other terms
     unchanged). Never sent twice: after a timeout or an unknown result the read-back decides.
If Oracle refuses the setup task process for this task, the run stops with a plain message; no other route is
tried (CLAUDE.md > Route status).
"""
import argparse
import base64
import collections
import contextlib
import difflib
import json
import sys
import time
from datetime import timedelta
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE)]
from common import oracle, page  # noqa: E402

import rpt_package as pkg  # noqa: E402
import rpt_rules as rules  # noqa: E402

TASK = pkg.TASK
WHERE = ("Setup and Maintenance > Financials > Customer Billing > Manage Receivables Payment Terms, search for "
         "{name} (set {set})")
WHAT = "Receivables payment term"


class RouteRefused(Exception):
    """Oracle refused the setup task process for this task (HTTP error on the call itself)."""

    def __init__(self, text, http=None):
        super().__init__(text)
        self.http = http


# ---------------------------------------------------------------- Oracle (read-only except send)

class Pod:
    """Every Oracle call of the folder. page/matrix/stub_receivables.py replaces it with saved pod files."""

    def __init__(self):
        self.today_value = None
        self.template_source = None

    def host(self):
        return oracle.HOST or ""

    def sets(self):
        """[(code, name)] of Oracle's reference data sets (setIdSetsLOV, GET); also Oracle's today."""
        r = oracle.call("GET", f"{oracle.API_BASE}/setIdSetsLOV", params={"onlyData": "true", "limit": 500})
        self.today_value = oracle.server_date(r)
        return sorted((i["SetCode"], i.get("SetName") or i["SetCode"]) for i in r.json().get("items", []))

    def today(self):
        if self.today_value is None:
            self.sets()
        return self.today_value

    def template(self):
        """The task's own empty template (setupTaskCSVTemplateExports, the resource FSCR's export engine uses).
        None when Oracle refuses it or it doesn't finish (the caller then uses the data file's layout)."""
        proc = f"{oracle.API_BASE}/setupTaskCSVTemplateExports/{TASK}/child/SetupTaskCSVTemplateExportProcess"
        r, err = oracle.try_call("POST", proc, json={"TaskCode": TASK}, timeout=120)
        pid = (r.json() if r is not None and r.ok else {}).get("ProcessId")
        if err or pid is None:
            print(f"  template not available: {(err or r.text)[:300]}")
            return None
        result = f"{proc}/{pid}/child/SetupTaskCSVTemplateExportProcessResult/{pid}"
        status = oracle.poll_result(result, "template").get("StatusCode")
        if status != "COMPLETED":
            print(f"  template ended {status}")
            return None
        data = oracle.call("GET", f"{result}/enclosure/FileContent").content
        oracle.save_work_file(data, TASK, "template")
        return data

    def export(self, tag):
        return oracle.export_task(TASK, tag)[0]

    def send(self, zip_bytes):
        """The setup task process (setupTaskCSVImports, as Business Units). Returns the process number;
        RouteRefused when Oracle refuses the call itself."""
        proc, _ = oracle.process_urls("Import", TASK, 0)
        r, err = oracle.try_call("POST", proc, json={"TaskCode": TASK, "FileContent": base64.b64encode(zip_bytes).decode(),
                                                     "SourceTargetDiffOkFlag": True}, timeout=300)
        if err:
            raise RouteRefused(err, r.status_code if r is not None else None)
        pid = r.json().get("ProcessId")
        if pid is None:
            raise RouteRefused(f"Oracle gave no process number: {r.text[:500]}")
        return pid

    def wait(self, pid):
        """(status, Oracle's log texts) of a sent process (polled every 10 s, 30-minute limit)."""
        _, result_url = oracle.process_urls("Import", TASK, pid)
        result = oracle.poll_result(result_url, "Receivables payment terms")
        texts = []
        for link in result.get("links", []):
            if link.get("rel") == "enclosure" and link.get("name") in ("ProcessLog", "ProcessResultsReport",
                                                                        "ProcessResultsSummaryReport"):
                rr, err = oracle.try_call("GET", link["href"], timeout=180)
                if err or rr is None:
                    continue
                (oracle.WORK_DIR / f"{TASK}_{pid}_{link['name']}").write_bytes(rr.content)
                texts += pkg.unpack(rr.content)
        return result.get("StatusCode"), texts


# ---------------------------------------------------------------- the check before Create

class Item:
    """One requested term: the checked Term, its problems, and what Oracle has."""

    def __init__(self, req, index):
        self.req, self.index = req, index
        self.name = req.get("name") if isinstance(req, dict) else None
        self.set = str(req.get("set_code") or "").strip() if isinstance(req, dict) else ""
        self.term, self.problems = None, []
        self.status = None              # new | exists | problems
        self.found, self.oracle = {}, {}
        self.rows = None                # {entity: [rows]} built for the file


class Plan:
    def __init__(self):
        self.items, self.layout, self.before, self.sets, self.language = [], None, None, [], None
        self.notes, self.today = [], None


def layout_of(pod, data_bytes):
    """The pod's layout: its own template, else the data file's (the evidence shows both identical). Checks the task,
    the pod (ProcessEnv in the host) and that the template's release is the data file's."""
    lay_d, rows = pkg.read_rows(data_bytes)
    tpl = pod.template()
    if tpl is None:
        pod.template_source = "data"
        lay = lay_d
    else:
        pod.template_source = "template"
        lay = pkg.read_layout(tpl)
        if lay.release != lay_d.release:
            raise pkg.LayoutError(f"the template is release {lay.release}, the data file {lay_d.release}")
        for d in pkg.same_layout(lay, lay_d):
            print(f"  note: template and data file differ: {d}; the template is followed")
    env = (lay.env or "").lower()
    if env and env not in pod.host().lower():
        raise pkg.LayoutError(f"the file is from pod {lay.env}, but this project points at another one")
    return lay, rows


def close(word, choices, n=8):
    low = {c.lower(): c for c in choices}
    return [low[m] for m in difflib.get_close_matches(str(word).lower(), list(low), n=n, cutoff=0.4)]


def plan(reqs, pod):
    """Every check before Create, read-only. Raises pkg.LayoutError or SystemExit (Oracle couldn't be read)."""
    p = Plan()
    p.sets = pod.sets()
    oracle_today = pod.today()
    p.today = oracle_today - timedelta(days=1) if oracle_today else None
    for i, r in enumerate(reqs):
        it = Item(r, i)
        it.term, it.problems = rules.check(r, p.today)
        p.items.append(it)
    seen = {}
    for it in p.items:                               # the same name twice in one upload
        if not it.name:
            continue
        if it.name in seen:
            first = seen[it.name]
            text = (f"'{it.name}' is listed twice for set {it.set}." if first.set == it.set else
                    f"'{it.name}' is listed twice (sets {first.set} and {it.set}). Installment rows join a term by its "
                    "name only, so upload these two separately.")
            it.problems.append({"key": "name", "row": None, "text": text, "fix": "Keep one of the two rows, or give "
                                "one another name.", "field": "name", "value": it.name, "suggestions": []})
            it.term = None
        else:
            seen[it.name] = it
    data = pod.export("before")
    p.layout, p.before = layout_of(pod, data)
    p.template_source = pod.template_source
    existing = pkg.terms_in(p.before)
    langs = pkg.languages(p.before)
    p.language = langs[0] if len(langs) == 1 else None
    codes = [c for c, _ in p.sets]
    ar_sets = sorted({k[1] for k in existing})
    for it in p.items:
        key = (it.name, it.set)
        if it.set and it.set not in codes:
            hit = [c for c in codes if c.lower() == it.set.lower()]
            sugg = hit + [c for c in ar_sets if c not in hit] + [c for c in close(it.set, codes) if c not in hit + ar_sets]
            it.problems.append({"key": "set_code", "row": None,
                                "text": f"Set Code '{it.set}' isn't one of Oracle's reference data sets.",
                                "fix": "Pick one of: " + ", ".join((sugg or codes)[:12]) + ".", "field": "set_code",
                                "value": it.set, "suggestions": (sugg or codes)[:12]})
            it.term = None
        elif it.set and it.set not in ar_sets:
            it.found["set_code"] = (f"No Receivables payment term uses set {it.set} yet; Oracle decides at Create "
                                    "whether this set can hold one.")
        if it.name and key in existing:
            it.status = "exists"
            continue
        near = sorted(n for (n, s) in existing if s == it.set and it.name and n != it.name
                      and " ".join(n.split()).lower() == " ".join(it.name.split()).lower())
        if near:
            it.found["name"] = (f"Oracle has '{near[0]}' in set {it.set}, which differs only in capitals or spaces. "
                                "This one will be a new term.")
        if p.language is None:
            it.problems.append({"key": "language", "row": None,
                                "text": "Oracle's language for payment term names couldn't be decided (it has "
                                        + ("none" if not langs else f"several: {', '.join(langs)}")
                                        + "). Nothing will be created.",
                                "fix": "Tell your Oracle administrator; the sheet has no language column yet.",
                                "field": "language", "value": None, "suggestions": langs})
            it.term = None
        it.status = "problems" if it.problems else "new"
        if it.status == "new":
            it.rows = pkg.term_rows(it.term, p.language)
            names = dict(p.sets)
            it.oracle = {"set_code": f"{it.set} ({names[it.set]})" if names.get(it.set, it.set) != it.set else it.set}
    return p


def plan_results(p):
    """The page's --plan answer per term (page/server.py apply_oracle_check)."""
    out = []
    names = dict(p.sets)
    for it in p.items:
        res = {"name": it.name, "ok": True, "status": it.status,
               "problems": [dict(x) for x in it.problems], "skipped": None, "found": dict(it.found),
               "fills": {}, "oracle": dict(it.oracle), "summary": None}
        if it.status == "exists":
            res["skipped"] = (f"A {WHAT} '{it.name}' already exists in set {it.set}. It will be skipped; nothing is "
                              "changed.")
            res["found"]["name"] = res["skipped"]
        elif it.term:
            res["fills"] = dict(it.term.filled)
            res["summary"] = rules.describe(it.term, p.language, names.get(it.set))
            if pod_note(p):
                res["summary"] += " " + pod_note(p)
        out.append(res)
    return out


def pod_note(p):
    return ("Oracle's empty template wasn't available, so its layout was read from Oracle's current data file."
            if getattr(p, "template_source", None) == "data" else "")


# ---------------------------------------------------------------- results

def failed(code, text, saved, problems=None, message=None):
    return {"ok": False, "text": text, "error": {"code": code, "detail": {
        "message": message, "saved": saved, "registry_id": None, **({"problems": problems} if problems else {})}}}


def shown(rows):
    """What Oracle shows now for one term, in the sheet's words (the result card)."""
    h = rows[pkg.ENTITIES["header"]][0] if rows.get(pkg.ENTITIES["header"]) else {}
    lab = lambda c: rules.LABEL.get(h.get(c), h.get(c))
    return {"name": h.get("Name"), "set_code": h.get("SetCode"), "description": h.get("Description") or None,
            "from_date": (h.get("StartDateActive") or "").replace("/", "-") or None,
            "to_date": (h.get("EndDateActive") or "").replace("/", "-") or None,
            "base_amount": h.get("BaseAmount"), "print_lead_days": h.get("PrintingLeadDays") or None,
            "tax_freight": lab("FirstInstallmentCode"), "discount_basis": lab("CalcDiscountOnLinesFlag"),
            "discount_date_basis": lab("DiscountBasisDateType"),
            "installments": [{"sequence": l.get("SequenceNum"), "relative_amount": l.get("RelativeAmount"),
                              **{k: l[c] for c, k in (("DueDays", "days"), ("DueDate", "fixed_date"),
                                                      ("DueDayOfMonth", "day_of_month"),
                                                      ("DueMonthsForward", "months_ahead")) if l.get(c)}}
                             for l in rows.get(pkg.ENTITIES["line"], [])],
            "discounts": [{"installment": d.get("AR_PAYMENT_TERM_LINE.SequenceNum"), "percent": d.get("DiscountPercent"),
                           **{k: d[c] for c, k in (("DiscountDays", "days"), ("DiscountDate", "fixed_date"),
                                                   ("DiscountDayOfMonth", "day_of_month")) if d.get(c)}}
                          for d in rows.get(pkg.ENTITIES["discount"], [])]}


def rows_of(rows, key):
    return {e: [r for r in rows.get(e, []) if pkg.key_of(r) == key] for e in pkg.ENTITIES.values()}


def suggestions_for(field, it, p):
    if field == "set_code":
        used = sorted({k[1] for k in pkg.terms_in(p.before)})
        return [c for c in used if c != it.set] + [c for c, _ in p.sets if c not in used and c != it.set][:8]
    if field == "name" and it.name:
        return [it.name[:rules.NAME_MAX].rstrip()] if len(it.name) > rules.NAME_MAX else []
    if field == "print_lead_days":
        return ["1", "2"]
    if field == "tax_freight":
        return [rules.LABEL["INCLUDE"], rules.LABEL["ALLOCATE"]]
    if field == "discount_basis":
        return [rules.LABEL["I"], rules.LABEL["L"]]
    if field in ("months_ahead",) or field.endswith("months_ahead"):
        return ["0", "1"]
    return []


def refusal_problems(it, fail, p):
    """Oracle's reason for a refused term -> the page's structured problem for the decision panel ([] when it names
    no value the user can change; the page then asks Claude for a proposal)."""
    field = fail.get("field") if fail else None
    if not field:
        return []
    why = "; ".join(fail["reasons"])
    req = it.req
    if fail.get("child"):
        rows = req.get("installments") or []
        n = next((k for k, r in enumerate(rows, 1) if isinstance(r, dict) and r.get(field) not in (None, "")), 1)
        value = (rows[n - 1] or {}).get(field) if rows else None
        return [{"field": field, "value": value, "reason": why, "text": why,
                 "suggestions": suggestions_for(field, it, p), "rows": "installments", "row": n,
                 "where": f"Installment {n}"}]
    return [{"field": field, "value": req.get(field), "reason": why, "text": why,
             "suggestions": suggestions_for(field, it, p)}]


def result_of(it, p, outcome):
    o = outcome or {}
    key = (it.name, it.set)
    where = WHERE.format(name=it.name, set=it.set)
    if it.status == "problems":
        return failed("INVALID_REQUEST", " ".join(x["text"] for x in it.problems) + " Nothing was sent for it.", "no",
                      problems=[x for x in it.problems])
    if it.status == "exists" or o.get("meanwhile"):
        rows = rows_of(p.before, key)
        return {"ok": True, "skipped": True, "where": where, "created": shown(rows),
                "text": f"The {WHAT} {it.name} is already in set {it.set} in Oracle"
                        + (" (made while this run was checking)" if o.get("meanwhile") else "")
                        + ", so it was skipped; nothing was changed."}
    if o.get("route"):
        return failed(o["route"]["code"], o["route"]["text"], "no", message=o["route"]["detail"])
    if o.get("unknown"):
        return failed(o["unknown"]["code"], o["unknown"]["text"], "maybe", message=o["unknown"]["detail"])
    rec = o.get("check") or {}
    if not rec.get("saved"):
        why = "; ".join(o["fail"]["reasons"]) if o.get("fail") else \
            "it isn't in Oracle after the run, and Oracle's log names no reason"
        return failed("INVALID_REQUEST", f"Oracle refused the {WHAT} {it.name}: {why}. Nothing was saved in Oracle.",
                      "no", problems=refusal_problems(it, o.get("fail"), p), message=why)
    if rec.get("diffs"):
        return failed("VERIFY_FAILED", f"The {WHAT} {it.name} was saved in Oracle, but not as sent: "
                      + "; ".join(rec["diffs"][:8]) + ".", "yes", message="; ".join(rec["diffs"]))
    n, d = len(it.term.lines), sum(len(ln["discounts"]) for ln in it.term.lines)
    text = (f"Created the {WHAT} {it.name} in set {it.set} with {n} installment{'s' if n != 1 else ''}"
            + (f" and {d} discount{'s' if d != 1 else ''}" if d else "")
            + ", and checked it in Oracle: every value as sent.")
    if rec.get("notes"):
        text += " " + "; ".join(rec["notes"]) + "."
    return {"ok": True, "where": where, "text": text, "created": shown(rows_of(o["after"], key))}


# ---------------------------------------------------------------- Create

def create(p, pod, progress):
    """One file for every new term, sent once, read back. {(name, set): outcome}."""
    out = {}
    new = [it for it in p.items if it.status == "new"]
    if not new:
        return out
    progress.step("checking", 40, "Reading the names again just before sending")
    lay_now, now = pkg.read_rows(pod.export("names"))
    existing = pkg.terms_in(now)
    for it in list(new):
        if (it.name, it.set) in existing:          # made meanwhile: never sent twice
            out[(it.name, it.set)] = {"meanwhile": True}
            new.remove(it)
    p.before = now
    if not new:
        return out
    rows = collections.defaultdict(list)
    for it in new:
        for e, rs in it.rows.items():
            rows[e] += rs
    data = pkg.build_zip(p.layout, rows)
    oracle.save_work_file(data, TASK, "send")
    progress.step("creating", 50, f"Sending {len(new)} new term{'s' if len(new) != 1 else ''} to Oracle in one go")
    try:
        pid = pod.send(data)
    except RouteRefused as e:
        code = "NO_PERMISSION" if e.http in (401, 403) else "SETUP_NEEDED"
        text = ("Oracle refused the setup task process for Receivables payment terms"
                + (f" (HTTP {e.http})" if e.http else "") + ". Nothing was created. This way of creating them isn't "
                "proven for this task yet, and no other way was tried.")
        print(f"ROUTE REFUSED: {e}")
        for it in new:
            out[(it.name, it.set)] = {"route": {"code": code, "text": text, "detail": str(e)[:1500]}}
        return out
    print(f"  process {pid}")
    status, texts, wait_error = None, [], None
    try:
        status, texts = pod.wait(pid)
    except (SystemExit, Exception) as e:  # noqa: BLE001 - never sent again; the read-back decides
        wait_error = str(e) or type(e).__name__
        print(f"  waiting for process {pid} stopped: {wait_error}")
    print(f"  Oracle's result: {status}")
    fails = pkg.log_failures(texts, [it.name for it in new])
    progress.step("verifying", 85, "Reading the terms back from Oracle")
    try:
        _, after = pkg.read_rows(pod.export("after"))
    except (SystemExit, Exception) as e:  # noqa: BLE001
        msg = str(e) or type(e).__name__
        code = page._classify(wait_error or msg)
        for it in new:
            out[(it.name, it.set)] = {"unknown": {"code": code, "detail": msg[:1500],
                                                  "text": f"The {WHAT} {it.name} may have been saved in Oracle; reading "
                                                          "it back didn't finish. A rerun skips it if it is there."}}
        return out
    sent = {(it.name, it.set): it.rows for it in new}
    checks, changed = pkg.reconcile(p.layout, sent, now, after)
    if changed:
        print(f"  NOTE: other terms changed during the run: {', '.join(changed)}")
        p.notes.append(f"Oracle also shows changes on other terms during this run: {', '.join(changed)}.")
    refused = [it for it in new if not checks[(it.name, it.set)]["saved"]]
    unnamed = [f for f in fails if f["term"] is None]           # blocks that quote no sent name
    unclaimed = [it for it in refused if not any(f["term"] == it.name for f in fails)]
    for it in new:
        key = (it.name, it.set)
        mine = [f for f in fails if f["term"] == it.name]
        if not mine and unnamed and unclaimed == [it]:
            mine = unnamed                     # the one refused term the log doesn't name: those reasons are its own
        fail = None
        if mine:
            fail = {"reasons": [r for f in mine for r in f["reasons"]], "field": next((f["field"] for f in mine
                                                                                        if f["field"]), None),
                    "child": any(f["child"] for f in mine if f["field"])}
        elif it in unclaimed and unnamed:      # several unnamed refusals: quoted, never guessed per term
            fail = {"reasons": ["Oracle's log, which doesn't say which term: "
                                + "; ".join(r for f in unnamed for r in f["reasons"])], "field": None, "child": False}
        out[key] = {"check": checks[key], "fail": fail, "after": after}
    return out


# ---------------------------------------------------------------- commands

def read_requests(arg):
    raw = json.loads(Path(arg).read_text(encoding="utf-8") if arg.endswith(".json") and Path(arg).exists() else arg)
    if isinstance(raw, dict) and "terms" in raw:
        raw = raw["terms"]
    return raw if isinstance(raw, list) else [raw]


POD = Pod


def plan_command(argv):
    """--plan '<JSON>' (read-only): {"ok", "text", "results": [{"name", "ok", "status", "problems": [{"key", "row",
    "text", "fix", ...}], "skipped", "found", "fills", "oracle", "summary"}]}."""
    out = sys.stdout
    try:
        reqs = read_requests(argv[1] if len(argv) > 1 else str(HERE / "request.json"))
    except (ValueError, OSError) as e:
        print(json.dumps({"ok": False, "text": f"The request couldn't be read ({e})."}), file=out)
        return 2
    pod = POD()
    with contextlib.redirect_stdout(sys.stderr):
        oracle.check_environment()
        oracle.init_work_dir(HERE)
        try:
            p = plan(reqs, pod)
            p.template_source = pod.template_source
        except pkg.LayoutError as e:
            print(f"LAYOUT: {e}")
            print(json.dumps({"ok": False, "text": pkg.LAYOUT_TEXT, "detail": e.why}), file=out)
            return 1
        except SystemExit as e:
            print(json.dumps({"ok": False, "text": "Oracle couldn't be read just now for Receivables payment terms.",
                              "detail": str(e)[:500]}), file=out)
            return 1
        oracle.cleanup_work_dir()
    p.template_source = pod.template_source
    c = collections.Counter(it.status for it in p.items)
    print(json.dumps({"ok": True, "text": f"{c['new']} new, {c['exists']} already in Oracle, {c['problems']} with "
                      "problems (nothing was changed in Oracle).", "language": p.language,
                      "layout": {"source": p.template_source, "order": p.layout.order(), "release": p.layout.release},
                      "results": plan_results(p)}, ensure_ascii=False, default=str), file=out)
    return 0


def run_batch(reqs, out):
    """Every term of an upload in one call. Progress lines, then {"step": "result", "ok", "text", "results"}."""
    progress = page.Progress(out)
    t0, pod = time.time(), POD()
    top_error, outcome, p = None, {}, None
    with contextlib.redirect_stdout(sys.stderr):
        progress.step("reading")
        oracle.check_environment()
        oracle.init_work_dir(HERE)
        messages, real_fail = [], oracle.fail

        def fail(message):
            messages.append(str(message))
            real_fail(message)
        oracle.fail = fail
        try:
            progress.step("checking", 20, "Checking every Receivables payment term with Oracle")
            p = plan(reqs, pod)
            for it in p.items:
                print(f"  {it.name} ({it.set}): {it.status}" + "".join(f"; {x['text']}" for x in it.problems))
            outcome = create(p, pod, progress)
        except pkg.LayoutError as e:
            top_error = {"code": "SETUP_NEEDED", "step": "checking", "detail": e.why, "text": pkg.LAYOUT_TEXT}
            print(f"LAYOUT: {e}")
        except (SystemExit, Exception) as e:  # noqa: BLE001 - answered per term below
            msg = messages[-1] if messages else f"{type(e).__name__}: {e}"
            top_error = {"code": page._classify(msg), "step": "checking", "detail": msg[:1500]}
            print(f"STOPPED: {msg[:1500]}")
        finally:
            oracle.fail = real_fail
        results = []
        for i, r in enumerate(reqs):
            it = p.items[i] if p and i < len(p.items) else Item(r, i)
            if top_error and (it.name, it.set) not in outcome and it.status != "problems":
                results.append(failed(top_error["code"], top_error.get("text") or (
                    page.ERRORS.get(top_error["code"], page.ERRORS["FAILED"]) + " Nothing was sent to Oracle."), "no",
                    message=top_error["detail"]))
            else:
                results.append(result_of(it, p, outcome.get((it.name, it.set))))
        progress.step("done")
    made = sum(1 for r in results if r["ok"] and not r.get("skipped"))
    skipped = sum(1 for r in results if r.get("skipped"))
    bad = sum(1 for r in results if not r["ok"])
    text = (f"Created {made} of {len(results)} Receivables payment terms" + (f", {skipped} already there" if skipped
                                                                              else "")
            + (f", {bad} not created" if bad else "") + ".")
    text = page.plain_check(text, "result") + ("".join(" " + n for n in p.notes) if p and p.notes else "")
    print(f"Whole run: {int(time.time() - t0)} s", file=sys.stderr)
    if not bad and not top_error:
        oracle.cleanup_work_dir()
    line = {"step": "result", "percent": 100, "ok": not bad, "text": text, "results": results}
    route = next((o["route"] for o in outcome.values() if o.get("route")), None)
    if top_error or route:
        e = top_error or {"code": route["code"], "step": "creating", "detail": route["detail"]}
        line["error"] = {k: e[k] for k in ("code", "step", "detail")}
    print(json.dumps(line, ensure_ascii=False, default=str), file=out)
    return 0 if not bad else 1


def run_batch_command(argv):
    try:
        reqs = read_requests(argv[1] if len(argv) > 1 else "")
        if not all(isinstance(r, dict) for r in reqs):
            raise ValueError("a list of requests is needed")
    except (ValueError, OSError) as e:
        print(json.dumps({"step": "result", "percent": 100, "ok": False, "text": "The request could not be read.",
                          "error": {"code": "INVALID_REQUEST", "step": "reading", "detail": str(e)}}))
        return 2
    return run_batch(reqs, sys.stdout)


def check_command():
    """--check (read-only): the template, the data file, the sets and the language; nothing is created."""
    pod = POD()
    oracle.check_environment()
    oracle.init_work_dir(HERE)
    try:
        sets = pod.sets()
        lay, rows = layout_of(pod, pod.export("check"))
    except pkg.LayoutError as e:
        print(f"CHECK FAILED: {e}")
        return 1
    print(f"Oracle's today: {pod.today()}; {len(sets)} reference data sets")
    print(f"layout from the {pod.template_source}: release {lay.release}, pod {lay.env}, entity order {lay.order()}")
    print(f"{len(pkg.terms_in(rows))} Receivables payment terms; base languages {pkg.languages(rows)}")
    oracle.cleanup_work_dir()
    print("CHECK OK (nothing was created or changed)")
    return 0


# ---------------------------------------------------------------- page interface (common/page.py)

NUM = lambda key, label, ph: {"key": key, "label": label, "required": False, "type": "number", "placeholder": ph}
DISCOUNT_FIELDS = [f for i, (pre, word) in enumerate(zip(rules.PREFIX, rules.ORDINAL))
                   for f in (NUM(f"{pre}_percent", f"{word} discount (percent)", ("2", "1", "0.5")[i]),
                             NUM(f"{pre}_days", f"{word} discount: paid within (days)", ("10", "20", "30")[i]),
                             {"key": f"{pre}_fixed_date", "label": f"{word} discount: by date", "required": False,
                              "type": "date", "placeholder": "2026-12-15"},
                             NUM(f"{pre}_day_of_month", f"{word} discount: day of the month", "15"),
                             NUM(f"{pre}_months_ahead", f"{word} discount: months ahead", "0"))]
SPEC = {
    "title": "Create a Receivables payment term",
    "description": "Creates a Receivables payment term with its installments and discounts; an existing one is never "
                   "changed.",
    "fields": [
        {"key": "name", "label": "Payment term name", "required": True, "type": "text", "placeholder": "Net 30 AR",
         "default": None, "help": "Up to 15 characters. Capitals and spaces count."},
        {"key": "set_code", "label": "Reference data set", "required": True, "type": "pick", "placeholder": "COMMON",
         "default": None, "help": "Never filled in for you."},
        {"key": "installments", "label": "Installments", "required": True, "type": "rows", "min_rows": 1,
         "add_label": "Add an installment", "row_label": "Installment",
         "help": "Each installment: its share of the Base Amount and one due date.",
         "fields": [NUM("sequence", "Sequence", "1"),
                    {"key": "relative_amount", "label": "Relative amount", "required": True, "type": "number",
                     "placeholder": "50"},
                    NUM("days", "Due after (days)", "30"),
                    {"key": "fixed_date", "label": "Fixed due date", "required": False, "type": "date",
                     "placeholder": "2026-12-31"},
                    NUM("day_of_month", "Due on day of the month", "15"),
                    NUM("months_ahead", "Months ahead", "1")] + DISCOUNT_FIELDS},
        {"key": "description", "label": "Description", "required": False, "type": "text",
         "placeholder": "60 then 40", "default": None},
        {"key": "from_date", "label": "From date", "required": False, "type": "date", "placeholder": "2026-10-29",
         "default": None, "help": "Empty or 'today': Oracle's today minus one day."},
        {"key": "to_date", "label": "To date", "required": False, "type": "date", "placeholder": "2027-12-31",
         "default": None},
        {"key": "base_amount", "label": "Base amount", "required": False, "type": "number", "placeholder": "100",
         "default": 100},
        {"key": "print_lead_days", "label": "Print lead days", "required": False, "type": "number",
         "placeholder": "1", "default": None, "help": "Needed with 2 or more installments."},
        {"key": "tax_freight", "label": "Tax and freight", "required": False, "type": "pick",
         "placeholder": rules.LABEL["INCLUDE"], "default": None, "help": "Needed with 2 or more installments."},
        {"key": "discount_basis", "label": "Discount basis", "required": False, "type": "pick",
         "placeholder": rules.LABEL["I"], "default": None, "help": "Needed when a discount is given."},
        {"key": "discount_date_basis", "label": "Discount date basis", "required": False, "type": "pick",
         "placeholder": rules.LABEL["APPLICATION_DATE"], "default": rules.LABEL["APPLICATION_DATE"]},
        {"key": "cutoff_day", "label": "Cutoff day", "required": False, "type": "number", "placeholder": "25",
         "default": None},
        {"key": "credit_check", "label": "Credit check", "required": False, "type": "yes-no", "placeholder": "No",
         "default": False},
        {"key": "prepayment", "label": "Prepayment", "required": False, "type": "yes-no", "placeholder": "No",
         "default": False},
    ],
}
FIXED_LISTS = {"tax_freight": ["INCLUDE", "ALLOCATE"], "discount_basis": ["I", "L"],
               "discount_date_basis": ["APPLICATION_DATE", "RECEIPT_DATE", "DEPOSIT_DATE"]}


def options_for(key):
    """--options set_code: Oracle's reference data sets (setIdSetsLOV, GET). The three choice lists are fixed."""
    if key in FIXED_LISTS:
        return [{"value": rules.LABEL[c], "label": rules.LABEL[c]} for c in FIXED_LISTS[key]]
    if key != "set_code":
        raise page.PageError("FAILED", detail=f"no list for {key!r}")
    oracle.check_environment()
    return [{"value": c, "label": c if n == c else f"{c} ({n})"} for c, n in POD().sets()]


def run_request(request, progress):
    """--run: one term through --run-batch's flow; a refusal is a plain stop with Oracle's reason."""
    req = {k: v for k, v in request.items() if v not in (None, "", [])}
    req["installments"] = [{k: v for k, v in r.items() if v not in (None, "")} for r in request.get("installments") or []]
    buf = __import__("io").StringIO()
    run_batch([req], buf)
    line = json.loads(buf.getvalue().strip().splitlines()[-1])
    res = line["results"][0]
    if not res["ok"]:
        err = res.get("error") or {}
        raise page.PageError(err.get("code") or "FAILED", res["text"], err.get("detail"))
    return {"text": res["text"], "created": res.get("created"), "skipped": res.get("skipped"), "where": res.get("where")}


def main():
    argv = sys.argv[1:]
    if argv[:1] == ["--plan"]:
        sys.exit(plan_command(argv))
    if argv[:1] == ["--run-batch"]:
        sys.exit(run_batch_command(argv))
    page.main(SPEC, options_for, run_request)       # --spec / --options / --run; else returns
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(HERE / "request.json"), help="requirements JSON")
    ap.add_argument("--check", action="store_true", help="read-only: layout, sets, language; nothing is created")
    args = ap.parse_args()
    if args.check:
        sys.exit(check_command())
    sys.exit(run_batch(read_requests(args.file), sys.stdout))


if __name__ == "__main__":
    main()
