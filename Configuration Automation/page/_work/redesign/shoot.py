"""Screenshots of the page (demo server, Oracle stubbed) and the reference mockup at every stage, in dark and light at
1360 px and dark at 390 px, plus the checks: no console errors, the theme survives a reload, the rail never moves,
no stage-preview buttons. Run: python page/_work/redesign/shoot.py [demo port] [modes]"""
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DEMO = HERE / "demo"
OUT = HERE / "shots"
OUT.mkdir(exist_ok=True)
PORT = sys.argv[1] if len(sys.argv) > 1 else "8797"
URL = f"http://127.0.0.1:{PORT}/"
REF = (HERE / "reference" / "mockup.html").as_uri()
MODES = [("dark", 1360, 900), ("light", 1360, 900), ("dark", 390, 844)]
if len(sys.argv) > 2:
    MODES = [m for m in MODES if f"{m[0]}-{m[1]}" in sys.argv[2].split(",")]
report = {"console_errors": [], "rail": {}, "theme_reload": None, "stage_buttons": None}


def snap(page, name):
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)


def rail_box(page):
    """The rail's place on the page (not the screen, so scrolling doesn't count as a move)."""
    return page.evaluate("(() => { const r = document.getElementById('rail').getBoundingClientRect();"
                         " return [Math.round(r.left + scrollX), Math.round(r.top + scrollY), Math.round(r.width),"
                         " Math.round(r.height)]; })()")


def app_flow(ctx, tag):
    page = ctx.new_page()
    page.on("console", lambda m: m.type == "error" and report["console_errors"].append(f"{tag}: {m.text}"))
    page.on("pageerror", lambda e: report["console_errors"].append(f"{tag}: {e}"))
    boxes = []
    page.goto(URL + "#/")
    page.wait_for_selector("#choose")
    page.wait_for_timeout(800)
    snap(page, f"app-{tag}-01-upload"); boxes.append(rail_box(page))
    page.set_input_files("#file", str(DEMO / "Setup_Workbook.xlsx"))
    page.wait_for_selector("text=Reading rows…")
    page.wait_for_timeout(1500)
    snap(page, f"app-{tag}-02-checking"); boxes.append(rail_box(page))
    page.wait_for_selector("#create", timeout=60000)
    page.wait_for_timeout(800)
    snap(page, f"app-{tag}-03-problems"); boxes.append(rail_box(page))
    page.click("[data-mod='Payment Terms']")
    page.wait_for_timeout(500)
    snap(page, f"app-{tag}-03b-problems-module-open")
    page.goto(URL + "#/")
    page.wait_for_selector("#choose")
    page.set_input_files("#file", str(DEMO / "Setup_Workbook_fixed.xlsx"))
    page.wait_for_selector("text=Reading rows…")
    page.wait_for_timeout(1500)
    snap(page, f"app-{tag}-04-rechecking"); boxes.append(rail_box(page))
    page.wait_for_selector("#create:not([disabled])", timeout=60000)
    page.wait_for_timeout(800)
    snap(page, f"app-{tag}-05-all-clear"); boxes.append(rail_box(page))
    page.click("#create")
    page.wait_for_selector("text=Creating in Oracle", timeout=30000)
    page.wait_for_timeout(2500)
    snap(page, f"app-{tag}-06-running"); boxes.append(rail_box(page))
    page.wait_for_selector(".question .q-pick", timeout=120000)
    page.wait_for_timeout(800)
    snap(page, f"app-{tag}-07-paused"); boxes.append(rail_box(page))
    page.locator(".question .q-pick").first.click()
    page.wait_for_selector("#results", timeout=180000)
    page.wait_for_timeout(1200)
    snap(page, f"app-{tag}-08-done"); boxes.append(rail_box(page))
    report["rail"][tag] = boxes
    report["stage_buttons"] = page.locator("#rail button").count()
    page.close()


def ref_flow(ctx, theme, tag):
    page = ctx.new_page()
    page.goto(REF + f"?theme={theme}")
    page.wait_for_selector("text=Choose workbook")
    page.wait_for_timeout(800)
    snap(page, f"ref-{tag}-01-upload")
    page.click("text=Choose workbook")
    page.wait_for_timeout(700)
    snap(page, f"ref-{tag}-02-checking")
    page.wait_for_selector("text=Fix these now", timeout=10000)
    page.wait_for_timeout(400)
    snap(page, f"ref-{tag}-03-problems")
    page.click("text=Set to 1")
    page.click("button:has-text('Younas, Yaqub')")
    page.wait_for_timeout(400)
    snap(page, f"ref-{tag}-04-rechecking")
    page.wait_for_selector("text=Every check passed", timeout=10000)
    page.wait_for_timeout(300)
    snap(page, f"ref-{tag}-05-all-clear")
    page.click("text=Create 22 items")
    page.wait_for_timeout(2000)
    snap(page, f"ref-{tag}-06-running")
    page.wait_for_selector("text=Needs your decision", timeout=20000)
    page.wait_for_timeout(300)
    snap(page, f"ref-{tag}-07-paused")
    page.click("button:text-is('1')")
    page.wait_for_selector("text=Result cards", timeout=30000)
    page.wait_for_timeout(600)
    snap(page, f"ref-{tag}-08-done")
    page.close()


with sync_playwright() as p:
    b = p.chromium.launch()
    for theme, w, h in MODES:
        tag = f"{theme}-{w}"
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
        ctx.add_init_script(f"try{{localStorage.setItem('sa-theme','{theme}')}}catch(e){{}}")
        app_flow(ctx, tag)
        ref_flow(ctx, theme, tag)
        ctx.close()
    # the theme switch survives a reload
    ctx = b.new_context(viewport={"width": 1360, "height": 900})
    page = ctx.new_page()
    page.goto(URL + "#/")
    page.wait_for_selector("#theme-toggle")
    before = page.evaluate("document.documentElement.dataset.theme")
    page.click("#theme-toggle")
    page.reload()
    page.wait_for_selector("#theme-toggle")
    after = page.evaluate("document.documentElement.dataset.theme")
    report["theme_reload"] = {"before": before, "after_toggle_and_reload": after,
                              "label": page.inner_text("#theme-label")}
    ctx.close()
    b.close()
print(json.dumps(report, indent=1))
