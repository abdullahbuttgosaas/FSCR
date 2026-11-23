"""Create and approve price lists from pricelists.json via the priceLists REST resource.

Per price list: resolve names (business unit, currency, access sets) with
read-only lookups -> skip if a price list with that name already exists ->
POST priceLists -> POST each access set -> PATCH StatusCode=APPROVED ->
re-read and verify. DONE only when header, access set(s), APPROVED status and
the re-read check all hold.

Plain dates (YYYY-MM-DD) are sent as midnight in this computer's local time
zone; the offset used is printed.

Temporary files (request/response log) go in "Price Lists/_work/", deleted after
a verified success and kept after any failure.

  python "Price Lists/run.py" --check   # validate + resolve names + existence, no changes
  python "Price Lists/run.py"           # full run

Page interface (root CLAUDE.md > Page interface, common/page.py), one price list per run:
  python "Price Lists/run.py" --spec
  python "Price Lists/run.py" --options business_unit | currency | access_sets.name
  python "Price Lists/run.py" --options business_unit --all   # full live list, not the samples
  python "Price Lists/run.py" --run '{"name": "X", "business_unit": "ABD", ...}'
"""
import argparse
import json
import os
import re
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

sys.dont_write_bytecode = True  # keep the project free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import oracle, page  # noqa: E402

RESOURCE = "priceLists"
# Optional fields whose name -> code translation is not proven yet.
NOT_YET_SUPPORTED = ("type", "line_type", "calculation_method")


# ---------------------------------------------------------------- requirements

def _text(obj, key, where, required=False, maxlen=None):
    val = obj.get(key)
    if val in (None, ""):
        if required:
            oracle.fail(f"{where}: '{key}' is required")
        return ""
    if not isinstance(val, str) or val != val.strip():
        oracle.fail(f"{where}: '{key}' must be text without leading/trailing spaces")
    if "'" in val:
        oracle.fail(f"{where}: '{key}' must not contain a single quote (used in REST queries)")
    if maxlen and len(val) > maxlen:
        oracle.fail(f"{where}: '{key}' is longer than {maxlen} characters")
    return val


def _date(obj, key, where, required=False):
    val = obj.get(key)
    if val in (None, ""):
        if required:
            oracle.fail(f"{where}: '{key}' is required")
        return None
    try:
        return date.fromisoformat(val)
    except (TypeError, ValueError):
        oracle.fail(f"{where}: '{key}' must be a date as YYYY-MM-DD, got {val!r}")


def load_requirements(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        oracle.fail(f"Cannot read {path}: {e}")
    return parse_requirements(data, path)


def parse_requirements(data, path):
    """The request (file contents or a page request) -> normalised price lists."""
    raw = data.get("price_lists")
    if not isinstance(raw, list) or not raw:
        oracle.fail(f"{path} must contain a non-empty 'price_lists' list")
    out, seen = [], set()
    for pl in raw:
        name = _text(pl, "name", "price list", required=True)
        where = f"price list {name}"
        if name in seen:
            oracle.fail(f"{where}: listed twice in {path}")
        seen.add(name)
        for key in NOT_YET_SUPPORTED:
            if pl.get(key):
                oracle.fail(f"{where}: setting '{key}' is not supported yet (only the UI "
                            "default is proven). Leave it out or ask to extend the folder.")
        access = pl.get("access_sets") or []
        if not isinstance(access, list) or not access:
            oracle.fail(f"{where}: at least one access set is required")
        start = _date(pl, "start_date", where, required=True)
        end = _date(pl, "end_date", where)
        if end and end < start:
            oracle.fail(f"{where}: end_date is before start_date")
        out.append({
            "name": name,
            "business_unit": _text(pl, "business_unit", where, required=True),
            "currency": _text(pl, "currency", where, required=True),
            "start_date": start,
            "end_date": end,
            "description": _text(pl, "description", where),
            "access_sets": [_text({"a": a}, "a", f"{where} access set", required=True) for a in access],
        })
    return out


# ---------------------------------------------------------------- name lookups

def resolve_business_unit(name):
    # KeywordFinder is a fuzzy search; keep only exact (case-insensitive) active matches.
    # (A plain q= filter on finBusinessUnitsLOV timed out after 300s.)
    items = oracle.rest_items("finBusinessUnitsLOV", finder=f"KeywordFinder;SearchTerm={name}")
    hits = [i for i in items if i.get("BusinessUnitName", "").lower() == name.lower()
            and i.get("ActiveFlag") is not False]
    if len(hits) != 1:
        found = sorted({i.get("BusinessUnitName") for i in items})
        oracle.fail(f"Business unit {name!r}: {len(hits)} exact active match(es); "
                    f"similar names found: {found[:10]}. Ask the user which business unit.")
    return hits[0]["BusinessUnitName"], hits[0]["BusinessUnitId"]


def resolve_currency(text):
    # Codes first (Oracle allows user-defined codes like "1214", not only 3 letters),
    # then the name.
    items = []
    if text.isalnum():
        items = oracle.rest_items("currenciesLOV",
                                  finder=f"CurrencyCodeAllRowsFinder;CurrencyCode={text.upper()}")
        items = [i for i in items if i.get("EnabledFlag") == "Y"]
    if not items:
        items = oracle.rest_items("currenciesLOV", q=f"Name='{text}'")
        items = [i for i in items if i.get("EnabledFlag") == "Y"]
    if len(items) != 1:
        oracle.fail(f"Currency {text!r}: {len(items)} enabled match(es). Ask the user.")
    return items[0]["CurrencyCode"], items[0]["Name"]


def resolve_access_set(text):
    items = oracle.rest_items("setIdSetsLOV", finder=f"SetCodeFinder;SetCode={text.upper()}")
    if not items:
        items = oracle.rest_items("setIdSetsLOV", q=f"SetName='{text}'")
    if len(items) != 1:
        oracle.fail(f"Access set {text!r}: {len(items)} match(es) by code or name. Ask the user.")
    return items[0]["SetCode"], items[0]["SetName"]


def find_price_list(name):
    return oracle.rest_items(RESOURCE, q=f"PriceListName='{name}'", expand="accessSets")


# ---------------------------------------------------------------- dates

def local_midnight(d):
    """Plain date -> ISO datetime at 00:00 in this computer's time zone."""
    return datetime(d.year, d.month, d.day).astimezone().isoformat()


def same_instant(a, b):
    return datetime.fromisoformat(a) == datetime.fromisoformat(b)


# ---------------------------------------------------------------- main steps

def plan(pl):
    """Resolve every name; return the request bodies (no changes in Oracle)."""
    bu_name, bu_id = resolve_business_unit(pl["business_unit"])
    cur_code, cur_name = resolve_currency(pl["currency"])
    sets = [resolve_access_set(a) for a in pl["access_sets"]]
    body = {"PriceListName": pl["name"], "BusinessUnit": bu_name,
            "CurrencyCode": cur_code, "StartDate": local_midnight(pl["start_date"])}
    if pl["description"]:
        body["PriceListDescription"] = pl["description"]
    if pl["end_date"]:
        body["EndDate"] = local_midnight(pl["end_date"])
    print(f"  {pl['name']}: business unit {bu_name} (id {bu_id}), currency {cur_code} "
          f"({cur_name}), start {body['StartDate']}"
          + (f", end {body['EndDate']}" if "EndDate" in body else "")
          + f", access sets {[c for c, _ in sets]}")
    return {"body": body, "bu_id": bu_id, "set_codes": [c for c, _ in sets]}


def verify(pl, p, found=None):
    """found (optional dict): filled with {name: the price list as re-read}."""
    items = find_price_list(pl["name"])
    if len(items) != 1:
        print(f"  FAIL  {pl['name']}: found {len(items)} price lists with this name")
        return False
    it, body, ok = items[0], p["body"], True
    if found is not None:
        found[pl["name"]] = it
    checks = [("StatusCode", it.get("StatusCode") == "APPROVED", "APPROVED"),
              ("BusinessUnitId", it.get("BusinessUnitId") == p["bu_id"], p["bu_id"]),
              ("CurrencyCode", it.get("CurrencyCode") == body["CurrencyCode"], body["CurrencyCode"]),
              ("StartDate", same_instant(it.get("StartDate"), body["StartDate"]), body["StartDate"])]
    if "EndDate" in body:
        checks.append(("EndDate", bool(it.get("EndDate")) and same_instant(it["EndDate"], body["EndDate"]),
                       body["EndDate"]))
    if "PriceListDescription" in body:
        checks.append(("PriceListDescription",
                       it.get("PriceListDescription") == body["PriceListDescription"],
                       body["PriceListDescription"]))
    for field, good, want in checks:
        print(f"  {'OK  ' if good else 'FAIL'}  {field} = {it.get(field)!r}" + ("" if good else f" (expected {want!r})"))
        ok &= good
    have = {a.get("AccessSetCode") for a in it.get("accessSets", [])}
    for code in p["set_codes"]:
        good = code in have
        print(f"  {'OK  ' if good else 'FAIL'}  access set {code}")
        ok &= good
    return ok


# ---------------------------------------------------------------- page interface

HERE = Path(__file__).resolve().parent
TODAY = "today"   # page word: Oracle's today (REST Date header) minus one day
SPEC = {
    "title": "Create a price list",
    "description": "Creates a price list, gives it access and approves it; existing ones are never changed.",
    "fields": [
        {"key": "name", "label": "Price list name", "required": True, "type": "text",
         "placeholder": "Retail USD 2027", "default": None, "help": "No single quotes (')."},
        {"key": "business_unit", "label": "Business unit", "required": True, "type": "pick",
         "placeholder": "ABD", "default": None, "list": "samples",
         "help": "Pick one that is known to work, or type another; it is checked with Oracle."},
        {"key": "currency", "label": "Currency", "required": True, "type": "pick",
         "placeholder": "USD", "default": None, "list": "samples",
         "help": "Pick one that is known to work, or type a code (USD) or name; it is checked with Oracle."},
        {"key": "start_date", "label": "Start date", "required": True, "type": "date",
         "placeholder": "2026-10-21", "default": None,
         "help": "'today' means Oracle's today minus one day."},
        {"key": "access_sets", "label": "Access sets", "required": True, "type": "rows",
         "min_rows": 1, "add_label": "Add an access set", "row_label": "Access set",
         "fields": [{"key": "name", "label": "Access set", "required": True, "type": "pick",
                     "placeholder": "001 Customer Site", "list": "samples"}]},
        {"key": "description", "label": "Description", "required": False, "type": "text",
         "placeholder": "Prices for retail customers", "default": None},
        {"key": "end_date", "label": "End date", "required": False, "type": "date",
         "placeholder": "2027-12-31", "default": None},
        # 2026-10-26: the rest of the Create Price List screen (pl_batch.py)
        {"key": "type", "label": "Type", "required": False, "type": "pick",
         "placeholder": "Segment price list", "default": "Segment price list"},
        {"key": "charge_definition", "label": "Pricing charge definition", "required": False, "type": "pick",
         "placeholder": "Sale Price", "default": None},
        {"key": "line_type", "label": "Line type", "required": False, "type": "pick",
         "placeholder": "Buy", "default": "Buy"},
        {"key": "calculation_method", "label": "Calculation method", "required": False, "type": "pick",
         "placeholder": "Price", "default": "Price"},
    ],
}
WHERE = "Order Management > Pricing Administration > Manage Price Lists, search for {name}"


def all_items(path, **params):
    """Every item of a REST list (200 per page)."""
    out, offset = [], 0
    while True:
        data = oracle.rest("GET", path, params={"onlyData": "true", "limit": 200,
                                                "offset": offset, **params})
        out += data.get("items", [])
        if not data.get("hasMore"):
            return out
        offset += len(data.get("items", []))


# Drop-down samples: only verified values - used by a real create in this project
# (ZZ_POC_PRICELIST3, ZZ_TEST_4832, ZZ_TEST_1567, ZZ_TEST_6183: ABD / USD / 001 CUSTOMER
# SITE) or by the user's own test (US1, ABC Procurement BU, PKR, AFN, ENTERPRISE, SET0001;
# 2026-10-21). See CLAUDE.md > Page interface. Values in Oracle's exact spelling (codes;
# the drop-down shows Oracle's names); each is confirmed live when the list is read.
# `--options FIELD --all` gives the full live list instead; a --run always checks a typed
# value against the full live list.
SAMPLES = {"business_unit": ["ABD", "US1", "ABC Procurement BU"],
           "currency": ["USD", "PKR", "AFN"],
           "access_sets.name": ["001 CUSTOMER SITE", "ENTERPRISE", "SET0001"]}


def options_for(key):
    """The page's drop-down: the samples above, each confirmed live (a sample Oracle no
    longer has is left out, with a NOTE). With --all, or during --run (the check of what
    was typed in), the full live list."""
    full = live_options(key)
    dropdown = sys.argv[1:2] == ["--options"] and "--all" not in sys.argv
    if key not in SAMPLES or not dropdown:
        return full
    by_value = {o["value"]: o for o in full}
    wanted = list(SAMPLES[key])
    if key == "business_unit":
        # plus every business unit the Business Units folder created (read from the shared
        # file each time the list loads; nothing is imported from that folder)
        wanted += [e["name"] for e in registry_load().get("business_units", [])
                   if e.get("name") and e["name"] not in wanted]
    keep = [by_value[v] for v in wanted if v in by_value]
    for v in wanted:
        if v not in by_value:
            print(f"  NOTE  {key} {v!r} is not in Oracle's list; left out", file=sys.stderr)
    return keep


def live_options(key):
    """Live lists through REST: business units (finBusinessUnitsLOV, active ones),
    currencies (currenciesLOV, enabled ones) and access sets (setIdSetsLOV)."""
    oracle.check_environment()
    import pl_batch
    if key == "business_unit":
        # 2026-10-26: only business units the user has Pricing Administrator access on (the Create Price
        # List screen's list), and active
        lst = pl_batch.Lists()
        active = {b["BusinessUnitName"] for b in lst.business_units() if b.get("ActiveFlag") is not False}
        names = sorted((n for n in lst.pricing_units() if n in active), key=str.lower)
        return [{"value": n, "label": n} for n in names]
    lists_of = {"type": "types", "line_type": "line_types", "calculation_method": "methods",
                "charge_definition": "charge_defs"}
    if key in lists_of:
        return [{"value": c[1], "label": c[1]} for c in getattr(pl_batch.Lists(), lists_of[key])()]
    if key == "currency":
        items = all_items("currenciesLOV", q="EnabledFlag='Y'")
        return [{"value": i["CurrencyCode"], "label": (i.get("Name") or i["CurrencyCode"]).strip()}
                for i in sorted(items, key=lambda i: i["CurrencyCode"])]
    if key == "access_sets.name":
        return [{"value": i["SetCode"], "label": i.get("SetName") or i["SetCode"]}
                for i in sorted(all_items("setIdSetsLOV"), key=lambda i: i["SetCode"])]
    raise page.PageError("FAILED", detail=f"no list for {key!r}")


def _plain_checks(request):
    problems = []
    for key, label in (("name", "Price list name"), ("description", "Description")):
        if "'" in (request.get(key) or ""):
            problems.append({"field": key, "problem": "quote",
                             "text": f"{label} can't contain a single quote (')."})
    s, e = request.get("start_date"), request.get("end_date")
    if s and e and TODAY not in (s.lower(), e.lower()) and e < s:
        problems.append({"field": "end_date", "problem": "before_start",
                         "text": "End date is before the start date."})
    codes = [a["name"] for a in request.get("access_sets", [])]
    for i, c in enumerate(codes, 1):
        if c in codes[:i - 1]:
            problems.append({"field": "access_sets.name", "problem": "twice", "row": i,
                             "text": f"Access set {i}: it is already listed above."})
    if problems:
        raise page.PageError("INVALID_REQUEST", " ".join(p["text"] for p in problems), problems)


def run_request(request, progress):
    """--run: one price list through pl_batch (2026-10-26): every check, then header, access sets,
    approval and the read-back; dates as 12:00 AM in the Oracle user's time zone."""
    import pl_batch
    oracle.check_environment()
    req = {k: v for k, v in request.items() if v not in (None, "")}
    progress.step("checking", 20)
    lists = pl_batch.Lists()
    pl_batch.Lists_cache.value = lists
    pls, zone, label = pl_batch.plan([req], lists)
    p = pls[0]
    if p.status == "problems":
        raise page.PageError("INVALID_REQUEST", " ".join(x["reason"] for x in p.problems),
                             [{"field": x["field"] if x["field"] != "access_sets" else "access_sets.name",
                               "problem": "not_valid", "text": x["reason"], "valid": x["suggestions"]}
                              for x in p.problems])
    o = None
    if p.status in ("new", "waiting", "incomplete"):
        o = pl_batch.make_one(p, lists, zone, progress)
    res = pl_batch.result_of(p, o, zone)
    progress.step("done")
    if not res["ok"]:
        err = res["error"]
        raise page.PageError(err["code"], res["text"], err["detail"])
    if o and o.get("state") in ("created", "completed"):
        confirm_pricing(p.body["BusinessUnit"])
    return res


def main():
    if sys.argv[1:2] in (["--plan"], ["--run-batch"], ["--time-zone"]):   # 2026-10-26, pl_batch.py
        import pl_batch
        if sys.argv[1] == "--time-zone":
            oracle.check_environment()
            zone, label = pl_batch.user_zone(refresh=True)
            print(f"Oracle user's time zone: {label} -> {zone}" if zone else f"Not read: {label}")
            sys.exit(0 if zone else 1)
        sys.exit((pl_batch.plan_command if sys.argv[1] == "--plan" else pl_batch.run_batch_command)(sys.argv[1:]))
    page.main(SPEC, options_for, run_request)   # --spec / --options / --run; else returns
    here = HERE
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(here / "pricelists.json"), help="requirements JSON")
    ap.add_argument("--check", action="store_true",
                    help="validate, resolve names and check existence; change nothing")
    args = ap.parse_args()

    oracle.check_environment()
    import pl_batch                          # 2026-10-26: the same engine as --run-batch
    sys.exit((pl_batch.plan_command if args.check else pl_batch.run_batch_command)(["--file", args.file]))


# ---------------------------------------------------------------- new business units (2026-10-21)
# Oracle caches a user's data access: a business unit that the Business Units folder just
# created may not be usable for pricing until the user signs out and in again. That folder
# lists what it created in common/created_business_units.json ("pending" when Oracle still
# needed a fresh sign-in). A business unit there that no price list has used yet
# (pricing_confirmed false) gets a short wait and retries when Oracle refuses it; then the
# run says a fresh sign-in is needed. The first price list made with it confirms it.

REGISTRY = oracle.PROJECT_ROOT / "common" / "created_business_units.json"
FRESH_SIGNIN_TEXT = "Oracle needs a fresh sign-in before this business unit shows for pricing."
RETRIES, RETRY_WAIT = 3, 40            # attempts after the first refusal, seconds between them


class FreshSignInNeeded(Exception):
    """Oracle refused a newly created business unit: the user must sign in again."""


def registry_load():
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"business_units": []}


def new_business_unit(name):
    """The shared file's entry for a business unit no price list has used yet, else None."""
    for e in registry_load().get("business_units", []):
        if e.get("name", "").lower() == name.lower() and not e.get("pricing_confirmed"):
            return e
    return None


def confirm_pricing(name):
    """A price list was made with this business unit: mark it confirmed in the shared file."""
    data = registry_load()
    for e in data.get("business_units", []):
        if e.get("name", "").lower() == name.lower() and not e.get("pricing_confirmed"):
            e.update(pricing_confirmed=True, status="ready", note="")
            tmp = REGISTRY.with_name(REGISTRY.name + ".tmp")      # atomic, like Business Units
            tmp.write_text(json.dumps(data, indent=1), encoding="utf-8")
            os.replace(tmp, REGISTRY)
            print(f"  OK    {name}: first price list made with it, marked ready in {REGISTRY.name}")


def create_header(pl, p, progress=None):
    """POST the price list header. For a new business unit from the shared file, a refusal
    that names the business unit is retried after a short wait; still refused -> a fresh
    sign-in is needed (FreshSignInNeeded). Any other business unit: the call as before."""
    bu = p["body"]["BusinessUnit"]
    entry = new_business_unit(bu)
    if entry is None:
        return oracle.rest("POST", RESOURCE, json=p["body"])
    print(f"  NOTE  {bu} is a new business unit ({entry.get('status')}); a refusal is retried")
    for attempt in range(RETRIES + 1):
        r, err = oracle.try_call("POST", f"{oracle.API_BASE}/{RESOURCE}", json=p["body"], timeout=120)
        if not err:
            return r.json() if r.content else {}
        if not re.search(r"business\s*unit|BusinessUnit", err, re.I):
            oracle.fail(err)                  # not about the business unit: stop as before
        print(f"  ...   Oracle refused {bu} (try {attempt + 1} of {RETRIES + 1}): {err.splitlines()[-1][:200]}")
        if find_price_list(pl["name"]):
            oracle.fail(f"{pl['name']} exists although Oracle answered with an error; not retried.")
        if attempt < RETRIES:
            if progress:
                progress.step("creating", 50, "Oracle hasn't caught up with the new business unit yet; "
                                              "trying again in a moment")
            time.sleep(RETRY_WAIT)
    raise FreshSignInNeeded(f"{FRESH_SIGNIN_TEXT} Sign out of Oracle and sign in again, then "
                            f"create the price list for {bu} again. Nothing was created.")


def run_lists(lists, here, check=False, progress=None, found=None):
    """Skip existing, plan, create, add access sets, approve, verify. Returns the names
    created. progress: the page's progress lines (--run); found: see verify()."""
    work = oracle.init_work_dir(here)
    log = []

    def save_log():
        (work / "steps.json").write_text(json.dumps(log, indent=1, default=str), encoding="utf-8")

    todo = []
    for pl in lists:
        existing = find_price_list(pl["name"])
        if existing:
            e = existing[0]
            print(f"  SKIP  {pl['name']}: already exists (status {e.get('StatusCode')}, "
                  f"{len(e.get('accessSets', []))} access set(s)) - not touched")
            continue
        todo.append((pl, plan(pl)))
    if not todo or check:
        print("Nothing to create." if not todo else "Check only: nothing changed in Oracle.")
        oracle.cleanup_work_dir()
        return []

    all_ok = True
    for pl, p in todo:
        name = pl["name"]
        if progress:
            progress.step("creating")
        print(f"Creating {name} ...")
        created = create_header(pl, p, progress)
        log.append({"step": "create", "name": name, "request": p["body"], "response": created})
        save_log()
        pid = created.get("PriceListId")
        if not pid:
            oracle.fail(f"No PriceListId in create response for {name}: {created}")
        print(f"  PriceListId={pid}, status {created.get('StatusCode')}")
        for code in p["set_codes"]:
            r = oracle.rest("POST", f"{RESOURCE}/{pid}/child/accessSets", json={"AccessSetCode": code})
            log.append({"step": "access_set", "name": name, "code": code, "response": r})
            save_log()
            print(f"  access set {code} added")
        if progress:
            progress.step("approving", 70, "Approving it")
        r = oracle.rest("PATCH", f"{RESOURCE}/{pid}", json={"StatusCode": "APPROVED"})
        log.append({"step": "approve", "name": name, "response": r})
        save_log()
        print(f"  approve requested, status {r.get('StatusCode')}")
        if progress:
            progress.step("verifying")
        print(f"Verifying {name} ...")
        if not verify(pl, p, found):
            all_ok = False
        else:
            confirm_pricing(p["body"]["BusinessUnit"])
    if not all_ok:
        oracle.fail("Verification failed (MISMATCH) - see FAIL lines above. "
                    "Created price lists are left as they are (never deleted).")
    print("All requested price lists created, approved and verified.")
    oracle.cleanup_work_dir()
    return [pl["name"] for pl, _ in todo]


if __name__ == "__main__":
    main()
