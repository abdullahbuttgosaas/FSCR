"""Prompt 3 live test (2026-10-30): one Receivables payment term through the real page on 127.0.0.1:8765.
Switch to Receivables, upload the workbook, wait for the check (stop on any red problem), press Create once, follow
the run to the end. Records times, progress texts, screenshots and the job's final view in report.json."""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
URL = "http://127.0.0.1:8765/"
term = json.loads((HERE / "term.json").read_text())
ROOT = HERE.parents[2]
rep = {"term": term["name"], "progress": [], "console_errors": []}
now = lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")


def api(path):
    return json.loads(urllib.request.urlopen(URL + path.lstrip("/"), timeout=30).read())


def save():
    (HERE / "report.json").write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")


with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page(viewport={"width": 1360, "height": 900})
    page.on("console", lambda m: m.type == "error" and rep["console_errors"].append(m.text))
    page.goto(URL + "#/")
    page.wait_for_selector("[data-area-mod]", timeout=60000)
    page.click("#area-switch [data-area='Receivables']")
    page.wait_for_selector("#area-mods[aria-label='Modules in Receivables'] [data-area-mod]")
    page.screenshot(path=str(HERE / "01_upload_receivables.png"), full_page=True)
    rep["check_start"] = now()
    t0 = time.time()
    page.set_input_files("#file", str(ROOT / term["file"]))
    page.wait_for_function("location.hash.startsWith('#/sheet/')", timeout=900000)
    uid = page.evaluate("location.hash").split("/")[-1]
    page.wait_for_selector("#create", timeout=900000)
    rep["check_end"], rep["check_seconds"] = now(), round(time.time() - t0)
    page.wait_for_timeout(800)
    page.screenshot(path=str(HERE / "02_check.png"), full_page=True)
    pv = api(f"/api/sheet/{uid}")
    rep["check"] = {"ok": pv["ok"], "stops": pv["stops"], "problems": pv["problems"], "notes": pv["notes"],
                    "records": [{"name": r["name"], "ok": r["ok"], "skipped": r.get("skipped"),
                                 "summary": r.get("oracle_summary"),
                                 "fields": [(f["label"], f.get("sheet"), f.get("oracle"), f.get("note"))
                                            for f in r["fields"]]} for r in pv["records"]]}
    save()
    if not pv["ok"] or page.is_disabled("#create"):
        rep["stopped"] = "the check is not clean: nothing was created"
        save()
        print(json.dumps(rep["check"], indent=1))
        sys.exit(2)
    rep["create_start"] = now()
    t1 = time.time()
    page.click("#create")
    page.wait_for_function("location.hash.startsWith('#/job/')", timeout=60000)
    jid = page.evaluate("location.hash").split("/")[-1]
    rep["job"] = jid
    last = None
    while True:
        j = api(f"/api/job/{jid}")
        line = (j.get("state"), j.get("text"), (j.get("sub") or {}).get("text") if isinstance(j.get("sub"), dict) else None,
                [(it.get("state"), it.get("step_text") or it.get("text")) for it in j.get("items", [])])
        if line != last:
            rep["progress"].append({"at": now(), "state": j.get("state"), "text": j.get("text"),
                                    "items": [{"name": it.get("name"), "state": it.get("state"),
                                               "text": it.get("text") or it.get("step_text")} for it in j.get("items", [])]})
            last = line
            save()
        if j.get("state") in ("done", "failed", "asking") and not any(
                it.get("state") in ("running", "waiting", "queued") for it in j.get("items", [])):
            break
        if time.time() - t1 > 2400:
            rep["stopped"] = "the run didn't finish within 40 minutes (left running on the page)"
            break
        time.sleep(2)
    rep["create_end"], rep["create_seconds"] = now(), round(time.time() - t1)
    page.wait_for_timeout(2500)
    page.screenshot(path=str(HERE / "03_result.png"), full_page=True)
    rep["job_final"] = api(f"/api/job/{jid}")
    save()
    b.close()
print(json.dumps({k: rep[k] for k in ("term", "check_seconds", "create_seconds") if k in rep}))
