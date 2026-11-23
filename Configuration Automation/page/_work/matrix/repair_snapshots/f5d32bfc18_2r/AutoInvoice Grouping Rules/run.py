"""Manage AutoInvoice Grouping Rules (AR_MANAGE_AUTOINVOICE_GROUPING_RULES): new grouping rules with their transaction
classes and optional grouping characteristics, through Oracle's setup task process without a browser (as Business
Units and Receivables Payment Terms).

  python "AutoInvoice Grouping Rules/run.py" --check                     # read-only: layout, existing rules
  python "AutoInvoice Grouping Rules/run.py" --plan '<JSON list or one request>'      # read-only, the preview
  python "AutoInvoice Grouping Rules/run.py" --run-batch '<JSON list>'   # every rule of an upload in one go
  python "AutoInvoice Grouping Rules/run.py" --spec | --options FIELD | --run '<JSON>'   # page interface
  python "AutoInvoice Grouping Rules/run.py"                             # the rules in request.json

Order, the same for --plan and --run-batch (nothing is sent for a rule unless all its checks pass):
  1. rules without Oracle (agr_rules.py: name 40, not ORA_, From Date asked, classes, characteristics);
  2. read-only Oracle reads: the task's own empty template (setupTaskCSVTemplateExports; the data file as
     fallback) and the task's data file (existing names, the characteristics Oracle's rules use);
  3. --run-batch only: the names read again from a fresh data file, ONE file of all new rules built from the
     pod's template (agr_package.py) and sent as a setup task process (setupTaskCSVImports, Basic auth), Oracle's
     result and log read, and every sent rule compared field by field with a fresh data file (other rules
     unchanged). Never sent twice: after a timeout or an unknown result the read-back decides.
If Oracle refuses the setup task process for this task, the run stops with a plain message; no other route is
tried (CLAUDE.md > Route status). Copied from Receivables Payment Terms/run.py (isolation rule) and changed.
"""
import argparse
import base64
import collections
import contextlib
import difflib
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent), str(HERE)]
from common import oracle, page  # noqa: E402

import agr_package as pkg  # noqa: E402
import agr_rules as rules  # noqa: E402

TASK = pkg.TASK
WHERE = "Setup and Maintenance > Financials > Customer Billing > Manage AutoInvoice Grouping Rules, search for {name}"
WHAT = "AutoInvoice grouping rule"


class RouteRefused(Exception):
    """Oracle refused the setup task process for this task (HTTP error on the call itself)."""

    def __init__(self, text, http=None):
        super().__init__(text)
        self.http = http


# ---------------------------------------------------------------- Oracle (read-only except send)

class Pod:
    """Every Oracle call of the folder. page/matrix/stub_grouping.py replaces it with the stand-in files."""

    def __init__(self):
        self.template_source = None

    def host(self):
        return oracle.HOST or ""

    def template(self):
        """The task's own empty template (setupTaskCSVTemplateExports). None when Oracle refuses it or it doesn't
        finish (the caller then uses the data file's layout)."""
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
        """The setup task process (setupTaskCSVImports). Returns the process number; RouteRefused when Oracle
        refuses the call itself."""
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
        result = oracle.poll_result(result_url, "AutoInvoice grouping rules")
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
    """One requested rule: the checked Rule, its problems, and what Oracle has."""

    def __init__(self, req, index):
        self.req, self.index = req, index
        self.name = req.get("name") if isinstance(req, dict) else None
        self.rule, self.problems = None, []
        self.status = None              # new | exists | problems
        self.found, self.oracle, self.notes = {}, {}, []
        self.rows = None                # {entity: [rows]} built for the file


class Plan:
    def __init__(self):
        self.items, self.layout, self.before, self.chars = [], None, None, []
        self.notes, self.template_source = [], None


def layout_of(pod, data_bytes):
    """The pod's layout: its own template, else the data file's. Checks the task, the pod (ProcessEnv in the host)
    and that the template's release is the data file's."""
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
    for i, r in enumerate(reqs):
        it = Item(r, i)
        it.rule, it.problems = rules.check(r)
        p.items.append(it)
    seen = set()
    for it in p.items:                               # the same name twice in one upload
        if not it.name:
            continue
        if it.name in seen:
            it.problems.append({"key": "name", "row": None, "text": f"'{it.name}' is listed twice.",
                                "fix": "Keep one of the two rows, or give one another name.", "field": "name",
                                "value": it.name, "suggestions": []})
            it.rule = None
        seen.add(it.name)
    data = pod.export("before")
    p.layout, p.before = layout_of(pod, data)
    p.template_source = pod.template_source
    existing = pkg.rules_in(p.before)
    p.chars = pkg.characteristics(p.before)
    for it in p.items:
        if it.name and it.name in existing:
            it.status = "exists"
            continue
        near = sorted(n for n in existing if it.name and n != it.name
                      and " ".join(n.split()).lower() == " ".join(it.name.split()).lower())
        if near:
            it.found["name"] = (f"Oracle has '{near[0]}', which differs only in capitals or spaces. This one will be "
                                "a new rule.")
        if it.rule:                                # yellow notes; the preview shows them with the summary
            it.notes = list(it.rule.notes.values())
            # The dependency rule (root CLAUDE.md > Design principles): a characteristic must already exist in Oracle.
            # Oracle has no public list (FSCR ora_reference_lookups.md:16), so "exists" = an Oracle rule uses it. An
            # unknown name would make Oracle drop that characteristic and save the rule without it (FSCR
            # ora_reference_lookups.md:16 "Missing name removes affected child row"), which a rerun can't repair.
            for n, row in enumerate(it.req.get("classes") or [], 1):
                ch = str((row or {}).get("characteristic") or "").strip() if isinstance(row, dict) else ""
                if ch and ch not in p.chars:
                    sugg = [c for c in p.chars if c.lower() == ch.lower()] + close(ch, p.chars)
                    it.problems.append({
                        "key": "classes", "row": n, "rows": "classes", "where": f"Class row {n}",
                        "text": f"Class row {n}: no grouping rule in Oracle uses characteristic '{ch}', so it can't "
                                "be confirmed before Create (Oracle has no list of them to read).",
                        "fix": ("Use one Oracle already uses: " + ", ".join(p.chars[:12]) + "." if p.chars else
                                "Oracle's rules use no characteristic yet: leave Characteristic empty for now.")
                               + " If Oracle doesn't know a name, it saves the rule without it.",
                        "field": "characteristic", "value": ch, "suggestions": list(dict.fromkeys(sugg))[:12]})
                    it.rule = None
        it.status = "problems" if it.problems else "new"
        if it.status == "new":
            it.rows = pkg.rule_rows(it.rule)
    return p


def plan_results(p):
    """The page's --plan answer per rule (page/server.py apply_oracle_check)."""
    out = []
    for it in p.items:
        res = {"name": it.name, "ok": True, "status": it.status,
               "problems": [dict(x) for x in it.problems], "skipped": None, "found": dict(it.found),
               "fills": {}, "oracle": dict(it.oracle), "summary": None}
        if it.status == "exists":
            res["skipped"] = f"An {WHAT} '{it.name}' already exists in Oracle. It will be skipped; nothing is changed."
            res["found"]["name"] = res["skipped"]
        elif it.rule:
            res["fills"] = dict(it.rule.filled)
            res["summary"] = " ".join([rules.describe(it.rule)] + it.notes)
            res["notes"] = list(it.notes)
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
    """What Oracle shows now for one rule, in the sheet's words (the result card)."""
    h = rows[pkg.ENTITIES["rule"]][0] if rows.get(pkg.ENTITIES["rule"]) else {}
    chars = collections.defaultdict(list)
    for q in rows.get(pkg.ENTITIES["request"], []):
        chars[q.get(pkg.CLASS_LINK)].append(q.get("FromColumnName"))
    return {"name": h.get("Name"), "description": h.get("Description") or None,
            "from_date": (h.get("StartDate") or "").split(" ")[0].replace("/", "-") or None,
            "to_date": (h.get("EndDate") or "").split(" ")[0].replace("/", "-") or None,
            "classes": [{"transaction_class": rules.LABEL.get(c.get("Class11"), c.get("Class11")),
                         "characteristics": chars.get(c.get("Class11"), [])}
                        for c in rows.get(pkg.ENTITIES["class"], [])]}


def rows_of(rows, key):
    return {e: [r for r in rows.get(e, []) if pkg.key_of(r) == key] for e in pkg.ENTITIES.values()}


def suggestions_for(field, it, p):
    if field == "characteristic":
        return list(p.chars)[:12]
    if field == "transaction_class":
        return list(rules.LABEL.values())
    if field == "name" and it.name:
        return [it.name[:rules.NAME_MAX].rstrip()] if len(it.name) > rules.NAME_MAX else []
    return []


def refusal_problems(it, fail, p):
    """Oracle's reason for a refused rule -> the page's structured problem for the decision panel ([] when it names
    no value the user can change; the page then asks Claude for a proposal)."""
    field = fail.get("field") if fail else None
    if not field:
        return []
    why = "; ".join(fail["reasons"])
    req = it.req
    if fail.get("child"):
        rows = req.get("classes") or []
        n = next((k for k, r in enumerate(rows, 1) if isinstance(r, dict) and r.get(field) not in (None, "")), 1)
        value = (rows[n - 1] or {}).get(field) if rows else None
        return [{"field": field, "value": value, "reason": why, "text": why,
                 "suggestions": suggestions_for(field, it, p), "rows": "classes", "row": n,
                 "where": f"Class row {n}"}]
    return [{"field": field, "value": req.get(field), "reason": why, "text": why,
             "suggestions": suggestions_for(field, it, p)}]


def result_of(it, p, outcome):
    o = outcome or {}
    where = WHERE.format(name=it.name)
    if it.status == "problems":
        return failed("INVALID_REQUEST", " ".join(x["text"] for x in it.problems) + " Nothing was sent for it.", "no",
                      problems=[x for x in it.problems])
    if it.status == "exists" or o.get("meanwhile"):
        return {"ok": True, "skipped": True, "where": where, "created": shown(rows_of(p.before, it.name)),
                "text": f"The {WHAT} {it.name} is already in Oracle"
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
    n = len(it.rule.classes)
    k = sum(len(c) for c in it.rule.classes.values())
    text = (f"Created the {WHAT} {it.name} with {n} transaction class{'es' if n != 1 else ''}"
            + (f" and {k} characteristic{'s' if k != 1 else ''}" if k else "")
            + ", and checked it in Oracle: every value as sent.")
    return {"ok": True, "where": where, "text": text, "created": shown(rows_of(o["after"], it.name))}


# ---------------------------------------------------------------- Create

def create(p, pod, progress):
    """One file for every new rule, sent once, read back. {name: outcome}."""
    out = {}
    new = [it for it in p.items if it.status == "new"]
    if not new:
        return out
    progress.step("checking", 40, "Reading the names again just before sending")
    _, now = pkg.read_rows(pod.export("names"))
    existing = pkg.rules_in(now)
    for it in list(new):
        if it.name in existing:                    # made meanwhile: never sent twice
            out[it.name] = {"meanwhile": True}
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
    progress.step("creating", 50, f"Sending {len(new)} new rule{'s' if len(new) != 1 else ''} to Oracle in one go")
    try:
        pid = pod.send(data)
    except RouteRefused as e:
        code = "NO_PERMISSION" if e.http in (401, 403) else "SETUP_NEEDED"
        text = ("Oracle refused the setup task process for AutoInvoice grouping rules"
                + (f" (HTTP {e.http})" if e.http else "") + ". Nothing was created. This way of creating them isn't "
                "proven for this task yet, and no other way was tried.")
        print(f"ROUTE REFUSED: {e}")
        for it in new:
            out[it.name] = {"route": {"code": code, "text": text, "detail": str(e)[:1500]}}
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
    progress.step("verifying", 85, "Reading the rules back from Oracle")
    try:
        _, after = pkg.read_rows(pod.export("after"))
    except (SystemExit, Exception) as e:  # noqa: BLE001
        msg = str(e) or type(e).__name__
        code = page._classify(wait_error or msg)
        for it in new:
            out[it.name] = {"unknown": {"code": code, "detail": msg[:1500],
                                        "text": f"The {WHAT} {it.name} may have been saved in Oracle; reading it back "
                                                "didn't finish. A rerun skips it if it is there."}}
        return out
    sent = {it.name: it.rows for it in new}
    checks, changed = pkg.reconcile(p.layout, sent, now, after)
    if changed:
        print(f"  NOTE: other rules changed during the run: {', '.join(changed)}")
        p.notes.append(f"Oracle also shows changes on other grouping rules during this run: {', '.join(changed)}.")
    refused = [it for it in new if not checks[it.name]["saved"]]
    unnamed = [f for f in fails if f["rule"] is None]           # blocks that quote no sent name
    unclaimed = [it for it in refused if not any(f["rule"] == it.name for f in fails)]
    for it in new:
        mine = [f for f in fails if f["rule"] == it.name]
        if not mine and unnamed and unclaimed == [it]:
            mine = unnamed                     # the one refused rule the log doesn't name: those reasons are its own
        fail = None
        if mine:
            fail = {"reasons": [r for f in mine for r in f["reasons"]],
                    "field": next((f["field"] for f in mine if f["field"]), None),
                    "child": any(f["child"] for f in mine if f["field"])}
        elif it in unclaimed and unnamed:      # several unnamed refusals: quoted, never guessed per rule
            fail = {"reasons": ["Oracle's log, which doesn't say which rule: "
                                + "; ".join(r for f in unnamed for r in f["reasons"])], "field": None, "child": False}
        out[it.name] = {"check": checks[it.name], "fail": fail, "after": after}
    return out


# ---------------------------------------------------------------- commands

def read_requests(arg):
    raw = json.loads(Path(arg).read_text(encoding="utf-8") if arg.endswith(".json") and Path(arg).exists() else arg)
    if isinstance(raw, dict) and "rules" in raw:
        raw = raw["rules"]
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
        except pkg.LayoutError as e:
            print(f"LAYOUT: {e}")
            print(json.dumps({"ok": False, "text": pkg.LAYOUT_TEXT, "detail": e.why}), file=out)
            return 1
        except SystemExit as e:
            print(json.dumps({"ok": False, "text": "Oracle couldn't be read just now for AutoInvoice grouping rules.",
                              "detail": str(e)[:500]}), file=out)
            return 1
        oracle.cleanup_work_dir()
    c = collections.Counter(it.status for it in p.items)
    print(json.dumps({"ok": True, "text": f"{c['new']} new, {c['exists']} already in Oracle, {c['problems']} with "
                      "problems (nothing was changed in Oracle).", "characteristics": p.chars,
                      "layout": {"source": p.template_source, "order": p.layout.order(), "release": p.layout.release},
                      "results": plan_results(p)}, ensure_ascii=False, default=str), file=out)
    return 0


def run_batch(reqs, out):
    """Every rule of an upload in one call. Progress lines, then {"step": "result", "ok", "text", "results"}."""
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
            progress.step("checking", 20, "Checking every AutoInvoice grouping rule with Oracle")
            p = plan(reqs, pod)
            for it in p.items:
                print(f"  {it.name}: {it.status}" + "".join(f"; {x['text']}" for x in it.problems))
            outcome = create(p, pod, progress)
        except pkg.LayoutError as e:
            top_error = {"code": "SETUP_NEEDED", "step": "checking", "detail": e.why, "text": pkg.LAYOUT_TEXT}
            print(f"LAYOUT: {e}")
        except (SystemExit, Exception) as e:  # noqa: BLE001 - answered per rule below
            msg = messages[-1] if messages else f"{type(e).__name__}: {e}"
            top_error = {"code": page._classify(msg), "step": "checking", "detail": msg[:1500]}
            print(f"STOPPED: {msg[:1500]}")
        finally:
            oracle.fail = real_fail
        results = []
        for i, r in enumerate(reqs):
            it = p.items[i] if p and i < len(p.items) else Item(r, i)
            if top_error and it.name not in outcome and it.status != "problems":
                results.append(failed(top_error["code"], top_error.get("text") or (
                    page.ERRORS.get(top_error["code"], page.ERRORS["FAILED"]) + " Nothing was sent to Oracle."), "no",
                    message=top_error["detail"]))
            else:
                results.append(result_of(it, p, outcome.get(it.name)))
        progress.step("done")
    made = sum(1 for r in results if r["ok"] and not r.get("skipped"))
    skipped = sum(1 for r in results if r.get("skipped"))
    bad = sum(1 for r in results if not r["ok"])
    text = (f"Created {made} of {len(results)} AutoInvoice grouping rules" + (f", {skipped} already there" if skipped
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
    """--check (read-only): the template, the data file and the characteristics in use; nothing is created."""
    pod = POD()
    oracle.check_environment()
    oracle.init_work_dir(HERE)
    try:
        lay, rows = layout_of(pod, pod.export("check"))
    except pkg.LayoutError as e:
        print(f"CHECK FAILED: {e}")
        return 1
    print(f"layout from the {pod.template_source}: release {lay.release}, pod {lay.env}, entity order {lay.order()}")
    for n in lay.order():
        print(f"  {n}: {','.join(lay.entities[n]['header'])}")
    print(f"{len(pkg.rules_in(rows))} AutoInvoice grouping rules: {', '.join(sorted(pkg.rules_in(rows)))}")
    print(f"characteristics in use: {', '.join(pkg.characteristics(rows)) or '(none)'}")
    oracle.cleanup_work_dir()
    print("CHECK OK (nothing was created or changed)")
    return 0


# ---------------------------------------------------------------- page interface (common/page.py)

SPEC = {
    "title": "Create an AutoInvoice grouping rule",
    "description": "Creates an AutoInvoice grouping rule with its transaction classes and characteristics; an "
                   "existing one is never changed.",
    "fields": [
        {"key": "name", "label": "Grouping rule name", "required": True, "type": "text",
         "placeholder": "CORSAIR OEM BY ORDER REFERENCE", "default": None,
         "help": "Up to 40 characters, not starting with ORA_. Capitals and spaces count."},
        {"key": "from_date", "label": "From date", "required": True, "type": "date", "placeholder": "2026-11-01",
         "default": None, "help": "Never filled in for you."},
        {"key": "classes", "label": "Transaction classes", "required": False, "type": "rows", "min_rows": 0,
         "add_label": "Add a class row", "row_label": "Class row",
         "help": "One row per class, or per class and characteristic.",
         "fields": [{"key": "transaction_class", "label": "Transaction class", "required": True, "type": "pick",
                     "placeholder": "Invoice"},
                    {"key": "characteristic", "label": "Characteristic", "required": False, "type": "text",
                     "placeholder": "L.INTERFACE_LINE_ATTRIBUTE1"}]},
        {"key": "description", "label": "Description", "required": False, "type": "text",
         "placeholder": "One invoice per OEM order reference for Intel, AMD and NVIDIA", "default": None},
        {"key": "to_date", "label": "To date", "required": False, "type": "date", "placeholder": "2027-12-31",
         "default": None},
    ],
}


def options_for(key):
    """--options classes.transaction_class: the three seeded classes (FSCR: a fixed list, nothing to read)."""
    if key in ("classes.transaction_class", "transaction_class"):
        return [{"value": v, "label": v} for v in rules.LABEL.values()]
    raise page.PageError("FAILED", detail=f"no list for {key!r}")


def run_request(request, progress):
    """--run: one rule through --run-batch's flow; a refusal is a plain stop with Oracle's reason."""
    req = {k: v for k, v in request.items() if v not in (None, "", [])}
    req["classes"] = [{k: v for k, v in r.items() if v not in (None, "")} for r in request.get("classes") or []]
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
    ap.add_argument("--check", action="store_true", help="read-only: layout, existing rules; nothing is created")
    args = ap.parse_args()
    if args.check:
        sys.exit(check_command())
    sys.exit(run_batch(read_requests(args.file), sys.stdout))


if __name__ == "__main__":
    main()
