"""Read-only "look at an Oracle screen" helper for the page's automatic repairs.

It opens one task's screen with the saved sign-in (hidden browser), reads what is asked
and leaves WITHOUT saving: it never presses Save/Submit/Import/Approve, never types
anything, and always ends with Cancel (and "Yes" to leave without saving).

  python page/look.py --folder Customers --task "Create Customer" --area Customers \
      --offering Financials [--heading "Create Organization Customer"] \
      [--label "Account Address Set" ...] [--click "Link or tab text" ...] [--text] \
      [--screenshot name]

Prints one JSON line. Screenshots go to page/_work/look/<name>.png (Claude can view them).
Credentials are never read or typed: the browser uses .session/ through Playwright only.
The folder's own code opens the screen; during a repair the server points
PAGE_LOOK_SNAPSHOT at a copy of the folder taken before the repair, so code edited by
the repair is never run from here (the server checks edits before it reruns anything).
"""
import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from common import browser, oracle  # noqa: E402

LOOK = ROOT / "page" / "_work" / "look"
NEVER = re.compile(r"\b(save|submit|import|approve|post|delete|remove|create|add row|ok|apply|"
                   r"done|complete|confirm|send|upload)\b", re.I)
FROM = {"code": "folder"}


def opener(folder):
    """How the folder itself opens a task screen (its own layout-aware steps), taken from
    the pre-repair copy of the folder when the server provides one."""
    fdir = ROOT / folder
    snap = os.environ.get("PAGE_LOOK_SNAPSHOT")
    if snap and (Path(snap) / folder).is_dir():
        fdir, FROM["code"] = Path(snap) / folder, "copy taken before the repair"
    if not (fdir / "browser_flow.py").exists():
        return lambda ui, t, a, o: ui.open_task(t, a, o)
    sys.path.insert(0, str(fdir))
    spec = importlib.util.spec_from_file_location("folder_flow", fdir / "browser_flow.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "open_task_page"):
        return mod.open_task_page                        # e.g. Customers
    if hasattr(mod, "Setup"):                            # e.g. Payment Terms, Business Units
        return lambda ui, t, a, o: mod.Setup(ui).open_task(t, a, o)
    return lambda ui, t, a, o: ui.open_task(t, a, o)


LABEL_JS = r"""(wanted) => {
  const norm = s => s.replace(/[*\s]+/g, ' ').trim().toLowerCase();
  for (const l of document.querySelectorAll('label')) {
    if (!l.offsetWidth || norm(l.innerText) !== norm(wanted)) continue;
    const row = l.closest('tr') || l.parentElement;
    const req = !!(row && row.querySelector('[title="Required"], .af_inputText_label-required, abbr'))
                || /\*/.test(row ? row.innerText.split('\n')[0] : '');
    const ctl = l.htmlFor ? document.getElementById(l.htmlFor) : null;
    return {label: l.innerText.trim(), required: req,
            control: ctl ? (ctl.tagName.toLowerCase() + (ctl.type ? ':' + ctl.type : '')) : null};
  }
  return null;
}"""


BUTTONS_JS = r"""() => {
  const seen = new Set(), out = [];
  for (const e of document.querySelectorAll('button, a[title], a[role=button], img[title], [role=button], [title][onclick]')) {
    if (!e.offsetWidth) continue;
    const item = {tag: e.tagName.toLowerCase(), text: (e.innerText || '').trim().slice(0, 60),
                  title: e.getAttribute('title') || '', aria: e.getAttribute('aria-label') || ''};
    const key = JSON.stringify(item);
    if (!item.text && !item.title && !item.aria || seen.has(key)) continue;
    seen.add(key); out.push(item);
    if (out.length >= 120) break;
  }
  return out;
}"""


def leave(ui):
    """Cancel, and "Yes" if Oracle asks about leaving without saving. Never saves."""
    page = ui.page
    cancel = page.get_by_role("button", name=re.compile(r"^Cancel$")).first
    if cancel.count() and cancel.is_visible():
        ui.click(cancel, "Cancel (leave without saving)")
        yes = page.get_by_role("button", name=re.compile(r"^Y\s*es$"))
        try:
            yes.first.wait_for(timeout=5000)
            ui.click(yes.first, "Yes (leave without saving)")
        except Exception:
            pass
        ui.settle()
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--area", required=True)
    ap.add_argument("--offering", required=True)
    ap.add_argument("--heading", help="wait until this screen heading shows (e.g. Create Organization Customer)")
    ap.add_argument("--click", action="append", default=[], help="link/tab text (never save-type buttons)")
    ap.add_argument("--label", action="append", default=[])
    ap.add_argument("--text", action="store_true")
    ap.add_argument("--buttons", action="store_true",
                    help="list the visible buttons and icons with their names / titles")
    ap.add_argument("--screenshot")
    a = ap.parse_args()
    out = {"ok": False, "folder": a.folder, "task": a.task, "labels": [], "left_without_saving": False}
    bad = [c for c in a.click if NEVER.search(c)]
    if bad:
        out["error"] = f"refused to click {bad}: only links and tabs, never buttons that could save"
        print(json.dumps(out))
        sys.exit(2)
    open_screen = opener(a.folder)
    work = LOOK
    work.mkdir(parents=True, exist_ok=True)
    oracle.WORK_DIR = work
    try:
        with browser.OracleUI(work, headless=True) as ui:
            try:
                open_screen(ui, a.task, a.area, a.offering)
                ui.settle()
                ui.check_signed_in()
                if a.heading:
                    ui.wait_heading(a.heading, timeout=90000)
                out["heading"] = [h.strip() for h in ui.page.locator("h1:visible").all_inner_texts()][:3]
                for c in a.click:
                    target = ui.page.locator("a:visible, [role=tab]:visible, [role=menuitem]:visible") \
                        .filter(has_text=re.compile(rf"^\s*{re.escape(c)}\s*$")).first
                    ui.click(target, f"look: {c}")
                    ui.settle()
                for lab in a.label:
                    out["labels"].append({"asked": lab, **(ui.page.evaluate(LABEL_JS, lab) or {"label": None})})
                if a.text:
                    out["text"] = ui.page.locator("body").inner_text()[:3000]
                if a.buttons:
                    out["buttons"] = ui.page.evaluate(BUTTONS_JS)
                if a.screenshot:
                    shot = work / f"{re.sub(r'[^A-Za-z0-9_-]', '_', a.screenshot)}.png"
                    ui.page.screenshot(path=str(shot), full_page=True)
                    out["screenshot"] = str(shot.relative_to(ROOT))
                out["ok"] = True
            finally:
                out["left_without_saving"] = leave(ui)
    except SystemExit:
        out["error"] = "stopped (see the message above, e.g. the sign-in expired)"
    out["screen_opened_by"] = FROM["code"]
    print(json.dumps(out))
    sys.exit(0 if out["ok"] else 1)


if __name__ == "__main__":
    main()
