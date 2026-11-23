"""The Done screen against the demo server (Oracle and Claude stubbed): a mixed run (created, skipped by the user,
answered with a suggestion, a typed value and Claude's proposal, a repair, a not-created item) and a clean run
(nothing needed attention, no Claude), in dark and light at 1360 px and dark at 390 px. Checks: console errors,
horizontal scroll, search, filters, collapse / expand. Run: python page/_work/redesign/shoot_done.py [port] [modes]"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DEMO = HERE / "demo"
OUT = HERE / "shots_done"
OUT.mkdir(exist_ok=True)
URL = f"http://127.0.0.1:{sys.argv[1] if len(sys.argv) > 1 else '8797'}/"
MODES = [("dark", 1360, 900), ("light", 1360, 900), ("dark", 390, 844)]
if len(sys.argv) > 2:
    MODES = [m for m in MODES if f"{m[0]}-{m[1]}" in sys.argv[2].split(",")]
report = {"console_errors": [], "hscroll": {}, "checks": {}}


def answer_questions(page):
    """Answer each open decision card the way the scenario needs, until the run is done."""
    for _ in range(400):
        if page.locator("#results").count():
            return
        for card in page.locator(".question").all():
            if not card.locator(".q-use").count():
                continue                                   # busy: the answer is being checked or tried
            text = card.inner_text()
            n = card.get_attribute("data-n")
            if '"RETURN_ORDER"' in text:
                page.fill(f"#q-text-{n}", "Return Order (manual)")
                card.locator(".q-use").click()
            elif '"NET30_ZZ"' in text or '"2/10 NET 30"' in text:
                card.locator(".q-pick").first.click()
            elif '"ZZ_ORDER_REASON"' in text:
                card.locator(".q-skip").click()
            page.wait_for_timeout(800)
            break
        page.wait_for_timeout(700)
    raise RuntimeError("the run did not finish")


def run_to_done(page, sheet):
    (DEMO / "work" / "flags" / "RUSH_FLAKY").unlink(missing_ok=True)
    page.goto(URL + "#/")
    page.wait_for_selector("#choose")
    page.set_input_files("#file", str(DEMO / sheet))
    page.wait_for_selector("#create:not([disabled])", timeout=60000)
    page.click("#create")
    answer_questions(page)
    page.wait_for_timeout(1200)


def visible_groups(page):
    return page.evaluate("[...document.querySelectorAll('#results .rgroup')].map(g => g.dataset.group)")


with sync_playwright() as p:
    b = p.chromium.launch()
    for theme, w, h in MODES:
        tag = f"{theme}-{w}"
        ctx = b.new_context(viewport={"width": w, "height": h})
        ctx.add_init_script(f"try{{localStorage.setItem('sa-theme','{theme}')}}catch(e){{}}")
        page = ctx.new_page()
        page.on("console", lambda m, t=tag: m.type == "error" and report["console_errors"].append(f"{t}: {m.text}"))
        page.on("pageerror", lambda e, t=tag: report["console_errors"].append(f"{t}: {e}"))
        for scen, sheet in (("mixed", "Done_mixed.xlsx"), ("clean", "Done_clean.xlsx")):
            run_to_done(page, sheet)
            page.screenshot(path=str(OUT / f"{scen}-{tag}.png"), full_page=True)
            report["hscroll"][f"{scen}-{tag}"] = page.evaluate("document.documentElement.scrollWidth - innerWidth")
            if scen == "mixed" and tag == "dark-1360":
                c = report["checks"]
                c["groups"] = visible_groups(page)
                c["first_cards_in_order_types"] = page.evaluate(
                    "[...document.querySelectorAll('[data-group=\"Order Types\"] .rcard .pill')].map(x => x.innerText)")
                page.fill("#q", "net")
                page.wait_for_timeout(300)
                c["search_net"] = visible_groups(page)
                page.screenshot(path=str(OUT / f"mixed-{tag}-search-net.png"), full_page=True)
                page.fill("#q", "zzzz-nothing")
                page.wait_for_timeout(300)
                c["search_nothing"] = page.inner_text("#results")
                page.fill("#q", "")
                page.click("[data-filter='Skipped']")
                page.wait_for_timeout(300)
                c["filter_skipped"] = visible_groups(page)
                page.click("[data-filter='All']")
                head = page.locator("[data-toggle='Payment Terms']")
                head.click()
                page.wait_for_timeout(300)
                c["collapse_pt"] = {"aria": head.get_attribute("aria-expanded"),
                                    "grid_hidden": page.evaluate("document.getElementById(document.querySelector(\"[data-toggle='Payment Terms']\").getAttribute('aria-controls')).hidden")}
                page.screenshot(path=str(OUT / f"mixed-{tag}-collapsed-pt.png"), full_page=True)
                page.click("#toggle-all")
                page.wait_for_timeout(300)
                c["after_collapse_all"] = {"label": page.inner_text("#toggle-all"),
                                           "expanded": page.evaluate("[...document.querySelectorAll('[data-toggle]')].map(b => b.getAttribute('aria-expanded'))")}
                page.click("#toggle-all")
                page.wait_for_timeout(300)
                c["after_expand_all"] = {"label": page.inner_text("#toggle-all"),
                                         "expanded": page.evaluate("[...document.querySelectorAll('[data-toggle]')].map(b => b.getAttribute('aria-expanded'))")}
                c["head_min_height"] = page.evaluate("Math.min(...[...document.querySelectorAll('.rg-head, #toggle-all, [data-filter]')].map(e => e.getBoundingClientRect().height))")
                c["export_button"] = page.locator("#export").count()
                c["failed_sheet_button"] = page.locator("#failed-sheet").inner_text() if page.locator("#failed-sheet").count() else None
        ctx.close()
    b.close()
print(json.dumps(report, indent=1))
