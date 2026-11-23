"""Shared Playwright helpers for Oracle UI work.

The user signs in once with common/login_once.py; the signed-in session is kept in
.session/state.json (per PC, never shared). Claude never types credentials.
"""
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from common import oracle

# The last browser step that failed, in plain words, for the page (2026-10-26): set by OracleUI.retry() (e.g.
# "Oracle's Setup page did not open Create Customer after 3 tries") or, for any other failed step, by step().
# A folder's read-only check prints it as its reason, so the page shows the real step instead of "no answer".
FAILED_STEP = {"text": None}


def failed_step_text(default=None):
    """The plain reason of the last failed browser step in this process, or `default`."""
    return FAILED_STEP["text"] or default

SESSION_DIR = oracle.PROJECT_ROOT / ".session"
STATE_FILE = SESSION_DIR / "state.json"

# None = Playwright's own Chromium (installed by "playwright install chromium").
# If that install is blocked on a PC, set this to "chrome" to use the installed
# Google Chrome instead (or "msedge" for Microsoft Edge).
CHANNEL = None

START_PATH = "/fscmUI/faces/AtkHomePageWelcome"


def start_url():
    return f"{oracle.HOST}{START_PATH}"


def refuse_production():
    """Browser rule: never open Oracle in the browser for prod/production."""
    if oracle.ORACLE_ENV.lower() in oracle.PROD_LABELS:
        oracle.fail(f"ORACLE_ENV is '{oracle.ORACLE_ENV}': browser work against "
                    "production is not allowed. Nothing was opened.")


def is_signed_in(url):
    """True once the page is on the Oracle pod itself (not the sign-in service)."""
    u, host = urlparse(url), urlparse(oracle.HOST)
    return u.hostname == host.hostname and u.path.startswith("/fscmUI/")


def launch(playwright, headless=True):
    try:
        return playwright.chromium.launch(headless=headless, channel=CHANNEL)
    except Exception as e:  # browser binary missing or blocked
        fix = ("run: playwright install chromium" if CHANNEL is None else
               f"install {CHANNEL} or set CHANNEL in common/browser.py")
        oracle.fail(f"Could not start the browser ({type(e).__name__}): {e}\nFix: {fix}")


def new_context(browser, use_session=True):
    """Browser context, signed in from .session/state.json when it exists."""
    if use_session and STATE_FILE.exists():
        return browser.new_context(storage_state=str(STATE_FILE), accept_downloads=True)
    return browser.new_context(accept_downloads=True)


def save_session(context):
    SESSION_DIR.mkdir(exist_ok=True)
    context.storage_state(path=str(STATE_FILE))


def sync_playwright():
    try:
        from playwright.sync_api import sync_playwright as sp
    except ImportError:
        oracle.fail("Playwright is not installed. Fix: pip install -r requirements.txt")
    return sp()


# ---------------------------------------------------------------- Setup and Maintenance UI

SETUP_PATH = "/fscmUI/faces/FuseTaskListManagerTop"   # opens Setup and Maintenance directly
HELP_WIDGET = "**/guidedlearning.oracle.com/**"        # "Oracle Guided Learning" pop-up source
RUNNING = ("Not started", "In progress", "Running", "Processing", "Queued", "Submitted")
EXPORT_CONFIRM = re.compile(r"has been initiated in the (.+?) process")
IMPORT_CONFIRM = re.compile(r"has been submitted to the (.+?) process")


class OracleUI:
    """Drive a Setup and Maintenance task's Export/Import to CSV File actions.

    with OracleUI(work_dir) as ui:
        zip_path, summary = ui.export_csv("Manage Payment Terms", "Payables", "Financials")
        summary = ui.import_csv("Manage Payment Terms", "Payables", zip_path, "Financials")

    Any offering / functional area / task works by name. Setup and Maintenance opens
    the Redwood "Set Up <offering>" page (since 2026-10-20) at one address and
    remembers the user's last offering, so open_area() switches the offering when
    the page shows a different one.

    Uses the session saved by common/login_once.py. Stops (oracle.fail) with a plain
    message when the session has expired, and keeps a screenshot + page text in
    work_dir for every failure.
    """

    def __init__(self, work_dir, headless=True, poll_seconds=10, timeout_seconds=1800):
        self.work = Path(work_dir)
        self.headless = headless
        self.poll = poll_seconds
        self.timeout = timeout_seconds

    # ---- lifecycle
    def __enter__(self):
        oracle.check_environment()
        refuse_production()
        if not STATE_FILE.exists():
            oracle.fail("No saved Oracle sign-in on this PC. Run common/login_once.py "
                        "and sign in, then run this again.")
        self._pw_cm = sync_playwright()
        self._pw = self._pw_cm.__enter__()
        self.browser = launch(self._pw, headless=self.headless)
        self.context = self.browser.new_context(storage_state=str(STATE_FILE), accept_downloads=True,
                                                viewport={"width": 1600, "height": 1000})
        # The Guided Learning help widget opens a pop-up over the page and swallows
        # clicks; it is not needed for automation, so it is not loaded at all.
        self.context.route(HELP_WIDGET, lambda route: route.abort())
        self.context.set_default_timeout(60000)
        self.page = self.context.new_page()
        return self

    def __exit__(self, *exc):
        try:
            self.browser.close()
        finally:
            self._pw_cm.__exit__(*exc)

    # ---- basics
    def log(self, msg):
        print(f"  [ui] {msg}", flush=True)

    def settle(self):
        """Wait for Oracle's partial page refreshes to finish."""
        try:
            self.page.wait_for_load_state("networkidle", timeout=90000)
        except Exception:
            pass  # long-polling pages never go fully idle; the explicit waits below decide

    def evidence(self, tag):
        """Keep a screenshot and the page text for a failure."""
        self.work.mkdir(parents=True, exist_ok=True)
        shot, text = self.work / f"fail_{tag}.png", self.work / f"fail_{tag}.txt"
        try:
            self.page.screenshot(path=str(shot), full_page=True)
            text.write_text(self.page.inner_text("body"), encoding="utf-8")
        except Exception:
            pass
        return shot

    def retry(self, plain, act, done, tries=3, pause=3.0, wait=20000, last_wait=60000, soft=False):
        """A browser step that Oracle may drop while its page is still busy (2026-10-26: a search or a click made
        too early is lost). act(attempt) does the step (attempt 1, 2, 3: the caller may repeat it differently, e.g.
        click the link again); done(timeout_ms) checks the expected result really appeared (the heading, dialog or
        rows) and raises or returns False when it didn't. Up to `tries` tries with a short pause and a fresh wait
        each time (the last wait longer), then one clear failure: "Oracle's <plain> after 3 tries". Never use it
        for a step that may already have saved data in Oracle (Save, Submit, Import). soft=True: after the last try
        return 0 instead of failing (the caller then decides, e.g. "Oracle offers no such field here")."""
        err = None
        for attempt in range(1, tries + 1):
            if attempt > 1:
                self.log(f"{plain}: not yet (try {attempt - 1}/{tries}); trying again")
                self.check_signed_in()
                self.dismiss_popups()
                self.page.wait_for_timeout(int(pause * 1000))
            try:
                act(attempt)
                if done(wait if attempt < tries else last_wait) is not False:
                    if attempt > 1:
                        self.log(f"{plain}: done on try {attempt}/{tries}")
                    return attempt
            except SystemExit:
                raise
            except Exception as e:  # noqa: BLE001 - a Playwright timeout or a lost element: try again
                err = e
        if soft:
            self.log(f"{plain}: still not after {tries} tries")
            return 0
        FAILED_STEP["text"] = f"Oracle's {plain} after {tries} tries"
        self.fail("retry", FAILED_STEP["text"] + (f" ({str(err).splitlines()[0][:160]})" if err else ""))

    def fail(self, tag, message):
        if not FAILED_STEP["text"]:
            FAILED_STEP["text"] = str(message).splitlines()[0][:300]
        shot = self.evidence(tag)
        oracle.fail(f"{message}\n  Screenshot: {shot}")

    def check_signed_in(self):
        if not is_signed_in(self.page.url):
            self.evidence("signin")
            oracle.fail("The saved Oracle sign-in has expired (the sign-in page appeared). "
                        "Run common/login_once.py, sign in, then run this again.")

    def dismiss_popups(self):
        """Fallback if a Guided Learning dialog still shows: close it."""
        dlg = self.page.get_by_role("dialog", name="Welcome to Oracle Guided Learning")
        if dlg.count() and dlg.first.is_visible():
            for sel in ("button[aria-label='Close']:visible", "button:visible"):
                btn = dlg.first.locator(sel)
                if btn.count():
                    btn.first.click()
                    self.log("closed the Guided Learning pop-up")
                    return

    def visible(self, text):
        """The visible element showing exactly this text (menus exist hidden per row)."""
        return self.page.locator(f"td:text-is('{text}'):visible, a:text-is('{text}'):visible, "
                                 f"span:text-is('{text}'):visible").first

    def click(self, locator, what, tries=3):
        """Click with retries: Oracle re-renders rows and menus while they load."""
        for attempt in range(1, tries + 1):
            try:
                locator.click(timeout=20000)
                return
            except Exception as e:
                self.check_signed_in()
                self.dismiss_popups()
                self.log(f"retry {attempt}/{tries} clicking {what}: {str(e).splitlines()[0][:120]}")
                self.page.wait_for_timeout(2000)
        self.fail("click", f"Could not click {what} after {tries} tries.")

    def choose(self, select, label):
        """Pick an option in an ADF drop-down like a person does. A bare select_option
        is sometimes ignored by Oracle (no refresh); focus + choose + Tab is not."""
        def act(attempt):
            select.focus()
            select.select_option(label=label)
            select.press("Tab")
            self.settle()

        def done(timeout):                   # 2026-10-26: the chosen label is really the selected one
            end = time.time() + timeout / 1000
            while time.time() < end:
                try:
                    if select.evaluate("s => s.selectedIndex >= 0 ? s.options[s.selectedIndex].text.trim() : ''") \
                            == label.strip():
                        return True
                except Exception:            # noqa: BLE001 - the drop-down was redrawn: look again
                    pass
                self.page.wait_for_timeout(300)
            return False
        self.retry(f"drop-down did not take '{label}'", act, done, wait=5000, last_wait=10000)

    def button(self, name_pattern):
        return self.page.get_by_role("button", name=re.compile(name_pattern)).first

    # ---- navigation (Redwood "Set Up <offering>" page, since 2026-10-20)
    # Setup and Maintenance now redirects to /fscmUI/redwood/setup/functional-setup/...
    # The classic "Setup: <offering>" page is gone for this user. Task screens
    # themselves (Create Customer, Manage Payment Terms, ...) are still classic ADF.
    SWITCHER = "h1[role=button][aria-haspopup=true]"     # "Set Up <offering>" title
    MENU_NAMES = {("Export to CSV File", "Create New"): "Export",
                  ("Export to CSV File", "View All"): "Export History",
                  ("Import from CSV File", "Create New"): "Import",
                  ("Import from CSV File", "View All"): "Import History"}

    def use_newest_page(self):
        """Task links may open a new browser tab; always work in the newest one."""
        pages = [p for p in self.context.pages if not p.is_closed()]
        if pages and pages[-1] is not self.page:
            self.page = pages[-1]
            self.page.wait_for_load_state("domcontentloaded")

    def wait_setup_page(self):
        try:
            self.page.locator(self.SWITCHER).first.wait_for(timeout=120000)
            self.page.locator("li[role=row]:visible").first.wait_for(timeout=120000)
        except Exception:
            self.check_signed_in()
            self.fail("offering", "Setup and Maintenance did not show its 'Set Up' page.")
        self.settle()

    def open_setup(self):
        self.page.goto(f"{oracle.HOST}{SETUP_PATH}", wait_until="domcontentloaded", timeout=120000)
        self.settle()
        self.check_signed_in()
        self.wait_setup_page()

    def current_offering(self):
        return (self.page.locator(self.SWITCHER).first.get_attribute("aria-label") or "").strip()

    def open_offering(self, offering):
        """Set Up page with the given offering selected (e.g. "Financials")."""
        self.open_setup()
        shown = self.current_offering()
        if shown == offering:
            return
        self.log(f"switching offering from '{shown}' to '{offering}'")
        items = self.page.locator("oj-list-view[id^='oj-sp-data-switcher-list-view'] li:visible")
        item = items.filter(has_text=re.compile(rf"^\s*{re.escape(offering)}\s*$")).first

        def offered(timeout):
            if self.current_offering() == offering:
                return True
            item.wait_for(timeout=timeout)
            item.click(timeout=10000)
            for _ in range(max(1, timeout // 1000)):
                if self.current_offering() == offering:
                    return True
                self.page.wait_for_timeout(1000)
            return False
        self.retry(f"Setup page did not switch to the offering '{offering}'",
                   lambda attempt: self.current_offering() == offering or
                   self.click(self.page.locator(self.SWITCHER).first, "offering switcher"),
                   offered, wait=30000, last_wait=60000)
        self.wait_setup_page()

    def open_area(self, area, offering=None):
        if offering:
            self.open_offering(offering)
        else:
            self.open_setup()
        item = self.page.locator("li[role=row]:visible").filter(
            has_text=re.compile(rf"^\s*{re.escape(area)}\s*$")).first
        try:
            item.wait_for(timeout=60000)
        except Exception:
            self.fail("area", f"Functional area '{area}' not found on 'Set Up "
                              f"{self.current_offering()}'.")
        self.retry(f"Setup page did not open the functional area '{area}'",
                   lambda attempt: self.click(item, f"functional area {area}"),
                   lambda timeout: self.page.locator("button[aria-label$=' Actions']").first.wait_for(timeout=timeout),
                   wait=30000, last_wait=60000)
        self.settle()

    def load_task(self, task, max_rounds=40):
        """The task's link in the area's list. The list loads 25 tasks at a time while
        scrolling, so scroll to its end until the task shows (or the list stops growing)."""
        link = self.page.locator(f"li a:text-is('{task}')")
        grow = r"""() => { const a = [...document.querySelectorAll('li a')]
            .filter(a => a.innerText.trim() && a.closest('li').querySelector("button[aria-label$=' Actions']"));
            if (a.length) a[a.length - 1].scrollIntoView(); return a.length; }"""
        last, same = -1, 0
        for _ in range(max_rounds):
            if link.count():
                link.first.scroll_into_view_if_needed()
                return link.first
            n = self.page.evaluate(grow)
            self.page.mouse.wheel(0, 1200)
            self.page.wait_for_timeout(2500)
            same = same + 1 if n == last else 0
            if same >= 4:
                break
            last = n
        self.fail("task", f"Task '{task}' not found in this functional area ({last} tasks listed).")

    def find_task(self, task):
        """The task's Actions button ("<task> Actions") in the current functional area."""
        link = self.load_task(task)
        return link.locator("xpath=ancestor::li[1]").locator(
            f"button[aria-label='{task} Actions']").first

    def open_task_link(self, link, task):
        start = (len(self.context.pages), self.page.url)

        def act(attempt):
            if attempt == 1 or link.count() and link.is_visible():
                self.click(link, f"task {task}")
            self.page.wait_for_timeout(3000)
            self.use_newest_page()
            self.settle()

        def done(timeout):                   # 2026-10-26: a new tab, a new address, or the link has gone
            end = time.time() + timeout / 1000
            while time.time() < end:
                if (len(self.context.pages), self.page.url) != start or not (link.count() and link.is_visible()):
                    return True
                self.page.wait_for_timeout(500)
            return False
        self.retry(f"Setup page did not open {task}", act, done)

    def open_task(self, task, area, offering=None):
        """Open the task's own page (e.g. Manage Order Lookups) from Setup and Maintenance."""
        self.open_area(area, offering)
        self.open_task_link(self.load_task(task), task)

    def task_menu(self, task, menu, entry=None):
        """Task Actions > entry. Accepts the new names (Export, Export History, Import,
        Import History) or the classic pairs (Export to CSV File, Create New / View All)."""
        name = self.MENU_NAMES.get((menu, entry), menu)
        actions = self.find_task(task)
        item = self.page.locator("[role=menuitem]:visible").filter(
            has_text=re.compile(rf"^\s*{re.escape(name)}\s*$")).first
        self.retry(f"Actions menu of {task} did not open",
                   lambda attempt: self.click(actions, f"{task} Actions"),
                   lambda timeout: item.wait_for(timeout=timeout), wait=10000, last_wait=20000)
        if item.get_attribute("aria-disabled") == "true":
            self.fail("menu", f"'{name}' is disabled in the Actions menu of '{task}'.")
        self.click(item, f"{task} Actions > {name}")
        self.page.wait_for_timeout(3000)
        self.use_newest_page()
        self.settle()

    def search_task(self, task, area, offering=None):
        """Open a task's own page by name and functional area (e.g. Create Customer in
        Customers). The Redwood area list loads its tasks while scrolling, so the task is
        reached by opening the area and scrolling to it. (The page's Name search drawer
        sometimes stays open over the page and blocks clicks, so it is not used.)"""
        self.open_task(task, area, offering)

    # ---- form helpers (ADF pages)
    def field(self, label, scope=None):
        """The visible form element with exactly this label. Search dialogs keep
        hidden copies of fields with the same label, so only visible ones count."""
        root = scope or self.page
        return root.get_by_label(label, exact=True).and_(self.page.locator(":visible")).first

    def wait_heading(self, text, timeout=90000):
        """Wait until a page heading (e.g. "Manage Customers") is shown."""
        self.page.locator("h1:visible").filter(
            has_text=re.compile(rf"^\s*{re.escape(text)}")).first.wait_for(timeout=timeout)
        self.settle()

    @staticmethod
    def match_value(wanted, choices):
        """The one choice equal to wanted: exact first, else case-insensitive if that
        is unique. None when nothing (or more than one) matches. Never guesses."""
        if wanted in choices:
            return wanted
        low = [c for c in choices if c.lower() == wanted.lower()]
        return low[0] if len(set(low)) == 1 else None

    def field_error(self, element):
        """Oracle's message for a field it marked invalid (red border), else None.
        ADF marks the field's row with p_AFError and shows the text in a note
        window when the field has focus."""
        if not element.evaluate("e => !!e.closest('.p_AFError')"):
            return None
        try:
            element.focus()
            self.page.wait_for_timeout(1000)
        except Exception:
            pass
        notes = [" ".join(t.split()) for t in self.page.locator(
            ".AFNoteWindow:visible, [role=alert]:visible").all_inner_texts() if t.strip()]
        return "; ".join(dict.fromkeys(n for n in notes if n.startswith("Error"))) or "invalid value"

    def set_check(self, box, value, what):
        """Tick or untick an ADF checkbox. ADF draws its own box over the input, so a
        click on the input is intercepted; click its label (or the drawn box)."""
        box_id = box.get_attribute("id")
        targets = [self.page.locator(f"label[for='{box_id}']:visible").first,
                   box.locator("xpath=..").first, box]
        for target in targets:
            if box.is_checked() == value:
                break
            try:
                target.click(timeout=10000)
            except Exception:
                continue
            self.settle()
        if box.is_checked() != value:
            self.fail("check", f"Could not {'tick' if value else 'untick'} '{what}'.")

    def select_options(self, select):
        return [o.strip() for o in select.locator("option").all_inner_texts()]

    def lov_dialogs(self):
        """Open "Search and Select" dialogs of list-of-values fields."""
        return self.page.locator("div[id$='::lovDialogId']:visible")

    def close_lov_dialogs(self):
        for dlg in reversed(self.lov_dialogs().all()):   # newest is on top
            self.close_dialog(dlg, "Search dialog")

    def close_dialog(self, dlg, what):
        """Cancel a Search and Select dialog and make sure it closed (2026-10-26: a lost Cancel left a dialog that
        the next step picked up). Cancel never saves anything."""
        def act(attempt):
            if dlg.is_visible():
                self.click(dlg.get_by_role("button", name="Cancel").first, f"{what} Cancel")
            self.page.wait_for_timeout(800)

        def done(timeout):
            dlg.wait_for(state="hidden", timeout=timeout)
        self.retry(f"{what} did not close", act, done, wait=5000, last_wait=15000)

    def fresh_search(self, search, read, what, wait=10, tries=3):
        """A read-only search whose answer is believed only when it is fresh (2026-10-26: a Search clicked while
        Oracle is busy is lost and the old rows, or none, were read as the answer). search() clicks the Search
        button; read() returns what the screen shows now. The answer is the first read that differs from what
        was shown before the click, or, when nothing changes, what two searches in a row agree on. Up to `tries`
        searches; never fails (an empty or unchanged answer is still an answer), so it is only for reads."""
        seen = []
        for attempt in range(1, tries + 1):
            before = read()
            search()
            self.settle()
            end = time.time() + (wait if attempt < tries else wait * 3)
            got = before
            while time.time() < end:
                self.page.wait_for_timeout(1000)
                got = read()
                if got != before:
                    return got
            if seen and seen[-1] == got:
                return got
            seen.append(got)
            if attempt < tries:
                self.log(f"{what}: the screen did not change after Search (try {attempt}/{tries}); searching again")
        return got

    def search_dialog(self, open_list, more, what):
        """Open a field's Search and Select dialog: open_list() clicks the field's list icon, `more` is its
        "Search..." link. Each click is checked and done again when lost (2026-10-26). Returns the dialog."""
        self.retry(f"{what} list did not open", lambda attempt: more.count() and more.is_visible() or open_list(),
                   lambda timeout: more.wait_for(timeout=timeout), wait=20000, last_wait=30000)
        before = self.lov_dialogs().count()

        def opened(timeout):
            end = time.time() + timeout / 1000
            while time.time() < end:
                if self.lov_dialogs().count() > before:
                    return True
                self.page.wait_for_timeout(500)
            return False
        self.retry(f"{what} search dialog did not open",
                   lambda attempt: self.lov_dialogs().count() > before or self.click(more, f"{what} Search..."),
                   opened, wait=30000, last_wait=60000)
        return self.lov_dialogs().last

    def lov_rows(self, dlg):
        """Result rows of a Search and Select dialog as lists of cell texts."""
        return dlg.evaluate(r"""d => [...d.querySelectorAll('tr[_afrrk]')]
            .map(r => [...r.querySelectorAll('td')].filter(td => !td.querySelector('td'))
                 .map(td => td.innerText.trim()).filter(t => t))
            .filter(c => c.length)""")

    def lov_type(self, element, value, what):
        """Type a value into a list-of-values field and Tab out, like a person.

        Oracle accepts a unique match silently. When the value is not unique or not
        known it opens the field's Search and Select dialog: a row whose cell equals
        the value is picked (exactly, or case-insensitively when unique); otherwise
        the dialog is closed. Returns (ok, rows shown in the dialog)."""
        element.fill(value)
        element.press("Tab")
        self.settle()
        self.page.wait_for_timeout(1500)
        dialogs = self.lov_dialogs()
        if not dialogs.count():
            return True, []
        dlg = dialogs.last
        rows = self.lov_rows(dlg)
        cells = [c for r in rows for c in r]
        hit = self.match_value(value, cells)
        if hit is not None:
            cell = dlg.locator("tr[_afrrk] td:visible").filter(
                has_text=re.compile(rf"^\s*{re.escape(hit)}\s*$")).first
            def pick(attempt):
                if dlg.is_visible():
                    self.click(cell, f"{what} value {hit}")
                    self.click(dlg.get_by_role("button", name="OK", exact=True), f"{what} OK")
                self.settle()
            self.retry(f"{what} search dialog did not take '{hit}'", pick,
                       lambda timeout: dlg.wait_for(state="hidden", timeout=timeout), wait=10000, last_wait=20000)
            self.log(f"{what}: picked {hit!r} in the search dialog")
            return True, rows
        self.close_lov_dialogs()
        return False, rows

    def lov_search_all(self, icon, what, max_rows=2000):
        """All rows of a list-of-values field's Search and Select dialog (empty search).

        icon: the field's search icon (id ends with ::lovIconId). Scrolls the
        result table until no new rows load. Leaves the dialog with Cancel."""
        page = self.page
        more = page.locator("a:text-is('Search...'):visible").last
        self.retry(f"{what} list did not open",
                   lambda attempt: more.count() and more.is_visible() or self.click(icon, f"{what} list"),
                   lambda timeout: more.wait_for(timeout=timeout), wait=20000, last_wait=30000)
        before = self.lov_dialogs().count()

        def opened(timeout):
            end = time.time() + timeout / 1000
            while time.time() < end:
                if self.lov_dialogs().count() > before:
                    return True
                page.wait_for_timeout(500)
            return False
        self.retry(f"{what} search dialog did not open",
                   lambda attempt: self.lov_dialogs().count() > before or self.click(more, f"{what} Search..."),
                   opened, wait=30000, last_wait=60000)
        dlg = self.lov_dialogs().last
        empty = dlg.get_by_text(re.compile(r"^\s*No (rows|results|data)", re.I)).first
        nothing = {"n": 0}

        def searched(timeout):               # rows, or "No rows" that a second search agrees with
            end = time.time() + timeout / 1000
            while time.time() < end:
                if self.lov_rows(dlg):
                    return True
                if empty.count() and empty.is_visible():
                    nothing["n"] += 1
                    return nothing["n"] >= 2 or None
                page.wait_for_timeout(500)
            return False

        def search(attempt):
            self.click(dlg.get_by_role("button", name="Search", exact=True), f"{what} Search")
            self.settle()
            page.wait_for_timeout(2000)
        for attempt in range(1, 4):          # 2026-10-26: a Search lost while Oracle is busy silently gave []
            search(attempt)
            got = searched(20000 if attempt < 3 else 40000)
            if got:
                break
            if got is None and attempt >= 2:
                break
            self.log(f"{what} search showed no rows yet (try {attempt}/3); searching again")
        seen = {}
        body = dlg.locator("div[id$='::db']").first
        for _ in range(200):
            before = len(seen)
            for r in self.lov_rows(dlg):
                seen.setdefault(tuple(r), None)
            if len(seen) >= max_rows or not body.count():
                break
            at_end = body.evaluate("e => e.scrollTop + e.clientHeight >= e.scrollHeight - 2")
            if at_end and len(seen) == before:
                break
            body.evaluate("e => { e.scrollTop += 300; }")
            page.wait_for_timeout(1200)
        self.close_dialog(dlg, f"{what} search dialog")
        return [list(r) for r in seen]

    def page_messages(self):
        """Texts of visible Oracle message dialogs (Error / Warning / Confirmation).
        ADF shows them in a popup whose id ends with ::msgDlg."""
        return [" ".join(t.split()) for t in
                self.page.locator("div[id$='::msgDlg']:visible").all_inner_texts() if t.strip()]

    def close_messages(self):
        for dlg in self.page.locator("div[id$='::msgDlg']:visible").all():
            self.click(dlg.get_by_role("button", name=re.compile(r"^O\s*K$")).first, "message OK")
            self.page.wait_for_timeout(1000)

    def step(self, name):
        """with ui.step("fill address"): ...  Any Playwright error inside becomes one
        clear failure naming the step, with a screenshot. Each Playwright wait has
        its own timeout (60 s default), so a hanging step fails within minutes."""
        ui = self

        class _Step:
            def __enter__(self):
                ui.log(f"step: {name}")
                self.t = time.time()

            def __exit__(self, kind, err, tb):
                if kind is None or issubclass(kind, SystemExit):
                    return False
                ui.check_signed_in()
                first = str(err).splitlines()[0][:300] if str(err) else kind.__name__
                if not FAILED_STEP["text"]:
                    FAILED_STEP["text"] = f"Oracle's screens did not finish the step '{name}'"
                ui.fail("step", f"Step '{name}' failed after {int(time.time() - self.t)}s: {first}")
        return _Step()

    # ---- Oracle's own date (never the PC clock)
    MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
              "September", "October", "November", "December")

    @staticmethod
    def parse_screen_date(text):
        """Oracle's on-screen m/d/yy (e.g. 10/20/26) -> datetime.date."""
        import datetime as _dt
        m, d, y = (int(x) for x in text.strip().split("/"))
        return _dt.date(2000 + y if y < 100 else y, m, d)

    def picker_today(self, date_input, what="date field"):
        """Oracle's today from an EMPTY date field's calendar: Oracle opens it on its
        own current month with today selected. Read-only: the calendar is closed with
        Escape and the field stays empty."""
        import datetime as _dt
        if date_input.input_value().strip():
            self.fail("today", f"{what} is not empty; cannot read Oracle's today from it.")
        glyph = date_input.locator("xpath=ancestor::tr[1]").locator("a[title='Select Date']").first
        self.click(glyph, f"{what} calendar")
        grid = self.page.locator("table[summary][id$='::cg']:visible").first
        try:
            grid.wait_for(timeout=20000)
        except Exception:
            self.fail("today", f"The calendar of {what} did not open.")
        month, year = grid.get_attribute("summary").split()
        day = grid.locator("td.p_AFSelected").first.inner_text().strip()
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(800)
        if date_input.input_value().strip():
            self.fail("today", f"{what} changed while reading the calendar.")
        today = _dt.date(int(year), self.MONTHS.index(month) + 1, int(day))
        self.log(f"Oracle's today (calendar of {what}): {today.isoformat()}")
        return today

    def done(self):
        """Use the page's Done button (browser Back leaves Setup and Maintenance)."""
        btn = self.page.get_by_role("button", name="Done")
        if btn.count():
            self.click(btn.first, "Done")
            self.settle()

    # ---- process tracking (Redwood "Setup Export History" / "Setup Import History")
    HISTORY_JS = r"""(name) => {
        const rows = [...document.querySelectorAll('tr')].filter(r => r.offsetWidth);
        const head = rows.find(r => r.querySelector('th') && /Status/.test(r.innerText));
        if (!head) return null;
        const heads = [...head.querySelectorAll('th')].map(th => th.innerText.trim());
        const out = [];
        for (const r of rows) {
            const tds = [...r.querySelectorAll('td')];
            if (!tds.length) continue;
            const rec = {};
            heads.forEach((h, i) => { if (h && tds[i]) rec[h] = tds[i].innerText.trim(); });
            if (!name || rec['Name'] === name) out.push(rec);
        }
        return out;
    }"""

    def history_rows(self, name=None):
        return self.page.evaluate(self.HISTORY_JS, name) or []

    def open_history(self, task, area, kind, offering=None):
        """kind: "Export" or "Import"."""
        self.open_area(area, offering)
        self.task_menu(task, f"{kind} History")
        try:
            self.page.get_by_role("button", name="Refresh").first.wait_for(timeout=60000)
        except Exception:
            self.fail("history", f"Setup {kind} History did not open.")
        self.settle()

    def wait_process(self, task, area, kind, process, offering=None):
        """Follow the process on <kind> History, refreshing until it finishes.
        Returns the row (dict by column name)."""
        if kind.endswith("CSV File"):
            kind = "Export" if kind.startswith("Export") else "Import"
        self.open_history(task, area, kind, offering)
        start = time.time()
        while True:
            rows = self.history_rows(process)
            status = rows[0].get("Status", "") if rows else ""
            elapsed = int(time.time() - start)
            self.log(f"{kind}: {process} status '{status or 'not listed yet'}' ({elapsed}s)")
            if status and status not in RUNNING:
                return rows[0]
            if elapsed > self.timeout:
                self.fail("timeout", f"{process} still '{status}' after {elapsed}s.")
            self.page.wait_for_timeout(self.poll * 1000)
            self.click(self.page.get_by_role("button", name="Refresh").first, "Refresh")
            self.settle()

    @staticmethod
    def summarize(row, process):
        total = row.get("Total Business Objects", "")
        done_ = row.get("Total Completed", "")
        good = row.get("Successful", "")
        errors = str(int(total) - int(good)) if total.isdigit() and good.isdigit() else None
        return {"status": row.get("Status"), "total": total, "completed": done_,
                "successful": good, "errors": errors, "process": process, "row": row}

    @staticmethod
    def complete(summary, stage=None):
        """Finished cleanly: status Successful and every business object completed and
        successful. (`stage` is ignored: the Redwood history shows no stage.)"""
        return (summary["status"] == "Successful" and summary["total"]
                and summary["total"] == summary["completed"] == summary["successful"])

    # ---- read-only check of the export/import screens (for --check)
    def check_actions(self, task, area, offering=None):
        """Open Actions > Export (New Setup Export) and Actions > Import (New Setup
        Import), confirm their fields and buttons are there, and leave each with
        Cancel. Nothing is submitted, so nothing is created in Oracle."""
        page = self.page
        for kind, need in (("Export", "input[id$='format_id|input']"), ("Import", None)):
            self.open_area(area, offering)
            self.task_menu(task, kind)
            page = self.page
            try:
                page.locator("h1:visible").filter(has_text=f"New Setup {kind}").first.wait_for(timeout=60000)
                if need:
                    page.locator(need).first.wait_for(state="attached", timeout=60000)
                else:
                    page.get_by_text("Drag and Drop").first.wait_for(timeout=60000)
                page.get_by_role("button", name=kind, exact=True).last.wait_for(timeout=30000)
            except Exception:
                self.fail("check", f"New Setup {kind} did not show its fields and {kind} button.")
            self.log(f"Actions > {kind} opens 'New Setup {kind}' with its fields; leaving with Cancel")
            self.click(page.get_by_role("button", name="Cancel").and_(page.locator(":visible")).first,
                       f"{kind} Cancel")
            self.page.wait_for_timeout(3000)
            self.use_newest_page()
            try:
                self.page.locator(self.SWITCHER).first.wait_for(timeout=60000)
            except Exception:
                self.fail("check", f"Cancel on New Setup {kind} did not return to the Set Up page.")

    # ---- the two actions
    def export_csv(self, task, area, offering=None):
        """Fresh CSV export downloaded into work_dir. Returns (zip path, summary)."""
        self.open_area(area, offering)
        self.task_menu(task, "Export")
        page = self.page
        try:
            page.locator("h1:visible").filter(has_text="New Setup Export").first.wait_for(timeout=60000)
        except Exception:
            self.fail("export", "New Setup Export did not open.")
        fmt = page.locator("input[id$='format_id|input']").first
        fmt.wait_for(state="attached", timeout=60000)
        if fmt.input_value() != "CSV or JSON":
            # the combobox input itself is not clickable; its visible label opens it
            self.click(page.get_by_text("File Format", exact=True).first, "File Format")
            option = page.locator("[id='lovDropdown_format_id']").get_by_text("CSV or JSON", exact=True).first
            try:
                option.wait_for(timeout=20000)
            except Exception:
                self.fail("export", "File Format has no 'CSV or JSON' choice.")
            self.click(option, "File Format CSV or JSON")
            page.wait_for_timeout(2000)
        process = ""
        for _ in range(30):
            vals = [i.input_value() for i in page.locator("input[type=text]:visible, input:not([type]):visible").all()]
            process = next((v for v in vals if v.startswith(task) and "_" in v), "")
            if process:
                break
            page.wait_for_timeout(1000)
        if not process:
            self.fail("export", "New Setup Export did not fill in a process name.")
        try:
            page.get_by_text("Tasks and business objects").first.wait_for(timeout=60000)
        except Exception:
            self.fail("export", "New Setup Export did not list the business objects.")
        export_btn = page.get_by_role("button", name="Export", exact=True).last
        for _ in range(30):
            if export_btn.is_enabled():
                break
            page.wait_for_timeout(1000)
        self.click(export_btn, "Export")
        try:
            page.get_by_text("Process submitted").first.wait_for(timeout=120000)
        except Exception:
            self.fail("export", "No 'Process submitted' message after Export.")
        self.log(f"export submitted: {process}")
        row = self.wait_process(task, area, "Export", process, offering)
        summary = self.summarize(row, process)
        if not self.complete(summary):
            self.fail("export", f"Export {process} did not complete: status '{summary['status']}', "
                                f"{summary['completed']}/{summary['total']} objects completed, "
                                f"{summary['successful']} successful.")
        self.work.mkdir(parents=True, exist_ok=True)
        tr = self.page.locator("tr").filter(has_text=process).first
        with self.page.expect_download(timeout=180000) as dl:
            self.click(tr.get_by_role("button", name="Download").first, "Download")
        path = self.work / dl.value.suggested_filename
        dl.value.save_as(str(path))
        self.log(f"downloaded {path.name} ({path.stat().st_size} bytes); "
                 f"{summary['completed']}/{summary['total']} objects")
        return path, summary

    def import_csv(self, task, area, zip_path, offering=None):
        """Import a CSV zip. Returns the history summary; fails unless fully successful.

        The new import page shows no process name, so the process is the Import
        History row that was not there before submitting."""
        zip_path = Path(zip_path)
        self.open_history(task, area, "Import", offering)
        known = {r.get("Name") for r in self.history_rows()}
        self.open_area(area, offering)
        self.task_menu(task, "Import")
        page = self.page
        try:
            page.locator("h1:visible").filter(has_text="New Setup Import").first.wait_for(timeout=60000)
            drop = page.get_by_text("Drag and Drop").first
            drop.wait_for(timeout=60000)
        except Exception:
            self.fail("import", "New Setup Import did not open.")
        with page.expect_file_chooser(timeout=30000) as fc:
            self.click(drop, "file drop area")
        fc.value.set_files(str(zip_path))                 # no native file picker
        try:
            page.get_by_text(zip_path.name).first.wait_for(timeout=120000)
        except Exception:
            self.fail("attach", f"Oracle did not show the attached file {zip_path.name}.")
        import_btn = page.get_by_role("button", name="Import", exact=True).last
        for _ in range(60):
            if import_btn.is_enabled():
                break
            page.wait_for_timeout(1000)
        else:
            self.fail("attach", f"The Import button stayed disabled after attaching {zip_path.name}.")
        self.settle()
        self.click(import_btn, "Import")
        try:
            page.get_by_text("Process submitted").first.wait_for(timeout=120000)
        except Exception:
            self.fail("import", "No 'Process submitted' message after Import.")
        self.open_history(task, area, "Import", offering)
        process = None
        for _ in range(12):
            new = [r.get("Name") for r in self.history_rows() if r.get("Name") not in known]
            if new:
                process = new[0]
                break
            self.page.wait_for_timeout(5000)
            self.click(self.page.get_by_role("button", name="Refresh").first, "Refresh")
            self.settle()
        if not process:
            self.fail("import", "The submitted import does not show in Import History.")
        self.log(f"import submitted: {process}")
        row = self.wait_process(task, area, "Import", process, offering)
        summary = self.summarize(row, process)
        if not self.complete(summary):
            self.fail("import", f"Import {process} did not complete cleanly: status "
                                f"'{summary['status']}', {summary['completed']}/{summary['total']} "
                                f"objects completed, {summary['successful']} successful. Row: {row}")
        self.log(f"import done: {summary['completed']}/{summary['total']} objects, all successful")
        return summary


if __name__ == "__main__":
    print(__doc__)
    sys.exit(0)
