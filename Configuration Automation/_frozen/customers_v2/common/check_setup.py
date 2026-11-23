"""Check that this PC is ready to run the project. Prints no secret values.

  python common/check_setup.py            # all checks except the saved sign-in
  python common/check_setup.py --final    # also check the saved sign-in; on success
                                          # writes the .setup_ok marker
  python common/check_setup.py --offline  # skip everything that contacts Oracle

Checks: Python 3.12+, packages, .env keys present (values never shown),
ORACLE_ENV rules, one read-only REST call, the Playwright browser starts,
and (with --final) the saved browser sign-in still works and the page's screen-look
helper (page/look.py) can open a task screen and leave without saving.
"""
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
MARKER = ROOT / ".setup_ok"
KEYS = ("ORACLE_USER", "ORACLE_PASS", "ORACLE_HOST", "ORACLE_ENV")

results = []


def report(name, ok, detail="", fix=""):
    results.append(ok)
    print(f"[{'OK' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))
    if not ok and fix:
        print(f"       Fix: {fix}")
    return ok


def check_python():
    v = sys.version_info
    return report("Python 3.12 or newer", v >= (3, 12), f"found {v.major}.{v.minor}.{v.micro}",
                  "install Python 3.12 (winget install Python.Python.3.12)")


def check_packages():
    ok = True
    # openpyxl (added 2026-10-23): the page reads the uploaded Excel sheet with it
    for mod, pkg in (("requests", "requests"), ("dotenv", "python-dotenv"), ("playwright", "playwright"),
                     ("openpyxl", "openpyxl")):
        try:
            __import__(mod)
            report(f"package {pkg}", True)
        except ImportError:
            ok = report(f"package {pkg}", False, "not installed",
                        "pip install -r requirements.txt") and ok
    return ok


def check_env_file():
    env_file = ROOT / ".env"
    if not env_file.exists():
        report(".env file", False, "missing",
               "create it from .env.example and fill in your own Oracle login, "
               "pod address and environment label")
        return None
    from dotenv import dotenv_values
    file_vals = dotenv_values(env_file, encoding="utf-8-sig")  # tolerate a BOM
    vals = {k: (os.environ.get(k) or file_vals.get(k) or "").strip() for k in KEYS}
    missing = [k for k in KEYS if not vals[k]]
    report(".env has all keys filled in", not missing,
           "missing or empty: " + ", ".join(missing) if missing else "all 4 present",
           "open .env and fill in " + ", ".join(missing) if missing else "")
    if missing:
        return None
    if not vals["ORACLE_HOST"].lower().startswith("https://"):
        report("ORACLE_HOST format", False, "does not start with https://",
               "write the full pod address, e.g. https://your-pod.fa.ocs.oraclecloud.com")
        return None
    env = vals["ORACLE_ENV"].lower()
    is_prod = env in ("prod", "production")
    allow = (os.environ.get("ALLOW_PROD") or file_vals.get("ALLOW_PROD") or "").strip().lower()
    report("ORACLE_ENV", not is_prod or allow == "yes",
           f"label is '{vals['ORACLE_ENV']}'" + (" (production)" if is_prod else ""),
           "production needs ALLOW_PROD=yes in .env, added by you deliberately")
    return {"host": vals["ORACLE_HOST"].rstrip("/"), "prod": is_prod}


def check_rest():
    from common import oracle
    import requests
    url = f"{oracle.API_BASE}/standardLookups"
    try:
        r = requests.get(url, params={"finder": "LookupTypeFinder;LookupType=YES_NO",
                                      "onlyData": "true"},
                         auth=(os.environ.get("ORACLE_USER", ""), os.environ.get("ORACLE_PASS", "")),
                         timeout=60)
    except requests.exceptions.SSLError as e:
        return report("Oracle REST call (read-only)", False, f"secure connection failed: {type(e).__name__}",
                      "a company proxy may be intercepting HTTPS; ask IT, or try another network")
    except requests.exceptions.RequestException as e:
        return report("Oracle REST call (read-only)", False, f"cannot reach the pod: {type(e).__name__}",
                      "check the ORACLE_HOST address in .env and your internet/VPN connection")
    fixes = {401: "Oracle rejected the user name or password in .env, or the account is "
                  "locked. Correct ORACLE_USER/ORACLE_PASS, or ask your Oracle admin to unlock it",
             403: "this Oracle user is not allowed to use REST services; ask your Oracle admin",
             404: "the address in ORACLE_HOST is not an Oracle Fusion pod; check it"}
    return report("Oracle REST call (read-only)", r.ok, f"HTTP {r.status_code}",
                  fixes.get(r.status_code, "see the HTTP status above; ask your Oracle admin"))


def check_browser_launch():
    from common import browser
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True, channel=browser.CHANNEL)
            b.new_page().goto("about:blank")
            b.close()
        return report("browser starts (Playwright)", True,
                      f"channel {browser.CHANNEL or 'chromium (Playwright)'}")
    except Exception as e:
        fix = ("playwright install chromium; if that is blocked, set CHANNEL = \"chrome\" "
               "in common/browser.py (uses the installed Google Chrome)"
               if browser.CHANNEL is None else
               f"install {browser.CHANNEL}, or set CHANNEL back to None and run playwright install chromium")
        return report("browser starts (Playwright)", False, f"{type(e).__name__}: {str(e).splitlines()[0][:150]}", fix)


def check_session():
    from common import browser
    if not browser.STATE_FILE.exists():
        return report("saved Oracle sign-in", False, "not signed in yet",
                      "Claude runs common/login_once.py; you sign in in the window that opens")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, channel=browser.CHANNEL)
        ctx = browser.new_context(b)
        page = ctx.new_page()
        try:
            page.goto(browser.start_url(), timeout=90000)
            page.wait_for_timeout(5000)
            ok = browser.is_signed_in(page.url)
        except Exception as e:
            b.close()
            return report("saved Oracle sign-in", False, f"{type(e).__name__}",
                          "check the network, then sign in again with common/login_once.py")
        b.close()
    return report("saved Oracle sign-in", ok, "still valid" if ok else "expired",
                  "sign in again: Claude runs common/login_once.py")


LOOK_SCREEN = {"folder": "Customers", "task": "Create Customer", "area": "Customers",
               "offering": "Financials", "heading": "Create Organization Customer",
               "label": "Account Address Set"}


def check_screen_look():
    """The page's screen-look helper (page/look.py, used by automatic repairs) can open a
    task screen with the saved sign-in, read a field label and leave without saving.
    Read-only: it never types or saves. Prints no secret values."""
    import json
    import subprocess
    look = ROOT / "page" / "look.py"
    if not look.exists():
        return report("screen look works", True, "skipped: this project has no page/look.py")
    s = LOOK_SCREEN
    if not (ROOT / s["folder"] / "browser_flow.py").exists():
        return report("screen look works", True, f"skipped: no {s['folder']} folder to open a screen with")
    cmd = [sys.executable, str(look), "--folder", s["folder"], "--task", s["task"], "--area", s["area"],
           "--offering", s["offering"], "--heading", s["heading"], "--label", s["label"]]
    res, p, last_error = None, None, None
    for _ in range(2):                    # once more after a quick first failure (seen 2026-10-21)
        try:
            p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                               errors="replace", timeout=300)
            res = json.loads(p.stdout.strip().splitlines()[-1])
            if res.get("ok"):
                break
        except Exception as e:  # noqa: BLE001
            last_error = e
    if res is None:
        return report("screen look works", False, f"no answer ({type(last_error).__name__})",
                      "check the internet connection, then run this check again")
    label = (res.get("labels") or [{}])[0].get("label")
    ok = bool(res.get("ok") and label and res.get("left_without_saving"))
    if ok:
        return report("screen look works", True, f"opened '{s['task']}', read '{label}', left without saving")
    err = (res.get("error") or "") + " " + p.stderr[-400:]
    if "sign-in" in err.lower():
        fix = "the saved Oracle sign-in has expired: sign in again (common/login_once.py), then rerun"
    elif not res.get("ok"):
        fix = (f"the '{s['task']}' screen didn't open; check the internet connection and that your "
               f"Oracle user may open it (Setup and Maintenance > {s['offering']}), then rerun")
    else:
        fix = (f"the screen opened but '{s['label']}' wasn't found or it couldn't leave without saving; "
               "Oracle's screen may have changed - tell the person who looks after this project")
    return report("screen look works", False, f"opened={res.get('ok')}, label={label!r}, "
                  f"left without saving={res.get('left_without_saving')}", fix)


def check_claude_tool():
    """Information only, never a failure: Claude's command-line tool is optional (automatic
    fixes). The page installs it per user without admin rights (common/claude_tool.py)."""
    from common import claude_tool
    res = claude_tool.find()
    if res["found"]:
        print(f"[INFO] Claude's command-line tool (optional, automatic fixes): {res['version']}")
    else:
        print(f"[INFO] Claude's command-line tool (optional, automatic fixes): {res['reason']} - "
              "the page installs it for this user, or setup continues without automatic fixes")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--final", action="store_true", help="also check the saved sign-in; write .setup_ok")
    ap.add_argument("--offline", action="store_true", help="skip checks that contact Oracle")
    args = ap.parse_args()

    print(f"Project folder: {ROOT}")
    check_python()
    if not check_packages():
        print("\nStopping: install the packages first.")
        sys.exit(1)
    env = check_env_file()
    if env:
        print(f"       Host: {env['host']}")
    check_browser_launch()
    check_claude_tool()
    if env and not args.offline:
        check_rest()
        if args.final:
            if env["prod"]:
                report("saved Oracle sign-in", True, "skipped: browser work is not allowed on production")
            elif check_session():
                check_screen_look()
    elif args.offline:
        print("[SKIP] Oracle checks (--offline)")

    passed = all(results) and env is not None
    print(f"\n{'All checks passed.' if passed else 'Some checks failed - see Fix lines above.'}")
    if passed and args.final and not args.offline:
        MARKER.write_text(f"setup checks passed {datetime.now():%Y-%m-%d %H:%M} "
                          f"(Python {sys.version.split()[0]})\n", encoding="utf-8")
        print(f"Wrote {MARKER.name}: this PC is set up.")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
