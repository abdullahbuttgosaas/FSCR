"""Create organization customers from customers.json on Oracle's Create Customer form.

Route: Setup and Maintenance > Financials > Search Tasks "Create Customer"
(functional area Customers) > fill the form > Save and Close. There is no CSV
export/import for this task (its Actions entries are disabled) and no REST is used.
Uses the sign-in saved by common/login_once.py; the only manual step is that sign-in.

Per customer: search Manage Customers by name (names are not unique in Oracle: customers
with the same name are listed, never touched, and a NEW customer is still created) ->
check every drop-down value against the screen's own list (stop and list the valid
values when one doesn't match) -> fill, note the Registry ID the form shows, Save and
Close (Oracle's "Warning: Matching Organizations/Persons": always Option 2 "Create new",
never Option 1) -> verify the new customer by its Registry ID and read its account, site
and purposes back (Manage Customers, Edit Account, Edit Site; left with Cancel) -> check
the other customers in the name search are unchanged. A rerun of the same request after a
save (sign-in, repair) verifies the customer it saved instead of making a second one.

Failures keep screenshots and page text in "Customers/_work/"; it is deleted
after a verified success.

  python "Customers/browser_flow.py"             # full run (headless)
  python "Customers/browser_flow.py" --check     # validate + existence check, no save
  python "Customers/browser_flow.py" --headed    # same as full run, browser visible

Page interface (root CLAUDE.md > Page interface, common/page.py), one customer per run:
  python "Customers/browser_flow.py" --spec
  python "Customers/browser_flow.py" --options account_address_set | state | purposes.purpose | ...
  python "Customers/browser_flow.py" --run '{"name": "X", "account_address_set": "...", ...}'
  python "Customers/browser_flow.py" --existing '{"name": "X"}'   # read-only: same-name customers
  python "Customers/browser_flow.py" --check-address '{"name": "X", "city": ..., "state": ..., "postal_code": ...}'
                                                                 # read-only: Oracle's geography
"""
import argparse
import collections
import hashlib
import json
import os
import time
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import browser, oracle, page  # noqa: E402

OFFERING, AREA, TASK = "Financials", "Customers", "Create Customer"
MANAGE_TASK = "Manage Customers"
FORM_TITLE = "Create Organization Customer"
ADDRESS_SET_ICON = "[id$='setIdLovId::lovIconId']"
PURPOSE_SELECT = "select[id$='SiteUseCode::content']"
# Manage Customers result tables (organizations, accounts of the selected one,
# sites of the selected account), told apart by their region ids.
ORG_TABLE, ACCOUNT_TABLE, SITE_TABLE = "pt_r1:0:AT1", "pt_r3:0:AT1", "pt_r4:0:AT1"
TODAY_WORD = "today"
PREFIX_LEN = 3   # existing customers whose name starts like the new one are compared

# key: (screen label, kind, where it is read back)
#   kinds: text, area (multi-line), select, date, check, geo (geography list), lov
#   read back on: org / account / site page; "set" = Manage Customers sites table
FIELDS = {
    "name": ("Name", "text", "org"),
    "duns_number": ("D-U-N-S Number", "text", "org"),
    "taxpayer_id": ("Taxpayer Identification Number", "text", "org"),
    "account_description": ("Account Description", "text", "account"),
    "account_type": ("Account Type", "select", "account"),
    "customer_class": ("Customer Class", "select", "account"),
    "account_established_date": ("Account Established Date", "date", "account"),
    "account_termination_date": ("Account Termination Date", "date", "account"),
    "account_notes_other": ("Account Notes Other", "area", "account"),
    "shipping_instructions": ("Shipping Instrustions", "area", "account"),  # Oracle's spelling
    "customer_agreement": ("Customer Agreement", "area", "account"),
    "account_address_set": ("Account Address Set", "set", "set"),
    "address_from_date": ("From Date", "date", "site"),
    "address_to_date": ("To Date", "date", "site"),
    "site_name": ("Site Name", "text", "site"),
    "mail_stop": ("Mail Stop", "text", "site"),
    "country": ("Country", "select", "site"),
    "address_line_1": ("Address Line 1", "text", "site"),
    "address_line_2": ("Address Line 2", "text", "site"),
    "state": ("State", "geo", "site"),
    "city": ("City", "geo", "site"),
    "postal_code": ("Postal Code", "geo", "site"),
    "responsible_mineral_status": ("Responsible Mineral Status", "lov", "site"),
    "address_note": ("Address", "text", "site"),       # extra "Address" field below the address
    "url": ("URL", "text", "site"),
    "contact_email": ("ContactEmail", "text", "site"),
    "authorizer": ("Authorizer", "text", "site"),
    "supplier_site_id": ("Supplier Site ID", "text", "site"),
    "sales_tax_geocode": ("Sales Tax Geocode", "text", "site"),
    "sales_tax_inside_city_limits": ("Sales Tax Inside City Limits", "check", "site"),
    "customer_category_code": ("Customer Category Code", "select", "site"),
    "site_language": ("Site Language", "select", "site"),
    "translated_customer_name": ("Translated Customer Name", "text", "site"),
    "key_account": ("Key Account", "check", "site"),
    "trading_partner_identifier": ("Trading Partner Identifier", "text", "site"),
    "edi_location_code": ("EDI Location Code", "text", "site"),
}
REQUIRED = ("name", "account_address_set", "supplier_site_id")
# Fill order on the form: country first (it redraws the address fields), state
# before city before postal code (each list is narrowed by the one before).
ORDER = ["name", "duns_number", "taxpayer_id", "account_description", "account_type",
         "customer_class", "account_established_date", "account_termination_date",
         "account_notes_other", "shipping_instructions", "customer_agreement",
         "account_address_set", "address_from_date", "address_to_date", "site_name",
         "mail_stop", "country", "address_line_1", "address_line_2", "state", "city",
         "postal_code", "responsible_mineral_status", "address_note", "url",
         "contact_email", "authorizer", "supplier_site_id", "sales_tax_geocode",
         "sales_tax_inside_city_limits", "customer_category_code", "site_language",
         "translated_customer_name", "key_account", "trading_partner_identifier",
         "edi_location_code"]
assert set(ORDER) == set(FIELDS)
PURPOSE_KEYS = {"purpose", "from_date", "to_date", "primary", "bill_to_site"}
# Address Purposes row (2026-10-23): Primary = the table's "Set Primary" action on the selected
# row (a "Primary Purpose" icon then shows); Bill-to Site = a list field Oracle offers only on
# a Ship to row (hidden on Bill to, Deliver to, Sold to, Statements), listing this customer's
# Bill to addresses ("1 Main Street,CUPERTINO, CA 95014"). See CLAUDE.md > Known gotchas.
BILL_TO_INPUT = "input[id$='billToSiteUseIdId::content']"
BILL_TO_ICON = "[id$='billToSiteUseIdId::lovIconId']"
PRIMARY_ICON = "img[title='Primary Purpose']"

# Person customers: Customer Type "Person" turns the same form into "Create Person
# Customer". Person Information replaces Name and D-U-N-S Number; everything else is
# the same as for organizations.
PERSON_NAME_FIELDS = {
    "prefix": ("Prefix", "select", "org"),
    "first_name": ("First Name", "text", "org"),
    "middle_name": ("Middle Name", "text", "org"),
    "last_name": ("Last Name", "text", "org"),
    "suffix": ("Suffix", "text", "org"),
}
PERSON_FIELDS = dict(PERSON_NAME_FIELDS, **{k: v for k, v in FIELDS.items()
                                            if k not in ("name", "duns_number")})
PERSON_ORDER = list(PERSON_NAME_FIELDS) + [k for k in ORDER if k not in ("name", "duns_number")]
assert set(PERSON_ORDER) == set(PERSON_FIELDS)
TYPES = {
    "Organization": {"fields": FIELDS, "order": ORDER, "title": FORM_TITLE,
                     "required": REQUIRED, "search_label": "Organization Name",
                     "results": ORG_TABLE},
    "Person": {"fields": PERSON_FIELDS, "order": PERSON_ORDER, "title": "Create Person Customer",
               "required": ("first_name", "account_address_set", "supplier_site_id"),
               "search_label": "Name",
               "results": "pt_r2:0:AT1"},   # person results sit in another table region
}


def person_name(want):
    """The name Oracle shows for a person customer: first, middle, last name and suffix
    (seen 2026-10-20: "ZZ_TEST_9231 Q Tester Jr."). The prefix (Ms.) is not part of
    it; Manage Customers shows it in its own column, Salutary Introduction."""
    return " ".join(want[k] for k in ("first_name", "middle_name", "last_name", "suffix")
                    if want.get(k))


# ---------------------------------------------------------------- requirements

def as_screen(d):
    return f"{d.month}/{d.day}/{d.strftime('%y')}"


def screen_date(v, where, key):
    """YYYY-MM-DD -> the form's m/d/yy. "today" stays a marker until the form is open:
    it becomes Oracle's today (the form's own default date) minus one day."""
    if v == TODAY_WORD:
        return TODAY_WORD
    try:
        d = date.fromisoformat(v)
    except (TypeError, ValueError):
        oracle.fail(f"{where}: '{key}' must be a date as YYYY-MM-DD or \"today\", got {v!r}")
    return as_screen(d)


def resolve_today(ui, cust):
    """Oracle's today = the default From Date the Create Customer form shows when it
    opens (never the PC clock). "today" in the request = that day minus one."""
    shown = ui.field("From Date").input_value().strip()
    if not shown:
        ui.fail("today", "The form showed no default From Date to read Oracle's today from.")
    today = ui.parse_screen_date(shown)
    day = as_screen(today - timedelta(days=1))
    items = [(cust["want"], k) for k in cust["want"]] +             [(pu, k) for pu in cust["purposes"] for k in ("from_date", "to_date")]
    for obj, key in items:
        if obj.get(key) == TODAY_WORD:
            obj[key] = day
            print(f"  NOTE  {key} \"today\" -> {day} (Oracle's today {shown} minus one day)")
    return today


def load_requirements(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        oracle.fail(f"Cannot read {path}: {e}")
    return parse_requirements(data, path)


def parse_requirements(data, path):
    """The request (file contents or a page request) -> normalised customers."""
    raw = data.get("customers")
    if not isinstance(raw, list) or not raw:
        oracle.fail(f"{path} must contain a non-empty 'customers' list")
    out, names = [], set()
    for c in raw:
        if not isinstance(c, dict):
            oracle.fail(f"{path}: every customer must be an object")
        where = f"customer {c.get('name') or c.get('first_name')!r}"
        ctype = c.get("customer_type", "Organization")
        if ctype not in TYPES:
            oracle.fail(f"{where}: customer_type {ctype!r} is not one of the screen's values: "
                        f"{', '.join(TYPES)}. Ask the user which one.")
        fields = TYPES[ctype]["fields"]
        unknown = set(c) - set(fields) - {"purposes", "customer_type"}
        if unknown:
            oracle.fail(f"{where}: unknown field(s) {sorted(unknown)} for a {ctype} customer; "
                        f"allowed: {sorted(fields) + ['customer_type', 'purposes']}")
        missing = [fields[k][0] for k in TYPES[ctype]["required"] if c.get(k) in (None, "")]
        if missing:
            oracle.fail(f"{where}: missing required value(s): {', '.join(missing)}. "
                        "Ask the user for them in one message.")
        want = {}
        for key, (label, kind, _) in fields.items():
            v = c.get(key)
            if v is None:
                continue
            if kind == "check":
                if not isinstance(v, bool):
                    oracle.fail(f"{where}: '{key}' must be true or false")
                want[key] = v
            elif kind == "date":
                want[key] = screen_date(v, where, key)
            else:
                if not isinstance(v, str) or v != v.strip() or not v:
                    oracle.fail(f"{where}: '{key}' must be non-empty text without outer spaces")
                want[key] = v
        name = want["name"] if ctype == "Organization" else person_name(want)
        # Names are not unique in Oracle, so two customers may share one; the same request
        # twice is a mistake. The key also finds a customer an earlier try of it saved.
        key = hashlib.sha1(json.dumps(c, sort_keys=True).encode("utf-8")).hexdigest()[:16]
        if key in names:
            oracle.fail(f"{where}: listed twice with the same values")
        names.add(key)
        purposes = []
        for pu in c.get("purposes") or []:
            if not isinstance(pu, dict) or not pu.get("purpose") or set(pu) - PURPOSE_KEYS:
                oracle.fail(f"{where}: each purpose needs 'purpose' (and optional "
                            "'from_date', 'to_date', 'primary', 'bill_to_site'), got {pu!r}")
            if not isinstance(pu.get("primary", False), bool):
                oracle.fail(f"{where}: purpose {pu['purpose']!r}: 'primary' must be true or false")
            bill = pu.get("bill_to_site")
            if bill is not None and (not isinstance(bill, str) or not bill or bill != bill.strip()):
                oracle.fail(f"{where}: purpose {pu['purpose']!r}: 'bill_to_site' must be non-empty "
                            "text without outer spaces")
            purposes.append({"purpose": pu["purpose"],
                             "from_date": screen_date(pu["from_date"], where, "purpose from_date")
                             if pu.get("from_date") else "",
                             "to_date": screen_date(pu["to_date"], where, "purpose to_date")
                             if pu.get("to_date") else "",
                             "primary": pu.get("primary", False), "bill_to_site": bill or ""})
        # Oracle keeps one Primary per type of purpose: refuse two before anything is opened
        primaries = collections.Counter(p["purpose"].lower() for p in purposes if p["primary"])
        for kind, n in primaries.items():
            if n > 1:
                shown = next(p["purpose"] for p in purposes if p["purpose"].lower() == kind)
                oracle.fail(f"{where}: only one {shown} purpose can be Primary, but {n} are marked "
                            "Primary. Nothing was saved. Ask the user which one is the Primary.")
        if len({p["purpose"].lower() for p in purposes}) != len(purposes):
            oracle.fail(f"{where}: a purpose is listed twice")
        out.append({"want": want, "purposes": purposes, "type": ctype, "name": name,
                    "fields": fields, "order": TYPES[ctype]["order"], "key": key})
    return out


# ---------------------------------------------------------------- reading the screen

ROWS_JS = r"""(part) => [...document.querySelectorAll('tr[_afrrk]')]
  .filter(r => r.offsetWidth && (r.closest('[id$="::db"]') || {id: ''}).id.includes(part))
  .map(r => [...r.querySelectorAll('td')].filter(td => !td.querySelector('td')).map(td => {
      const inp = [...td.querySelectorAll('input:not([type=hidden]), select, textarea')];
      if (!inp.length) return td.innerText.trim();
      return inp.map(i => i.tagName === 'SELECT' ? (i.options[i.selectedIndex] || {text: ''}).text
                          : i.type === 'checkbox' ? String(i.checked) : i.value).join(' ').trim();
  }))"""

PURPOSE_HEADS_JS = r"""() => [...document.querySelectorAll('[id*="sitedet:0:AT1"] th')]
  .filter(e => e.offsetWidth).map(e => e.innerText.trim())"""

# Edit Site purposes: each row's shown values and whether it carries the Primary icon
PURPOSE_PRIMARY_JS = r"""() => [...document.querySelectorAll('[id*="sitedet:0:AT1"] tr[_afrrk]')]
  .filter(r => r.offsetWidth).map(r => ({
     cells: [...r.querySelectorAll('td')].filter(td => !td.querySelector('td')).map(td => {
        const s = td.querySelector('select');
        return s ? (s.options[s.selectedIndex] || {text: ''}).text.trim() : td.innerText.trim(); }),
     primary: !!r.querySelector("img[title*='Primary']"),
     bill_to: (r.querySelector("input[id$='billToSiteUseIdId::content']") || {value: ''}).value.trim()}))"""

LABEL_TEXT_JS =r"""(label) => {
  for (const e of document.querySelectorAll('label, td, span')) {
    if (!e.offsetWidth || e.innerText.trim() !== label || e.closest('[id*=":_ATp:"]')) continue;
    let cell = e.closest('td') || e;
    let next = cell.nextElementSibling;
    while (next && !next.innerText.trim()) next = next.nextElementSibling;
    if (next) return next.innerText.trim();
  }
  return null;
}"""


def table_rows(ui, part):
    return ui.page.evaluate(ROWS_JS, part)


def cells(row):
    return [c for c in row if c not in ("", None)]


def read_value(ui, label, kind):
    el = ui.field(label)
    if not el.count():
        return None
    if kind == "select":
        return el.evaluate("e => (e.options[e.selectedIndex] || {text: ''}).text").strip()
    if kind == "check":
        return el.is_checked()
    return el.input_value()


# ---------------------------------------------------------------- Setup and Maintenance, either layout

_LAYOUT = {}   # detected once per run: "classic" or "Redwood"


def setup_layout(ui):
    """Which Setup and Maintenance layout Oracle shows: the Redwood "Set Up <offering>"
    page (2026-10-20) or the classic "Setup: <offering>" page (back on 2026-10-21).
    Opens Setup and Maintenance and waits for either one's controls."""
    page = ui.page
    page.goto(f"{oracle.HOST}{browser.SETUP_PATH}", wait_until="domcontentloaded", timeout=120000)
    ui.settle()
    wait_signed_in(ui)
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
    if _LAYOUT.get("layout") != layout:
        print(f"  Setup and Maintenance layout: {layout}")
    _LAYOUT["layout"] = layout
    return layout


def wait_signed_in(ui, seconds=30):
    """The saved sign-in passes through Oracle's sign-in service, which signs it back in by
    script; on 2026-10-23 a run looked too early and saw a blank page there, so it stopped
    with "sign-in expired" although the sign-in was valid (customer 3 of a sheet; the check
    a minute later said valid). Wait for the redirect to come back to Oracle before deciding."""
    for _ in range(seconds):
        if browser.is_signed_in(ui.page.url):
            return
        ui.page.wait_for_timeout(1000)
    ui.check_signed_in()


def classic_offering(ui, offering):
    """Classic page: switch the Offering drop-down to `offering` (already open page)."""
    page = ui.page
    title = f"Setup: {offering}"
    heading = page.get_by_text(re.compile(r"^Setup: ")).first
    heading.wait_for(timeout=60000)
    if heading.inner_text().strip() == title:
        return
    ui.log(f"switching offering from '{heading.inner_text().strip()}' to '{offering}'")
    options = page.locator("li[role=option]:visible")
    option = options.filter(has_text=re.compile(rf"^{re.escape(offering)}$"))

    def pick(attempt):               # 2026-10-26: a lost click leaves the old offering (shared retry helper)
        if not option.count():
            ui.click(page.locator("a[aria-label='Offering']"), "Offering drop-down")
        try:
            option.first.wait_for(timeout=20000)
        except Exception:
            if options.count():      # the list opened without it: not a lost click
                ui.fail("offering", f"Offering '{offering}' is not in the Offering list.")
            raise
        ui.click(option.first, f"offering {offering}")
        ui.settle()
    ui.retry(f"Setup page did not switch to the offering '{offering}'", pick,
             lambda timeout: page.get_by_text(title, exact=True).first.wait_for(timeout=timeout),
             wait=30000, last_wait=60000)


def classic_search_task(ui, task, area, heading=None):
    """Classic page: Search Tasks > the result in `area` > the task link (the area's
    task list renders lazily, so the task is reached through Search Tasks). With `heading`, the task link is
    clicked again until that page heading shows.
    2026-10-26: Oracle's busy Setup page drops a search or a click made too early (the text stays in the box, no
    results window; the task list stays with its row highlighted), so every step is checked and done again, up to
    3 tries, by the shared retry helper (ui.retry); none of them saves anything."""
    page = ui.page
    box = page.get_by_label("Search Tasks").first
    box.wait_for(timeout=60000)
    results = page.get_by_text("Search Task Results").first

    def search(attempt):
        box.fill(task)
        box.press("Enter")
        ui.settle()
    ui.retry(f"Search Tasks did not show results for '{task}'", search,
             lambda timeout: results.wait_for(timeout=timeout))
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
    link = page.locator(f"a:text-is('{task}'):visible").first

    def pick(attempt):
        if results.is_visible():
            ui.click(result_link(), f"search result {task} ({area})")
        ui.settle()

    def listed(timeout):             # the results window closed and the area's task list shows the task
        results.wait_for(state="hidden", timeout=timeout)
        link.wait_for(timeout=timeout)
    ui.retry(f"Setup page did not show {task} in the '{area}' task list", pick, listed, wait=30000, last_wait=60000)

    def open_(attempt):
        again = ui.page.locator(f"a:text-is('{task}'):visible").first
        if attempt == 1 or again.count():
            ui.click(again, f"task {task}" + (" (again)" if attempt > 1 else ""))
        ui.settle()
        ui.use_newest_page()
    if heading:
        ui.retry(f"Setup page did not open {task}", open_,
                 lambda timeout: ui.wait_heading(heading, timeout=timeout), wait=40000, last_wait=90000)
    else:
        open_(1)


def open_task_page(ui, task, area, offering, heading=None):
    """Open a task's own page on whichever layout Oracle shows. Redwood: the shared
    helper; classic: this folder's classic steps (2026-10-21), the task link checked by `heading`."""
    if setup_layout(ui) == "Redwood":
        ui.search_task(task, area, offering)
        return
    classic_offering(ui, offering)
    classic_search_task(ui, task, area, heading)


def search_customers(ui, name, ctype="Organization"):
    """Manage Customers search by name (Oracle matches the start of the name), for
    organizations or persons. Returns the result rows as dicts."""
    label = TYPES[ctype]["search_label"]
    with ui.step(f"search Manage Customers for {name!r}"):
        open_task_page(ui, MANAGE_TASK, AREA, OFFERING, heading=MANAGE_TASK)
        ui.wait_heading(MANAGE_TASK)
        kind = ui.field("Customer Type")
        if kind.count() and read_value(ui, "Customer Type", "select") != ctype:
            ui.choose(kind, ctype)
            ui.page.wait_for_timeout(2000)
        if not ui.field(label).count():   # search panel collapsed after an earlier search
            ui.retry("Manage Customers did not open its search panel",
                     lambda attempt: ui.field(label).count() or
                     ui.click(ui.page.get_by_text("Search", exact=True).first, "Search panel"),
                     lambda timeout: ui.field(label).wait_for(timeout=timeout), wait=10000, last_wait=30000)
        box = ui.field(label)
        box.fill(name)
        table = TYPES[ctype]["results"]
        empty, shown = {"n": 0}, {}

        def names_now():
            return [" ".join(cells(r)[1].split()).upper() for r in table_rows(ui, table) if len(cells(r)) >= 2]

        def search(attempt):
            shown["before"], shown["sent"] = names_now(), False
            button = ui.page.get_by_role("button", name="Search", exact=True).first
            source = (button.get_attribute("id") or "").split("::")[0]

            def sent(request):        # Oracle's page sent this Search to the server: the click was not lost
                if source and request.method == "POST" and source in (request.post_data or ""):
                    shown["sent"] = True
            ui.page.on("request", sent)
            try:
                ui.click(button, "Search")
                ui.settle()
            finally:
                ui.page.remove_listener("request", sent)

        def answered(timeout):        # 2026-10-26: rows of this name; no rows when Oracle got the Search (else twice)
            ui.page.locator(f"[id*='{table}'][id$='::db']").first.wait_for(timeout=timeout)
            ui.page.wait_for_timeout(2000)
            end = time.time() + min(timeout, 3000 if shown["sent"] else 15000) / 1000
            want = " ".join(name.split()).upper()
            while True:
                names = names_now()
                if any(n.startswith(want) for n in names):
                    return True
                if time.time() > end:
                    break
                ui.page.wait_for_timeout(1000)
            if names:                  # new rows answer the search; the earlier search's rows mean it was lost
                return names != shown["before"] or shown["sent"]
            empty["n"] += 1
            return shown["sent"] or empty["n"] >= 2
        ui.retry(f"Manage Customers did not answer the search for {name!r}", search, answered,
                 wait=60000, last_wait=90000)
    rows = []
    for r in table_rows(ui, table):
        c = cells(r)
        if len(c) >= 2:
            rows.append({"registry_id": c[0], "name": c[1], "rest": tuple(c[2:]), "table": table})
    return rows


def select_org(ui, registry_id, table=ORG_TABLE):
    """Select a result row so the Accounts and Sites tables show its data."""
    row = ui.page.locator(f"[id*='{table}'] tr[_afrrk]").filter(
        has=ui.page.locator(f"a:text-is('{registry_id}')")).first
    got = {}

    def pick(attempt):
        ui.click(row.locator("td").last, f"result row {registry_id}")
        ui.settle()
        ui.page.wait_for_timeout(3000)

    def shown(timeout):              # 2026-10-26: a lost click shows no accounts and sites (soft: then as before)
        end = time.time() + timeout / 1000
        while True:
            got["a"] = [cells(r) for r in table_rows(ui, ACCOUNT_TABLE) if cells(r)]
            got["s"] = [cells(r) for r in table_rows(ui, SITE_TABLE) if cells(r)]
            if got["a"] and got["s"] or time.time() > end:
                return bool(got["a"] and got["s"])
            ui.page.wait_for_timeout(1000)
    ui.retry(f"Manage Customers did not show the accounts of {registry_id}", pick, shown,
             wait=5000, last_wait=15000, soft=True)
    return got["a"], got["s"]


# ---------------------------------------------------------------- filling the form

def address_sets(ui):
    """[(code, name, description)] from the Account Address Set search dialog."""
    rows = ui.lov_search_all(ui.page.locator(ADDRESS_SET_ICON).first, "Account Address Set")
    out = []
    for r in rows:
        r = [c for c in r if "\t" not in c]       # drop whole-row texts, keep the cells
        if r:
            out.append((r[0], r[1] if len(r) > 1 else "", r[2] if len(r) > 2 else ""))
    return out


def resolve_address_set(sets, wanted):
    codes = {s[0]: s for s in sets}
    names = {}
    for s in sets:
        names.setdefault(s[1], []).append(s)
    hit = ui_match(wanted, list(codes))
    if hit:
        return codes[hit]
    hit = ui_match(wanted, list(names))
    if hit and len(names[hit]) == 1:
        return names[hit][0]
    listing = "\n    ".join(f"{s[1]} (code {s[0]})" for s in sets)
    oracle.fail(f"The account address set {wanted!r} is not one of the values on the screen. "
                f"Ask the user to pick one of these {len(sets)} (name or code):\n    {listing}")


ui_match = browser.OracleUI.match_value


def choose_select(ui, label, wanted, what):
    sel = ui.field(label)
    if not sel.count():
        ui.fail("field", f"The form has no '{label}' field here (for {what}).")
    options = [o for o in ui.select_options(sel) if o]
    hit = ui_match(wanted, options)
    if hit is None:
        oracle.fail(f"{what}: {wanted!r} is not one of the screen's values. Ask the user to "
                    f"pick one of: {', '.join(options) or '(the list is empty)'}")
    ui.choose(sel, hit)
    return hit


def late_dialog(ui, value, what, seconds=6):
    """Oracle sometimes opens a list field's choice dialog (e.g. State "CA": CA or
    CALIFORNIA) only after the shared helper stopped waiting. Wait a little longer;
    if it appears, pick the exact match like the helper does, else close it."""
    for _ in range(seconds * 2):
        dialogs = ui.lov_dialogs()
        if dialogs.count():
            dlg = dialogs.last
            rows = ui.lov_rows(dlg)
            hit = ui_match(value, [c for r in rows for c in r])
            if hit is None:
                ui.close_lov_dialogs()
                return False, rows
            cell = dlg.locator("tr[_afrrk] td:visible").filter(
                has_text=re.compile(rf"^\s*{re.escape(hit)}\s*$")).first
            ui.click(cell, f"{what} value {hit}")
            ui.click(dlg.get_by_role("button", name="OK", exact=True), f"{what} OK")
            ui.settle()
            ui.log(f"{what}: picked {hit!r} in a late search dialog")
            return True, rows
        ui.page.wait_for_timeout(500)
    return True, []


def wait_redraw(ui, handle, seconds=10):
    """Another country redraws the address fields; wait until the old Address Line 1
    is gone (replaced) so later fills land in the new fields. No redraw: carry on."""
    ui.settle()
    if handle is None:
        return
    for _ in range(seconds * 2):
        try:
            if not handle.evaluate("e => e.isConnected"):
                break
        except Exception:
            break
        ui.page.wait_for_timeout(500)
    ui.settle()


def set_date(ui, el, value):
    el.fill(value)
    el.press("Tab")
    ui.settle()


PLACE_KEYS = ("state", "city", "postal_code")


def fill_form(ui, cust, sets):
    page, want = ui.page, cust["want"]
    us = want.get("country", "United States") == "United States"
    places_done = False
    for key in cust["order"]:
        if key not in want:
            continue
        label, kind, _ = cust["fields"][key]
        value = want[key]
        if us and key in PLACE_KEYS:
            # v2 (2026-10-26): State, City and Postal Code through their search dialogs, the row picked by its
            # columns (pick_places, the same path as the preview); a place Oracle doesn't have raises
            # PlaceRefused with suggestions, before anything is saved
            refuse = os.environ.get("CUSTOMERS_TEST_REFUSE_CITY")
            if refuse and _up(want.get("city")) == _up(refuse) and not places_done:
                # testing only: Oracle made to refuse this city, as a value refusal would come back
                raise PlaceRefused({"key": "city", "text": f"test switch: Oracle refused City '{want.get('city')}'.",
                                    "suggestions": ["SANTA CLARA", "SAN JOSE"], "fix": "Pick a city Oracle has."})
            if not places_done:
                with ui.step("choose State, City and Postal Code in Oracle's lists"):
                    got = pick_places(ui, {k: want.get(k) for k in PLACE_KEYS}, choose=True)
                for k in PLACE_KEYS:
                    if got.get(k):
                        want[k] = got[k]
                for n in got.get("notes") or []:
                    print(f"  NOTE  {n}")
                places_done = True
            continue
        with ui.step(f"fill {label}"):
            if kind == "set":
                code, name, _ = resolve_address_set(sets, value)
                ok, rows = ui.lov_type(ui.field(label), code, label)
                if not ok or ui.field(label).input_value() != code:
                    ui.fail("set", f"Oracle did not accept the account address set {code}.")
                cust["set_name"] = name
                continue
            el = ui.field(label)
            if not el.count():
                ui.fail("field", f"The form has no '{label}' field "
                                 f"(country {want.get('country', 'United States')}).")
            if kind == "select" and key == "country":
                old = ui.field("Address Line 1")
                handle = old.element_handle() if old.count() else None
                want[key] = choose_select(ui, label, value, label)
                wait_redraw(ui, handle)
            elif kind == "select":
                want[key] = choose_select(ui, label, value, label)
            elif kind == "check":
                if el.is_checked() != value:
                    ui.set_check(el, value, label)
            elif kind == "date":
                set_date(ui, el, value)
            elif kind in ("geo", "lov"):
                ok, rows = ui.lov_type(el, value, label)
                if ok and not rows:
                    ok, rows = late_dialog(ui, value, label)
                if not ok:
                    shown = sorted({c for r in rows for c in r})[:30]
                    where = (" in Oracle's geography for this country. Oracle only accepts places "
                             "its geography already has; a missing one cannot be created here."
                             if kind == "geo" else " in Oracle's list.")
                    oracle.fail(f"{label}: {value!r} does not exist{where}"
                                + (f" Oracle's search for it showed: {', '.join(shown)}." if shown else
                                   " Oracle's search for it found nothing.")
                                + " Nothing was saved. Ask the user to pick a value Oracle knows.")
            else:
                el.fill(value)
                el.press("Tab")
                ui.settle()
            if kind not in ("set", "select", "check"):
                err = ui.field_error(ui.field(label))
                if err:
                    oracle.fail(f"{label}: Oracle does not accept {value!r} ({err}). Nothing was "
                                "saved. Ask the user for a valid value.")
    # A late redraw of the address (after another country) can empty fields already
    # filled (2026-10-21, Pakistan): fill those once more.
    for key in cust["order"]:
        label, kind, _ = cust["fields"][key]
        if key not in want or kind not in ("text", "geo", "lov") or not want[key]:
            continue
        el = ui.field(label)
        if el.count() and el.input_value() == "":
            with ui.step(f"fill {label} again (the address was redrawn)"):
                if kind == "text":
                    el.fill(want[key])
                    el.press("Tab")
                    ui.settle()
                else:
                    ok, rows = ui.lov_type(el, want[key], label)
                    if ok and not rows:
                        late_dialog(ui, want[key], label)
    for i, pu in enumerate(cust["purposes"], 1):
        with ui.step(f"add purpose {pu['purpose']}"):
            ui.click(page.locator("[title='Add Row']:visible").last, "Address Purposes Add Row")
            ui.settle()
            empty = None
            for _ in range(20):
                for s in page.locator(f"{PURPOSE_SELECT}:visible").all():
                    if not s.evaluate("e => (e.options[e.selectedIndex] || {text: ''}).text").strip():
                        # by its own id: a new row goes on top, so a position would move
                        # to another row (2026-10-23)
                        empty = page.locator(f"[id='{s.get_attribute('id')}']")
                        break
                if empty:
                    break
                page.wait_for_timeout(500)
            if empty is None:
                ui.fail("purpose", "No new Address Purposes row appeared.")
            pu["select_id"] = empty.get_attribute("id")
            options = [o for o in ui.select_options(empty) if o]
            hit = ui_match(pu["purpose"], options)
            if hit is None:
                oracle.fail(f"Purpose {pu['purpose']!r} is not one of the screen's values. Ask "
                            f"the user to pick one of: {', '.join(options)}")
            pu["purpose"] = hit
            ui.choose(empty, hit)
            row = empty.locator("xpath=ancestor::tr[1]")
            if pu["from_date"]:
                set_date(ui, row.locator("input[id$='inputDate2::content']").first, pu["from_date"])
            if pu["to_date"]:
                set_date(ui, row.locator("input[id$='inputDate3::content']").first, pu["to_date"])
            pu["from_shown"] = row.locator("input[id$='inputDate2::content']").first.input_value()
    # Primary first, then Bill-to Site last: Set Primary after a Bill-to Site was set made Oracle
    # say "Attribute SetId ... CustomerAccountSiteUseviaSite is required" (2026-10-23).
    # The same error also came with no Bill-to Site set (ZZ_TEST_3727, Bill to + Ship to both
    # Primary, 2026-10-23). A purpose that is the only one of its type is made Primary by Oracle
    # on save, so Set Primary is clicked only when its type is there more than once; the
    # verification still reads Primary back on Edit Site.
    kinds = collections.Counter(p["purpose"].lower() for p in cust["purposes"])
    for pu in cust["purposes"]:
        if pu.get("primary") and kinds[pu["purpose"].lower()] == 1:
            ui.log(f"{pu['purpose']} is the only purpose of its type: Oracle makes it Primary on save")
        elif pu.get("primary"):
            with ui.step(f"set purpose {pu['purpose']} as Primary"):
                set_primary(ui, pu)
    # Bill-to Site after every row is in: its list holds this customer's Bill to addresses and
    # Oracle keeps the list from the first time it is opened (2026-10-23). A Ship to row with
    # Bill-to Site left empty gets the one address of the list when the customer has a Bill to
    # purpose (2026-10-23: a customer made here has exactly one address).
    has_bill_to = any(p["purpose"].lower() == "bill to" for p in cust["purposes"])
    for pu in cust["purposes"]:
        if pu.get("bill_to_site") or (pu["purpose"].lower() == "ship to" and has_bill_to):
            with ui.step(f"set Bill-to Site of purpose {pu['purpose']}"):
                set_bill_to_site(ui, pu)


SELECTED_TEXT = "e => (e.options[e.selectedIndex] || {text: ''}).text"


def purpose_row(ui, pu):
    """The row of this purpose: by its select's id, checked against the purpose it shows
    (purposes are unique per customer), else found by that purpose."""
    sel = ui.page.locator(f"[id='{pu['select_id']}']")
    if sel.count() and sel.first.evaluate(SELECTED_TEXT).strip() == pu["purpose"]:
        return sel.first.locator("xpath=ancestor::tr[1]")
    for s in ui.page.locator(f"{PURPOSE_SELECT}:visible").all():
        if s.evaluate(SELECTED_TEXT).strip() == pu["purpose"]:
            return ui.page.locator(f"[id='{s.get_attribute('id')}']").locator("xpath=ancestor::tr[1]")
    ui.fail("purpose", f"The {pu['purpose']} row is no longer in Address Purposes.")


def set_bill_to_site(ui, pu):
    """The row's Bill-to Site: must be one of the options Oracle lists for that row; a typed
    value is not checked by the form (seen 2026-10-23), so the script matches it itself."""
    page, row, value = ui.page, purpose_row(ui, pu), pu["bill_to_site"]
    inp = row.locator(BILL_TO_INPUT).first
    icon = row.locator(BILL_TO_ICON).first

    def activate(attempt):                             # the field shows when its cell is clicked
        row.locator("td").filter(has=row.locator(BILL_TO_INPUT)).last.click()
        ui.settle()
        page.wait_for_timeout(800)

    def editable(timeout):           # 2026-10-26: a lost click must not read as "Oracle offers none" (soft)
        end = time.time() + timeout / 1000
        while time.time() < end:
            if inp.is_visible() and icon.is_visible():
                return True
            page.wait_for_timeout(500)
        return False
    if inp.count():
        ui.retry("Bill-to Site cell did not open", activate, editable, wait=3000, last_wait=6000, pause=1.0,
                 soft=True)
    if not inp.count() or not inp.is_visible() or not icon.is_visible():
        oracle.fail(f"Bill-to Site: Oracle offers no Bill-to Site for a {pu['purpose']} purpose (it "
                    "offers one only on a Ship to purpose). Nothing was saved. Ask the user to leave "
                    "it empty for this purpose.")
    pop = page.locator("[id$='billToSiteUseIdId::dropdownPopup::content']:visible")

    def open_list(attempt):
        if not pop.count():
            ui.click(icon, "Bill-to Site list")
        ui.settle()
        page.wait_for_timeout(1500)
    ui.retry("Bill-to Site list did not open", open_list, lambda timeout: pop.first.wait_for(timeout=timeout),
             wait=5000, last_wait=10000, soft=True)
    options = [t.strip() for t in (pop.first.inner_text() if pop.count() else "").splitlines()
               if t.strip() and t.strip() not in ("Search...", " ")]
    page.keyboard.press("Escape")
    ui.settle()
    if not value:                                      # empty: the customer's one address
        if len(options) != 1:
            oracle.fail(f"Bill-to Site for the {pu['purpose']} purpose was left empty, so the "
                        f"customer's one address is used, but Oracle offers {len(options)}: "
                        f"{', '.join(options) or 'none'}. Nothing was saved. Ask the user to pick one.")
        value = options[0]
        print(f"  Bill-to Site of {pu['purpose']}: picked automatically {value!r} (the only address)")
    # same text ignoring upper/lower case and extra spaces (the page compares it that way)
    flat = lambda t: re.sub(r"\s*,\s*", ",", " ".join(t.split())).lower()
    same_text = [o for o in options if flat(o) == flat(value)]
    hit = ui_match(value, options) or (same_text[0] if len(same_text) == 1 else None)
    if hit is None:
        oracle.fail(f"Bill-to Site {value!r} is not one of the screen's values for the "
                    f"{pu['purpose']} purpose. Oracle offers: "
                    + (", ".join(options) if options else
                       "nothing (it lists this customer's Bill to addresses; add a Bill to purpose)")
                    + ". Nothing was saved. Ask the user to pick one of them.")
    ok, _ = ui.lov_type(inp, hit, "Bill-to Site")
    if not ok or inp.input_value().strip() != hit:
        ui.fail("bill_to", f"Oracle did not take the Bill-to Site {hit!r}.")
    pu["bill_to_site"] = hit


def set_primary(ui, pu):
    """Select the row (its Site number cell) and use the table's Set Primary action; Oracle
    then shows a "Primary Purpose" icon in the row (about 1-3 s, 2026-10-23)."""
    page, row = ui.page, purpose_row(ui, pu)
    for attempt in range(2):
        row.locator("td").filter(has_text=re.compile(r"^\s*\d+\s*$")).first.click()
        ui.settle()
        page.wait_for_timeout(800)
        ui.click(page.locator("[title='Set Primary']:visible").first, "Set Primary")
        ui.settle()
        for _ in range(20):
            if row.locator(PRIMARY_ICON).count():
                return
            msgs = ui.page_messages()
            if msgs:
                ui.fail("primary", f"Oracle refused Set Primary for {pu['purpose']}: " + " / ".join(msgs))
            page.wait_for_timeout(500)
        ui.log(f"Set Primary didn't show on {pu['purpose']} (try {attempt + 1}/2)")
    ui.fail("primary", f"The {pu['purpose']} purpose didn't become Primary after Set Primary.")


def defaults_of(ui, fields=FIELDS):
    """What the form shows for every field before saving (requested or default)."""
    shown = {}
    for key, (label, kind, _) in fields.items():
        if kind == "set":
            shown[key] = ui.field(label).input_value()
        else:
            shown[key] = read_value(ui, label, kind)
    return shown


def open_form(ui, ctype):
    """Create Customer, switched to the requested customer type."""
    with ui.step("open Create Customer"):
        # 2026-10-26: a click on the task link made while the page is still busy is lost (the task list stays,
        # its Create Customer row highlighted): the link is clicked again until the form heading shows
        open_task_page(ui, TASK, AREA, OFFERING, heading=FORM_TITLE)
        ui.wait_heading(FORM_TITLE)
    if ctype != "Organization":
        with ui.step(f"switch Customer Type to {ctype}"):
            sel = ui.field("Customer Type")
            hit = ui_match(ctype, [o for o in ui.select_options(sel) if o])
            if hit is None:
                oracle.fail(f"Customer Type {ctype!r} is not on the screen; it shows: "
                            f"{', '.join(ui.select_options(sel))}")
            ui.choose(sel, hit)
            ui.wait_heading(TYPES[ctype]["title"])


MATCH_WARNING = re.compile(r"Warning: Matching (Organizations|Persons)")

# The warning's two choices (2026-10-23): Option 1 "Select from existing organizations" (a list
# of matches with Registry ID) and Option 2 "Create new organization based on what you
# provided" (selected by default). Only Option 2 is ever used: Option 1 would tie this account
# to someone else's customer.
MATCH_RADIOS_JS = r"""() => [...document.querySelectorAll('input[type=radio]')].map(r => {
    const lab = (r.labels && r.labels.length ? [...r.labels].map(l => l.innerText).join(' ') : '').trim();
    let box = r.parentElement, around = '';
    for (let i = 0; i < 4 && box; i++, box = box.parentElement) { around = box.innerText.trim(); if (around) break; }
    const shown = !!(r.offsetParent || (r.labels && r.labels[0] && r.labels[0].offsetParent));
    return {id: r.id, name: r.name, checked: r.checked, shown, label: lab, around: around.slice(0, 160)};
  }).filter(r => r.shown)"""
CREATE_NEW = re.compile(r"Create new (organization|person)", re.I)
SELECT_EXISTING = re.compile(r"Select from existing", re.I)


def matching_warning(ui):
    """Oracle's "Warning: Matching Organizations" dialog after Save and Close (seen
    2026-10-21). None when it isn't shown, else the listed matches [(registry ID, row text)]."""
    head = ui.page.get_by_text(MATCH_WARNING)
    if not (head.count() and head.first.is_visible()):
        return None
    text = ui.page.inner_text("body")
    part = text[text.find("Option 1"):text.find("Option 2")] if "Option 1" in text else ""
    found = []
    for line in part.splitlines():
        cols = [c.strip() for c in line.split("\t") if c.strip()]
        ids = [c for c in cols if re.fullmatch(r"\d{4,}", c)]
        if ids and ids[0] not in [f[0] for f in found]:
            found.append((ids[0], " | ".join(cols)))
    return found


def create_new_anyway(ui, name):
    """In the matching warning choose Option 2 (create a new customer from what was entered)
    and press OK. Never Option 1. Anything unclear: the warning and the form are cancelled
    (nothing saved) and the run stops."""
    radios = ui.page.evaluate(MATCH_RADIOS_JS)
    print("  matching warning choices: " + json.dumps(radios), file=sys.stderr)
    new = [r for r in radios if CREATE_NEW.search(r["label"] + " " + r["around"])
           and not SELECT_EXISTING.search(r["label"])]
    old = [r for r in radios if SELECT_EXISTING.search(r["label"] + " " + r["around"])
           and not CREATE_NEW.search(r["label"])]
    if len(new) != 1:
        ui.evidence("match_warning")
        leave_form(ui)
        ui.fail("save", f"Oracle warned that {name} matches existing customers, and its choice "
                        f"'Create new' could not be found ({len(new)} found); nothing was saved.")
    target = new[0]
    if not target["checked"]:
        lab = ui.page.locator(f"label[for='{target['id']}']")
        if lab.count():
            ui.click(lab.first, "Option 2 (create new)")
        else:
            ui.page.locator(f"[id='{target['id']}']").check(force=True)
        ui.page.wait_for_timeout(800)
    state = {r["id"]: r["checked"] for r in ui.page.evaluate(MATCH_RADIOS_JS)}
    if not state.get(target["id"]) or any(state.get(r["id"]) for r in old):
        ui.evidence("match_warning")
        leave_form(ui)
        ui.fail("save", f"Oracle's matching warning for {name} did not keep 'Create new' selected; "
                        "nothing was saved.")
    dlg = ui.page.locator("div[role='dialog']:visible, div[id$='::popup-container']:visible").filter(
        has_text=MATCH_WARNING)
    scope = dlg.last if dlg.count() else ui.page
    ok = scope.get_by_role("button", name=re.compile(r"^O\s*K$"))
    if not ok.count():
        ui.evidence("match_warning")
        leave_form(ui)
        ui.fail("save", f"Oracle's matching warning for {name} has no OK button; nothing was saved.")
    ui.click(ok.last, "OK (create new)")
    ui.settle()


def leave_form(ui):
    """Close Oracle's matching warning (its own Cancel) and leave the form unsaved."""
    ui.click(ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).last, "Cancel (warning)")
    ui.settle()
    ui.page.wait_for_timeout(1500)
    ui.click(ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).first, "Cancel")
    ui.settle()
    yes = ui.page.get_by_role("button", name=re.compile(r"^Y\s*es$"))
    if yes.count() and yes.first.is_visible():
        ui.click(yes.first, "Yes (leave without saving)")
        ui.settle()
    form = ui.page.locator("h1:visible").filter(has_text=re.compile(rf"^\s*{re.escape(FORM_TITLE)}")).first

    def again(attempt):              # 2026-10-26: a lost Cancel or Yes leaves the form open
        if yes.count() and yes.first.is_visible():
            ui.click(yes.first, "Yes (leave without saving)")
        elif form.count():
            ui.click(ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).first, "Cancel (again)")
        ui.settle()
    ui.retry("Create Customer form did not close without saving", lambda attempt: attempt > 1 and again(attempt),
             lambda timeout: form.wait_for(state="hidden", timeout=timeout), wait=10000, last_wait=30000)


class SaveMessage(Exception):
    """Oracle showed a message dialog after Save and Close: .msgs (its text). Whether the customer was saved
    is then read from Oracle (run_customers), never assumed."""

    def __init__(self, msgs):
        super().__init__(" / ".join(msgs))
        self.msgs = msgs


def save(ui, name):
    """Save and Close. Oracle's matching warning (customers with the same or a similar name)
    is answered with Option 2, create new. Returns the matches the warning listed
    [(registry ID, row text)] (empty when it didn't appear)."""
    warned = None
    ok_at = None
    with ui.step("Save and Close"):
        ui.click(ui.page.get_by_role("button", name="Save and Close").first, "Save and Close")
        ui.settle()
        for _ in range(90):
            msgs = ui.page_messages()
            if msgs:
                # v2 (2026-10-26): a message after Save and Close doesn't prove nothing was saved (two
                # customers were saved while the card said so); the caller checks Oracle itself
                ui.page.screenshot(path=str(ui.work / "save_message.png"), full_page=True)
                raise SaveMessage(msgs)
            match = matching_warning(ui)
            if match is not None:
                if warned is not None:
                    # After OK the warning stays up (OK greyed) while Oracle saves (2026-10-23);
                    # only a warning still there 90 s after OK counts as came back.
                    if time.time() - ok_at < 90:
                        ui.page.wait_for_timeout(2000)
                        continue
                    ui.fail("save", f"Oracle's matching warning for {name} came back after OK.")
                warned = match
                print(f"  Oracle: matching customers for {name}: "
                      + (", ".join(f"registry ID {r} ({t})" for r, t in match) or "(none listed)")
                      + " - choosing Option 2, create new")
                ui.page.screenshot(path=str(ui.work / "match_warning.png"), full_page=True)
                create_new_anyway(ui, name)
                ok_at = time.time()
                continue
            ui.use_newest_page()
            heads = ui.page.locator("h1:visible").all_inner_texts()
            if any(h.strip().startswith(MANAGE_TASK) for h in heads):
                return warned or []
            # Since the Redwood Set Up page (2026-10-20) Oracle may return there instead.
            if ui.page.locator(ui.SWITCHER).count() and ui.page.locator(ui.SWITCHER).first.is_visible():
                ui.log("Save and Close returned to the Set Up page")
                return warned or []
            ui.page.wait_for_timeout(2000)
        ui.fail("save", f"No result 3 minutes after Save and Close for {name}.")


def form_registry_id(ui):
    """The Registry ID the Create Customer form shows (Oracle assigns it when the form
    opens; read-only). None when it can't be read."""
    el = ui.field("Registry ID")
    v = (el.input_value() if el.count() else "") or ""
    if not v.strip():
        v = ui.page.evaluate(LABEL_TEXT_JS, "Registry ID") or ""
    v = v.strip()
    return v if re.fullmatch(r"\d+", v) else None


# ---------------------------------------------------------------- an earlier try of the same request

JOURNAL = "saved_requests.json"   # in _work/: kept after a failure, deleted after a verified success
JOURNAL_HOURS = 12


def journal(work, key, entry=None):
    """An earlier try of this request (by its key): {"registry_id", "state", "at", ...}, or
    None. With entry: write it. A rerun (sign-in, repair) so never saves the customer twice."""
    f = Path(work) / JOURNAL
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    if entry is None:
        e = data.get(key)
        return e if e and time.time() - e.get("at", 0) < JOURNAL_HOURS * 3600 else None
    data[key] = dict(entry, at=time.time())
    f.write_text(json.dumps(data, indent=1), encoding="utf-8")


def journal_drop(work, key):
    """This request was verified: forget its note. Returns how many other notes are left
    (another customer's saved-but-unverified try; then _work/ is kept, 2026-10-23)."""
    f = Path(work) / JOURNAL
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 0
    data.pop(key, None)
    data = {k: e for k, e in data.items() if time.time() - e.get("at", 0) < JOURNAL_HOURS * 3600}
    f.write_text(json.dumps(data, indent=1), encoding="utf-8")
    return len(data)


# ---------------------------------------------------------------- verification

def same(kind, got, want):
    if kind == "check":
        return got is want
    # A field the screen doesn't show (None, e.g. Sales Tax Geocode for Pakistan) = empty.
    got, want = (got or "").strip(), (want or "").strip()
    if kind == "geo":                 # Oracle stores geography names in capitals
        return got.lower() == want.lower()
    return got == want


def find_new(ui, cust, registry_id, before_ids):
    """The customer this run saved, among the customers with its name: by the Registry ID
    the form showed; else (no ID read, or Oracle used another one) the one name match that
    wasn't there before saving. Names are not unique, so the name alone never decides."""
    rows = [o for o in search_customers(ui, cust["name"], cust["type"])
            if o["name"].lower() == cust["name"].lower()]
    hit = [o for o in rows if registry_id and o["registry_id"] == registry_id]
    if hit:
        return hit[0], rows
    fresh = [o for o in rows if o["registry_id"] not in before_ids]
    if len(fresh) == 1:
        print(f"  NOTE  registry ID {registry_id or '(not read)'} from the form not in the search; "
              f"the one new customer named {cust['name']!r} is {fresh[0]['registry_id']}")
        return fresh[0], rows
    return None, rows


def open_edit(ui, number, what, heading):
    """Open an account or site from Manage Customers, checked by its page heading (2026-10-26: lost clicks)."""
    def act(attempt):
        link = ui.page.locator("a:visible").filter(has_text=re.compile(rf"^\s*{number}\s*$")).first
        if attempt == 1 or link.count():
            ui.click(link, f"{what} {number}")
        ui.settle()
    ui.retry(f"Manage Customers did not open {what} {number}", act,
             lambda timeout: ui.wait_heading(heading, timeout=timeout), wait=40000, last_wait=90000)


def back_to_manage(ui):
    """Cancel (read-only page, nothing saved) back to Manage Customers, checked by its heading."""
    def act(attempt):
        cancel = ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).first
        if attempt == 1 or cancel.count() and cancel.is_visible():
            ui.click(cancel, "Cancel")
        ui.settle()
    ui.retry("Manage Customers did not come back after Cancel", act,
             lambda timeout: ui.wait_heading(MANAGE_TASK, timeout=timeout), wait=40000, last_wait=90000)


def verify(ui, cust, expected, registry_id, before_ids):
    """Reopen the new customer (by its Registry ID) and compare every value."""
    want, name, fields = cust["want"], cust["name"], cust["fields"]
    ok = True

    def check(where, key_label, kind, got, exp):
        nonlocal ok
        good = same(kind, got, exp)
        ok &= good
        print(f"  {'OK  ' if good else 'FAIL'}  {where}: {key_label} = {got!r}"
              + ("" if good else f" (expected {exp!r})"))

    org, rows = find_new(ui, cust, registry_id, before_ids)
    if org is None:
        print(f"  FAIL  search: the new customer {name!r} (registry ID {registry_id}) is not among the "
              f"{len(rows)} customer(s) with this name: {', '.join(o['registry_id'] for o in rows)}")
        return False, None
    accounts, sites = select_org(ui, org["registry_id"], org["table"])
    print(f"  OK    search: {name} found, registry ID {org['registry_id']} "
          f"({len(rows)} customer(s) with this name)")
    if not accounts and not sites:
        # 2026-10-26: Manage Customers lists an account and site only from their start date, so a
        # customer whose Account Established Date / address From Date is after Oracle's today shows
        # none yet (Emberlight ... D01, 130952, both 11/1/26); the party itself is found above.
        today = date.fromisoformat(cust["oracle_today"]) if cust.get("oracle_today") else date.today()
        starts = [(fields[k][0], expected.get(k)) for k in ("account_established_date", "address_from_date")
                  if expected.get(k)]
        later = [f"{label} {v}" for label, v in starts
                 if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{2,4}", str(v).strip()) and ui.parse_screen_date(v) > today]
        if later:
            print(f"  NOTE  search: Manage Customers shows no account or site yet because they start "
                  f"later ({', '.join(later)}; Oracle's today {today.isoformat()}); the customer is saved "
                  f"with registry ID {org['registry_id']}, its account and site values are read back "
                  f"only from that date")
            return ok, org
    if len(accounts) != 1 or len(sites) != 1:
        print(f"  FAIL  search: {len(accounts)} account(s), {len(sites)} site(s) (expected 1 and 1)")
        return False, org
    account_no, site_no = accounts[0][0], sites[0][0]
    check("sites table", "Account Address Set", "text", sites[0][-1], cust["set_name"])
    shown_purposes = sorted(p.strip() for p in (sites[0][-2].split(",") if cust["purposes"] else []))
    if cust["purposes"]:
        check("sites table", "Purpose", "text", ", ".join(shown_purposes),
              ", ".join(sorted(p["purpose"] for p in cust["purposes"])))

    with ui.step(f"read account {account_no}"):
        open_edit(ui, account_no, "account", "Edit Account")
        for key, (label, kind, page) in fields.items():
            if page == "org" or (page == "account" and key in expected):
                if key == "account_established_date":
                    got = ui.page.evaluate(LABEL_TEXT_JS, label)
                else:
                    got = read_value(ui, label, kind)
                check("account", label, kind, got, expected[key])
        back_to_manage(ui)

    with ui.step(f"read site {site_no}"):
        open_edit(ui, site_no, "site", "Edit Site")
        for key, (label, kind, page) in fields.items():
            if page != "site" or key not in expected:
                continue
            if key == "address_from_date":
                got = ui.page.evaluate(LABEL_TEXT_JS, label)
            else:
                got = read_value(ui, label, kind)
            check("site", label, kind, got, expected[key])
        heads = [h for h in ui.page.evaluate(PURPOSE_HEADS_JS) if h]
        rows = [r for r in table_rows(ui, "sitedet:0:AT1") if cells(r)]
        for pu in cust["purposes"]:
            row = next((r for r in rows if pu["purpose"] in r), None)
            if row is None or "Purpose" not in heads:
                check("site purposes", pu["purpose"], "text", "(missing)", "present")
                continue
            base = row.index(pu["purpose"]) - heads.index("Purpose")
            col = lambda h: row[base + heads.index(h)] if 0 <= base + heads.index(h) < len(row) else None
            check("site purposes", f"{pu['purpose']} from date", "text", col("From Date"),
                  pu["from_date"] or pu["from_shown"])
            check("site purposes", f"{pu['purpose']} to date", "text", col("To Date"), pu["to_date"])
            # Edit Site orders its columns differently and the Bill-to Site cell holds a nested
            # table (skipped by ROWS_JS), so Primary and Bill-to Site are read from the row itself
            mine = [r for r in ui.page.evaluate(PURPOSE_PRIMARY_JS) if pu["purpose"] in r["cells"]]
            if pu.get("bill_to_site"):
                check("site purposes", f"{pu['purpose']} Bill-to Site", "text",
                      mine[0]["bill_to"] if mine else "(row not found)", pu["bill_to_site"])
            shown = mine[0]["primary"] if mine else None
            if pu.get("primary"):
                check("site purposes", f"{pu['purpose']} Primary", "check", shown, True)
            else:
                print(f"  NOTE  site purposes: {pu['purpose']} Primary not requested; Oracle shows "
                      f"{'Primary' if shown else 'not Primary'}")
                pu["primary_shown"] = shown
        if len(rows) != len(cust["purposes"]):
            check("site purposes", "number of purposes", "text", str(len(rows)),
                  str(len(cust["purposes"])))
        shot = ui.work / f"verified_{name}.png"
        ui.page.screenshot(path=str(shot), full_page=True)
        back_to_manage(ui)
    return ok, org


# ---------------------------------------------------------------- page interface

HERE = Path(__file__).resolve().parent
ORG_ONLY = {"name", "duns_number"}
PERSON_ONLY = set(PERSON_NAME_FIELDS)
SPEC = {
    "title": "Create a customer",
    "description": "Creates an organization or person customer with its account and address; "
                   "an existing customer is never changed.",
    "fields": [
        # Up front, in this order: the type, the name that type needs, then the two fields
        # every customer needs ("required_when" / "shown_when": common/page.py, 2026-10-21).
        {"key": "customer_type", "label": "Customer type", "required": True, "type": "pick",
         "placeholder": "Organization", "default": "Organization"},
        {"key": "name", "label": "Organization name", "required": False, "type": "text",
         "placeholder": "Acme Widgets", "default": None,
         "required_when": {"customer_type": "Organization"}, "shown_when": {"customer_type": "Organization"}},
        {"key": "first_name", "label": "First name", "required": False, "type": "text",
         "placeholder": "Jane", "default": None,
         "required_when": {"customer_type": "Person"}, "shown_when": {"customer_type": "Person"}},
        {"key": "account_address_set", "label": "Account address set", "required": True,
         "type": "pick", "placeholder": "Enterprise Set", "default": None, "list": "samples",
         "help": "Pick one that is known to work, or type another; it is checked with Oracle."},
        {"key": "supplier_site_id", "label": "Supplier site ID", "required": True, "type": "text",
         "placeholder": "1001", "default": None},
        {"key": "prefix", "label": "Prefix", "required": False, "type": "pick",
         "placeholder": "Ms.", "default": None, "shown_when": {"customer_type": "Person"}},
        {"key": "middle_name", "label": "Middle name", "required": False, "type": "text",
         "placeholder": "Q", "default": None, "shown_when": {"customer_type": "Person"}},
        {"key": "last_name", "label": "Last name", "required": False, "type": "text",
         "placeholder": "Doe", "default": None, "shown_when": {"customer_type": "Person"}},
        {"key": "suffix", "label": "Suffix", "required": False, "type": "text",
         "placeholder": "Jr.", "default": None, "shown_when": {"customer_type": "Person"}},
        {"key": "duns_number", "label": "D-U-N-S number", "required": False,
         "type": "text", "placeholder": "123456789", "default": None,
         "shown_when": {"customer_type": "Organization"}},
        {"key": "taxpayer_id", "label": "Taxpayer ID", "required": False, "type": "text",
         "placeholder": "123456789", "default": None},
        {"key": "account_type", "label": "Account type", "required": False, "type": "pick",
         "placeholder": "External", "default": None},
        {"key": "customer_class", "label": "Customer class", "required": False, "type": "pick",
         "placeholder": "Federal class", "default": None},
        {"key": "account_description", "label": "Account description", "required": False,
         "type": "text", "placeholder": "Main account", "default": None},
        {"key": "account_established_date", "label": "Account established date", "required": False,
         "type": "date", "placeholder": "2026-10-21", "default": None,
         "help": "Empty: Oracle's today. 'today' means Oracle's today minus one day."},
        {"key": "address_from_date", "label": "Address from date", "required": False, "type": "date",
         "placeholder": "2026-10-21", "default": None, "help": "Empty: Oracle's today."},
        {"key": "site_name", "label": "Site name", "required": False, "type": "text",
         "placeholder": "Head office", "default": None},
        {"key": "country", "label": "Country", "required": False, "type": "pick",
         "placeholder": "United States", "default": "United States", "list": "samples",
         "help": "Only the United States is offered so far (its address fields are proven)."},
        {"key": "address_line_1", "label": "Address line 1", "required": False, "type": "text",
         "placeholder": "1 Main Street", "default": None},
        {"key": "address_line_2", "label": "Address line 2", "required": False, "type": "text",
         "placeholder": "Suite 100", "default": None},
        {"key": "state", "label": "State", "required": False, "type": "pick",
         "placeholder": "CA", "default": None, "list": "samples",
         "help": "Proven states; another one you type is checked with Oracle."},
        {"key": "city", "label": "City", "required": False, "type": "text",
         "placeholder": "Cupertino", "default": None,
         "help": "Must be a city Oracle knows in that state."},
        {"key": "postal_code", "label": "Postal code", "required": False, "type": "text",
         "placeholder": "95014", "default": None,
         "help": "Must be a postal code Oracle knows for that city."},
        {"key": "key_account", "label": "Key account", "required": False, "type": "yes-no",
         "placeholder": "no", "default": False},
        # The rest of the request-file fields (2026-10-23), so the page's sheet upload can send a
        # customer with every column of the sheet; same checks as the request file.
        {"key": "account_termination_date", "label": "Account termination date", "required": False,
         "type": "date", "placeholder": "2027-12-31", "default": None},
        {"key": "account_notes_other", "label": "Account notes other", "required": False,
         "type": "text", "placeholder": "Notes", "default": None},
        {"key": "shipping_instructions", "label": "Shipping instructions", "required": False,
         "type": "text", "placeholder": "Leave at the gate", "default": None},
        {"key": "customer_agreement", "label": "Customer agreement", "required": False,
         "type": "text", "placeholder": "Agreement 1", "default": None},
        {"key": "address_to_date", "label": "Address to date", "required": False, "type": "date",
         "placeholder": "2027-12-31", "default": None},
        {"key": "mail_stop", "label": "Mail stop", "required": False, "type": "text",
         "placeholder": "MS 12", "default": None},
        {"key": "responsible_mineral_status", "label": "Responsible mineral status", "required": False,
         "type": "text", "placeholder": "Conflict Free", "default": None,
         "help": "Conflict Free, N/A, No Data or Undetermined; checked with Oracle."},
        {"key": "address_note", "label": "Address (extra line)", "required": False, "type": "text",
         "placeholder": "Back entrance", "default": None},
        {"key": "url", "label": "Web address", "required": False, "type": "text",
         "placeholder": "www.example.com", "default": None},
        {"key": "contact_email", "label": "Contact email", "required": False, "type": "text",
         "placeholder": "name@example.com", "default": None},
        {"key": "authorizer", "label": "Authorizer", "required": False, "type": "text",
         "placeholder": "Jane Doe", "default": None},
        {"key": "sales_tax_geocode", "label": "Sales tax geocode", "required": False, "type": "text",
         "placeholder": "050850000", "default": None},
        {"key": "sales_tax_inside_city_limits", "label": "Sales tax inside city limits",
         "required": False, "type": "yes-no", "placeholder": "yes", "default": True},
        {"key": "customer_category_code", "label": "Customer category code", "required": False,
         "type": "text", "placeholder": "A", "default": None},
        {"key": "site_language", "label": "Site language", "required": False, "type": "text",
         "placeholder": "American English", "default": None},
        {"key": "translated_customer_name", "label": "Translated customer name", "required": False,
         "type": "text", "placeholder": "Acme", "default": None},
        {"key": "trading_partner_identifier", "label": "Trading partner identifier", "required": False,
         "type": "text", "placeholder": "777", "default": None, "help": "Numbers only."},
        {"key": "edi_location_code", "label": "EDI location code", "required": False, "type": "text",
         "placeholder": "LOC1", "default": None},
        {"key": "purposes", "label": "Business purposes", "required": False, "type": "rows",
         "min_rows": 0, "add_label": "Add a purpose", "row_label": "Purpose",
         "fields": [
             {"key": "purpose", "label": "Purpose", "required": True, "type": "pick",
              "placeholder": "Bill to", "list": "samples"},
             {"key": "from_date", "label": "From date", "required": False, "type": "date",
              "placeholder": "2026-10-21"},
             {"key": "to_date", "label": "To date", "required": False, "type": "date",
              "placeholder": "2027-12-31"},
             {"key": "primary", "label": "Primary", "required": False, "type": "yes-no",
              "placeholder": "no"},
             {"key": "bill_to_site", "label": "Bill-to site", "required": False, "type": "text",
              "placeholder": "1 Main Street,CUPERTINO, CA 95014"},
         ]},
    ],
}
WHERE = ("Setup and Maintenance > Financials > Customers > Manage Customers, search for {name} "
         "(the account number opens Edit Account, the site number Edit Site)")
_LISTS = {}   # the form lists, read once per process (one browser visit for all of them)


def _state_options(ui):
    """The State list of the address (United States), from its Search and Select dialog."""
    field = ui.field("State")
    icon_id = field.get_attribute("id").replace("::content", "::lovIconId")
    rows = ui.lov_search_all(ui.page.locator(f"[id='{icon_id}']").first, "State")
    names = []
    for r in rows:
        r = [c for c in r if "\t" not in c]
        if r and r[0] not in names:
            names.append(r[0])
    return names


def _purpose_options(ui):
    """The Purpose drop-down of a new Address Purposes row (the form is left with Cancel)."""
    page_ = ui.page
    ui.click(page_.locator("[title='Add Row']:visible").last, "Address Purposes Add Row")
    ui.settle()
    for _ in range(20):
        for s in page_.locator(f"{PURPOSE_SELECT}:visible").all():
            if not s.evaluate("e => (e.options[e.selectedIndex] || {text: ''}).text").strip():
                return [o for o in ui.select_options(s) if o]
        page_.wait_for_timeout(500)
    ui.fail("purpose", "No new Address Purposes row appeared.")


def form_lists():
    """Every pick list of the page, read live on Create Customer (organization form, then
    the person form for Prefix); nothing is saved: the form is left with Cancel."""
    if _LISTS:
        return _LISTS
    oracle.check_environment()
    browser.refuse_production()
    work = oracle.init_work_dir(HERE)
    # Files already there belong to a failed run: its evidence and the note of what it saved
    # (saved_requests.json). A --run reads these lists first, so deleting them here let the
    # rerun after a repair save the customer a second time (ZZ_TEST_3727, 2026-10-23).
    had_files = any(work.iterdir())
    with browser.OracleUI(work, headless=True) as ui:
        open_form(ui, "Organization")
        with ui.step("read the form's lists"):
            sel = lambda label: [o for o in ui.select_options(ui.field(label)) if o]
            _LISTS["customer_type"] = [(o, o) for o in sel("Customer Type")]
            _LISTS["account_address_set"] = [(c, n or c) for c, n, _ in address_sets(ui)]
            for key, label in (("account_type", "Account Type"), ("customer_class", "Customer Class"),
                               ("country", "Country"), ("site_language", "Site Language"),
                               ("customer_category_code", "Customer Category Code")):
                _LISTS[key] = [(o, o) for o in sel(label)] if ui.field(label).count() else []
            _LISTS["state"] = [(s, s) for s in _state_options(ui)]
            _LISTS["purposes.purpose"] = [(o, o) for o in _purpose_options(ui)]
        with ui.step("read the person form's Prefix list"):
            ui.choose(ui.field("Customer Type"), "Person")
            ui.wait_heading(TYPES["Person"]["title"])
            _LISTS["prefix"] = [(o, o) for o in sel("Prefix")]
        ui.click(ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).first, "Cancel")
        ui.settle()
        yes = ui.page.get_by_role("button", name=re.compile(r"^Y\s*es$"))
        if yes.count() and yes.first.is_visible():
            ui.click(yes.first, "Yes (leave without saving)")
    if not had_files:
        oracle.cleanup_work_dir()
    return _LISTS


# The page's drop-downs: only values proven by a real, verified customer create in this
# project, written here so the form opens at once (no browser visit). (value, label) as the
# form shows them. A value joins only after such a create (see CLAUDE.md > Page interface). `--options FIELD --all` reads the
# full live list from the form; a --run checks anything typed against the full live list.
SAMPLES = {
    "customer_type": [("Organization", "Organization"), ("Person", "Person")],
    "prefix": [("Mr.", "Mr."), ("Mrs.", "Mrs."), ("Ms.", "Ms.")],
    "account_type": [("External", "External"), ("Internal", "Internal")],
    "customer_class": [("Federal class", "Federal class"), ("Public sector companies", "Public sector companies")],
    # Only values that have created a verified customer in this project (2026-10-21).
    "account_address_set": [("ENTERPRISE", "Enterprise Set"), ("CUSTOMER_RDS", "CUSTOMER_RDS"),
                            ("001 CUSTOMER SITE", "001 Customer Site")],
    "country": [("United States", "United States")],
    "state": [("CA", "CA")],
    "purposes.purpose": [("Bill to", "Bill to"), ("Ship to", "Ship to")],
}


def options_for(key):
    """The drop-down samples above; with --all, or during --run (the check of what was
    typed in), the full lists read live from the Create Customer form."""
    dropdown = sys.argv[1:2] == ["--options"] and "--all" not in sys.argv
    if dropdown and key in SAMPLES:
        return [{"value": v, "label": l} for v, l in SAMPLES[key]]
    lists = form_lists()
    if key not in lists:
        raise page.PageError("FAILED", detail=f"no list for {key!r}")
    return [{"value": v, "label": l} for v, l in lists[key]]


class _PlainStop(Exception):
    """A stop inside the normal run that the user can fix by changing a value."""


PLAIN_STOPS = (r"is not one of the screen's values", r"is not one of the values on the screen",
               r"does not exist in Oracle's geography", r"does not exist in Oracle's list",
               r"Oracle does not accept", r"Oracle did not save", r"Oracle offers no Bill-to Site",
               r"can be Primary, but")


def _plain(msg):
    """The user's part of a run message: up to "Nothing was saved" / "Ask the user"."""
    msg = msg.split("\n  Screenshot:")[0]                              # ui.fail() adds it
    text = re.split(r"\s+(?:Nothing was saved|Ask the user)", msg, maxsplit=1)[0].strip()
    text = re.sub(r"^Step '[^']*' failed after \d+s:\s*", "", text)   # the step name stays in detail
    text = re.sub(r"\s*\(Error:.*?\)", "", text)                       # Oracle's raw field message
    # a refused save: "Oracle did not save X: Error <Oracle's sentence> (HZ-120150) OK"
    text = re.sub(r"^Oracle did not save ([^:]+): (?:Error\s+)?", r"Oracle refused to save \1: ", text)
    text = re.sub(r"\s*\([A-Z]{2,4}-\d+\)", "", text)
    text = re.sub(r"\s+OK$", "", text)
    if "date range for a child record" in text:
        text += (" (A purpose's dates must lie within the address dates; the address starts on "
                 "its from date, Oracle's today when left empty.)")
    return text if text.endswith((".", ")")) else text + "."


def problems_of(msg, request):
    """A plain stop as a structured refusal for the page's decision panel (v2, 2026-10-26): [{"field",
    "value", "reason", "suggestions"}] with the values Oracle offered, when the message names them."""
    labels = {lab.lower(): key for key, (lab, _k, _s) in dict(FIELDS, **PERSON_FIELDS).items()}
    text = _plain(msg)
    m = re.search(r"(?:^|: )([A-Z][\w -]+?): '([^']*)' (?:is not one of|does not exist)", msg) or         re.search(r"[Tt]he ([a-z][\w ]+?) '([^']*)' is not one of the values", msg) or         re.search(r"(Bill-to Site) '([^']*)'", msg)
    if not m:
        return []
    label, value = m.group(1).strip(), m.group(2)
    field = "purposes.bill_to_site" if label.lower() == "bill-to site" else labels.get(label.lower(), label.lower())
    sugg = []
    o = re.search(r"(?:pick one of|Oracle offers|Oracle's search for it showed): (.+?)(?:\. Nothing was saved|$)", msg)
    if o and field == "purposes.bill_to_site":       # one address per customer; it holds ", " itself
        sugg = [o.group(1).strip()]
    elif o:
        sugg = [x.strip() for x in o.group(1).split(", ") if x.strip()][:12]
        if field == "account_address_set":          # "Enterprise Set (ENTERPRISE)" -> the code, which is matched
            sugg = [re.sub(r"^.*\(([^()]+)\)$", r"\1", x) for x in sugg]
    return [{"field": field, "value": value if value else request.get(field), "reason": text, "suggestions": sugg}]


def run_request(request, progress):
    """--run: one organization or person customer through the normal run."""
    oracle.check_environment()
    browser.refuse_production()
    ctype = request.get("customer_type", "Organization")
    problems = []
    if ctype == "Organization":
        if not request.get("name"):
            problems.append({"field": "name", "problem": "missing",
                             "text": "Please fill in Customer name (needed for an organization)."})
        wrong = sorted(PERSON_ONLY & set(request))
    else:
        if not request.get("first_name"):
            problems.append({"field": "first_name", "problem": "missing",
                             "text": "Please fill in First name (needed for a person)."})
        wrong = sorted(ORG_ONLY & set(request))
    labels = {f["key"]: f["label"] for f in SPEC["fields"]}
    for k in wrong:
        problems.append({"field": k, "problem": "wrong_type",
                         "text": f"{labels[k]} doesn't apply to a {ctype.lower()} customer."})
    # one Primary per type of purpose (Oracle's rule): refused here, before Oracle is opened
    rows_by_kind = collections.defaultdict(list)
    for i, p in enumerate(request.get("purposes", []), 1):
        if p.get("primary"):
            rows_by_kind[str(p.get("purpose", "")).lower()].append((i, p.get("purpose")))
    for rows in rows_by_kind.values():
        if len(rows) > 1:
            problems.append({"field": "purposes.primary", "problem": "two_primary",
                             "row": rows[1][0],
                             "text": f"Only one {rows[0][1]} purpose can be Primary; purposes "
                                     + " and ".join(str(i) for i, _ in rows) + " are both marked Primary."})
    if problems:
        raise page.PageError("INVALID_REQUEST", " ".join(p["text"] for p in problems), problems)
    c = {k: v for k, v in request.items() if k != "purposes"}
    for k in ("account_established_date", "address_from_date"):
        if str(c.get(k, "")).lower() == TODAY_WORD:
            c[k] = TODAY_WORD
    if c.get("customer_type") == "Organization":
        c.pop("customer_type")
    c["purposes"] = []
    for p in request.get("purposes", []):
        p = dict(p)
        for k in ("from_date", "to_date"):
            if str(p.get(k, "")).lower() == TODAY_WORD:
                p[k] = TODAY_WORD
        c["purposes"].append(p)
    customers = parse_requirements({"customers": [c]}, "page")
    name = customers[0]["name"]
    where = WHERE.format(name=name)
    args = argparse.Namespace(check=False, headed=False)
    found, last = {}, {"msg": ""}
    orig = oracle.fail

    def plain_fail(msg):
        last["msg"] = msg
        if any(re.search(p, msg) for p in PLAIN_STOPS):
            print(f"\nERROR: {msg}", file=sys.stderr)
            raise _PlainStop(msg)
        orig(msg)
    oracle.fail = plain_fail          # this process only, while the run goes; restored below
    run_start = time.time()

    def this_run_saving():
        """The rerun note written by THIS run just before Save and Close (v2): then "nothing was saved" is never
        said without Oracle's word for it."""
        e = journal(oracle.WORK_DIR or HERE / "_work", customers[0]["key"])
        return e if e and e.get("at", 0) >= run_start - 1 else None
    try:
        run_customers(args, customers, HERE, progress, found)
    except PlaceRefused as e:
        # v2: a State, City or Postal Code Oracle doesn't have, found before anything was saved
        pr = e.problem
        raise page.PageError("NOT_IN_ORACLE", pr["text"] + " Nothing was saved.",
                             {"message": str(e), "saved": "no", "registry_id": None,
                              "problems": [{"field": pr["key"], "value": request.get(pr["key"]), "reason": pr["text"],
                                            "suggestions": pr.get("suggestions") or []}]})
    except _PlainStop as e:
        # (a stop inside ui.step() comes back as "Step '<name>' failed after Ns: <message>")
        code = "INVALID_REQUEST" if "Oracle did not save" in str(e) else "NOT_IN_ORACLE"
        late = this_run_saving()
        if late:      # after Save was clicked: never claimed "nothing saved" without checking (v2)
            raise page.PageError("FAILED", f"{_plain(str(e))} The customer {name} may have been saved in Oracle "
                                 f"(Registry ID {late.get('registry_id')} if it was). Running the same sheet again "
                                 "checks this and never creates it twice.",
                                 {"message": str(e), "saved": "maybe", "registry_id": late.get("registry_id")})
        raise page.PageError(code, _plain(str(e)) + " Nothing was saved.",
                             {"message": str(e), "saved": "no", "registry_id": None,
                              "problems": problems_of(str(e), request)})
    except SystemExit as e:
        if e.code in (0, None):
            raise
        # Any other stop: say plainly what was and wasn't created (2026-10-23; the page shows
        # it on the failure card, nothing asks the user mid-run). The rerun note says it.
        code = page._classify(last["msg"])
        done = journal(oracle.WORK_DIR or HERE / "_work", customers[0]["key"])
        rid = (done or {}).get("registry_id")
        if done and done.get("state") == "saved" and code == "VERIFY_FAILED":
            what = (f"The customer {name} is in Oracle with Registry ID {rid}; it was not created twice.")
        elif done and done.get("state") == "saved":
            what = (f"The customer {name} was saved in Oracle (Registry ID {rid}), but checking it "
                    "didn't finish. Running the same sheet again checks it without creating it twice.")
        elif done:
            what = (f"The customer {name} may have been saved in Oracle (Registry ID {rid} if it was). "
                    "Running the same sheet again checks this and never creates it twice.")
        else:
            what = "Nothing was saved in Oracle."
        # detail.saved (yes / maybe / no) and registry_id: the page sorts failed customers by it
        # (only "no" goes into the sheet with the failed customers, 2026-10-23)
        saved = "no" if not done else ("yes" if done.get("state") == "saved" else "maybe")
        raise page.PageError(code, f"{page.ERRORS.get(code, page.ERRORS['FAILED'])} {what}",
                             {"message": last["msg"] or f"stopped ({e.code})", "saved": saved,
                              "registry_id": rid if done else None})
    finally:
        oracle.fail = orig
    progress.step("done")
    got = found.get(name, {})
    others = got.get("same_name_before") or []
    if got.get("saved_earlier"):
        others = [i for i in others if i != got.get("registry_id")]
    text = (f"Created the {ctype.lower()} customer {name} with Registry ID {got.get('registry_id')}, "
            "with its account and address, and checked every value in Oracle.")
    if others:
        text += (f" {len(others)} other customer{'s' if len(others) != 1 else ''} with this name "
                 f"(Registry ID{'s' if len(others) != 1 else ''} {', '.join(others)}) "
                 f"{'were' if len(others) != 1 else 'was'} not touched.")
    if got.get("saved_earlier"):
        text += " It was saved by the first try of this request and not created again."
    return {"text": text, "where": WHERE.format(name=f"{name}, Registry ID {got.get('registry_id')}"),
            "created": {"registry_id": got.get("registry_id"), "name": name, "type": ctype,
                        "account_address_set": got.get("set_name"), "values": got.get("values"),
                        "purposes": got.get("purposes"),
                        "other_customers_with_this_name": ", ".join(others) or None}}


def geo_rows(ui, label, wanted):
    """Read-only: the rows of a geography field's Search and Select dialog (City, Postal Code)
    for one search text, e.g. "CUPERTINO, SANTA CLARA, CA" or "95014, CUPERTINO, SANTA CLARA,
    CA" (2026-10-23). Nothing is typed into the customer's fields; the dialog is cancelled."""
    icon_id = ui.field(label).get_attribute("id").replace("::content", "::lovIconId")
    ui.click(ui.page.locator(f"[id='{icon_id}']").first, f"{label} list")
    more = ui.page.locator("a:text-is('Search...'):visible").last
    more.wait_for(timeout=20000)
    ui.click(more, f"{label} Search...")
    dlg = ui.lov_dialogs().last
    dlg.wait_for(timeout=60000)
    dlg.locator("input[id$='value00::content']").first.fill(wanted)
    ui.click(dlg.get_by_role("button", name="Search", exact=True), f"{label} Search")
    ui.settle()
    ui.page.wait_for_timeout(2000)
    rows = [[p.strip() for p in r[0].split(",")] for r in ui.lov_rows(dlg) if r]
    ui.click(dlg.get_by_role("button", name="Cancel").first, f"{label} Cancel")
    ui.page.wait_for_timeout(800)
    return rows


# ---------------------------------------------------------------- places: one path for the preview and Create (v2)
# 2026-10-26 (customers v2): State, City and Postal Code are chosen through each field's own Search and Select
# dialog on Create Customer, the row picked by its columns (city, county, state / postal code, city, county,
# state), never by typing + Tab: a typed name that starts another name (ABSECON / ABSECON HIGHLANDS, DALLAS in 5
# counties, SEATTLE / SEATTLE HEIGHTS) made Oracle open a choice dialog whose rows the old code read before they
# loaded, so real cities were reported as missing. The preview runs exactly this path on an unsaved form (left
# with Cancel), so a place that passes the preview passes Create.

PLACE_WAIT = 25          # seconds to wait for a search dialog's rows


class PlaceRefused(Exception):
    """A State, City or Postal Code Oracle doesn't have (as the user wrote it): .problem = {"key", "text", "fix",
    "suggestions"}."""

    def __init__(self, problem):
        super().__init__(problem["text"])
        self.problem = problem


ROW_TEXTS_JS = r"""d => [...d.querySelectorAll('tr[_afrrk]')].map((r, i) => [i,
    [...r.querySelectorAll('td')].filter(td => !td.querySelector('td')).map(td => td.innerText.trim())
      .filter(t => t).join(' | ')])"""


def place_search(ui, label, text):
    """Open the field's Search and Select dialog, search text, wait until its rows are there (or Oracle says
    there are none). Returns (dialog, [(row index, [parts])]); the dialog stays open."""
    field = ui.field(label)
    icon_id = field.get_attribute("id").replace("::content", "::lovIconId")
    more = ui.page.locator("a:text-is('Search...'):visible").last
    # 2026-10-26: the list and its dialog checked and opened again when a click was lost (shared retry helper)
    ui.retry(f"{label} list did not open",
             lambda attempt: more.count() and more.is_visible() or
             ui.click(ui.page.locator(f"[id='{icon_id}']").first, f"{label} list"),
             lambda timeout: more.wait_for(timeout=timeout), wait=20000, last_wait=30000)
    before = ui.lov_dialogs().count()

    def opened(timeout):
        end = time.time() + timeout / 1000
        while time.time() < end:
            if ui.lov_dialogs().count() > before:
                return True
            ui.page.wait_for_timeout(500)
        return False
    ui.retry(f"{label} search dialog did not open",
             lambda attempt: ui.lov_dialogs().count() > before or ui.click(more, f"{label} Search..."),
             opened, wait=30000, last_wait=60000)
    dlg = ui.lov_dialogs().last
    box = dlg.locator("input[id$='value00::content']").first
    box.fill(text)
    box.press("Tab")                 # commit the text first: a quick Search used the old (empty) value
    ui.settle()
    rows = []
    for attempt in (1, 2):           # "No rows" is believed only when a second search says it too
        ui.click(dlg.get_by_role("button", name="Search", exact=True), f"{label} Search")
        ui.settle()
        started = time.time()
        for _ in range(PLACE_WAIT * 2):
            rows = [(i, [p.strip() for p in t.split(",")]) for i, t in dlg.evaluate(ROW_TEXTS_JS) if t]
            if rows:
                return dlg, rows
            if time.time() - started > 5 and dlg.get_by_text(re.compile(r"No (rows|results|data) to display")).count():
                break
            ui.page.wait_for_timeout(500)
    return dlg, rows


def place_cancel(ui, dlg, label):
    ui.close_dialog(dlg, f"{label} search dialog")      # Cancel, checked that the dialog closed (2026-10-26)


def place_rows(ui, label, text):
    """Read-only: the parts of each row for one search text (the dialog is cancelled)."""
    dlg, rows = place_search(ui, label, text)
    place_cancel(ui, dlg, label)
    return [parts for _, parts in rows]


def place_choose(ui, label, text, fits, expect):
    """Search and pick the first row whose parts fit (fits(parts) -> bool, checked by its columns), then OK;
    the field must then show `expect` (capitals ignored)."""
    dlg, rows = place_search(ui, label, text)
    index = next((i for i, parts in rows if fits(parts)), None)
    if index is None:
        place_cancel(ui, dlg, label)
        ui.fail("place", f"Oracle's {label} list no longer shows {expect!r}.")
    row = dlg.locator("tr[_afrrk]").nth(index)

    def pick(attempt):               # OK only fills the field (nothing saved); checked that the dialog closed
        if dlg.is_visible():
            ui.click(row.locator("td").first, f"{label} row {expect}")
            ui.click(dlg.get_by_role("button", name="OK", exact=True), f"{label} OK")
        ui.settle()
    ui.retry(f"{label} search dialog did not take {expect!r}", pick,
             lambda timeout: dlg.wait_for(state="hidden", timeout=timeout), wait=10000, last_wait=20000)
    ui.page.wait_for_timeout(1000)
    got = ui.field(label).input_value()
    if " ".join(got.split()).upper() != " ".join(str(expect).split()).upper():
        ui.fail("place", f"{label} shows {got!r} after choosing {expect!r} in Oracle's list.")
    return got


def clear_places(ui):
    """Empty Postal Code and City (a new State narrows them; an old value must not stay)."""
    for label in ("Postal Code", "City"):
        el = ui.field(label)
        if el.count() and el.input_value():
            el.fill("")
            el.press("Tab")
            ui.settle()


def _up(t):
    return " ".join(str(t or "").split()).upper()


def _close(word, names, n=8):
    import difflib
    names = list(dict.fromkeys(names))
    hits = difflib.get_close_matches(_up(word), names, n=n, cutoff=0.6)
    return hits + [x for x in names if x.startswith(_up(word)[:3]) and x not in hits][:max(0, n - len(hits))]


def pick_places(ui, req, choose=True):
    """State, City and Postal Code of a request, as Create sets them (choose=True picks each in its dialog on
    the form). Raises PlaceRefused with suggestions for a value Oracle doesn't have. Returns {"state", "city",
    "postal_code", "county", "notes": [...]} as Oracle shows them. The preview calls it on an unsaved form."""
    state, city, postal = (str(req.get(k) or "").strip() for k in ("state", "city", "postal_code"))
    out, notes = {}, []
    if choose and not state:
        # no State in this row: an earlier row's State must not narrow the City list (preview, 2026-10-26)
        clear_places(ui)
        st = ui.field("State")
        if st.count() and st.input_value():
            st.fill("")
            st.press("Tab")
            ui.settle()
    if state:
        rows = place_rows(ui, "State", state)
        hit = [p for p in rows if p and _up(p[0]) == _up(state)]
        if not hit:
            known = [s for s, _ in (_LISTS.get("state") or [])]
            if not known:
                try:
                    known = _state_options(ui)          # the whole list (about 20 s), only for a missing state
                except BaseException:  # noqa: BLE001 - suggestions are a help, not a condition
                    known = [p[0] for p in rows]
            raise PlaceRefused({"key": "state", "text": f"Oracle has no state '{state}'.",
                                "suggestions": _close(state, [_up(s) for s in known]),
                                "fix": "Use a state Oracle has (for example its two-letter code)."})
        if choose:
            clear_places(ui)
            out["state"] = place_choose(ui, "State", state, lambda p: p and _up(p[0]) == _up(state), _up(state))
        else:
            out["state"] = _up(state)
    in_state = lambda p: not state or _up(p[-1]) == _up(state)
    postal_rows = []
    if postal:
        postal_rows = [p for p in place_rows(ui, "Postal Code", postal) if len(p) >= 3 and _up(p[0]) == _up(postal)]
    if city:
        rows = place_rows(ui, "City", city)
        exact = [p for p in rows if len(p) >= 2 and _up(p[0]) == _up(city) and in_state(p)]
        if not exact:
            # suggestions: the cities Oracle has for this postal code in the state, then the closest names
            by_postal = sorted({_up(p[1]) for p in postal_rows if in_state(p)})
            near = place_rows(ui, "City", city[:3]) if len(city) >= 3 else []
            names = [_up(p[0]) for p in rows + near if p and in_state(p)]
            other = sorted({_up(p[-1]) for p in rows if p and _up(p[0]) == _up(city)})
            text = (f"Oracle has no city '{city}' in {state}." if state else f"Oracle has no city called '{city}'.")
            if other:
                text += f" It has {_up(city)} in: {', '.join(other)}."
            raise PlaceRefused({"key": "city", "text": text,
                                "suggestions": list(dict.fromkeys(by_postal + _close(city, names)))[:10],
                                "fix": "Use a city Oracle has for this State and Postal Code."})
        counties = sorted({_up(p[1]) for p in exact})
        county = None
        if postal_rows:
            fit = {_up(p[2]) for p in postal_rows if _up(p[1]) == _up(city) and in_state(p)}
            county = next((c for c in counties if c in fit), None)
        if county is None and len(counties) > 1:
            county = next((c for c in counties if c == _up(city)), counties[0])
            notes.append(f"Oracle has {_up(city)} in {len(counties)} counties of {_up(state)} ({', '.join(counties)}); "
                         f"{county} is used. Add a Postal Code to choose another.")
        county = county or counties[0]
        out["county"] = county
        if choose:
            out["city"] = place_choose(ui, "City", city, lambda p: len(p) >= 2 and _up(p[0]) == _up(city)
                                       and in_state(p) and _up(p[1]) == county, _up(city))
        else:
            out["city"] = _up(city)
    if postal:
        fits = [p for p in postal_rows if in_state(p) and (not city or _up(p[1]) == _up(city))]
        if not fits:
            places = sorted({f"{_up(p[1])}, {_up(p[-1])}" for p in postal_rows})
            where = ", ".join(x for x in (_up(city), _up(state)) if x)
            # once a State is on the form Oracle's postal search keeps to that state (2026-10-26)
            raise PlaceRefused({"key": "postal_code",
                                "text": (f"Postal code {postal} isn't one Oracle has for {where}." if postal_rows or where
                                         else f"Oracle has no postal code '{postal}'."),
                                "suggestions": sorted({_up(p[1]) for p in postal_rows if in_state(p)})[:10],
                                "fix": (f"Oracle has {postal} only for {'; '.join(places)}. Use a postal code of "
                                        f"{where}, or change the City." if postal_rows else
                                        f"Use a postal code Oracle has for {where}." if where else
                                        "Check it; Oracle only accepts postal codes it already has.")})
        if choose:
            want_c = out.get("county")
            same = lambda p: len(p) >= 3 and _up(p[0]) == _up(postal) and in_state(p) and (not city or _up(p[1]) == _up(city))
            exact_c = [p for p in fits if not want_c or _up(p[2]) == want_c]
            out["postal_code"] = place_choose(ui, "Postal Code", postal,
                                              (lambda p: same(p) and _up(p[2]) == want_c) if exact_c and want_c else same,
                                              _up(postal))
        else:
            out["postal_code"] = _up(postal)
    out["notes"] = notes
    return out


def address_problems(ui, req):
    """City, State and Postal Code against Oracle's geography, read-only, through exactly the path Create uses
    (pick_places on an unsaved form). [{"key", "text", "fix", "suggestions"}] plus notes for what was found."""
    try:
        got = pick_places(ui, req, choose=True)
    except PlaceRefused as e:
        return [e.problem], {}
    found = {}
    if got.get("city"):
        found["city"] = f"Found in Oracle: {got['city']}" + (f", {got['state']}" if got.get("state") else "") \
            + (f" ({got['county']} county)" if got.get("county") else "")
    if got.get("postal_code"):
        found["postal_code"] = f"Found in Oracle for {', '.join(x for x in (got.get('city'), got.get('state')) if x)}"
    if got.get("state") and not got.get("city"):
        found["state"] = f"Found in Oracle: {got['state']}"
    for n in got.get("notes") or []:
        found["city"] = (found.get("city", "") + " " + n).strip()
    return [], found


def preview_command(argv, what):
    """Read-only page commands for the preview (2026-10-23), one JSON line on stdout:
    --existing '<request>'      -> {"ok", "name", "matches": [{"registry_id", "name"}]}
    --check-address '<request>' -> {"ok", "problems": [{"key", "text", "fix"}], "found": {key: text}}
    A JSON list of requests (several customers in one sheet) is done in one browser visit and
    gives {"ok", "results": [one of the above per request, in order]}. The browser part gets
    one retry for what isn't done yet (Oracle's screens are sometimes slow)."""
    import contextlib
    import io
    out = sys.stdout
    try:
        raw = json.loads(argv[1] if len(argv) > 1 else "")
        reqs = raw if isinstance(raw, list) else [raw]
        items = []
        for req in reqs:
            ctype = req.get("customer_type", "Organization")
            name = req.get("name") if ctype == "Organization" else person_name(req)
            if ctype not in TYPES or not name:
                raise ValueError("no customer type or name")
            items.append((req, ctype, name))
    except (ValueError, AttributeError) as e:
        print(json.dumps({"ok": False, "text": f"The request couldn't be read ({e})."}), file=out)
        return 2
    results = {}
    for i, (req, ctype, name) in enumerate(items):
        if what == "address" and req.get("country", "United States") != "United States":
            results[i] = {"ok": True, "problems": [], "found": {}, "skipped": "country"}
        elif what == "address" and not any(req.get(k) for k in ("state", "city", "postal_code")):
            results[i] = {"ok": True, "problems": [], "found": {}}
    err = sys.stderr
    text = ("Oracle couldn't be searched for customers with this name." if what == "existing"
            else "Oracle's places couldn't be looked up.")
    # v2 (2026-10-26): up to 3 tries, each in a fresh browser, waiting 10 s then 30 s in between; what still
    # can't be checked comes back "held" (the page lets the rest go on). CUSTOMERS_TEST_GEO_FAILS=n (testing
    # only) makes the first n tries fail as if Oracle's places couldn't be looked up.
    import os
    test_fails = int(os.environ.get("CUSTOMERS_TEST_GEO_FAILS") or 0) if what == "address" else 0
    for attempt in (1, 2, 3):
        todo = [i for i in range(len(items)) if i not in results]
        if not todo:
            break
        if attempt > 1:
            time.sleep(10 if attempt == 2 else 30)
        log = io.StringIO()
        with contextlib.redirect_stdout(err), contextlib.redirect_stderr(log):
            try:
                oracle.check_environment()
                browser.refuse_production()
                work = oracle.init_work_dir(HERE)
                had_files = any(work.iterdir())       # a failed run's evidence and rerun note: kept
                if attempt <= test_fails:
                    raise RuntimeError(f"test switch: the places lookup made to fail (try {attempt})")
                with browser.OracleUI(work, headless=True) as ui:
                    if what == "address":
                        open_form(ui, "Organization")   # the geography dialogs are the same for persons
                    for i in todo:
                        req, ctype, name = items[i]
                        if what == "existing":
                            rows = search_customers(ui, name, ctype)
                            results[i] = {"ok": True, "name": name, "type": ctype,
                                          "matches": [{"registry_id": o["registry_id"], "name": o["name"]}
                                                      for o in rows if o["name"].lower() == name.lower()]}
                        else:
                            probs, found = address_problems(ui, req)
                            results[i] = {"ok": True, "problems": probs, "found": found}
                    if what == "address":
                        ui.click(ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).first, "Cancel")
                        ui.settle()
                if not had_files:
                    oracle.cleanup_work_dir()
            except SystemExit:
                pass
            except Exception as e:  # noqa: BLE001
                print(f"--{what} failed: {type(e).__name__}: {e}", file=log)
        err.write(log.getvalue())
        if re.search(r"sign-in", log.getvalue(), re.I):
            text = "Your Oracle sign-in has expired."
            break
        if len(results) < len(items):
            print(f"--{what}: try {attempt} left {len(items) - len(results)} not done", file=err)
    if len(results) < len(items) and not text.startswith("Your Oracle sign-in"):
        text = browser.failed_step_text(text)    # the real failed step, e.g. "Oracle's ... after 3 tries" (2026-10-26)
    full = [results.get(i) or ({"ok": False, "held": True, "text": text} if what == "address" else
                               {"ok": False, "text": text}) for i in range(len(items))]
    if isinstance(raw, list):
        print(json.dumps({"ok": all(r["ok"] for r in full), "results": full}), file=out)
    else:
        print(json.dumps(full[0]), file=out)
    return 0 if all(r["ok"] for r in full) else 1


# ---------------------------------------------------------------- --plan / --answer-check (v2, 2026-10-26)

LIST_KEYS = {"account_address_set": "Account Address Set", "account_type": "Account Type",
             "customer_class": "Customer Class", "country": "Country", "prefix": "Prefix",
             "site_language": "Site Language", "customer_category_code": "Customer Category Code"}
FIXED_LISTS = {"responsible_mineral_status": ["Conflict Free", "N/A", "No Data", "Undetermined"]}
PLAN_KEYS = ("site_language", "customer_category_code")      # the preview's own lists check the others


def list_problems(req, lists, keys):
    """A value of a list field that the Create Customer form doesn't offer: [{"key", "text", "fix", "suggestions"}]."""
    out = []
    for key in keys:
        v = req.get(key)
        if v in (None, ""):
            continue
        label = LIST_KEYS.get(key) or key.replace("_", " ").capitalize()
        opts = lists.get(key) if key in lists else [(x, x) for x in FIXED_LISTS.get(key, [])]
        if opts is None:
            continue
        if not opts:
            out.append({"key": key, "text": f"Oracle's {label} list is empty in this environment, so no value can be "
                        f"set; '{v}' would be refused.", "fix": f"Leave {label} empty.", "suggestions": []})
            continue
        hit = [o for o in opts if str(v).strip().lower() in (str(o[0]).lower(), str(o[1]).lower())]
        if not hit:
            sugg = [o[0] for o in opts]
            import difflib
            near = difflib.get_close_matches(str(v), [o[1] for o in opts], n=8, cutoff=0.4)
            out.append({"key": key, "text": f"{label} '{v}' is not one of the values Oracle offers.",
                        "fix": f"Pick one of: {', '.join(near or [o[1] for o in opts][:12])}.",
                        "suggestions": [o[0] for o in opts if o[1] in near] or sugg[:12]})
    for i, pu in enumerate(req.get("purposes") or [], 1):
        opts = lists.get("purposes.purpose")
        if opts and pu.get("purpose") and not any(str(pu["purpose"]).lower() == o[0].lower() for o in opts):
            out.append({"key": "purposes", "row": i, "text": f"Purpose '{pu['purpose']}' is not one Oracle offers.",
                        "fix": f"Pick one of: {', '.join(o[0] for o in opts)}.", "suggestions": [o[0] for o in opts]})
    return out


def plan_command(argv, answer=False):
    """--plan '<JSON list>' (read-only, the page's preview): the list fields the sheet itself can't check (Site
    Language, Customer Category Code) against the form's own lists; a browser visit only when one is filled.
    --answer-check '<JSON list>' (read-only, an answer in the page's decision panel): every list field and the
    State / City / Postal Code through the same path as Create. One JSON line {"ok", "results": [{"ok",
    "problems": [{"key", "text", "fix", "suggestions"}], "found"}]}."""
    import contextlib
    out = sys.stdout
    try:
        raw = json.loads(argv[1] if len(argv) > 1 else "")
        reqs = raw if isinstance(raw, list) else [raw]
    except ValueError as e:
        print(json.dumps({"ok": False, "text": f"The request couldn't be read ({e})."}), file=out)
        return 2
    keys = list(LIST_KEYS) + list(FIXED_LISTS) if answer else list(PLAN_KEYS)
    need = any(r.get(k) not in (None, "") for r in reqs for k in keys if k in LIST_KEYS) or         (answer and any(r.get("purposes") for r in reqs))
    results = []
    with contextlib.redirect_stdout(sys.stderr):
        try:
            lists = form_lists() if need else {}
            for r in reqs:
                probs = list_problems(r, lists, keys)
                found = {}
                if answer and r.get("country", "United States") == "United States" and                         any(r.get(k) for k in PLACE_KEYS):
                    oracle.check_environment()
                    work = oracle.init_work_dir(HERE)
                    had = any(work.iterdir())
                    with browser.OracleUI(work, headless=True) as ui:
                        open_form(ui, "Organization")
                        p2, found = address_problems(ui, r)
                        ui.click(ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).first, "Cancel")
                        ui.settle()
                    if not had:
                        oracle.cleanup_work_dir()
                    probs += p2
                results.append({"ok": True, "problems": probs, "found": found})
        except (SystemExit, Exception) as e:  # noqa: BLE001
            print(f"--plan failed: {type(e).__name__}: {e}", file=sys.stderr)
            print(json.dumps({"ok": False, "text": browser.failed_step_text("Oracle's lists couldn't be read just now.")}),
                  file=out)
            return 1
    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False), file=out)
    return 0


# ---------------------------------------------------------------- main

def main():
    if sys.argv[1:2] in (["--plan"], ["--answer-check"]):   # read-only (v2, 2026-10-26)
        sys.exit(plan_command(sys.argv[1:], answer=sys.argv[1] == "--answer-check"))
    if sys.argv[1:2] == ["--existing"]:          # read-only: same-name customers (the page's preview)
        sys.exit(preview_command(sys.argv[1:], "existing"))
    if sys.argv[1:2] == ["--check-address"]:     # read-only: City / State / Postal Code (the preview)
        sys.exit(preview_command(sys.argv[1:], "address"))
    page.main(SPEC, options_for, run_request)   # --spec / --options / --run; else returns
    here = HERE
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(here / "customers.json"), help="requirements JSON")
    ap.add_argument("--check", action="store_true",
                    help="validate values against the screen and check existence; save nothing")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    args = ap.parse_args()

    oracle.check_environment()
    browser.refuse_production()
    customers = load_requirements(args.file)
    print(f"{len(customers)} customer(s) requested in {args.file}")
    run_customers(args, customers, here)


def run_customers(args, customers, here, progress=None, found=None):
    """The normal run for the requested customers (same-name search, form, save, verify).
    A customer is created even when others have its name (they are never touched).
    progress: the page's progress lines (--run). found (optional dict): filled with
    {name: {"registry_id", "same_name_before", "saved_earlier", "values", "set_name",
    "purposes"}}."""
    def step(key, percent=None, text=None):
        if progress:
            progress.step(key, percent, text)

    work = oracle.init_work_dir(here)
    created, all_ok, left = [], True, 0
    form_checked = set()   # customer types whose form --check has opened

    with browser.OracleUI(work, headless=not args.headed) as ui:
        for cust in customers:
            name, ctype, fields = cust["name"], cust["type"], cust["fields"]
            print(f"\n== {name}" + (" (person)" if ctype == "Person" else ""))
            before = search_customers(ui, name, ctype)
            same_name = [o for o in before if o["name"].lower() == name.lower()]
            before_ids = [o["registry_id"] for o in same_name]
            prefix = name[:PREFIX_LEN]
            earlier = None if args.check else journal(work, cust["key"])
            if earlier and [i for i in before_ids if i not in earlier["before_ids"]]:
                # An earlier try of this same request saved it (then the run stopped: sign-in,
                # repair): verify that customer, never save a second one.
                print(f"  NOTE  an earlier try of this request saved {name} (registry ID "
                      f"{earlier['registry_id']}); verifying it, not creating it again")
                cust.update(want=earlier["want"], purposes=earlier["purposes"], set_name=earlier["set_name"],
                            oracle_today=earlier.get("oracle_today"))
                expected, before_ids = earlier["expected"], earlier["before_ids"]
                registry_id, warned = earlier["registry_id"], earlier.get("warned") or []
                neighbours = [dict(o, rest=tuple(o["rest"])) for o in earlier["neighbours"]]
                again = True
            else:
                again = False
                if same_name:
                    print(f"  NOTE  {len(same_name)} customer(s) named {name} already exist (registry ID "
                          f"{', '.join(before_ids)}); they are not touched and a new one is created")
                else:
                    print(f"  {name}: no customer with this name yet; {len(before)} start with it")
                neighbours = search_customers(ui, prefix, ctype) if prefix != name else before
                print(f"  snapshot: {len(neighbours)} existing customer(s) shown for '{prefix}' "
                      "(compared again after saving)")

                step("filling", 35, "Filling in the customer form")
                open_form(ui, ctype)
                with ui.step("read the Registry ID the form shows"):
                    registry_id = form_registry_id(ui)
                print(f"  Registry ID on the form: {registry_id or '(not shown)'}")
                with ui.step("read the Account Address Set list"):
                    sets = address_sets(ui)
                print(f"  {len(sets)} account address sets on the screen")
                cust["oracle_today"] = resolve_today(ui, cust).isoformat()
                fill_form(ui, cust, sets)
                expected = defaults_of(ui, fields)
                for key, v in cust["want"].items():
                    if fields[key][1] != "set" and expected.get(key) != v and not same(fields[key][1], expected.get(key), v):
                        ui.fail("fill", f"{fields[key][0]} shows {expected.get(key)!r} after filling, "
                                        f"expected {v!r}.")
                defaults = {fields[k][0]: v for k, v in expected.items()
                            if k not in cust["want"] and v not in ("", None)}
                print(f"  filled; form defaults kept: {defaults or 'none'}")
                ui.page.screenshot(path=str(work / f"before_save_{name}.png"), full_page=True)
                if args.check:
                    print("  CHECK  all values accepted by the form; not saving (--check)")
                    form_checked.add(ctype)
                    ui.click(ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).first, "Cancel")
                    ui.settle()
                    continue
                step("creating", 60, "Saving the customer in Oracle")
                memo = {"registry_id": registry_id, "before_ids": before_ids, "want": cust["want"],
                        "purposes": cust["purposes"], "set_name": cust.get("set_name"),
                        "expected": expected, "neighbours": neighbours, "oracle_today": cust["oracle_today"]}
                journal(work, cust["key"], dict(memo, state="saving"))
                try:
                    warned = save(ui, name)
                except SaveMessage as e:
                    warned = []
                    print(f"  NOTE  Oracle showed a message after Save and Close: {e} - checking Oracle")
                    try:
                        ui.close_messages()
                    except Exception:  # noqa: BLE001 - the form is left next anyway
                        pass
                    try:
                        leave_form(ui)
                    except BaseException:  # noqa: BLE001 - the form may have closed already
                        pass
                    org, _rows = find_new(ui, cust, registry_id, before_ids)
                    if org is None:
                        journal_drop(work, cust["key"])
                        oracle.fail(f"Oracle did not save {name}: {e} (checked in Oracle: no new customer "
                                    f"named {name}).")
                    print(f"  NOTE  Oracle saved {name} anyway (Registry ID {org['registry_id']}); checking it")
                    registry_id = org["registry_id"]
                    memo["registry_id"] = registry_id
                    if found is not None:
                        found.setdefault(name, {})["save_message"] = str(e)
                journal(work, cust["key"], dict(memo, state="saved", warned=warned))
                if os.environ.get("CUSTOMERS_TEST_FAIL_AFTER_SAVE"):
                    # testing only: a failure right after the save, to prove the card never hides it
                    oracle.fail(f"test switch: the run was stopped right after saving {name}.")
                print(f"  saved {name}" + (" (Oracle's matching warning: Option 2, create new)" if warned else ""))

            step("verifying", 80, "Checking the customer, its account and its address")
            print("  Verifying (the new customer by its registry ID, account, site, purposes) ...")
            ok, org = verify(ui, cust, expected, registry_id, before_ids)
            if found is not None:
                found[name] = {"registry_id": org and org["registry_id"],
                               "same_name_before": before_ids, "saved_earlier": again,
                               "values": {k: expected.get(k) for k in cust["want"]},
                               "set_name": cust.get("set_name"),
                               "purposes": [{"purpose": p["purpose"],
                                             "from_date": p["from_date"] or p.get("from_shown"),
                                             "to_date": p["to_date"] or None,
                                             "primary": p.get("primary") or bool(p.get("primary_shown")),
                                             "bill_to_site": p.get("bill_to_site") or None}
                                            for p in cust["purposes"]]}
            after = {o["registry_id"]: o for o in search_customers(ui, prefix, ctype)}
            changed = [(o, after[o["registry_id"]]) for o in neighbours
                       if o["registry_id"] in after and after[o["registry_id"]] != o]
            gone = [o["registry_id"] for o in neighbours if o["registry_id"] not in after]
            if changed:
                print(f"  FAIL  existing customers changed (before, after): {changed}")
                ok = False
            else:
                print(f"  OK    existing customers for '{prefix}' unchanged "
                      f"({len(neighbours) - len(gone)} compared: name, country, primary address)")
            if gone:
                print(f"  NOTE  not shown in the second search (list paging): {', '.join(gone)}")
            all_ok &= ok
            if ok:
                created.append(name)
                left = journal_drop(work, cust["key"])

        for ctype in dict.fromkeys(c["type"] for c in customers):
            if not args.check or ctype in form_checked:
                continue
            # Every requested customer of this type exists: still prove its form works.
            print(f"\n== {ctype} form check (no new {ctype.lower()} customer in the request)")
            open_form(ui, ctype)
            with ui.step("read the Account Address Set list"):
                print(f"  {len(address_sets(ui))} account address sets on the screen")
            with ui.step("read Oracle's today"):
                today = resolve_today(ui, {"want": {}, "purposes": []})
                print(f"  Oracle's today (form default From Date): {today.isoformat()}")
            ui.click(ui.page.get_by_role("button", name=re.compile(r"^Cancel$")).first, "Cancel")
            ui.settle()
            print(f"  CHECK  {TYPES[ctype]['title']} form opens; left with Cancel, nothing saved")

    print(f"\nCreated and verified: {', '.join(created) or 'none'}")
    if not all_ok:
        oracle.fail("Verification failed - see FAIL lines above.")
    if args.check:
        print(f"Check only: nothing saved. Files kept in {work}")
        return created
    if created and left:
        # Several customers per sheet run one after another: the note of another customer's
        # saved-but-unchecked try must survive, or its retry would save it twice (2026-10-23).
        print(f"Kept {work}: {left} other saved customer(s) still to be checked by a retry")
        return created
    oracle.cleanup_work_dir()
    return created


if __name__ == "__main__":
    main()
