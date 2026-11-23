"""Sign in to Oracle once in a visible browser window and keep the session.

Run from the project root:  python common/login_once.py
A browser window opens on the Oracle start page. The USER signs in there (this
script never types or reads credentials). As soon as the Oracle home page is
reached, the session is saved to .session/state.json and the window closes.
Gives up after 15 minutes. Refuses to run when ORACLE_ENV is prod/production.
"""
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import browser, oracle  # noqa: E402

TIMEOUT_SECONDS = 15 * 60


def main():
    oracle.check_environment()
    browser.refuse_production()
    with browser.sync_playwright() as pw:
        b = browser.launch(pw, headless=False)
        ctx = browser.new_context(b, use_session=False)
        page = ctx.new_page()
        page.goto(browser.start_url())
        print("A browser window is open. Please sign in to Oracle there.")
        print("It closes by itself when you reach the Oracle home page.")
        start = time.time()
        while time.time() - start < TIMEOUT_SECONDS:
            if page.is_closed():
                oracle.fail("The browser window was closed before sign-in finished.")
            if browser.is_signed_in(page.url):
                page.wait_for_timeout(3000)  # let the home page settle
                browser.save_session(ctx)
                b.close()
                print("Signed in. Session saved for this PC (.session/, never shared).")
                return
            page.wait_for_timeout(2000)
        b.close()
        oracle.fail("Sign-in did not finish within 15 minutes. Run it again when ready.")


if __name__ == "__main__":
    main()
