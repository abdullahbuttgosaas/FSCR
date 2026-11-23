"""Setup and Maintenance steps for the Payment Terms folder on EITHER layout.

common/browser.py's navigation and export/import were rewritten for the Redwood
"Set Up" page (2026-10-20). Oracle is back on the classic "Setup: <offering>" page
(2026-10-21), so this folder carries its own classic steps (the proven pre-Redwood
ones) and picks the layout itself. Used only by this folder (isolation rules). Copied 2026-10-21 from the classic steps\nproven in the Business Units folder; this copy belongs to Payment Terms and is changed\nonly here.

    setup = Setup(ui)                      # detects the layout once, prints it
    path, summary = setup.export_csv(task, area, offering)
    summary = setup.import_csv(task, area, zip_path, offering)
    setup.open_task(task, area, offering)  # the task's own page
    setup.check_actions(task, area, offering)
"""
import re
import time
from pathlib import Path

from common import browser, oracle

EXPORT_CONFIRM = re.compile(r"has been initiated in the (.+?) process")
IMPORT_CONFIRM = re.compile(r"has been submitted to the (.+?) process")
RUNNING = ("Not started", "In progress", "Running", "Processing", "Queued", "Submitted")


class ImportNotClean(Exception):
    """Oracle finished the import process but not cleanly (errors, or not all objects). The
    caller reads the export afterwards to see which terms got in (2026-10-25). `summary` is
    the results page as read; `detail` the plain part of it."""

    def __init__(self, summary, detail, rows=None):
        super().__init__(detail)
        self.summary, self.detail = summary, detail
        self.rows = rows or {}        # {row identifier (the term name): [Oracle's messages]}


def log_errors(text):
    """The failed rows of an import's log file ("Download Log File" on the results page):
    {row identifier: [messages]}. Seen 2026-10-25: "Row Identifier: <term name>. Status: Error.
    ... Message Text: ... JBO-27040: Value ... for field Name exceeds the maximum length allowed."
    Only the sentences that say what is wrong are kept (not the "cannot be loaded" chain)."""
    rows = {}
    for block in text.split("Row Identifier: ")[1:]:
        ident = block.split(". Status:", 1)[0].strip()
        if "Status: Error" not in block.split("\n", 1)[0]:
            continue
        body = block.split("Message Text:", 1)[-1].split("\n\n\n", 1)[0]
        msgs = []
        for part in re.split(r"JBO-\d+:\s*", " ".join(body.split())):
            part = re.sub(r"(Failed to validate a row with key .*? in \S+|The data row that caused the "
                          r"exception exists in the \S+ file\.)\s*", "", part).strip(" .")
            if part and not re.search(r"cannot be loaded", part) and part not in msgs:
                msgs.append(part)
        rows.setdefault(ident, []).extend(m for m in msgs if m not in rows.get(ident, []))
    return rows


class Setup:
    def __init__(self, ui):
        self.ui = ui
        self.layout = None

    # ---- layout
    def detect(self):
        """Open Setup and Maintenance and tell the layout: "classic" or "Redwood"."""
        ui = self.ui
        page = ui.page
        page.goto(f"{oracle.HOST}{browser.SETUP_PATH}", wait_until="domcontentloaded", timeout=120000)
        ui.settle()
        ui.check_signed_in()
        for _ in range(60):
            if "/redwood/" in page.url and page.locator(ui.SWITCHER).count():
                layout = "Redwood"
                break
            if page.get_by_text(re.compile(r"^Setup: ")).count():
                layout = "classic"
                break
            page.wait_for_timeout(2000)
        else:
            ui.fail("layout", "Setup and Maintenance showed neither the classic nor the Redwood page.")
        if layout != self.layout:
            print(f"  Setup and Maintenance layout: {layout}")
        self.layout = layout
        return layout

    # ---- classic navigation
    def _offering(self, offering):
        ui, page = self.ui, self.ui.page
        self.detect()
        title = f"Setup: {offering}"
        heading = page.get_by_text(re.compile(r"^Setup: ")).first
        heading.wait_for(timeout=60000)
        if heading.inner_text().strip() == title:
            return
        ui.log(f"switching offering from '{heading.inner_text().strip()}' to '{offering}'")
        options = page.locator("li[role=option]:visible")
        option = options.filter(has_text=re.compile(rf"^{re.escape(offering)}$"))

        def pick(attempt):           # 2026-10-26: a lost click leaves the old offering (shared retry helper)
            if not option.count():
                ui.click(page.locator("a[aria-label='Offering']"), "Offering drop-down")
            try:
                option.first.wait_for(timeout=20000)
            except Exception:
                if options.count():  # the list opened without it: not a lost click
                    ui.fail("offering", f"Offering '{offering}' is not in the Offering list.")
                raise
            ui.click(option.first, f"offering {offering}")
            ui.settle()
        ui.retry(f"Setup page did not switch to the offering '{offering}'", pick,
                 lambda timeout: page.get_by_text(title, exact=True).first.wait_for(timeout=timeout),
                 wait=30000, last_wait=60000)

    def _task_row(self, task, area, offering):
        """Classic: Search Tasks > the result in `area`: the area opens with the task's
        row (long task lists render lazily, so Search Tasks is used, not scrolling).
        2026-10-26: Oracle's busy Setup page drops a search or a click made too early, so each step is checked
        and done again, up to 3 tries (shared retry helper ui.retry; replaces the one extra click of 2026-10-21)."""
        ui, page = self.ui, self.ui.page
        self._offering(offering)
        box = page.get_by_label("Search Tasks").first
        box.wait_for(timeout=60000)
        actions = page.locator(f'button[title="{task} : Actions"]')
        results = page.get_by_text("Search Task Results").first

        def search(attempt):
            box.fill(task)
            box.press("Enter")
            ui.settle()

        # With a single match Oracle skips the results window and opens the area with the
        # task selected (seen 2026-10-21 for Manage Data Access for Users); else it lists
        # task + area in "Search Task Results".
        def answered(timeout):
            end = time.time() + timeout / 1000
            while time.time() < end:
                if results.is_visible() or actions.count() and actions.first.is_visible():
                    return True
                page.wait_for_timeout(1000)
            return False
        ui.retry(f"Search Tasks did not show results for '{task}'", search, answered, wait=30000, last_wait=60000)
        if not results.is_visible() and actions.count() and actions.first.is_visible():
            return actions.first
        links = page.locator(f"a:text-is('{task}'):visible")
        try:
            links.first.wait_for(timeout=30000)
        except Exception:
            ui.fail("task", f"Task '{task}' not found by Search Tasks.")

        def result_link():
            for i in range(links.count()):
                row = links.nth(i).locator("xpath=ancestor::tr[1]").inner_text()
                if row.split("\t")[-1].strip() == area:
                    return links.nth(i)
            ui.fail("task", f"Task '{task}' is not listed under functional area '{area}'.")
        result_link()

        def pick(attempt):
            if results.is_visible():
                ui.click(result_link(), f"search result {task} ({area})" + (", again" if attempt > 1 else ""))
            ui.settle()
        ui.retry(f"Setup page did not show {task} in the '{area}' task list", pick,
                 lambda timeout: actions.first.wait_for(timeout=timeout), wait=20000, last_wait=60000)
        return actions.first

    def _menu(self, task, area, menu, entry, offering):
        """Classic: task row Actions > menu (Export to CSV File / Import from CSV File)
        > entry (Create New / View All). Each click checked (2026-10-26, shared retry helper); the entry has
        opened its page when the task row's Actions button has gone. Nothing here submits anything."""
        ui = self.ui
        actions = self._task_row(task, area, offering)
        ui.retry(f"Actions menu of {task} did not open",
                 lambda attempt: ui.visible(menu).count() or ui.click(actions, f"{task} Actions"),
                 lambda timeout: ui.visible(menu).wait_for(timeout=timeout), wait=10000, last_wait=20000)
        ui.retry(f"{menu} menu of {task} did not open",       # submenus open on click, not hover
                 lambda attempt: ui.visible(entry).count() or ui.click(ui.visible(menu), menu),
                 lambda timeout: ui.visible(entry).wait_for(timeout=timeout), wait=20000, last_wait=30000)

        def pick(attempt):
            if ui.visible(entry).count():
                ui.click(ui.visible(entry), f"{menu} > {entry}")
            ui.settle()
        ui.retry(f"Setup page did not open {menu} > {entry} of {task}", pick,
                 lambda timeout: actions.wait_for(state="hidden", timeout=timeout), wait=30000, last_wait=60000)

    # ---- classic process tracking
    def _confirm(self, pattern, what):
        ui, page = self.ui, self.ui.page
        msg = page.get_by_text(pattern)
        try:
            msg.first.wait_for(timeout=120000)
        except Exception:
            ui.fail(what, f"No confirmation after submitting the {what}.")
        process = pattern.search(msg.first.inner_text()).group(1)
        ui.click(ui.button(r"^O\s*K$"), "OK")
        ui.settle()
        return process

    def _wait(self, task, area, kind, process, offering):
        ui, page = self.ui, self.ui.page
        self._menu(task, area, kind, "View All", offering)
        start = time.time()
        while True:
            row = page.locator("tr").filter(has=page.locator(f"span:text-is('{process}')")).last
            try:
                row.wait_for(timeout=60000)
            except Exception:
                ui.fail("history", f"Process {process} is not listed in the {kind} history.")
            status = row.locator("a").last.inner_text().strip() if row.locator("a").count() else ""
            elapsed = int(time.time() - start)
            ui.log(f"{kind}: {process} status '{status or '?'}' ({elapsed}s)")
            if status and status not in RUNNING:
                return row
            if elapsed > ui.timeout:
                ui.fail("timeout", f"{process} still '{status}' after {elapsed}s.")
            page.wait_for_timeout(ui.poll * 1000)
            ui.click(ui.button(r"^Refresh$"), "Refresh")
            ui.settle()

    def _results(self, row, process):
        ui, page = self.ui, self.ui.page
        summary = page.get_by_text("Summary", exact=True).first

        def show(attempt):           # 2026-10-26: checked by the results page's Summary (shared retry helper)
            if attempt == 1 or not summary.is_visible():
                ui.click(row.locator("a").last, f"{process} status")
            ui.settle()
        ui.retry(f"history did not open the results of {process}", show,
                 lambda timeout: summary.wait_for(timeout=timeout), wait=30000, last_wait=60000)
        ui.settle()
        text = " ".join(page.inner_text("body").split())

        def grab(pattern):
            m = re.search(pattern, text)
            return m.group(1).strip() if m else None
        return {"status": grab(r"Summary Status (.+?) Stage"), "stage": grab(r" Stage (.+?) Task"),
                "total": grab(r"Total Objects (\d+)"), "completed": grab(r"Total Objects Completed (\d+)"),
                "errors": grab(r"Completed with Errors (\d+)"), "text": text, "process": process}

    @staticmethod
    def _complete(s, stage):
        return (s["status"] == "Completed successfully" and s["stage"] == stage and s["total"]
                and s["total"] == s["completed"] and s["errors"] == "0")

    def _done(self):
        btn = self.ui.page.get_by_role("button", name="Done")
        if btn.count():
            self.ui.click(btn.first, "Done")
            self.ui.settle()

    # ---- the public steps (either layout)
    def export_csv(self, task, area, offering):
        ui = self.ui
        if self.detect() == "Redwood":
            return ui.export_csv(task, area, offering)
        self._menu(task, area, "Export to CSV File", "Create New", offering)
        show = ui.page.locator("select:visible").first
        show.wait_for(timeout=60000)
        ui.choose(show, "All")
        ui.click(ui.button(r"^Subm"), "Submit")
        process = self._confirm(EXPORT_CONFIRM, "export")
        ui.log(f"export submitted: {process}")
        summary = self._results(self._wait(task, area, "Export to CSV File", process, offering), process)
        if not self._complete(summary, "Ready for download"):
            ui.fail("export", f"Export {process} did not complete: status '{summary['status']}', "
                              f"stage '{summary['stage']}', {summary['completed']}/{summary['total']} "
                              f"objects, {summary['errors']} with errors.")
        ui.work.mkdir(parents=True, exist_ok=True)
        with ui.page.expect_download(timeout=180000) as dl:
            ui.click(ui.button(r"^Download File$"), "Download File")
        path = ui.work / dl.value.suggested_filename
        dl.value.save_as(str(path))
        ui.log(f"downloaded {path.name} ({path.stat().st_size} bytes); "
               f"{summary['completed']}/{summary['total']} objects")
        self._done()
        return path, summary

    def import_csv(self, task, area, zip_path, offering):
        ui = self.ui
        if self.detect() == "Redwood":
            return ui.import_csv(task, area, zip_path, offering)
        zip_path = Path(zip_path)
        self._menu(task, area, "Import from CSV File", "Create New", offering)
        file_input = ui.page.locator("input[type=file]").first
        file_input.wait_for(state="attached", timeout=60000)
        file_input.set_input_files(str(zip_path))       # no native file picker
        try:
            ui.page.get_by_text(zip_path.name).first.wait_for(timeout=120000)
        except Exception:
            ui.fail("attach", f"Oracle did not accept the file {zip_path.name}.")
        ui.settle()
        ui.click(ui.button(r"^Subm"), "Submit")
        process = self._confirm(IMPORT_CONFIRM, "import")
        ui.log(f"import submitted: {process}")
        summary = self._results(self._wait(task, area, "Import from CSV File", process, offering), process)
        if not self._complete(summary, "Ready for data validation"):
            ui.evidence("import")
            detail = (f"Import {process} did not complete cleanly: status '{summary['status']}', stage "
                      f"'{summary['stage']}', {summary['completed']}/{summary['total']} objects, "
                      f"{summary['errors']} with errors.")
            ui.log(detail + f"\nPage text: {summary['text'][:3000]}")
            rows = {}
            try:                                   # the log names each failed row and why
                with ui.page.expect_download(timeout=120000) as dl:
                    ui.click(ui.page.get_by_text("Download Log File").first, "Download Log File")
                log_path = ui.work / f"import_log_{process}.log".replace(" ", "_")
                dl.value.save_as(str(log_path))
                rows = log_errors(log_path.read_text(encoding="utf-8", errors="replace"))
                ui.log(f"import log saved: {log_path.name}; failed rows: {rows}")
            except Exception as e:  # noqa: BLE001 - the log is extra detail; the export decides
                ui.log(f"the import log couldn't be downloaded ({type(e).__name__}: {e})")
            self._done()
            raise ImportNotClean(summary, detail, rows)
        ui.log(f"import done: {summary['completed']}/{summary['total']} objects, 0 errors")
        self._done()
        return summary

    def open_task(self, task, area, offering):
        ui = self.ui
        if self.detect() == "Redwood":
            return ui.open_task(task, area, offering)
        actions = self._task_row(task, area, offering)
        start = ui.page

        def act(attempt):            # 2026-10-26: the task link clicked again when the click was lost
            link = start.locator(f"a:text-is('{task}'):visible").first
            if attempt == 1 or ui.page is start and link.count():
                ui.click(link, f"task {task}" + (" (again)" if attempt > 1 else ""))
            ui.settle()
            ui.use_newest_page()

        def opened(timeout):         # a new tab, or the task list (its Actions button) has gone
            if ui.page is not start:
                return True
            actions.wait_for(state="hidden", timeout=timeout)
        ui.retry(f"Setup page did not open {task}", act, opened, wait=30000, last_wait=60000)

    def check_actions(self, task, area, offering):
        """Read-only: open Export > Create New and Import > Create New, confirm their
        fields and Submit, leave each with Cancel. Nothing is submitted."""
        ui = self.ui
        if self.detect() == "Redwood":
            return ui.check_actions(task, area, offering)
        page = ui.page
        for menu, need in (("Export to CSV File", page.get_by_label("Process Name")),
                           ("Import from CSV File", page.locator("input[type=file]"))):
            self._menu(task, area, menu, "Create New", offering)
            try:
                need.first.wait_for(state="attached", timeout=60000)
                ui.button(r"^Subm").wait_for(timeout=30000)
            except Exception:
                ui.fail("check", f"{menu} > Create New did not show its fields and Submit button.")
            ui.log(f"{menu} > Create New opens with its fields and Submit; leaving with Cancel")
            back = page.get_by_text(re.compile(r"^Setup: ")).first

            def cancel(attempt, menu=menu):     # Cancel submits nothing; checked (2026-10-26)
                if attempt == 1 or not back.is_visible():
                    ui.click(page.get_by_role("button", name=re.compile(r"^Cancel$")).first, f"{menu} Cancel")
                ui.settle()
            ui.retry(f"Cancel on {menu} did not return to Setup and Maintenance", cancel,
                     lambda timeout: back.wait_for(timeout=timeout), wait=30000, last_wait=60000)
