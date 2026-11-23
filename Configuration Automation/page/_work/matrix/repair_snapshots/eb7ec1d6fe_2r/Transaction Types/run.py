"""Manage Transaction Types (AR_MANAGE_TRANSACTION_TYPES): new Receivables transaction types, HEADER ONLY (no reference
accounts, no account segments), through Oracle's setup task process without a browser (as Receivables Payment Terms,
AutoInvoice Grouping Rules and Transaction Sources).

  python "Transaction Types/run.py" --check                     # read-only: layout, sets, existing types
  python "Transaction Types/run.py" --plan '<JSON list or one request>'      # read-only, the preview
  python "Transaction Types/run.py" --run-batch '<JSON list>'   # every type of an upload in one go
  python "Transaction Types/run.py" --spec | --options FIELD | --run '<JSON>'   # page interface
  python "Transaction Types/run.py"                             # the types in request.json

Order, the same for --plan and --run-batch (nothing is sent for a type unless all its checks pass):
  1. rules without Oracle (tt_rules.py: name 20, set, description 80, class, status, dates, the six flags, sign,
     transaction status, printing, payment term + set);
  2. read-only Oracle reads: the reference data sets (setIdSetsLOV), the task's own empty template
     (setupTaskCSVTemplateExports; the data file as fallback), the task's data file and Oracle's list of transaction
     types (transactionTypesLOV) for existing types, and, only when a type names a payment term that isn't on the same
     sheet, the Receivables payment terms task's data file;
  3. --run-batch only: the names read again; a payment term that was on the sheet (payment_term_pending, created first
     by the page) read again from Oracle; ONE file of all new types built from the pod's template (tt_package.py) and
     sent as a setup task process (setupTaskCSVImports, Basic auth), Oracle's result and log read, every sent type
     compared field by field with a fresh data file (other types unchanged). Never sent twice.
Requests that reach Oracle use neutral ZZ_TEST_ names only (root CLAUDE.md, user's rule 2026-11-01).
Copied from Transaction Sources/run.py (isolation rule) and changed.
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

import tt_package as pkg  # noqa: E402
import tt_rules as rules  # noqa: E402

TASK = pkg.TASK
WHERE = ("Setup and Maintenance > Financials > Customer Billing > Manage Transaction Types, search for {name} "
         "(set {set})")
WHAT = "transaction type"


class RouteRefused(Exception):
    """Oracle refused the setup task process for this task (HTTP error on the call itself)."""

    def __init__(self, text, http=None):
        super().__init__(text)
        self.http = http


# ---------------------------------------------------------------- Oracle (read-only except send)

class Pod:
    """Every Oracle call of the folder. page/matrix/stub_transaction_types.py replaces it with saved pod files."""

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

    def lov_types(self):
        """[(Name, set code or set name, Description)] of every transaction type (transactionTypesLOV, GET, paged;
        FSCR names it as discovery evidence). Used beside the data file for existing names and, when the data file
        doesn't show a new type, for the read-back. No name is sent: the whole list is read."""
        out, params = [], {"onlyData": "true", "limit": 500, "offset": 0}
        while True:
            r = oracle.call("GET", f"{oracle.API_BASE}/transactionTypesLOV", params=params).json()
            out += [(i.get("Name"), i.get("SetCode") or i.get("SetName"), i.get("Description"))
                    for i in r.get("items", [])]
            if not r.get("hasMore"):
                return out
            params["offset"] += params["limit"]

    def terms_export(self, tag):
        """The Receivables payment terms task's data file (read only), for the term names and sets."""
        return oracle.export_task(pkg.TERMS_TASK, tag)[0]

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
        result = oracle.poll_result(result_url, "transaction types")
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
    """One requested type: the checked TrxType, its problems, and what Oracle has."""

    def __init__(self, req, index):
        self.req, self.index = req, index
        self.name = req.get("name") if isinstance(req, dict) else None
        self.set = str(req.get("set_code") or "").strip() if isinstance(req, dict) else ""
        self.tt, self.problems = None, []
        self.status = None              # new | exists | problems
        self.found, self.oracle = {}, {}
        self.rows = None


class Plan:
    def __init__(self):
        self.items, self.layout, self.before, self.sets, self.terms = [], None, None, [], None
        self.lov = {}                   # (Name, SetCode) -> Description, from transactionTypesLOV
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
    """{(Name, SetCode): Description} of the type list (a set given by its name is mapped to its code)."""
    code = {c: c for c, _ in sets}
    for c, n in sets:
        code.setdefault(n, c)
    return {(name, code.get(s, s)): desc for name, s, desc in lov}


def term_problem(it, term, tset, keys):
    in_set = sorted(n for n, s in keys if s == tset)
    sugg = [n for n in in_set if n.lower() == term.lower()] + close(term, in_set)
    other = sorted(s for n, s in keys if n == term and s != tset)
    return {"key": "payment_term", "row": None, "field": "payment_term", "value": term,
            "text": f"Payment Term '{term}' in set {tset} isn't in Oracle and isn't on this sheet's Receivables Payment "
                    "Terms tab." + (f" Oracle has it in set {', '.join(other)}." if other else ""),
            "fix": "Add the term to the Receivables Payment Terms tab, or use one Oracle has in set "
                   f"{tset}: " + (", ".join(in_set[:12]) or "(none)") + ".",
            "suggestions": list(dict.fromkeys(sugg))[:12] or in_set[:12]}


def plan(reqs, pod):
    """Every check before Create, read-only. Raises pkg.LayoutError or SystemExit (Oracle couldn't be read)."""
    p = Plan()
    p.sets = pod.sets()
    for i, r in enumerate(reqs):
        it = Item(r, i)
        it.tt, it.problems = rules.check(r)
        p.items.append(it)
    seen = set()
    for it in p.items:                               # the same name and set twice in one upload
        if not it.name:
            continue
        if (it.name, it.set) in seen:
            it.problems.append({"key": "name", "row": None, "text": f"'{it.name}' is listed twice for set {it.set}.",
                                "fix": "Keep one of the two rows, or give one another name.", "field": "name",
                                "value": it.name, "suggestions": []})
            it.tt = None
        seen.add((it.name, it.set))
    data = pod.export("before")
    p.layout, p.before = layout_of(pod, data)
    p.template_source = pod.template_source
    p.lov = lov_keys(pod.lov_types(), p.sets)
    existing = {**p.lov, **pkg.types_in(p.before)}
    codes = [c for c, _ in p.sets]
    used_sets = sorted({k[1] for k in existing if k[1]})

    def set_problem(it, key, label, value):
        hit = [c for c in codes if c.lower() == value.lower()]
        sugg = hit + [c for c in used_sets if c not in hit] + [c for c in close(value, codes) if c not in hit]
        it.problems.append({"key": key, "row": None, "text": f"{label} '{value}' isn't one of Oracle's reference data "
                            "sets.", "fix": "Pick one of: " + ", ".join((sugg or codes)[:12]) + ".", "field": key,
                            "value": value, "suggestions": (sugg or codes)[:12]})
        it.tt = None

    for it in p.items:
        if it.set and it.set not in codes:
            set_problem(it, "set_code", "Set Code", it.set)
        if it.name and (it.name, it.set) in existing:
            it.status = "exists"
            continue
        near = sorted(n for (n, s) in existing if s == it.set and it.name and n != it.name
                      and " ".join(n.split()).lower() == " ".join(it.name.split()).lower())
        if near:
            it.found["name"] = (f"Oracle has '{near[0]}' in set {it.set}, which differs only in capitals or spaces. "
                                "This one will be a new transaction type.")
        if it.tt and it.tt.term:
            if it.tt.term_set not in codes:
                set_problem(it, "payment_term_set", "Payment Term Set", it.tt.term_set)
            elif it.tt.term_pending:             # a row of the same upload: the page creates it first
                it.found["payment_term"] = (f"On the Receivables Payment Terms tab of this sheet: {it.tt.term} is "
                                            "created first; this transaction type waits for it.")
            else:
                if p.terms is None:
                    p.terms = pkg.term_keys(pod.terms_export("terms"))
                if (it.tt.term, it.tt.term_set) not in p.terms:
                    it.problems.append(term_problem(it, it.tt.term, it.tt.term_set, p.terms))
                    it.tt = None
        it.status = "problems" if it.problems else "new"
        if it.status == "new":
            it.rows = pkg.type_rows(it.tt)
            names = dict(p.sets)
            it.oracle = {"set_code": f"{it.set} ({names[it.set]})" if names.get(it.set, it.set) != it.set else it.set}
    return p


def plan_results(p):
    """The page's --plan answer per type (page/server.py apply_oracle_check)."""
    out = []
    for it in p.items:
        res = {"name": it.name, "ok": True, "status": it.status,
               "problems": [dict(x) for x in it.problems], "skipped": None, "found": dict(it.found),
               "fills": {}, "oracle": dict(it.oracle), "summary": None}
        if it.status == "exists":
            res["skipped"] = (f"A {WHAT} '{it.name}' already exists in set {it.set}. It will be skipped; nothing is "
                              "changed.")
            res["found"]["name"] = res["skipped"]
        elif it.tt:
            res["summary"] = rules.describe(it.tt)
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
    """What Oracle shows now for one type, in the sheet's words (the result card)."""
    lab = lambda v: rules.LABEL.get(v, v) or None
    day = lambda v: (v or "").split(" ")[0].replace("/", "-") or None
    out = {"name": row.get("Name"), "set_code": row.get("SetCode"), "description": row.get("Description") or None,
           "trx_class": lab(row.get("Type")), "status": lab(row.get("Status")), "from_date": day(row.get("StartDate")),
           "to_date": day(row.get("EndDate"))}
    out.update({k: lab(row.get(col)) for k, (col, _) in rules.FLAGS.items()})
    out.update(creation_sign=lab(row.get("CreationSign")), transaction_status=lab(row.get("DefaultStatus")),
               printing_option=lab(row.get("DefaultPrintingOption")), payment_term=row.get("DefaultTermName") or None,
               payment_term_set=row.get("DefaultTermSetCode") or None)
    return out


def suggestions_for(field, it, p):
    if field in ("set_code", "payment_term_set"):
        used = sorted({k[1] for k in pkg.types_in(p.before) if k[1]})
        return [c for c in used if c != it.set] + [c for c, _ in p.sets if c not in used and c != it.set][:8]
    if field == "payment_term":
        return sorted(n for n, s in (p.terms or set()) if s == (it.tt.term_set if it.tt else ""))[:12]
    if field in rules.FLAGS:
        return ["Yes", "No"]
    return {"trx_class": ["Invoice", "Debit Memo"], "status": ["Active", "Inactive"],
            "creation_sign": ["Positive Sign"], "transaction_status": ["Open"],
            "printing_option": ["Print", "Do Not Print"]}.get(field, [])


def refusal_problems(it, fail, p):
    """Oracle's reason for a refused type -> the page's structured problem for the decision panel."""
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
        row = pkg.types_in(p.before).get(key) or {"Name": it.name, "SetCode": it.set, "Description": p.lov.get(key)}
        return {"ok": True, "skipped": True, "where": where, "created": shown(row),
                "text": f"The {WHAT} {it.name} is already in set {it.set} in Oracle"
                        + (" (made while this run was checking)" if o.get("meanwhile") else "")
                        + ", so it was skipped; nothing was changed."}
    if o.get("term_missing"):
        return failed("INVALID_REQUEST", o["term_missing"], "no",
                      problems=[term_problem(it, it.tt.term, it.tt.term_set, p.terms or set())],
                      message=o["term_missing"])
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
                "text": f"Created the {WHAT} {it.name} in set {it.set}. Oracle's data file for this task doesn't list "
                        "it, so only its name, set and description were checked in Oracle's list of transaction types "
                        "(they match); its other values couldn't be read back."}
    text = (f"Created the {WHAT} {it.name} ({rules.LABEL[it.tt.trx_class]}) in set {it.set}"
            + (f" with payment term {it.tt.term}" if it.tt.term else "")
            + ", and checked it in Oracle: every value as sent."
            + ("".join(" " + n + "." for n in rec.get("notes", []))))
    return {"ok": True, "where": where, "text": text, "created": shown(pkg.types_in(o["after"]).get(key, {}))}


# ---------------------------------------------------------------- Create

def create(p, pod, progress):
    """One file for every new type, sent once, read back. {(name, set): outcome}."""
    out = {}
    new = [it for it in p.items if it.status == "new"]
    if not new:
        return out
    progress.step("checking", 40, "Reading the names again just before sending")
    _, now = pkg.read_rows(pod.export("names"))
    p.lov = lov_keys(pod.lov_types(), p.sets)
    existing = {**p.lov, **pkg.types_in(now)}
    for it in list(new):
        if (it.name, it.set) in existing:          # made meanwhile: never sent twice
            out[(it.name, it.set)] = {"meanwhile": True}
            new.remove(it)
    pending = [it for it in new if it.tt.term and it.tt.term_pending]
    if pending:                                    # created earlier in this run by the payment terms module
        p.terms = pkg.term_keys(pod.terms_export("terms_now"))
        for it in pending:
            if (it.tt.term, it.tt.term_set) not in p.terms:
                out[(it.name, it.set)] = {"term_missing": f"Its payment term {it.tt.term} (set {it.tt.term_set}) isn't "
                                          "in Oracle yet, so this transaction type was not sent. Nothing was saved in "
                                          "Oracle."}
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
    progress.step("creating", 50, f"Sending {len(new)} new transaction type{'s' if len(new) != 1 else ''} to Oracle "
                  "in one go")
    try:
        pid = pod.send(data)
    except RouteRefused as e:
        code = "NO_PERMISSION" if e.http in (401, 403) else "SETUP_NEEDED"
        text = ("Oracle refused the setup task process for transaction types"
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
    progress.step("verifying", 85, "Reading the transaction types back from Oracle")
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
    if unlisted:                                   # not in the data file: Oracle's type list decides
        try:
            lov = lov_keys(pod.lov_types(), p.sets)
        except (SystemExit, Exception) as e:  # noqa: BLE001
            lov = {}
            print(f"  the type list couldn't be read: {e}")
        for k in unlisted:
            if k in lov:
                want = sent[k][pkg.ENTITIES["type"]][0].get("Description") or ""
                diffs = [] if (lov[k] or "") == want else [f"the description: Oracle has '{lov[k]}', sent '{want}'"]
                checks[k] = {"saved": True, "diffs": diffs, "notes": [], "entity": "list",
                             "lov_only": {"Name": k[0], "SetCode": k[1], "Description": lov[k]}}
    if changed:
        print(f"  NOTE: other transaction types changed during the run: {', '.join(changed)}")
        p.notes.append(f"Oracle also shows changes on other transaction types during this run: {', '.join(changed)}.")
    refused = [it for it in new if not checks[(it.name, it.set)]["saved"]]
    unnamed = [f for f in fails if f["type"] is None]
    unclaimed = [it for it in refused if not any(f["type"] == it.name for f in fails)]
    for it in new:
        key = (it.name, it.set)
        mine = [f for f in fails if f["type"] == it.name]
        if not mine and unnamed and unclaimed == [it]:
            mine = unnamed
        fail = None
        if mine:
            fail = {"reasons": [r for f in mine for r in f["reasons"]],
                    "field": next((f["field"] for f in mine if f["field"]), None), "child": False}
        elif it in unclaimed and unnamed:
            fail = {"reasons": ["Oracle's log, which doesn't say which transaction type: "
                                + "; ".join(r for f in unnamed for r in f["reasons"])], "field": None, "child": False}
        out[key] = {"check": checks[key], "fail": fail, "after": after}
    return out


# ---------------------------------------------------------------- commands

def read_requests(arg):
    raw = json.loads(Path(arg).read_text(encoding="utf-8") if arg.endswith(".json") and Path(arg).exists() else arg)
    if isinstance(raw, dict) and "types" in raw:
        raw = raw["types"]
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
            print(json.dumps({"ok": False, "text": "Oracle couldn't be read just now for transaction types.",
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
    """Every type of an upload in one call. Progress lines, then {"step": "result", "ok", "text", "results"}."""
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
            progress.step("checking", 20, "Checking every transaction type with Oracle")
            p = plan(reqs, pod)
            for it in p.items:
                print(f"  {it.name} ({it.set}): {it.status}" + "".join(f"; {x['text']}" for x in it.problems))
            outcome = create(p, pod, progress)
        except pkg.LayoutError as e:
            top_error = {"code": "SETUP_NEEDED", "step": "checking", "detail": e.why, "text": pkg.LAYOUT_TEXT}
            print(f"LAYOUT: {e}")
        except (SystemExit, Exception) as e:  # noqa: BLE001 - answered per type below
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
    text = (f"Created {made} of {len(results)} transaction types" + (f", {skipped} already there" if skipped else "")
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
    """--check (read-only): the sets, the template, the data file, Oracle's type list; nothing is created."""
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
        e = lay.entities[n]
        print(f"  {n}: NodeSequence {e['node_sequence']}, {e['node_path']}, {len(e['header'])} columns: "
              f"{','.join(e['header'])}")
    for n in lay.order():
        print(f"  {n}: {len(rows.get(n, []))} rows")
    found = pkg.types_in(rows)
    print(f"{len(found)} transaction types in the data file: " + "; ".join(
        f"{k[0]} ({k[1]}, {r.get('Type')})" for k, r in sorted(found.items())))
    lov = lov_keys(pod.lov_types(), sets)
    print(f"{len(lov)} transaction types in Oracle's type list: " + "; ".join(f"{k[0]} ({k[1]})" for k in sorted(lov)))
    oracle.cleanup_work_dir()
    print("CHECK OK (nothing was created or changed)")
    return 0


# ---------------------------------------------------------------- page interface (common/page.py)

FIXED_LISTS = {"trx_class": ["INV", "DM"], "status": ["A", "I"], "creation_sign": ["P"], "transaction_status": ["OP"],
               "printing_option": ["PRI", "NOT"]}
YN = {"type": "yes-no", "required": True, "placeholder": "Yes", "default": None}
SPEC = {
    "title": "Create a transaction type",
    "description": "Creates a Receivables transaction type (no accounts); an existing one is never changed.",
    "fields": [
        {"key": "name", "label": "Transaction type name", "required": True, "type": "text",
         "placeholder": "INVOICE OEM", "default": None, "help": "At most 20 characters. Capitals and spaces count."},
        {"key": "set_code", "label": "Reference data set", "required": True, "type": "pick", "placeholder": "COMMON",
         "default": None, "help": "Never filled in for you."},
        {"key": "trx_class", "label": "Class", "required": True, "type": "pick", "placeholder": "Invoice",
         "default": None},
        {"key": "status", "label": "Status", "required": True, "type": "pick", "placeholder": "Active", "default": None},
        {"key": "from_date", "label": "From date", "required": True, "type": "date", "placeholder": "2026-11-01",
         "default": None},
        {"key": "open_receivable", "label": "Open receivable", **YN},
        {"key": "post_to_gl", "label": "Post to GL", **YN},
        {"key": "allow_freight", "label": "Allow freight", **YN},
        {"key": "tax_calculation", "label": "Tax calculation", **YN},
        {"key": "natural_application", "label": "Natural application only", **YN},
        {"key": "allow_overapplication", "label": "Allow overapplication", **YN},
        {"key": "creation_sign", "label": "Creation sign", "required": True, "type": "pick",
         "placeholder": "Positive Sign", "default": None},
        {"key": "transaction_status", "label": "Transaction status", "required": True, "type": "pick",
         "placeholder": "Open", "default": None},
        {"key": "printing_option", "label": "Printing option", "required": True, "type": "pick", "placeholder": "Print",
         "default": None},
        {"key": "description", "label": "Description", "required": False, "type": "text",
         "placeholder": "Invoices for order lines", "default": None, "help": "At most 80 characters."},
        {"key": "to_date", "label": "To date", "required": False, "type": "date", "placeholder": "", "default": None},
        {"key": "payment_term", "label": "Payment term", "required": False, "type": "text", "placeholder": "30 NET",
         "default": None, "help": "A Receivables payment term; give its set too."},
        {"key": "payment_term_set", "label": "Payment term set", "required": False, "type": "pick",
         "placeholder": "COMMON", "default": None},
    ],
}


def options_for(key):
    """--options set_code / payment_term_set: Oracle's reference data sets (setIdSetsLOV, GET). The choice lists are
    fixed."""
    if key in FIXED_LISTS:
        return [{"value": rules.LABEL[c], "label": rules.LABEL[c]} for c in FIXED_LISTS[key]]
    if key not in ("set_code", "payment_term_set"):
        raise page.PageError("FAILED", detail=f"no list for {key!r}")
    oracle.check_environment()
    return [{"value": c, "label": c if n == c else f"{c} ({n})"} for c, n in POD().sets()]


def run_request(request, progress):
    """--run: one type through --run-batch's flow; a refusal is a plain stop with Oracle's reason."""
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
    ap.add_argument("--check", action="store_true", help="read-only: layout, sets, existing types; nothing is created")
    args = ap.parse_args()
    if args.check:
        sys.exit(check_command())
    sys.exit(run_batch(read_requests(args.file), sys.stdout))


if __name__ == "__main__":
    main()
