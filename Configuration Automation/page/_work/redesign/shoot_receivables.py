"""Screenshots of the Order Management | Receivables switch and the Receivables Payment Terms module (2026-10-30), against
stubs only: the page's real server code in this process on port 8798 with Oracle replaced (the Order Management folders
by demo/demo_stub.py, Receivables Payment Terms by its REAL folder code through page/matrix/stub_receivables.py). Upload
screen on both sides of the switch (dark and light at 1360 px, dark at 390 px), a Receivables check with problems, a
clean check, a refused value at Create (the decision panel) and a Create result. Also: console errors, every browser
request's host, every connection this process opens (none may leave 127.0.0.1), no sideways scroll at 390 px, and the
page with localStorage blocked. Run: python page/_work/redesign/shoot_receivables.py   (work files: shots_receivables/)"""
import http.server
import json
import os
import shutil
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "shots_receivables"
WORK = OUT / "work"
shutil.rmtree(OUT, ignore_errors=True)
WORK.mkdir(parents=True)
PORT = 8798
URL = f"http://127.0.0.1:{PORT}/"

# ---- every connection this process opens is logged; anything but this machine is refused
OUTBOUND = []
_connect = socket.socket.connect


def _guard(self, addr):
    host = addr[0] if isinstance(addr, tuple) else str(addr)
    if host not in ("127.0.0.1", "::1", "localhost"):
        OUTBOUND.append(str(addr))
        raise OSError(f"blocked by shoot_receivables: {addr}")
    return _connect(self, addr)


socket.socket.connect = _guard

os.environ["MATRIX_WORK"] = str(WORK)
sys.path[:0] = [str(ROOT / "page"), str(ROOT)]
sys.argv = ["server.py"]
import run_summary  # noqa: E402
import server  # noqa: E402

server.WORK, server.LOGS, server.SERVER_LOG = WORK, WORK / "logs", WORK / "server.log"
run_summary.SERVER_LOG, run_summary.LOGS = WORK / "server.log", WORK / "logs"
server.session_valid = lambda *a, **k: {"valid": True}
server.oracle_today = lambda *a, **k: "2026-10-30"
server.setup_quick = lambda *a, **k: True
server.claude_status = lambda *a, **k: {"installed": True, "signed_in": True, "signing_in": False}
server.claude_status_cached = server.claude_status
server.ENV_CHILD.update(MATRIX_WORK=str(WORK), ORACLE_HOST="https://oracle-not-used.invalid", ORACLE_ENV="test")
server.find_claude = lambda *a, **k: "stub"
server.claude_command = lambda cli: [server.PY, str(ROOT / "page" / "matrix" / "stub_claude.py")]
DEMO = str(HERE / "demo" / "demo_stub.py")
for name in ("Customers", "Order Types", "Payment Terms", "Lookup types", "Business Units", "Price Lists"):
    server.FOLDERS[name] = {"name": name, "script": DEMO, "spec": {"fields": []}, "error": None}
server.FOLDERS["Receivables Payment Terms"] = {"name": "Receivables Payment Terms", "spec": {"fields": []}, "error": None,
                                               "script": str(ROOT / "page" / "matrix" / "stub_receivables.py")}


def check_upload(data, file_name):
    """As full_check, with Oracle's answers from the stubs: the sheet check, then the folders' read-only checks."""
    uid = server.uuid.uuid4().hex[:10]
    with server.LOCK:
        server.UPLOADS[uid] = {"preview": None, "file": file_name, "at": time.time(), "job": None, "data": data}
    res = server.offline_check(data, "2026-10-30", None)
    if res["records"] and not res["stops"]:
        for r, got in zip(res["records"], server.oracle_checks(res["records"])):
            server.apply_oracle_check(res, r, got)
    for r in res["records"]:
        r["ok"] = not r["problems"]
    res["ok"] = bool(res["records"]) and not res["stops"] and not res["problems"]
    with server.LOCK:
        server.UPLOADS[uid]["preview"] = res
    server.log(f"upload {uid} ({file_name}): {'ready' if res['ok'] else 'not ready'}, {len(res['records'])} record(s), "
               f"{len(res['problems'])} problem(s), checked")
    return uid, res


server.check_upload = check_upload
srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), server.Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
threading.Thread(target=server.worker, daemon=True).start()

# ---- sheets (the page's own generator)
from openpyxl import load_workbook  # noqa: E402

import workbook  # noqa: E402

NOTES = ROOT / "Receivables Payment Terms" / "manual-notes"
GOOD, BAD = NOTES / "Receivables_Payment_Terms_TEST_good.xlsx", NOTES / "Receivables_Payment_Terms_TEST_bad.xlsx"
ASK = WORK / "Receivables_refused_set.xlsx"
wb = load_workbook(GOOD)
ws = wb["Receivables Payment Terms"]
ws.cell(4, 1, "ZZ_TEST_AR_ASK")
ws.cell(4, 2, "ZZ_NOT_FOR_AR")                       # in Oracle's set list, refused by the stub pod at Create
lines = wb["Receivables Term Lines"]
for r in range(4, 6):
    lines.cell(r, 1, "ZZ_TEST_AR_ASK")
wb.save(ASK)

from playwright.sync_api import sync_playwright  # noqa: E402

report = {"shots": [], "console_errors": [], "request_hosts": {}, "outbound_from_server": OUTBOUND, "checks": {}}


def snap(page, name):
    page.wait_for_timeout(500)
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    report["shots"].append(f"{name}.png")


def watch(page, tag):
    page.on("console", lambda m: m.type == "error" and report["console_errors"].append(f"{tag}: {m.text}"))
    page.on("pageerror", lambda e: report["console_errors"].append(f"{tag}: {e}"))
    page.on("request", lambda r: report["request_hosts"].__setitem__(
        urlparse(r.url).hostname or r.url[:30], report["request_hosts"].get(urlparse(r.url).hostname or r.url[:30], 0) + 1))


def open_page(ctx, theme, tag):
    page = ctx.new_page()
    watch(page, tag)
    page.add_init_script(f"try {{ localStorage.setItem('sa-theme', '{theme}'); }} catch (e) {{}}")
    page.goto(URL + "#/")
    page.wait_for_selector("[data-area-mod]")
    return page


def side(page, area_name):
    page.click(f"#area-switch [data-area='{area_name}']")
    page.wait_for_selector(f"#area-mods[aria-label='Modules in {area_name}'] [data-area-mod]")


def upload(page, path):
    page.goto(URL + "#/")
    page.wait_for_selector("#choose")
    page.set_input_files("#file", str(path))
    page.wait_for_selector("#create", timeout=120000)


def no_sideways(page, tag):
    w = page.evaluate("[document.documentElement.scrollWidth, window.innerWidth]")
    report["checks"][f"no sideways scroll {tag}"] = w[0] <= w[1]


with sync_playwright() as p:
    browser = p.chromium.launch()
    for theme, width, height in (("dark", 1360, 900), ("light", 1360, 900), ("dark", 390, 844)):
        ctx = browser.new_context(viewport={"width": width, "height": height})
        page = open_page(ctx, theme, f"{theme}-{width}")
        tag = f"{theme}_{width}"
        report["checks"][f"default side {tag}"] = page.get_attribute("#area-switch [data-area='Order Management']",
                                                                     "aria-pressed") == "true"
        side(page, "Order Management")
        cards = page.eval_on_selector_all("[data-area-mod]", "els => els.map(e => e.dataset.areaMod)")
        report["checks"][f"Order Management cards {tag}"] = cards
        report["checks"][f"Order Management template {tag}"] = page.get_attribute("#template", "href")
        snap(page, f"upload_order_management_{tag}")
        if width == 390:
            no_sideways(page, "Order Management 390")
        side(page, "Receivables")
        report["checks"][f"Receivables cards {tag}"] = page.eval_on_selector_all(
            "[data-area-mod]", "els => els.map(e => e.dataset.areaMod)")
        report["checks"][f"Receivables template {tag}"] = page.get_attribute("#template", "href")
        snap(page, f"upload_receivables_{tag}")
        if width == 390:
            no_sideways(page, "Receivables 390")
        page.reload()
        page.wait_for_selector("[data-area-mod]")
        report["checks"][f"side kept after reload {tag}"] = page.get_attribute(
            "#area-switch [data-area='Receivables']", "aria-pressed") == "true"
        side(page, "Order Management")
        ctx.close()

    # the blank templates the two sides give
    ctx = browser.new_context(viewport={"width": 1360, "height": 900})
    page = open_page(ctx, "dark", "templates")
    for a in ("Order Management", "Receivables"):
        side(page, a)
        with page.expect_download() as d:
            page.click("#template")
        path = WORK / d.value.suggested_filename
        d.value.save_as(path)
        report["checks"][f"template tabs {a}"] = [s for s in load_workbook(path).sheetnames]
        report["checks"][f"template file name {a}"] = d.value.suggested_filename
    side(page, "Order Management")
    ctx.close()

    # a Receivables check with problems, a clean check, the decision panel, a Create result
    for theme, width, height in (("dark", 1360, 900), ("dark", 390, 844)):
        ctx = browser.new_context(viewport={"width": width, "height": height})
        page = open_page(ctx, theme, f"check-{theme}-{width}")
        upload(page, BAD)
        page.wait_for_timeout(600)
        report["checks"][f"problems check: Create disabled {width}"] = page.is_disabled("#create")
        snap(page, f"check_problems_{theme}_{width}")
        if width == 390:
            no_sideways(page, "check problems 390")
        ctx.close()
    ctx = browser.new_context(viewport={"width": 1360, "height": 900})
    page = open_page(ctx, "dark", "create")
    (WORK / "rpt_pod.json").unlink(missing_ok=True)
    upload(page, GOOD)
    report["checks"]["clean check: Create enabled"] = not page.is_disabled("#create")
    snap(page, "check_clean_dark_1360")
    page.click("#create")
    page.wait_for_selector("#new-run", timeout=180000)
    snap(page, "create_result_dark_1360")
    report["checks"]["create result text"] = page.inner_text("#results")[:600]
    upload(page, ASK)
    page.click("#create")
    page.wait_for_selector(".question", timeout=180000)
    snap(page, "create_question_dark_1360")
    page.click(".question .q-pick")
    page.wait_for_selector("#new-run", timeout=180000)
    snap(page, "create_question_answered_dark_1360")
    ctx.close()

    # localStorage blocked: the page still works on the default side, and the switch still switches
    ctx = browser.new_context(viewport={"width": 1360, "height": 900})
    page = ctx.new_page()
    watch(page, "no-storage")
    page.add_init_script("Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked'); } });")
    page.goto(URL + "#/")
    page.wait_for_selector("[data-area-mod]")
    ok1 = page.get_attribute("#area-switch [data-area='Order Management']", "aria-pressed") == "true"
    side(page, "Receivables")
    ok2 = page.eval_on_selector_all("[data-area-mod]", "els => els.map(e => e.dataset.areaMod)") == [
        "Receivables Payment Terms"]
    report["checks"]["storage blocked: default Order Management, switch works"] = ok1 and ok2
    ctx.close()
    browser.close()

srv.shutdown()
report["server_log_tail"] = (WORK / "server.log").read_text(encoding="utf-8").splitlines()[-25:]
(OUT / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k != "server_log_tail"}, indent=1, ensure_ascii=False))
