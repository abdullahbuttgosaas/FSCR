"""Create payment terms from terms.json through the Oracle UI (Playwright), then verify.

Route: Setup and Maintenance > Payables > Manage Payment Terms > Actions >
Export / Import CSV File, driven by common/browser.py (no REST). Uses the sign-in
saved by common/login_once.py; the only manual step is that sign-in.

Every field of Oracle's Create Payment Terms screen (2026-10-25): header (name, from / to
date, description, cutoff day, rank), installments (percent or amount; days, fixed date,
day of month + months ahead, or calendar), up to three discounts per installment (percent;
days, or day of month + months ahead), and any number of reference data sets.

Steps: rules checked first (no Oracle) -> Oracle's lists when needed (today, calendars, set
codes from Create Payment Terms, left with Cancel) -> fresh export -> skip terms that already
exist (exact name: capitals and spaces count) -> add the new terms' rows to every file that
holds terms (row layout learned from an existing user-created term), keeping every existing
row and every file once -> import -> second fresh export -> check the new terms and that
existing terms are unchanged; says which terms were saved and which were not.

Temporary files go in "Payment Terms/_work/": deleted after a verified success,
kept after any failure (with screenshots).

  python "Payment Terms/browser_flow.py"             # full run (headless)
  python "Payment Terms/browser_flow.py" --check     # read-only: screens + Oracle's today, no export
  python "Payment Terms/browser_flow.py" --dry-run   # export + build import zip, no import
  python "Payment Terms/browser_flow.py" --headed    # same, with a visible browser
  python "Payment Terms/browser_flow.py" --plan [FILE or JSON]   # read-only: rules, lists, existing names

Page interface (root CLAUDE.md > Page interface, common/page.py), one term per run:
  python "Payment Terms/browser_flow.py" --spec
  python "Payment Terms/browser_flow.py" --options set_assignments.set | installments.calendar
  python "Payment Terms/browser_flow.py" --run '{"name": "X", "from_date": "today", "installments": [...]}'
"""
import argparse
import csv
import re
import io
import json
import random
import sys
import time
import zipfile
from datetime import date, timedelta
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import browser, oracle, page  # noqa: E402
from classic_setup import Setup, ImportNotClean  # noqa: E402  (this folder's own layout-aware steps)

TASK = "Manage Payment Terms"
AREA = "Payables"
OFFERING = "Financials"
HEADER, LINE, SUBS, TRANS = ("AP_TERM_HEADER.csv", "AP_TERM_LINE.csv",
                             "AP_TERM_SUBSCRIPTION.csv", "AP_TERM_HEADER_TRANSLATION.csv")
PARENT = "AP_TERM_HEADER.Name"
WHO = ("LastUpdateDate", "LastUpdatedBy", "CreationDate", "CreatedBy", "LastUpdateLogin")
SEED_USER = "SEED_DATA_FROM_APPLICATION"
TODAY = "today"   # request word: Oracle's today minus one day (see CLAUDE.md > Dates)
NAME_MAX = 50     # Oracle's Name field holds 50 characters (seen on the screen 2026-10-25)
DESC_MAX = 240    # see CLAUDE.md > Field rules (proven limit)
MAX_DISCOUNTS = 3
STYLES = (("days", "Days"), ("fixed_date", "Fixed Date"), ("day_of_month", "Day of Month"),
          ("calendar", "Calendar"))
ORDINAL = ("First", "Second", "Third")


# ---------------------------------------------------------------- requirements (no Oracle)

class Rules:
    """Collects every problem of a request in plain words (all at once). Each problem:
    {"key": request key, "row": installment number or None, "text": ...}."""

    def __init__(self):
        self.problems = []

    def bad(self, key, text, row=None):
        self.problems.append({"key": key, "row": row, "text": text})

    def number(self, v, key, label, lo=None, hi=None, whole=False, row=None):
        """The value as export text ("30", "33.333"), "" when empty, None when wrong."""
        if v is None or v == "":
            return ""
        if isinstance(v, bool):
            self.bad(key, f"{label} must be a number.", row)
            return None
        try:
            n = float(v)
        except (TypeError, ValueError):
            self.bad(key, f"{label} must be a number; it says '{v}'.", row)
            return None
        if n != n or n in (float("inf"), float("-inf")):      # "nan" / "inf" pass float() (2026-10-26)
            self.bad(key, f"{label} must be a number; it says '{v}'.", row)
            return None
        if whole and not n.is_integer():
            self.bad(key, f"{label} must be a whole number; it says '{v}'.", row)
            return None
        if (lo is not None and n < lo) or (hi is not None and n > hi):
            self.bad(key, f"{label} must be " + (f"between {lo} and {hi}" if hi is not None else f"{lo} or more")
                     + f"; it says '{v}'.", row)
            return None
        return str(int(n)) if n.is_integer() else repr(n).rstrip("0").rstrip(".")

    def day(self, v, key, label, row=None, required=False):
        """A date as export text YYYY/MM/DD, "today", "" when empty, None when wrong."""
        if v in (None, ""):
            if required:
                self.bad(key, f"{label} is required.", row)
            return ""
        if str(v).strip().lower() == TODAY:
            return TODAY   # resolved later from Oracle's own date
        try:
            return date.fromisoformat(str(v).strip()).strftime("%Y/%m/%d")
        except ValueError:
            self.bad(key, f"{label} must be a date written as YYYY-MM-DD; it says '{v}'.", row)
            return None

    def text(self, v, key, label, maxlen, required=False):
        if v in (None, ""):
            if required:
                self.bad(key, f"{label} is required.")
            return ""
        if not isinstance(v, str):
            self.bad(key, f"{label} must be text.")
            return None
        if v != v.strip():
            self.bad(key, f"{label} '{v}' starts or ends with a space; remove it (Oracle keeps spaces, so "
                          "'Net 30 ' would be a different term from 'Net 30').")
            return None
        if len(v) > maxlen:
            self.bad(key, f"{label} can be at most {maxlen} characters; it has {len(v)}.")
            return None
        return v


def as_term(t):
    """A page request (one installment row holds its three discounts as discount_*,
    discount2_*, discount3_* and set rows as {"set": code}) -> the request file's shape.
    A request file term passes unchanged."""
    t = dict(t)
    rows = []
    for r in t.get("installments") or []:
        r = dict(r) if isinstance(r, dict) else r
        if isinstance(r, dict) and "discounts" not in r:
            ds = []
            for i, pre in enumerate(("discount", "discount2", "discount3")):
                d = {k: r.pop(f"{pre}_{k}") for k in ("percent", "days", "day_of_month", "months_ahead")
                     if f"{pre}_{k}" in r}
                if d:
                    ds.append(dict(d, _n=i + 1))
            if ds:
                r["discounts"] = ds
        rows.append(r)
    if "installments" in t:
        t["installments"] = rows
    t["set_assignments"] = [s["set"] if isinstance(s, dict) else s for s in t.get("set_assignments") or []]
    return t


def check_term(t, rules):
    """Every rule that needs no Oracle, for one term (request file shape). Returns the term
    with export-format values, or None when it has problems (all are in rules.problems)."""
    start_n = len(rules.problems)
    name = rules.text(t.get("name"), "name", "Name", NAME_MAX, required=True)
    known = {"name", "from_date", "to_date", "description", "cutoff_day", "rank", "installments",
             "set_assignments"}
    for k in set(t) - known:
        rules.bad(k, f"'{k}' is not a payment term field.")
    start = rules.day(t.get("from_date"), "from_date", "From Date", required=True)
    end = rules.day(t.get("to_date"), "to_date", "To Date")
    if start and end and TODAY not in (start, end) and end < start:
        rules.bad("to_date", "To Date is before From Date.")
    term = {"name": name,
            "description": rules.text(t.get("description"), "description", "Item Description", DESC_MAX),
            "from_date": start, "to_date": end,
            "cutoff_day": rules.number(t.get("cutoff_day"), "cutoff_day", "Cutoff Day", 1, 31, whole=True),
            "rank": rules.number(t.get("rank"), "rank", "Rank", 0, None, whole=True)}
    inst = t.get("installments")
    if not isinstance(inst, list) or not inst:
        rules.bad("installments", "At least one installment is required.")
        inst = []
    lines, kinds = [], []
    for i, n in enumerate(inst, 1):
        if not isinstance(n, dict):
            rules.bad("installments", f"Installment {i} must be a row of values.", i)
            continue
        lines.append(check_line(n, i, rules, kinds))
    if kinds and all(lines):
        if set(kinds) == {"percent", "amount"}:
            rules.bad("installments", "A payment term is either all percent or all amount: you must either enter "
                      "a percentage due or an amount due, not both (Oracle AP-810315).")
        elif kinds[0] == "percent":
            total = sum(float(l["DuePercent"]) for l in lines)
            if abs(total - 100) > 1e-9:
                rules.bad("installments", f"The installments add up to {total:g}%; the total percentage for all "
                          "lines must equal 100% (Oracle AP-810270).")
        elif float(lines[-1]["DueAmount"]) != 0:
            rules.bad("installments", f"An amount term's last installment must have Amount Due 0 (it has "
                      f"{lines[-1]['DueAmount']}): Oracle AP-810272.", len(lines))
    sets = t.get("set_assignments") or []
    if not isinstance(sets, list):
        rules.bad("set_assignments", "Set assignments must be a list of set codes.")
        sets = []
    sets = [str(s).strip() for s in sets]
    for i, s in enumerate(sets):
        if s in sets[:i]:
            rules.bad("set_assignments", f"Set {s} is listed twice.")
    term.update(lines=lines, sets=sets)
    return term if len(rules.problems) == start_n else None


def check_line(n, i, rules, kinds):
    """One installment: percent or amount, ONE way to set its due date, up to three discounts."""
    w = f"Installment {i}: "
    known = {"due_percent", "due_amount", "days", "fixed_date", "day_of_month", "months_ahead", "calendar",
             "discounts"}
    for k in set(n) - known:
        rules.bad("installments", f"{w}'{k}' is not an installment field.", i)
    pct = rules.number(n.get("due_percent"), "installments", w + "Due (%)", 0, 100, row=i)
    amt = rules.number(n.get("due_amount"), "installments", w + "Amount Due", 0, None, row=i)
    if pct and amt:
        rules.bad("installments", w + "enter Due (%) or Amount Due, not both (Oracle AP-810315).", i)
    elif not pct and not amt and pct is not None and amt is not None:
        rules.bad("installments", w + "Due (%) or Amount Due is required.", i)
    elif pct or amt:
        kinds.append("percent" if pct else "amount")
    line = {"SequenceNum": str(i), "DuePercent": pct or "", "DueAmount": amt or "",
            "DueDays": rules.number(n.get("days"), "installments", w + "Days", 0, None, whole=True, row=i),
            "FixedDate": rules.day(n.get("fixed_date"), "installments", w + "Fixed Date", row=i),
            "DueDayOfMonth": rules.number(n.get("day_of_month"), "installments", w + "Day of Month", 1, 31,
                                          whole=True, row=i),
            "DueMonthsForward": rules.number(n.get("months_ahead"), "installments", w + "Months Ahead", 0, None,
                                             whole=True, row=i),
            "Calendar": str(n.get("calendar") or "").strip()}
    if line["FixedDate"] == TODAY:
        rules.bad("installments", w + "Fixed Date must be a date, not 'today'.", i)
    if line["DueMonthsForward"] and not line["DueDayOfMonth"]:
        rules.bad("installments", w + "Months Ahead only works with Day of Month.", i)
    if line["DueDayOfMonth"] and line["DueMonthsForward"] == "":
        # proven 2026-10-26 (ZZ_TEST_PT_6142_DOM_NOMA): Oracle refuses the term at save with "You must enter months
        # ahead because you entered a due day of the month or discount day of the month."; the screen says nothing
        rules.bad("installments", w + f"Day of Month {line['DueDayOfMonth']} needs Months Ahead too: add Months "
                  "Ahead (0 means the same month, 1 the next month).", i)
    used = [label for key, label in STYLES if n.get(key) not in (None, "")]
    if len(used) != 1:
        rules.bad("installments", w + ("give one way to set the due date: Days, Fixed Date, Day of Month "
                                       "(with Months Ahead), or Calendar." if not used else
                                       f"use one way to set the due date, not {' and '.join(used)}."), i)
    ds = n.get("discounts") or []
    if not isinstance(ds, list) or len(ds) > MAX_DISCOUNTS:
        rules.bad("installments", w + "at most three discounts.", i)
        ds = []
    prev = None
    for k, d in enumerate(ds, 1):
        sfx = "" if k == 1 else str(k)
        pos = d.get("_n", k) if isinstance(d, dict) else k
        label = f"{w}{ORDINAL[pos - 1]} Discount"
        if pos != k:
            rules.bad("installments", f"{label} needs the {ORDINAL[k - 1].lower()} discount first.", i)
        d = {x: v for x, v in (d.items() if isinstance(d, dict) else []) if x != "_n"}
        dp = rules.number(d.get("percent"), "installments", label + " (%)", 0, 100, row=i)
        dd = rules.number(d.get("days"), "installments", label + " Days", 0, None, whole=True, row=i)
        dm = rules.number(d.get("day_of_month"), "installments", label + " Day of Month", 1, 31, whole=True, row=i)
        da = rules.number(d.get("months_ahead"), "installments", label + " Months Ahead", 0, None, whole=True, row=i)
        if not dp and dp is not None:
            rules.bad("installments", f"{label}: the discount percentage is required when its days or day of "
                      "month are given (Oracle AP-810447).", i)
        if dp and float(dp) <= 0:
            # proven 2026-10-26 (ZZ_TEST_PT_6142_DISC0): Oracle refused a 0% discount, "You must enter a positive number."
            rules.bad("installments", f"{label}: the discount percentage must be more than 0 (Oracle: \"You must "
                      "enter a positive number\"); leave the whole discount empty for none.", i)
        if da and not dm:
            rules.bad("installments", f"{label}: Months Ahead only works with Day of Month.", i)
        if dm and da == "":
            # proven 2026-10-26 (ZZ_TEST_PT_6142_DISC_NOMA): the same Oracle refusal as the due Day of Month
            rules.bad("installments", f"{label}: Day of Month {dm} needs Months Ahead too: add Months Ahead (0 "
                      "means the same month, 1 the next month).", i)
        if dd and dm:
            rules.bad("installments", f"{label}: use Days or Day of Month, not both.", i)
        if not dd and not dm and dd is not None and dm is not None:
            rules.bad("installments", f"{label}: give its Days or its Day of Month.", i)
        if prev and dp and prev[0] and float(dp) >= float(prev[0]):
            rules.bad("installments", f"{label} ({dp}%) must be lower than the one before it ({prev[0]}%): "
                      f"Oracle {'AP-810459' if k == 2 else 'AP-810454'}.", i)
        if prev and dd and prev[1] and int(dd) <= int(prev[1]):
            rules.bad("installments", f"{label} days ({dd}) must come after the one before it ({prev[1]} days): "
                      "Oracle AP-810418.", i)
        prev = (dp, dd)
        line.update({f"DiscountPercent{sfx}": dp or "", f"DiscountDays{sfx}": dd or "",
                     f"DiscountDayOfMonth{sfx}": dm or "", f"DiscountMonthsForward{sfx}": da or ""})
    return line if all(v is not None for v in line.values()) else None


def list_problems(term, lists, rules):
    """Values that must be in Oracle's lists: Calendar and set codes."""
    for ln in term["lines"]:
        cal = ln.get("Calendar")
        if cal and cal not in lists["calendars"]:
            rules.bad("installments", f"Installment {ln['SequenceNum']}: Oracle has no calendar '{cal}'. "
                      f"It has: {', '.join(lists['calendars'])}.", int(ln["SequenceNum"]))
    for s in term["sets"]:
        if s not in lists["sets"]:
            rules.bad("set_assignments", f"Oracle has no set code '{s}'. Pick one of: {', '.join(lists['sets'])}.")


def parse_requirements(data, path, rules=None):
    """The request (file contents or a page request) -> normalised terms. With `rules`
    given, problems are collected there and the bad terms come back as None; without it,
    any problem stops the run listing every problem."""
    collect = rules is not None
    rules = rules or Rules()
    raw = data.get("terms") if isinstance(data, dict) else None
    if not isinstance(raw, list) or not raw:
        oracle.fail(f"{path} must contain a non-empty 'terms' list")
    out, seen = [], set()
    for t in raw:
        t = as_term(t) if isinstance(t, dict) else {}
        name = t.get("name")
        if name in seen:
            rules.bad("name", f"The name '{name}' is listed twice; each name can be there only once.")
        seen.add(name)
        out.append(check_term(t, rules))
    if rules.problems and not collect:
        oracle.fail("The request has problems:\n  " + "\n  ".join(p["text"] for p in rules.problems))
    return out


# ---------------------------------------------------------------- Oracle's today and lists (read-only)

LISTS = {}       # cached in this process: {"today", "calendars", "sets"}


def oracle_today(ui):
    """Oracle's today = the From Date that Create Payment Terms fills in by itself.
    Read-only: the Create page is left with Cancel."""
    return screen_lists(ui, lists=False)["today"]


def screen_lists(ui, lists=True):
    """Read-only look at Create Payment Terms: Oracle's today (the From Date it fills in) and,
    with lists=True, the Calendar and Set Code drop-downs (an installment row and a set row
    are added to the unsaved form; rows need a name, so a random ZZ_TEST_PT_ name is typed).
    Nothing is saved: Cancel, and Yes to leave without saving."""
    if LISTS.get("today") and (not lists or LISTS.get("calendars")):
        return LISTS
    page = ui.page
    ui.setup.open_task(TASK, AREA, OFFERING)
    # Manage Payment Terms' own filter row has an (empty) "From Date" box too, so the form counts as open only when
    # a From Date shows a value: Oracle's default, filled a moment after the field shows (2026-10-26)
    dates = page.get_by_label("From Date", exact=True)

    def filled():
        for i in range(dates.count()):
            f = dates.nth(i)
            try:
                if f.is_visible() and f.input_value().strip():
                    return page.locator(f"[id='{f.get_attribute('id')}']")
            except Exception:  # noqa: BLE001 - redrawn while read: look again
                pass
        return None
    got = {}

    def create(attempt):             # opens an empty form (nothing saved); a lost click is clicked again (2026-10-26)
        button = page.locator("[title='Create']:visible").first
        if attempt == 1 or button.count():
            ui.click(button, "Create" + (" (again)" if attempt > 1 else ""))
        ui.settle()

    def opened(timeout):
        end = time.time() + timeout / 1000
        while time.time() < end:
            got["field"] = filled()
            if got["field"] is not None:
                return True
            page.wait_for_timeout(500)
        return False
    ui.retry("Manage Payment Terms did not open Create Payment Terms with its default From Date", create, opened,
             wait=30000, last_wait=60000)
    field = got["field"]
    shown = field.input_value().strip()
    LISTS["today"] = ui.parse_screen_date(shown)
    ui.log(f"Oracle's today (Create Payment Terms default From Date {shown}): {LISTS['today'].isoformat()}")
    if lists:
        name = ui.field("Name")
        typed = f"ZZ_TEST_PT_LISTS_{random.randint(1000, 9999)}"      # never saved

        def fill(attempt):
            name.fill(typed)
            name.press("Tab")
            ui.settle()
            page.wait_for_timeout(1500)
            ui.close_messages()
        ui.retry("Create Payment Terms did not take the Name", fill,      # checked (2026-10-26)
                 lambda timeout: name.input_value().strip() == typed, wait=5000, last_wait=10000)
        adds = page.locator("[title='Add Row']:visible")
        cal = page.locator("select[id*=':ta1:'][id$='so1::content']:visible").first
        sets = page.locator("select[id*=':ta3:'][id$='so2::content']:visible").first

        def add_row(button, select, what):
            # rows of the unsaved form (nothing saved); Add Row again only while its row hasn't shown (2026-10-26)
            def act(attempt):
                if not select.count():
                    ui.click(button(), f"{what} Add Row (not saved)")
                ui.settle()
                page.wait_for_timeout(1500)
            ui.retry(f"Create Payment Terms did not add an {what} row", act,
                     lambda timeout: select.wait_for(timeout=timeout), wait=15000, last_wait=30000)

        def options(select, what):    # a list read before Oracle filled it is read again (2026-10-26)
            got = {"v": []}

            def filled(timeout):
                end = time.time() + timeout / 1000
                while True:
                    got["v"] = [o for o in ui.select_options(select) if o]
                    if got["v"] or time.time() > end:
                        return bool(got["v"])
                    page.wait_for_timeout(1000)
            ui.retry(f"{what} list stayed empty", lambda attempt: None, filled, wait=5000, last_wait=10000,
                     soft=True)
            return got["v"]
        add_row(lambda: adds.first, cal, "Installments")
        LISTS["calendars"] = options(cal, "Calendar")
        add_row(lambda: page.locator("[title='Add Row']:visible").last, sets, "Set Assignments")
        LISTS["sets"] = options(sets, "Set Code")
        ui.log(f"lists: {len(LISTS['calendars'])} calendars, {len(LISTS['sets'])} set codes")
    yes = page.get_by_role("button", name=re.compile(r"^Yes$"))

    def leave(attempt):              # Cancel and Yes save nothing; checked that the form closed (2026-10-26)
        if not (yes.count() and yes.first.is_visible()):
            ui.click(page.get_by_role("button", name=re.compile(r"^Cancel$")).first, "Cancel")
            ui.settle()
        try:
            yes.first.wait_for(timeout=5000)
        except Exception:
            pass
        if yes.count() and yes.first.is_visible():
            ui.click(yes.first, "Yes (leave without saving)")
            ui.settle()
    ui.retry("Create Payment Terms did not close without saving", leave,
             lambda timeout: field.wait_for(state="hidden", timeout=timeout), wait=20000, last_wait=40000)
    return LISTS


def needs_lists(terms):
    return any(t and (t["sets"] or any(l["Calendar"] for l in t["lines"])) for t in terms)


def resolve_today(terms, today):
    """Replace the word "today" by Oracle's today minus one day (export format)."""
    day = (today - timedelta(days=1)).strftime("%Y/%m/%d")
    for t in terms:
        for key in ("from_date", "to_date"):
            if t[key] == TODAY:
                t[key] = day
                print(f"  NOTE  {t['name']}: {key} \"today\" -> {day} (Oracle's today "
                      f"{today.isoformat()} minus one day)")
        if t["to_date"] and t["to_date"] < t["from_date"]:
            oracle.fail(f"term {t['name']}: to_date is before from_date")


def uses_today(terms):
    return any(TODAY in (t["from_date"], t["to_date"]) for t in terms)


# ---------------------------------------------------------------- files

def read_zip(path):
    z = zipfile.ZipFile(path)
    files = {}
    for n in z.namelist():
        data = z.read(n)
        if n.endswith(".csv"):
            text = data.decode("utf-8-sig")
            rows = list(csv.reader(io.StringIO(text)))
            files[n] = {"raw": data, "text": text, "header": rows[0], "rows": rows[1:]}
        else:
            files[n] = {"raw": data}
    for need in (HEADER, LINE, SUBS, TRANS):
        if need not in files:
            oracle.fail(f"Export {path.name} has no {need}; files: {sorted(files)}")
    return files


def as_dicts(f):
    return [dict(zip(f["header"], r)) for r in f["rows"]]


def term_names(files):
    """Names exactly as Oracle has them: capitals and spaces count ("PP payment term" and
    "PP Payment Term" are two terms in this pod)."""
    return {r[0] for r in files[HEADER]["rows"]}


def pick_template(files):
    """Most recently created user-made term: its rows show how UI-created terms look."""
    user = [r for r in as_dicts(files[HEADER]) if r.get("CreatedBy") != SEED_USER]
    if not user:
        oracle.fail("No user-created payment term in the export to learn the row layout from.")
    return max(user, key=lambda r: r.get("CreationDate", ""))["Name"]


def template_row(files, fname, tpl):
    rows = [r for r in as_dicts(files[fname]) if r[fname == HEADER and "Name" or PARENT] == tpl]
    return rows[0] if rows else None


def build_rows(files, term, tpl):
    """New rows per file: every column empty, then the template's who/fixed columns,
    then the requested values."""
    def blank(fname):
        return {c: "" for c in files[fname]["header"]}

    def who_from(fname, fallback_any=False):
        src = template_row(files, fname, tpl)
        if src is None and fallback_any:
            src = next((r for r in as_dicts(files[fname]) if r.get("CreatedBy") != SEED_USER), None)
        return {k: src[k] for k in WHO if src and k in src}

    th = template_row(files, HEADER, tpl)
    h = blank(HEADER)
    h.update(who_from(HEADER))
    h.update({"Name": term["name"], "EnabledFlag": th["EnabledFlag"], "Type": th["Type"],
              "StartDateActive": term["from_date"], "EndDateActive": term["to_date"],
              "DueCutoffDay": term["cutoff_day"], "Rank": term["rank"],
              "Description": term["description"]})
    lines = []
    for ln in term["lines"]:
        r = blank(LINE)
        r.update(who_from(LINE, fallback_any=True))
        r.update({k: v for k, v in ln.items() if k in r})
        r[PARENT] = term["name"]
        lines.append(r)
    tt = template_row(files, TRANS, tpl)
    tr = blank(TRANS)
    tr.update(who_from(TRANS))
    tr.update({PARENT: term["name"], "Name": term["name"], "Description": term["description"],
               "Language": tt["Language"] if tt else "US", "SourceLang": tt["SourceLang"] if tt else "US"})
    subs = []
    for code in term["sets"]:
        r = blank(SUBS)
        r.update(who_from(SUBS, fallback_any=True))
        r.update({PARENT: term["name"], "SetCode": code})
        subs.append(r)
    return {HEADER: [h], LINE: lines, TRANS: [tr], SUBS: subs}


def csv_line(header, row):
    buf = io.StringIO()
    csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n").writerow([row.get(c, "") for c in header])
    return buf.getvalue()


def build_import_zip(files, additions, path):
    """Every existing file once; existing rows byte-for-byte; new rows appended."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zo:
        for name, f in files.items():
            data = f["raw"]
            new = additions.get(name, [])
            if new:
                text = f["text"] if f["text"].endswith("\n") else f["text"] + "\n"
                data = (text + "".join(csv_line(f["header"], r) for r in new)).encode("utf-8")
            zo.writestr(name, data)
    return path


# ---------------------------------------------------------------- verify

def data_view(files, fname):
    """Rows without the who columns, as comparable tuples."""
    f = files[fname]
    idx = [i for i, c in enumerate(f["header"]) if c not in WHO]
    return {tuple(r[i] for i in idx) for r in f["rows"]}, idx


def same_value(got, want):
    """Oracle may write a number back differently ("2.50" for "2.5"); the meaning counts."""
    if got == want:
        return True
    try:
        return float(got) == float(want)
    except (TypeError, ValueError):
        return False


def verify(before, after, terms, additions_by_term, per=None):
    """Every new term's rows as built, and all existing rows unchanged. per (optional dict):
    filled with {term name: True/False} (a sheet run reports each term on its own)."""
    ok = True
    names_after = term_names(after)
    for term in terms:
        n = term["name"]
        before_ok = ok
        ok = True
        if n not in names_after:
            print(f"  FAIL  {n}: not in the export after import")
            ok = False
            if per is not None:
                per[n] = False
            ok = ok and before_ok
            continue
        for fname, rows in additions_by_term[n].items():
            hdr = after[fname]["header"]
            key = "Name" if fname == HEADER else PARENT
            got = [r for r in as_dicts(after[fname]) if r[key] == n]
            if len(got) != len(rows):
                print(f"  FAIL  {n}: {fname} has {len(got)} row(s), expected {len(rows)}")
                ok = False
                continue
            for want in rows:
                match = [g for g in got if all(same_value(g[c], want.get(c, "")) for c in hdr if c not in WHO)]
                if not match:
                    diff = {c: (got[0][c], want.get(c, "")) for c in hdr
                            if c not in WHO and not same_value(got[0][c], want.get(c, ""))}
                    print(f"  FAIL  {n}: {fname} differs (got, expected): {diff}")
                    ok = False
            if ok:
                print(f"  OK    {n}: {fname} ({len(rows)} row(s))")
        if per is not None:
            per[n] = ok
        ok = ok and before_ok
    new_names = {t["name"] for t in terms}
    for fname in (HEADER, LINE, TRANS, SUBS):
        key = 0
        old_rows = [r for r in before[fname]["rows"] if r[key] not in new_names]
        new_rows = [r for r in after[fname]["rows"] if r[key] not in new_names]
        if sorted(old_rows) == sorted(new_rows):
            print(f"  OK    existing rows unchanged in {fname} ({len(old_rows)})")
            continue
        b_data, idx = data_view(before, fname)
        a_data, _ = data_view(after, fname)
        b_data = {t for t in b_data if t[0] not in new_names}
        a_data = {t for t in a_data if t[0] not in new_names}
        if b_data == a_data:
            print(f"  NOTE  {fname}: only who/date columns of existing rows changed")
        else:
            print(f"  FAIL  {fname}: existing rows changed: {len(b_data - a_data)} removed/changed, "
                  f"{len(a_data - b_data)} new/changed")
            ok = False
    return ok


# ---------------------------------------------------------------- page interface

HERE = Path(__file__).resolve().parent
NUM = lambda key, label, ph: {"key": key, "label": label, "required": False, "type": "number", "placeholder": ph}
DISCOUNT_FIELDS = [f for i, (pre, word) in enumerate((("discount", "First"), ("discount2", "Second"),
                                                       ("discount3", "Third")))
                   for f in (NUM(f"{pre}_percent", f"{word} discount (percent)", ("2", "1", "0.5")[i]),
                             NUM(f"{pre}_days", f"{word} discount: paid within (days)", ("10", "20", "30")[i]),
                             NUM(f"{pre}_day_of_month", f"{word} discount: day of the month", "15"),
                             NUM(f"{pre}_months_ahead", f"{word} discount: months ahead", "0"))]
SPEC = {
    "title": "Create a payment term",
    "description": "Creates a payment term with its installments; an existing term is never changed.",
    "fields": [
        {"key": "name", "label": "Payment term name", "required": True, "type": "text",
         "placeholder": "Net 30", "default": None,
         "help": "Up to 50 characters. Capital and small letters count: 'Net 30' and 'net 30' are two terms."},
        {"key": "from_date", "label": "From date", "required": True, "type": "date",
         "placeholder": "2026-10-21", "default": None,
         "help": "'today' means Oracle's today minus one day."},
        {"key": "installments", "label": "Installments", "required": True, "type": "rows",
         "min_rows": 1, "add_label": "Add an installment", "row_label": "Installment",
         "help": "Each installment: a percent or an amount, and one way to set its due date. "
                 "Percents add up to 100; with amounts the last installment is 0.",
         "fields": [
             NUM("due_percent", "Percent due", "50"),
             NUM("due_amount", "Amount due", "500"),
             NUM("days", "Due after (days)", "30"),
             {"key": "fixed_date", "label": "Fixed due date", "required": False, "type": "date",
              "placeholder": "2026-12-31"},
             NUM("day_of_month", "Due on day of the month", "15"),
             NUM("months_ahead", "Months ahead", "1"),
             {"key": "calendar", "label": "Calendar", "required": False, "type": "pick",
              "placeholder": "AKPmt Calendar"},
         ] + DISCOUNT_FIELDS},
        {"key": "description", "label": "Description", "required": False, "type": "text",
         "placeholder": "Half in 30 days, half in 60", "default": None},
        {"key": "to_date", "label": "To date", "required": False, "type": "date",
         "placeholder": "2027-12-31", "default": None},
        {"key": "cutoff_day", "label": "Cutoff day of the month", "required": False,
         "type": "number", "placeholder": "25", "default": None},
        {"key": "rank", "label": "Rank", "required": False, "type": "number",
         "placeholder": "1", "default": None},
        {"key": "set_assignments", "label": "Reference data sets", "required": False,
         "type": "rows", "min_rows": 0, "add_label": "Add a set", "row_label": "Set",
         "fields": [{"key": "set", "label": "Set", "required": True, "type": "pick",
                     "placeholder": "COMMON"}]},
    ],
}
WHERE = "Setup and Maintenance > Financials > Payables > Manage Payment Terms, search for {name}"
# export column -> the page's key, for the result card (what Oracle shows now)
LINE_KEYS = [("SequenceNum", "sequence"), ("DuePercent", "due_percent"), ("DueAmount", "due_amount"),
             ("DueDays", "days"), ("FixedDate", "fixed_date"), ("DueDayOfMonth", "day_of_month"),
             ("DueMonthsForward", "months_ahead"), ("Calendar", "calendar")] + [
    (f"Discount{c}{s}", f"{p}_{k}") for s, p in (("", "discount"), ("2", "discount2"), ("3", "discount3"))
    for c, k in (("Percent", "percent"), ("Days", "days"), ("DayOfMonth", "day_of_month"),
                 ("MonthsForward", "months_ahead"))]


def options_for(key):
    """--options set_assignments.set: Oracle's reference data sets, read live through REST
    (setIdSetsLOV, GET only; the same 37 codes as the Set Code drop-down on Create Payment
    Terms, 2026-10-25). --options installments.calendar: the Calendar drop-down of Create
    Payment Terms (read-only screen look, about 40 s)."""
    oracle.check_environment()
    if key == "installments.calendar":
        return [{"value": c, "label": c} for c in lists_now()["calendars"]]
    if key != "set_assignments.set":
        raise page.PageError("FAILED", detail=f"no list for {key!r}")
    items = oracle.rest_items("setIdSetsLOV", limit=500)
    return [{"value": i["SetCode"], "label": i.get("SetName") or i["SetCode"]}
            for i in sorted(items, key=lambda i: i["SetCode"])]


def lists_now():
    """Oracle's today, calendars and set codes in their own short browser visit (cached)."""
    if not LISTS.get("calendars"):
        work = oracle.init_work_dir(HERE)
        had_files = any(work.iterdir())
        with browser.OracleUI(work, headless=True) as ui:
            ui.setup = Setup(ui)
            screen_lists(ui)
        if not had_files:
            oracle.cleanup_work_dir()
    return LISTS


def page_problems(rules):
    """Rules problems -> the page contract's problems (field names the rows field)."""
    return [{"field": p["key"], "problem": "invalid", "text": p["text"], **({"row": p["row"]} if p["row"] else {})}
            for p in rules.problems]


def run_request(request, progress):
    """--run: one payment term through the normal flow."""
    oracle.check_environment()
    browser.refuse_production()
    rules = Rules()
    terms = parse_requirements({"terms": [request]}, "page", rules)
    if rules.problems:
        raise page.PageError("INVALID_REQUEST", " ".join(p["text"] for p in rules.problems), page_problems(rules))
    name = request["name"]
    args = argparse.Namespace(check=False, dry_run=False, headed=False)
    found = {}
    # Every stop says what was saved (error.detail "saved", 2026-10-25): the after-export tells
    # whether the term got in, so the page's failed-only sheet never holds a saved term.
    messages, real_fail = [], oracle.fail

    def fail(message):
        messages.append(str(message))
        real_fail(message)
    oracle.fail = fail
    try:
        created = run_terms(args, terms, HERE, progress, found)
    except page.PageError:
        raise
    except (SystemExit, Exception) as e:  # noqa: BLE001 - every stop gets the saved state
        msg = messages[-1] if messages else f"{type(e).__name__}: {e}"
        got = found.get(name) or {}
        saved = ("yes" if got.get("saved") else
                 "no" if not found.get("_imported") or "Not saved: " + name in msg else "maybe")
        text = {"no": "Nothing was saved in Oracle.",
                "yes": f"The payment term {name} was saved in Oracle, but checking it didn't finish.",
                "maybe": f"The payment term {name} may have been saved in Oracle."}[saved]
        if saved == "no" and got.get("reason"):          # Oracle refused a value: the user changes it
            raise page.PageError("INVALID_REQUEST", f"Oracle refused the payment term: {got['reason']}. {text}",
                                 {"message": msg, "saved": "no", "registry_id": None})
        code = page._classify(msg)
        raise page.PageError(code, f"{page.ERRORS[code]} {text}", {"message": msg, "saved": saved, "registry_id": None})
    finally:
        oracle.fail = real_fail
    progress.step("done")
    return result_of(name, found.get(name, {}), skipped=not created)


def result_of(name, got, skipped):
    """The page's result for one term, from what the export shows (created or skipped)."""
    h = got.get("header") or {}
    shown = {"name": h.get("Name"), "from_date": h.get("StartDateActive"),
             "to_date": h.get("EndDateActive") or None, "description": h.get("Description") or None,
             "cutoff_day": h.get("DueCutoffDay") or None, "rank": h.get("Rank") or None,
             "installments": [{key: l[col] for col, key in LINE_KEYS if l.get(col)} for l in got.get("lines", [])],
             "sets": got.get("sets", [])}
    where = WHERE.format(name=h.get("Name") or name)
    if skipped:
        return {"text": f"The payment term {h.get('Name') or name} already exists in Oracle, so "
                        "nothing was changed.", "skipped": True, "created": shown, "where": where}
    n = len(shown["installments"])
    return {"text": f"Created the payment term {name} from {shown['from_date']} with {n} "
                    f"installment{'s' if n != 1 else ''}, and checked every value in Oracle.",
            "created": shown, "where": where}


ROW_KEYS = ("due_percent", "due_amount", "days", "fixed_date", "day_of_month", "months_ahead", "calendar")


def refusal_problems(req, why, ranks):
    """Oracle's import reason for one refused term -> the page's structured problems [{field, value, reason,
    suggestions, rows?, row?, where?}] for the decision panel (2026-10-26). The import log names the term, not
    the installment, so an installment value is found by the rule the reason states. [] when the reason names
    no value the user can change (the card then only quotes Oracle)."""
    t, out = (why or "").lower(), []
    rows = req.get("installments") if isinstance(req.get("installments"), list) else []
    blank = lambda v: v in (None, "")

    def row_problem(field, n, value, sugg):
        out.append({"field": field, "value": value, "reason": why, "text": why, "suggestions": sugg,
                    "rows": "installments", "row": n, "where": f"Installment {n}"})
    if "months ahead" in t:              # AP_ALL_ENTER_MONTH: a Day of Month without its Months Ahead
        for n, r in enumerate(rows, 1):
            for pre in ("", "discount_", "discount2_", "discount3_"):
                if not blank(r.get(pre + "day_of_month")) and blank(r.get(pre + "months_ahead")):
                    row_problem(pre + "months_ahead", n, r.get(pre + "months_ahead"), ["0", "1"])
    m = __import__("re").search(r"record with the value (.+?) already exists", why or "")
    if m and str(req.get("rank") or "").strip() and m.group(1).strip() == str(req.get("rank")).strip().split(".")[0]:
        rank = int(float(req["rank"]))
        free = [str(n) for n in range(rank + 1, rank + 1000) if str(n) not in ranks][:3]
        out.append({"field": "rank", "value": req.get("rank"), "reason": why, "text": why, "suggestions": free})
    if "positive number" in t:           # a 0% discount
        for n, r in enumerate(rows, 1):
            for pre in ("discount_", "discount2_", "discount3_"):
                if not blank(r.get(pre + "percent")) and float(r[pre + "percent"]) <= 0:
                    row_problem(pre + "percent", n, r.get(pre + "percent"), ["1", "2"])
    if "maximum length" in t:
        for key, n in (("name", NAME_MAX), ("description", DESC_MAX)):
            if key.lower() in t and isinstance(req.get(key), str):
                out.append({"field": key, "value": req[key], "reason": why, "text": why,
                            "suggestions": [req[key][:n].rstrip()]})
    return out


def run_batch_command(argv):
    """--run-batch '<JSON list of page requests>' (2026-10-25, the upload sheet): every term of
    an upload in ONE import. Progress lines as --run, then one result line: {"step": "result",
    "ok": all fine, "text", "results": [one --run style result per request, in order]}. A term
    with problems, already in Oracle, refused by Oracle (its reason from the import log) or
    saved but not matching gets its own result; the others go on. Only a stop that leaves no
    per-term answer (a screen or sign-in problem before the import) also gives a top-level
    "error" for the page's repair rules; a rerun skips what was saved (exact names)."""
    import contextlib
    out = sys.stdout
    progress = page.Progress(out)
    current = {"step": "reading"}
    real_step = progress.step

    def tracked(key, percent=None, text=None):
        current["step"] = key
        real_step(key, percent, text)
    progress.step = tracked

    def failed(code, text, saved, message=None, problems=None):
        return {"ok": False, "text": text,          # may quote Oracle's own reason, so no word check
                "error": {"code": code, "step": current["step"], "detail": {
                    "message": message, "saved": saved, "registry_id": None,
                    **({"problems": problems} if problems else {})}}}
    try:
        reqs = json.loads(argv[1] if len(argv) > 1 else "")
        if not isinstance(reqs, list) or not all(isinstance(r, dict) for r in reqs):
            raise ValueError("a list of requests is needed")
    except ValueError as e:
        print(json.dumps({"step": "result", "percent": 100, "ok": False, "text": "The request could not be read.",
                          "error": {"code": "INVALID_REQUEST", "step": "reading", "detail": str(e)}}), file=out)
        return 2
    top_error = None
    results = [None] * len(reqs)
    with contextlib.redirect_stdout(sys.stderr):
        progress.step("reading")
        good, names = [], []
        for i, req in enumerate(reqs):
            rules = Rules()
            term = parse_requirements({"terms": [req]}, "page", rules)[0]
            if req.get("name") in names:
                rules.bad("name", f"The name '{req.get('name')}' is listed twice in this upload.")
            names.append(req.get("name"))
            if rules.problems:
                results[i] = failed("INVALID_REQUEST", " ".join(p["text"] for p in rules.problems) +
                                    " Nothing was saved in Oracle.", "no", problems=page_problems(rules))
            else:
                good.append((i, term))
        if good:
            progress.step("checking")
            found, messages, real_fail = {}, [], oracle.fail

            def fail(message):
                messages.append(str(message))
                real_fail(message)
            oracle.fail = fail
            crash = None
            try:
                run_terms(argparse.Namespace(check=False, dry_run=False, headed=False), [t for _, t in good],
                          HERE, progress, found)
            except page.PageError as e:
                crash = (e.code, e.text, e.detail)
            except (SystemExit, Exception) as e:  # noqa: BLE001 - answered per term below
                msg = messages[-1] if messages else f"{type(e).__name__}: {e}"
                crash = (page._classify(msg), None, msg)
            finally:
                oracle.fail = real_fail
            for i, t in good:
                name, got = t["name"], found.get(t["name"], {})
                if got.get("skipped"):
                    results[i] = dict(result_of(name, got, skipped=True), ok=True)
                elif got.get("saved") and got.get("verified"):
                    results[i] = dict(result_of(name, got, skipped=False), ok=True)
                elif got.get("saved"):
                    results[i] = failed("VERIFY_FAILED", f"The payment term {name} was saved in Oracle, but not every "
                                        "value matches what was asked.", "yes", crash and str(crash[2]))
                elif got.get("reason") or found.get("_after"):
                    why = got.get("reason") or "it isn't there after the upload, and Oracle's log names no reason"
                    results[i] = failed("INVALID_REQUEST", f"Oracle refused the payment term {name}: {why}. Nothing "
                                        "was saved in Oracle.", "no", why,
                                        problems=refusal_problems(reqs[i], why, found.get("_ranks") or set()))
                else:
                    code, text, detail = crash or ("FAILED", None, None)
                    saved = "maybe" if found.get("_imported") else "no"
                    results[i] = failed(code, (text or page.ERRORS.get(code, page.ERRORS["FAILED"])) + " " +
                                        ("Nothing was saved in Oracle." if saved == "no" else
                                         f"The payment term {name} may have been saved in Oracle."), saved,
                                        detail if isinstance(detail, str) else json.dumps(detail))
            if crash and not found.get("_after"):     # no answer from Oracle for the terms: page repair rules
                top_error = {"code": crash[0], "step": current["step"],
                             "detail": crash[2] if isinstance(crash[2], (str, list)) else json.dumps(crash[2])}
        progress.step("done")
    made = sum(1 for r in results if r["ok"] and not r.get("skipped"))
    skipped = sum(1 for r in results if r.get("skipped"))
    bad = sum(1 for r in results if not r["ok"])
    text = (f"Created {made} of {len(results)} payment terms" + (f", {skipped} already there" if skipped else "")
            + (f", {bad} not created" if bad else "") + ".")
    line = {"step": "result", "percent": 100, "ok": not bad, "text": page.plain_check(text, "result"),
            "results": results}
    if top_error:
        line["error"] = top_error
    print(json.dumps(line, ensure_ascii=False), file=out)
    return 0 if not bad else 1


# ---------------------------------------------------------------- --plan (read-only)

def describe(term, today=None):
    """What Oracle will get for one checked term, in plain words (the preview's summary)."""
    def money(v):
        return f"{v}%" if v else ""

    def due(l):
        part = money(l["DuePercent"]) or f"amount {l['DueAmount']}"
        if l["DueDays"]:
            when = f"in {l['DueDays']} days"
        elif l["FixedDate"]:
            when = f"on {l['FixedDate'].replace('/', '-')}"
        elif l["DueDayOfMonth"]:
            when = (f"on day {l['DueDayOfMonth']}" + (f", {l['DueMonthsForward']} month(s) ahead"
                                                       if l["DueMonthsForward"] else ""))
        else:
            when = f"by {l['Calendar']}"
        discs = []
        for s in ("", "2", "3"):
            if l.get(f"DiscountPercent{s}"):
                d = l[f"DiscountPercent{s}"] + "% discount " + (f"within {l[f'DiscountDays{s}']} days"
                                                                if l.get(f"DiscountDays{s}") else
                                                                f"by day {l[f'DiscountDayOfMonth{s}']}" +
                                                                (f", {l[f'DiscountMonthsForward{s}']} month(s) ahead"
                                                                 if l.get(f"DiscountMonthsForward{s}") else ""))
                discs.append(d)
        return f"{part} {when}" + (f" ({'; '.join(discs)})" if discs else "")
    n, sets = len(term["lines"]), term["sets"]
    start = term["from_date"]
    if start == TODAY and today:
        start = (today - timedelta(days=1)).strftime("%Y/%m/%d")
    return (f"{n} installment{'s' if n != 1 else ''}: " + "; ".join(due(l) for l in term["lines"]) +
            f". {len(sets) or 'No'} set{'s' if len(sets) != 1 else ''}" + (f": {', '.join(sets)}" if sets else "") +
            f". From {start.replace('/', '-')}" + (f" to {term['to_date'].replace('/', '-')}" if term["to_date"] else "")
            + ".")

def plan_command(argv):
    """--plan [terms.json | '<JSON>'] (read-only, 2026-10-25): what a run would do with each
    term, nothing changed in Oracle. First every rule that needs no Oracle, then one browser
    visit: Oracle's today, the Calendar and Set Code lists (Create Payment Terms, left with
    Cancel) and one export for the names (exact: capitals and spaces count). Prints one JSON
    line: {"ok", "lists": {"today", "calendars", "sets"}, "results": [{"name", "status": "new" |
    "exists" | "problems", "ok", "skipped", "problems": [{"key", "row", "text"}], "existing"}]}.
    The JSON may be a request file ({"terms": [...]}), one page request, or a list of them."""
    import contextlib
    out = sys.stdout
    arg = argv[1] if len(argv) > 1 else str(HERE / "terms.json")
    try:
        raw = json.loads(Path(arg).read_text(encoding="utf-8") if Path(arg).suffix == ".json" and
                         Path(arg).exists() else arg)
        data = raw if isinstance(raw, dict) and "terms" in raw else {"terms": raw if isinstance(raw, list) else [raw]}
    except (ValueError, OSError) as e:
        print(json.dumps({"ok": False, "text": f"The request couldn't be read ({e})."}), file=out)
        return 2
    per_term = []
    terms = []
    with contextlib.redirect_stdout(sys.stderr):
        for t in data["terms"]:
            r = Rules()
            terms.append(parse_requirements({"terms": [t]}, "plan", r)[0])
            per_term.append(r)
        names = [t.get("name") if isinstance(t, dict) else None for t in data["terms"]]
        for i, n in enumerate(names):
            if n is not None and n in names[:i]:
                per_term[i].bad("name", f"The name '{n}' is listed twice; each name can be there only once.")
        try:
            oracle.check_environment()
            browser.refuse_production()
            work = oracle.init_work_dir(HERE)
            had_files = any(work.iterdir())
            with browser.OracleUI(work, headless=True) as ui:
                ui.setup = Setup(ui)
                lists = screen_lists(ui)
                zip_path, _ = ui.setup.export_csv(TASK, AREA, OFFERING)
            before = read_zip(zip_path)
            if not had_files:
                oracle.cleanup_work_dir()
        except SystemExit:
            print(json.dumps({"ok": False, "text": browser.failed_step_text(   # the real failed step (2026-10-26)
                "Oracle couldn't be checked just now (sign-in, screen or export problem).")}), file=out)
            return 1
    existing = term_names(before)
    loose = lambda s: " ".join(str(s).split()).lower()
    # Rank is unique across ALL payment terms: proven 2026-10-26 (ZZ_TEST_PT_6142_RANK5 refused, "A record with the
    # value 5 already exists. Enter a unique value."). Oracle's ranks from the export, then this upload's in order.
    ranks = {}
    for h in as_dicts(before[HEADER]):
        if str(h.get("Rank") or "").strip():
            ranks.setdefault(str(int(float(h["Rank"]))), h.get("Name") or list(h.values())[0])
    results = []
    for t, raw_t, r in zip(terms, data["terms"], per_term):
        if t:
            list_problems(t, lists, r)
        if t and TODAY in (t["from_date"], t["to_date"]):
            # "today" is only known now (Oracle's today minus one day): the To Date check again (2026-10-26)
            day = (lists["today"] - timedelta(days=1)).strftime("%Y/%m/%d")
            s_, e_ = (day if x == TODAY else x for x in (t["from_date"], t["to_date"]))
            if s_ and e_ and e_ < s_:
                r.bad("to_date", f"To Date {e_.replace('/', '-')} is before From Date {s_.replace('/', '-')} "
                      "(\"today\" = Oracle's today minus one day).")
        name = raw_t.get("name") if isinstance(raw_t, dict) else None
        exists = name in existing
        rank = t["rank"] if t else ""
        if rank and not exists:
            if rank in ranks:
                free = next(str(n) for n in range(int(rank) + 1, int(rank) + 10000) if str(n) not in ranks)
                r.bad("rank", f"Rank {rank} is already used by payment term {ranks[rank]}; Oracle allows each rank "
                      f"on one payment term only (\"A record with the value {rank} already exists\").")
                r.problems[-1]["fix"] = f"Use a rank no other term has, for example {free}, or leave Rank empty."
            else:
                ranks[rank] = name
        for p in r.problems:
            p.setdefault("fix", "Change it in the sheet and upload it again.")
        res = {"name": name, "ok": True, "problems": r.problems, "skipped": None, "existing": None,
               "found": {}, "fills": {}, "summary": describe(t, lists["today"]) if t and not exists else None}
        near = sorted(n for n in existing if name and n != name and loose(n) == loose(name))
        if near and not exists:     # Oracle's check is exact: a different term (yellow, 2026-10-25)
            res["found"]["name"] = (f"Oracle has {', '.join(repr(n) for n in near)}, which differs only in capitals "
                                    f"or spaces. Oracle treats '{name}' as a new, separate term.")
        if exists:
            rows = term_rows(before, name)
            res["existing"] = {"from_date": rows["header"].get("StartDateActive"),
                               "installments": len(rows["lines"]), "sets": rows["sets"]}
            res["skipped"] = (f"Payment term {name} already exists in Oracle (exact name), so it will be skipped; "
                              "nothing is changed.")
        res["status"] = "exists" if exists else ("problems" if r.problems else "new")
        results.append(res)
    print(json.dumps({"ok": True, "lists": {"today": lists["today"].isoformat(), "calendars": lists["calendars"],
                                            "sets": lists["sets"]}, "results": results}, ensure_ascii=False),
          file=out)
    return 0


# ---------------------------------------------------------------- main

def main():
    if sys.argv[1:2] == ["--plan"]:                 # read-only: rules, Oracle's lists, existing names
        sys.exit(plan_command(sys.argv[1:]))
    if sys.argv[1:2] == ["--run-batch"]:            # the upload sheet: all its terms in one import
        sys.exit(run_batch_command(sys.argv[1:]))
    page.main(SPEC, options_for, run_request)   # --spec / --options / --run; else returns
    here = HERE
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(here / "terms.json"), help="requirements JSON")
    ap.add_argument("--check", action="store_true",
                    help="read-only: validate, open the export/import screens and read Oracle's "
                         "today; nothing is submitted or created in Oracle")
    ap.add_argument("--dry-run", action="store_true", help="export and build the zip, no import")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    args = ap.parse_args()

    oracle.check_environment()
    browser.refuse_production()
    terms = load_requirements(args.file)
    print(f"{len(terms)} payment term(s) requested in {args.file}")
    run_terms(args, terms, here)


def load_requirements(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        oracle.fail(f"Cannot read {path}: {e}")
    return parse_requirements(data, path)


def run_terms(args, terms, here, progress=None, found=None):
    """The normal flow (check, or lists -> export -> skip existing -> build -> import ->
    export -> verify). Returns the terms it created ([] when none). progress: the page's
    progress lines (--run). found (optional dict): {name: {"header": row, "lines": [rows],
    "sets": [codes], "skipped": bool, "saved": bool}} as the export shows them."""
    work = oracle.init_work_dir(here)
    found = {} if found is None else found
    import_problem = None

    with browser.OracleUI(work, headless=not args.headed) as ui:
        ui.setup = Setup(ui)       # classic or Redwood Setup and Maintenance, detected
        if args.check:
            print("Checking the screens (read-only) ...")
            ui.setup.check_actions(TASK, AREA, OFFERING)
            resolve_today(terms, oracle_today(ui))
            print("Check passed: export/import screens open, Oracle's today read. Nothing was "
                  "submitted or created in Oracle (existence is checked on the fresh export of "
                  "a real run).")
            oracle.cleanup_work_dir()
            return []
        if needs_lists(terms) or uses_today(terms):
            lists = screen_lists(ui, lists=needs_lists(terms))
            if needs_lists(terms):
                rules = Rules()
                for t in terms:
                    list_problems(t, lists, rules)
                if rules.problems and progress:
                    raise page.PageError("NOT_IN_ORACLE", " ".join(p["text"] for p in rules.problems),
                                         page_problems(rules))
                if rules.problems:
                    oracle.fail("Values Oracle doesn't have:\n  " + "\n  ".join(p["text"] for p in rules.problems))
            resolve_today(terms, lists["today"])
        print("Exporting (before) ...")
        before_zip, _ = ui.setup.export_csv(TASK, AREA, OFFERING)
        before = read_zip(before_zip)
        existing = term_names(before)
        found["_ranks"] = {str(int(float(h["Rank"]))) for h in as_dicts(before[HEADER])     # for refusal suggestions
                           if str(h.get("Rank") or "").strip()}
        todo = []
        for t in terms:
            if t["name"] in existing:          # exact: capitals and spaces count
                print(f"  SKIP  {t['name']}: a payment term with this exact name already exists - not touched")
                found[t["name"]] = dict(term_rows(before, t["name"]), skipped=True, saved=False)
            else:
                todo.append(t)
        if not todo:
            print("Nothing to create.")
            oracle.cleanup_work_dir()
            return []

        tpl = pick_template(before)
        print(f"Row layout learned from existing term '{tpl}'")
        additions, by_term = {}, {}
        for t in todo:
            rows = build_rows(before, t, tpl)
            by_term[t["name"]] = {f: r for f, r in rows.items() if r}
            for fname, r in rows.items():
                additions.setdefault(fname, []).extend(r)
        names = re.sub(r"[^\w-]+", "_", "_".join(t["name"] for t in todo))[:60]
        import_zip = build_import_zip(before, additions, work / f"import_{names}.zip")
        print(f"Built {import_zip.name}: " + ", ".join(f"{f} +{len(r)}" for f, r in additions.items() if r))
        if args.dry_run:
            print(f"Dry run: not importing. Files kept in {work}")
            return []

        if progress:
            progress.step("creating")
        print("Importing ...")
        found["_imported"] = True
        try:
            ui.setup.import_csv(TASK, AREA, import_zip, OFFERING)
        except ImportNotClean as e:
            # Oracle finished the import but not cleanly: which terms got in is read from the
            # export below, so a rerun (or a failed-only sheet) never makes one twice.
            import_problem = e
            print(f"  IMPORT NOT CLEAN: {e}")
        if progress:
            progress.step("verifying")
        print("Exporting (after) to verify ...")
        after_zip, _ = ui.setup.export_csv(TASK, AREA, OFFERING)

    print("Verifying ...")
    after = read_zip(after_zip)
    names_after = term_names(after)
    saved = [t for t in todo if t["name"] in names_after]
    failed = [t for t in todo if t["name"] not in names_after]
    for t in saved:
        found[t["name"]] = dict(term_rows(after, t["name"]), skipped=False, saved=True)
    reasons = import_problem.rows if import_problem else {}
    print("Saved in Oracle: " + (", ".join(t["name"] for t in saved) or "none"))
    print("Not saved: " + (", ".join(t["name"] for t in failed) or "none"))
    for t in failed:
        found[t["name"]] = {"saved": False, "reason": "; ".join(reasons.get(t["name"], [])) or None}
        print(f"  NOT SAVED  {t['name']}: " + ("; ".join(reasons.get(t["name"], [])) or "Oracle's log names no reason"))
    per = {}
    ok = verify(before, after, saved, by_term, per) if saved else True
    found["_after"] = True
    for t in saved:
        found[t["name"]]["verified"] = per.get(t["name"], False)
    if failed or import_problem:
        why = "; ".join(f"{t['name']}: {'; '.join(reasons.get(t['name'], [])) or 'no reason in the log'}"
                        for t in failed)
        oracle.fail(f"The import didn't finish cleanly. Saved and checked: "
                    f"{', '.join(t['name'] for t in saved) or 'none'}"
                    f"{'' if ok else ' (but some values differ, see FAIL lines)'}. Not saved: "
                    f"{', '.join(t['name'] for t in failed) or 'none'}. Oracle said: "
                    f"{why or (import_problem.detail if import_problem else 'the import ended without them')}")
    if not ok:
        oracle.fail("Verification failed (MISMATCH) - see FAIL lines above.")
    print("All requested payment terms created and verified.")
    oracle.cleanup_work_dir()
    return todo


def term_rows(files, name):
    """One term as an export shows it: header row, line rows, set codes (exact name)."""
    return {"header": next((r for r in as_dicts(files[HEADER]) if r["Name"] == name), None),
            "lines": sorted((r for r in as_dicts(files[LINE]) if r[PARENT] == name),
                            key=lambda r: int(r["SequenceNum"] or 0)),
            "sets": [r["SetCode"] for r in as_dicts(files[SUBS]) if r[PARENT] == name]}


if __name__ == "__main__":
    main()
