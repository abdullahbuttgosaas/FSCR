"""Quick, read-only check: is the saved Oracle browser sign-in (.session/) still valid?

  python common/session_check.py        # prints one JSON line, exit 0 valid / 1 not valid

Light: a hidden browser opens the Oracle start page once with the saved session and
stops as soon as it sees either the Oracle home (valid) or the sign-in form (expired);
nothing is typed or created. A plain page request is not enough (2026-10-21): the start
page always goes to Oracle's identity service first, which signs a saved session back in
with a script only a browser runs. Prints {"valid", "reason", "how", "seconds", "saved_at"}.
The session file is only handed to Playwright, never read or printed here. Additive
helper for the page's start-up (page/server.py); common/check_setup.py is unchanged.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import browser, oracle  # noqa: E402


def saved_at():
    if not browser.STATE_FILE.exists():
        return None
    ts = browser.STATE_FILE.stat().st_mtime          # when the sign-in was saved (file date only)
    return datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds")


def by_browser(pw, limit=45):
    """True on the Oracle home, False on the sign-in form (or still not home after `limit` s)."""
    b = browser.launch(pw, headless=True)
    try:
        page = browser.new_context(b).new_page()
        page.route(browser.HELP_WIDGET, lambda route: route.abort())
        page.goto(browser.start_url(), timeout=90000, wait_until="domcontentloaded")
        end = time.time() + limit
        while time.time() < end:
            if browser.is_signed_in(page.url):
                return True
            on_signin = urlparse(page.url).hostname != urlparse(oracle.HOST).hostname
            if on_signin and page.locator("input[type=password]:visible").count():
                return False
            page.wait_for_timeout(500)
        return False
    finally:
        b.close()


def main():
    t = time.time()
    out = {"valid": False, "reason": "", "how": "", "saved_at": saved_at()}
    if oracle.ORACLE_ENV.lower() in oracle.PROD_LABELS:
        out.update(reason="production: browser work is not allowed")
    elif not browser.STATE_FILE.exists():
        out.update(reason="missing")
    else:
        try:
            with browser.sync_playwright() as pw:
                ok, out["how"] = by_browser(pw), "browser"
            out.update(valid=bool(ok), reason="valid" if ok else "expired")
        except Exception as e:  # noqa: BLE001 - e.g. no network
            out.update(reason=f"check failed: {type(e).__name__}: {str(e).splitlines()[0][:200] if str(e) else ''}")
    out["seconds"] = round(time.time() - t, 1)
    print(json.dumps(out))
    sys.exit(0 if out["valid"] else 1)


if __name__ == "__main__":
    main()
