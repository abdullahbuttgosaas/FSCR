"""Add lookup codes (order types) to an EXISTING lookup type.

Route 1 (preferred): REST, standardLookups/<type>/child/lookupCodes (Basic auth from
.env, links taken from Oracle's own responses). GET the type and its codes -> skip
codes that exist -> unique-meaning check -> POST each new code -> GET it back and
compare every field -> GET all codes again: every other code unchanged. Then, in a
full run, a read-only look at the Create Order screen's Order Type list.

Route 2 (automatic fallback, only when REST fails or is refused, e.g. HTTP 403):
Setup and Maintenance > Order Management > Orders > Manage Order Lookups > Actions >
Export / Import, driven by common/browser.py; fresh export -> append the new code
rows -> import -> second fresh export -> screen check. Built for the Redwood Set Up
page; not yet re-proven on the classic layout (see CLAUDE.md).

Temporary files go in "Order Types/_work/": deleted after a verified success,
kept after any failure (with screenshots).

  python "Order Types/browser_flow.py"             # full run (REST, fallback if needed)
  python "Order Types/browser_flow.py" --check     # read-only through REST (GET only)
  python "Order Types/browser_flow.py" --check-ui  # read-only check of the fallback screens
  python "Order Types/browser_flow.py" --dry-run   # fallback route: export + build zip, no import
  python "Order Types/browser_flow.py" --headed    # browser parts visible

Page interface (root CLAUDE.md > Page interface, common/page.py), one code per run:
  python "Order Types/browser_flow.py" --spec
  python "Order Types/browser_flow.py" --options lookup_type
  python "Order Types/browser_flow.py" --run '{"code": "X", "meaning": "Y"}'
"""
import argparse
import csv
import io
import json
import re
import sys
import time
import zipfile
from datetime import date, timedelta
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import browser, oracle, page  # noqa: E402

OFFERING, AREA, TASK = "Order Management", "Orders", "Manage Order Lookups"
TYPE_CSV, CODE_CSV = "FND_APP_STANDARD_LOOKUP.csv", "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv"
PARENT = "FND_APP_STANDARD_LOOKUP.LookupType"
WHO = ("CreatedBy", "CreationDate", "LastUpdatedBy", "LastUpdateDate", "LastUpdateLogin")
SEED_USER = "SEED_DATA_FROM_APPLICATION"
FALLBACK_TYPES = ("ORA_DOO_ORDER_TYPES", "DOO_ORDER_TYPES")
FALLBACK_MEANING = "Type of Sales Order"
TODAY = "today"   # request word: Oracle's today minus one day (see CLAUDE.md > Dates)
SERVER_TODAY = None   # Oracle's today (date of the REST response), set by rest_route()
KNOWN_FIELDS = {"code", "meaning", "description", "display_sequence", "enabled",
                "start_date", "end_date", "tag"}


# ---------------------------------------------------------------- requirements

def _text(v, where, key, maxlen, required=False):
    if v in (None, ""):
        if required:
            oracle.fail(f"{where}: '{key}' is required")
        return ""
    if not isinstance(v, str) or v != v.strip() or len(v) > maxlen:
        oracle.fail(f"{where}: '{key}' must be text up to {maxlen} characters, no outer spaces")
    return v


def _date(v, where, key):
    if v in (None, ""):
        return ""
    if v == TODAY:
        return TODAY   # resolved later from Oracle's own date
    try:
        return date.fromisoformat(v).strftime("%Y/%m/%d")   # export format
    except (TypeError, ValueError):
        oracle.fail(f"{where}: '{key}' must be a date as YYYY-MM-DD, got {v!r}")


def load_requirements(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        oracle.fail(f"Cannot read {path}: {e}")
    return parse_requirements(data, path)


def parse_requirements(data, path):
    """The request (file contents or a page request) -> (lookup type, code rows)."""
    lookup_type = _text(data.get("lookup_type") or FALLBACK_TYPES[0], "file", "lookup_type", 30)
    raw = data.get("codes")
    if not isinstance(raw, list) or not raw:
        oracle.fail(f"{path} must contain a non-empty 'codes' list")
    out, seen, meanings = [], set(), set()
    for c in raw:
        unknown = set(c) - KNOWN_FIELDS
        if unknown:
            oracle.fail(f"code {c.get('code')!r}: unknown field(s) {sorted(unknown)}; "
                        f"allowed: {sorted(KNOWN_FIELDS)}")
        code = _text(c.get("code"), "code", "code", 30, required=True)
        where = f"code {code}"
        if code in seen:
            oracle.fail(f"{where}: listed twice")
        seen.add(code)
        meaning = _text(c.get("meaning"), where, "meaning", 80, required=True)
        if meaning.lower() in meanings:
            oracle.fail(f"{where}: meaning {meaning!r} is used twice in this request")
        meanings.add(meaning.lower())
        seq = c.get("display_sequence")
        if seq is not None and (isinstance(seq, bool) or not isinstance(seq, int) or seq < 0):
            oracle.fail(f"{where}: 'display_sequence' must be a whole number")
        enabled = c.get("enabled", True)
        if not isinstance(enabled, bool):
            oracle.fail(f"{where}: 'enabled' must be true or false")
        start, end = _date(c.get("start_date"), where, "start_date"), _date(c.get("end_date"), where, "end_date")
        if start and end and end < start and TODAY not in (start, end):
            oracle.fail(f"{where}: end_date is before start_date")
        out.append({"LookupCode": code, "Meaning": meaning,
                    "Description": _text(c.get("description"), where, "description", 240),
                    "DisplaySequence": "" if seq is None else str(seq),
                    "EnabledFlag": "Y" if enabled else "N",
                    "StartDateActive": start, "EndDateActive": end,
                    "Tag": _text(c.get("tag"), where, "tag", 150)})
    return lookup_type, out


# ---------------------------------------------------------------- screen (read-only)

ROWS_JS = r"""() => [...document.querySelectorAll('tr[_afrrk]')].filter(r => r.offsetWidth)
  .map(r => [...r.querySelectorAll('td')].filter(td => !td.querySelector('td')).map(td => {
      const i = [...td.querySelectorAll('input:not([type=hidden]):not([type=checkbox]), textarea')];
      return i.length ? i.map(x => x.value).join(' ').trim() : td.innerText.trim(); }))"""


def search_lookup_type(ui, lookup_type):
    """Manage Order Lookups: search the type and select its row. Since the Redwood
    Set Up page (2026-10-20) the first Search click can be lost while the classic page
    is still starting, so the search is retried until the row shows. Returns the page."""
    page = ui.page          # after open_task: the task's own page (it may be a new tab)
    field = page.get_by_label("Lookup Type", exact=True).first
    field.wait_for(timeout=60000)
    ui.settle()
    result = page.get_by_text(lookup_type, exact=True).first

    def search(attempt):
        field.fill(lookup_type)
        ui.click(page.get_by_role("button", name="Search", exact=True), "Search")
        ui.settle()
    ui.retry(f"{TASK} search did not show {lookup_type}", search,          # shared retry helper (2026-10-26)
             lambda timeout: result.wait_for(timeout=timeout), wait=20000, last_wait=40000)
    ui.click(result, "lookup type row")
    ui.settle()
    return page


def codes_shown(ui, page, lookup_type, ready):
    """Wait until the selected type's codes show (ready(timeout) raises or returns False when not); a lost click
    on the type's row is clicked again (2026-10-26). Soft: the caller reports what it could not read."""
    def act(attempt):
        if attempt > 1:
            ui.click(page.get_by_text(lookup_type, exact=True).first, "lookup type row (again)")
            ui.settle()
    return ui.retry(f"{TASK} did not show the codes of {lookup_type}", act, ready, wait=30000, last_wait=30000,
                    soft=True)


def open_lookup(ui, lookup_type):
    """Manage Order Lookups, search the type and select it (nothing is typed elsewhere)."""
    ui.open_task(TASK, AREA, OFFERING)
    page = search_lookup_type(ui, lookup_type)


def leave_without_saving(ui):
    page = ui.page
    field = page.get_by_label("Lookup Type", exact=True).first

    def cancel(attempt):             # Cancel saves nothing; checked that the task page closed (2026-10-26)
        if attempt == 1 or field.count() and field.is_visible():
            ui.click(page.get_by_role("button", name=re.compile(r"^Ca")).first, "Cancel")
        ui.settle()
        yes = page.get_by_role("button", name=re.compile(r"^Y\s*es$"))
        if yes.count() and yes.first.is_visible():
            ui.click(yes.first, "Yes (leave without saving)")
            ui.settle()
    ui.retry(f"{TASK} did not close after Cancel", cancel,
             lambda timeout: field.wait_for(state="hidden", timeout=timeout), wait=20000, last_wait=40000)


def oracle_today_on_screen(ui):
    """Oracle's today from the calendar of a NEW, unsaved code row's empty Start Date.
    The page is left with Cancel, so the row is never saved."""
    page = ui.page
    before = page.locator("input[aria-label='Start Date']:visible, "
                          "input[id$='::content'][aria-label*='Start Date']:visible").count()
    add = page.locator("[title='Add Row']:visible, [title='New']:visible, [title='Create']:visible")
    if not add.count():
        ui.fail("today", "No add-row button on the Lookup Codes table.")
    got = {}

    def empty_start():
        for f in page.get_by_label("Start Date").and_(page.locator(":visible")).all():
            if not f.input_value().strip():
                return f
        return None

    def act(attempt):                # a row of the unsaved table (nothing saved); added again only while none shows
        if empty_start() is None:
            ui.click(add.last, "Lookup Codes add row (not saved)" + (", again" if attempt > 1 else ""))
        ui.settle()

    def shown(timeout):
        end = time.time() + timeout / 1000
        while time.time() < end:
            got["f"] = empty_start()
            if got["f"] is not None:
                return True
            page.wait_for_timeout(500)
        return False
    ui.retry(f"Lookup Codes table did not add a row ({before} Start Dates before)", act, shown,
             wait=10000, last_wait=20000)
    return calendar_today(ui, got["f"], "new code row Start Date")


MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")


def calendar_today(ui, field, what):
    """Oracle's today from an empty date cell's calendar, opened with the down-arrow key
    (in this table the calendar icon of Start Date is clipped and cannot be clicked).
    The calendar opens on Oracle's today with that day selected; closed with Escape."""
    import datetime as _dt
    page = ui.page
    # Pin the field by its id: Oracle redraws the table rows, and a position-based
    # locator would then point at another row's Start Date.
    field = page.locator(f"[id='{field.get_attribute('id')}']")
    if field.input_value().strip():
        ui.fail("today", f"{what} is not empty; cannot read Oracle's today from it.")
    grid = page.locator("table[summary][id$='::cg']:visible").first

    def open_calendar(attempt):      # 2026-10-26: a lost key press is pressed again (never while the calendar shows)
        if not grid.count():
            field.click()
            field.press("ArrowDown")
    ui.retry(f"calendar of {what} did not open", open_calendar, lambda timeout: grid.wait_for(timeout=timeout),
             wait=10000, last_wait=20000)
    month, year = grid.get_attribute("summary").split()
    day = grid.locator("td.p_AFSelected").first.inner_text().strip()
    page.keyboard.press("Escape")
    page.wait_for_timeout(800)
    if field.input_value().strip():
        ui.fail("today", f"{what} changed while reading the calendar.")
    today = _dt.date(int(year), MONTHS.index(month) + 1, int(day))
    ui.log(f"Oracle's today (calendar of {what}): {today.isoformat()}")
    return today


def resolve_today(codes, today):
    day = (today - timedelta(days=1)).strftime("%Y/%m/%d")
    for c in codes:
        for key in ("StartDateActive", "EndDateActive"):
            if c[key] == TODAY:
                c[key] = day
                print(f"  NOTE  {c['LookupCode']}: {key} \"today\" -> {day} (Oracle's today "
                      f"{today.isoformat()} minus one day)")
        if c["StartDateActive"] and c["EndDateActive"] and c["EndDateActive"] < c["StartDateActive"]:
            oracle.fail(f"code {c['LookupCode']}: end_date is before start_date")


def uses_today(codes):
    return any(TODAY in (c["StartDateActive"], c["EndDateActive"]) for c in codes)


def check_on_screen(ui, lookup_type, codes):
    """Read-only look at the type's codes on screen + Oracle's today. Returns today."""
    open_lookup(ui, lookup_type)
    read = {"rows": []}

    def settled(timeout):            # 2026-10-26: read when the codes have shown and stopped changing
        end = time.time() + timeout / 1000
        last = None
        while time.time() < end:
            now = [r for r in ui.page.evaluate(ROWS_JS) if any(r)]
            if now and now == last:
                read["rows"] = now
                return True
            last = now
            ui.page.wait_for_timeout(2000)
        read["rows"] = last or []
        return False
    codes_shown(ui, ui.page, lookup_type, settled)
    rows = read["rows"]
    shown = {c for r in rows for c in r if c}
    for c in codes:
        state = "exists on screen (would be skipped)" if c["LookupCode"] in shown else "not on screen (would be created)"
        clash = [r for r in rows if c["Meaning"] in r and c["LookupCode"] not in r]
        print(f"  {c['LookupCode']}: {state}" + (f"; meaning {c['Meaning']!r} already used" if clash else ""))
    today = oracle_today_on_screen(ui)
    leave_without_saving(ui)
    return today


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
    for need in (TYPE_CSV, CODE_CSV):
        if need not in files:
            oracle.fail(f"Export {Path(path).name} has no {need}; files: {sorted(files)}")
    return files


def dicts(f):
    return [dict(zip(f["header"], r)) for r in f["rows"]]


def find_lookup_type(files, wanted):
    types = {r["LookupType"]: r for r in dicts(files[TYPE_CSV])}
    for name in dict.fromkeys((wanted,) + FALLBACK_TYPES):
        if name in types:
            return name
    by_meaning = [t for t, r in types.items() if r["Meaning"] == FALLBACK_MEANING]
    if len(by_meaning) == 1:
        return by_meaning[0]
    oracle.fail(f"The lookup type {wanted!r} is not in the export (also tried "
                f"{', '.join(FALLBACK_TYPES)} and meaning '{FALLBACK_MEANING}'). "
                "Ask the user in plain words which lookup type holds the order types. "
                f"Types in the export: {sorted(types)}")


def codes_of(files, lookup_type):
    return [r for r in dicts(files[CODE_CSV]) if r[PARENT] == lookup_type]


def template_code(codes):
    """Most recently created user-made code of the type: its who columns are reused."""
    user = [r for r in codes if r.get("CreatedBy") != SEED_USER]
    pool = user or codes
    if not pool:
        oracle.fail("The lookup type has no codes to learn the row layout from.")
    return max(pool, key=lambda r: r.get("CreationDate", ""))


def build_rows(files, lookup_type, new_codes, tpl):
    header = files[CODE_CSV]["header"]
    rows = []
    for c in new_codes:
        r = {col: "" for col in header}
        r.update({k: tpl[k] for k in WHO if k in tpl})
        r.update(c)
        r[PARENT] = lookup_type
        rows.append(r)
    return rows


def csv_line(header, row):
    buf = io.StringIO()
    csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n").writerow([row.get(c, "") for c in header])
    return buf.getvalue()


def build_import_zip(files, new_rows, path):
    """Every file once; every existing row byte-for-byte; new code rows appended."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zo:
        for name, f in files.items():
            data = f["raw"]
            if name == CODE_CSV:
                text = f["text"] if f["text"].endswith("\n") else f["text"] + "\n"
                data = (text + "".join(csv_line(f["header"], r) for r in new_rows)).encode("utf-8")
            zo.writestr(name, data)
    return path


# ---------------------------------------------------------------- verify

def verify_files(before, after, lookup_type, new_rows):
    ok = True
    got = {r["LookupCode"]: r for r in codes_of(after, lookup_type)}
    for want in new_rows:
        code = want["LookupCode"]
        row = got.get(code)
        if row is None:
            print(f"  FAIL  {code}: not in the export after import")
            ok = False
            continue
        diffs = {k: (row.get(k), v) for k, v in want.items() if k not in WHO and row.get(k) != v}
        if diffs:
            note = ""
            if "StartDateActive" in diffs or "EndDateActive" in diffs:
                note = " (a one-day difference in a date would mean a time-zone shift)"
            print(f"  FAIL  {code}: differs (got, expected): {diffs}{note}")
            ok = False
        else:
            print(f"  OK    {code}: seq {row['DisplaySequence'] or '-'}, enabled {row['EnabledFlag']}, "
                  f"start {row['StartDateActive'] or '-'}, end {row['EndDateActive'] or '-'}, "
                  f"meaning {row['Meaning']!r}, description {row['Description']!r}, tag {row['Tag']!r}")
    new_keys = {(lookup_type, r["LookupCode"]) for r in new_rows}
    for fname, key in ((TYPE_CSV, lambda r: (r[0],)), (CODE_CSV, lambda r: (r[0], r[1]))):
        hdr = before[fname]["header"]
        old = [r for r in before[fname]["rows"]]
        new = [r for r in after[fname]["rows"] if key(r) not in new_keys]
        if sorted(old) == sorted(new):
            print(f"  OK    existing rows unchanged in {fname} ({len(old)})")
            continue
        idx = [i for i, c in enumerate(hdr) if c not in WHO]
        strip = lambda rows: sorted(tuple(r[i] for i in idx) for r in rows)
        if strip(old) == strip(new):
            print(f"  NOTE  {fname}: only who/date-stamp columns of existing rows changed")
        else:
            print(f"  FAIL  {fname}: existing rows changed")
            ok = False
    return ok


def screen_date(export_date):
    """Export date 2026/10/19 -> on-screen m/d/yy, e.g. 10/19/26."""
    if not export_date:
        return ""
    y, m, d = export_date.split("/")
    return f"{int(m)}/{int(d)}/{y[2:]}"


def verify_screen(ui, lookup_type, new_rows):
    """Search the type in Manage Order Lookups and read each new code's row. No saving."""
    ui.open_task(TASK, AREA, OFFERING)
    page = search_lookup_type(ui, lookup_type)
    ok = True
    for want in new_rows:
        code = want["LookupCode"]
        cell = page.locator("table td").filter(has_text=re.compile(rf"^{re.escape(code)}$")).first
        if not codes_shown(ui, page, lookup_type, lambda timeout: cell.wait_for(timeout=timeout)):
            print(f"  FAIL  on screen: {code} not shown in the Lookup Codes table")
            ok = False
            continue
        row = cell.locator("xpath=ancestor::tr[1]")
        values = [i.input_value() for i in row.locator("input[type=text], input:not([type])").all()]
        enabled = row.locator("input[type=checkbox]").first.is_checked()
        expect = [want["DisplaySequence"], screen_date(want["StartDateActive"]),
                  screen_date(want["EndDateActive"]), want["Meaning"], want["Description"], want["Tag"]]
        good = values[:6] == expect and enabled == (want["EnabledFlag"] == "Y")
        print(f"  {'OK  ' if good else 'FAIL'}  on screen: {code} seq {values[0]!r} enabled {enabled} "
              f"start {values[1]!r} end {values[2]!r} meaning {values[3]!r} "
              f"description {values[4]!r} tag {values[5]!r}")
        ok &= good
    shot = ui.work / "screen_check.png"
    page.screenshot(path=str(shot))
    leave_without_saving(ui)        # leave without saving anything
    return ok, shot


# ---------------------------------------------------------------- planning (both routes)

def plan_codes(existing, codes, lookup_type):
    """Skip codes that exist, stop on a meaning clash, assign missing display
    sequences. existing: rows with LookupCode, Meaning, DisplaySequence (text).
    Returns the codes to create (or [] when nothing is left)."""
    have = {r["LookupCode"]: r for r in existing}
    todo = []
    for c in codes:
        old = have.get(c["LookupCode"])
        if old:
            print(f"  SKIP  {c['LookupCode']}: already exists in {lookup_type} - not touched "
                  f"(meaning {old['Meaning']!r}, sequence {old['DisplaySequence'] or '-'}, "
                  f"enabled {old.get('EnabledFlag', '?')}, start {old.get('StartDateActive') or '-'})")
        else:
            todo.append(c)
    if not todo:
        return []
    clashes = [f"{c['LookupCode']}: meaning {c['Meaning']!r} is already used by code {used_by}"
               for c, used_by in meaning_clashes(existing, todo)]
    if clashes:
        oracle.fail("Code meanings must be unique within the lookup type. Ask the user for "
                    "a different meaning:\n  " + "\n  ".join(clashes))
    for c, kind, n, used in assign_sequences(existing, todo):
        if kind == "assigned":
            print(f"  NOTE  {c['LookupCode']}: no display sequence given; using {n} "
                  "(next after the highest existing one)")
        elif used:
            print(f"  NOTE  {c['LookupCode']}: display sequence {n} is "
                  f"also used by {', '.join(used)} (allowed; only affects list order)")
    return todo


def meaning_clashes(existing, todo):
    """Oracle requires code meanings to be unique within a lookup type (capitals ignored).
    Returns [(code row, code that already uses its meaning)]."""
    taken = {r["Meaning"].lower(): r["LookupCode"] for r in existing}
    return [(c, taken[c["Meaning"].lower()]) for c in todo if c["Meaning"].lower() in taken]


def assign_sequences(existing, todo):
    """Fills a missing DisplaySequence with the next number after the highest one (existing
    codes and the rows before it). Returns [(code row, "assigned" | "given", number, other
    existing codes with that number)]."""
    seqs = [int(r["DisplaySequence"]) for r in existing if str(r["DisplaySequence"]).isdigit()]
    nxt, out = max(seqs, default=0), []
    for c in todo:
        if not c["DisplaySequence"]:
            nxt += 1
            c["DisplaySequence"] = str(nxt)
            out.append((c, "assigned", nxt, []))
        else:
            nxt = max(nxt, int(c["DisplaySequence"]))
            used = [r["LookupCode"] for r in existing if str(r["DisplaySequence"]) == c["DisplaySequence"]]
            out.append((c, "given", int(c["DisplaySequence"]), used))
    return out


# ---------------------------------------------------------------- route 1: REST

class RestUnavailable(Exception):
    """REST failed or was refused; the run switches to the fallback route."""


class RestRefused(Exception):
    """Oracle answered the create with HTTP 400: it refused a VALUE (e.g. FND-7103, a meaning in use).
    Not a reason for the fallback route: the same value would be refused there too (2026-10-26)."""


# Whether this process saved anything in Oracle yet: "no", "yes" (a code was created) or
# "maybe" (stopped during the fallback's import). A failed --run reports it in error.detail
# (root CLAUDE.md > Page interface), so the page knows what was saved.
SAVED = {"state": "no"}


REST_FIELDS = ("LookupCode", "Meaning", "Description", "EnabledFlag", "StartDateActive",
               "EndDateActive", "DisplaySequence", "Tag")


def rest_get(url, what, **params):
    r, err = oracle.try_call("GET", url, params=params, timeout=120)
    if err:
        raise RestUnavailable(f"{what}: {err}")
    return r


def rest_lookup_type(wanted):
    """The order type lookup through REST: the requested name, then the fallbacks,
    then the type whose meaning is "Type of Sales Order". Returns (item, response)."""
    base = f"{oracle.API_BASE}/standardLookups"
    for name in dict.fromkeys((wanted,) + FALLBACK_TYPES):
        r = rest_get(base, f"GET lookup type {name}", finder=f"LookupTypeFinder;LookupType={name}",
                     limit=5)
        items = [i for i in r.json().get("items", []) if i.get("LookupType") == name]
        if items:
            if name != wanted:
                print(f"  NOTE  {wanted} not found; using {name} instead")
            return items[0], r
    r = rest_get(base, "GET lookup type by meaning", q=f"Meaning='{FALLBACK_MEANING}'", limit=25)
    items = r.json().get("items", [])
    if len(items) == 1:
        print(f"  NOTE  {wanted} not found; using {items[0]['LookupType']} (meaning "
              f"'{FALLBACK_MEANING}') instead")
        return items[0], r
    oracle.fail(f"The lookup type {wanted!r} was not found through REST (also tried "
                f"{', '.join(FALLBACK_TYPES)} and meaning '{FALLBACK_MEANING}'). Ask the user in "
                "plain words which lookup type holds the order types.")


def rest_codes(type_item):
    href = oracle.link_href(type_item, "lookupCodes")
    if not href:
        raise RestUnavailable("the lookup type item has no lookupCodes link")
    rows, offset = [], 0
    while True:
        data = rest_get(href, "GET lookup codes", onlyData="true", limit=200, offset=offset).json()
        rows += data.get("items", [])
        if not data.get("hasMore"):
            return href, rows
        offset += len(data.get("items", []))


def as_plan_row(r):
    """REST code -> the row shape plan_codes() uses (text values)."""
    seq = r.get("DisplaySequence")
    return {"LookupCode": r["LookupCode"], "Meaning": r.get("Meaning") or "",
            "DisplaySequence": "" if seq is None else str(seq),
            "EnabledFlag": r.get("EnabledFlag"), "StartDateActive": r.get("StartDateActive")}


def rest_body(c):
    """Request values (export format) -> REST body; only fields the request has, plus
    the UI default EnabledFlag."""
    body = {"LookupCode": c["LookupCode"], "Meaning": c["Meaning"], "EnabledFlag": c["EnabledFlag"]}
    if c["Description"]:
        body["Description"] = c["Description"]
    if c["StartDateActive"]:
        body["StartDateActive"] = c["StartDateActive"].replace("/", "-")
    if c["EndDateActive"]:
        body["EndDateActive"] = c["EndDateActive"].replace("/", "-")
    if c["DisplaySequence"]:
        body["DisplaySequence"] = int(c["DisplaySequence"])
    if c["Tag"]:
        body["Tag"] = c["Tag"]
    return body


def rest_expected(body):
    """What a GET must return for the new code (empty optional fields come back null)."""
    exp = {k: None for k in REST_FIELDS}
    exp.update(body)
    return exp


def rest_route(wanted_type, codes, check_only):
    """Returns (lookup_type, created bodies). Raises RestUnavailable to fall back."""
    print("REST: reading the lookup type and its codes ...")
    type_item, resp = rest_lookup_type(wanted_type)
    lookup_type = type_item["LookupType"]
    print(f"  lookup type {lookup_type}: meaning {type_item.get('Meaning')!r}, "
          f"REST access {type_item.get('RestAccessSecured')}")
    global SERVER_TODAY
    SERVER_TODAY = oracle.server_date(resp)
    if uses_today(codes) or check_only:
        today = SERVER_TODAY
        print(f"  Oracle's today (server date of the REST response): {today.isoformat()}")
        resolve_today(codes, today)
    href, existing = rest_codes(type_item)
    print(f"  {len(existing)} existing code(s)")
    todo = plan_codes([as_plan_row(r) for r in existing], codes, lookup_type)
    if check_only:
        for c in todo:
            print(f"  WOULD CREATE  {rest_body(c)}")
        print("Check passed (REST, read-only): only GET calls were made; nothing was created.")
        return lookup_type, []
    if not todo:
        print("Nothing to create.")
        return lookup_type, []
    created = []
    for c in todo:
        body = rest_body(c)
        print(f"REST: creating {body['LookupCode']} ...")
        r, err = oracle.try_call("POST", href, json=body, timeout=120)
        if err:
            if r is not None and r.status_code == 400 and not created:
                raise RestRefused(str(err))
            if r is not None and r.status_code in (401, 403):
                print(f"  REST refused creating lookup codes (HTTP {r.status_code}): this login has "
                      "no permission to create them through REST.")
            if not created:
                raise RestUnavailable(f"POST {body['LookupCode']}: {err}")
            oracle.fail(f"REST created {', '.join(b['LookupCode'] for b in created)} but then "
                        f"failed on {body['LookupCode']}:\n{err}\nRun again: existing codes are "
                        "skipped, the rest go through the fallback if REST still fails.")
        created.append(body)
        SAVED["state"] = "yes"
        print(f"  created (HTTP {r.status_code})")
    return lookup_type, created


def rest_verify(type_lookup, created, before, found=None):
    """GET every new code back and compare every field; every other code unchanged.
    found (optional dict): filled with {code: the row as Oracle returned it}."""
    type_item, _ = rest_lookup_type(type_lookup)
    href, after = rest_codes(type_item)
    ok = True
    for body in created:
        data = rest_get(href, f"GET {body['LookupCode']}", onlyData="true",
                        finder=f"LookupCodeFinder;LookupCode={body['LookupCode']}").json()
        rows = [r for r in data.get("items", []) if r.get("LookupCode") == body["LookupCode"]]
        if len(rows) != 1:
            print(f"  FAIL  {body['LookupCode']}: {len(rows)} row(s) found by GET")
            ok = False
            continue
        exp, got = rest_expected(body), rows[0]
        if found is not None:
            found[body["LookupCode"]] = got
        diffs = {k: (got.get(k), v) for k, v in exp.items() if got.get(k) != v}
        if diffs:
            print(f"  FAIL  {body['LookupCode']}: differs (got, expected): {diffs}")
            ok = False
        else:
            print(f"  OK    {body['LookupCode']}: " + ", ".join(f"{k} {got.get(k)!r}" for k in REST_FIELDS))
    new = {b["LookupCode"] for b in created}
    strip = lambda rows: sorted(tuple((k, r.get(k)) for k in REST_FIELDS) for r in rows
                                if r["LookupCode"] not in new)
    if strip(before) == strip(after):
        print(f"  OK    every other code unchanged ({len(before)})")
    else:
        print("  FAIL  other codes changed")
        ok = False
    return ok


# ---------------------------------------------------------------- Create Order (read-only)

def create_order_has_type(ui, meanings):
    """Create Order (Order Management work area) > Order Type: type each meaning and
    see whether Oracle accepts it from its list. Read-only: Cancel > Yes, nothing saved.
    Returns {meaning: True/False}."""
    page = ui.page
    found = {}
    with ui.step("open Create Order"):
        page.goto(browser.start_url(), wait_until="domcontentloaded", timeout=120000)
        ui.settle()
        ui.check_signed_in()
        nav = page.locator("a[title='Navigator']:visible").first
        nav.wait_for(timeout=60000)
        node = "pt1:_UISnvr:0:nv_itemNode_order_management_order_management"

        # 2026-10-26: the Navigator fills its links a few seconds after opening (3 s was not always enough) and a
        # click can be lost, so each step is checked and done again (shared retry helper)
        def navigator(attempt):
            if attempt > 1:
                page.keyboard.press("Escape")
            ui.click(nav, "Navigator")

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
        ui.retry("Order Management work area did not open", order_area,
                 lambda timeout: link.wait_for(timeout=timeout), wait=60000, last_wait=90000)

        def create(attempt):
            if attempt == 1 or link.count() and link.is_visible():
                ui.click(link, "Create Order" + (" (again)" if attempt > 1 else ""))
            ui.settle()
        ui.retry("Order Management did not open Create Order", create,
                 lambda timeout: ui.wait_heading("Create Order", timeout=timeout), wait=60000, last_wait=90000)
    with ui.step("look up the order types on Create Order"):
        for meaning in meanings:
            field = ui.field("Order Type")
            ok, rows = ui.lov_type(field, meaning, "Order Type")
            shown = field.input_value()
            found[meaning] = ok and shown == meaning
            print(f"  {'OK  ' if found[meaning] else 'FAIL'}  Create Order > Order Type accepts "
                  f"{meaning!r} (field shows {shown!r})")
            field.fill("")
            field.press("Tab")
            ui.settle()
            ui.close_lov_dialogs()
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
    return found


def setup_layout(ui):
    """Which Setup and Maintenance layout Oracle shows now: "Redwood" or "classic"."""
    ui.page.goto(f"{oracle.HOST}{browser.SETUP_PATH}", wait_until="domcontentloaded", timeout=120000)
    ui.settle()
    ui.check_signed_in()
    for _ in range(60):
        if "/redwood/" in ui.page.url or ui.page.locator(ui.SWITCHER).count():
            return "Redwood"
        if ui.page.get_by_text(re.compile(r"^Setup: ")).count():
            return "classic"
        ui.page.wait_for_timeout(2000)
    return "unknown"


# ---------------------------------------------------------------- page interface

SPEC = {
    "title": "Add an order type",
    "description": "Adds a new order type that sales orders can use; existing ones are never changed.",
    "fields": [
        {"key": "code", "label": "Order type code", "required": True, "type": "text",
         "placeholder": "RUSH_ORDER", "default": None,
         "help": "Up to 30 characters; capital and small letters count as different."},
        {"key": "meaning", "label": "Name shown to users", "required": True, "type": "text",
         "placeholder": "Rush Order", "default": None,
         "help": "Up to 80 characters; no other order type may already use it."},
        {"key": "description", "label": "Description", "required": False, "type": "text",
         "placeholder": "Orders shipped the same day", "default": None},
        {"key": "display_sequence", "label": "Position in the list", "required": False,
         "type": "number", "placeholder": "30", "default": None,
         "help": "Empty: the next number after the last order type."},
        {"key": "enabled", "label": "Active", "required": False, "type": "yes-no",
         "placeholder": "yes", "default": True},
        {"key": "start_date", "label": "Start date", "required": False, "type": "date",
         "placeholder": "2026-10-21", "default": None,
         "help": "Empty: active right away. 'today' means Oracle's today minus one day."},
        {"key": "end_date", "label": "End date", "required": False, "type": "date",
         "placeholder": "2027-12-31", "default": None},
        {"key": "tag", "label": "Tag", "required": False, "type": "text",
         "placeholder": "INT", "default": None},
        {"key": "lookup_type", "label": "Order type list", "required": False, "type": "pick",
         "placeholder": "Type of Sales Order", "default": FALLBACK_TYPES[0], "list": "samples"},
    ],
}
MAX_LEN = {"code": 30, "meaning": 80, "description": 240, "tag": 150}
WHERE = ("Setup and Maintenance > Order Management > Orders > Manage Order Lookups > "
         "{type}; and the Order Type list on Create Order")


# Drop-down samples: only values that have created a verified order type in this project
# (ABCABC1, ZZ_TEST_2868, ZZ_TEST_9464, ... all in ORA_DOO_ORDER_TYPES). A value joins only
# after such a create (see CLAUDE.md > Page interface). `--options lookup_type --all`
# gives the live search below; a --run checks anything typed against it.
SAMPLES = {"lookup_type": [("ORA_DOO_ORDER_TYPES", "Type of Sales Order")]}


def options_for(key):
    """The drop-down sample above; with --all, or during --run (the check of what was
    typed in), the live list."""
    if key in SAMPLES and sys.argv[1:2] == ["--options"] and "--all" not in sys.argv:
        return [{"value": v, "label": l} for v, l in SAMPLES[key]]
    return live_options(key)


def live_options(key):
    """--options lookup_type: the lookup types that hold order types, found live through
    REST the same way the run looks for them (the default names, then the meaning)."""
    oracle.check_environment()
    if key != "lookup_type":
        raise page.PageError("FAILED", detail=f"no list for {key!r}")
    base = f"{oracle.API_BASE}/standardLookups"
    found = {}
    for name in FALLBACK_TYPES:
        r = rest_get(base, f"GET lookup type {name}", finder=f"LookupTypeFinder;LookupType={name}",
                     limit=5)
        for i in r.json().get("items", []):
            if i.get("LookupType") == name:
                found[name] = i
    r = rest_get(base, "GET lookup type by meaning", q=f"Meaning='{FALLBACK_MEANING}'", limit=25)
    for i in r.json().get("items", []):
        found.setdefault(i["LookupType"], i)
    return [{"value": t, "label": i.get("Meaning") or t} for t, i in found.items()]


def _plain_checks(request):
    """Checks the page contract can't express (lengths, whole numbers), in plain words."""
    problems = []
    for key, n in MAX_LEN.items():
        v = request.get(key)
        if isinstance(v, str) and len(v) > n:
            label = next(f["label"] for f in SPEC["fields"] if f["key"] == key)
            problems.append({"field": key, "problem": "too_long",
                             "text": f"{label} can be at most {n} characters (it has {len(v)})."})
    seq = request.get("display_sequence")
    if seq is not None and (not float(seq).is_integer() or seq < 0):
        problems.append({"field": "display_sequence", "problem": "not_whole",
                         "text": "Position in the list must be a whole number, e.g. 30."})
    s, e = request.get("start_date"), request.get("end_date")
    if s and e and "today" not in (s.lower(), e.lower()) and e < s:
        problems.append({"field": "end_date", "problem": "before_start",
                         "text": "End date is before the start date."})
    if problems:
        raise page.PageError("INVALID_REQUEST", " ".join(p["text"] for p in problems), problems)


def run_request(request, progress):
    """--run: one order type through the normal flow (REST, fallback if REST is refused)."""
    oracle.check_environment()
    browser.refuse_production()
    _plain_checks(request)
    code = {k: request[k] for k in ("code", "meaning", "description", "enabled", "start_date",
                                    "end_date", "tag") if k in request}
    if "display_sequence" in request:
        code["display_sequence"] = int(request["display_sequence"])
    wanted_type, codes = parse_requirements(
        {"lookup_type": request.get("lookup_type") or FALLBACK_TYPES[0], "codes": [code]}, "page")
    # Read-only look first: an existing code is skipped; a meaning in use stops in plain words.
    # (If REST is refused here, the flow below falls back and checks the same itself.)
    try:
        type_item, _ = rest_lookup_type(wanted_type)
        _, existing = rest_codes(type_item)
    except RestUnavailable as e:
        print(f"REST read failed ({str(e)[:300]}); the run checks existence on its own.")
        type_item, existing = {"LookupType": wanted_type}, []
    have = {r["LookupCode"]: r for r in existing}
    c = codes[0]
    old = have.get(c["LookupCode"])
    if old is None:
        clash = [r["LookupCode"] for r in existing
                 if (r.get("Meaning") or "").lower() == c["Meaning"].lower()]
        if clash:
            why = f"Another order type ({clash[0]}) already uses the name '{c['Meaning']}'."
            raise page.PageError(
                "INVALID_REQUEST", f"{why} Please choose a different name.",
                {"message": why, "saved": "no", "registry_id": None,
                 "problems": [{"field": "meaning", "problem": "in_use", "used_by": clash[0], "value": c["Meaning"],
                               "reason": why, "text": why,
                               "suggestions": free_values("meaning", c, existing)}]})
    where = WHERE.format(type=type_item.get("Meaning") or type_item["LookupType"])
    if old is not None:
        progress.step("done")
        return {"text": f"Order type {c['LookupCode']} already exists in Oracle, so nothing "
                        "was changed.", "skipped": True,
                "created": {k: old.get(k) for k in REST_FIELDS}, "where": where}
    args = argparse.Namespace(check=False, check_ui=False, fallback=False, dry_run=False,
                              no_order_screen=False, headed=False)
    # A stop from here on says what was saved (error.detail "saved", 2026-10-25), so the page
    # can tell the user and leave a saved order type out of the failed-only sheet.
    messages, real_fail = [], oracle.fail

    def fail(message):
        messages.append(str(message))
        real_fail(message)
    oracle.fail = fail
    try:
        out = run_rest(args, wanted_type, codes, HERE, progress)
        if out is None:
            progress.step("creating", 50, "Creating it in Oracle another way (this takes a few minutes)")
            fallback_route(args, wanted_type, codes, HERE)
    except (SystemExit, Exception) as e:  # noqa: BLE001 - every stop gets the saved state
        if isinstance(e, page.PageError):
            raise
        if isinstance(e, RestRefused):
            # Oracle refused a value, nothing saved: a plain refusal the user can answer, never a repair
            reason = oracle_reason(str(e))
            field = refused_field(reason)
            sugg = free_values(field, c, existing) if field in ("meaning", "code") else []
            raise page.PageError("INVALID_REQUEST", f"Oracle refused order type {c['LookupCode']}: {reason} "
                                 "Nothing was saved in Oracle.",
                                 {"message": str(e), "saved": "no", "registry_id": None,
                                  "problems": [{"field": field, "problem": "refused",
                                                "value": request.get(field or ""), "reason": reason,
                                                "text": reason, "suggestions": sugg}]})
        msg = messages[-1] if messages else (f"{type(e).__name__}: {e}" if not isinstance(e, SystemExit)
                                             else "the run stopped")
        saved = SAVED["state"]
        text = {"no": "Nothing was saved in Oracle.",
                "yes": f"Order type {c['LookupCode']} was created in Oracle, but checking it didn't finish.",
                "maybe": f"Order type {c['LookupCode']} may have been created in Oracle."}[saved]
        code_ = page._classify(msg)
        raise page.PageError(code_, f"{page.ERRORS[code_]} {text}",
                             {"message": msg, "saved": saved, "registry_id": None})
    finally:
        oracle.fail = real_fail
    if out is None:
        progress.step("done")
        return {"text": f"Added order type {c['LookupCode']} ({c['Meaning']}) and checked it "
                        "in Oracle.", "created": {"LookupCode": c["LookupCode"],
                                                  "Meaning": c["Meaning"]}, "where": where}
    if not out["created"]:   # created by someone else in the meantime: skipped by the flow
        progress.step("done")
        return {"text": f"Order type {c['LookupCode']} already exists in Oracle, so nothing "
                        "was changed.", "skipped": True, "created": None, "where": where}
    got = out["found"].get(c["LookupCode"], {})
    progress.step("done")
    shown = ("and it shows on Create Order." if active_today(out["created"][0]) else
             "It isn't active today (" + ("not enabled" if got.get("EnabledFlag") == "N" else "outside its dates")
             + "), so Create Order doesn't offer it yet; that check was left out.")
    return {"text": f"Added order type {c['LookupCode']} ({c['Meaning']}), checked every value "
                    f"in Oracle{',' if shown.startswith('and') else '.'} {shown}",
            "created": {k: got.get(k) for k in REST_FIELDS}, "where": where}


PROVEN_CODE = re.compile(r"^[A-Za-z0-9_]+$")  # every code created so far looks like this (small letters:
                                               # teest, test123456 proven 2026-10-20/21)


def oracle_reason(err):
    """Oracle's own sentence from an HTTP 400 answer (the body after the status line)."""
    lines = [ln for ln in err.splitlines() if ln.strip()]
    body = " ".join(lines[2:]) if len(lines) > 2 else err      # oracle.try_call: request, status, body
    return " ".join(body.split())[:400]


def free_values(field, c, existing):
    """Suggestions for a refused meaning or code (2026-10-26): close variants no existing order type uses
    (meanings compared ignoring capitals, as this folder does; codes exactly, as Oracle does)."""
    if field == "meaning":
        used = {(r.get("Meaning") or "").lower() for r in existing}
        base = c["Meaning"]
        tries = [f"{base} ({c['LookupCode']})"] + [f"{base} {n}" for n in range(2, 10)]
        return [t for t in tries if t.lower() not in used and len(t) <= MAX_LEN["meaning"]][:3]
    if field == "code":
        used = {r.get("LookupCode") for r in existing}
        base = c["LookupCode"][:MAX_LEN["code"] - 2]
        return [f"{base}_{n}" for n in range(2, 10) if f"{base}_{n}" not in used][:3]
    return []


def refused_field(reason):
    """Which field an Oracle refusal is about (FND-7103: the meaning; a key clash or length: the code)."""
    t = reason.lower()
    if "meaning" in t:
        return "meaning"
    if "description" in t:
        return "description"
    if "tag" in t:
        return "tag"
    if "date" in t:
        return "end_date" if "end" in t else "start_date"
    if "sequence" in t:
        return "display_sequence"
    if "code" in t or "primary key" in t or "maximum length" in t:
        return "code"
    return None


def plan_command(argv):
    """--plan '<request or list of requests>' (read-only, 2026-10-25, for the page's preview of
    an upload sheet): what a --run of each request would do, by the same rules the run uses,
    reading the order types through REST (GET only). Requests are planned in order, as the page
    runs them one after another. One JSON line on stdout:
      {"ok": true, "results": [{"ok": true, "skipped": text | null, "existing": {...} | null,
        "problems": [{"key", "text", "fix"}], "found": {key: note}, "fills": {key: text}}]}
    or {"ok": false, "text"}. A single request (not a list) gives the single result."""
    import contextlib
    out = sys.stdout
    try:
        raw = json.loads(argv[1] if len(argv) > 1 else "")
        reqs = raw if isinstance(raw, list) else [raw]
        if not all(isinstance(r, dict) for r in reqs):
            raise ValueError("each request must be an object")
    except (ValueError, TypeError) as e:
        print(json.dumps({"ok": False, "text": f"The request couldn't be read ({e})."}), file=out)
        return 2
    results = []
    try:
        with contextlib.redirect_stdout(sys.stderr):
            oracle.check_environment()
            types = {}                  # requested list -> (type item, existing codes as plan rows)
            for req in reqs:
                wanted = req.get("lookup_type") or FALLBACK_TYPES[0]
                if wanted not in types:
                    try:
                        hit = [o["value"] for o in live_options("lookup_type")
                               if wanted.lower() in (o["value"].lower(), o["label"].lower())]
                    except RestUnavailable:
                        hit = []
                    item, _ = rest_lookup_type(hit[0] if len(hit) == 1 else wanted)
                    types[wanted] = (item, [as_plan_row(r) for r in rest_codes(item)[1]])
            planned = {}                # per list: the rows planned so far (later rows follow them)
            for req in reqs:
                wanted = req.get("lookup_type") or FALLBACK_TYPES[0]
                item, existing = types[wanted]
                res = {"ok": True, "skipped": None, "existing": None, "problems": [], "found": {}, "fills": {}}
                code, meaning = str(req.get("code") or ""), str(req.get("meaning") or "")
                seq = req.get("display_sequence")
                seq = str(seq) if seq not in (None, "") and str(seq).isdigit() else ""
                old = next((r for r in existing if r["LookupCode"] == code), None)   # case counts
                if code and old:
                    res["existing"] = old
                    res["skipped"] = (f"Order type {code} already exists in Oracle (name shown to users "
                                      f"'{old['Meaning']}', position {old['DisplaySequence'] or 'none'}), so it "
                                      "will be skipped; nothing is changed.")
                    results.append(res)
                    continue
                if code and not PROVEN_CODE.match(code):
                    res["found"]["code"] = ("Not proven: Oracle hasn't been tried yet with a code that has "
                                            "spaces or other signs. It is sent exactly as typed.")
                for key, n in MAX_LEN.items():     # in the preview too (2026-10-26; before: only at --run)
                    v = req.get(key)
                    if isinstance(v, str) and len(v) > n:
                        label = next(f["label"] for f in SPEC["fields"] if f["key"] == key)
                        res["problems"].append({"key": key, "text": f"{label} can be at most {n} characters "
                                                f"(it has {len(v)}).", "fix": f"Shorten it to {n} characters."})
                row = {"LookupCode": code, "Meaning": meaning, "DisplaySequence": seq}
                if meaning:
                    for _, used_by in meaning_clashes(existing, [row]):
                        res["problems"].append({"key": "meaning", "text": f"Another order type ({used_by}) "
                                                f"already uses the name '{meaning}' (capitals ignored).",
                                                "fix": "Choose a different Meaning."})
                before = planned.setdefault(wanted, [])
                (_, kind, n, used), = assign_sequences(existing + before, [row])
                top = lambda rows: max([int(r["DisplaySequence"]) for r in rows
                                        if str(r["DisplaySequence"]).isdigit()], default=0)
                if kind == "assigned":
                    res["fills"]["display_sequence"] = (
                        f"{n} (highest existing {top(existing)} + 1)" if n == top(existing) + 1 else
                        f"{n} (highest existing {top(existing)}; the rows above take up to {n - 1})")
                elif used:
                    res["found"]["display_sequence"] = (f"Also used by {', '.join(used)}; allowed, it only "
                                                        "changes the order of the list.")
                before.append(row)
                results.append(res)
    except (SystemExit, RestUnavailable, Exception) as e:  # noqa: BLE001 - one plain answer
        print(f"--plan failed: {type(e).__name__}: {e}", file=sys.stderr)
        print(json.dumps({"ok": False, "text": browser.failed_step_text(   # the real failed step (2026-10-26)
            "Oracle's order types couldn't be read just now.")}), file=out)
        return 1
    print(json.dumps({"ok": True, "results": results} if isinstance(raw, list) else results[0]), file=out)
    return 0


# ---------------------------------------------------------------- main

HERE = Path(__file__).resolve().parent


def main():
    if sys.argv[1:2] == ["--plan"]:                # read-only: the page's preview of a sheet
        sys.exit(plan_command(sys.argv[1:]))
    page.main(SPEC, options_for, run_request)   # --spec / --options / --run; else returns
    here = HERE
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(here / "ordertypes.json"), help="requirements JSON")
    ap.add_argument("--check", action="store_true",
                    help="read-only through REST: lookup type, codes, existence, meaning, "
                         "sequence; only GET calls")
    ap.add_argument("--check-ui", action="store_true",
                    help="read-only check of the fallback route's screens")
    ap.add_argument("--fallback", action="store_true",
                    help="skip REST and use the export/import fallback route")
    ap.add_argument("--no-order-screen", action="store_true",
                    help="skip the read-only Create Order check after a REST run")
    ap.add_argument("--dry-run", action="store_true", help="fallback route: export and build the zip, no import")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    args = ap.parse_args()

    oracle.check_environment()
    wanted_type, codes = load_requirements(args.file)
    print(f"{len(codes)} code(s) requested for lookup type {wanted_type} in {args.file}")

    if not (args.check_ui or args.fallback or args.dry_run):
        if run_rest(args, wanted_type, codes, here) is not None:
            return
    fallback_route(args, wanted_type, codes, here)


def run_rest(args, wanted_type, codes, here, progress=None):
    """Route 1 end to end: REST create + GET verify + the Create Order check. Returns
    {"lookup_type", "before", "created", "found"} or None when REST is unavailable
    (the caller then runs the fallback). progress: the page's progress lines (--run)."""
    try:
        before_type, _ = rest_lookup_type(wanted_type)
        _, before = rest_codes(before_type)
        if progress:
            progress.step("creating")
        lookup_type, created = rest_route(wanted_type, codes, args.check)
    except RestUnavailable as e:
        print(f"\nREST route failed:\n  {str(e)[:1500]}\nSwitching to the Playwright "
              "export/import fallback route.\n")
        return None
    out = {"lookup_type": lookup_type, "before": before, "created": created, "found": {}}
    if args.check or not created:
        return out
    if progress:
        progress.step("verifying")
    print("REST: verifying (GET every new code, compare all codes) ...")
    if not rest_verify(lookup_type, created, before, out["found"]):
        oracle.fail("REST verification failed - see FAIL lines above. Created codes are "
                    "left as they are (never deleted).")
    print("All requested codes created through REST and verified by GET.")
    if args.no_order_screen:
        return out
    today = SERVER_TODAY.isoformat() if SERVER_TODAY else None
    active = []
    for b in created:
        start = (b.get("StartDateActive") or "").replace("/", "-")
        end = (b.get("EndDateActive") or "").replace("/", "-")
        if not active_today(b):
            print(f"  NOTE  {b['LookupCode']}: not active on Oracle's today ({today}; enabled "
                  f"{b.get('EnabledFlag', 'Y')}, start {start or '-'}, end {end or '-'}), so "
                  "Create Order does not offer it; Create Order check skipped for it")
        else:
            active.append(b)
    if not active:
        return out
    browser.refuse_production()
    if progress:
        progress.step("order_screen", 92, "Checking that it shows on Create Order")
    work = oracle.init_work_dir(here)
    with browser.OracleUI(work, headless=not args.headed) as ui:
        print("Create Order check (read-only) ...")
        found = create_order_has_type(ui, [b["Meaning"] for b in active])
    if not all(found.values()):
        oracle.fail("A new order type is not offered on Create Order - see FAIL lines.")
    oracle.cleanup_work_dir()
    return out


def active_today(b):
    """Create Order only offers codes active on Oracle's today (enabled, inside their dates)."""
    today = SERVER_TODAY.isoformat() if SERVER_TODAY else None
    start = (b.get("StartDateActive") or "").replace("/", "-")
    end = (b.get("EndDateActive") or "").replace("/", "-")
    return b.get("EnabledFlag", "Y") == "Y" and not (today and ((start and start > today) or (end and end < today)))


def fallback_route(args, wanted_type, codes, here):
    """Route 2: Playwright export/import (unchanged, built for the Redwood Set Up page)."""
    browser.refuse_production()
    work = oracle.init_work_dir(here)

    with browser.OracleUI(work, headless=not args.headed) as ui:
        layout = setup_layout(ui)
        print(f"Fallback route: Setup and Maintenance shows the {layout} layout"
              + ("" if layout == "Redwood" else " (this route was built for Redwood and is not "
                 "yet re-proven on classic)"))
        if args.check_ui or args.check:
            print("Checking the fallback screens (read-only) ...")
            ui.check_actions(TASK, AREA, OFFERING)
            resolve_today(codes, check_on_screen(ui, wanted_type, codes))
            print("Check passed: export/import screens open, the lookup type and its codes show "
                  "on screen, Oracle's today read. Nothing was saved, submitted or created.")
            oracle.cleanup_work_dir()
            return
        if uses_today(codes):
            open_lookup(ui, wanted_type)
            today = oracle_today_on_screen(ui)
            leave_without_saving(ui)
            resolve_today(codes, today)
        print("Exporting (before) ...")
        before_zip, _ = ui.export_csv(TASK, AREA, OFFERING)
        before = read_zip(before_zip)
        lookup_type = find_lookup_type(before, wanted_type)
        if lookup_type != wanted_type:
            print(f"  NOTE  {wanted_type} not found; using {lookup_type} instead")
        existing = codes_of(before, lookup_type)
        print(f"Lookup type {lookup_type}: {len(existing)} existing code(s)")
        todo = plan_codes(existing, codes, lookup_type)
        if not todo:
            print("Nothing to create.")
            oracle.cleanup_work_dir()
            return
        tpl = template_code(existing)
        print(f"Row layout learned from existing code '{tpl['LookupCode']}'")
        new_rows = build_rows(before, lookup_type, todo, tpl)
        names = "_".join(c["LookupCode"] for c in todo)[:60]
        import_zip = build_import_zip(before, new_rows, work / f"import_{names}.zip")
        print(f"Built {import_zip.name}: {CODE_CSV} +{len(new_rows)}")
        if args.dry_run:
            print(f"Dry run: not importing. Files kept in {work}")
            return

        print("Importing ...")
        SAVED["state"] = "maybe"
        ui.import_csv(TASK, AREA, import_zip, OFFERING)
        SAVED["state"] = "yes"
        print("Exporting (after) to verify ...")
        after_zip, _ = ui.export_csv(TASK, AREA, OFFERING)
        print("Verifying files ...")
        files_ok = verify_files(before, read_zip(after_zip), lookup_type,
                                [{k: v for k, v in r.items() if k != PARENT} for r in new_rows])
        if not files_ok:
            oracle.fail("Verification failed (MISMATCH) - see FAIL lines above.")
        print("Checking on screen ...")
        screen_ok, shot = verify_screen(ui, lookup_type, todo)
        if not screen_ok:
            oracle.fail(f"On-screen check failed - see FAIL lines above. Screenshot: {shot}")

    print("All requested codes created and verified (files and screen).")
    oracle.cleanup_work_dir()


if __name__ == "__main__":
    main()
