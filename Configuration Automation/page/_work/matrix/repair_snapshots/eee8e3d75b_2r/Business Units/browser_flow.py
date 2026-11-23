"""Create business units and give a login Business unit data access, through the Oracle UI.

Two steps, both by CSV export/import (Setup and Maintenance > offering Order
Management, Redwood "Set Up" page, task Actions > Export / Import), driven by
common/browser.py. No REST. Uses the sign-in saved by common/login_once.py.

  1. Manage Business Unit (area Organization Structures, task code
     FUN_MANAGE_BUSINESS_UNIT): one new FUN_BUSINESS_UNIT row (name, location
     code, default set code). The import zip holds ONLY that row; every other
     file is header-only, so no existing business unit is in the file at all.
  2. Manage Data Access for Users (area Users and Security, task code
     ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS): one new ORA_FUN_ALL_USER_DATA_ACCESS
     row (user, role code, the new BU, security context Business unit). The import
     zip holds ONLY that row, so no other user's access, role or BU is in the file.

Normal run (fast, 2026-10-23; see CLAUDE.md "Fast first-time runs"): the lists are
checked through REST (at the same time), the import file is built from the saved template
(bu_import_template.json, no before-export), the import is submitted and the new business
unit is polled by a quick REST read every 3 s, and step 2 is REST (filtered read-back).
The screen checks - a second export (new row exactly as built, every other row
unchanged), the Manage Business Units screen, Users with Data Access and the Create Order
Business Unit list (fresh app session; Cancel > Yes, nothing saved) - run only with
"Check on screen too" (--screen-check) or --check. Without REST the old screen route runs.
Every step stops with a plain message after 6 minutes.

Temporary files go in "Business Units/_work/": deleted after a verified success,
kept after any failure (with screenshots).

  python "Business Units/browser_flow.py" --check     # read-only: screens, lists, exports
  python "Business Units/browser_flow.py"             # full run (headless)
  python "Business Units/browser_flow.py" --headed    # same, browser visible

Page interface (root CLAUDE.md > Page interface, common/page.py), one business unit per run:
  python "Business Units/browser_flow.py" --spec
  python "Business Units/browser_flow.py" --options location | default_set | user | role
  python "Business Units/browser_flow.py" --run '{"name": "X"}'
"""
import argparse
import collections
import csv
import io
import json
import os
import re
import subprocess
import sys
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import browser, oracle, page  # noqa: E402
from classic_setup import Setup  # noqa: E402  (this folder's own layout-aware steps)

OFFERING = "Order Management"
BU_AREA, BU_TASK = "Organization Structures", "Manage Business Unit"
DA_AREA, DA_TASK = "Users and Security", "Manage Data Access for Users"
BU_CSV, DA_CSV = "FUN_BUSINESS_UNIT.csv", "ORA_FUN_ALL_USER_DATA_ACCESS.csv"
BU_OBJECT = "FUN_ALL_BUSINESS_UNITS_V"           # data access object for "Business unit"
SECURITY_CONTEXT = "Business unit"
WHO = ("CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin")
IGNORE = WHO + ("SysEffectiveDate",)            # changes by itself between exports
REQUIRED = ("name",)
# Defaults (the user's standing choice): unless a request names something else, the BU
# goes to this location and default set.
DEFAULTS = {"location": "Go Saas Lahore Office", "default_set": "001 CUSTOMER SITE"}
# Always given on every business unit, first, and never replaced or skipped by anything
# in the request (2026-10-21): this user (or its fallback) gets both roles on it.
REQUIRED_USER = {"user": "Configuration.TEST", "user_fallback": "Configuration"}
REQUIRED_ROLES = ("Order Manager", "Pricing Administrator")
# Optional, in addition: one more access row per role named here, for "user" (empty: the
# required user), added last, after everything required is verified. A failure there
# never undoes or blocks the required steps (the result is then a partial success).
EXTRA_KEYS = ("user", "role", "pricing_role")
KNOWN = set(REQUIRED) | set(DEFAULTS) | set(EXTRA_KEYS) | {"active", "screen_check", "manager"}
# "location": "none" (or null) = no location, as on the Create Business Unit screen (2026-10-26)
NO_LOCATION = ("none", "(none)", "no location")
# Columns a new business unit gets from the Create Business Unit form (learned from BUs
# made in the UI, e.g. "ui" and "abcde" on 2026-10-20). Everything else stays empty.
BU_FIXED = {"Classification": "FUN_BUSINESS_UNIT", "ClassificationCode": "FUN_BUSINESS_UNIT",
            "OrgInformationContext": "FUN_BUSINESS_UNIT", "EffectiveStartDate": "0001/01/01",
            "EffectiveEndDate": "4712/12/31", "ProfitCenterFlag": "N"}
DA_FIXED = {"ActiveFlag": "Y", "RecordTypeCode": "USER_DEFINED", "ObjectName": BU_OBJECT}
ROWS_JS = r"""(part) => [...document.querySelectorAll('tr[_afrrk]')]
  .filter(r => r.offsetWidth && (!part || (r.closest('[id$="::db"]') || {id: ''}).id.includes(part)))
  .map(r => [...r.querySelectorAll('td')].filter(td => !td.querySelector('td'))
     .map(td => td.innerText.trim()).filter(Boolean))"""

# Speed and limits (2026-10-23, see CLAUDE.md > Known gotchas "Fast first-time runs").
STEP_LIMIT = 360          # seconds: a step stops with a plain message after 6 minutes
SLOW_AFTER = 90           # seconds: then "Oracle is responding slowly right now"
TICK = 10                 # seconds between the timer lines of a step
POLL_EVERY = 3            # seconds between quick reads for the new business unit
# Oracle caches the Create Order Business Unit list in the app session cookie of the saved
# sign-in: dropped in memory for the Create Order check (never in the saved file).
APP_COOKIE = {"name": "JSESSIONID", "path": "/fscmUI"}
TEMPLATE = Path(__file__).resolve().parent / "bu_import_template.json"


# ---------------------------------------------------------------- steps: timer and limit

class StepTimeout(Exception):
    """A step ran over STEP_LIMIT. .what: the step in plain words; .state: what is and isn't
    done in Oracle at that point, in plain words."""

    def __init__(self, what, state):
        super().__init__(f"Timeout: '{what}' took longer than {STEP_LIMIT // 60} minutes")
        self.what, self.state = what, state


PROGRESS_LOCK = threading.Lock()


def elapsed_text(seconds):
    s = int(seconds)
    return f"{s // 60} min {s % 60:02d} s" if s >= 60 else f"{s} s"


class Phase:
    """One step of a run: plain sub-steps with a running timer (a progress line every 10 s),
    "Oracle is responding slowly right now" after 90 s, and the 6-minute limit, checked
    between sub-steps and in every wait loop (check()). state: plain words for the result if
    it stops here; set it as the step goes on. Without progress (command line) it prints."""

    def __init__(self, progress, key, percent, text, state="Nothing was changed in Oracle in this step."):
        self.progress, self.key, self.percent, self.text, self.state = progress, key, percent, text, state
        self.sub_text, self.t0, self._stop = "", time.time(), threading.Event()

    def emit(self):
        el = time.time() - self.t0
        line = self.text + (f": {self.sub_text}" if self.sub_text else "") + f" ({elapsed_text(el)})"
        if el >= SLOW_AFTER:
            line += " - Oracle is responding slowly right now"
        if self.progress:
            with PROGRESS_LOCK:
                self.progress.step(self.key, self.percent, line)

    def sub(self, text):
        self.check()
        self.sub_text = text
        print(f"  ... {self.text}: {text} ({elapsed_text(time.time() - self.t0)})", flush=True)
        self.emit()

    def check(self):
        if time.time() - self.t0 > STEP_LIMIT:
            raise StepTimeout(self.text, self.state)

    def __enter__(self):
        self.t0 = time.time()
        self.emit()

        def tick():
            while not self._stop.wait(TICK):
                self.emit()
        self._thread = threading.Thread(target=tick, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join()
        print(f"  step '{self.text}': {elapsed_text(time.time() - self.t0)}", flush=True)
        return False


# ---------------------------------------------------------------- the browser, only when needed

class LazyUI:
    """The browser opens on first use (a business unit to create, a screen check, a
    fallback); a run that only adds access rows never opens it. Attributes go to the real
    OracleUI (with its .setup); close() at the end."""

    def __init__(self, work, headless):
        object.__setattr__(self, "_args", (work, headless))
        object.__setattr__(self, "_ui", None)

    def _open(self):
        if self._ui is None:
            ui = browser.OracleUI(self._args[0], headless=self._args[1]).__enter__()
            ui.setup = Setup(ui)
            object.__setattr__(self, "_ui", ui)
        return self._ui

    def __getattr__(self, name):
        return getattr(self._open(), name)

    def __setattr__(self, name, value):
        setattr(self._open(), name, value)

    def close(self):
        if self._ui is not None:
            self._ui.__exit__(None, None, None)


# ---------------------------------------------------------------- import file from a saved template

def save_template(files):
    """The header line of every file of a business unit export (no data rows) and its
    metadata file, so a later run builds its import file without exporting first."""
    data = {"about": "Header lines of the Manage Business Unit export (no data rows), saved by "
                     "browser_flow.py; used to build the import file without a before-export.",
            "files": {n: ({"head_line": f["head_line"]} if "header" in f else
                          {"text": f["raw"].decode("utf-8")}) for n, f in sorted(files.items())}}
    try:
        old = json.loads(TEMPLATE.read_text(encoding="utf-8")).get("files")
    except (OSError, ValueError):
        old = None
    if old != data["files"]:
        TEMPLATE.write_text(json.dumps(data, indent=1), encoding="utf-8")
        print(f"  saved the import template ({TEMPLATE.name}, {len(files)} files, headers only)")


def load_template():
    try:
        data = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    files = {}
    for n, f in data.get("files", {}).items():
        if "head_line" in f:
            files[n] = {"head_line": f["head_line"], "header": next(csv.reader([f["head_line"]])), "rows": []}
        else:
            files[n] = {"raw": f["text"].encode("utf-8")}
    return files if BU_CSV in files else None


# ---------------------------------------------------------------- requirements

def load_requirements(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        oracle.fail(f"Cannot read {path}: {e}")
    return parse_requirements(data, path)


def parse_requirements(data, path):
    """The request (file contents or a page request) -> business units with defaults."""
    raw = data.get("business_units")
    if not isinstance(raw, list) or not raw:
        oracle.fail(f"{path} must contain a non-empty 'business_units' list")
    out, names = [], set()
    for b in raw:
        where = f"business unit {b.get('name')!r}"
        unknown = set(b) - KNOWN
        if unknown:
            oracle.fail(f"{where}: unknown field(s) {sorted(unknown)}; allowed: {sorted(KNOWN)}")
        missing = [k for k in REQUIRED if not b.get(k)]
        if missing:
            oracle.fail(f"{where}: missing required value(s): {', '.join(missing)}. Ask the user "
                        "for them in one plain message.")
        b = dict(b)
        no_loc = "location" in b and (b["location"] is None or str(b["location"]).strip().lower() in NO_LOCATION)
        for k, v in DEFAULTS.items():
            if k == "location" and no_loc:
                b[k] = None
                continue
            if b.get(k) in (None, ""):
                b[k] = v
                print(f"  {b['name']}: {k} not given; default {v!r}")
        for k in REQUIRED + tuple(DEFAULTS) + EXTRA_KEYS:
            v = b.get(k)
            if v is not None and (not isinstance(v, str) or v != v.strip()):
                oracle.fail(f"{where}: '{k}' must be text without outer spaces")
        # extra access (optional): one row per role named, for the named user or the required one
        roles = [r for r in (b.get("role"), b.get("pricing_role")) if r]
        if b.get("user") and not roles:
            oracle.fail(f"{where}: an extra user needs a role for the extra access (role or pricing_role)")
        b["extra"] = [{"user": b.get("user") or None, "role": r} for r in dict.fromkeys(roles)]
        if b.get("manager"):
            import bu_batch                  # the allowed managers (2026-10-26)
            m = bu_batch.find_manager(b["manager"]) if isinstance(b["manager"], str) else None
            if m is None:
                oracle.fail(f"{where}: '{b['manager']}' can't be the manager: only "
                            + " or ".join(x["name"] for x in bu_batch.MANAGERS) + " can be chosen.")
            b["manager_entry"] = m
        if len(b["name"]) > 240:
            oracle.fail(f"{where}: name is longer than 240 characters")
        if not isinstance(b.get("active", True), bool):
            oracle.fail(f"{where}: 'active' must be true or false")
        if not isinstance(b.get("screen_check", False), bool):
            oracle.fail(f"{where}: 'screen_check' must be true or false")
        b["screen_check"] = b.get("screen_check", False)
        if b["name"].lower() in names:
            oracle.fail(f"{where}: listed twice")
        names.add(b["name"].lower())
        out.append(dict(b, active=b.get("active", True)))
    return out


# ---------------------------------------------------------------- files

def read_zip(path):
    z = zipfile.ZipFile(path)
    files = {}
    for n in z.namelist():
        raw = z.read(n)
        if n.endswith(".csv"):
            text = raw.decode("utf-8-sig")
            rows = list(csv.reader(io.StringIO(text)))
            files[n] = {"raw": raw, "header": rows[0], "rows": rows[1:],
                        "head_line": text.splitlines()[0]}
        else:
            files[n] = {"raw": raw}
    return files


def dicts(f):
    return [dict(zip(f["header"], r)) for r in f["rows"]]


def need(files, name, task):
    if name not in files:
        oracle.fail(f"The {task} export has no {name}; files: {sorted(files)}")
    return files[name]


def csv_line(header, row):
    buf = io.StringIO()
    csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n").writerow([row.get(c, "") for c in header])
    return buf.getvalue()


def build_only_new(files, target, new_rows, path):
    """Every file of the export once; every CSV header-only except `target`, which holds
    only the new rows. Nothing that already exists is in the import at all."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zo:
        for name, f in files.items():
            if "header" not in f:
                zo.writestr(name, f["raw"])          # ASM_SETUP_CSV_METADATA.xml unchanged
                continue
            body = f["head_line"] + "\n"
            if name == target:
                body += "".join(csv_line(f["header"], r) for r in new_rows)
            zo.writestr(name, body.encode("utf-8"))
    return path


def oracle_today(bu_files):
    """Oracle's today = the SysEffectiveDate Oracle writes into the business unit export
    (set-assignment and service-provider rows), never the PC clock."""
    seen = collections.Counter()
    for f in bu_files.values():
        if "header" in f and "SysEffectiveDate" in f["header"]:
            seen.update(r["SysEffectiveDate"] for r in dicts(f) if r.get("SysEffectiveDate"))
    if not seen:
        oracle.fail("The business unit export shows no SysEffectiveDate to read Oracle's today from.")
    day = seen.most_common(1)[0][0]                    # YYYY/MM/DD
    print(f"  Oracle's today (SysEffectiveDate in the export): {day}")
    return day


def compare_existing(before, after, name_col, new_names, files_label):
    """Rows of every CSV that existed before must be unchanged after (who columns and
    SysEffectiveDate ignored). Rows of the new records are left out."""
    ok = True
    for fname, f in before.items():
        if "header" not in f:
            continue
        if fname not in after:
            print(f"  FAIL  {files_label}: {fname} missing from the after-export")
            ok = False
            continue
        hdr = f["header"]
        keep = [i for i, c in enumerate(hdr) if c not in IGNORE]
        col = next((c for c in name_col if c in hdr), None)
        idx = hdr.index(col) if col else None
        strip = lambda rows: collections.Counter(
            tuple(r[i] for i in keep) for r in rows if idx is None or r[idx] not in new_names)
        a_hdr = after[fname]["header"]
        a_rows = [[dict(zip(a_hdr, r)).get(c, "") for c in hdr] for r in after[fname]["rows"]]
        b, a = strip(f["rows"]), strip(a_rows)
        if b == a:
            print(f"  OK    existing rows unchanged in {fname} ({sum(b.values())})")
        else:
            print(f"  FAIL  {fname}: existing rows changed ({sum((b - a).values())} gone/changed, "
                  f"{sum((a - b).values())} new/changed)")
            ok = False
    return ok


# ---------------------------------------------------------------- screen: Manage Business Unit

def open_bu_form(ui):
    with ui.step("open Create Business Unit"):
        ui.setup.open_task(BU_TASK, BU_AREA, OFFERING)
        page = ui.page
        page.get_by_text("Search Results").first.wait_for(timeout=60000)
        icon = page.locator("img[id$='AT1:_ATp:create::icon']").first
        icon.wait_for(timeout=60000)
        ui.settle()
        heading = page.locator("h1:visible").filter(has_text=re.compile(r"^\s*Create Business Unit"))

        def plus(attempt):
            # the + only reacts to a real mouse click, and a click made while the page is
            # still settling is lost (seen 2026-10-20), so click again until the form opens
            if heading.count():
                return
            box = icon.bounding_box()
            if box is None:             # the + is being redrawn: try again (2026-10-26)
                raise RuntimeError("the + has no position yet")
            page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        ui.retry("+ on Manage Business Units did not open Create Business Unit", plus,
                 lambda timeout: heading.first.wait_for(timeout=timeout), pause=2.0, wait=20000, last_wait=40000)
        ui.settle()


def leave_bu_form(ui):
    form = ui.page.locator("h1:visible").filter(has_text=re.compile(r"^\s*Create Business Unit")).first

    def cancel(attempt):             # Cancel saves nothing; checked that the form closed (2026-10-26)
        if attempt == 1 or form.count():
            ui.click(ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).first, "Cancel")
        ui.settle()
    ui.retry("Create Business Unit form did not close after Cancel", cancel,
             lambda timeout: form.wait_for(state="hidden", timeout=timeout), wait=15000, last_wait=30000)


def location_dialog(ui):
    page = ui.page
    return ui.search_dialog(lambda: ui.click(page.locator("[id$='locationCodeId::lovIconId']").first, "Location list"),
                            page.locator("a:text-is('Search...'):visible").last, "Location")


def location_search(ui, dlg, name="", code=""):
    dlg.get_by_label("Name", exact=True).first.fill(name)
    dlg.get_by_label("Code", exact=True).first.fill(code)
    # 2026-10-26: a lost Search left the previous rows, read as this search's answer: only a fresh answer counts
    return ui.fresh_search(lambda: ui.click(dlg.get_by_role("button", name="Search", exact=True), "Location Search"),
                           lambda: [c for r in ui.lov_rows(dlg) for c in r if "\t" not in c], "Location search")


def resolve_location(ui, wanted, bu_rows):
    """Location name (as the user gives it) -> location code for the import.
    The dialog shows names only and searches by Name or Code, so: the name must exist
    exactly; its code is found by asking the dialog for the name of each location code
    that existing business units use."""
    dlg = location_dialog(ui)
    names = location_search(ui, dlg, name=wanted)
    hit = ui.match_value(wanted, names)
    if hit is None:
        similar = sorted(set(location_search(ui, dlg, name=wanted[:3] + "%")))
        ui.close_dialog(dlg, "Location dialog")
        oracle.fail(f"Location {wanted!r} is not one of the screen's locations. Ask the user to "
                    f"pick one; locations starting like it: {', '.join(similar) or '(none)'}")
    codes = sorted({r["InternalLocationCode"] for r in bu_rows if r["InternalLocationCode"]})
    found = None
    for code in codes:
        if ui.match_value(hit, location_search(ui, dlg, code=code)) is not None:
            found = code
            break
    ui.close_dialog(dlg, "Location dialog")
    if not found:
        oracle.fail(f"Location {hit!r} exists, but no existing business unit uses it, so its "
                    "location code cannot be read from the screen. Ask the user for the code.")
    loc_set = collections.Counter(r["LocationSetCode"] for r in bu_rows
                                  if r["InternalLocationCode"] == found).most_common(1)[0][0]
    print(f"  location {hit!r} = code {found} (location set {loc_set or '-'})")
    return hit, found, loc_set


def resolve_default_set(ui, wanted):
    rows = ui.lov_search_all(ui.page.locator("[id$='defaultSetCodeId::lovIconId']").first, "Default Set")
    sets = [[c for c in r if "\t" not in c] for r in rows]
    sets = [(r[0], r[1] if len(r) > 1 else "") for r in sets if r]
    code = ui.match_value(wanted, [s[0] for s in sets])
    if code is None:
        name = ui.match_value(wanted, [s[1] for s in sets])
        code = next((s[0] for s in sets if s[1] == name), None) if name else None
    if code is None:
        listing = "; ".join(f"{n} ({c})" for c, n in sets)
        oracle.fail(f"Default set {wanted!r} is not one of the screen's sets. Ask the user to pick "
                    f"one (name and code): {listing}")
    name = next(n for c, n in sets if c == code)
    print(f"  default set {wanted!r} = code {code} ({name})")
    return code, name


def screen_bu(ui, name):
    """Manage Business Units: search by name, return the row (Name, Active, Location, Manager)."""
    page = ui.page
    ui.setup.open_task(BU_TASK, BU_AREA, OFFERING)
    page.get_by_text("Search Results").first.wait_for(timeout=60000)
    box = page.locator("input[id$='q1:value00::content']").first
    box.fill(name)
    # 2026-10-26: only a fresh answer to this Search counts (a lost Search kept the old rows)
    shown = ui.fresh_search(lambda: ui.click(page.locator("button[id$='q1::search']").first, "Search"),
                            lambda: page.evaluate(ROWS_JS, ""), "Manage Business Units search")
    rows = [r for r in shown if r and r[0] == name]
    active = page.locator("tr[_afrrk]").filter(has=page.locator(f"a:text-is('{name}')")) \
        .locator("[title*='ctive'], img").count() > 0
    return rows, active


# ---------------------------------------------------------------- screen: Manage Data Access for Users

def open_data_access(ui):
    with ui.step("open Manage Data Access for Users"):
        ui.setup.open_task(DA_TASK, DA_AREA, OFFERING)
        ui.wait_heading(DA_TASK)
        page = ui.page

        def tab(attempt):
            ui.click(page.get_by_text("Users with Data Access", exact=True).first, "Users with Data Access")
            ui.settle()
            page.wait_for_timeout(2000)
        ui.retry("Manage Data Access for Users did not show its Users with Data Access search", tab,
                 lambda timeout: ui.field("Security Context").wait_for(timeout=timeout), wait=20000, last_wait=40000)
        ui.choose(ui.field("Security Context"), SECURITY_CONTEXT)


def access_rows(ui, user, role_name=""):
    """Users with Data Access, Security Context Business unit: rows [user, role, context, BU]."""
    page = ui.page
    f = ui.field("User Name")
    ok, _ = ui.lov_type(f, user, "User Name")
    if not ok:
        return None
    if role_name:
        ok, _ = ui.lov_type(ui.field("Role"), role_name, "Role")
        if not ok:
            oracle.fail(f"Role {role_name!r} is not accepted by the Role field.")
    else:
        ui.field("Role").fill("")
    # 2026-10-26: only a fresh answer to this Search counts (a lost Search kept the old rows)
    shown = ui.fresh_search(lambda: ui.click(page.get_by_role("button", name="Search", exact=True).first, "Search"),
                            lambda: page.evaluate(ROWS_JS, ""), "Users with Data Access search")
    return [r for r in shown if len(r) >= 3 and r[0] == user]


def check_role_name(ui, wanted):
    """The role must be in the Role list exactly (names only on screen)."""
    page = ui.page
    # the search form's ids differ between "Users with" and "without Data Access":
    # find the list icon next to the visible Role field
    role_id = ui.field("Role").get_attribute("id")
    icon_id = role_id.replace("::content", "::lovIconId")
    dlg = ui.search_dialog(lambda: ui.click(page.locator(f"[id='{icon_id}']").first, "Role list"),
                           page.locator("a:text-is('Search...'):visible").last, "Role")
    search = lambda: ui.click(dlg.get_by_role("button", name="Search", exact=True), "Role Search")  # noqa: E731
    read = lambda: [c for r in ui.lov_rows(dlg) for c in r if "\t" not in c]                       # noqa: E731
    dlg.locator("input[type=text]:visible").first.fill(wanted)
    names = ui.fresh_search(search, read, "Role search")      # 2026-10-26: only a fresh answer counts
    hit = ui.match_value(wanted, names)
    if hit is None:
        dlg.locator("input[type=text]:visible").first.fill(wanted.split()[0] + "%")
        similar = sorted(set(ui.fresh_search(search, read, "Role search")))[:40]
        ui.close_dialog(dlg, "Role dialog")
        oracle.fail(f"Role {wanted!r} is not in the screen's Role list. Ask the user to pick one; "
                    f"roles starting like it: {', '.join(similar) or '(none)'}")
    ui.close_dialog(dlg, "Role dialog")
    return hit


def role_code(ui, users, role_name, da_rows):
    """Role name (screen) -> role code (import file). The screen shows names, the export
    shows codes; both list the same user's Business unit access rows, so the code is the
    one whose BUs in the export are exactly the BUs the screen shows for that role."""
    for user in users:
        rows = access_rows(ui, user, role_name)
        if rows is None:
            continue
        bus = {r[3] for r in rows if len(r) > 3 and r[1] == role_name}
        if not bus:
            continue
        by_code = collections.defaultdict(set)
        for r in da_rows:
            if r["UserName"] == user and r["ObjectName"] == BU_OBJECT and r["BuName"]:
                by_code[r["RoleName"]].add(r["BuName"])
        hits = [c for c, s in by_code.items() if bus <= s]       # codes covering every screen BU
        same = [c for c in hits if by_code[c] == bus]
        pick = same if len(same) == 1 else hits
        if len(pick) == 1:
            print(f"  role {role_name!r} = code {pick[0]} (matched on {user}'s BUs {sorted(bus)})")
            return pick[0]
    oracle.fail(f"Could not tell the code of role {role_name!r}: none of {users} has Business unit "
                "access with that role yet, so the screen and the export cannot be matched. Ask the "
                "user for the role code.")


def pick_user(ui, b, da_rows):
    """The request's user, or its fallback, as Oracle knows it (export rows or the screen)."""
    known = {r["UserName"] for r in da_rows}
    for user in [b["user"]] + ([b["user_fallback"]] if b.get("user_fallback") else []):
        if user in known or access_rows(ui, user) is not None:
            if user != b["user"]:
                print(f"  NOTE  user {b['user']!r} not found; using the fallback {user!r}")
            return user
    oracle.fail(f"User {b['user']!r} (fallback {b.get('user_fallback')!r}) is not known to Manage "
                "Data Access for Users. Ask the user for the exact user name.")


# ---------------------------------------------------------------- screen: Create Order (read-only)

def create_order_business_units(ui):
    """Business Unit drop-down of Create Order (Order Management work area). Read-only:
    the page is left with Cancel > Yes, nothing is saved."""
    page = ui.page
    with ui.step("open Create Order"):
        page.goto(browser.start_url(), wait_until="domcontentloaded", timeout=120000)
        ui.settle()
        ui.check_signed_in()
        page.locator("a[title='Navigator']:visible").first.wait_for(timeout=60000)
        node = "pt1:_UISnvr:0:nv_itemNode_order_management_order_management"
        # The Navigator fills its links a few seconds after opening; 3 s was not always
        # enough (2026-10-21), so wait up to 45 s and reopen it (shared retry helper since 2026-10-26).
        def navigator(attempt):
            if attempt > 1:
                page.keyboard.press("Escape")
            ui.click(page.locator("a[title='Navigator']:visible").first, "Navigator")

        def has_node(timeout):
            end = time.time() + timeout / 1000
            while time.time() < end:
                if page.evaluate(f"() => !!document.getElementById('{node}')"):
                    return True
                page.wait_for_timeout(1000)
            return False
        ui.retry("Navigator did not show Order Management > Order Management", navigator, has_node,
                 wait=45000, last_wait=45000)
        link = page.locator("a:visible").filter(has_text=re.compile(r"^\s*Create Order\s*$")).first

        def order_area(attempt):
            if attempt == 1 or not link.count():
                page.evaluate(f"() => {{ const n = document.getElementById('{node}'); if (n) n.click(); }}")
                page.wait_for_load_state("domcontentloaded")
            ui.settle()
        if not link.count():
            ui.retry("Order Management work area did not open", order_area,
                     lambda timeout: link.wait_for(timeout=timeout), wait=60000, last_wait=90000)

        def create(attempt):
            if attempt == 1 or link.count() and link.is_visible():
                ui.click(link, "Create Order" + (" (again)" if attempt > 1 else ""))
            ui.settle()
        ui.retry("Order Management did not open Create Order", create,
                 lambda timeout: ui.wait_heading("Create Order", timeout=timeout), wait=60000, last_wait=90000)
    with ui.step("read the Create Order Business Unit list"):
        sel = page.locator("select[id$='AP1:soc3::content']").first
        if not sel.count():
            sel = ui.field("Business Unit")
        sel.wait_for(timeout=60000)
        got = {"options": []}

        def listed(timeout):         # 2026-10-26: the list fills after the page; an empty read is read again
            end = time.time() + timeout / 1000
            while True:
                got["options"] = [o for o in ui.select_options(sel) if o]
                if got["options"] or time.time() > end:
                    return bool(got["options"])
                page.wait_for_timeout(1000)
        ui.retry("Create Order Business Unit list stayed empty", lambda attempt: None, listed,
                 wait=10000, last_wait=20000, soft=True)
        options = got["options"]
    with ui.step("leave Create Order without saving"):
        form = page.locator("h1:visible").filter(has_text=re.compile(r"^\s*Create Order")).first
        yes = page.get_by_role("button", name=re.compile(r"^Y\s*es$"))

        def leave(attempt):          # Cancel and Yes save nothing; checked that the order closed (2026-10-26)
            if not (yes.count() and yes.first.is_visible()):
                ui.click(page.get_by_role("button", name="Cancel", exact=True).first, "Cancel")
            try:
                yes.first.wait_for(timeout=15000)
                ui.click(yes.first, "Yes (leave without saving)")
            except Exception:
                pass
            ui.settle()
        ui.retry("Create Order did not close without saving", leave,
                 lambda timeout: form.wait_for(state="hidden", timeout=timeout), wait=20000, last_wait=40000)
    return options


# ---------------------------------------------------------------- main

def show_existing(row):
    keys = ("Name", "DefaultSetCode", "InternalLocationCode", "LocationSetCode", "Status",
            "LegalEntityName", "PrimaryLedgerName", "ManagerListName", "CreatedBy", "CreationDate")
    return ", ".join(f"{k} {row.get(k)!r}" for k in keys if row.get(k))


# ---------------------------------------------------------------- REST (lists, existence, step 2)

HCM_BASE = oracle.HOST + "/hcmRestApi/resources/11.13.18.05"   # found by describe 2026-10-21
match_value = browser.OracleUI.match_value


class RestUnavailable(Exception):
    """A REST call failed or was refused; the run uses the screen / export route instead."""


def rget(url, what, **params):
    params.setdefault("onlyData", "true")
    r, err = oracle.try_call("GET", url, params=params, timeout=180)
    if err and r is None:
        # a network blip (the Oracle host name didn't resolve for a moment, 2026-10-26): a read
        # only, so it is simply asked once more after a short wait
        time.sleep(8)
        r, err = oracle.try_call("GET", url, params=params, timeout=180)
    if err:
        raise RestUnavailable(f"{what}: {err}")
    return r.json()


def rest_all(url, what, **params):
    items, offset = [], 0
    while True:
        # 200 per page: the userRoleDetails list returned nothing at limit=500 (2026-10-21)
        data = rget(url, what, limit=200, offset=offset, **params)
        items += data.get("items", [])
        if not data.get("hasMore"):
            return items
        offset += len(data.get("items", []))


def ds_lov(name, user=None):
    """A list link of dataSecurities (userNames, userRoleDetails, ...) taken from an item
    Oracle returns, never built by hand. The role list belongs to the row it is read
    from (another user's row gave 0 roles, 2026-10-21), so for roles pass the user: the
    link is then taken from one of that user's own rows."""
    params = {"limit": 1}
    if user:
        params["finder"] = f"ManageDataAccessRF;Userrf={user}"
    r, err = oracle.try_call("GET", f"{oracle.API_BASE}/dataSecurities", params=params, timeout=180)
    if err or not r.json().get("items"):
        raise RestUnavailable(f"dataSecurities: {err or 'no item to read its lists from'}")
    href = oracle.link_href(r.json()["items"][0], name)
    if not href:
        raise RestUnavailable(f"dataSecurities has no {name} list")
    return href


def rest_bu(name):
    items = rget(f"{oracle.API_BASE}/finBusinessUnitsLOV", "business unit search",
                 finder=f"KeywordFinder;SearchTerm={name}").get("items", [])
    return [i for i in items if i.get("BusinessUnitName", "").lower() == name.lower()]


def rest_location(wanted, bu_rows):
    """Location name -> (name, code, location set code, LocationId) from HCM locations."""
    locs = rest_all(f"{HCM_BASE}/locations", "locations",
                    fields="LocationId,LocationCode,LocationName,SetId,ActiveStatus")
    names = [l["LocationName"] for l in locs]
    hit = match_value(wanted, names)
    if hit is None:
        oracle.fail(f"Location {wanted!r} does not exist in Oracle (a location cannot be created "
                    f"here). Ask the user to pick one of these {len(names)} locations: "
                    + ", ".join(sorted(set(names), key=str.lower)))
    loc = next(l for l in locs if l["LocationName"] == hit)
    if loc.get("ActiveStatus") != "A":
        oracle.fail(f"Location {hit!r} exists but is not active (status {loc.get('ActiveStatus')}). "
                    "Ask the user for an active location.")
    used = collections.Counter(r["LocationSetCode"] for r in bu_rows or []
                               if r["InternalLocationCode"] == loc["LocationCode"] and r["LocationSetCode"])
    loc_set = used.most_common(1)[0][0] if used else ("COMMON" if loc.get("SetId") == 0 else None)
    if not loc_set and bu_rows is None:
        # no before-export in a fast run: the caller exports once and asks again
        print(f"  location {hit!r} is in reference set id {loc.get('SetId')}: the export tells its set code")
        return hit, loc["LocationCode"], None, loc["LocationId"]
    if not loc_set:
        oracle.fail(f"Location {hit!r} (code {loc['LocationCode']}) is in reference set id "
                    f"{loc.get('SetId')}, which no business unit uses yet; ask the user to confirm.")
    print(f"  location {hit!r} = code {loc['LocationCode']} (location set {loc_set}, REST)")
    return hit, loc["LocationCode"], loc_set, loc["LocationId"]


def rest_default_set(wanted):
    sets = rest_all(f"{oracle.API_BASE}/setIdSetsLOV", "reference data sets")
    code = match_value(wanted, [s["SetCode"] for s in sets])
    if code is None:
        name = match_value(wanted, [s["SetName"] for s in sets])
        code = next((s["SetCode"] for s in sets if s["SetName"] == name), None) if name else None
    if code is None:
        oracle.fail(f"Default set {wanted!r} is not one of Oracle's reference data sets. Ask the user "
                    "to pick one (name and code): "
                    + "; ".join(f"{s['SetName']} ({s['SetCode']})" for s in sets))
    name = next(s["SetName"] for s in sets if s["SetCode"] == code)
    print(f"  default set {wanted!r} = code {code} ({name}, REST)")
    return code, name


def rest_user(b):
    href = ds_lov("userNames")
    for user in [b["user"]] + ([b["user_fallback"]] if b.get("user_fallback") else []):
        hits = [u for u in rget(href, "user names", q=f"DisplayName='{user}'").get("items", [])
                if u.get("DisplayName") == user and u.get("ActiveFlag") == "Y"]
        if hits:
            if user != b["user"]:
                print(f"  NOTE  user {b['user']!r} not found; using the fallback {user!r}")
            return user
    oracle.fail(f"User {b['user']!r} (fallback {b.get('user_fallback')!r}) is not an active Oracle "
                "user. Ask the user for the exact user name.")


def rest_roles(user):
    """The roles the user holds (userRoleDetails of the user's own access row), read once."""
    return rest_all(ds_lov("userRoleDetails", user), "user roles", q=f"Username='{user}'")


def rest_access_on(bu_name, user=None):
    """Only the access rows on this business unit (and of this user): about 0.5 s, instead
    of all 400+ rows. A name with a quote falls back to the full read, filtered here."""
    if "'" in bu_name + (user or ""):
        return [r for r in rest_access_rows() if r.get("SecurityContextValue") == bu_name
                and (user is None or r.get("UserName") == user)]
    q = (f"UserName='{user}';" if user else "") + f"SecurityContextValue='{bu_name}'"
    return [r for r in rest_all(f"{oracle.API_BASE}/dataSecurities", "data access rows", q=q,
                                orderBy="UserRoleDataAssignmentId:asc")
            if r.get("SecurityContextValue") == bu_name and (user is None or r.get("UserName") == user)]


def rest_today():
    """Oracle's today (YYYY/MM/DD) from the date of a read-only REST answer, for an access
    row's start date when the export/import fallback needs one and no export was read."""
    r, err = oracle.try_call("GET", f"{oracle.API_BASE}/setIdSetsLOV", params={"limit": 1, "onlyData": "true"},
                             timeout=60)
    if err or not r.headers.get("Date"):
        raise RestUnavailable(f"Oracle's date: {err or 'no Date header'}")
    from email.utils import parsedate_to_datetime
    return parsedate_to_datetime(r.headers["Date"]).strftime("%Y/%m/%d")


def rest_role(user, wanted, roles=None):
    """Role name -> role code among the roles the user holds (userRoleDetails); pass roles
    (rest_roles) to reuse one read for several roles."""
    roles = rest_roles(user) if roles is None else roles
    names = [r["RoleName"] for r in roles]
    hit = match_value(wanted, names)
    if hit is None:
        word = wanted.split()[0].lower() if wanted.split() else ""
        similar = sorted({n for n in names if word and word in n.lower()})
        oracle.fail(f"{user} does not hold a role named {wanted!r}. Ask the user to pick one of "
                    f"{user}'s roles" + (f" like it: {', '.join(similar)}" if similar else
                                         f" ({len(names)} roles)") + ".")
    code = next(r["RoleCommonName"] for r in roles if r["RoleName"] == hit)
    print(f"  role {hit!r} = code {code} ({user} holds it, REST)")
    return hit, code


# ---------------------------------------------------------------- pricing visibility (2026-10-21)
# Oracle caches a user's data access: a role newly given on a business unit may not show
# (e.g. for pricing, or in Create Order) until that user signs out and in again. After the
# access rows are written, this folder re-checks through fresh REST reads for up to 2
# minutes and records every created business unit in common/created_business_units.json
# (shared with Price Lists): "ready", or "pending" when Oracle still needs a fresh sign-in.

REGISTRY = oracle.PROJECT_ROOT / "common" / "created_business_units.json"
FRESH_SIGNIN_TEXT = "Oracle needs a fresh sign-in before this business unit shows for pricing."
VISIBLE_WAIT, VISIBLE_EVERY = 120, 5           # seconds (quick filtered reads since 2026-10-23)


def registry_load():
    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    data.setdefault("business_units", [])
    return data


def registry_add(name, status, note, user, roles):
    """Add one business unit to the shared file, only after both access rows are verified.
    A name already there is skipped (never doubled, never changed). Written atomically: a
    temporary file next to it, then replaced in one step, so a reader never sees half a file."""
    if name.upper().startswith("ZZ_TEST_"):
        # test data (2026-10-26, the user's rule): the price list drop-down (demos) must not show it
        print(f"  NOTE  {name} is test data: not written to {REGISTRY.name}")
        return False
    data = registry_load()
    if any(e.get("name", "").lower() == name.lower() for e in data["business_units"]):
        print(f"  SKIP  {name} is already in {REGISTRY.name} - not added twice")
        return False
    data["business_units"].append({
        "name": name, "status": status, "note": note, "user": user, "roles": roles,
        "pricing_confirmed": False, "written": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    data["about"] = ("Business units created and verified by the Business Units folder (business "
                     "unit, Order Manager and Pricing Administrator access rows). status: ready | "
                     "pending (Oracle needs a fresh sign-in before it shows for pricing). "
                     "pricing_confirmed: set by Price Lists after a price list was created with it.")
    tmp = REGISTRY.with_name(REGISTRY.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
    os.replace(tmp, REGISTRY)
    print(f"  {'OK  ' if status == 'ready' else 'NOTE'}  {name} added to {REGISTRY.name}: {status}"
          + (f" ({note})" if note else ""))
    return True


def oracle_reason(err):
    """Oracle's own message from a failed call, in its words (no codes or addresses)."""
    body = (err or "").split("\n", 2)[-1].strip()
    try:
        data = json.loads(body)
        body = data.get("detail") or data.get("title") or data.get("o:errorDetails") or body
        if isinstance(body, list):
            body = "; ".join(str(x.get("detail", x)) if isinstance(x, dict) else str(x) for x in body)
    except ValueError:
        pass
    body = re.sub(r"<[^>]+>", " ", str(body))
    return re.sub(r"\s+", " ", body).strip()[:300] or "Oracle gave no reason"


def add_access(ui, work, args, items, rest_ok, found, key, label, tolerant=False, deep=False, ph=None):
    """One data access row per item (that user, role code, the business unit): REST, with
    the export/import fallback; an existing row is skipped. Only these rows are added; no
    other user's access is touched. Verified by a REST read-back of only those users' rows
    on those business units (exactly one active row each, about 0.5 s). deep (Check on
    screen too, --check): also every other row of every user unchanged (two full reads) and
    on screen. tolerant (the optional extra access): no fallback, a rejection is returned as
    a plain reason instead. ph: the step's Phase (sub-steps, limit). Returns (ok, route, reason)."""
    sub = ph.sub if ph else (lambda text: None)
    route, reason = "REST", ""

    def mine_rows():
        return [r for u, bu in sorted({(p["user"], p["b"]["name"]) for p in items})
                for r in rest_access_on(bu, u)]
    before = mine_rows() if rest_ok else []
    full_before = rest_access_rows() if rest_ok and deep else None
    todo = [p for p in items if not any(is_mine(r, [p]) for r in before)]
    for p in items:
        if p not in todo:
            print(f"  SKIP  access {p['user']} / {p['role_name']} / {p['b']['name']} exists")
    done = []
    if todo and rest_ok and not args.fallback:
        print(f"\n{label} (route: REST): creating {len(todo)} data access row(s) ...")
        sub("Saving it in Oracle")
        try:
            for p in todo:
                rest_create_access(p)
                done.append(p)
        except RestUnavailable as e:
            if tolerant:
                reason = oracle_reason(str(e))
                print(f"  NOTE  {label}: Oracle didn't accept it: {reason}")
                return False, "REST (rejected)", reason
            print(f"\nREST failed for {label.lower()}:\n  {str(e)[:1200]}\n"
                  f"Switching {label.lower()} to the export/import fallback for what is still missing.")
            route = "export/import (fallback)"
    elif todo and tolerant:
        return False, "not run", "Oracle didn't allow adding it automatically right now"
    elif todo:
        route = "export/import"
    left = [p for p in todo if p not in done]
    if left and route != "REST":
        da_before = read_zip(ui.setup.export_csv(DA_TASK, DA_AREA, OFFERING)[0])
        da_now = dicts(need(da_before, DA_CSV, DA_TASK))
        left = [p for p in left if not any(
            x["UserName"] == p["user"] and x["RoleName"] == p["code"] and x["BuName"] == p["b"]["name"]
            and x["ObjectName"] == BU_OBJECT for x in da_now)]
        if left:
            for p in left:              # a fast run read no export: Oracle's today from a REST answer
                if not p["da_row"].get("StartDateActive"):
                    p["da_row"]["StartDateActive"] = rest_today()
            zip_ = build_only_new(da_before, DA_CSV, [p["da_row"] for p in left], work / f"import_{key.replace(':', '_')}.zip")
            print(f"\n{label} (route: {route}): importing {len(left)} data access row(s) ({zip_.name}) ...")
            ui.setup.import_csv(DA_TASK, DA_AREA, zip_, OFFERING)
    print(f"\nVerifying {label.lower()} (route {route}) ...")
    sub("Reading it back from Oracle")
    ok = True
    if rest_ok:
        after = mine_rows()
        for p in items:
            mine = [r for r in after if is_mine(r, [p])]
            if found is not None and mine:
                found.setdefault(p["b"]["name"], {})[key] = mine[0]
            good = len(mine) == 1 and mine[0].get("ActiveFlag") is True
            print(f"  {'OK  ' if good else 'FAIL'}  access {p['user']} / {p['role_name']} ({p['code']}) / "
                  f"{p['b']['name']} (REST GET): " + (f"active, id {mine[0].get('UserRoleDataAssignmentId')}"
                                                      if mine else "not found"))
            ok &= good
        if deep:
            full_after = rest_access_rows()
            strip = lambda rows: collections.Counter(
                tuple((k, r.get(k)) for k in ACCESS_KEYS + ("UserRoleDataAssignmentId",)) for r in rows)
            # both sides without these rows: an existing (skipped) row is in both lists
            # (2026-10-21, an existing business unit showed "1 gone" otherwise)
            b_other = strip(r for r in full_before if not is_mine(r, items))
            a_other = strip(r for r in full_after if not is_mine(r, items))
            if b_other == a_other:
                print(f"  OK    every other access row unchanged ({sum(b_other.values())} rows, all users)")
            else:
                print(f"  FAIL  other access rows changed ({sum((b_other - a_other).values())} gone/changed, "
                      f"{sum((a_other - b_other).values())} new)")
                ok = False
    if deep or not rest_ok:           # the screen is the only read-back without REST
        sub("Looking at it on Oracle's screen")
        open_data_access(ui)
        for p in items:
            rows = access_rows(ui, p["user"], p["role_name"]) or []
            good = any(len(r) > 3 and r[3] == p["b"]["name"] for r in rows)
            print(f"  {'OK  ' if good else 'FAIL'}  on screen (Users with Data Access): {p['user']} / "
                  f"{p['role_name']} / {p['b']['name']}")
            ok &= good
    if not ok:
        reason = "Oracle doesn't show the new access as expected"
    return ok, route, reason


# ---------------------------------------------------------------- roles for Business unit access

class ExtraAccessRefused(Exception):
    """The chosen extra role can't be given on a business unit: stop before anything is made.
    .valid: the roles that can (plain names)."""

    def __init__(self, text, valid):
        super().__init__(text)
        self.text, self.valid = text, valid


def bu_role_codes(access_rows, mapping_rows=None):
    """Role codes Oracle shows working with the Business unit security context: an existing
    access row with the role on a business unit (any user), or Oracle's security context
    mapping (data access export). Oracle has no REST list of roles per context (its Security
    Context list is the same for every role, checked 2026-10-21)."""
    codes = {r.get("RoleCommonName") for r in access_rows if r.get("SecurityContext") == SECURITY_CONTEXT}
    codes |= {r.get("RoleName") for r in (mapping_rows or []) if r.get("ObjectName") == BU_OBJECT}
    return {c for c in codes if c}


def check_extra_role(user, role, roles, codes, extra_user_named):
    """The extra role must be one the user holds and one that works with business units.
    Returns (role name, code); else ExtraAccessRefused with the valid choices."""
    names = {r["RoleName"]: r["RoleCommonName"] for r in roles}
    valid = sorted((n for n, c in names.items() if c in codes), key=str.lower)
    hit = match_value(role, list(names))
    if hit is None:
        raise ExtraAccessRefused(f"{user} doesn't hold a role called '{role}', so it can't be given "
                                 "as extra access. Please pick one of the roles that can.", valid)
    if names[hit] not in codes:
        raise ExtraAccessRefused(f"The role '{hit}' can't be given for a business unit, so it can't be "
                                 "the extra access. Please pick one of the roles that can.", valid)
    return hit, names[hit]


def pricing_visible(p):
    """Fresh REST reads: the business unit is listed and active, and the user's new access
    row for the role on it is there and active. (No REST list shows the login's pricing
    access as such; the first price list is the final proof, see Price Lists.)"""
    try:
        bu = [h for h in rest_bu(p["b"]["name"]) if h.get("ActiveFlag") is not False]
        rows = [r for r in rest_access_on(p["b"]["name"], p["user"])
                if is_mine(r, [p]) and r.get("ActiveFlag") is True]
    except RestUnavailable as e:
        print(f"  NOTE  visibility check could not read Oracle: {str(e)[:200]}")
        return False
    return bool(bu) and bool(rows)


def wait_for_pricing(p):
    """Up to 2 minutes: a fresh REST read every 30 s until the business unit is visible."""
    start = time.time()
    while True:
        if pricing_visible(p):
            print(f"  OK    {p['b']['name']} is visible through a fresh read "
                  f"({int(time.time() - start)} s after the access rows were written)")
            return True
        if time.time() - start >= VISIBLE_WAIT:
            print(f"  NOTE  {p['b']['name']} still not visible after {VISIBLE_WAIT} s")
            return False
        print(f"  ...   {p['b']['name']} not visible yet; trying again in {VISIBLE_EVERY} s")
        time.sleep(VISIBLE_EVERY)


def fresh_signin_and_recheck(ui, names):
    """The saved browser sign-in may hold the old access. The user signs in again in a
    window (common/login_once.py starts a fresh sign-in without the saved session; nothing
    is read or typed here), then Create Order is checked once more. Returns its list, or
    None when no fresh sign-in was possible.
    The recheck uses a new context in the browser that is already open: a second OracleUI
    here would start Playwright twice ("Sync API inside the asyncio loop", 2026-10-21)."""
    print(f"  NOTE  {', '.join(names)} not on Create Order yet. {FRESH_SIGNIN_TEXT} "
          "A sign-in window opens: please sign in there again.")
    p = subprocess.run([sys.executable, str(oracle.PROJECT_ROOT / "common" / "login_once.py")],
                       cwd=oracle.PROJECT_ROOT)
    if p.returncode != 0:
        print("  NOTE  The fresh sign-in didn't finish, so Create Order can't be checked again now. "
              "Please sign out of Oracle and sign in again later.")
        return None
    old_context, old_page = ui.context, ui.page
    ctx = browser.new_context(ui.browser)      # signed in from the fresh sign-in
    try:
        ctx.route(browser.HELP_WIDGET, lambda route: route.abort())
        ctx.set_default_timeout(60000)
        ui.context, ui.page = ctx, ctx.new_page()
        ui.page.set_viewport_size({"width": 1600, "height": 1000})
        return create_order_business_units(ui)
    finally:
        ui.context, ui.page = old_context, old_page
        ctx.close()


def create_order_fresh(ui):
    """Create Order's Business Unit list in a fresh browser context: signed in from the saved
    sign-in (Playwright loads it; this script never reads or changes that file) minus ONLY
    the app session cookie (APP_COOKIE), dropped in memory. Oracle caches the list in that
    app session (2026-10-22): with it, a new business unit stayed hidden however long one
    waited, which looked like a failed run. Without it Oracle starts a new app session on
    the same sign-in and reads the access afresh."""
    old_context, old_page = ui.context, ui.page
    ctx = browser.new_context(ui.browser)
    try:
        ctx.clear_cookies(**APP_COOKIE)
        ctx.route(browser.HELP_WIDGET, lambda route: route.abort())
        ctx.set_default_timeout(60000)
        ui.context, ui.page = ctx, ctx.new_page()
        ui.page.set_viewport_size({"width": 1600, "height": 1000})
        return create_order_business_units(ui)
    finally:
        ui.context, ui.page = old_context, old_page
        ctx.close()


def rest_access_rows():
    # Sorted by id: unsorted pages are not stable (2026-10-21 one read of 380 rows had 98
    # duplicates and missed 98, which made the "every other row unchanged" check fail).
    return rest_all(f"{oracle.API_BASE}/dataSecurities", "data access rows",
                    orderBy="UserRoleDataAssignmentId:asc")


ACCESS_KEYS = ("UserName", "RoleCommonName", "SecurityContext", "SecurityContextValue",
               "SecurityContextValue2", "SecurityContextValue3", "ActiveFlag")


def is_mine(row, plans):
    return any(row.get("UserName") == p["user"] and row.get("RoleCommonName") == p["code"]
               and row.get("SecurityContext") == SECURITY_CONTEXT
               and row.get("SecurityContextValue") == p["b"]["name"] for p in plans)


def rest_create_access(p):
    body = {"UserName": p["user"], "RoleCommonName": p["code"], "RoleNameCr": p["role_name"],
            "SecurityContext": SECURITY_CONTEXT, "SecurityContextValue": p["b"]["name"],
            "ActiveFlag": True}
    r, err = oracle.try_call("POST", f"{oracle.API_BASE}/dataSecurities", json=body, timeout=180)
    if err:
        if r is not None and r.status_code in (401, 403):
            print(f"  REST refused creating data access (HTTP {r.status_code}): this login has no "
                  "permission to do it through REST.")
        raise RestUnavailable(f"POST dataSecurities for {p['b']['name']}: {err}")
    print(f"  data access created through REST (HTTP {r.status_code})")


# ---------------------------------------------------------------- page interface

HERE = Path(__file__).resolve().parent
SPEC = {
    "title": "Create a business unit",
    "description": "These will always be set up: Order Manager and Pricing Administrator access "
                   f"for {REQUIRED_USER['user']}. More options add extra access on top of that, as "
                   "a last step. An existing business unit is never changed; only missing access "
                   "is added to it.",
    "fields": [
        {"key": "name", "label": "Business unit name", "required": True, "type": "text",
         "placeholder": "Karachi Sales", "default": None, "help": "Up to 240 characters."},
        # Up front and pre-filled with the standing defaults (required pick + default: the
        # form shows the default, and a left-out value means the default).
        {"key": "location", "label": "Location", "required": True, "type": "pick",
         "placeholder": "Go Saas Lahore Office", "default": DEFAULTS["location"], "list": "samples",
         "help": "Pick one that is known to work, or type another; it is checked with Oracle."},
        {"key": "default_set", "label": "Default set", "required": True, "type": "pick",
         "placeholder": "001 Customer Site", "default": DEFAULTS["default_set"], "list": "samples",
         "help": "Pick one that is known to work, or type another; it is checked with Oracle."},
        {"key": "manager", "label": "Manager", "required": False, "type": "pick",
         "placeholder": "Yaqub, Younas", "default": None,
         "help": "Optional. Only Yaqub, Younas or Smith, Aron can be chosen."},
        # More options = extra access, in addition to the two required roles (never instead).
        {"key": "user", "label": "Extra access user", "required": False, "type": "pick",
         "placeholder": "Configuration.TEST", "default": None,
         "help": f"Empty: {REQUIRED_USER['user']}. Gets the extra role below, after the required "
                 "access is in place."},
        {"key": "role", "label": "Extra access role", "required": False, "type": "pick",
         "placeholder": "Buyer", "default": None,
         "help": "In addition to Order Manager and Pricing Administrator. Only roles that can be "
                 "given for a business unit are listed."},
        {"key": "pricing_role", "label": "Second extra access role", "required": False,
         "type": "pick", "placeholder": "Pricing Analyst", "default": None,
         "help": "Optional, one more extra role for the same user."},
        {"key": "active", "label": "Active", "required": False, "type": "yes-no",
         "placeholder": "yes", "default": True},
        {"key": "screen_check", "label": "Check on screen too", "required": False, "type": "yes-no",
         "placeholder": "no", "default": False,
         "help": "Also opens Oracle's own screens to look at the result (Manage Business Units, "
                 "Users with Data Access, Create Order). Takes several minutes longer."},
    ],
}
WHERE = ("Setup and Maintenance > Order Management > Organization Structures > Manage Business "
         "Unit (search {name}); Users and Security > Manage Data Access for Users > Users with "
         "Data Access; and the Business Unit list on Create Order")


def default_user():
    """The default user, or its fallback, as REST knows it (for the role list)."""
    return rest_user(REQUIRED_USER)


# The page's drop-downs for location and default set: only verified values - used by a
# real create in this project (Go Saas Lahore Office / 001 CUSTOMER SITE: ZZ_TEST_1424,
# ZZ_TEST_5950, TEstBU, ZZ_TEST_3079, ZZ_TEST_5115) or by the user's own test (the others,
# 2026-10-21). Oracle's exact spelling, confirmed in the live lists 2026-10-21; (value,
# label). See CLAUDE.md > Page interface. `--options FIELD --all` gives the full live
# list; a --run checks anything typed against the full live list.
SAMPLES = {
    "location": [("Go Saas Lahore Office", "Go Saas Lahore Office"),
                 ("GoSaaS Labs Location", "GoSaaS Labs Location"),
                 ("Headquarters_ZS", "Headquarters_ZS")],
    "default_set": [("001 CUSTOMER SITE", "001 Customer Site"), ("ENTERPRISE", "Enterprise Set"),
                    ("CUSTOMER_RDS", "CUSTOMER_RDS")],
}


def options_for(key):
    """The drop-down samples above for location and default set; with --all, during --run
    (the check of what was typed in) and for the other lists, read live through REST."""
    if key == "manager":                 # only these two (the user's decision, 2026-10-26)
        import bu_batch
        return [{"value": m["name"], "label": m["name"]} for m in bu_batch.MANAGERS]
    if key in SAMPLES and sys.argv[1:2] == ["--options"] and "--all" not in sys.argv:
        return [{"value": v, "label": l} for v, l in SAMPLES[key]] +             ([{"value": "none", "label": "(none)"}] if key == "location" else [])   # no location (2026-10-26)
    return live_options(key)


def live_options(key):
    """Live lists through REST (GET only), the same lists the run checks against."""
    oracle.check_environment()
    if key == "location":
        locs = rest_all(f"{HCM_BASE}/locations", "locations",
                        fields="LocationName,ActiveStatus")
        names = sorted({l["LocationName"] for l in locs if l.get("ActiveStatus") == "A"}, key=str.lower)
        return [{"value": "none", "label": "(none)"}] + [{"value": n, "label": n} for n in names]
    if key == "default_set":
        return [{"value": s["SetCode"], "label": s.get("SetName") or s["SetCode"]}
                for s in sorted(rest_all(f"{oracle.API_BASE}/setIdSetsLOV", "reference data sets"),
                                key=lambda s: s["SetCode"])]
    if key == "user":
        # The userNames list stops at 500 rows (528 users on 2026-10-21: offset 500 gave
        # nothing), so it is read in both sort orders and joined; that covers up to 1000.
        href = ds_lov("userNames")
        total = rget(href, "user names", limit=1, totalResults="true").get("totalResults") or 0
        if total > 1000:
            print(f"  NOTE  {total} users: the list may miss some (500 from each end only)")
        users = rest_all(href, "user names", orderBy="DisplayName:asc")
        users += rest_all(href, "user names", orderBy="DisplayName:desc")
        names = sorted({u["DisplayName"] for u in users
                        if u.get("ActiveFlag") == "Y" and u.get("DisplayName")}, key=str.lower)
        return [{"value": n, "label": n} for n in names]
    if key in ("role", "pricing_role"):
        # Extra access roles: the drop-down lists the roles the required user holds that can
        # be given for a business unit (an existing access row on a business unit, any user:
        # 59 of 281 on 2026-10-21, a quick read). During --run every role the user holds is
        # accepted here, because the run itself checks the chosen one up front, also against
        # Oracle's security context mapping, and lists the valid ones if it can't be used.
        user = default_user()
        roles = rest_all(ds_lov("userRoleDetails", user), "user roles", q=f"Username='{user}'")
        codes = None if "--run" in sys.argv else bu_role_codes(rest_access_rows())
        names = sorted({r["RoleName"] for r in roles if r.get("RoleName")
                        and (codes is None or r.get("RoleCommonName") in codes)}, key=str.lower)
        return [{"value": n, "label": n} for n in names]
    raise page.PageError("FAILED", detail=f"no list for {key!r}")


def mapping_rows(ui):
    """Oracle's security context mapping (which role works with which security context), from
    a fresh data access export (read-only)."""
    files = read_zip(ui.setup.export_csv(DA_TASK, DA_AREA, OFFERING)[0])
    m = next((f for n, f in files.items() if "SECURITY_CONTEXT_MAPPING" in n), None)
    return dicts(m) if m else []


def rest_user_exact(name):
    """The named user if Oracle has it as an active user (no fallback), else None."""
    hits = [u for u in rget(ds_lov("userNames"), "user names", q=f"DisplayName='{name}'").get("items", [])
            if u.get("ActiveFlag") == "Y"]
    return match_value(name, [u["DisplayName"] for u in hits])


def plan_extras(b, required_user, access_rows, load_mapping):
    """Up-front check of the extra access, before anything is created: the user is active,
    and each extra role is one the user holds and one that can be given for a business unit
    (an existing access row on a business unit, any user; else Oracle's security context
    mapping, read only when needed through load_mapping()). Returns
    [{"user", "role_name", "code"}]; raises ExtraAccessRefused."""
    if not b.get("extra"):
        return []
    named = b["extra"][0]["user"]
    user = required_user
    if named:
        user = rest_user_exact(named)
        if user is None:
            raise ExtraAccessRefused(f"{named} isn't an active user in Oracle, so the extra access "
                                     "can't be given to them. Please check the user name.", [])
    roles = rest_all(ds_lov("userRoleDetails", user), "user roles", q=f"Username='{user}'")
    codes, mapping, out = bu_role_codes(access_rows), None, []
    for e in b["extra"]:
        names = {r["RoleName"]: r["RoleCommonName"] for r in roles}
        hit = match_value(e["role"], list(names))
        if hit and names[hit] not in codes and mapping is None:
            mapping = load_mapping()
            codes = bu_role_codes(access_rows, mapping)
        role_name, code = check_extra_role(user, e["role"], roles, codes, bool(named))
        print(f"  extra access {user} / {role_name} ({code}): the role can be given for a business unit")
        out.append({"user": user, "role_name": role_name, "code": code})
    return out


def run_request(request, progress):
    """--run: one business unit. Required first (the business unit, Order Manager and
    Pricing Administrator access for the required user, verified, cache check, shared list),
    then the extra access from More options as its own last step."""
    oracle.check_environment()
    browser.refuse_production()
    name = request["name"]
    if len(name) > 240:
        raise page.PageError("INVALID_REQUEST", "Business unit name can be at most 240 characters.",
                             [{"field": "name", "problem": "too_long"}])
    where = WHERE.format(name=name)
    b = {k: request[k] for k in ("name", "location", "default_set", "user", "role", "pricing_role",
                                 "active", "manager") if k in request}
    if b.get("manager") in ("", None):
        b.pop("manager", None)
    if b.get("user") and not (b.get("role") or b.get("pricing_role")):
        raise page.PageError("INVALID_REQUEST", "Please also pick a role for the extra access, or "
                             "leave the extra access user empty.",
                             [{"field": "role", "problem": "missing"}])
    units = parse_requirements({"business_units": [b]}, "page")
    # The extra role is checked before the run starts and before anything is created.
    if units[0]["extra"]:
        required_user = rest_user(REQUIRED_USER)

        def load_mapping():
            progress.step("checking_roles", 25, "Checking which roles can be given for a business unit")
            with browser.OracleUI(oracle.init_work_dir(HERE), headless=True) as ui:
                ui.setup = Setup(ui)
                rows = mapping_rows(ui)
            oracle.cleanup_work_dir()        # only the read-only export was in it
            return rows
        try:
            units[0]["extra_plan"] = plan_extras(units[0], required_user, rest_access_rows(), load_mapping)
        except ExtraAccessRefused as e:
            raise page.PageError("NOT_IN_ORACLE", e.text + (f" Roles that can: {', '.join(e.valid)}."
                                                             if e.valid else ""),
                                 [{"field": "role", "problem": "not_in_oracle", "valid": e.valid}])
    args = argparse.Namespace(check=False, fallback=False, headed=False,
                              screen_check=bool(units[0].get("screen_check")))
    found = {}
    try:
        run_units(args, units, HERE, progress, found)
    except StepTimeout as e:
        raise page.PageError("TIMEOUT", f"Oracle took longer than {STEP_LIMIT // 60} minutes for this step: "
                                        f"{e.what}. {e.state}",
                             {"step": e.what, "limit_seconds": STEP_LIMIT, "found": found})
    progress.step("done")
    got = found.get(name) or next((v for k, v in found.items() if k.lower() == name.lower()), {})
    shown_name = (got.get("name") or name)
    caps_note = (f" Oracle already had it as '{shown_name}', which differs from '{name}' only in capitals, so it "
                 "was treated as that business unit." if shown_name != name else "")
    lines, parts = [], []
    req = got.get("required") or []
    added = [r["role"] for r in req if r["status"] == "added"]
    had = [r["role"] for r in req if r["status"] != "added"]
    user = req[0]["user"] if req else REQUIRED_USER["user"]
    and_join = lambda xs: " and ".join(xs)
    if got.get("existing"):
        lines.append("Business unit: already in Oracle, not changed")
        for r in req:
            lines.append(f"{r['role']} access: " + ("added (it was missing)" if r["status"] == "added"
                                                    else "already there"))
        if added:
            # a half-made business unit: say exactly what was missing and what was added
            parts.append(f"The business unit {shown_name} was already in Oracle but {user} was missing "
                         f"{and_join(added)} access on it. Added: {and_join(added)} access."
                         + (f" {and_join(had)} access was already there." if had else ""))
        else:
            parts.append(f"The business unit {shown_name} was already in Oracle with {and_join(had)} "
                         f"access for {user}, so it wasn't changed.")
    else:
        lines.append("Business unit: created and checked")
        for r in req:
            lines.append(f"{r['role']} access: done")
        parts.append(f"Created the business unit {shown_name} and gave {user} {and_join(added)} access on it.")
    # what was checked in Oracle, and what wasn't looked at on the screens
    checked = []
    if not got.get("existing"):
        checked.append("the business unit is there and " + ("active" if units[0]["active"] else "inactive")
                       + (f" at {got['loc_name']}" if got.get("loc_name") else ""))
    if req:
        checked.append(f"{and_join(r['role'] for r in req)} access for {user} "
                       f"{'is' if len(req) == 1 else 'are'} there and active")
    if checked:
        parts.append("Checked in Oracle: " + "; ".join(checked) + ".")
    if got.get("screens"):
        parts.append("Also checked on the screens: Manage Business Units, Users with Data Access and Create Order"
                     + ("" if got.get("create_order") is not False else
                        f" (Create Order doesn't list it yet: {FRESH_SIGNIN_TEXT})") + ".")
    else:
        parts.append("Not looked at on Oracle's screens this time (Manage Business Units, Users with Data "
                     "Access, Create Order); choose Check on screen too under More options for that.")
    if added and got.get("pending") and got.get("create_order") is not False:
        parts.append(f"It doesn't show for pricing yet. {FRESH_SIGNIN_TEXT} Sign out of Oracle and sign in again.")
    extra = got.get("extra") or []
    failed = [e for e in extra if e["status"] == "not added"]
    for e in extra:
        lines.append(f"Extra access {e['role']} for {e['user']}: " +
                     {"added": "done", "already there": "already there"}.get(e["status"], "not added"))
    if failed:
        reason = "; ".join(f"{e['role']}: {e['reason']}" for e in failed)
        try:
            page.plain_check(reason, "reason")
        except ValueError:
            reason = "Oracle didn't accept it"
        parts = ["The business unit is ready: Order Manager and Pricing Administrator were given. "
                 f"The extra access wasn't added: {reason}"]
    elif extra:
        parts.append("Extra access: " + "; ".join(f"{e['role']} for {e['user']} "
                                                  + ("done" if e["status"] == "added" else "already there")
                                                  for e in extra) + ".")
    nothing = got.get("existing") and not added and not any(e["status"] == "added" for e in extra)
    if nothing and not failed:
        parts = [f"The business unit {shown_name} already exists in Oracle with all the requested "
                 f"access ({and_join(had)} for {user}" + ("" if not extra else ", and the extra access")
                 + "), so nothing was changed."]
    bu = got.get("business_unit") or {}
    keys = ("UserName", "RoleNameCr", "RoleCommonName", "SecurityContext", "SecurityContextValue",
            "ActiveFlag", "UserRoleDataAssignmentId")
    return {"text": " ".join(parts) + caps_note, "where": where, "skipped": bool(nothing),
            "partial": bool(failed), "steps": lines,
            "created": {"business_unit": {k: bu.get(k) for k in
                                          ("Name", "InternalLocationCode", "LocationSetCode",
                                           "DefaultSetCode", "Status", "OrganizationCode",
                                           "BusinessUnitName", "BusinessUnitId", "ActiveFlag") if k in bu},
                        "required_access": [dict({k: (r.get("row") or {}).get(k) for k in keys},
                                                 status=r["status"]) for r in req],
                        "extra_access": [dict({k: (e.get("row") or {}).get(k) for k in keys},
                                              role=e["role"], user=e["user"], status=e["status"],
                                              reason=e.get("reason") or None) for e in extra],
                        "create_order_list": got.get("create_order"),
                        "checked_on_screens": bool(got.get("screens")),
                        "pricing": ("pending: needs a fresh sign-in" if got.get("pending") else "ready")
                        if added else "not changed"}}


# ---------------------------------------------------------------- main

def main():
    if sys.argv[1:2] in (["--plan"], ["--run-batch"]):   # the upload sheet (2026-10-26), bu_batch.py
        import bu_batch
        sys.exit((bu_batch.plan_command if sys.argv[1] == "--plan" else bu_batch.run_batch_command)(sys.argv[1:]))
    page.main(SPEC, options_for, run_request)   # --spec / --options / --run; else returns
    here = HERE
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(here / "request.json"), help="requirements JSON")
    ap.add_argument("--check", action="store_true",
                    help="read-only: REST lists, BU export, export/import screens, Create Order "
                         "list; nothing imported, created or saved")
    ap.add_argument("--fallback", action="store_true",
                    help="step 2 by export/import instead of REST")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    ap.add_argument("--screen-check", action="store_true",
                    help="also check the result on Oracle's screens and by a second export (slow)")
    args = ap.parse_args()

    oracle.check_environment()
    browser.refuse_production()
    units = load_requirements(args.file)
    print(f"{len(units)} business unit(s) requested in {args.file}")
    try:
        run_units(args, units, here)
    except StepTimeout as e:
        oracle.fail(f"Timeout: '{e.what}' took longer than {STEP_LIMIT // 60} minutes. {e.state}")


def run_units(args, units, here, progress=None, found=None):
    """The requested business units, required first, extra access last:
      1. the business unit (export/import), verified;
      2. Order Manager, then Pricing Administrator access for the required user (REST,
         export/import fallback), each verified by read-back;
      3. the pricing cache check and common/created_business_units.json (and, with the
         screen check, the Create Order list);
      4. the extra access (More options), REST only: a rejection is noted, never a failure,
         and never undoes or blocks 1-3.
    Fast by default (2026-10-23): with REST, no before-export (the import file comes from
    bu_import_template.json), the import is submitted and the new business unit is polled
    by a quick REST read every 3 s (never the import status screen), access rows are read
    only for that user and business unit, independent reads run at the same time, and the
    browser opens only to create a business unit. The screen checks (after-export compare,
    Manage Business Units, Users with Data Access, Create Order) run only with the screen
    check (More options "Check on screen too", --screen-check) or --check. Every step has a
    6-minute limit (Phase / StepTimeout).
    An existing business unit is not changed: only its missing required and extra rows are
    added (needs REST). progress: the page's progress lines (--run). found (optional dict):
    filled per business unit with what was done (see run_request)."""
    def step(key, percent=None, text=None):
        if progress:
            with PROGRESS_LOCK:
                progress.step(key, percent, text)

    def phase(key, percent, text, state="Nothing was changed in Oracle in this step."):
        return Phase(progress, key, percent, text, state)

    screen = bool(args.check or getattr(args, "screen_check", False) or any(b.get("screen_check") for b in units))
    t_run = time.time()
    work = oracle.init_work_dir(here)
    results = []
    ui = LazyUI(work, headless=not args.headed)
    try:
        oracle.session()                     # one REST session, made before the parallel reads
        rest_ok, existing_rest = True, {}
        try:
            with ThreadPoolExecutor(4) as pool:
                existing_rest = dict(zip([b["name"] for b in units],
                                         pool.map(lambda b: rest_bu(b["name"]), units)))
        except RestUnavailable as e:
            rest_ok = False
            print(f"  REST unavailable for the lists and data access ({str(e)[:300]}); "
                  "using the screens and the export/import route")

        bu_before = bu_rows = None
        today = None

        def before_export():
            nonlocal bu_before, bu_rows, today
            if bu_before is None:
                print("Exporting Manage Business Unit (before) ...")
                bu_zip, _ = ui.setup.export_csv(BU_TASK, BU_AREA, OFFERING)
                bu_before = read_zip(bu_zip)
                save_template(bu_before)
                bu_rows = dicts(need(bu_before, BU_CSV, BU_TASK))
                today = oracle_today(bu_before)
                print(f"  {len(bu_rows)} business units in the export")

        if not rest_ok or screen:            # the screen route, --check and the screen check need it
            with phase("reading_business_units", 22, "Reading Oracle's business units"):
                before_export()

        plans, da_rows, mapping = [], None, None

        def load_mapping():
            nonlocal mapping
            if mapping is None:
                print("Exporting Manage Data Access for Users (security context mapping) ...")
                mapping = mapping_rows(ui)
            return mapping

        for b in units:
            print(f"\n== {b['name']}")
            same = [r for r in bu_rows or [] if r["Name"].lower() == b["name"].lower()]
            in_rest = existing_rest.get(b["name"]) or []
            existing = bool(same or in_rest)
            on_bu = []
            if existing:
                print(f"  NOTE  {b['name']}: business unit already exists - not changed. Its values: "
                      + (show_existing(same[0]) if same else str(in_rest[0])))
                if not rest_ok:
                    print("  SKIP  its access can only be checked and added through REST, which is "
                          "unavailable now")
                    results.append((b["name"], "skipped (exists)"))
                    continue
                b = dict(b, name=same[0]["Name"] if same else in_rest[0]["BusinessUnitName"])
            print("  checking the request against Oracle's lists ...")
            loc_name = loc_code = loc_set = loc_id = set_code = set_name = None
            if rest_ok:
                with phase("checking_lists", 25, "Checking the details with Oracle"):
                    # independent reads at the same time; each list read once
                    with ThreadPoolExecutor(4) as pool:
                        f_user = pool.submit(rest_user, REQUIRED_USER)
                        f_loc = None if existing or b["location"] is None else                             pool.submit(rest_location, b["location"], bu_rows)
                        f_set = None if existing else pool.submit(rest_default_set, b["default_set"])
                        f_on = pool.submit(rest_access_on, b["name"]) if existing else None
                        user = f_user.result()
                        roles = rest_roles(user)
                        req = [rest_role(user, r, roles) for r in REQUIRED_ROLES]
                        if not existing and f_loc is None:          # no location (screen: optional)
                            loc_name, loc_code, loc_set, loc_id = None, "", "", None
                        elif not existing:
                            loc_name, loc_code, loc_set, loc_id = f_loc.result()
                        if not existing:
                            set_code, set_name = f_set.result()
                        on_bu = f_on.result() if f_on else []
                    if not existing and loc_set is None and b["location"] is not None:  # outside the common set
                        before_export()
                        loc_name, loc_code, loc_set, loc_id = rest_location(b["location"], bu_rows)
                if existing:
                    print("        data access rows on it: " + ("; ".join(
                        f"{r['UserName']} / {r['RoleNameCr']}" for r in on_bu
                        if r.get("SecurityContext") == SECURITY_CONTEXT) or "none"))
            else:
                if da_rows is None:
                    print("Exporting Manage Data Access for Users (for the screen checks) ...")
                    da_rows = dicts(need(read_zip(ui.setup.export_csv(DA_TASK, DA_AREA, OFFERING)[0]),
                                         DA_CSV, DA_TASK))
                open_bu_form(ui)
                with ui.step("check location and default set (screen)"):
                    loc_name, loc_code, loc_set = resolve_location(ui, b["location"], bu_rows)                         if b["location"] is not None else (None, "", "")
                    set_code, set_name = resolve_default_set(ui, b["default_set"])
                leave_bu_form(ui)
                open_data_access(ui)
                with ui.step("check roles and user (screen)"):
                    ub = dict(REQUIRED_USER)
                    user = pick_user(ui, ub, da_rows)
                    others = [user] + [u for u in REQUIRED_USER.values() if u and u != user]
                    req = []
                    for r in REQUIRED_ROLES:
                        rn = check_role_name(ui, r)
                        req.append((rn, role_code(ui, others, rn, da_rows)))
            # extra access: checked before anything is created (the page checked it already)
            extra = b.get("extra_plan")
            if extra is None and b.get("extra") and rest_ok:
                try:
                    extra = plan_extras(b, user, rest_access_rows(), load_mapping)
                except ExtraAccessRefused as e:
                    oracle.fail(f"{b['name']}: {e.text}" + (f" Roles that can: {', '.join(e.valid)}."
                                                             if e.valid else ""))
            da_row = dict(DA_FIXED, UserName=user, BuName=b["name"], StartDateActive=today or "")
            item = lambda u, rn, c: {"b": b, "user": u, "role_name": rn, "code": c,
                                     "da_row": dict(da_row, UserName=u, RoleName=c)}
            p = {"b": b, "existing": existing, "user": user, "loc_name": loc_name, "loc_id": loc_id,
                 "set_name": set_name,
                 "required": [item(user, rn, c) for rn, c in req],
                 "extra": [item(e["user"], e["role_name"], e["code"]) for e in (extra or [])
                           if (e["user"], e["code"]) not in {(user, c) for _, c in req}],
                 "extra_wanted": extra or [], "extra_no_rest": bool(b.get("extra")) and not rest_ok,
                 "had": [it for it in [item(user, rn, c) for rn, c in req] if any(is_mine(r, [it]) for r in on_bu)]}
            if not existing:
                p["bu_row"] = dict(BU_FIXED, Name=b["name"], DefaultSetCode=set_code,
                                   InternalLocationCode=loc_code, LocationSetCode=loc_set,
                                   Status="A" if b["active"] else "I")
                m = b.get("manager_entry")
                if m:                        # the manager columns Oracle writes (2026-10-26)
                    p["bu_row"].update(ManagerListName=m["name"], PersonNumber=m["person_number"],
                                       FirstName=m["first"], LastName=m["last"], MiddleNames="",
                                       EffectiveStartDate3=m["start"], EffectiveEndDate3=m["end"])
                p["manager_id"] = m["person_id"] if m else None
            plans.append(p)
            if found is not None:
                found.setdefault(b["name"], {}).update(name=b["name"], existing=existing, loc_name=loc_name,
                                                       screens=screen)
            print(f"  plan: " + ("" if existing else
                                 f"step 1 BU {b['name']} (location {loc_code}, default set {set_code}, "
                                 f"{'active' if b['active'] else 'inactive'}) by export/import; ")
                  + "required access " + ", ".join(f"{user} / {rn} ({c})" for rn, c in req)
                  + f" by {'REST' if rest_ok and not args.fallback else 'export/import'}"
                  + ("; then extra access " + ", ".join(f"{x['user']} / {x['role_name']}" for x in p["extra"])
                     if p["extra"] else ""))

        if args.check:
            print("\nChecking the export/import screens (read-only) ...")
            with ui.step("export/import screens of both tasks"):
                ui.setup.check_actions(BU_TASK, BU_AREA, OFFERING)
                ui.setup.check_actions(DA_TASK, DA_AREA, OFFERING)
            with ui.step("Create Order Business Unit list (fresh app session)"):
                options = create_order_fresh(ui)
            print(f"\nCreate Order Business Unit list (read-only, without the cached app session): "
                  f"{len(options)} BUs: {', '.join(options)}")
            for name in [b["name"] for b in units]:
                print(f"  {name}: {'already in' if name in options else 'not yet in'} "
                      "the Create Order list")
            print("Check passed: REST lists read (GET only), BU export done, screens opened and "
                  "left with Cancel; nothing imported, created or saved.")
            oracle.cleanup_work_dir()
            return
        if not plans:
            print("Nothing to create.")
            oracle.cleanup_work_dir()
            return

        # ---- step 1: business units (export/import: REST cannot create a business unit)
        new = [p for p in plans if not p["existing"]]
        if new:
            new_names = {p["b"]["name"] for p in new}
            files = bu_before or load_template()
            if files is None:                # first run on this PC: one export for the headers
                with phase("reading_business_units", 30, "Reading Oracle's business units"):
                    before_export()
                files = bu_before
            zip1 = build_only_new(files, BU_CSV, [p["bu_row"] for p in new], work / "import_business_units.zip")
            with phase("creating", 40, "Creating the business unit") as ph:
                print(f"\nStep 1 (route: export/import): importing {len(new)} business unit row(s) "
                      f"({zip1.name}, only new rows) ...")
                if rest_ok:
                    # 2026-10-26: Oracle's Setup task process (as bu_batch.py, proven there), which gives
                    # Oracle's result and log: a refused row stops with Oracle's reason at once instead
                    # of a 6-minute wait for a business unit that will never show up.
                    import bu_batch
                    ph.sub("Sending the new business unit to Oracle")
                    status, process, texts = bu_batch.send(zip1.read_bytes())
                    if status != "COMPLETED":
                        fails = bu_batch.log_failures(texts)
                        group = bu_batch.group_refusal(texts)
                        why = "; ".join(r for f in fails for r in f["reasons"]) or group or f"it ended {status}"
                        missing = [p["b"]["name"] for p in new if not rest_bu(p["b"]["name"])]
                        if missing:
                            oracle.fail(f"Oracle didn't save the business unit {', '.join(missing)}: {why}. Nothing "
                                        "of it was saved and no access was given.")
                    ph.state = ("The business unit was sent to Oracle but didn't show up in time; no access "
                                "was given yet. If Oracle still finishes it, running the same request again "
                                "adds only the access that is missing.")
                    ph.sub("Waiting for Oracle to finish it")
                    hits = {}
                    while True:
                        for p in new:
                            n = p["b"]["name"]
                            if n not in hits:
                                try:
                                    h = rest_bu(n)
                                except RestUnavailable as e:
                                    print(f"  NOTE  quick read failed, trying again: {str(e)[:200]}")
                                    h = []
                                if h:
                                    hits[n] = h
                        if len(hits) == len(new):
                            break
                        ph.check()
                        time.sleep(POLL_EVERY)
                    print(f"  OK    Oracle shows the new business unit(s) (import {process})")
                else:
                    ui.setup.import_csv(BU_TASK, BU_AREA, zip1, OFFERING)
            with phase("checking_bu", 50, "Checking the business unit") as ph:
                ok1 = True
                for p in new:
                    n = p["b"]["name"]
                    if rest_ok:
                        h = rest_bu(n)
                        good = len(h) == 1 and h[0].get("ActiveFlag") is p["b"]["active"] and \
                            (h[0].get("LocationId") or None) == p["loc_id"] and                             int(h[0].get("ManagerId") or 0) == (p.get("manager_id") or 0)
                        print(f"  {'OK  ' if good else 'FAIL'}  {n} (REST GET): {h[0] if h else 'not found'}")
                        ok1 &= good
                        if found is not None:
                            found.setdefault(n, {})["business_unit"] = dict(h[0]) if h else {}
                if screen or not rest_ok:
                    # "Checking the business unit's details": a second export and the screen
                    # (418 s on 2026-10-22), only with the screen check or without REST
                    ph.sub("Reading its details from Oracle's setup data")
                    print("Exporting Manage Business Unit (after) to verify ...")
                    bu_after = read_zip(ui.setup.export_csv(BU_TASK, BU_AREA, OFFERING)[0])
                    got = {r["Name"]: r for r in dicts(need(bu_after, BU_CSV, BU_TASK))}
                    for p in new:
                        row, want = got.get(p["b"]["name"]), p["bu_row"]
                        if found is not None and row:
                            found.setdefault(p["b"]["name"], {}).setdefault("business_unit", {}).update(row)
                        if row is None:
                            print(f"  FAIL  {p['b']['name']}: not in the after-export")
                            ok1 = False
                            continue
                        diffs = {k: (row.get(k), v) for k, v in want.items() if row.get(k) != v}
                        print(f"  {'FAIL' if diffs else 'OK  '}  {p['b']['name']} (export): "
                              + (f"differs (got, expected) {diffs}" if diffs else
                                 f"default set {row['DefaultSetCode']}, location {row['InternalLocationCode']}, "
                                 f"status {row['Status']}, organization code {row['OrganizationCode'][:40]}"))
                        ok1 &= not diffs
                    ok1 &= compare_existing(bu_before, bu_after, ("Name", "FUN_BUSINESS_UNIT.Name", "ClientBuName"),
                                            new_names, BU_TASK)
                    ph.sub("Looking at it on Oracle's screen")
                    for p in new:
                        rows, _ = screen_bu(ui, p["b"]["name"])
                        good = bool(rows) and p["loc_name"] in rows[0]
                        print(f"  {'OK  ' if good else 'FAIL'}  on screen (Manage Business Units): {rows[:1]}")
                        ok1 &= good
            if not ok1:
                oracle.fail("Step 1 (business unit) verification failed - see FAIL lines. No access "
                            "was given. The business unit row(s) may exist now; a rerun adds only "
                            "what is missing.")
        if found is not None:
            for p in plans:
                if p["existing"]:
                    found.setdefault(p["b"]["name"], {})["business_unit"] = \
                        dict((existing_rest.get(p["b"]["name"]) or rest_bu(p["b"]["name"]) or [{}])[0])

        # ---- step 2: the required access, one role after the other (always, never replaced)
        routes = []
        for i, role in enumerate(REQUIRED_ROLES):
            key = re.sub(r"\W+", "_", role.lower())
            items = [p["required"][i] for p in plans]
            had = {id(it) for p, it in zip(plans, items) if any(h["code"] == it["code"] for h in p["had"])}
            with phase(f"access_{key}", 60 + 10 * i, f"Giving {role} access",
                       state=f"The business unit is there; {role} access may be missing. Running the same "
                             "request again adds only what is missing.") as ph:
                ok, route, _ = add_access(ui, work, args, items, rest_ok, found, f"required:{role}",
                                          f"Step 2 ({role})", deep=screen, ph=ph)
            routes.append(f"{role} {route}")
            if not ok:
                oracle.fail(f"{role} access verification failed - see FAIL lines above. The business "
                            "unit is there; a rerun adds only what is missing.")
            for p, it in zip(plans, items):
                if found is not None:
                    f = found.setdefault(p["b"]["name"], {})
                    f.setdefault("required", []).append(
                        {"role": it["role_name"], "user": it["user"],
                         "status": "already there" if id(it) in had else "added",
                         "row": f.get(f"required:{role}")})
            step(f"access_{key}_done", 65 + 10 * i, f"{role} access: done")

        # ---- step 3: Oracle's access cache, the shared list (and Create Order with the screen check)
        step("verifying", 85, "Checking the result")
        options = None
        if screen:
            with phase("create_order", 88, "Checking the Create Order screen") as ph:
                options = create_order_fresh(ui)
                missing = [p["b"]["name"] for p in plans if p["b"]["name"] not in options]
                if missing:
                    # last resort only: the fresh app session should already show it
                    ph.sub("Waiting for you to sign in to Oracle again")
                    again = fresh_signin_and_recheck(ui, missing)
                    if again is not None:
                        options = again
        with phase("pricing", 90, "Checking that it shows for pricing"):
            for p in plans:
                name = p["b"]["name"]
                good = None if options is None else name in options
                if good is not None:
                    print(f"  {'OK  ' if good else 'NOTE'}  Create Order Business Unit list shows {name}"
                          + ("" if good else f" - not yet: {FRESH_SIGNIN_TEXT}"))
                # not a failure of this folder: the business unit and its access are verified above
                visible = rest_ok and all(wait_for_pricing(it) for it in p["required"])
                ready = visible and good is not False
                registry_add(name, "ready" if ready else "pending", "" if ready else FRESH_SIGNIN_TEXT,
                             p["user"], [it["role_name"] for it in p["required"]])
                if found is not None:
                    found.setdefault(name, {}).update(create_order=good, pending=not ready)

        # ---- step 4: extra access (optional, last; a rejection is a note, not a failure)
        for p in plans:
            if not (p["extra_wanted"] or p["extra_no_rest"]):
                continue
            extra_out = []
            req_codes = {(it["user"], it["code"]) for it in p["required"]}
            for e in p["extra_wanted"]:
                if (e["user"], e["code"]) in req_codes:
                    extra_out.append({"role": e["role_name"], "user": e["user"], "status": "already there",
                                      "reason": "it is part of the required access"})
            if p["extra_no_rest"]:
                extra_out += [{"role": e["role"], "user": e["user"] or p["user"], "status": "not added",
                               "reason": "Oracle didn't allow adding it automatically right now"}
                              for e in p["b"]["extra"]]
            with phase("extra_access", 95, "Adding the extra access",
                       state="The business unit and its required access are ready; the extra access may "
                             "be missing.") as ph:
                for it in p["extra"]:
                    had = any(is_mine(r, [it]) for r in rest_access_on(it["b"]["name"], it["user"]))
                    try:
                        ok, route, reason = add_access(ui, work, args, [it], rest_ok, found,
                                                       f"extra:{it['code']}", f"Extra access ({it['role_name']})",
                                                       tolerant=True, deep=screen, ph=ph)
                    except StepTimeout:
                        raise
                    except Exception as e:  # noqa: BLE001 - the required part is done; this is only a note
                        ok, route, reason = False, "not checked", "Oracle couldn't be checked for it"
                        print(f"  NOTE  extra access {it['role_name']}: {type(e).__name__}: {str(e)[:300]}")
                    extra_out.append({"role": it["role_name"], "user": it["user"],
                                      "status": ("already there" if had else "added") if ok else "not added",
                                      "reason": "" if ok else reason,
                                      "row": (found or {}).get(p["b"]["name"], {}).get(f"extra:{it['code']}")})
                    routes.append(f"extra {it['role_name']} {route}")
            if found is not None:
                found.setdefault(p["b"]["name"], {})["extra"] = extra_out
            for x in extra_out:
                print(f"  {'OK  ' if x['status'] != 'not added' else 'NOTE'}  extra access {x['user']} / "
                      f"{x['role']}: {x['status']}" + (f" ({x['reason']})" if x["reason"] else ""))
        results += [(p["b"]["name"], ("existing business unit, " if p["existing"] else
                                      "step 1 export/import, ") + "; ".join(routes) + ": verified"
                     + ("" if screen else " (screen checks not run)"))
                    for p in plans]
    finally:
        ui.close()

    print("\n" + "\n".join(f"{n}: {s}" for n, s in results))
    print(f"Whole run: {elapsed_text(time.time() - t_run)}")
    oracle.cleanup_work_dir()
    return results


if __name__ == "__main__":
    main()
