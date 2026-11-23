"""Offline behaviour matrix: every module x every pause-and-ask / repair behaviour, through the page's real server code
(queue, per-record and batch runs, questions, answers, repair, Claude proposals, Run summary, HTTP view), with the
folders' scripts replaced by stub_folder.py (Oracle stubbed) and Claude's tool by stub_claude.py. Nothing reaches
Oracle or Claude; logs go to page/_work/matrix, not the page's own server.log.

  python page/matrix/test_matrix.py      # about 2 minutes; exit 0 = every cell PASS (2026-10-26: 48 of 48)
Since 2026-10-26 also, for every module with a read-only check before Create: a check that can't run (re-run twice,
then the folder's real reason under "Oracle", nothing created) and one that fails once (the re-run answers).
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
srv.shutdown()
print(f"\n{len(table) - fails} of {len(table)} PASS")
print(f"check that can't run: {len(extra) - extra_fails} of {len(extra)} PASS")
table += extra
fails += extra_fails
(WORK / "matrix_result.json").write_text(json.dumps(table, indent=1), encoding="utf-8")
sys.exit(1 if fails else 0)
