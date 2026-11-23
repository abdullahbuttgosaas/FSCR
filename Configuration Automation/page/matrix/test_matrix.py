"""Offline behaviour matrix: every module x every pause-and-ask / repair behaviour, through the page's real server code
(queue, per-record and batch runs, questions, answers, repair, Claude proposals, Run summary, HTTP view), with the
folders' scripts replaced by stub_folder.py (Oracle stubbed) and Claude's tool by stub_claude.py. Nothing reaches
Oracle or Claude; logs go to page/_work/matrix, not the page's own server.log.

  python page/matrix/test_matrix.py      # about 3 minutes; exit 0 = every cell PASS (2026-10-26: 48 of 48;
                                         # 2026-10-30 with Receivables Payment Terms: 56 of 56)
Since 2026-10-26 also, for every module with a read-only check before Create: a check that can't run (re-run twice,
then the folder's real reason under "Oracle", nothing created) and one that fails once (the re-run answers).
Since 2026-10-30 also the Receivables Payment Terms folder's own rules, file builder and read-back: the REAL folder
code with Oracle replaced by the pod's saved files (stub_receivables.py), through the folder's commands and through
the page's server (preview, Create, pause-and-ask), plus the layout units against FSCR's saved ETIA-TEST files.
The same for AutoInvoice Grouping Rules (2026-11-01), Transaction Sources (2026-11-01) and Transaction Types
(2026-11-02, header only, stub_transaction_types.py; a payment term and a type in one upload through depends_on).
Since 2026-11-02 also the sign-in gate: a Receivables-only sheet is checked and created with the saved browser sign-in
expired and never checked; a sheet with an Order Management module still waits for it.
"""
import json
import os
import shutil
import sys
import threading
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORK = ROOT / "page" / "_work" / "matrix"
os.environ["MATRIX_WORK"] = str(WORK)
sys.path[:0] = [str(ROOT / "page"), str(ROOT)]
sys.argv = ["server.py"]
import http.server  # noqa: E402

import run_summary  # noqa: E402
import server  # noqa: E402

shutil.rmtree(WORK, ignore_errors=True)
WORK.mkdir(parents=True)
server.WORK, server.LOGS, server.SERVER_LOG = WORK, WORK / "logs", WORK / "server.log"
run_summary.SERVER_LOG, run_summary.LOGS = WORK / "server.log", WORK / "logs"
server.TEST_MODE["on"] = True
CLAUDE = {"signed_in": True}
server.claude_status = lambda *a, **k: {"installed": True, "signed_in": CLAUDE["signed_in"], "version": "stub"}
server.find_claude = lambda *a, **k: "stub"
server.claude_command = lambda cli: [server.PY, str(HERE / "stub_claude.py")]
STUB = str(HERE / "stub_folder.py")

MODULES = {
    "Customers": dict(folder="Customers", group="Customers", tab="Organization Customers", field="city", rows=None,
                      base={"customer_type": "Organization", "account_address_set": "Enterprise Set",
                            "supplier_site_id": "1", "city": "Dallas", "state": "TX"}, key="name"),
    "Order Types": dict(folder="Order Types", group="Order Types", tab="Order Types", field="meaning", rows=None,
                        base={"meaning": "m"}, key="code"),
    "Payment Terms": dict(folder="Payment Terms", group="Payment Terms", tab="Payment Terms", child="Payment Term Lines",
                          field="months_ahead", rows="installments", key="name",
                          base={"from_date": "2026-10-25", "installments": [{"due_percent": 100, "day_of_month": 15,
                                                                             "months_ahead": 0}]}),
    "Lookup types": dict(folder="Lookup types", group="Lookup Types", tab="Lookup Types", child="Lookup Codes",
                         field="meaning", rows="codes", key="lookup_type",
                         base={"meaning": "m", "module": "Order Management", "codes": [{"code": "A", "meaning": "x"}]}),
    "Business Units": dict(folder="Business Units", group="Business Units", tab="Business Units", field="location",
                           rows=None, base={"default_set": "COMMON", "location": "none"}, key="name"),
    "Price Lists": dict(folder="Price Lists", group="Price Lists", tab="Price Lists", field="currency", rows=None,
                        base={"currency": "USD", "business_unit": "X", "start_date": "2026-10-27",
                              "access_sets": [{"set_code": "COMMON"}]}, key="name"),
    "Receivables Payment Terms": dict(folder="Receivables Payment Terms", group="Receivables Payment Terms",
                                      tab="Receivables Payment Terms", child="Receivables Term Lines", field="days",
                                      rows="installments", key="name",
                                      base={"set_code": "COMMON", "from_date": "2026-10-29", "print_lead_days": 1,
                                            "tax_freight": "Include in the first installment",
                                            "installments": [{"relative_amount": 60, "days": 30},
                                                             {"relative_amount": 40, "days": 60}]}),
    "AutoInvoice Grouping Rules": dict(folder="AutoInvoice Grouping Rules", group="AutoInvoice Grouping Rules",
                                       tab="AutoInvoice Grouping Rules", child="Grouping Rule Classes",
                                       field="characteristic", rows="classes", key="name",
                                       base={"description": "One invoice per OEM order reference for Intel, AMD and NVIDIA",
                                             "from_date": "2026-11-01",
                                             "classes": [{"transaction_class": "Invoice", "characteristic": "L.INTERFACE_LINE_ATTRIBUTE1"},
                                                         {"transaction_class": "Credit Memo"}]}),
    "Transaction Sources": dict(folder="Transaction Sources", group="Transaction Sources", tab="Transaction Sources",
                                field="description", rows=None, key="name",
                                base={"set_code": "COMMON", "description": "Manual invoices for OEM price adjustments",
                                      "source_type": "Manual", "from_date": "2026-11-01", "last_number": 500000}),
    "Transaction Types": dict(folder="Transaction Types", group="Transaction Types", tab="Transaction Types",
                              field="description", rows=None, key="name",
                              base={"set_code": "COMMON", "description": "OEM debit memos for freight corrections",
                                    "trx_class": "Debit Memo", "status": "Active", "from_date": "2026-11-01",
                                    "open_receivable": "Yes", "post_to_gl": "Yes", "allow_freight": "Yes",
                                    "tax_calculation": "Yes", "natural_application": "No",
                                    "allow_overapplication": "No", "creation_sign": "Positive Sign",
                                    "transaction_status": "Open", "printing_option": "Print"}),
}
for m in MODULES.values():
    server.FOLDERS[m["folder"]] = {"name": m["folder"], "script": STUB, "spec": {"fields": []}, "error": None}

COUNT = {"n": 0}


def record(mod, marker=None, name=None):
    m = MODULES[mod]
    COUNT["n"] += 1
    name = name or f"ZZ_STUB_{COUNT['n']}"
    req = json.loads(json.dumps(m["base"]))
    req[m["key"]] = name
    if marker:
        if m["rows"]:
            req[m["rows"]][0][m["field"]] = marker
        else:
            req[m["field"]] = marker
    rows = {"record": [m["tab"], 4], "children": [[m["child"], 4]] if m.get("child") else []}
    return {"folder": m["folder"], "group": m["group"], "request": req, "title": name, "name": name, "rows": rows}


def value_in(mod, req):
    m = MODULES[mod]
    return req[m["rows"]][0][m["field"]] if m["rows"] else req[m["field"]]


def busy(job):
    return job["state"] in ("queued", "running", "repairing") or any(
        (it.get("question") or {}).get("state") in ("checking", "retrying") for it in job["items"])


def settle(job, limit=180):
    t = time.time()
    time.sleep(0.5)
    while busy(job) and time.time() - t < limit:
        time.sleep(0.3)
    return job


def start(records, force=False):
    return settle(server.new_batch(records, upload=None, force_fail=force))


def log_text():
    return (WORK / "server.log").read_text(encoding="utf-8") if (WORK / "server.log").exists() else ""


def claude_calls():
    f = WORK / "claude_calls.jsonl"
    return [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()] if f.exists() else []


def limits_ok(call):
    a = call["argv"]
    return ("--max-budget-usd" in a and a[a.index("--max-budget-usd") + 1] == str(server.REPAIR_BUDGET_USD)
            and "--strict-mcp-config" in a and "--no-chrome" in a and "dontAsk" in a)


def http_job(jid):
    return json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/api/job/{jid}", timeout=30).read())


def check(cond, why):
    if not cond:
        raise AssertionError(why)


# ---------------------------------------------------------------- behaviours

def b_suggestion(mod):
    job = start([record(mod, "REFUSE_ME")])
    it = job["items"][0]
    q = it.get("question") or {}
    check(job["state"] == "asking" and q.get("state") == "open", f"not asking: {job['state']} {q}")
    check(q.get("suggestions", [])[:1] == ["GOOD_1"], f"suggestions {q.get('suggestions')}")
    check(it["state"] == "failed" and value_in(mod, it["request"]) == "REFUSE_ME", "changed before an answer")
    server.answer_question(job, it["n"], "GOOD_1")
    settle(job)
    check(it["state"] == "done", f"after the answer: {it['state']} {(it.get('result') or {}).get('text')}")
    check(value_in(mod, it["request"]) == "GOOD_1" and q["state"] == "answered", f"answer not applied: {q['state']}")
    return f"asked ({q.get('where') or q['label']}), answered GOOD_1, created"


def b_typed(mod):
    job = start([record(mod, "REFUSE_ME")])
    it = job["items"][0]
    server.answer_question(job, it["n"], "BAD_TYPED")
    t = time.time()
    while it["question"]["state"] == "checking" and time.time() - t < 60:
        time.sleep(0.3)
    q = it["question"]
    check(q["state"] == "open" and "BAD_TYPED" in (q.get("message") or ""), f"bad value not refused: {q}")
    check(value_in(mod, it["request"]) == "REFUSE_ME", "a refused typed value was applied")
    server.answer_question(job, it["n"], "TYPED_OK")
    settle(job)
    check(it["state"] == "done" and value_in(mod, it["request"]) == "TYPED_OK", f"typed value: {it['state']}")
    return "BAD_TYPED refused in the panel, TYPED_OK created"


def b_skip(mod):
    job = start([record(mod, "REFUSE_ME")])
    it = job["items"][0]
    server.answer_question(job, it["n"], skip=True)
    settle(job)
    check(it["question"]["state"] == "skipped" and it["state"] == "failed", f"skip: {it['question']['state']}")
    check(job["state"] in ("failed", "done"), f"run still {job['state']}")
    s = server.summary_view(job["id"], job) or {}
    lines = " ".join(" ".join(x["lines"]) for x in s.get("sections", []))
    check("skipped by you" in lines, "summary has no skip decision")
    return "skipped, not created, run ended, summary lists the decision"


def b_refresh(mod):
    job = start([record(mod, "REFUSE_ME")])
    it = job["items"][0]
    v = http_job(job["id"])
    q = next(x for x in v["items"] if x["n"] == it["n"]).get("question") or {}
    check(v["state"] == "asking" and q.get("state") == "open" and "GOOD_1" in (q.get("suggestions") or []),
          f"refresh view: {v['state']} {q}")
    v2 = http_job(job["id"])
    check(v2["items"] == v["items"], "a second refresh differs")
    server.answer_question(job, it["n"], "GOOD_2")
    settle(job)
    v3 = http_job(job["id"])
    e = next(x for x in v3["items"] if x["n"] == it["n"])
    check(e["state"] == "done" and (e.get("question") or {}).get("state") == "answered", f"after: {e['state']}")
    return "question shown again on refresh (HTTP), answered after it, created"


def b_forced_failure(mod):
    before = len(claude_calls())
    job = start([record(mod)], force=True)
    it = job["items"][0]
    calls = claude_calls()[before:]
    check(f"job {job['id']}" in log_text() and "repair attempt 1" in log_text().split(f"job {job['id']} queued")[-1],
          "no repair attempt logged")
    check(calls and not calls[0]["proposal"] and limits_ok(calls[0]), f"repair call / limits: {calls}")
    check(it["state"] == "done" and it.get("repairs", 0) >= 1, f"after repair: {it['state']} repairs={it.get('repairs')}")
    return f"test switch failed it, repair started (budget ${server.REPAIR_BUDGET_USD}), rerun created it"


def b_unknown(mod):
    before = len(claude_calls())
    job = start([record(mod, "UNKNOWN_ME")])
    it = job["items"][0]
    q = it.get("question") or {}
    calls = claude_calls()[before:]
    check(calls and calls[0]["proposal"] and limits_ok(calls[0]), f"proposal call / limits: {calls}")
    check(q.get("state") == "open" and q.get("proposed") and q.get("suggestions") == ["CLAUDE_FIX"],
          f"proposal question: {q}")
    check(q["field"] == MODULES[mod]["field"], f"proposed field {q['field']}")
    check(value_in(mod, it["request"]) == "UNKNOWN_ME", "the proposal was applied without an answer")
    server.answer_question(job, it["n"], "CLAUDE_FIX")
    settle(job)
    check(it["state"] == "done" and value_in(mod, it["request"]) == "CLAUDE_FIX", f"after: {it['state']}")
    s = server.summary_view(job["id"], job) or {}
    lines = " ".join(" ".join(x["lines"]) for x in s.get("sections", []))
    check("Claude's proposal for" in lines and "$0.01" in lines and "tokens" in lines, f"summary: {lines[:300]}")
    return "Claude proposed CLAUDE_FIX (not applied), user accepted, created; summary shows tokens and cost"


def b_unknown_no_claude(mod):
    before = len(claude_calls())
    CLAUDE["signed_in"] = False
    try:
        job = start([record(mod, "UNKNOWN_ME")])
    finally:
        CLAUDE["signed_in"] = True
    it = job["items"][0]
    check(len(claude_calls()) == before, "Claude was called although not signed in")
    check(not it.get("question") and it["state"] == "failed" and job["state"] == "failed",
          f"expected a plain card: {it.get('question')} {job['state']}")
    return "Claude not signed in: not started, plain card with Oracle's reason"


def b_one_record_script_failure(mod):
    good, flaky = record(mod), record(mod, "FLAKY_ME")
    job = start([good, flaky])
    a, b = job["items"]
    seg = log_text().split(f"job {job['id']} queued")[-1]
    check(a["state"] == "done" and b["state"] == "done", f"states {a['state']} {b['state']}")
    check("repair attempt 1" in seg, "no repair for the failed record")
    return "the failed record repaired and created, the other untouched"


BEHAVIOURS = [("Answered with a suggestion", b_suggestion), ("Answered with a typed value", b_typed),
              ("Skipped", b_skip), ("Page refresh", b_refresh), ("Forced script failure -> repair", b_forced_failure),
              ("Unknown refusal -> Claude proposes", b_unknown),
              ("Unknown refusal, Claude not signed in", b_unknown_no_claude),
              ("Script failure in 1 of 2 records -> repair", b_one_record_script_failure)]

PORT = 8799
srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), server.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
threading.Thread(target=server.worker, daemon=True).start()

table, fails = [], 0
for mod in MODULES:
    for title, fn in BEHAVIOURS:
        try:
            note, ok = fn(mod), "PASS"
        except Exception as e:  # noqa: BLE001
            note, ok = f"{type(e).__name__}: {e}"[:300], "FAIL"
            fails += 1
        table.append((mod, title, ok, note))
        print(f"{ok}  {mod:15} {title:45} {note}", flush=True)


# ---------------------------------------------------------------- a check with Oracle that can't run (2026-10-26)

def check_calls(name):
    f = WORK / "flags" / "check_calls"
    return [x for x in f.read_text(encoding="utf-8").splitlines() if x == name] if f.exists() else []


def c_check_fails(mod):
    """The folder's read-only check can't run: re-run twice (pause shortened), then one stop with the folder's real
    reason under "Oracle", nothing created, no run started."""
    rec, jobs = record(mod, "CHECK_FAILS"), set(server.JOBS)
    got = server.oracle_checks([rec])[0]
    res = {"stops": [], "problems": []}
    server.apply_oracle_check(res, rec, got)
    stop = (res["stops"] or [""])[0]
    n = len(check_calls(rec["name"]))
    check(n == 1 + server.CHECK_RERUNS, f"{n} calls")
    check("did not open Create Customer after 3 tries" in stop and "Nothing was created" in stop, f"stop {stop!r}")
    check("no answer" not in stop and res.get("oracle_stops") == res["stops"], f"oracle_stops {res.get('oracle_stops')}")
    check(set(server.JOBS) == jobs, "a run was started")
    return f"{n} tries, then under Oracle: {stop[:60]}..."


def c_check_flaky(mod):
    """The check fails once and works on the automatic re-run: no stop."""
    rec = record(mod, "CHECK_FLAKY")
    got = server.oracle_checks([rec])[0]
    check(got and got.get("ok"), f"answer {got}")
    n = len(check_calls(rec["name"]))
    check(n == 2, f"{n} calls")
    return "failed once, the automatic re-run answered"


server.CHECK_RERUN_PAUSE = 0.2          # 20 s on the page
checks = [m for m in MODULES if server.group_of({"group": MODULES[m]["group"]}).get("oracle_check")]
extra, extra_fails = [], 0
for mod in checks:
    for title, fn in (("Check can't run -> re-runs, real reason", c_check_fails),
                      ("Check fails once -> re-run answers", c_check_flaky)):
        try:
            note, ok = fn(mod), "PASS"
        except Exception as e:  # noqa: BLE001
            note, ok = f"{type(e).__name__}: {e}"[:300], "FAIL"
            extra_fails += 1
        extra.append((mod, title, ok, note))
        print(f"{ok}  {mod:15} {title:45} {note}", flush=True)


# ---------------------------------------------------------------- Receivables Payment Terms: the real folder (2026-10-30)

import io  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import zipfile  # noqa: E402

import workbook  # noqa: E402

RPT = "Receivables Payment Terms"
STUB_RPT = str(HERE / "stub_receivables.py")
sys.path.insert(0, str(ROOT / RPT))
import rpt_package as rpkg  # noqa: E402
import rpt_rules as rrules  # noqa: E402

FSCR = (ROOT.parent / "fscr-main" / "fscr-main" / "project" / "draft-impl-project-20261028" / "exports" / "financials"
        / "customer-billing" / "manage-receivables-payment-terms")
FSCR_FILES = {"template": "ETIA-TEST_setup_task_csv_template_export_ar_manage_receivables_payment_terms_100004619543924.zip",
              "before": "ETIA-TEST_setup_task_csv_export_ar_manage_receivables_payment_terms_100004619522844.zip",
              "after": "ETIA-TEST_setup_task_csv_export_ar_manage_receivables_payment_terms_100004731498215.zip",
              "candidate": "zzfscr-n45-4203-candidate.zip"}
POD_ORDER = ["AR_PAYMENT_TERM_LINE", "AR_PAYMENT_TERM", "AR_PAYMENT_TERM_TRANSLATION", "AR_PAYMENT_TERM_DISCOUNT"]


def rpt_pod(**control):
    """A fresh stub pod (its four standing terms) with these switches."""
    (WORK / "rpt_pod.json").unlink(missing_ok=True)
    (WORK / "rpt_sent.zip").unlink(missing_ok=True)
    (WORK / "rpt_stub.json").write_text(json.dumps(control), encoding="utf-8")


def rpt_cmd(cmd, payload):
    p = subprocess.run([server.PY, STUB_RPT, cmd, json.dumps(payload)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=server.ENV_CHILD, cwd=str(ROOT), timeout=300)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise AssertionError(f"{cmd} gave no answer: {p.stderr[-600:]}")


def ar_term(name="ZZ_TEST_AR_1", **kw):
    t = {"name": name, "set_code": "COMMON", "from_date": "2026-10-29", "print_lead_days": 1,
         "tax_freight": "Include in the first installment",
         "installments": [{"relative_amount": 60, "days": 30}, {"relative_amount": 40, "days": 60}]}
    t.update(kw)
    return {k: v for k, v in t.items() if v is not None}


def plan1(t, **control):
    rpt_pod(**control)
    got = rpt_cmd("--plan", [t])
    check(got.get("ok"), f"the check didn't run: {got}")
    return got["results"][0]


def has(res, key, words):
    hit = [p for p in res["problems"] if p["key"] == key and words in p["text"]]
    check(hit, f"no {key} problem saying {words!r}: {[(p['key'], p['text']) for p in res['problems']]}")
    return hit[0]["text"]


def rpt_record(t):
    n = len(t.get("installments") or [])
    return {"folder": RPT, "group": RPT, "request": t, "title": t["name"], "name": t["name"],
            "rows": {"record": [RPT, 4], "children": [["Receivables Term Lines", 4 + i] for i in range(n)]}}


def real_folder(fn):
    """Run fn with the page's server using the real folder (through stub_receivables.py) for Receivables."""
    old = server.FOLDERS[RPT]["script"]
    server.FOLDERS[RPT]["script"] = STUB_RPT
    try:
        return fn()
    finally:
        server.FOLDERS[RPT]["script"] = old


def sent_ok(order):
    """The file the folder sent: members in the template's order, metadata copied, ISO dates, audit columns empty."""
    z = zipfile.ZipFile(WORK / "rpt_sent.zip")
    check(z.namelist() == [f"{n}.csv" for n in order] + [rpkg.METADATA], f"member order {z.namelist()}")
    meta = z.read(rpkg.METADATA)
    if order == POD_ORDER:
        fixture = (ROOT / RPT / "manual-notes" / "pod_layout_etia_test" / rpkg.METADATA).read_bytes()
        check(meta == fixture, "the metadata isn't the template's, byte for byte")
    check(re.findall(rb"<BusinessObjectShortName>(\w+)</BusinessObjectShortName>\s*<BatchName>", meta)
          == [n.encode() for n in order], "metadata entity order")
    lay, rows = rpkg.read_rows((WORK / "rpt_sent.zip").read_bytes())
    for e, rs in rows.items():
        for r in rs:
            check(not any(r.get(c) for c in rpkg.AUDIT), f"{e}: an audit column is filled")
            for c, v in r.items():
                if lay.entities[e]["types"].get(c) == "date" and v:
                    check(re.fullmatch(r"\d{4}-\d{2}-\d{2}", v), f"{e}.{c} = {v} is not YYYY-MM-DD")
    return rows


def r_happy():
    rpt_pod()
    t = ar_term("ZZ_TEST_AR_4821", discount_basis="Invoice amount",
                installments=[{"relative_amount": 60, "days": 30, "discount_percent": 2, "discount_days": 10},
                              {"relative_amount": 40, "days": 60}])
    res = rpt_cmd("--plan", [t])["results"][0]
    check(res["status"] == "new" and not res["problems"] and "2 installments" in (res["summary"] or ""), f"plan {res}")
    job = real_folder(lambda: start([rpt_record(t)]))
    it = job["items"][0]
    check(it["state"] == "done" and "every value as sent" in it["result"]["text"], f"create: {it['state']} {it.get('result')}")
    rows = sent_ok(POD_ORDER)
    check(len(rows["AR_PAYMENT_TERM_LINE"]) == 2 and len(rows["AR_PAYMENT_TERM_DISCOUNT"]) == 1
          and rows["AR_PAYMENT_TERM"][0]["PrintingLeadDays"] == "1", "sent rows")
    again = real_folder(lambda: start([rpt_record(t)]))["items"][0]
    check(again["state"] == "done" and again["result"].get("skipped"), f"rerun: {again.get('result')}")
    return "checked, created in one go (1 header, 2 lines, 1 discount, 1 name row), read back as sent; rerun skipped"


def r_name_long():
    t = has(plan1(ar_term("ZZ_TEST_AR_LONG_16")), "name", "longer than 15 characters")
    return t[:70]


def r_sum():
    res = plan1(ar_term(installments=[{"relative_amount": 60, "days": 30}, {"relative_amount": 30, "days": 60}]))
    return has(res, "installments", "add up to 90, but Base Amount is 100")[:80]


def r_print_lead():
    res = plan1(ar_term(print_lead_days=None))
    a = has(res, "print_lead_days", "Print Lead Days is needed")
    has(plan1(ar_term(print_lead_days=0)), "print_lead_days", "above 0")
    one = plan1(ar_term(print_lead_days=None, tax_freight=None, installments=[{"relative_amount": 100, "days": 30}]))
    check(not one["problems"] and one["fills"].get("tax_freight"), f"one installment: {one}")
    return a[:60] + "; 0 refused; one installment needs neither"


def r_tax_freight():
    return has(plan1(ar_term(tax_freight=None)), "tax_freight", "choose Tax and Freight")[:80]


def r_duplicate():
    res = plan1(ar_term("30 Net", installments=[{"relative_amount": 100, "days": 30}], print_lead_days=None,
                        tax_freight=None))
    check(res["status"] == "exists" and "skipped" in (res["skipped"] or ""), f"exists: {res}")
    other = rpt_cmd("--plan", [ar_term("30 Net", set_code="S1", installments=[{"relative_amount": 100, "days": 30}])])
    check(other["results"][0]["status"] == "new", f"other set: {other['results'][0]}")
    twice = rpt_cmd("--plan", [ar_term("ZZ_TWICE"), ar_term("ZZ_TWICE")])["results"]
    check(not twice[0]["problems"], "first of two flagged")
    has(twice[1], "name", "listed twice for set COMMON")
    return "exact name + set skipped; same name in set S1 is new; twice in the sheet red on the later row"


def r_capitals():
    res = plan1(ar_term("30 net", installments=[{"relative_amount": 100, "days": 30}]))
    check(res["status"] == "new" and "differs only in capitals" in res["found"].get("name", ""), f"{res}")
    return res["found"]["name"][:80]


def r_dates():
    res = plan1(ar_term(from_date="2026-11-10", to_date="2026-11-01"))
    has(res, "to_date", "To Date must be after the From Date")
    res2 = plan1(ar_term(from_date="2026-11-10", to_date="2026-11-10"))
    return has(res2, "to_date", "after the From Date")[:60] + " (also when equal)"


def r_amount_due():
    res = plan1(ar_term(installments=[{"relative_amount": 100, "days": 30}, {"relative_amount": 0, "days": 60}]))
    has(res, "installments", "not money")
    res = plan1(ar_term(installments=[{"relative_amount": 60, "day_of_month": 15}, {"relative_amount": 40, "days": 60,
                                                                                   "fixed_date": "2026-12-01"}]))
    has(res, "installments", "Installment 1: Day of Month needs Months Ahead (0 = same month)")
    has(res, "installments", "Installment 2: give one due date, not Days and Fixed Date")
    res = plan1(ar_term(installments=[{"relative_amount": 60}, {"relative_amount": 40, "days": 60}]))
    has(res, "installments", "Installment 1: give one due date")
    return "an amount line of 0 refused (not money); Day of Month without Months Ahead; two due dates; none"


def r_discounts():
    def disc(discount_basis=None, **d):
        return ar_term(discount_basis=discount_basis, installments=[dict({"relative_amount": 60, "days": 30}, **d),
                                                                    {"relative_amount": 40, "days": 60}])
    has(plan1(disc(discount_percent=2, discount_days=10)), "discount_basis", "choose the Discount Basis")
    has(plan1(disc(discount_percent=2, discount_days=10, discount2_percent=2, discount2_days=20,
                   discount_basis="Invoice amount")), "installments", "2% is given twice")
    has(plan1(disc(discount_percent=101, discount_days=10, discount_basis="Invoice amount")), "installments",
        "a discount must be between 0 and 100 percent")
    has(plan1(disc(discount2_percent=1, discount2_days=20, discount_basis="Invoice amount")), "installments",
        "fill the First Discount before the Second Discount")
    has(plan1(disc(discount_percent=2, discount_days=10, discount4_percent=1, discount_basis="Invoice amount")),
        "installments", "at most 3 discounts")
    has(plan1(disc(discount_percent=2, discount_day_of_month=10, discount_basis="Invoice amount")), "installments",
        "Day of Month needs Months Ahead")
    has(plan1(disc(discount_percent=2, discount_days=10, discount_basis="Lines and tax, excluding freight")),
        "discount_basis", "only Invoice amount and Lines only")
    ok = plan1(disc(discount_percent=2, discount_days=10, discount2_percent=1, discount2_days=20,
                    discount3_percent=0.5, discount3_fixed_date="2026-12-15", discount_basis="Lines only"))
    check(not ok["problems"], f"three discounts: {ok['problems']}")
    return "basis needed; same % twice; 0-100; order; 4th refused; DoM needs months; F/T labels not offered; 3 fine"


def r_refused_at_create():
    rpt_pod()
    t = ar_term("ZZ_REFUSE_AR", set_code="ZZ_NOT_FOR_AR")

    def go():
        job = start([rpt_record(t)])
        it = job["items"][0]
        q = it.get("question") or {}
        check(job["state"] == "asking" and q.get("field") == "set_code" and "COMMON" in q.get("suggestions", []),
              f"question {job['state']} {q}")
        check(it["result"]["error"]["detail"]["saved"] == "no", "saved state")
        server.answer_question(job, it["n"], "COMMON")
        settle(job)
        check(it["state"] == "done" and it["request"]["set_code"] == "COMMON" and q["state"] == "answered",
              f"after the answer: {it['state']} {(it.get('result') or {}).get('text')}")
        return job
    real_folder(go)
    return "Oracle refused set ZZ_NOT_FOR_AR: asked (Set Code, suggestions COMMON ...), answered COMMON, created"


def r_entity_order():
    notes = []
    for order, names in (("reversed", POD_ORDER[::-1]), ("shuffled", [POD_ORDER[i] for i in (2, 0, 3, 1)])):
        rpt_pod(order=order)
        got = rpt_cmd("--run-batch", [ar_term(f"ZZ_ORDER_{order[:3].upper()}", discount_basis="Invoice amount",
                                              installments=[{"relative_amount": 50, "days": 30, "discount_percent": 1,
                                                             "discount_days": 5}, {"relative_amount": 50, "days": 60}])])
        r = got["results"][0]
        check(r["ok"] and "every value as sent" in r["text"], f"{order}: {r}")
        sent_ok(names)
        notes.append(order)
    return "template entity order " + " and ".join(notes) + ": file follows it, created and read back as sent"


def r_layout_stops():
    rpt_pod(template="no_discount")
    got = rpt_cmd("--plan", [ar_term()])
    check(not got["ok"] and got["text"] == rpkg.LAYOUT_TEXT and "AR_PAYMENT_TERM_DISCOUNT" in got["detail"], f"{got}")
    rpt_pod(template="other_release")
    got = rpt_cmd("--plan", [ar_term()])
    check(not got["ok"] and "release" in got["detail"], f"{got}")
    rpt_pod(template="refused")
    got = rpt_cmd("--plan", [ar_term()])
    check(got["ok"] and got["layout"]["source"] == "data" and "current data file" in got["results"][0]["summary"], f"{got}")
    return "no DISCOUNT entity / other release: plain stop, nothing built; template refused: data file layout, said so"


def r_language():
    res = plan1(ar_term(), langs=[])
    a = has(res, "language", "couldn't be decided (it has none)")
    res = plan1(ar_term(), langs=["US", "D"])
    has(res, "language", "several: D, US")
    return a[:70] + " / several"


def r_route_refused():
    rpt_pod(route="refused")
    job = real_folder(lambda: start([rpt_record(ar_term("ZZ_ROUTE_AR"))]))
    it = job["items"][0]
    err = it["result"]["error"]
    seg = log_text().split(f"job {job['id']} queued")[-1]
    check(it["state"] == "failed" and err["code"] == "SETUP_NEEDED" and "no other way was tried" in it["result"]["text"],
          f"{it['state']} {it.get('result')}")
    check("repair attempt" not in seg and not it.get("question"), "repaired or asked")
    return "plain card (route refused, nothing created, no other way tried); no repair, no question"


def r_check_cant_run():
    rpt_pod(check="fails")
    rec, jobs = rpt_record(ar_term("ZZ_CHECK_AR")), set(server.JOBS)
    before = log_text().count("couldn't run")
    got = real_folder(lambda: server.oracle_checks([rec]))[0]
    res = {"stops": [], "problems": []}
    server.apply_oracle_check(res, rec, got)
    stop = (res["stops"] or [""])[0]
    check(log_text().count("couldn't run") - before == server.CHECK_RERUNS, "re-runs")
    check("couldn't be read just now for Receivables payment terms" in stop and res.get("oracle_stops") == res["stops"],
          f"stop {stop!r}")
    check(set(server.JOBS) == jobs, "a run was started")
    return f"{1 + server.CHECK_RERUNS} tries, then under Oracle: {stop[:70]}..."


def ar_sheet(terms, lines):
    """A sheet made by the page's own generator (Receivables area), rows filled by column label."""
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(workbook.make_template(area="Receivables")))
    for tab, rows in (("Receivables Payment Terms", terms), ("Receivables Term Lines", lines)):
        ws = wb[tab]
        col = {str(c.value).rstrip(" *"): c.column for c in ws[2] if c.value}
        for i, r in enumerate(rows):
            for k, v in r.items():
                ws.cell(4 + i, col[k], v)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def ar_preview(data):
    res = server.offline_check(data, "2026-10-30", None)
    if res["records"] and not res["stops"]:
        for r, got in zip(res["records"], real_folder(lambda: server.oracle_checks(res["records"]))):
            server.apply_oracle_check(res, r, got)
    for r in res["records"]:
        r["ok"] = not r["problems"]
    res["ok"] = bool(res["records"]) and not res["stops"] and not res["problems"]
    return res


AR_TERMS = [{"Name": "ZZ_GOOD_AR", "Set Code": "COMMON", "Print Lead Days": 1, "Tax and Freight": "Include in the first installment",
             "Discount Basis": "Invoice amount"},
            {"Name": "ZZ_TOO_LONG_NAME_X", "Set Code": "COMMON"},
            {"Name": "ZZ_SUM_90", "Set Code": "COMMON", "Print Lead Days": 1, "Tax and Freight": "Allocate across all installments"},
            {"Name": "30 net", "Set Code": "COMMON"},
            {"Name": "30 Net", "Set Code": "COMMON"},
            {"Name": "ZZ_DOM", "Set Code": "COMMON", "To Date": "2026-10-01"}]
AR_LINES = [{"Payment Term Name": "ZZ_GOOD_AR", "Relative Amount": 60, "Days": 30, "First Discount (%)": 2,
             "First Discount Days": 10},
            {"Payment Term Name": "ZZ_GOOD_AR", "Relative Amount": 40, "Days": 60},
            {"Payment Term Name": "ZZ_TOO_LONG_NAME_X", "Relative Amount": 100, "Days": 30},
            {"Payment Term Name": "ZZ_SUM_90", "Relative Amount": 60, "Days": 30},
            {"Payment Term Name": "ZZ_SUM_90", "Relative Amount": 30, "Days": 60},
            {"Payment Term Name": "30 net", "Relative Amount": 100, "Days": 30},
            {"Payment Term Name": "30 Net", "Relative Amount": 100, "Days": 30},
            {"Payment Term Name": "ZZ_DOM", "Relative Amount": 100, "Day of Month": 15}]


def r_preview():
    rpt_pod()
    res = ar_preview(ar_sheet(AR_TERMS, AR_LINES))
    by = {r["name"]: r for r in res["records"]}
    check(by["ZZ_GOOD_AR"]["ok"] and "2 installments" in (by["ZZ_GOOD_AR"].get("oracle_summary") or ""), "good term")
    check(any("longer than 15" in p["text"] for p in by["ZZ_TOO_LONG_NAME_X"]["problems"]), "long name")
    check(any("add up to 90" in p["text"] for p in by["ZZ_SUM_90"]["problems"]), "sum")
    low = by["30 net"]
    check(low["ok"] and any("differs only in capitals" in (f.get("note") or "") for f in low["fields"]), "capitals note")
    check(any(f.get("note") == "Filled in by the automation" for f in low["fields"]), "fills")
    check(by["30 Net"].get("skipped") and by["30 Net"]["ok"], "skipped")
    dom = [p for p in by["ZZ_DOM"]["problems"]]
    check(any(p["tab"] == "Receivables Term Lines" and p["row"] == 11 and "Months Ahead" in p["text"] for p in dom),
          f"child row: {dom}")
    check(any(p["column"] == "To Date" for p in dom), "to date before today")
    # since 2026-11-01 the Receivables area has a second module: it gets the plain empty-module line, no rows
    check(not res["ok"] and [m["name"] for m in res["modules"] if m["count"]] == [RPT]
          and all("no rows for this" in (m["text"] or "") for m in res["modules"] if m["name"] != RPT),
          f"modules {res['modules']}")
    return ("good OK with summary; long name, sum red; capitals yellow; existing skipped; DoM red on its own line row "
            "(11); To Date red; only this module has rows (the other Receivables module: empty-module line)")


def r_units():
    """Layout units against FSCR's saved ETIA-TEST files (read-only)."""
    if not all((FSCR / f).exists() for f in FSCR_FILES.values()):
        return "FSCR's saved files aren't on this PC: units skipped"
    raw = {k: (FSCR / f).read_bytes() for k, f in FSCR_FILES.items()}
    lay = rpkg.read_layout(raw["template"])
    check(lay.order() == POD_ORDER and lay.release == "11.13.26.10.0", f"order {lay.order()}")
    t, probs = rrules.check({"name": "ZZFSCR N45 4203", "set_code": "COMMON", "description": "ZZ FSCR Test Net 45 4203",
                             "from_date": "2026-10-28", "print_lead_days": 1,
                             "tax_freight": "Include in the first installment",
                             "installments": [{"relative_amount": 50, "days": 30}, {"relative_amount": 50, "days": 45}]})
    check(not probs, f"rules {probs}")
    data = rpkg.build_zip(lay, rpkg.term_rows(t, "US"))
    z, tpl = zipfile.ZipFile(io.BytesIO(data)), zipfile.ZipFile(io.BytesIO(raw["template"]))
    check(z.namelist() == tpl.namelist() and z.read(rpkg.METADATA) == tpl.read(rpkg.METADATA), "members / metadata")
    _, mine = rpkg.read_rows(data)
    _, cand = rpkg.read_rows(raw["candidate"])
    same_bytes = all(z.read(n) == zipfile.ZipFile(io.BytesIO(raw["candidate"])).read(n) for n in z.namelist())
    for e in POD_ORDER:
        check(len(mine[e]) == len(cand[e]), f"{e}: {len(mine[e])} rows, FSCR {len(cand[e])}")
        for a, b in zip(mine[e], cand[e]):
            diff = {c: (a.get(c), b.get(c)) for c in b if c not in rpkg.AUDIT and (a.get(c) or "") != (b.get(c) or "")}
            check(not diff, f"{e} differs from the file Oracle accepted: {diff}")
    _, before = rpkg.read_rows(raw["before"])
    _, after = rpkg.read_rows(raw["after"])
    key = ("ZZFSCR N45 4203", "COMMON")
    res, changed = rpkg.reconcile(lay, {key: {e: [r for r in cand[e] if rpkg.key_of(r) == key] for e in cand}},
                                  before, after)
    check(res[key]["saved"] and not res[key]["diffs"] and not changed, f"reconcile {res[key]} {changed}")
    check(rpkg.same("2026/10/28", "2026-10-28", "date") and not rpkg.same("2026/10/28", "2026-10-29", "date"), "dates")
    # a template whose metadata lists the entities reversed: the file follows it
    rev = io.BytesIO()
    meta = tpl.read(rpkg.METADATA).decode()
    blocks = re.findall(r"\s*<MigrationProcessBusinessObjectCSVMetadataVORow>.*?</MigrationProcessBusinessObjectCSVMetadataVORow>",
                        meta, re.S)
    meta2 = meta.replace("".join(blocks), "".join(blocks[::-1]))
    with zipfile.ZipFile(rev, "w") as zo:
        for n in [f"{e}.csv" for e in POD_ORDER[::-1]] + [rpkg.METADATA]:
            zo.writestr(n, meta2 if n == rpkg.METADATA else tpl.read(n))
    lay2 = rpkg.read_layout(rev.getvalue())
    z2 = zipfile.ZipFile(io.BytesIO(rpkg.build_zip(lay2, rpkg.term_rows(t, "US"))))
    check(lay2.order() == POD_ORDER[::-1] and z2.namelist() == [f"{e}.csv" for e in POD_ORDER[::-1]] + [rpkg.METADATA]
          and z2.read(rpkg.METADATA) == meta2.encode(), "reversed template")
    # an extra parent-link column is kept and left empty; any other unknown column stops
    def variant(member, old, new):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as zo:
            for n in tpl.namelist():
                zo.writestr(n, tpl.read(n).replace(old, new) if n == member else tpl.read(n))
        return b.getvalue()
    lay3 = rpkg.read_layout(variant("AR_PAYMENT_TERM_LINE.csv", b'"SetCode"', b'"SetCode","AR_PAYMENT_TERM.Extra"'))
    z3 = zipfile.ZipFile(io.BytesIO(rpkg.build_zip(lay3, rpkg.term_rows(t, "US"))))
    first = z3.read("AR_PAYMENT_TERM_LINE.csv").decode().splitlines()
    check(first[0].endswith('"AR_PAYMENT_TERM.Extra"') and first[1].endswith('"COMMON",""'), "extra link column")
    try:
        rpkg.read_layout(variant("AR_PAYMENT_TERM.csv", b'"CycleName"', b'"CycleName","Surprise"'))
        check(False, "an unknown column was accepted")
    except rpkg.LayoutError as e:
        check("Surprise" in e.why, e.why)
    return ("ETIA-TEST template read (order LINE, TERM, TRANSLATION, DISCOUNT); FSCR's accepted term rebuilt value for "
            f"value{' and byte for byte' if same_bytes else ''}; its read-back: every value as sent, 10 other terms "
            "unchanged; slash = ISO date; reversed template followed; extra link column kept empty, unknown column stops")


RPT_CASES = [("Happy path, 2 installments + discount", r_happy), ("Name over 15 characters", r_name_long),
             ("Installments not adding up", r_sum), ("Missing / zero Print Lead Days", r_print_lead),
             ("Missing Tax and Freight", r_tax_freight), ("Duplicate name in the same set -> skipped", r_duplicate),
             ("Capitals-only match -> yellow note", r_capitals), ("To Date not after From Date", r_dates),
             ("Amount Due rules (share, one due date)", r_amount_due), ("Discount rules", r_discounts),
             ("Refused value at Create -> pause and ask", r_refused_at_create),
             ("Template with a different entity order", r_entity_order),
             ("Template not as known -> plain stop", r_layout_stops), ("Base language none / several", r_language),
             ("Route refused -> plain card, no other way", r_route_refused),
             ("Check can't run -> re-runs, real reason", r_check_cant_run),
             ("Preview of a sheet through the page", r_preview), ("Layout units on FSCR's ETIA-TEST files", r_units)]
rpt_table, rpt_fails = [], 0
for title, fn in RPT_CASES:
    try:
        note, ok = fn(), "PASS"
    except Exception as e:  # noqa: BLE001
        note, ok = f"{type(e).__name__}: {e}"[:400], "FAIL"
        rpt_fails += 1
    rpt_table.append(("Receivables folder", title, ok, note))
    print(f"{ok}  {'RPT folder':15} {title:45} {note}", flush=True)


# ---------------------------------------------------------------- AutoInvoice Grouping Rules: the real folder (2026-11-01)
# The folder's real code with Oracle replaced by stub_grouping.py, whose layout is ETIA-TEST's real template (saved by
# the read-only check of 2026-11-01; before that a STAND-IN from FSCR's contract). Sample data follows the Corsair demo
# story (customers Intel, AMD and NVIDIA); characteristic names are the ones ETIA-TEST's rules use.

AGR = "AutoInvoice Grouping Rules"
STUB_AGR = str(HERE / "stub_grouping.py")
sys.path.insert(0, str(ROOT / AGR))
import agr_package as apkg  # noqa: E402
import agr_rules as arules  # noqa: E402

POD_LAYOUT = ROOT / AGR / "manual-notes" / "pod_layout_etia_test"
AGR_ORDER = ["ORA_AR_AI_GRP_TXN_TYPE", "ORA_AR_AI_GRP_TXN_REQUEST", "AR_AI_GROUPING_RULE"]   # metadata order
AGR_MEMBERS = (POD_LAYOUT / "members.txt").read_text(encoding="utf-8").split()      # the pod's zip order
OEM = "CORSAIR OEM BY ORDER REFERENCE"


def agr_pod(**control):
    """A fresh stub pod (ETIA-TEST's DEFAULT, PROJECTS, GLOBAL_INTERCOMPANY, ORA_PSCR, one earlier Corsair rule)."""
    (WORK / "agr_pod.json").unlink(missing_ok=True)
    (WORK / "agr_sent.zip").unlink(missing_ok=True)
    (WORK / "agr_stub.json").write_text(json.dumps(control), encoding="utf-8")


def agr_cmd(cmd, payload):
    p = subprocess.run([server.PY, STUB_AGR, cmd, json.dumps(payload)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=server.ENV_CHILD, cwd=str(ROOT), timeout=300)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise AssertionError(f"{cmd} gave no answer: {p.stderr[-600:]}")


def ag_rule(name=OEM, **kw):
    r = {"name": name, "description": "One invoice per OEM order reference for Intel, AMD and NVIDIA",
         "from_date": "2026-11-01",
         "classes": [{"transaction_class": "Invoice", "characteristic": "L.INTERFACE_LINE_ATTRIBUTE1"},
                     {"transaction_class": "Debit Memo"}, {"transaction_class": "Credit Memo"}]}
    r.update(kw)
    return {k: v for k, v in r.items() if v is not None}


def agr_plan1(r, **control):
    agr_pod(**control)
    got = agr_cmd("--plan", [r])
    check(got.get("ok"), f"the check didn't run: {got}")
    return got["results"][0]


def agr_record(r):
    n = len(r.get("classes") or [])
    return {"folder": AGR, "group": AGR, "request": r, "title": r["name"], "name": r["name"],
            "rows": {"record": [AGR, 4], "children": [["Grouping Rule Classes", 4 + i] for i in range(n)]}}


def agr_real(fn):
    """Run fn with the page's server using the real folder (through stub_grouping.py)."""
    old = server.FOLDERS[AGR]["script"]
    server.FOLDERS[AGR]["script"] = STUB_AGR
    try:
        return fn()
    finally:
        server.FOLDERS[AGR]["script"] = old


def agr_sent_ok(order):
    """The file the folder sent: members in the template's zip order, metadata copied (its entity order = order),
    ISO dates, audit columns empty."""
    z = zipfile.ZipFile(WORK / "agr_sent.zip")
    check(z.namelist() == AGR_MEMBERS, f"member order {z.namelist()}")
    meta = z.read(apkg.METADATA)
    if order == AGR_ORDER:
        check(meta == (POD_LAYOUT / apkg.METADATA).read_bytes(), "the metadata isn't the template's, byte for byte")
    block = meta.split(b"<MigrationProcessBusinessObjectCSVMetadata1>")[1].split(b"</MigrationProcessBusinessObjectCSVMetadata1>")[0]
    check(re.findall(rb"<BusinessObjectShortName>(\w+)</BusinessObjectShortName>", block) == [n.encode() for n in order],
          "metadata entity order")       # ETIA-TEST's metadata names the entities again later, in another order
    lay, rows = apkg.read_rows((WORK / "agr_sent.zip").read_bytes())
    for e, rs in rows.items():
        for r in rs:
            check(not any(r.get(c) for c in apkg.AUDIT), f"{e}: an audit column is filled")
            for c, v in r.items():
                if lay.entities[e]["types"].get(c) == "date" and v:
                    check(re.fullmatch(r"\d{4}-\d{2}-\d{2}", v), f"{e}.{c} = {v} is not YYYY-MM-DD")
    return rows


def a_happy():
    agr_pod()
    r = ag_rule()
    res = agr_cmd("--plan", [r])["results"][0]
    check(res["status"] == "new" and not res["problems"] and "3 transaction classes" in (res["summary"] or ""), f"plan {res}")
    job = agr_real(lambda: start([agr_record(r)]))
    it = job["items"][0]
    check(it["state"] == "done" and "every value as sent" in it["result"]["text"], f"create: {it['state']} {it.get('result')}")
    rows = agr_sent_ok(AGR_ORDER)
    check(len(rows["AR_AI_GROUPING_RULE"]) == 1 and len(rows["ORA_AR_AI_GRP_TXN_TYPE"]) == 3
          and [q["FromColumnName"] for q in rows["ORA_AR_AI_GRP_TXN_REQUEST"]] == ["L.INTERFACE_LINE_ATTRIBUTE1"]
          and rows["AR_AI_GROUPING_RULE"][0]["StartDate"] == "2026-11-01", f"sent rows {rows}")
    again = agr_real(lambda: start([agr_record(r)]))["items"][0]
    check(again["state"] == "done" and again["result"].get("skipped"), f"rerun: {again.get('result')}")
    return "checked, created in one go (1 rule, 3 classes, 1 characteristic), read back as sent; rerun skipped"


def a_name():
    has(agr_plan1(ag_rule("CORSAIR OEM INVOICES GROUPED BY CUSTOMER PO X")), "name", "longer than 40 characters")
    has(agr_plan1(ag_rule("ORA_CORSAIR OEM BY PO")), "name", "can't start with ORA_")
    has(agr_plan1(ag_rule(" CORSAIR OEM BY ORDER REFERENCE")), "name", "starts or ends with a space")
    has(agr_plan1(ag_rule(description="One invoice per OEM order reference for Intel, AMD and NVIDIA component and "
                                      "cooling orders")), "description", "at most 80 characters")
    return "41 characters, ORA_ prefix, outer space, description over 80: each red"


def a_dates():
    has(agr_plan1(ag_rule(from_date=None)), "from_date", "never filled in for you")
    has(agr_plan1(ag_rule(to_date="2026-10-31")), "to_date", "can't be before the From Date")
    same = agr_plan1(ag_rule(to_date="2026-11-01"))
    check(not same["problems"], f"equal dates: {same['problems']}")
    return "From Date missing red (never defaulted); To Date before red; equal allowed (FSCR: on or after)"


def a_classes():
    has(agr_plan1(ag_rule(classes=[{"characteristic": "L.INTERFACE_LINE_ATTRIBUTE2"}])), "classes", "Class row 1: Transaction Class is missing")
    has(agr_plan1(ag_rule(classes=[{"transaction_class": "Sales Invoice"}])), "classes", "isn't one of: Invoice")
    has(agr_plan1(ag_rule(classes=[{"transaction_class": "Invoice"}, {"transaction_class": "invoice"}])), "classes",
        "Invoice is listed twice")
    has(agr_plan1(ag_rule(classes=[{"transaction_class": "Invoice", "characteristic": "L.INTERFACE_LINE_ATTRIBUTE2"},
                                   {"transaction_class": "Invoice", "characteristic": "L.INTERFACE_LINE_ATTRIBUTE2"}])),
        "classes", "characteristic L.INTERFACE_LINE_ATTRIBUTE2 is listed twice under Invoice")
    both = agr_plan1(ag_rule(classes=[{"transaction_class": "I"}, {"transaction_class": "Invoice",
                                                                   "characteristic": "L.INTERFACE_LINE_ATTRIBUTE2"}]))
    check(not both["problems"] and "1 transaction class:" in both["summary"], f"class + characteristic: {both}")
    none = agr_plan1(ag_rule(classes=[]))
    check(not none["problems"] and "no transaction class rows" in none["summary"], f"no classes: {none}")
    return "class missing / unknown / twice, characteristic twice: red; code I + characteristic row = one class; none: note"


def a_characteristic():
    res = agr_plan1(ag_rule(classes=[{"transaction_class": "Invoice", "characteristic": "PURCHASE_ORDER"}]))
    t = has(res, "classes", "no grouping rule in Oracle uses characteristic 'PURCHASE_ORDER'")
    p = next(x for x in res["problems"] if "PURCHASE_ORDER" in x["text"])
    check("L.INTERFACE_LINE_ATTRIBUTE1" in p["fix"] and p["row"] == 1, f"fix / row: {p}")
    low = agr_plan1(ag_rule(classes=[{"transaction_class": "Invoice", "characteristic": "l.interface_line_attribute1"}]))
    check(any("L.INTERFACE_LINE_ATTRIBUTE1" in x["suggestions"] for x in low["problems"]), f"capitals suggestion {low['problems']}")
    return t[:70] + "...: red, fix lists Oracle's names; capitals suggest the exact name"


def a_existing():
    res = agr_plan1(ag_rule("CORSAIR DISTRIBUTION BY SALES ORDER"))
    check(res["status"] == "exists" and "skipped" in (res["skipped"] or ""), f"exists {res}")
    low = agr_cmd("--plan", [ag_rule("Corsair Distribution By Sales Order")])["results"][0]
    check(low["status"] == "new" and "differs only in capitals" in low["found"].get("name", ""), f"capitals {low}")
    twice = agr_cmd("--plan", [ag_rule(), ag_rule()])["results"]
    check(not twice[0]["problems"], "first of two flagged")
    has(twice[1], "name", "listed twice")
    return "existing name skipped; capitals-only match yellow; twice in the sheet red on the later row"


def a_refused_at_create():
    agr_pod()
    r = ag_rule("CORSAIR CONSOLIDATED OEM", classes=[{"transaction_class": "Invoice",
                                                      "characteristic": "L.INTERFACE_LINE_ATTRIBUTE7"}])

    def go():
        job = start([agr_record(r)])
        it = job["items"][0]
        q = it.get("question") or {}
        check(job["state"] == "asking" and q.get("field") == "characteristic" and "L.INTERFACE_LINE_ATTRIBUTE2" in q.get("suggestions", []),
              f"question {job['state']} {q}")
        check(it["result"]["error"]["detail"]["saved"] == "no", "saved state")
        server.answer_question(job, it["n"], "L.INTERFACE_LINE_ATTRIBUTE2")
        settle(job)
        check(it["state"] == "done" and it["request"]["classes"][0]["characteristic"] == "L.INTERFACE_LINE_ATTRIBUTE2"
              and q["state"] == "answered", f"after the answer: {it['state']} {(it.get('result') or {}).get('text')}")
        return job
    agr_real(go)
    return "Oracle refused ATTRIBUTE7 (stub: consolidated billing only): asked, answered ATTRIBUTE2, created"


def a_entity_order():
    notes = []
    for order, names in (("reversed", AGR_ORDER[::-1]), ("shuffled", [AGR_ORDER[i] for i in (1, 2, 0)])):
        agr_pod(order=order)
        r = agr_cmd("--run-batch", [ag_rule(f"CORSAIR AMD BY PO {order[:3].upper()}")])["results"][0]
        check(r["ok"] and "every value as sent" in r["text"], f"{order}: {r}")
        agr_sent_ok(names)
        notes.append(order)
    return "template entity order " + " and ".join(notes) + ": file follows it, created and read back as sent"


def a_layout_stops():
    agr_pod(template="no_request")
    got = agr_cmd("--plan", [ag_rule()])
    check(not got["ok"] and got["text"] == apkg.LAYOUT_TEXT and "ORA_AR_AI_GRP_TXN_REQUEST" in got["detail"], f"{got}")
    agr_pod(template="other_release")
    got = agr_cmd("--plan", [ag_rule()])
    check(not got["ok"] and "release" in got["detail"], f"{got}")
    agr_pod(template="refused")
    got = agr_cmd("--plan", [ag_rule()])
    check(got["ok"] and got["layout"]["source"] == "data" and "current data file" in got["results"][0]["summary"], f"{got}")
    return "no characteristic entity / other release: plain stop; template refused: data file layout, said so"


def a_route_refused():
    agr_pod(route="refused")
    job = agr_real(lambda: start([agr_record(ag_rule("CORSAIR NVIDIA BY PO"))]))
    it = job["items"][0]
    seg = log_text().split(f"job {job['id']} queued")[-1]
    check(it["state"] == "failed" and it["result"]["error"]["code"] == "SETUP_NEEDED"
          and "no other way was tried" in it["result"]["text"], f"{it['state']} {it.get('result')}")
    check("repair attempt" not in seg and not it.get("question"), "repaired or asked")
    return "plain card (route refused, nothing created, no other way tried); no repair, no question"


def a_check_cant_run():
    agr_pod(check="fails")
    rec, jobs = agr_record(ag_rule("CORSAIR INTEL BY PO")), set(server.JOBS)
    before = log_text().count("couldn't run")
    got = agr_real(lambda: server.oracle_checks([rec]))[0]
    res = {"stops": [], "problems": []}
    server.apply_oracle_check(res, rec, got)
    stop = (res["stops"] or [""])[0]
    check(log_text().count("couldn't run") - before == server.CHECK_RERUNS, "re-runs")
    check("couldn't be read just now for AutoInvoice grouping rules" in stop and res.get("oracle_stops") == res["stops"],
          f"stop {stop!r}")
    check(set(server.JOBS) == jobs, "a run was started")
    return f"{1 + server.CHECK_RERUNS} tries, then under Oracle: {stop[:70]}..."


def ag_sheet(rules_, classes):
    """A sheet made by the page's own generator (Receivables area), rows filled by column label."""
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(workbook.make_template(area="Receivables")))
    for tab, rows in (("AutoInvoice Grouping Rules", rules_), ("Grouping Rule Classes", classes)):
        ws = wb[tab]
        col = {str(c.value).rstrip(" *"): c.column for c in ws[2] if c.value}
        for i, r in enumerate(rows):
            for k, v in r.items():
                ws.cell(4 + i, col[k], v)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def ag_preview(data):
    res = server.offline_check(data, "2026-11-01", None)
    if res["records"] and not res["stops"]:
        for r, got in zip(res["records"], agr_real(lambda: server.oracle_checks(res["records"]))):
            server.apply_oracle_check(res, r, got)
    for r in res["records"]:
        r["ok"] = not r["problems"]
    res["ok"] = bool(res["records"]) and not res["stops"] and not res["problems"]
    return res


AG_RULES = [{"Name": OEM, "Item Description": "One invoice per OEM order reference for Intel, AMD and NVIDIA",
             "From Date": "2026-11-01"},
            {"Name": "CORSAIR RMA CREDITS BY SALES ORDER", "Item Description": "RMA credit memos, one per sales order",
             "From Date": "2026-11-01"},
            {"Name": "CORSAIR DISTRIBUTION BY SALES ORDER", "From Date": "2026-11-01"},
            {"Name": "ORA_CORSAIR INTEL", "From Date": "2026-11-01"},
            {"Name": "CORSAIR AMD REBATE DEBITS", "Item Description": "Debit memos for AMD volume rebate adjustments"}]
AG_CLASSES = [{"Grouping Rule Name": OEM, "Transaction Class": "Invoice", "Characteristic": "L.INTERFACE_LINE_ATTRIBUTE1"},
              {"Grouping Rule Name": OEM, "Transaction Class": "Debit Memo"},
              {"Grouping Rule Name": OEM, "Transaction Class": "Credit Memo"},
              {"Grouping Rule Name": "CORSAIR RMA CREDITS BY SALES ORDER", "Transaction Class": "Credit Memo",
               "Characteristic": "RMA_NUMBER"},
              {"Grouping Rule Name": "CORSAIR DISTRIBUTION BY SALES ORDER", "Transaction Class": "Invoice"},
              {"Grouping Rule Name": "ORA_CORSAIR INTEL", "Transaction Class": "Invoice"},
              {"Grouping Rule Name": "CORSAIR AMD REBATE DEBITS", "Transaction Class": "Debit Memo"}]


def a_preview():
    agr_pod()
    res = ag_preview(ag_sheet(AG_RULES, AG_CLASSES))
    by = {r["name"]: r for r in res["records"]}
    check(by[OEM]["ok"] and "3 transaction classes" in (by[OEM].get("oracle_summary") or ""), f"good rule {by[OEM]}")
    rma = by["CORSAIR RMA CREDITS BY SALES ORDER"]["problems"]
    check(any(p["tab"] == "Grouping Rule Classes" and p["row"] == 7 and "RMA_NUMBER" in p["text"] for p in rma),
          f"unknown characteristic on its class row: {rma}")
    check(by["CORSAIR DISTRIBUTION BY SALES ORDER"].get("skipped") and by["CORSAIR DISTRIBUTION BY SALES ORDER"]["ok"],
          "existing skipped")
    check(any("ORA_" in p["text"] for p in by["ORA_CORSAIR INTEL"]["problems"]), "ORA_ prefix")
    check(any(p.get("column") == "From Date" for p in by["CORSAIR AMD REBATE DEBITS"]["problems"]), "From Date required")
    check(not res["ok"] and [m["name"] for m in res["modules"] if m["count"]] == [AGR]
          and all("no rows for this" in (m["text"] or "") for m in res["modules"] if m["name"] != AGR),
          f"modules {res['modules']}")
    return ("good OK with summary; unknown characteristic red on its class row (7); existing skipped; ORA_ red; "
            "From Date red; only this module has rows (the other Receivables module: empty-module line)")


def a_units():
    """Layout units against ETIA-TEST's real template (headers and metadata saved 2026-11-01)."""
    tpl_b = io.BytesIO()
    with zipfile.ZipFile(tpl_b, "w") as zo:
        for n in AGR_MEMBERS:
            zo.writestr(n, (POD_LAYOUT / n).read_bytes())
    tpl = zipfile.ZipFile(io.BytesIO(tpl_b.getvalue()))
    lay = apkg.read_layout(tpl_b.getvalue())
    check(lay.order() == AGR_ORDER and lay.release == "11.13.26.10.0", f"order {lay.order()}")
    rule, probs = arules.check(ag_rule())
    check(not probs, f"rules {probs}")
    data = apkg.build_zip(lay, apkg.rule_rows(rule))
    z = zipfile.ZipFile(io.BytesIO(data))
    check(z.namelist() == tpl.namelist() and z.read(apkg.METADATA) == tpl.read(apkg.METADATA), "members / metadata")
    _, mine = apkg.read_rows(data)
    check(mine["ORA_AR_AI_GRP_TXN_REQUEST"][0]["ORA_AR_AI_GRP_TXN_TYPE.Class11"] == "I"
          and [c["Class11"] for c in mine["ORA_AR_AI_GRP_TXN_TYPE"]] == ["I", "D", "C"], f"rows {mine}")
    sent = {OEM: {e: list(rs) for e, rs in mine.items()}}
    after = {e: [dict(r, **({"StartDate": "2026/11/01"} if e == "AR_AI_GROUPING_RULE" else {})) for r in rs]
             for e, rs in mine.items()}
    res, changed = apkg.reconcile(lay, sent, {e: [] for e in mine}, after)
    check(res[OEM]["saved"] and not res[OEM]["diffs"] and not changed, f"reconcile {res}")
    dropped = dict(after, ORA_AR_AI_GRP_TXN_REQUEST=[])            # Oracle dropped an unknown characteristic
    res2, _ = apkg.reconcile(lay, sent, {e: [] for e in mine}, dropped)
    check(res2[OEM]["saved"] and any("L.INTERFACE_LINE_ATTRIBUTE1" in d for d in res2[OEM]["diffs"]), f"dropped {res2}")

    def variant(member, old, new):
        b = io.BytesIO()
        with zipfile.ZipFile(b, "w") as zo:
            for n in tpl.namelist():
                zo.writestr(n, tpl.read(n).replace(old, new) if n == member else tpl.read(n))
        return b.getvalue()
    lay3 = apkg.read_layout(variant("ORA_AR_AI_GRP_TXN_TYPE.csv", b'"LastUpdatedBy"', b'"LastUpdatedBy","AR_AI_GROUPING_RULE.Extra"'))
    first = zipfile.ZipFile(io.BytesIO(apkg.build_zip(lay3, apkg.rule_rows(rule)))).read(
        "ORA_AR_AI_GRP_TXN_TYPE.csv").decode().splitlines()
    check(first[0].endswith('"AR_AI_GROUPING_RULE.Extra"') and first[1].endswith('"",""'), "extra link column")
    try:
        apkg.read_layout(variant("AR_AI_GROUPING_RULE.csv", b'"ConsBillingUseFlag"', b'"ConsBillingUseFlag","Surprise"'))
        check(False, "an unknown column was accepted")
    except apkg.LayoutError as e:
        check("Surprise" in e.why, e.why)
    return ("ETIA-TEST template read (entities TYPE, REQUEST, RULE; zip RULE, TYPE, REQUEST); file = its members and metadata byte for byte; slash date = ISO on read-back; a "
            "characteristic Oracle dropped is a mismatch; extra link column kept empty; unknown column stops")


AGR_CASES = [("Happy path, Corsair OEM rule", a_happy), ("Name and description rules", a_name),
             ("From / To Date", a_dates), ("Class rows", a_classes),
             ("Characteristic not in Oracle -> red", a_characteristic),
             ("Existing / capitals / twice", a_existing),
             ("Refused value at Create -> pause and ask", a_refused_at_create),
             ("Template with a different entity order", a_entity_order),
             ("Template not as known -> plain stop", a_layout_stops),
             ("Route refused -> plain card, no other way", a_route_refused),
             ("Check can't run -> re-runs, real reason", a_check_cant_run),
             ("Preview of a Corsair sheet through the page", a_preview),
             ("Layout units on ETIA-TEST's real template", a_units)]
agr_table, agr_fails = [], 0
for title, fn in AGR_CASES:
    try:
        note, ok = fn(), "PASS"
    except Exception as e:  # noqa: BLE001
        note, ok = f"{type(e).__name__}: {e}"[:400], "FAIL"
        agr_fails += 1
    agr_table.append(("Grouping rules folder", title, ok, note))
    print(f"{ok}  {'AGR folder':15} {title:45} {note}", flush=True)


# ---------------------------------------------------------------- Transaction Sources: the real folder (2026-11-01)
# The folder's real code with Oracle replaced by stub_transaction_sources.py (layout: ETIA-TEST's real template once the
# read-only check saved it, else the STAND-IN). The grouping rules the stub knows are the grouping rules stub's state, so
# a rule created by that stub earlier in a test is in "Oracle". Offline sample names follow the Corsair story.

TS = "Transaction Sources"
STUB_TS = str(HERE / "stub_transaction_sources.py")
sys.path.insert(0, str(ROOT / TS))
import ts_package as tpkg  # noqa: E402
import ts_rules as trules  # noqa: E402

TS_LAYOUT = next(p for p in (ROOT / TS / "manual-notes" / "pod_layout_etia_test",
                             ROOT / TS / "manual-notes" / "standin_layout_NOT_FROM_ORACLE") if (p / "members.txt").exists())
TS_MEMBERS = (TS_LAYOUT / "members.txt").read_text(encoding="utf-8").split()
OEM_RULE = "CORSAIR OEM BY ORDER REFERENCE"


def ts_pod(**control):
    """A fresh stub pod (two standing sources; the grouping rules stub's standing rules) with these switches."""
    for f in ("ts_pod.json", "ts_sent.zip", "agr_pod.json", "agr_sent.zip"):
        (WORK / f).unlink(missing_ok=True)
    (WORK / "ts_stub.json").write_text(json.dumps(control), encoding="utf-8")
    (WORK / "agr_stub.json").write_text("{}", encoding="utf-8")


def ts_cmd(cmd, payload):
    p = subprocess.run([server.PY, STUB_TS, cmd, json.dumps(payload)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=server.ENV_CHILD, cwd=str(ROOT), timeout=300)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise AssertionError(f"{cmd} gave no answer: {p.stderr[-600:]}")


def ts_src(name="CORSAIR MANUAL INVOICES", **kw):
    s = {"name": name, "set_code": "COMMON", "description": "Manual invoices for OEM price adjustments and samples",
         "source_type": "Manual", "from_date": "2026-11-01", "auto_numbering": "Yes", "last_number": 500000}
    s.update(kw)
    return {k: v for k, v in s.items() if v is not None}


def ts_imported(name="CORSAIR OEM ORDERS", rule="DEFAULT", **kw):
    return ts_src(name, description="Imported OEM order lines from Order Management for Intel, AMD and NVIDIA",
                  source_type="Imported", last_number=100000, grouping_rule=rule, **kw)


def ts_plan1(s, **control):
    ts_pod(**control)
    got = ts_cmd("--plan", [s])
    check(got.get("ok"), f"the check didn't run: {got}")
    return got["results"][0]


def ts_record(s):
    return {"folder": TS, "group": TS, "request": s, "title": s["name"], "name": s["name"],
            "rows": {"record": [TS, 4], "children": []}}


def both_real(fn):
    """Run fn with the page's server using the real grouping rules and transaction sources folders (stubs)."""
    old = (server.FOLDERS[AGR]["script"], server.FOLDERS[TS]["script"])
    server.FOLDERS[AGR]["script"], server.FOLDERS[TS]["script"] = STUB_AGR, STUB_TS
    try:
        return fn()
    finally:
        server.FOLDERS[AGR]["script"], server.FOLDERS[TS]["script"] = old


def ts_sent_ok():
    z = zipfile.ZipFile(WORK / "ts_sent.zip")
    check(z.namelist() == TS_MEMBERS, f"member order {z.namelist()}")
    check(z.read(tpkg.METADATA) == (TS_LAYOUT / tpkg.METADATA).read_bytes(), "metadata not copied byte for byte")
    lay, rows = tpkg.read_rows((WORK / "ts_sent.zip").read_bytes())
    check(not rows["AR_BATCH_SOURCE"], "rows sent in AR_BATCH_SOURCE")
    for r in rows["ORA_AR_TXN_BATCH_SOURCE"]:
        check(not any(r.get(c) for c in tpkg.AUDIT), "an audit or derived column is filled")
        check(re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["StartDate"]), f"StartDate {r['StartDate']}")
    return rows["ORA_AR_TXN_BATCH_SOURCE"]


def t_happy():
    ts_pod()
    s = ts_src()
    res = ts_cmd("--plan", [s])["results"][0]
    check(res["status"] == "new" and not res["problems"] and "Manual source" in (res["summary"] or ""), f"plan {res}")
    job = both_real(lambda: start([ts_record(s)]))
    it = job["items"][0]
    check(it["state"] == "done" and "every value as sent" in it["result"]["text"], f"create: {it['state']} {it.get('result')}")
    sent = ts_sent_ok()
    check(len(sent) == 1 and sent[0]["BatchSourceType"] == "INV" and sent[0]["LastBatchNum"] == "500000"
          and sent[0]["AutoTrxNumberingFlag"] == "Y" and sent[0]["InvalidLinesRule"] == "Reject", f"sent {sent}")
    again = both_real(lambda: start([ts_record(s)]))["items"][0]
    check(again["state"] == "done" and again["result"].get("skipped"), f"rerun: {again.get('result')}")
    return "checked, created (1 row, create target only), read back from AR_BATCH_SOURCE as sent; rerun skipped"


def t_rules():
    has(ts_plan1(ts_src("ORA_CORSAIR MANUAL")), "name", "can't start with ORA_")
    has(ts_plan1(ts_src(" CORSAIR MANUAL")), "name", "starts or ends with a space")
    has(ts_plan1(ts_src(description=None)), "description", "Item Description is missing")
    has(ts_plan1(ts_src(from_date=None)), "from_date", "never filled in for you")
    has(ts_plan1(ts_src(last_number=None)), "last_number", "never filled in for you")
    has(ts_plan1(ts_src(last_number=0)), "last_number", "1 or more")
    has(ts_plan1(ts_src(last_number=1.5)), "last_number", "1 or more")
    has(ts_plan1(ts_src(auto_numbering="No")), "last_number", "only applies with automatic numbering")
    ok = ts_plan1(ts_src(auto_numbering="No", last_number=None))
    check(not ok["problems"], f"no numbering: {ok}")
    has(ts_plan1(ts_src(source_type="Online")), "source_type", "two choices")
    has(ts_plan1(ts_src(status="Closed")), "status", "isn't one of")
    filled = ts_plan1(ts_src(source_type=None, status=None, invalid_lines=None, auto_numbering=None))
    check(filled["fills"] == {"source_type": "Manual", "status": "Active", "invalid_lines": "Reject Invoice",
                              "auto_numbering": "Yes"}, f"defaults {filled['fills']}")
    return ("ORA_, outer space, no description, no From Date, Last Number missing / 0 / 1.5 / with numbering No, bad "
            "Type and Status: red; FSCR's four defaults filled in and shown")


def t_existing():
    res = ts_plan1(ts_src("Manual"))              # only in Oracle's source list, not in the data file (as ETIA-TEST)
    check(res["status"] == "exists" and "skipped" in (res["skipped"] or ""), f"exists {res}")
    doo = ts_cmd("--plan", [ts_src("Distributed Order Orchestration")])["results"][0]   # in the data file
    check(doo["status"] == "exists", f"data file source {doo}")
    low = ts_cmd("--plan", [ts_src("MANUAL")])["results"][0]
    check(low["status"] == "new" and "differs only in capitals" in low["found"].get("name", ""), f"capitals {low}")
    other = ts_cmd("--plan", [ts_src("Manual", set_code="ENTERPRISE")])["results"][0]
    check(other["status"] == "new", f"other set {other}")
    twice = ts_cmd("--plan", [ts_src(), ts_src()])["results"]
    check(not twice[0]["problems"], "first of two flagged")
    has(twice[1], "name", "listed twice for set COMMON")
    bad_set = ts_cmd("--plan", [ts_src(set_code="CORSAIR_SET")])["results"][0]
    has(bad_set, "set_code", "isn't one of Oracle's reference data sets")
    return ("existing source skipped, from the source list and from the data file; capitals yellow; other set new; "
            "twice red; unknown set red")


def t_rule_oracle():
    ok = ts_plan1(ts_imported(rule="DEFAULT"))
    check(not ok["problems"] and "grouping rule DEFAULT" in ok["summary"], f"rule in Oracle {ok}")
    res = ts_plan1(ts_imported(rule=OEM_RULE))
    t = has(res, "grouping_rule", "isn't in Oracle and isn't on this sheet")
    check("DEFAULT" in next(p["fix"] for p in res["problems"] if p["key"] == "grouping_rule"), "fix lists Oracle's rules")
    has(ts_plan1(ts_src(grouping_rule="DEFAULT")), "grouping_rule", "only applies to an AutoInvoice source")
    return "rule already in Oracle: OK; rule nowhere: red, fix lists Oracle's rules; rule on a Manual source: red"


def t_rule_pending():
    ts_pod()
    s = ts_imported(rule=OEM_RULE, grouping_rule_pending=True)
    res = ts_cmd("--plan", [s])["results"][0]
    check(res["status"] == "new" and "created first" in res["found"].get("grouping_rule", ""), f"pending plan {res}")
    got = ts_cmd("--run-batch", [s])["results"][0]
    check(not got["ok"] and "isn't in Oracle yet, so this source was not sent" in got["text"]
          and got["error"]["detail"]["saved"] == "no", f"pending, rule missing at Create {got}")
    check(not (WORK / "ts_sent.zip").exists(), "a file was sent")
    return "rule on the sheet: preview OK with 'created first'; at Create the rule still missing: not sent, nothing saved"


def t_refused_at_create():
    ts_pod()
    s = ts_src("CORSAIR NVIDIA SAMPLES", set_code="ZZ_NOT_FOR_TS")

    def go():
        job = start([ts_record(s)])
        it = job["items"][0]
        q = it.get("question") or {}
        check(job["state"] == "asking" and q.get("field") == "set_code" and "COMMON" in q.get("suggestions", []),
              f"question {job['state']} {q}")
        server.answer_question(job, it["n"], "COMMON")
        settle(job)
        check(it["state"] == "done" and it["request"]["set_code"] == "COMMON", f"after {it['state']}")
        return job
    both_real(go)
    return "Oracle refused set ZZ_NOT_FOR_TS: asked (Set Code, COMMON suggested), answered, created"


def t_entity_order():
    ts_pod(order="reversed")
    r = ts_cmd("--run-batch", [ts_src("CORSAIR AMD SAMPLES")])["results"][0]
    check(r["ok"] and "every value as sent" in r["text"], f"reversed: {r}")
    meta = zipfile.ZipFile(WORK / "ts_sent.zip").read(tpkg.METADATA)
    block = meta.split(b"<MigrationProcessBusinessObjectCSVMetadata1>")[1].split(b"</MigrationProcessBusinessObjectCSVMetadata1>")[0]
    names = re.findall(rb"<BusinessObjectShortName>(\w+)</BusinessObjectShortName>", block)
    lay = tpkg.read_layout((WORK / "ts_sent.zip").read_bytes())
    check([n.decode() for n in names] == lay.order(), "metadata order not followed")
    return f"template entity order reversed ({', '.join(lay.order())}): file follows it, created and read back"


def t_layout_stops():
    ts_pod(template="no_persisted")
    got = ts_cmd("--plan", [ts_src()])
    check(not got["ok"] and got["text"] == tpkg.LAYOUT_TEXT and "AR_BATCH_SOURCE" in got["detail"], f"{got}")
    ts_pod(template="other_release")
    got = ts_cmd("--plan", [ts_src()])
    check(not got["ok"] and "release" in got["detail"], f"{got}")
    ts_pod(template="refused")
    got = ts_cmd("--plan", [ts_src()])
    check(got["ok"] and got["layout"]["source"] == "data" and "current data file" in got["results"][0]["summary"], f"{got}")
    return "no AR_BATCH_SOURCE / other release: plain stop; template refused: data file layout, said so"


def t_route_refused():
    ts_pod(route="refused")
    job = both_real(lambda: start([ts_record(ts_src("CORSAIR INTEL SAMPLES"))]))
    it = job["items"][0]
    seg = log_text().split(f"job {job['id']} queued")[-1]
    check(it["state"] == "failed" and it["result"]["error"]["code"] == "SETUP_NEEDED"
          and "no other way was tried" in it["result"]["text"], f"{it['state']} {it.get('result')}")
    check("repair attempt" not in seg and not it.get("question"), "repaired or asked")
    return "plain card (route refused, nothing created, no other way tried); no repair, no question"


def t_check_cant_run():
    ts_pod(check="fails")
    rec, jobs = ts_record(ts_src("CORSAIR CHECK")), set(server.JOBS)
    before = log_text().count("couldn't run")
    got = both_real(lambda: server.oracle_checks([rec]))[0]
    res = {"stops": [], "problems": []}
    server.apply_oracle_check(res, rec, got)
    stop = (res["stops"] or [""])[0]
    check(log_text().count("couldn't run") - before == server.CHECK_RERUNS, "re-runs")
    check("couldn't be read just now for transaction sources" in stop and set(server.JOBS) == jobs, f"stop {stop!r}")
    return f"{1 + server.CHECK_RERUNS} tries, then under Oracle: {stop[:60]}..."


def dep_records(rule_classes):
    rule = {"name": OEM_RULE, "description": "One invoice per OEM order reference for Intel, AMD and NVIDIA",
            "from_date": "2026-11-01", "classes": rule_classes}
    src = ts_imported(rule=OEM_RULE, grouping_rule_pending=True)
    return [dict(agr_record(rule)), dict(ts_record(src))]


def t_dependency_run():
    ts_pod()
    job = both_real(lambda: start(dep_records([{"transaction_class": "Invoice",
                                                "characteristic": "L.INTERFACE_LINE_ATTRIBUTE1"}])))
    r, s = job["items"]
    check(r["state"] == "done" and s["state"] == "done" and "every value as sent" in s["result"]["text"],
          f"both: {r['state']} {s['state']} {(s.get('result') or {}).get('text')}")
    sent = ts_sent_ok()
    check(sent[0]["GroupName"] == OEM_RULE, f"GroupName {sent}")
    ts_pod()
    job = both_real(lambda: start(dep_records([{"transaction_class": "Invoice",
                                                "characteristic": "L.INTERFACE_LINE_ATTRIBUTE7"}])))
    r, s = job["items"]
    check((r.get("question") or {}).get("state") == "open" and s.get("held"), f"held: {r['state']} {s.get('hold_text')}")
    server.answer_question(job, r["n"], skip=True)
    settle(job)
    check(s["state"] == "failed" and "Not sent" in s["result"]["text"] and not (WORK / "ts_sent.zip").exists(),
          f"after skip: {s['state']} {(s.get('result') or {}).get('text')}")
    return ("rule + source in one upload: rule created first, source then created with it; rule refused and skipped by "
            "the user: source held, then not sent (nothing sent for it)")


def ts_sheet(rules_, classes, sources):
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(workbook.make_template(area="Receivables")))
    for tab, rows in (("AutoInvoice Grouping Rules", rules_), ("Grouping Rule Classes", classes),
                      ("Transaction Sources", sources)):
        ws = wb[tab]
        col = {str(c.value).rstrip(" *"): c.column for c in ws[2] if c.value}
        for i, r in enumerate(rows):
            for k, v in r.items():
                ws.cell(4 + i, col[k], v)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def t_preview():
    ts_pod()
    srcs = [{"Name": "CORSAIR OEM ORDERS", "Set Code": "COMMON", "Item Description": "Imported OEM order lines",
             "Type": "Imported", "From Date": "2026-11-01", "Last Number": 100000, "Grouping Rule": OEM_RULE},
            {"Name": "CORSAIR RMA RETURNS", "Set Code": "COMMON", "Item Description": "Imported RMA returns",
             "Type": "Imported", "From Date": "2026-11-01", "Last Number": 1, "Grouping Rule": "CORSAIR RMA BY ORDER"},
            {"Name": "CORSAIR MANUAL INVOICES", "Set Code": "COMMON", "Item Description": "Manual invoices",
             "From Date": "2026-11-01", "Last Number": 500000, "Grouping Rule": "DEFAULT"},
            {"Name": "CORSAIR SAMPLES", "Set Code": "COMMON", "From Date": "2026-11-01", "Last Number": 1}]
    data = ts_sheet([{"Name": OEM_RULE, "From Date": "2026-11-01"}],
                    [{"Grouping Rule Name": OEM_RULE, "Transaction Class": "Invoice",
                      "Characteristic": "L.INTERFACE_LINE_ATTRIBUTE1"}], srcs)
    res = server.offline_check(data, "2026-11-01", None)
    if res["records"] and not res["stops"]:
        for r, got in zip(res["records"], both_real(lambda: server.oracle_checks(res["records"]))):
            server.apply_oracle_check(res, r, got)
    by = {r["name"]: r for r in res["records"]}
    oem = by["CORSAIR OEM ORDERS"]
    check(not oem["problems"] and oem["request"].get("grouping_rule_pending")
          and any("is created first" in (f.get("note") or "") for f in oem["fields"]), f"pending source {oem}")
    check(any("isn't in Oracle and isn't on this sheet" in p["text"] for p in by["CORSAIR RMA RETURNS"]["problems"]),
          "rule nowhere")
    check(any("only applies to an AutoInvoice source" in p["text"] for p in by["CORSAIR MANUAL INVOICES"]["problems"]),
          "rule on Manual")
    check(any(p.get("column") == "Item Description" for p in by["CORSAIR SAMPLES"]["problems"]), "description required")
    names = [m["name"] for m in res["modules"] if m["count"]]
    check(names == [AGR, TS], f"modules {res['modules']}")
    return ("rule on the sheet: source OK with 'created first' note; rule nowhere: red; rule on Manual: red; "
            "no description: red; modules grouping rules then sources")


def t_units():
    tpl_b = io.BytesIO()
    with zipfile.ZipFile(tpl_b, "w") as zo:
        for n in TS_MEMBERS:
            zo.writestr(n, (TS_LAYOUT / n).read_bytes())
    lay = tpkg.read_layout(tpl_b.getvalue())
    s, probs = trules.check(ts_imported(rule="DEFAULT"))
    check(not probs, f"rules {probs}")
    data = tpkg.build_zip(lay, tpkg.source_rows(s))
    z = zipfile.ZipFile(io.BytesIO(data))
    tpl = zipfile.ZipFile(io.BytesIO(tpl_b.getvalue()))
    check(z.namelist() == tpl.namelist() and z.read(tpkg.METADATA) == tpl.read(tpkg.METADATA), "members / metadata")
    check(z.read("AR_BATCH_SOURCE.csv") == tpl.read("AR_BATCH_SOURCE.csv"), "AR_BATCH_SOURCE not header-only")
    _, mine = tpkg.read_rows(data)
    row = mine["ORA_AR_TXN_BATCH_SOURCE"][0]
    key = (row["Name"], row["SetCode"])
    persisted = {c: (v.replace("-", "/") if c == "StartDate" else v) for c, v in row.items()
                 if c in lay.entities["AR_BATCH_SOURCE"]["header"]}
    after = {"ORA_AR_TXN_BATCH_SOURCE": [], "AR_BATCH_SOURCE": [persisted]}
    res, changed = tpkg.reconcile(lay, {key: mine}, {"ORA_AR_TXN_BATCH_SOURCE": [], "AR_BATCH_SOURCE": []}, after)
    check(res[key]["saved"] and not res[key]["diffs"] and res[key]["entity"] == "AR_BATCH_SOURCE" and not changed,
          f"reconcile {res}")
    res2, _ = tpkg.reconcile(lay, {key: mine}, after, {"ORA_AR_TXN_BATCH_SOURCE": [], "AR_BATCH_SOURCE": []})
    check(not res2[key]["saved"], "missing source counted as saved")
    names = tpkg.rule_names(_rules_zip(["DEFAULT", OEM_RULE]))
    check(names == sorted(["DEFAULT", OEM_RULE]), f"rule names {names}")
    return ("template read (" + ", ".join(lay.order()) + "); file = its members and metadata, AR_BATCH_SOURCE header only; "
            "read-back finds the source in AR_BATCH_SOURCE (slash date = ISO); a missing one isn't saved; rule names read")


def _rules_zip(names):
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("AR_AI_GROUPING_RULE.csv", '"Name","StartDate"\n' + "".join(f'"{n}","1952/01/01"\n' for n in names))
    return b.getvalue()


def t_hidden_readback():
    ts_pod(export_hides_new=True)
    r = ts_cmd("--run-batch", [ts_src("CORSAIR AMD REBATES")])["results"][0]
    check(r["ok"] and "only its name, set and description were checked" in r["text"], f"source list read-back {r}")
    again = ts_cmd("--run-batch", [ts_src("CORSAIR AMD REBATES")])["results"][0]
    check(again.get("skipped"), f"rerun {again}")
    ts_pod(export_hides_new=True)
    bad = ts_cmd("--run-batch", [ts_src("CORSAIR AMD REBATES", set_code="ZZ_NOT_FOR_TS")])["results"][0]
    check(not bad["ok"] and bad["error"]["detail"]["saved"] == "no", f"refused {bad}")
    return ("a new source the data file doesn't list: found in Oracle's source list, name/set/description checked and "
            "said so; rerun skipped; a refused one still 'nothing saved'")


TS_CASES = [("Happy path, Manual source", t_happy), ("Read-back when the data file hides it", t_hidden_readback), ("Field rules and FSCR defaults", t_rules),
            ("Existing / capitals / other set / twice / set", t_existing),
            ("Grouping rule already in Oracle / nowhere / Manual", t_rule_oracle),
            ("Grouping rule on the sheet (pending)", t_rule_pending),
            ("Refused value at Create -> pause and ask", t_refused_at_create),
            ("Template with a different entity order", t_entity_order),
            ("Template not as known -> plain stop", t_layout_stops),
            ("Route refused -> plain card, no other way", t_route_refused),
            ("Check can't run -> re-runs, real reason", t_check_cant_run),
            ("Rule + source in one upload (depends_on)", t_dependency_run),
            ("Preview of a sheet with both modules", t_preview), ("Layout units", t_units)]
ts_table, ts_fails = [], 0
for title, fn in TS_CASES:
    try:
        note, ok = fn(), "PASS"
    except Exception as e:  # noqa: BLE001
        note, ok = f"{type(e).__name__}: {e}"[:400], "FAIL"
        ts_fails += 1
    ts_table.append(("Transaction sources folder", title, ok, note))
    print(f"{ok}  {'TS folder':15} {title:45} {note}", flush=True)
# ---------------------------------------------------------------- Transaction Types: the real folder (2026-11-02)
# The folder's real code with Oracle replaced by stub_transaction_types.py (layout: ETIA-TEST's real template once the
# read-only check saved it, else the STAND-IN). The Receivables payment terms the stub knows are the payment terms
# stub's state, so a term created by that stub earlier in a test is in "Oracle". Offline names follow the Corsair story.

TT = "Transaction Types"
STUB_TT = str(HERE / "stub_transaction_types.py")
sys.path.insert(0, str(ROOT / TT))
import tt_package as ypkg  # noqa: E402
import tt_rules as yrules  # noqa: E402

TT_LAYOUT = next(p for p in (ROOT / TT / "manual-notes" / "pod_layout_etia_test",
                             ROOT / TT / "manual-notes" / "standin_layout_NOT_FROM_ORACLE") if (p / "members.txt").exists())
TT_MEMBERS = (TT_LAYOUT / "members.txt").read_text(encoding="utf-8").split()
NET45 = "CORSAIR NET 45"
TT_REQUIRED = ("set_code", "trx_class", "status", "from_date", "open_receivable", "post_to_gl", "allow_freight",
               "tax_calculation", "natural_application", "allow_overapplication", "creation_sign",
               "transaction_status", "printing_option")


def tt_pod(**control):
    """A fresh stub pod (its standing types; the payment terms stub's standing terms) with these switches."""
    for f in ("tt_pod.json", "tt_sent.zip", "rpt_pod.json", "rpt_sent.zip"):
        (WORK / f).unlink(missing_ok=True)
    (WORK / "tt_stub.json").write_text(json.dumps(control), encoding="utf-8")
    (WORK / "rpt_stub.json").write_text("{}", encoding="utf-8")


def tt_cmd(cmd, payload):
    p = subprocess.run([server.PY, STUB_TT, cmd, json.dumps(payload)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=server.ENV_CHILD, cwd=str(ROOT), timeout=300)
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        raise AssertionError(f"{cmd} gave no answer: {p.stderr[-600:]}")


def tt_type(name="CORSAIR OEM INVOICE", **kw):
    t = {"name": name, "set_code": "COMMON", "description": "OEM invoices to Intel, AMD and NVIDIA from Order Management",
         "trx_class": "Invoice", "status": "Active", "from_date": "2026-11-01", "open_receivable": "Yes",
         "post_to_gl": "Yes", "allow_freight": "Yes", "tax_calculation": "Yes", "natural_application": "No",
         "allow_overapplication": "No", "creation_sign": "Positive Sign", "transaction_status": "Open",
         "printing_option": "Print"}
    t.update(kw)
    return {k: v for k, v in t.items() if v is not None}


def tt_plan1(t, **control):
    tt_pod(**control)
    got = tt_cmd("--plan", [t])
    check(got.get("ok"), f"the check didn't run: {got}")
    return got["results"][0]


def tt_record(t):
    return {"folder": TT, "group": TT, "request": t, "title": t["name"], "name": t["name"],
            "rows": {"record": [TT, 4], "children": []}}


def tt_real(fn):
    """Run fn with the page's server using the real payment terms and transaction types folders (stubs)."""
    old = (server.FOLDERS[RPT]["script"], server.FOLDERS[TT]["script"])
    server.FOLDERS[RPT]["script"], server.FOLDERS[TT]["script"] = STUB_RPT, STUB_TT
    try:
        return fn()
    finally:
        server.FOLDERS[RPT]["script"], server.FOLDERS[TT]["script"] = old


def tt_sent_ok():
    z = zipfile.ZipFile(WORK / "tt_sent.zip")
    check(z.namelist() == TT_MEMBERS, f"member order {z.namelist()}")
    check(z.read(ypkg.METADATA) == (TT_LAYOUT / ypkg.METADATA).read_bytes(), "metadata not copied byte for byte")
    check(z.read("AR_REF_ACCT_TRX_TYPE.csv") == (TT_LAYOUT / "AR_REF_ACCT_TRX_TYPE.csv").read_bytes(),
          "AR_REF_ACCT_TRX_TYPE is not header-only (accounts must never be sent)")
    lay, rows = ypkg.read_rows((WORK / "tt_sent.zip").read_bytes())
    for r in rows["AR_TRANSACTION_TYPE"]:
        check(not any(r.get(c) for c in ypkg.AUDIT), "an audit column is filled")
        check(re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["StartDate"]), f"StartDate {r['StartDate']}")
        check(not r.get("AllocateTaxFreight") and not r.get("AdjPostToGlFlag"), "an accounting field is filled")
    return rows["AR_TRANSACTION_TYPE"]


def y_happy():
    tt_pod()
    t = tt_type()
    res = tt_cmd("--plan", [t])["results"][0]
    check(res["status"] == "new" and not res["problems"] and "Invoice type" in (res["summary"] or "")
          and not res["fills"], f"plan {res}")
    job = tt_real(lambda: start([tt_record(t)]))
    it = job["items"][0]
    check(it["state"] == "done" and "every value as sent" in it["result"]["text"], f"create: {it['state']} {it.get('result')}")
    sent = tt_sent_ok()
    want = {"Type": "INV", "Status": "A", "CreationSign": "P", "DefaultStatus": "OP", "DefaultPrintingOption": "PRI",
            "AccountingAffectFlag": "Y", "PostToGl": "Y", "AllowFreightFlag": "Y", "TaxCalculationFlag": "Y",
            "NaturalApplicationOnlyFlag": "N", "AllowOverapplicationFlag": "N", "DefaultTermName": ""}
    check(len(sent) == 1 and all(sent[0][k] == v for k, v in want.items()), f"sent {sent}")
    again = tt_real(lambda: start([tt_record(t)]))["items"][0]
    check(again["state"] == "done" and again["result"].get("skipped"), f"rerun: {again.get('result')}")
    return "checked, created (1 row, accounts header only), read back as sent (slash dates); rerun skipped"


def y_rules():
    for k in TT_REQUIRED:                         # FSCR: never defaulted
        res = tt_plan1(tt_type(**{k: None}))
        check(any(p["key"] == k and ("missing" in p["text"]) for p in res["problems"]), f"{k} not asked: {res['problems']}")
    has(tt_plan1(tt_type("X" * 21)), "name", "21 characters; Oracle takes at most 20")
    has(tt_plan1(tt_type(description="d" * 81)), "description", "81 characters; Oracle takes at most 80")
    ok = tt_plan1(tt_type("Y" * 20, description="d" * 80))
    check(not ok["problems"], f"20 / 80 refused {ok['problems']}")
    has(tt_plan1(tt_type(trx_class="Credit Memo")), "trx_class", "isn't offered yet")
    has(tt_plan1(tt_type(trx_class="Debit")), "trx_class", "isn't one of Invoice or Debit Memo")
    dm = tt_plan1(tt_type(trx_class="DM"))
    check(not dm["problems"] and "Debit Memo type" in dm["summary"], f"DM code {dm}")
    has(tt_plan1(tt_type(natural_application="Yes", allow_overapplication="Yes")), "allow_overapplication",
        "can't both be Yes")
    has(tt_plan1(tt_type(creation_sign="Negative Sign")), "creation_sign", "isn't one of Positive Sign")
    has(tt_plan1(tt_type(transaction_status="Closed")), "transaction_status", "isn't one of Open")
    has(tt_plan1(tt_type(status="D")), "status", "isn't one of Active or Inactive")
    has(tt_plan1(tt_type(to_date="2026-10-31")), "to_date", "is before From Date")
    has(tt_plan1(tt_type(post_to_gl="Maybe")), "post_to_gl", "must be Yes or No")
    has(tt_plan1(tt_type(payment_term=NET45)), "payment_term_set", "Payment Term Set is missing")
    has(tt_plan1(tt_type(payment_term_set="COMMON")), "payment_term_set", "only applies with a Payment Term")
    return ("13 required fields each asked (never defaulted); Name 21 / Description 81 red with counts, 20 / 80 OK; "
            "Credit Memo not offered; DM code OK; natural + overapplication; sign, status, D, dates, flags, term pairs")


def y_existing():
    res = tt_plan1(tt_type("Debit Memo"))          # only in Oracle's type list, not in the data file
    check(res["status"] == "exists" and "skipped" in (res["skipped"] or ""), f"exists {res}")
    inv = tt_cmd("--plan", [tt_type("Invoice")])["results"][0]   # in the data file
    check(inv["status"] == "exists", f"data file type {inv}")
    low = tt_cmd("--plan", [tt_type("INVOICE")])["results"][0]
    check(low["status"] == "new" and "differs only in capitals" in low["found"].get("name", ""), f"capitals {low}")
    other = tt_cmd("--plan", [tt_type("Invoice", set_code="ENTERPRISE")])["results"][0]
    check(other["status"] == "new", f"other set {other}")
    twice = tt_cmd("--plan", [tt_type(), tt_type()])["results"]
    check(not twice[0]["problems"], "first of two flagged")
    has(twice[1], "name", "listed twice for set COMMON")
    has(tt_cmd("--plan", [tt_type(set_code="CORSAIR_SET")])["results"][0], "set_code",
        "isn't one of Oracle's reference data sets")
    return "existing type skipped (from the type list and from the data file); capitals yellow; other set new; twice red; unknown set red"


def y_term_oracle():
    ok = tt_plan1(tt_type(payment_term="30 Net", payment_term_set="COMMON"))
    check(not ok["problems"] and "payment term 30 Net (set COMMON)" in ok["summary"], f"term in Oracle {ok}")
    res = tt_plan1(tt_type(payment_term=NET45, payment_term_set="COMMON"))
    has(res, "payment_term", "isn't in Oracle and isn't on this sheet")
    check("30 Net" in next(p["fix"] for p in res["problems"] if p["key"] == "payment_term"), "fix lists Oracle's terms")
    other = tt_plan1(tt_type(payment_term="30 Net", payment_term_set="ENTERPRISE"))
    has(other, "payment_term", "Oracle has it in set COMMON")
    has(tt_plan1(tt_type(payment_term="30 Net", payment_term_set="NO_SUCH_SET")), "payment_term_set",
        "isn't one of Oracle's reference data sets")
    return "term in Oracle: OK; term nowhere: red, fix lists Oracle's terms; term in another set: red, says where; bad term set: red"


def y_term_pending():
    tt_pod()
    t = tt_type(payment_term=NET45, payment_term_set="COMMON", payment_term_pending=True)
    res = tt_cmd("--plan", [t])["results"][0]
    check(res["status"] == "new" and "created first" in res["found"].get("payment_term", ""), f"pending plan {res}")
    got = tt_cmd("--run-batch", [t])["results"][0]
    check(not got["ok"] and "isn't in Oracle yet, so this transaction type was not sent" in got["text"]
          and got["error"]["detail"]["saved"] == "no", f"pending, term missing at Create {got}")
    check(not (WORK / "tt_sent.zip").exists(), "a file was sent")
    return "term on the sheet: preview OK with 'created first'; at Create the term still missing: not sent, nothing saved"


def y_refused_at_create():
    tt_pod()
    t = tt_type("CORSAIR NVIDIA DEBIT", trx_class="Debit Memo", set_code="ZZ_NOT_FOR_TT")

    def go():
        job = start([tt_record(t)])
        it = job["items"][0]
        q = it.get("question") or {}
        check(job["state"] == "asking" and q.get("field") == "set_code" and "COMMON" in q.get("suggestions", []),
              f"question {job['state']} {q}")
        server.answer_question(job, it["n"], "COMMON")
        settle(job)
        check(it["state"] == "done" and it["request"]["set_code"] == "COMMON", f"after {it['state']}")
        return job
    tt_real(go)
    return "Oracle refused set ZZ_NOT_FOR_TT: asked (Set Code, COMMON suggested), answered, created"


def y_entity_order():
    tt_pod(order="reversed")
    r = tt_cmd("--run-batch", [tt_type("CORSAIR AMD INVOICE")])["results"][0]
    check(r["ok"] and "every value as sent" in r["text"], f"reversed: {r}")
    meta = zipfile.ZipFile(WORK / "tt_sent.zip").read(ypkg.METADATA)
    block = meta.split(b"<MigrationProcessBusinessObjectCSVMetadata1>")[1].split(b"</MigrationProcessBusinessObjectCSVMetadata1>")[0]
    names = re.findall(rb"<BusinessObjectShortName>(\w+)</BusinessObjectShortName>", block)
    lay = ypkg.read_layout((WORK / "tt_sent.zip").read_bytes())
    check([n.decode() for n in names] == lay.order(), "metadata order not followed")
    return f"template entity order reversed ({', '.join(lay.order())}): file follows it, created and read back"


def y_layout_stops():
    tt_pod(template="no_accounts")
    got = tt_cmd("--plan", [tt_type()])
    check(not got["ok"] and got["text"] == ypkg.LAYOUT_TEXT and "AR_REF_ACCT_TRX_TYPE" in got["detail"], f"{got}")
    tt_pod(template="other_release")
    got = tt_cmd("--plan", [tt_type()])
    check(not got["ok"] and "release" in got["detail"], f"{got}")
    tt_pod(template="refused")
    got = tt_cmd("--plan", [tt_type()])
    check(got["ok"] and got["layout"]["source"] == "data" and "current data file" in got["results"][0]["summary"], f"{got}")
    return "no AR_REF_ACCT_TRX_TYPE / other release: plain stop; template refused: data file layout, said so"


def y_route_refused():
    tt_pod(route="refused")
    job = tt_real(lambda: start([tt_record(tt_type("CORSAIR INTEL DEBIT", trx_class="Debit Memo"))]))
    it = job["items"][0]
    seg = log_text().split(f"job {job['id']} queued")[-1]
    check(it["state"] == "failed" and it["result"]["error"]["code"] == "SETUP_NEEDED"
          and "no other way was tried" in it["result"]["text"], f"{it['state']} {it.get('result')}")
    check("repair attempt" not in seg and not it.get("question"), "repaired or asked")
    return "plain card (route refused, nothing created, no other way tried); no repair, no question"


def y_check_cant_run():
    tt_pod(check="fails")
    rec, jobs = tt_record(tt_type("CORSAIR CHECK")), set(server.JOBS)
    before = log_text().count("couldn't run")
    got = tt_real(lambda: server.oracle_checks([rec]))[0]
    res = {"stops": [], "problems": []}
    server.apply_oracle_check(res, rec, got)
    stop = (res["stops"] or [""])[0]
    check(log_text().count("couldn't run") - before == server.CHECK_RERUNS, "re-runs")
    check("couldn't be read just now for transaction types" in stop and set(server.JOBS) == jobs, f"stop {stop!r}")
    return f"{1 + server.CHECK_RERUNS} tries, then under Oracle: {stop[:60]}..."


def y_hidden_readback():
    tt_pod(export_hides_new=True)
    r = tt_cmd("--run-batch", [tt_type("CORSAIR AMD DEBIT", trx_class="Debit Memo")])["results"][0]
    check(r["ok"] and "only its name, set and description were checked" in r["text"], f"type list read-back {r}")
    again = tt_cmd("--run-batch", [tt_type("CORSAIR AMD DEBIT", trx_class="Debit Memo")])["results"][0]
    check(again.get("skipped"), f"rerun {again}")
    tt_pod(export_hides_new=True)
    bad = tt_cmd("--run-batch", [tt_type("CORSAIR AMD DEBIT", set_code="ZZ_NOT_FOR_TT")])["results"][0]
    check(not bad["ok"] and bad["error"]["detail"]["saved"] == "no", f"refused {bad}")
    return ("a new type the data file doesn't list: found in Oracle's type list, name/set/description checked and said "
            "so; rerun skipped; a refused one still 'nothing saved'")


def tt_dep_records(term_set):
    term = ar_term(NET45, set_code=term_set, installments=[{"relative_amount": 100, "days": 45}], print_lead_days=None,
                   tax_freight=None)
    t = tt_type(payment_term=NET45, payment_term_set="COMMON", payment_term_pending=True)
    return [dict(rpt_record(term)), dict(tt_record(t))]


def y_dependency_run():
    tt_pod()
    job = tt_real(lambda: start(tt_dep_records("COMMON")))
    a, b = job["items"]
    check(a["state"] == "done" and b["state"] == "done" and "with payment term CORSAIR NET 45" in b["result"]["text"],
          f"both: {a['state']} {b['state']} {(b.get('result') or {}).get('text')} / {(a.get('result') or {}).get('text')}")
    sent = tt_sent_ok()
    check(sent[0]["DefaultTermName"] == NET45 and sent[0]["DefaultTermSetCode"] == "COMMON", f"term {sent}")
    tt_pod()
    job = tt_real(lambda: start(tt_dep_records("ZZ_NOT_FOR_AR")))
    a, b = job["items"]
    check((a.get("question") or {}).get("state") == "open" and b.get("held"), f"held: {a['state']} {b.get('hold_text')}")
    server.answer_question(job, a["n"], skip=True)
    settle(job)
    check(b["state"] == "failed" and "Not sent" in b["result"]["text"] and not (WORK / "tt_sent.zip").exists(),
          f"after skip: {b['state']} {(b.get('result') or {}).get('text')}")
    return ("payment term + type in one upload: term created first, type then created with it; term refused and skipped "
            "by the user: type held, then not sent (nothing sent for it)")


def tt_sheet(terms, lines, types):
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(workbook.make_template(area="Receivables")))
    for tab, rows in (("Receivables Payment Terms", terms), ("Receivables Term Lines", lines),
                      ("Transaction Types", types)):
        ws = wb[tab]
        col = {str(c.value).rstrip(" *"): c.column for c in ws[2] if c.value}
        for i, r in enumerate(rows):
            for k, v in r.items():
                ws.cell(4 + i, col[k], v)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def y_preview():
    tt_pod()
    base = {"Set Code": "COMMON", "Class": "Invoice", "Status": "Active", "From Date": "2026-11-01",
            "Open Receivable": "Yes", "Post to GL": "Yes", "Allow Freight": "Yes", "Tax Calculation": "Yes",
            "Natural Application Only": "No", "Allow Overapplication": "No", "Creation Sign": "Positive Sign",
            "Transaction Status": "Open", "Printing Option": "Print"}
    types = [dict(base, **{"Name": "CORSAIR OEM INVOICE", "Payment Term": NET45, "Payment Term Set": "COMMON"}),
             dict(base, **{"Name": "CORSAIR RMA INVOICE", "Payment Term": "CORSAIR NET 60", "Payment Term Set": "COMMON"}),
             dict(base, **{"Name": "CORSAIR OEM DEBIT", "Class": "Debit Memo"}),
             {k: v for k, v in dict(base, Name="CORSAIR SAMPLES").items() if k != "Post to GL"}]
    data = tt_sheet([{"Name": NET45, "Set Code": "COMMON", "From Date": "2026-11-01"}],
                    [{"Payment Term Name": NET45, "Relative Amount": 100, "Days": 45}], types)
    res = server.offline_check(data, "2026-11-01", None)
    if res["records"] and not res["stops"]:
        for r, got in zip(res["records"], tt_real(lambda: server.oracle_checks(res["records"]))):
            server.apply_oracle_check(res, r, got)
    by = {r["name"]: r for r in res["records"]}
    oem = by["CORSAIR OEM INVOICE"]
    check(not oem["problems"] and oem["request"].get("payment_term_pending")
          and any("is created first" in (f.get("note") or "") for f in oem["fields"]), f"pending type {oem}")
    check(any("isn't in Oracle and isn't on this sheet" in p["text"] for p in by["CORSAIR RMA INVOICE"]["problems"]),
          "term nowhere")
    check(not by["CORSAIR OEM DEBIT"]["problems"], f"debit memo {by['CORSAIR OEM DEBIT']['problems']}")
    check(any(p.get("column") == "Post to GL" for p in by["CORSAIR SAMPLES"]["problems"]), "required flag not red")
    names = [m["name"] for m in res["modules"] if m["count"]]
    check(names == [RPT, TT], f"modules {res['modules']}")
    return ("term on the sheet: type OK with 'created first' note; term nowhere: red; debit memo OK; an empty required "
            "flag: red (never defaulted); modules payment terms then types")


def y_units():
    tpl_b = io.BytesIO()
    with zipfile.ZipFile(tpl_b, "w") as zo:
        for n in TT_MEMBERS:
            zo.writestr(n, (TT_LAYOUT / n).read_bytes())
    lay = ypkg.read_layout(tpl_b.getvalue())
    t, probs = yrules.check(tt_type(payment_term=NET45, payment_term_set="COMMON", to_date="2027-12-31"))
    check(not probs, f"rules {probs}")
    data = ypkg.build_zip(lay, ypkg.type_rows(t))
    z = zipfile.ZipFile(io.BytesIO(data))
    tpl = zipfile.ZipFile(io.BytesIO(tpl_b.getvalue()))
    check(z.namelist() == tpl.namelist() and z.read(ypkg.METADATA) == tpl.read(ypkg.METADATA), "members / metadata")
    check(z.read("AR_REF_ACCT_TRX_TYPE.csv") == tpl.read("AR_REF_ACCT_TRX_TYPE.csv"), "accounts not header-only")
    _, mine = ypkg.read_rows(data)
    row = mine["AR_TRANSACTION_TYPE"][0]
    check(row["EndDate"] == "2027-12-31" and row["DefaultTermSetCode"] == "COMMON", f"row {row}")
    key = (row["Name"], row["SetCode"])
    got = {c: (v.replace("-", "/") if c in ("StartDate", "EndDate") else v) for c, v in row.items()}
    after = {"AR_TRANSACTION_TYPE": [got], "AR_REF_ACCT_TRX_TYPE": []}
    empty = {"AR_TRANSACTION_TYPE": [], "AR_REF_ACCT_TRX_TYPE": []}
    res, changed = ypkg.reconcile(lay, {key: mine}, empty, after)
    check(res[key]["saved"] and not res[key]["diffs"] and not changed, f"reconcile {res}")
    res2, _ = ypkg.reconcile(lay, {key: mine}, after, empty)
    check(not res2[key]["saved"], "missing type counted as saved")
    acct = dict(after, AR_REF_ACCT_TRX_TYPE=[{"AR_TRANSACTION_TYPE.Name": key[0], "AR_TRANSACTION_TYPE.SetCode": key[1],
                                              "BuName": "X"}])
    res3, _ = ypkg.reconcile(lay, {key: mine}, empty, acct)
    check(res3[key]["notes"], "account rows not noted")
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as zz:
        zz.writestr("AR_PAYMENT_TERM.csv", '"Name","SetCode"\n"30 Net","COMMON"\n"IMMEDIATE","ENTERPRISE"\n')
    check(ypkg.term_keys(b.getvalue()) == {("30 Net", "COMMON"), ("IMMEDIATE", "ENTERPRISE")}, "term keys")
    return ("template read (" + ", ".join(lay.order()) + "); file = its members and metadata, accounts header only; "
            "read-back as sent (slash dates = ISO); a missing one isn't saved; account rows noted; term names + sets read")


TT_CASES = [("Happy path, Invoice type", y_happy), ("Read-back when the data file hides it", y_hidden_readback),
            ("Field rules, nothing defaulted", y_rules), ("Existing / capitals / other set / twice / set", y_existing),
            ("Payment term in Oracle / nowhere / other set", y_term_oracle),
            ("Payment term on the sheet (pending)", y_term_pending),
            ("Refused value at Create -> pause and ask", y_refused_at_create),
            ("Template with a different entity order", y_entity_order),
            ("Template not as known -> plain stop", y_layout_stops),
            ("Route refused -> plain card, no other way", y_route_refused),
            ("Check can't run -> re-runs, real reason", y_check_cant_run),
            ("Term + type in one upload (depends_on)", y_dependency_run),
            ("Preview of a sheet with both modules", y_preview), ("Layout units", y_units)]
tt_table, tt_fails = [], 0
for title, fn in TT_CASES:
    try:
        note, ok = fn(), "PASS"
    except Exception as e:  # noqa: BLE001
        note, ok = f"{type(e).__name__}: {e}"[:400], "FAIL"
        tt_fails += 1
    tt_table.append(("Transaction types folder", title, ok, note))
    print(f"{ok}  {'TT folder':15} {title:45} {note}", flush=True)


# ---------------------------------------------------------------- the sign-in gate (2026-11-02)
# A sheet whose modules all say "uses_browser": false (the four Receivables modules) is checked and created without the
# saved Oracle browser sign-in; any other module on the sheet keeps the old gate (sign-in window at the preview).

SIGN = {"calls": 0, "windows": 0}


def gate_patch():
    SIGN.update(calls=0, windows=0)
    orig = (server.session_valid, server.oracle_signin, server.full_check)

    def invalid():
        SIGN["calls"] += 1
        return {"valid": False, "reason": "expired (matrix)"}

    def window():
        SIGN["windows"] += 1
        time.sleep(1)               # a real window takes minutes; the upload stores its preview first
        return False
    server.session_valid, server.oracle_signin = invalid, window
    server.full_check = lambda data: dict(server.offline_check(data, "2026-11-01", None), ok=True, checked="full")
    return orig


def gate_restore(orig):
    server.session_valid, server.oracle_signin, server.full_check = orig


def gate_post(uid):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/sheet/create", json.dumps({"upload": uid}).encode(),
                                 {"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def g_units():
    rec = lambda mod: {"group": MODULES[mod]["group"]}  # noqa: E731
    check(not server.needs_signin([rec(RPT), rec("AutoInvoice Grouping Rules"), rec(TT), rec("Transaction Sources")]),
          "Receivables-only sheet needs the sign-in")
    for mod in ("Customers", "Order Types", "Payment Terms", "Lookup types", "Business Units", "Price Lists"):
        check(server.needs_signin([rec(mod)]) and server.needs_signin([rec(TT), rec(mod)]), f"{mod} doesn't need it")
    check(server.needs_signin([]), "an empty sheet changed behaviour")
    return "four Receivables modules: no sign-in; each Order Management module alone or mixed in: sign-in; empty: as before"


def g_upload_receivables():
    orig = gate_patch()
    try:
        data = tt_sheet([{"Name": NET45, "Set Code": "COMMON", "From Date": "2026-11-01"}],
                        [{"Payment Term Name": NET45, "Relative Amount": 100, "Days": 45}], [])
        uid, res = server.check_upload(data, "receivables.xlsx")
        time.sleep(0.5)
        check(SIGN["calls"] == 0 and SIGN["windows"] == 0, f"sign-in touched {SIGN}")
        check(res.get("checked") == "full" and not res.get("signin"), f"preview {res.get('signin')} {res.get('checked')}")
        check("no module of this sheet uses the browser" in log_text(), "log line")
        server.UPLOADS[uid]["preview"]["records"] = [record(TT)]      # the stub folder runs it
        ans = gate_post(uid)
        check("id" in ans and SIGN["calls"] == 0, f"create {ans} {SIGN}")
        job = settle(server.JOBS[ans["id"]])
        check(job["items"][0]["state"] == "done", f"run {job['items'][0]['state']}")
    finally:
        gate_restore(orig)
    return "expired sign-in: Receivables sheet checked in full, Create ran, sign-in never checked, no window"


def g_upload_order_management():
    orig = gate_patch()
    try:
        from openpyxl import load_workbook
        wb = load_workbook(io.BytesIO(workbook.make_template()))
        ws = wb["Order Types"]
        col = {str(c.value).rstrip(" *"): c.column for c in ws[2] if c.value}
        for k, v in (("Lookup Type", "ORA_DOO_ORDER_TYPES"), ("Lookup Code", "ZZ_STUB_GATE"), ("Meaning", "m")):
            ws.cell(4, col[k], v)
        buf = io.BytesIO()
        wb.save(buf)
        uid, res = server.check_upload(buf.getvalue(), "om.xlsx")
        time.sleep(1.5)
        check(SIGN["calls"] == 1 and res.get("signin") == "waiting" and not res["ok"], f"preview {SIGN} {res.get('signin')}")
        check(SIGN["windows"] == 1, f"window {SIGN}")
        server.UPLOADS[uid]["preview"] = dict(res, ok=True, records=[record("Order Types"), record(TT)])
        server.UPLOADS[uid]["job"] = None
        ans = gate_post(uid)
        time.sleep(1.5)
        check(ans.get("signin") and SIGN["calls"] == 2, f"create {ans} {SIGN}")
    finally:
        gate_restore(orig)
    return "expired sign-in: Order Management sheet waits for the sign-in window; Create of a mixed sheet asks for it too"


GATE_CASES = [("Which sheets need the sign-in", g_units), ("Receivables-only sheet, sign-in expired", g_upload_receivables),
              ("Order Management sheet, sign-in expired", g_upload_order_management)]
gate_table, gate_fails = [], 0
for title, fn in GATE_CASES:
    try:
        note, ok = fn(), "PASS"
    except Exception as e:  # noqa: BLE001
        note, ok = f"{type(e).__name__}: {e}"[:400], "FAIL"
        gate_fails += 1
    gate_table.append(("Sign-in gate", title, ok, note))
    print(f"{ok}  {'Sign-in gate':15} {title:45} {note}", flush=True)
srv.shutdown()
print(f"\n{len(table) - fails} of {len(table)} PASS")
print(f"check that can't run: {len(extra) - extra_fails} of {len(extra)} PASS")
print(f"Receivables Payment Terms folder (real code, Oracle replaced): {len(rpt_table) - rpt_fails} of {len(rpt_table)} PASS")
print(f"AutoInvoice Grouping Rules folder (real code, ETIA-TEST layout, Oracle replaced): {len(agr_table) - agr_fails} of {len(agr_table)} PASS")
print(f"Transaction Sources folder (real code, Oracle replaced): {len(ts_table) - ts_fails} of {len(ts_table)} PASS")
print(f"Transaction Types folder (real code, Oracle replaced): {len(tt_table) - tt_fails} of {len(tt_table)} PASS")
print(f"Sign-in gate: {len(gate_table) - gate_fails} of {len(gate_table)} PASS")
table += extra + rpt_table + agr_table + ts_table + tt_table + gate_table
fails += extra_fails + rpt_fails + agr_fails + ts_fails + tt_fails + gate_fails
(WORK / "matrix_result.json").write_text(json.dumps(table, indent=1), encoding="utf-8")
sys.exit(1 if fails else 0)
