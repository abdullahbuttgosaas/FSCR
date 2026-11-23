"""Price lists from a sheet (2026-10-26, scope A: the price list header, its line defaults, access sets and
approval). Every check up front, then the price lists one after another, with Oracle's answer per price list.

  python "Price Lists/run.py" --plan '<JSON list or one request>'      # read-only
  python "Price Lists/run.py" --run-batch '<JSON list of requests>'
  python "Price Lists/run.py" --time-zone                             # read the Oracle user's time zone (screen, read-only)

A request (the Create Price List screen's fields):
  {"name": "Retail USD 2027",                 # required, max 80, no single quote, no outer spaces
   "description": "...",                      # optional, max 1000
   "type": "Segment price list",              # optional: Segment (default), Floor, GSA, Ceiling (code or name)
   "currency": "USD",                         # required: code or name (enabled currencies)
   "business_unit": "ABD",                    # required: one the user has Pricing Administrator access on
   "business_unit_pending": false,            # true: created earlier in the same upload (waited for, never guessed)
   "start_date": "2026-10-27",                # required: YYYY-MM-DD or "today" (the user's today)
   "end_date": "2027-12-31",                  # optional, after the start date
   "charge_definition": "Sale Price",         # optional: Sale Price / Recurring Sale Price (code or name)
   "line_type": "Buy",                        # optional: Buy (default)
   "calculation_method": "Price",             # optional: Price (default), Cost, Covered item price percent,
                                              #           Source document cost (code or name)
   "access_sets": ["001 CUSTOMER SITE"]}      # required, one or more (code or name); also [{"name": ...}]

Dates: the screen shows a price list's dates in the Oracle USER's time zone (Set Preferences > Regional, e.g.
"(UTC-05:00) New York - Eastern Time (ET)"), Oracle stores the moment in UTC. A plain date is sent as 12:00 AM
of that date in the user's time zone (daylight saving included), so the screen shows exactly that date at
12:00 AM. The zone is read from the screen once and kept in oracle_time_zone.json; without it nothing is sent.

Create, per price list (nothing sent unless all its checks passed): header (POST priceLists, Oracle makes it
In progress) -> access sets (POST accessSets) -> approval (PATCH StatusCode APPROVED) -> read back (header,
access sets, status, dates). An existing price list is never changed; a half-made one (same header, In
progress) is completed: only its missing access sets and the approval.
"""
import contextlib
import difflib
import json
import re
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, available_timezones

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import oracle, page  # noqa: E402

HERE = Path(__file__).resolve().parent
RESOURCE = "priceLists"
TZ_FILE = HERE / "oracle_time_zone.json"
TZ_MAX_AGE = 7 * 86400               # the zone is read again from the screen after a week
ACCESS_USER = "Configuration.TEST"   # the REST login: price lists are made by it (CreatedBy), so its access counts
PRICING_ROLE = "ORA_QP_PRICING_ADMINISTRATOR_JOB"   # the role that puts a business unit on the Create screen
NAME_MAX, DESC_MAX = 80, 1000
CURRENCY_MAX = 3                     # priceLists/describe CurrencyCode precision (2026-10-26)
KEYS = ("name", "description", "type", "currency", "business_unit", "business_unit_pending", "start_date",
        "end_date", "charge_definition", "line_type", "calculation_method", "access_sets")
WAIT_BU, WAIT_EVERY = 300, 15        # a pending business unit: up to 5 minutes, a read every 15 s
WHERE = "Order Management > Pricing Administration > Manage Price Lists, search for {name}"
TEST_PREFIX = "ZZ_TEST_"


# ---------------------------------------------------------------- the Oracle user's time zone

def zone_of(label):
    """Oracle's label "(UTC-05:00) New York - Eastern Time (ET)" -> "America/New_York" (the city), or None."""
    if not label:
        return None
    if "Coordinated Universal Time" in label:
        return "UTC"
    m = re.match(r"\(UTC[^)]*\)\s*(.+?)\s+-\s", label)
    if not m:
        return None
    city = m.group(1).strip().replace(" ", "_")
    hits = [z for z in available_timezones() if z.split("/")[-1].lower() == city.lower()]
    return sorted(hits, key=len)[0] if hits else None


def read_zone_from_screen():
    """Settings and Actions > Set Preferences > Regional > Time Zone (read-only; nothing is changed)."""
    from common import browser
    with browser.OracleUI(oracle.init_work_dir(HERE), headless=True) as ui:
        p = ui.page
        p.goto(browser.start_url(), wait_until="domcontentloaded", timeout=120000)
        ui.settle(); ui.check_signed_in(); p.wait_for_timeout(3000)
        prefs = p.locator("a:visible").filter(has_text=re.compile(r"^\s*Set Preferences\s*$")).first
        reg = p.locator("a:visible").filter(has_text=re.compile(r"^\s*Regional\s*$")).first
        read = lambda: dict(p.evaluate("""() => [...document.querySelectorAll('select')].filter(e=>e.offsetWidth).map(e => {
            const l = e.id ? document.querySelector(`label[for="${CSS.escape(e.id)}"]`) : null;
            return [(l ? l.innerText : e.getAttribute('aria-label') || e.title || '').trim(),
                    (e.options[e.selectedIndex] || {}).text || '']; })"""))   # noqa: E731
        # 2026-10-26: each click checked and done again when lost (shared retry helper); nothing is changed here
        ui.retry("Settings and Actions menu did not open",
                 lambda attempt: prefs.count() or ui.click(p.locator("[title='Settings and Actions']:visible").first,
                                                           "Settings and Actions"),
                 lambda timeout: prefs.wait_for(timeout=timeout), wait=15000, last_wait=30000)

        def open_prefs(attempt):
            if prefs.count():
                ui.click(prefs, "Set Preferences")
            ui.settle()

        def regional_or_zone(timeout):
            end = time.time() + timeout / 1000
            while time.time() < end:
                if reg.count() or "Time Zone" in read():
                    return True
                p.wait_for_timeout(1000)
            return False
        ui.retry("Set Preferences did not open", open_prefs, regional_or_zone, wait=30000, last_wait=60000)

        def open_regional(attempt):
            if reg.count() and "Time Zone" not in read():
                ui.click(reg, "Regional")
            ui.settle()

        def zone_shown(timeout):
            end = time.time() + timeout / 1000
            while time.time() < end:
                if read().get("Time Zone"):
                    return True
                p.wait_for_timeout(1000)
            return False
        ui.retry("Set Preferences did not show the Regional Time Zone", open_regional, zone_shown,
                 wait=30000, last_wait=60000)
        vals = read()
    oracle.cleanup_work_dir()
    return vals.get("Time Zone"), vals


def user_zone(refresh=False):
    """(IANA zone, Oracle's label) of the Oracle user's time zone: the saved answer (a week at most), else
    read from the screen. None, reason when it can't be told (then no date is sent)."""
    saved = {}
    try:
        saved = json.loads(TZ_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    fresh = saved.get("zone") and time.time() - saved.get("saved", 0) < TZ_MAX_AGE
    if fresh and not refresh:
        return saved["zone"], saved["label"]
    try:
        label, vals = read_zone_from_screen()
    except BaseException as e:  # noqa: BLE001 - a screen that can't be read: the saved answer, else stop
        if saved.get("zone"):
            print(f"  NOTE  the time zone couldn't be read again ({str(e)[:200]}); using the saved one {saved['label']}")
            return saved["zone"], saved["label"]
        return None, f"the Oracle user's time zone couldn't be read ({str(e)[:200]})"
    if not label:                    # 2026-10-26: an unread label is an error, not a zone
        if saved.get("zone"):
            return saved["zone"], saved["label"]
        return None, "the Oracle user's time zone couldn't be read (Set Preferences showed no Time Zone)"
    zone = zone_of(label)
    if not zone:
        return None, f"Oracle's time zone '{label}' couldn't be matched to a known zone"
    TZ_FILE.write_text(json.dumps({"label": label, "zone": zone, "saved": time.time(),
                                   "read_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                   "date_format": vals.get("Date Format"), "time_format": vals.get("Time Format"),
                                   "about": "The Oracle user's time zone (Set Preferences > Regional), read from the "
                                            "screen by pl_batch.py; dates are sent as 12:00 AM in this zone."},
                                  indent=1), encoding="utf-8")
    print(f"  time zone of the Oracle user: {label} = {zone}")
    return zone, label


def at_midnight(d, zone):
    """A plain date -> 12:00 AM of that date in the user's zone, as Oracle's datetime text."""
    return datetime(d.year, d.month, d.day, tzinfo=ZoneInfo(zone)).isoformat()


def shown(iso, zone):
    """A stored moment as the screen shows it: "10/27/26 12:00 AM"."""
    if not iso:
        return None
    t = datetime.fromisoformat(iso).astimezone(ZoneInfo(zone))
    return f"{t.month}/{t.day}/{t:%y} {int(t.strftime('%I'))}:{t:%M} {t:%p}"


def user_today(zone):
    return datetime.now(ZoneInfo(zone)).date()


# ---------------------------------------------------------------- Oracle's lists (GET only)

def get_all(path, **params):
    out, off = [], 0
    while True:
        r, err = oracle.try_call("GET", f"{oracle.API_BASE}/{path}", timeout=300,
                                 params={"onlyData": "true", "limit": 200, "offset": off, **params})
        if err and r is None:                   # a network blip: one more try (reads only)
            time.sleep(8)
            r, err = oracle.try_call("GET", f"{oracle.API_BASE}/{path}", timeout=300,
                                     params={"onlyData": "true", "limit": 200, "offset": off, **params})
        if err:
            raise RuntimeError(f"{path}: {err.splitlines()[0]} {err.splitlines()[1] if len(err.splitlines()) > 1 else ''}")
        d = r.json()
        out += d.get("items", [])
        if not d.get("hasMore"):
            return out
        off += len(d.get("items", []))


def lookup(ltype):
    return [(c["LookupCode"], c["Meaning"]) for c in get_all(f"standardLookups/{ltype}/child/lookupCodes")
            if c.get("EnabledFlag") == "Y"]


class Lists:
    """Each list read once per run."""

    def __init__(self):
        self.cache = {}

    def _get(self, key, fn):
        if key not in self.cache:
            self.cache[key] = fn()
        return self.cache[key]

    def currencies(self):
        return self._get("cur", lambda: [(i["CurrencyCode"], (i.get("Name") or "").strip())
                                         for i in get_all("currenciesLOV", q="EnabledFlag='Y'")])

    def sets(self):
        return self._get("sets", lambda: [(i["SetCode"], i.get("SetName") or i["SetCode"]) for i in get_all("setIdSetsLOV")])

    def types(self):          # the screen's four (Return price lists have their own task: not in scope)
        return self._get("types", lambda: [x for x in lookup("ORA_QP_PRICE_LIST_TYPES") if x[0] != "RETURN"])

    def line_types(self):
        return self._get("lines", lambda: lookup("ORA_QP_ORDER_LINE_TYPES"))

    def methods(self):        # the screen's four (the pricing matrix method is not on the screen)
        return self._get("methods", lambda: [x for x in lookup("ORA_QP_PRCLT_CALC_METHODS") if x[0] != "ORA_QP_BASE_PRICE_MATRIX"])

    def charge_defs(self):
        return self._get("defs", lambda: [(i["PricingChargeDefinitionCode"], i.get("PricingChargeDefintion") or "",
                                            i.get("PricingChargeDefinitionId")) for i in get_all("chargeDefinitionsLOV")])

    def business_units(self, fresh=False):
        if fresh:
            self.cache.pop("bus", None)
        return self._get("bus", lambda: get_all("finBusinessUnitsLOV"))

    def pricing_units(self, fresh=False):
        """The business units the user can make price lists for: an active data access row with the Pricing
        Administrator role (exactly the Create Price List screen's Business Unit list, checked 2026-10-26)."""
        if fresh:
            self.cache.pop("pricing", None)

        def read():
            rows = get_all("dataSecurities", orderBy="UserRoleDataAssignmentId:asc")
            return sorted({r["SecurityContextValue"] for r in rows
                           if r.get("UserName") == ACCESS_USER and r.get("SecurityContext") == "Business unit"
                           and r.get("RoleCommonName") == PRICING_ROLE and r.get("ActiveFlag") is True})
        return self._get("pricing", read)

    def price_lists(self, fresh=False):
        if fresh:
            self.cache.pop("pls", None)
        return self._get("pls", lambda: get_all(RESOURCE, expand="accessSets"))


def pick(value, choices, what):
    """(code, name) for a value given by code or name (capitals and extra spaces ignored), or None."""
    v = " ".join(str(value).split()).lower()
    for c in choices:
        if v in (str(c[0]).lower(), " ".join(str(c[1]).split()).lower()):
            return c[0], c[1]
    # "Segment" for "Segment price list"
    hits = [c for c in choices if " ".join(str(c[1]).split()).lower().startswith(v + " ")]
    return (hits[0][0], hits[0][1]) if len(hits) == 1 else None


def close(word, names, n=8):
    w = " ".join(str(word).split()).lower()
    first = [x for x in names if w and x.lower().startswith(w[:3])]
    near = difflib.get_close_matches(word, names, n=n, cutoff=0.5)
    return list(dict.fromkeys(near + first))[:n]


# ---------------------------------------------------------------- one price list

class PL:
    def __init__(self, req, i):
        self.req, self.i = (req if isinstance(req, dict) else {}), i
        self.name = self.req.get("name") if isinstance(self.req.get("name"), str) else None
        self.problems, self.notes = [], []
        self.status = None          # new | exists | incomplete | waiting | problems
        self.body, self.set_codes, self.existing = {}, [], None
        self.start = self.end = None
        self.waiting = False

    def bad(self, field, value, reason, suggestions=None, fix=None):
        self.problems.append({"price_list": self.name, "business_unit": self.req.get("business_unit"), "field": field,
                              "key": field, "value": value, "reason": reason, "text": reason,
                              "suggestions": list(suggestions or [])[:12],
                              "fix": fix or (f"Pick one of: {', '.join(map(str, list(suggestions)[:12]))}." if suggestions
                                             else "Please correct it in the sheet.")})


def sets_of(req):
    a = req.get("access_sets")
    if isinstance(a, str):
        a = [a]
    out = []
    for x in a or []:
        out.append(x.get("name") if isinstance(x, dict) else x)
    return out


def check_rules(p, zone):
    r = p.req
    unknown = sorted(set(r) - set(KEYS))
    if unknown:
        p.bad(unknown[0], r[unknown[0]], f"These can't be set on a price list here: {', '.join(unknown)} (items, "
              "charges and tiers are not part of this).")
    n = r.get("name")
    if not isinstance(n, str) or not n.strip():
        p.bad("name", n, "The price list name is missing.")
    elif n != n.strip():
        p.bad("name", n, "The name starts or ends with a space; please remove it.", [n.strip()],
              fix="Remove the space at the start or end.")
    elif len(n) > NAME_MAX:
        p.bad("name", n, f"The name is {len(n)} characters long; Oracle takes at most {NAME_MAX}.",
              fix=f"Shorten it to {NAME_MAX} characters or fewer.")
    elif "'" in n:
        p.bad("name", n, "The name can't contain a single quote (').", fix="Remove the ' from the name.")
    d = r.get("description")
    if d not in (None, ""):
        if not isinstance(d, str):
            p.bad("description", d, "Item Description must be text.")
        elif len(d) > DESC_MAX:
            p.bad("description", d, f"Item Description is {len(d)} characters long; Oracle takes at most {DESC_MAX}.",
                  fix=f"Shorten it to {DESC_MAX} characters or fewer.")
        elif "'" in d:
            p.bad("description", d, "Item Description can't contain a single quote (').")
    for k in ("currency", "business_unit"):
        if not isinstance(r.get(k), str) or not r.get(k).strip():
            p.bad(k, r.get(k), f"{'Currency' if k == 'currency' else 'Business Unit'} is missing.")
    if not isinstance(r.get("business_unit_pending", False), bool):
        p.bad("business_unit_pending", r.get("business_unit_pending"), "business_unit_pending must be true or false.")
    sets = sets_of(r)
    if not sets:
        p.bad("access_sets", None, "At least one access set is needed: Oracle approves a price list only with one.")
    seen = set()
    for s in sets:
        if not isinstance(s, str) or not s.strip():
            p.bad("access_sets", s, "An access set is empty.")
        elif s.strip().lower() in seen:
            p.bad("access_sets", s, f"Access set '{s}' is listed twice.", fix="Keep it once.")
        seen.add(str(s).strip().lower())
    # dates
    for k, label in (("start_date", "Start Date"), ("end_date", "End Date")):
        v = r.get(k)
        if v in (None, ""):
            if k == "start_date":
                p.bad(k, v, "Start Date is missing.")
            continue
        if isinstance(v, str) and v.strip().lower() == "today":
            d_ = user_today(zone) if zone else None
        else:
            try:
                d_ = date.fromisoformat(str(v))
            except ValueError:
                p.bad(k, v, f"{label} must be a date written as YYYY-MM-DD; it says '{v}'.", fix="Write it like 2026-11-01.")
                continue
        setattr(p, "start" if k == "start_date" else "end", d_)
    # Oracle: "You must enter a start date that's on or before the end date." (2026-10-26, ZZ_TEST_PL_8034_B2BAD)
    if p.start and p.end and p.end < p.start:
        p.bad("end_date", r.get("end_date"), f"End Date ({p.end}) is before Start Date ({p.start}). Oracle: \"You must "
              "enter a start date that's on or before the end date.\"",
              fix=f"Write {p.start} or a later date, or leave End Date empty.")


def check_oracle(pls, lists, zone):
    names_seen = {}
    existing = {x["PriceListName"]: x for x in lists.price_lists()}
    pricing = lists.pricing_units()
    bus = {b["BusinessUnitName"]: b for b in lists.business_units()}
    for p in pls:
        r = p.req
        if p.name:
            if p.name in names_seen:
                p.bad("name", p.name, f"'{p.name}' is listed twice; each price list can be there only once.",
                      fix="Keep one of the two rows.")
            names_seen[p.name] = p
            p.existing = existing.get(p.name)
            twins = [n for n in existing if n.lower() == p.name.lower() and n != p.name]
            if twins:
                p.notes.append(f"Oracle has a price list '{twins[0]}' that differs only in capitals.")
        # currency
        if isinstance(r.get("currency"), str) and r["currency"].strip():
            c = pick(r["currency"], lists.currencies(), "currency")
            if not c:
                cur = lists.currencies()
                p.bad("currency", r["currency"], f"'{r['currency']}' is not one of Oracle's {len(cur)} enabled currencies.",
                      [x[0] for x in cur if x[0] in close(r["currency"].upper(), [y[0] for y in cur])]
                      or [y.split(" ")[0] for y in close(r["currency"], [f"{x[0]} ({x[1]})" for x in cur])]
                      or [x for x in ("USD", "EUR", "GBP", "PKR", "AFN") if x in {y[0] for y in cur}])
            elif len(c[0]) > CURRENCY_MAX:
                # seen 2026-10-21: currency 1214 is enabled, but Oracle refused it ("Value 1214 for field CurrencyCode
                # exceeds the maximum length allowed."); priceLists/describe: CurrencyCode is 3 characters
                cur = [x for x in lists.currencies() if len(x[0]) <= CURRENCY_MAX]
                p.bad("currency", r["currency"], f"Currency '{c[0]}' can't be used on a price list: Oracle takes only "
                      f"currency codes of {CURRENCY_MAX} letters.",
                      [x[0] for x in cur if x[0] in close(c[0].upper(), [y[0] for y in cur])]
                      or [x for x in ("USD", "EUR", "GBP", "PKR") if x in {y[0] for y in cur}],
                      fix="Use a three-letter currency code such as USD.")
            else:
                p.body["CurrencyCode"] = c[0]
                p.currency = c
        # business unit: in the user's pricing access list, and active
        bu = r.get("business_unit")
        if isinstance(bu, str) and bu.strip():
            hit = next((n for n in pricing if n == bu), None) or next((n for n in pricing if n.lower() == bu.lower()), None)
            b = bus.get(hit or bu) or next((x for k, x in bus.items() if k.lower() == bu.lower()), None)
            if hit and b and b.get("ActiveFlag") is False:
                p.bad("business_unit", bu, f"The business unit '{hit}' is inactive, so no price list is made for it.",
                      close(bu, [n for n in pricing if (bus.get(n) or {}).get("ActiveFlag") is not False]))
            elif hit:
                p.body["BusinessUnit"] = hit
                p.bu_id = (b or {}).get("BusinessUnitId")
            elif r.get("business_unit_pending"):
                p.waiting = True
                p.body["BusinessUnit"] = bu
                p.notes.append(f"Waits for the business unit {bu}, which is created earlier in the same upload: the price "
                               "list is made only once Oracle shows it for pricing.")
            elif b:
                p.bad("business_unit", bu, f"{ACCESS_USER} has no Pricing Administrator access on the business unit "
                      f"'{b['BusinessUnitName']}', so Oracle doesn't offer it for price lists.", close(bu, pricing))
            else:
                p.bad("business_unit", bu, f"Oracle has no business unit '{bu}' that can be used for price lists.",
                      close(bu, pricing) or [n for n in pricing if (bus.get(n) or {}).get("ActiveFlag") is not False][:8])
        # type, line type, method, charge definition (defaults as on the screen)
        for key, label, choices, default, field in (
                ("type", "Type", lists.types(), "SEGMENT", "PriceListTypeCode"),
                ("line_type", "Line Type", lists.line_types(), "ORA_BUY", "LineTypeCode"),
                ("calculation_method", "Calculation Method", lists.methods(), "PRICE", "CalculationMethodCode")):
            v = r.get(key)
            if v in (None, ""):
                p.body[field] = default
                continue
            c = pick(v, choices, key)
            if not c:
                p.bad(key, v, f"'{v}' is not a {label} Oracle offers here.", [x[1] for x in choices])
            else:
                p.body[field] = c[0]
        v = r.get("charge_definition")
        if v not in (None, ""):
            defs = lists.charge_defs()
            c = next((d for d in defs if str(v).strip().lower() in (d[0].lower(), d[1].lower())), None)
            if not c:
                p.bad("charge_definition", v, f"'{v}' is not a Pricing Charge Definition Oracle offers here.", [d[1] for d in defs])
            else:
                p.body["PricingChargeDefinitionCode"] = c[0]
                p.charge_def = c
        # access sets
        sets = lists.sets()
        for s in sets_of(r):
            if not isinstance(s, str) or not s.strip():
                continue
            c = pick(s, sets, "access set")
            if not c:
                p.bad("access_sets", s, f"'{s}' is not one of Oracle's {len(sets)} reference data sets.",
                      [x[0] for x in sets if x[0] in close(s.upper(), [y[0] for y in sets])] or [x[0] for x in sets][:12])
            elif c[0] not in p.set_codes:
                p.set_codes.append(c[0])
        # header body
        if p.name:
            p.body["PriceListName"] = p.name
        if r.get("description"):
            p.body["PriceListDescription"] = r["description"]
        if zone and p.start:
            p.body["StartDate"] = at_midnight(p.start, zone)
        if zone and p.end:
            p.body["EndDate"] = at_midnight(p.end, zone)


def compare_header(p, it, zone):
    """Differences between what a price list should be and what Oracle has."""
    want = dict(p.body)
    diffs = []
    for k in ("PriceListName", "CurrencyCode", "PriceListTypeCode", "LineTypeCode", "CalculationMethodCode",
              "PricingChargeDefinitionCode", "PriceListDescription"):
        if (want.get(k) or None) != (it.get(k) or None):
            diffs.append(f"{k}: Oracle has {it.get(k)!r}, wanted {want.get(k)!r}")
    if getattr(p, "bu_id", None) and it.get("BusinessUnitId") != p.bu_id:
        diffs.append(f"BusinessUnitId: Oracle has {it.get('BusinessUnitId')}, wanted {p.bu_id}")
    for k in ("StartDate", "EndDate"):
        w, g = want.get(k), it.get(k)
        if bool(w) != bool(g) or (w and datetime.fromisoformat(w) != datetime.fromisoformat(g)):
            diffs.append(f"{k}: Oracle shows {shown(g, zone) if g else 'none'}, wanted {shown(w, zone) if w else 'none'}")
    return diffs


def plan(reqs, lists=None, need_zone=True):
    lists = lists or Lists()
    Lists_cache.value = lists
    zone, label = user_zone() if need_zone else (None, None)
    pls = [PL(r, i) for i, r in enumerate(reqs)]
    for p in pls:
        if not isinstance(p.req, dict) or not p.req:
            p.bad("name", None, "This row could not be read.")
            continue
        check_rules(p, zone)
        if not zone:
            p.bad("start_date", p.req.get("start_date"), f"Dates can't be stored correctly: {label}. Nothing is sent "
                  "until the Oracle user's time zone is known.")
    check_oracle(pls, lists, zone)
    for p in pls:
        if p.problems:
            p.status = "problems"
        elif p.existing:
            e = p.existing
            have = {a.get("AccessSetCode") for a in e.get("accessSets") or []}
            missing = [c for c in p.set_codes if c not in have]
            diffs = compare_header(p, e, zone)
            if e.get("StatusCode") == "APPROVED":
                p.status = "exists"
                if missing:
                    p.notes.append(f"It is approved already; the access set(s) {', '.join(missing)} are NOT added (an "
                                   "existing price list is never changed).")
            elif diffs:
                p.status = "exists"
                p.notes.append("It is in Oracle (In progress) with other values, so it isn't completed: "
                               + "; ".join(diffs[:4]) + ".")
            else:
                p.status = "incomplete"
                p.missing_sets = missing
        else:
            p.status = "waiting" if p.waiting else "new"
    return pls, zone, label


def will_get(p, zone):
    if p.status == "problems":
        return None
    b, lst = p.body, Lists_cache.get()
    return {"Name": p.name, "Item Description": b.get("PriceListDescription") or "(none)",
            "Type": label_of(lst.types(), b.get("PriceListTypeCode")),
            "Currency": f"{b.get('CurrencyCode')} - {getattr(p, 'currency', (None, ''))[1]}",
            "Business Unit": b.get("BusinessUnit"),
            "Start Date": shown(b.get("StartDate"), zone), "End Date": shown(b.get("EndDate"), zone) or "(none)",
            "Pricing Charge Definition": getattr(p, "charge_def", (None, "(none)"))[1],
            "Line Type": label_of(lst.line_types(), b.get("LineTypeCode")),
            "Calculation Method": label_of(lst.methods(), b.get("CalculationMethodCode")),
            "Access Sets": ", ".join(p.set_codes), "Status": "Approved"}


class Lists_cache:              # the plan's lists, for will_get()
    value = None

    @classmethod
    def get(cls):
        return cls.value


def label_of(choices, code):
    return next((c[1] for c in choices if c[0] == code), code)


def plan_text(p, zone):
    if p.status == "problems":
        return " ".join(x["reason"] for x in p.problems) + " Nothing will be sent for it."
    if p.status == "exists":
        e = p.existing
        return (f"Already in Oracle ({(e.get('StatusCode') or '').replace('_', ' ').lower()}, access sets "
                f"{', '.join(a.get('AccessSetCode') for a in e.get('accessSets') or []) or 'none'}): it is skipped and not "
                "changed." + ("" if not p.notes else " " + " ".join(p.notes)))
    if p.status == "incomplete":
        return (f"Already in Oracle but not finished (in progress): only what is missing will be done: "
                + (f"access set(s) {', '.join(p.missing_sets)}, " if p.missing_sets else "") + "then the approval.")
    g = will_get(p, zone)
    lead = "Waits for its business unit, then new: " if p.status == "waiting" else "New: "
    return (lead + f"{g['Name']}, {g['Type']}, {g['Currency']}, business unit {g['Business Unit']}, from {g['Start Date']}"
            + (f" to {g['End Date']}" if g["End Date"] != "(none)" else "") + f", line defaults {g['Pricing Charge Definition']} / "
            f"{g['Line Type']} / {g['Calculation Method']}, access sets {g['Access Sets']}; then approved."
            + ("" if not p.notes else " " + " ".join(p.notes)))


# ---------------------------------------------------------------- create, complete, read back

def oracle_text(err):
    """Oracle's own words from a failed call."""
    body = (err or "").split("\n", 2)[-1].strip()
    try:
        d = json.loads(body)
        body = d.get("detail") or d.get("title") or body
        if isinstance(body, list):
            body = "; ".join(str(x.get("detail", x)) if isinstance(x, dict) else str(x) for x in body)
    except ValueError:
        pass
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(body))).strip()[:500] or "Oracle gave no reason"


def call(method, path, body=None):
    r, err = oracle.try_call(method, f"{oracle.API_BASE}/{path}", json=body, timeout=180)
    if err:
        return None, oracle_text(err), (r.status_code if r is not None else None)
    return (r.json() if r.content else {}), None, r.status_code


def wait_for_unit(p, lists, progress=None):
    """A business unit created earlier in the same upload: only once Oracle shows it for pricing (an active
    Pricing Administrator access row and the unit active). Bounded; never a guess."""
    start = time.time()
    while True:
        try:
            ok = p.body["BusinessUnit"] in lists.pricing_units(fresh=True)
            b = next((x for x in lists.business_units(fresh=True) if x["BusinessUnitName"] == p.body["BusinessUnit"]), None)
        except RuntimeError as e:
            ok, b = False, None
            print(f"  NOTE  couldn't read the access list ({str(e)[:150]}); trying again")
        if ok and b and b.get("ActiveFlag") is not False:
            p.bu_id = b.get("BusinessUnitId")
            print(f"  OK    {p.body['BusinessUnit']} is available for pricing ({int(time.time() - start)} s)")
            return True, int(time.time() - start)
        if time.time() - start >= WAIT_BU:
            return False, int(time.time() - start)
        if progress:
            progress.step("waiting", 30, f"Waiting until Oracle shows {p.body['BusinessUnit']} for pricing")
        time.sleep(WAIT_EVERY)


def read_back(name):
    items = get_all(RESOURCE, q=f"PriceListName='{name}'", expand="accessSets")
    return [i for i in items if i.get("PriceListName") == name]


def make_one(p, lists, zone, progress=None):
    """One price list: wait (pending unit) -> header -> access sets -> approval -> read back. Returns a dict:
    {"state": created | completed | skipped | not_saved | incomplete | waiting, ...}."""
    out = {"saved": [], "missing": [], "reason": None}
    if p.status == "waiting":
        ok, waited = wait_for_unit(p, lists, progress)
        if not ok:
            out.update(state="not_saved", field="business_unit",
                       reason=f"Oracle doesn't show the business unit {p.body['BusinessUnit']} for pricing yet (waited "
                              f"{waited // 60} min {waited % 60} s), so the price list wasn't made.")
            return out
        out["waited"] = waited
    pid, it = None, None
    if p.status == "incomplete":
        it = p.existing
        pid = it["PriceListId"]
    else:
        again = read_back(p.name)                   # made meanwhile: never twice
        if again:
            out.update(state="skipped", reason="It appeared in Oracle before it was sent.")
            return out
        if progress:
            progress.step("creating", 45, f"Creating the price list {p.name}")
        created, err, code = call("POST", RESOURCE, p.body)
        if err:
            again = read_back(p.name)
            if not again:
                out.update(state="not_saved", reason=err, field=field_of(err))
                return out
            it = again[0]                           # Oracle made it despite the error
        else:
            it = created
        pid = it.get("PriceListId")
        out["saved"].append("header (in progress)")
    have = {a.get("AccessSetCode") for a in (it.get("accessSets") or [])} if p.status == "incomplete" else set()
    for c in p.set_codes:
        if c in have:
            continue
        if progress:
            progress.step("access", 60, f"Adding access set {c}")
        _, err, _ = call("POST", f"{RESOURCE}/{pid}/child/accessSets", {"AccessSetCode": c})
        if err:
            out["missing"].append(f"access set {c} ({err})")
        else:
            out["saved"].append(f"access set {c}")
    if not out["missing"]:
        if progress:
            progress.step("approving", 75, "Approving it")
        _, err, _ = call("PATCH", f"{RESOURCE}/{pid}", {"StatusCode": "APPROVED"})
        if err:
            out["missing"].append(f"the approval ({err})")
        else:
            out["saved"].append("approval")
    else:
        out["missing"].append("the approval (it needs every access set first)")
    # read back
    if progress:
        progress.step("verifying", 85, "Reading it back from Oracle")
    got = read_back(p.name)
    if not got:
        out.update(state="not_saved", reason="Oracle doesn't show it after saving.")
        return out
    g = got[0]
    out["item"] = g
    diffs = compare_header(p, g, zone)
    have = {a.get("AccessSetCode") for a in g.get("accessSets") or []}
    lost = [c for c in p.set_codes if c not in have]
    if g.get("StatusCode") != "APPROVED" and not any("approval" in m for m in out["missing"]):
        out["missing"].append(f"the approval (Oracle shows {g.get('StatusCode')})")
    for c in lost:
        if not any(c in m for m in out["missing"]):
            out["missing"].append(f"access set {c}")
    out["diffs"] = diffs
    if out["missing"] or diffs:
        out["state"] = "incomplete"
    else:
        out["state"] = "completed" if p.status == "incomplete" else "created"
    return out


def field_of(text):
    t = (text or "").lower()
    for f, words in (("description", ("description",)), ("line_type", ("line type", "linetype")),
                     ("currency", ("currencycode",)), ("name", ("name",)), ("business_unit", ("business unit", "businessunit")),
                     ("currency", ("currency",)), ("end_date", ("end date", "enddate")),
                     ("start_date", ("start date", "startdate")), ("type", ("type",)),
                     ("calculation_method", ("calculation",)), ("charge_definition", ("charge",))):
        if any(w in t for w in words):
            return f
    return None


# ---------------------------------------------------------------- results

def failed(code, text, saved, problems=None, message=None):
    return {"ok": False, "text": text, "error": {"code": code, "detail": {
        "message": message, "saved": saved, "registry_id": None, **({"problems": problems} if problems else {})}}}


def created_view(g, zone):
    return {"PriceListName": g.get("PriceListName"), "PriceListId": g.get("PriceListId"),
            "BusinessUnit": g.get("BusinessUnit"), "Type": g.get("PriceListTypeCode"), "Currency": g.get("CurrencyCode"),
            "Start Date (screen)": shown(g.get("StartDate"), zone), "End Date (screen)": shown(g.get("EndDate"), zone),
            "Charge Definition": g.get("PricingChargeDefinitionCode"), "Line Type": g.get("LineTypeCode"),
            "Calculation Method": g.get("CalculationMethodCode"), "Status": g.get("StatusCode"),
            "Access Sets": [a.get("AccessSetCode") for a in g.get("accessSets") or []]}


def result_of(p, o, zone):
    where = WHERE.format(name=p.name)
    if p.status == "problems":
        return failed("INVALID_REQUEST", " ".join(x["reason"] for x in p.problems) + " Nothing was sent for it.", "no",
                      problems=p.problems)
    if p.status == "exists":
        return {"ok": True, "skipped": True, "where": where, "text": plan_text(p, zone),
                "created": created_view(p.existing, zone)}
    o = o or {}
    st = o.get("state")
    if st == "skipped":
        return {"ok": True, "skipped": True, "where": where, "text": f"The price list {p.name} is already in Oracle "
                f"({o.get('reason')}), so nothing was changed."}
    if st == "not_saved":
        prob = {"price_list": p.name, "business_unit": p.body.get("BusinessUnit"), "field": o.get("field"),
                "key": o.get("field"), "value": p.req.get(o.get("field")) if o.get("field") else None,
                "reason": o["reason"], "text": o["reason"], "suggestions": suggest(o.get("field"), p),
                "fix": "Please correct it in the sheet."}
        return failed("INVALID_REQUEST", f"Oracle didn't save the price list {p.name}: {o['reason']} Nothing of it was "
                      "saved; a rerun sends only what is missing.", "no", problems=[prob], message=o["reason"])
    if st == "incomplete":
        saved = ", ".join(o["saved"]) or "the header (earlier)"
        missing = "; ".join(o["missing"] + o.get("diffs", []))
        return failed("FAILED", f"Saved but incomplete: the price list {p.name} is in Oracle ({saved}); missing or "
                      f"different: {missing}. A rerun completes only what is missing.", "yes", message=missing)
    g = o.get("item") or {}
    text = (f"{'Completed' if st == 'completed' else 'Created'} the price list {p.name} "
            f"({g.get('PriceListTypeCode')}, {g.get('CurrencyCode')}, business unit {g.get('BusinessUnit')}, from "
            f"{shown(g.get('StartDate'), zone)}" + (f" to {shown(g.get('EndDate'), zone)}" if g.get("EndDate") else "")
            + f", access sets {', '.join(p.set_codes)}) and approved it. Saved and verified in Oracle, every value as sent.")
    if o.get("waited") is not None:
        text += f" Its business unit was available for pricing after {o['waited']} s."
    return {"ok": True, "where": where, "text": text, "created": created_view(g, zone)}


def suggest(field, p):
    try:
        lst = Lists_cache.get() or Lists()
        if field == "business_unit":
            return close(p.req.get("business_unit") or "", lst.pricing_units())
        if field == "currency":
            return [c[0] for c in lst.currencies()][:12]
        if field == "type":
            return [c[1] for c in lst.types()]
        if field == "calculation_method":
            return [c[1] for c in lst.methods()]
        if field == "charge_definition":
            return [c[1] for c in lst.charge_defs()]
    except RuntimeError:
        pass
    return []


def read_requests(arg):
    raw = json.loads(Path(arg).read_text(encoding="utf-8") if arg.endswith(".json") and Path(arg).exists() else arg)
    if isinstance(raw, dict) and "price_lists" in raw:
        raw = raw["price_lists"]
    return raw if isinstance(raw, list) else [raw]


def found_notes(p):
    """Yellow notes per field for the sheet's preview."""
    out = {}
    twin = next((n for n in p.notes if "differs only in capitals" in n), None)
    if p.status == "exists":
        out["name"] = "Already exists in Oracle: it will be skipped and not changed."
    elif p.status == "incomplete":
        out["name"] = "Already in Oracle but not finished (in progress): only its missing access sets and the approval are done."
    elif twin:
        out["name"] = (twin + " Oracle treats price list names as case-sensitive, so it would make this one as a NEW "
                       "price list. Make sure that is what you want.")
    if p.status == "waiting":
        out["business_unit"] = ("Waits for this business unit, which the same upload creates first; the price list is "
                                "made once Oracle shows it for pricing.")
    return out


def oracle_values(p, zone):
    """What Oracle will get per field, in the screen's words (new or waiting price lists)."""
    if p.status not in ("new", "waiting"):
        return {}
    g = will_get(p, zone) or {}
    tz = f" ({TZ_SHORT(zone)})" if zone else ""
    return {"name": g.get("Name"), "description": g.get("Item Description"), "type": g.get("Type"),
            "currency": g.get("Currency"), "business_unit": g.get("Business Unit"),
            "start_date": (g.get("Start Date") or "") + tz, "end_date": (g.get("End Date") + tz) if g.get("End Date") not in (None, "(none)") else "(none)",
            "charge_definition": g.get("Pricing Charge Definition"), "line_type": g.get("Line Type"),
            "calculation_method": g.get("Calculation Method")}


def TZ_SHORT(zone):
    return "Oracle user's time, " + zone.split("/")[-1].replace("_", " ")


def plan_command(argv):
    out = sys.stdout
    try:
        reqs = read_requests(argv[1] if len(argv) > 1 else str(HERE / "pricelists.json"))
    except (ValueError, OSError) as e:
        print(json.dumps({"ok": False, "text": f"The request couldn't be read ({e})."}), file=out)
        return 2
    with contextlib.redirect_stdout(sys.stderr):
        oracle.check_environment()
        try:
            lists = Lists()
            Lists_cache.value = lists
            pls, zone, label = plan(reqs, lists)
        except (RuntimeError, SystemExit) as e:
            from common import browser
            print(json.dumps({"ok": False, "text": browser.failed_step_text(   # the real failed step (2026-10-26)
                "Oracle couldn't be checked just now."), "detail": str(e)[:500]}), file=out)
            return 1
    # For the upload sheet (page/server.py apply_oracle_check, 2026-10-26): "found" = yellow notes on a
    # field, "oracle" = what Oracle will get per field (dates as the screen shows them).
    results = [{"name": p.name, "ok": True, "status": p.status, "problems": p.problems, "notes": p.notes,
                "found": found_notes(p), "oracle": oracle_values(p, zone),
                "oracle_will_get": will_get(p, zone), "summary": plan_text(p, zone),
                "skipped": plan_text(p, zone) if p.status == "exists" else None,
                "waits_for_business_unit": p.status == "waiting"} for p in pls]
    print(json.dumps({"ok": True, "time_zone": label, "text": f"{sum(p.status in ('new', 'waiting', 'incomplete') for p in pls)} "
                      f"to make or finish, {sum(p.status == 'exists' for p in pls)} already in Oracle, "
                      f"{sum(p.status == 'problems' for p in pls)} with problems (nothing was changed in Oracle).",
                      "results": results}, ensure_ascii=False), file=out)
    return 0


def run_batch_command(argv, progress=None):
    out = sys.stdout
    progress = progress or page.Progress(out)
    try:
        reqs = read_requests(argv[1] if len(argv) > 1 else "")
    except (ValueError, OSError) as e:
        print(json.dumps({"step": "result", "percent": 100, "ok": False, "text": "The request could not be read.",
                          "error": {"code": "INVALID_REQUEST", "step": "reading", "detail": str(e)}}), file=out)
        return 2
    results, top_error, t0 = [], None, time.time()
    with contextlib.redirect_stdout(sys.stderr):
        oracle.check_environment()
        try:
            progress.step("checking", 15, "Checking every price list with Oracle")
            lists = Lists()
            Lists_cache.value = lists
            pls, zone, label = plan(reqs, lists)
            print(f"time zone of the Oracle user: {label}")
            for p in pls:
                print(f"  {p.name}: {plan_text(p, zone)}")
            for k, p in enumerate(pls):
                o = None
                if p.status in ("new", "waiting", "incomplete"):
                    progress.step("creating", 20 + int(70 * k / max(1, len(pls))), f"Price list {k + 1} of {len(pls)}: {p.name}")
                    try:
                        o = make_one(p, lists, zone, progress)
                    except Exception as e:  # noqa: BLE001 - one price list's crash: said plainly, the others go on
                        got = read_back(p.name) if p.name else []
                        o = {"state": "incomplete" if got else "not_saved", "saved": ["header"] if got else [],
                             "missing": [f"the rest ({type(e).__name__}: {str(e)[:200]})"], "reason": f"{type(e).__name__}: {e}"}
                    print(f"  {p.name}: {o.get('state')} {o.get('saved')} missing {o.get('missing')} {o.get('reason') or ''}")
                results.append(result_of(p, o, zone))
        except Exception as e:  # noqa: BLE001 - before anything was sent
            top_error = {"code": page._classify(str(e)), "step": "checking", "detail": str(e)[:1500]}
            results = [failed(top_error["code"], "Oracle couldn't be checked just now; nothing was sent.", "no",
                              message=str(e)[:500]) for _ in reqs]
        progress.step("done")
    made = [r for r in results if r["ok"] and not r.get("skipped")]
    skipped = [r for r in results if r.get("skipped")]
    bad = [r for r in results if not r["ok"]]
    saved_bad = [reqs[i].get("name") for i, r in enumerate(results) if not r["ok"] and r["error"]["detail"]["saved"] == "yes"]
    text = (f"Done {len(made)} of {len(results)} price lists" + (f", {len(skipped)} already there" if skipped else "")
            + (f", {len(bad)} not done" if bad else "") + ".")
    if bad and (made or saved_bad):
        text += " Saved in Oracle: " + ", ".join([r["created"]["PriceListName"] for r in made if r.get("created")] + saved_bad) + "."
    print(f"Whole run: {int(time.time() - t0)} s", file=sys.stderr)
    line = {"step": "result", "percent": 100, "ok": not bad, "text": page.plain_check(text, "result"), "results": results}
    if top_error:
        line["error"] = top_error
    print(json.dumps(line, ensure_ascii=False, default=str), file=out)
    return 0 if not bad else 1
