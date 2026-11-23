"""Manage Transaction Sources (AR_MANAGE_TRANSACTION_SOURCES): new Receivables transaction sources (Manual or
Imported), through Oracle's setup task process without a browser (as Business Units, Receivables Payment Terms and
AutoInvoice Grouping Rules).

  python "Transaction Sources/run.py" --check                     # read-only: layout, sets, existing sources
  python "Transaction Sources/run.py" --plan '<JSON list or one request>'      # read-only, the preview
  python "Transaction Sources/run.py" --run-batch '<JSON list>'   # every source of an upload in one go
  python "Transaction Sources/run.py" --spec | --options FIELD | --run '<JSON>'   # page interface
  python "Transaction Sources/run.py"                             # the sources in request.json

Order, the same for --plan and --run-batch (nothing is sent for a source unless all its checks pass):
  1. rules without Oracle (ts_rules.py: name, set, description, type, From Date, numbering, grouping rule);
  2. read-only Oracle reads: the reference data sets (setIdSetsLOV), the task's own empty template
     (setupTaskCSVTemplateExports; the data file as fallback), the task's data file (existing sources), and, only when
     a source names a grouping rule that isn't on the same sheet, the grouping rules task's data file;
  3. --run-batch only: the names read again; a grouping rule that was on the sheet (grouping_rule_pending, created
     first by the page) read again from Oracle; ONE file of all new sources built from the pod's template
     (ts_package.py) and sent as a setup task process (setupTaskCSVImports, Basic auth), Oracle's result and log read,
     every sent source compared field by field with a fresh data file (other sources unchanged). Never sent twice.
Requests that reach Oracle use neutral ZZ_TEST_ names only (root CLAUDE.md, user's rule 2026-11-01).
Copied from AutoInvoice Grouping Rules/run.py (isolation rule) and changed.
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

import ts_package as pkg  # noqa: E402
import ts_rules as rules  # noqa: E402

TASK = pkg.TASK
WHERE = ("Setup and Maintenance > Financials > Customer Billing > Manage Transaction Sources, search for {name} "
         "(set {set})")
WHAT = "transaction source"


class RouteRefused(Exception):
    """Oracle refused the setup task process for this task (HTTP error on the call itself)."""

    def __init__(self, text, http=None):
        super().__init__(text)
        self.http = http


# ---------------------------------------------------------------- Oracle (read-only except send)

class Pod:
    """Every Oracle call of the folder. page/matrix/stub_transaction_sources.py replaces it with saved pod files."""

    def __init__(self):
        self.template_source = None

    def host(self):
        return oracle.HOST or ""

    def sets(self):
        """[(code, name)] of Oracle's reference data sets (setIdSetsLOV, GET)."""
        r = oracle.call("GET", f"{oracle.API_BASE}/setIdSetsLOV", params={"onlyData": "true", "limit": 500})
        return sorted((i["SetCode"], i.get("SetName") or i["SetCode"]) for i in r.json().get("items", []))

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

    def lov_sources(self):
        """[(Name, SetName, Description)] of every transaction source (transactionSourcesLOV, GET, paged; FSCR
        ora_reference_lookups.md). The task's data file lists only some sources (ETIA-TEST 2026-11-01: 1 of 22), so
        existence and the read-back also use this list. No name is sent: the whole list is read."""
        out, params = [], {"onlyData": "true", "limit": 500, "offset": 0}
        while True:
            r = oracle.call("GET", f"{oracle.API_BASE}/transactionSourcesLOV", params=params).json()
            out += [(i.get("Name"), i.get("SetName"), i.get("Description")) for i in r.get("items", [])]
            if not r.get("hasMore"):
                return out
            params["offset"] += params["limit"]

    def rules_export(self, tag):
        """The grouping rules task's data file (read only), for the rule names."""
        return oracle.export_task(pkg.RULES_TASK, tag)[0]

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
        result = oracle.poll_result(result_url, "transaction sources")
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
    """One requested source: the checked Source, its problems, and what Oracle has."""

    def __init__(self, req, index):
        self.req, self.index = req, index
        self.name = req.get("name") if isinstance(req, dict) else None
        self.set = str(req.get("set_code") or "").strip() if isinstance(req, dict) else ""
        self.src, self.problems = None, []
        self.status = None              # new | exists | problems
        self.found, self.oracle = {}, {}
        self.rows = None


class Plan:
    def __init__(self):
        self.items, self.layout, self.before, self.sets, self.rules = [], None, None, [], None
        self.lov = {}                   # (Name, SetCode) -> Description, from transactionSourcesLOV
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


def lov_keys(lov, sets):
    """{(Name, SetCode): Description} of the source list (it gives the set's name; mapped to its code)."""
    code = {}
    for c, n in sets:
        code.setdefault(n, c)
    return {(name, code.get(sname, sname)): desc for name, sname, desc in lov}


def rule_problem(it, rule, names):
    sugg = [n for n in names if n.lower() == rule.lower()] + close(rule, names)
    return {"key": "grouping_rule", "row": None, "field": "grouping_rule", "value": rule,
            "text": f"Grouping Rule '{rule}' isn't in Oracle and isn't on this sheet's AutoInvoice Grouping Rules tab.",
            "fix": "Add the rule to the AutoInvoice Grouping Rules tab, or use one Oracle has: "
                   + ", ".join(names[:12]) + ".",
            "suggestions": list(dict.fromkeys(sugg))[:12] or names[:12]}


def plan(reqs, pod):
    """Every check before Create, read-only. Raises pkg.LayoutError or SystemExit (Oracle couldn't be read)."""
    p = Plan()
    p.sets = pod.sets()
    for i, r in enumerate(reqs):
        it = Item(r, i)
        it.src, it.problems = rules.check(r)
        p.items.append(it)
    seen = set()
    for it in p.items:                               # the same name and set twice in one upload
        if not it.name:
            continue
        if (it.name, it.set) in seen:
            it.problems.append({"key": "name", "row": None, "text": f"'{it.name}' is listed twice for set {it.set}.",
                                "fix": "Keep one of the two rows, or give one another name.", "field": "name",
                                "value": it.name, "suggestions": []})
            it.src = None
        seen.add((it.name, it.set))
    data = pod.export("before")
    p.layout, p.before = layout_of(pod, data)
    p.template_source = pod.template_source
    p.lov = lov_keys(pod.lov_sources(), p.sets)
    existing = {**p.lov, **pkg.sources_in(p.before)}
    codes = [c for c, _ in p.sets]
    used_sets = sorted({k[1] for k in existing if k[1]})
    for it in p.items:
        if it.set and it.set not in codes:
            hit = [c for c in codes if c.lower() == it.set.lower()]
            sugg = hit + [c for c in used_sets if c not in hit] + [c for c in close(it.set, codes) if c not in hit]
            it.problems.append({"key": "set_code", "row": None,
                                "text": f"Set Code '{it.set}' isn't one of Oracle's reference data sets.",
                                "fix": "Pick one of: " + ", ".join((sugg or codes)[:12]) + ".", "field": "set_code",
                                "value": it.set, "suggestions": (sugg or codes)[:12]})
            it.src = None
        if it.name and (it.name, it.set) in existing:
            it.status = "exists"
            continue
        near = sorted(n for (n, s) in existing if s == it.set and it.name and n != it.name
                      and " ".join(n.split()).lower() == " ".join(it.name.split()).lower())
        if near:
            it.found["name"] = (f"Oracle has '{near[0]}' in set {it.set}, which differs only in capitals or spaces. "
                                "This one will be a new source.")
        if it.src and it.src.grouping_rule:
            if it.src.rule_pending:              # a row of the same upload: the page creates it first
                it.found["grouping_rule"] = (f"On the AutoInvoice Grouping Rules tab of this sheet: "
                                             f"{it.src.grouping_rule} is created first; this source waits for it.")
            else:
                if p.rules is None:
                    p.rules = pkg.rule_names(pod.rules_export("rules"))
                if it.src.grouping_rule not in p.rules:
                    it.problems.append(rule_problem(it, it.src.grouping_rule, p.rules))
                    it.src = None
        it.status = "problems" if it.problems else "new"
        if it.status == "new":
            it.rows = pkg.source_rows(it.src)
            names = dict(p.sets)
            it.oracle = {"set_code": f"{it.set} ({names[it.set]})" if names.get(it.set, it.set) != it.set else it.set}
    return p


def plan_results(p):
    """The page's --plan answer per source (page/server.py apply_oracle_check)."""
    out = []
    for it in p.items:
        res = {"name": it.name, "ok": True, "status": it.status,
               "problems": [dict(x) for x in it.problems], "skipped": None, "found": dict(it.found),
               "fills": {}, "oracle": dict(it.oracle), "summary": None}
        if it.status == "exists":
            res["skipped"] = (f"A {WHAT} '{it.name}' already exists in set {it.set}. It will be skipped; nothing is "
                              "changed.")
            res["found"]["name"] = res["skipped"]
        elif it.src:
            res["fills"] = dict(it.src.filled)
            res["summary"] = rules.describe(it.src)
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


def shown(row):
    """What Oracle shows now for one source, in the sheet's words (the result card)."""
    lab = lambda v: rules.LABEL.get(v, v) or None
    return {"name": row.get("Name"), "set_code": row.get("SetCode"), "description": row.get("Description") or None,
            "source_type": lab(row.get("BatchSourceType")), "status": lab(row.get("Status")),
            "from_date": (row.get("StartDate") or "").split(" ")[0].replace("/", "-") or None,
            "auto_numbering": lab(row.get("AutoTrxNumberingFlag")), "last_number": row.get("LastBatchNum") or None,
            "invalid_lines": lab(row.get("InvalidLinesRule")), "grouping_rule": row.get("GroupName") or None}


def suggestions_for(field, it, p):
    if field == "set_code":
        used = sorted({k[1] for k in pkg.sources_in(p.before) if k[1]})
        return [c for c in used if c != it.set] + [c for c, _ in p.sets if c not in used and c != it.set][:8]
    if field == "grouping_rule":
        return list(p.rules or [])[:12]
    if field == "last_number":
        return ["1"]
    if field in ("source_type", "status", "invalid_lines"):
        return {"source_type": ["Manual", "Imported"], "status": ["Active", "Inactive"],
                "invalid_lines": ["Reject Invoice", "Create Invoice"]}[field]
    return []


def refusal_problems(it, fail, p):
    """Oracle's reason for a refused source -> the page's structured problem for the decision panel."""
    field = fail.get("field") if fail else None
    if not field:
        return []
    why = "; ".join(fail["reasons"])
    return [{"field": field, "value": it.req.get(field), "reason": why, "text": why,
             "suggestions": suggestions_for(field, it, p)}]


def result_of(it, p, outcome):
    o = outcome or {}
    key = (it.name, it.set)
    where = WHERE.format(name=it.name, set=it.set)
    if it.status == "problems":
        return failed("INVALID_REQUEST", " ".join(x["text"] for x in it.problems) + " Nothing was sent for it.", "no",
                      problems=[x for x in it.problems])
    if it.status == "exists" or o.get("meanwhile"):
        row = pkg.sources_in(p.before).get(key) or {"Name": it.name, "SetCode": it.set,
                                                      "Description": p.lov.get(key)}
        return {"ok": True, "skipped": True, "where": where, "created": shown(row),
                "text": f"The {WHAT} {it.name} is already in set {it.set} in Oracle"
                        + (" (made while this run was checking)" if o.get("meanwhile") else "")
                        + ", so it was skipped; nothing was changed."}
    if o.get("rule_missing"):
        return failed("INVALID_REQUEST", o["rule_missing"], "no",
                      problems=[rule_problem(it, it.src.grouping_rule, p.rules or [])], message=o["rule_missing"])
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
    if rec.get("lov_only"):
        return {"ok": True, "where": where, "created": shown(rec["lov_only"]),
                "text": f"Created the {WHAT} {it.name} in set {it.set}. Oracle's data file for this task doesn't list it, "
                        "so only its name, set and description were checked in Oracle's list of sources (they match); "
                        "its other values couldn't be read back."}
    text = (f"Created the {WHAT} {it.name} in set {it.set}" + (" for AutoInvoice" if it.src.source_type == "FOREIGN" else "")
            + (f" with grouping rule {it.src.grouping_rule}" if it.src.grouping_rule else "")
            + ", and checked it in Oracle: every value as sent.")
    return {"ok": True, "where": where, "text": text, "created": shown(pkg.sources_in(o["after"]).get(key, {}))}


# ---------------------------------------------------------------- Create

def create(p, pod, progress):
    """One file for every new source, sent once, read back. {(name, set): outcome}."""
    out = {}
    new = [it for it in p.items if it.status == "new"]
    if not new:
        return out
    progress.step("checking", 40, "Reading the names again just before sending")
    _, now = pkg.read_rows(pod.export("names"))
    p.lov = lov_keys(pod.lov_sources(), p.sets)
    existing = {**p.lov, **pkg.sources_in(now)}
    for it in list(new):
        if (it.name, it.set) in existing:          # made meanwhile: never sent twice
            out[(it.name, it.set)] = {"meanwhile": True}
            new.remove(it)
    pending = [it for it in new if it.src.grouping_rule and it.src.rule_pending]
    if pending:                                    # created earlier in this run by the grouping rules module
        p.rules = pkg.rule_names(pod.rules_export("rules_now"))
        for it in pending:
            if it.src.grouping_rule not in p.rules:
                out[(it.name, it.set)] = {"rule_missing": f"Its grouping rule {it.src.grouping_rule} isn't in Oracle "
                                          "yet, so this source was not sent. Nothing was saved in Oracle."}
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
    progress.step("creating", 50, f"Sending {len(new)} new source{'s' if len(new) != 1 else ''} to Oracle in one go")
    try:
        pid = pod.send(data)
    except RouteRefused as e:
        code = "NO_PERMISSION" if e.http in (401, 403) else "SETUP_NEEDED"
        text = ("Oracle refused the setup task process for transaction sources"
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
    progress.step("verifying", 85, "Reading the sources back from Oracle")
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
    unlisted = [k for k in sent if not checks[k]["saved"]]
    if unlisted:                                   # not in the data file: Oracle's source list decides
        try:
            lov = lov_keys(pod.lov_sources(), p.sets)
        except (SystemExit, Exception) as e:  # noqa: BLE001
            lov = {}
            print(f"  the source list couldn't be read: {e}")
        for k in unlisted:
            if k in lov:
                want = sent[k][pkg.ENTITIES["source"]][0].get("Description") or ""
                diffs = [] if (lov[k] or "") == want else [f"the description: Oracle has '{lov[k]}', sent '{want}'"]
                checks[k] = {"saved": True, "diffs": diffs, "notes": [], "entity": "list",
                             "lov_only": {"Name": k[0], "SetCode": k[1], "Description": lov[k]}}
    if changed:
        print(f"  NOTE: other sources changed during the run: {', '.join(changed)}")
        p.notes.append(f"Oracle also shows changes on other transaction sources during this run: {', '.join(changed)}.")
    refused = [it for it in new if not checks[(it.name, it.set)]["saved"]]
    unnamed = [f for f in fails if f["source"] is None]
    unclaimed = [it for it in refused if not any(f["source"] == it.name for f in fails)]
    for it in new:
        key = (it.name, it.set)
        mine = [f for f in fails if f["source"] == it.name]
        if not mine and unnamed and unclaimed == [it]:
            mine = unnamed
        fail = None
        if mine:
            fail = {"reasons": [r for f in mine for r in f["reasons"]],
                    "field": next((f["field"] for f in mine if f["field"]), None), "child": False}
        elif it in unclaimed and unnamed:
            fail = {"reasons": ["Oracle's log, which doesn't say which source: "
                                + "; ".join(r for f in unnamed for r in f["reasons"])], "field": None, "child": False}
        out[key] = {"check": checks[key], "fail": fail, "after": after}
    return out


# ---------------------------------------------------------------- commands

def read_requests(arg):
    raw = json.loads(Path(arg).read_text(encoding="utf-8") if arg.endswith(".json") and Path(arg).exists() else arg)
    if isinstance(raw, dict) and "sources" in raw:
        raw = raw["sources"]
    return raw if isinstance(raw, list) else [raw]


POD = Pod


def plan_command(argv):
    """--plan '<JSON>' (read-only): {"ok", "text", "results": [{"name", "ok", "status", "problems", "skipped", "found",
    "fills", "oracle", "summary"}]}."""
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
            print(json.dumps({"ok": False, "text": "Oracle couldn't be read just now for transaction sources.",
                              "detail": str(e)[:500]}), file=out)
            return 1
        oracle.cleanup_work_dir()
    c = collections.Counter(it.status for it in p.items)
    print(json.dumps({"ok": True, "text": f"{c['new']} new, {c['exists']} already in Oracle, {c['problems']} with "
                      "problems (nothing was changed in Oracle).",
                      "layout": {"source": p.template_source, "order": p.layout.order(), "release": p.layout.release},
                      "results": plan_results(p)}, ensure_ascii=False, default=str), file=out)
    return 0


def run_batch(reqs, out):
    """Every source of an upload in one call. Progress lines, then {"step": "result", "ok", "text", "results"}."""
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
            progress.step("checking", 20, "Checking every transaction source with Oracle")
            p = plan(reqs, pod)
            for it in p.items:
                print(f"  {it.name} ({it.set}): {it.status}" + "".join(f"; {x['text']}" for x in it.problems))
            outcome = create(p, pod, progress)
        except pkg.LayoutError as e:
            top_error = {"code": "SETUP_NEEDED", "step": "checking", "detail": e.why, "text": pkg.LAYOUT_TEXT}
            print(f"LAYOUT: {e}")
        except (SystemExit, Exception) as e:  # noqa: BLE001 - answered per source below
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
    text = (f"Created {made} of {len(results)} transaction sources" + (f", {skipped} already there" if skipped else "")
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
    """--check (read-only): the sets, the template, the data file; nothing is created."""
    pod = POD()
    oracle.check_environment()
    oracle.init_work_dir(HERE)
    try:
        sets = pod.sets()
        lay, rows = layout_of(pod, pod.export("check"))
    except pkg.LayoutError as e:
        print(f"CHECK FAILED: {e}")
        return 1
    print(f"{len(sets)} reference data sets")
    print(f"layout from the {pod.template_source}: release {lay.release}, pod {lay.env}, entity order {lay.order()}, "
          f"members {lay.members}")
    for n in lay.order():
        print(f"  {n}: {len(lay.entities[n]['header'])} columns: {','.join(lay.entities[n]['header'])}")
    for n in lay.order():
        print(f"  {n}: {len(rows.get(n, []))} rows")
    src = pkg.sources_in(rows)
    print(f"{len(src)} transaction sources in the data file: " + "; ".join(
        f"{k[0]} ({k[1]}, {r.get('BatchSourceType')})" for k, r in sorted(src.items())))
    lov = lov_keys(pod.lov_sources(), sets)
    print(f"{len(lov)} transaction sources in Oracle's source list: " + "; ".join(f"{k[0]} ({k[1]})" for k in sorted(lov)))
    oracle.cleanup_work_dir()
    print("CHECK OK (nothing was created or changed)")
    return 0


# ---------------------------------------------------------------- page interface (common/page.py)

FIXED_LISTS = {"source_type": ["INV", "FOREIGN"], "status": ["A", "I"], "invalid_lines": ["Reject", "Create"]}
SPEC = {
    "title": "Create a transaction source",
    "description": "Creates a Receivables transaction source; an existing one is never changed.",
    "fields": [
        {"key": "name", "label": "Transaction source name", "required": True, "type": "text",
         "placeholder": "OM IMPORTED ORDERS", "default": None, "help": "Not starting with ORA_. Capitals and spaces count."},
        {"key": "set_code", "label": "Reference data set", "required": True, "type": "pick", "placeholder": "COMMON",
         "default": None, "help": "Never filled in for you."},
        {"key": "description", "label": "Description", "required": True, "type": "text",
         "placeholder": "Order lines imported from Order Management", "default": None},
        {"key": "from_date", "label": "From date", "required": True, "type": "date", "placeholder": "2026-11-01",
         "default": None, "help": "Never filled in for you."},
        {"key": "source_type", "label": "Type", "required": False, "type": "pick", "placeholder": "Manual",
         "default": "Manual"},
        {"key": "status", "label": "Status", "required": False, "type": "pick", "placeholder": "Active",
         "default": "Active"},
        {"key": "auto_numbering", "label": "Automatic numbering", "required": False, "type": "yes-no",
         "placeholder": "Yes", "default": True},
        {"key": "last_number", "label": "Last number", "required": False, "type": "number", "placeholder": "1",
         "default": None, "help": "Needed with automatic numbering: a whole number, 1 or more."},
        {"key": "invalid_lines", "label": "Invalid lines", "required": False, "type": "pick",
         "placeholder": "Reject Invoice", "default": "Reject Invoice"},
        {"key": "grouping_rule", "label": "Grouping rule", "required": False, "type": "text",
         "placeholder": "DEFAULT", "default": None, "help": "Only for sources AutoInvoice uses (Type: the second choice)."},
    ],
}


def options_for(key):
    """--options set_code: Oracle's reference data sets (setIdSetsLOV, GET). The three choice lists are fixed."""
    if key in FIXED_LISTS:
        return [{"value": rules.LABEL[c], "label": rules.LABEL[c]} for c in FIXED_LISTS[key]]
    if key != "set_code":
        raise page.PageError("FAILED", detail=f"no list for {key!r}")
    oracle.check_environment()
    return [{"value": c, "label": c if n == c else f"{c} ({n})"} for c, n in POD().sets()]


def run_request(request, progress):
    """--run: one source through --run-batch's flow; a refusal is a plain stop with Oracle's reason."""
    req = {k: v for k, v in request.items() if v not in (None, "", [])}
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
    ap.add_argument("--check", action="store_true", help="read-only: layout, sets, existing sources; nothing is created")
    args = ap.parse_args()
    if args.check:
        sys.exit(check_command())
    sys.exit(run_batch(read_requests(args.file), sys.stdout))


if __name__ == "__main__":
    main()
