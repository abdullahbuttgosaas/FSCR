"""Create standard lookups from lookups.json, then verify every value in Oracle.

Everything Manage Standard Lookups can create (2026-10-25):
- a NEW lookup type with its codes: one CSV import for all new types of a run (rows built from
  the export's column headers; Lookup Configuration Level User, as the screen makes it);
- new codes on an EXISTING User or Extensible type: REST, one POST per code to the type's
  lookupCodes link (as the Order Types folder does); existing codes are skipped, never changed;
  a System type takes no new codes (refused before anything is sent).
Modules are given by NAME: each name is looked up in the screen's Module dialog (it shows at most
500 rows, so names are searched one by one) and its internal ID is learned from a lookup that
already uses the module (screen search by Module, then REST); both are cached in modules.json.
After the import and the POSTs every type and code is read back through REST and compared:
"Saved: ... / Not saved: X (Oracle's reason)". A rerun skips what is saved.

  python "Lookup types/run.py"                  # full run
  python "Lookup types/run.py" --plan [FILE or JSON]   # read-only: rules, Oracle's state, modules
  python "Lookup types/run.py" --modules ["Name" ...]  # look modules up by name (cached), show the cache
  python "Lookup types/run.py" --check          # read-only: task flags + existence, no export
  python "Lookup types/run.py" --dry-run        # export + build import zip, no import
  python "Lookup types/run.py" --list-modules   # ModuleIds seen in the export, with examples
  python "Lookup types/run.py" --module-of XX_TYPE   # ModuleId of one existing lookup
  python "Lookup types/run.py" --dry-run --from-export <zip>   # offline build check

Page interface (root CLAUDE.md > Page interface, common/page.py), one lookup type per run:
  python "Lookup types/run.py" --spec
  python "Lookup types/run.py" --options module | rest_access_secured
  python "Lookup types/run.py" --run '{"lookup_type": "X", "module": "Order Management", ...}'
"""
import argparse
import base64
import collections
import difflib
import io
import json
import re
import sys
import time
import zipfile
from datetime import date, timedelta
from pathlib import Path

sys.dont_write_bytecode = True  # keep the project free of __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import oracle, page  # noqa: E402

TASK = "FND_MANAGE_STANDARD_LOOKUPS"
TYPE_CSV = "FND_APP_STANDARD_LOOKUP.csv"
CODE_CSV = "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv"
METADATA = "ASM_SETUP_CSV_METADATA.xml"
CODE_TYPE_COL = "FND_APP_STANDARD_LOOKUP.LookupType"
HERE = Path(__file__).resolve().parent
MODULE_CACHE = HERE / "modules.json"

# Values the screen sets itself when a lookup type is created (Lookup Configuration Level is
# shown as "User" and can't be changed; REST Access Secured defaults to Secure, seen on the
# screen 2026-10-25). Who/date columns are left empty: Oracle assigns them on import.
UI_TYPE_DEFAULTS = {"CustomizationLevel": "U", "RestAccessSecured": "SECURE"}
UI_CODE_DEFAULTS = {"EnabledFlag": "Y"}
ACCESS = {"SECURE": "Secure", "AUTH": "Authenticated", "ANON": "Anonymous"}   # code -> screen label
LEVELS = {"U": "User", "E": "Extensible", "S": "System"}
MAX = {"LookupType": 30, "Meaning": 80, "Description": 240, "LookupCode": 30, "Tag": 150}
MODULE_ID_RE = re.compile(r"^[0-9A-F]{32}$")
TODAY = "today"   # request word: Oracle's today (REST Date header) minus one day
CODE_FIELDS = ("LookupCode", "Meaning", "Description", "EnabledFlag", "StartDateActive", "EndDateActive",
               "DisplaySequence", "Tag")


# ---------------------------------------------------------------- rules (no Oracle)

class Rules:
    """Every problem of a request in plain words, all at once: {"key", "row", "text", "fix"}."""

    def __init__(self):
        self.problems = []

    def bad(self, key, text, row=None, fix="Change it in the request and check again."):
        self.problems.append({"key": key, "row": row, "text": text, "fix": fix})

    def text(self, v, key, label, maxlen, required=False, row=None):
        if v in (None, ""):
            if required:
                self.bad(key, f"{label} is required.", row)
            return ""
        if not isinstance(v, str):
            self.bad(key, f"{label} must be text.", row)
            return None
        if v != v.strip():
            self.bad(key, f"{label} '{v}' starts or ends with a space; remove it.", row)
            return None
        if len(v) > maxlen:
            self.bad(key, f"{label} can be at most {maxlen} characters; it has {len(v)}.", row)
            return None
        return v

    def day(self, v, key, label, row=None):
        """YYYY-MM-DD -> export format YYYY/MM/DD; "today" kept; "" empty; None wrong."""
        if v in (None, ""):
            return ""
        if str(v).strip().lower() == TODAY:
            return TODAY
        try:
            return date.fromisoformat(str(v).strip()).strftime("%Y/%m/%d")
        except ValueError:
            self.bad(key, f"{label} must be a date written as YYYY-MM-DD; it says '{v}'.", row)
            return None


def type_name_problems(name, rules):
    """The lookup type name rules, proven by real imports on 2026-10-25 (CLAUDE.md > Field rules):
    small letters and a name starting with ORA are refused by Oracle (JBO-25017, the whole type is
    dropped); spaces, "-" and "." are accepted (ZZ_TEST_LK_8806 SPACE, ZZ_TEST_LK_8806-DASH.DOT)."""
    if not name:
        return
    if name != name.upper():
        rules.bad("lookup_type", f"Lookup Type '{name}' has small letters; Oracle refuses them in a lookup type "
                  f"name. Write it in capitals, for example {name.upper()}.")
    if name.upper().startswith("ORA"):
        rules.bad("lookup_type", f"Lookup Type '{name}' starts with ORA; Oracle keeps names starting with ORA "
                  "for its own lookups and refuses it. Choose another name.")


def as_lookup(lk):
    """A page request (codes as rows) and a request file lookup have the same shape; the access
    value may be the code (SECURE, AUTH, ANON) or the screen's label (Secure, Authenticated,
    Anonymous)."""
    return dict(lk) if isinstance(lk, dict) else {}


def check_lookup(lk, rules):
    """Every rule that needs no Oracle for one lookup type and its codes. Returns the lookup in
    export column names (codes as a list), or None when it has problems."""
    start_n = len(rules.problems)
    known = {"lookup_type", "meaning", "description", "module", "module_id", "rest_access_secured", "codes",
             "existing_only"}
    for k in set(lk) - known:
        rules.bad(k, f"'{k}' is not a lookup type field.")
    t = rules.text(lk.get("lookup_type"), "lookup_type", "Lookup Type", MAX["LookupType"], required=True)
    # the name rules (small letters, ORA) apply to a NEW type only: checked in plan()
    access = str(lk.get("rest_access_secured") or "").strip()
    code = next((c for c, label in ACCESS.items() if access.upper() == c or access.lower() == label.lower()), None)
    if access and not code:
        rules.bad("rest_access_secured", f"REST Access Secured '{access}' isn't one of Oracle's values: "
                  "Secure, Authenticated, Anonymous.")
    module_id = str(lk.get("module_id") or "").strip().upper()
    if module_id and not MODULE_ID_RE.match(module_id):
        rules.bad("module_id", f"module_id must be Oracle's 32-character module number; it says '{module_id}'.")
    item = {"LookupType": t,
            "Meaning": rules.text(lk.get("meaning"), "meaning", "Meaning", MAX["Meaning"]),
            "Description": rules.text(lk.get("description"), "description", "Item Description", MAX["Description"]),
            "module": str(lk.get("module") or "").strip(), "ModuleId": module_id,
            "RestAccessSecured": code or "", "codes": [],
            "existing_only": bool(lk.get("existing_only"))}   # only add codes to a type Oracle has (the sheet)
    codes = lk.get("codes") or []
    if not isinstance(codes, list):
        rules.bad("codes", "codes must be a list of code rows.")
        codes = []
    seen, meanings = {}, {}
    for i, c in enumerate(codes, 1):
        if not isinstance(c, dict):
            rules.bad("codes", f"Code {i} must be a row of values.", i)
            continue
        w = f"Code {i}: "
        for k in set(c) - {"code", "meaning", "description", "enabled", "start_date", "end_date",
                           "display_sequence", "tag"}:
            rules.bad("codes", f"{w}'{k}' is not a lookup code field.", i)
        cd = rules.text(c.get("code"), "codes", w + "Lookup Code", MAX["LookupCode"], required=True, row=i)
        mn = rules.text(c.get("meaning"), "codes", w + "Meaning", MAX["Meaning"], required=True, row=i)
        if cd and cd in seen:
            rules.bad("codes", f"{w}Lookup Code '{cd}' is already listed as code {seen[cd]}.", i)
        if cd:
            seen.setdefault(cd, i)
        if mn and mn in meanings:      # capitals count, as Oracle's FND-7103 check
            rules.bad("codes", f"{w}Meaning '{mn}' is already used by code {meanings[mn]} of this type "
                      "(each code meaning once per type, Oracle FND-7103).", i)
        if mn:
            meanings.setdefault(mn, i)
        enabled = c.get("enabled")
        if isinstance(enabled, str) and enabled.strip().lower() in ("yes", "y", "true", "no", "n", "false"):
            enabled = enabled.strip().lower() in ("yes", "y", "true")
        if enabled not in (None, True, False):
            rules.bad("codes", f"{w}Enabled must be yes or no; it says '{enabled}'.", i)
            enabled = None
        seq = c.get("display_sequence")
        if seq not in (None, ""):
            try:
                n = float(seq)
                if isinstance(seq, bool) or not n.is_integer() or n < 0:
                    raise ValueError
                seq = str(int(n))
            except (TypeError, ValueError):
                rules.bad("codes", f"{w}Display Sequence must be a whole number, 0 or more; it says '{seq}'.", i)
                seq = None
        else:
            seq = ""
        start = rules.day(c.get("start_date"), "codes", w + "Start Date", i)
        end = rules.day(c.get("end_date"), "codes", w + "End Date", i)
        if start and end and TODAY not in (start, end) and end <= start:
            rules.bad("codes", f"{w}End Date must be after Start Date (Oracle: \"Start Date must be before End "
                      "Date\").", i)
        item["codes"].append({
            "LookupCode": cd, "Meaning": mn,
            "Description": rules.text(c.get("description"), "codes", w + "Item Description", MAX["Description"], row=i),
            "EnabledFlag": "Y" if enabled in (None, True) else "N",
            "StartDateActive": start, "EndDateActive": end, "DisplaySequence": seq,
            "Tag": rules.text(c.get("tag"), "codes", w + "Tag", MAX["Tag"], row=i)})
    if not codes and not rules.problems[start_n:]:
        item["no_codes"] = True                 # allowed for an existing type? no: nothing to do
    return item if len(rules.problems) == start_n else None


def parse_requirements(data, path, rules=None):
    """The request -> lookups in export column names. With `rules` the problems are collected
    and bad lookups come back as None; without, any problem stops listing them all."""
    collect = rules is not None
    rules = rules or Rules()
    raw = data.get("lookups") if isinstance(data, dict) else None
    if not isinstance(raw, list) or not raw:
        oracle.fail(f"{path} must contain a non-empty 'lookups' list")
    out, seen = [], set()
    for lk in raw:
        lk = as_lookup(lk)
        t = lk.get("lookup_type")
        if t and t in seen:
            rules.bad("lookup_type", f"Lookup Type '{t}' is listed twice; each lookup type can be there only once.")
        seen.add(t)
        out.append(check_lookup(lk, rules))
    if rules.problems and not collect:
        oracle.fail("The request has problems:\n  " + "\n  ".join(p["text"] for p in rules.problems))
    return out


# ---------------------------------------------------------------- Oracle, read-only (REST)

def rest_type(lookup_type):
    """The lookup type item (exact name) or None."""
    r = oracle.call("GET", f"{oracle.API_BASE}/standardLookups",
                    params={"finder": f"LookupTypeFinder;LookupType={lookup_type}", "limit": 5})
    return next((i for i in r.json().get("items", []) if i.get("LookupType") == lookup_type), None), r


def rest_codes(type_item):
    """All codes of a type (every page)."""
    href = oracle.link_href(type_item, "lookupCodes")
    rows, offset = [], 0
    while href:
        data = oracle.call("GET", href, params={"onlyData": "true", "limit": 500, "offset": offset}).json()
        rows += data.get("items", [])
        if not data.get("hasMore"):
            break
        offset += len(data.get("items", []))
    return href, rows


def meaning_used(meaning):
    """Lookup types that already use this meaning (exact), through REST."""
    m = meaning.replace("'", "''")
    r = oracle.call("GET", f"{oracle.API_BASE}/standardLookups",
                    params={"q": f"Meaning='{m}'", "onlyData": "true", "limit": 5,
                            "fields": "LookupType,Meaning"}).json()
    return [i["LookupType"] for i in r.get("items", []) if i.get("Meaning") == meaning]


def exists_in_oracle(lookup_type):
    return rest_type(lookup_type)[0] is not None


# ---------------------------------------------------------------- modules (names from the screen)

def module_cache():
    """{"modules": {name: {"name", "type", "key", "id", "found"}}}: every module this folder has looked
    up on the screen (name, Module Type, Module Key) and its internal ID once learned. Starts with
    the Module list in CLAUDE.md (names the user gave)."""
    data = {"modules": {}}
    if MODULE_CACHE.exists():
        try:
            data.update(json.loads(MODULE_CACHE.read_text(encoding="utf-8")))
        except ValueError:
            pass
    for name, mid in module_list():
        data["modules"].setdefault(name, {"name": name, "type": None, "key": None, "id": mid,
                                          "found": "CLAUDE.md Module list"})
    return data


def save_module_cache(data):
    MODULE_CACHE.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


def module_list():
    """The Module list (name -> ModuleId) from this folder's CLAUDE.md (names the user gave)."""
    text = (HERE / "CLAUDE.md").read_text(encoding="utf-8")
    part = text.split("### Module list", 1)[1].split("\n### ", 1)[0] if "### Module list" in text else ""
    rows = []
    for line in part.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and MODULE_ID_RE.match(cells[1]):
            rows.append((cells[0], cells[1]))
    return rows


Q = "pt1:r1:0:rt:1:r2:0:dynamicRegion1:0:pt1:AP1:qryId1:"        # the Search region's fields
NEW_ROW = "pt1:r1:0:rt:1:r2:0:dynamicRegion1:0:pt1:AP1:AT1:_ATp:ATt1:0:"


def open_lookups_screen(ui):
    """Setup and Maintenance > Tasks panel > Search > Manage Standard Lookups (the offering's own
    Search Tasks doesn't find it: the task sits in Application Extensions, seen 2026-10-25)."""
    from common import browser
    page = ui.page
    link = page.locator("a:text-is('Manage Standard Lookups'):visible").first

    def find(attempt):
        # 2026-10-26: a click or search lost on Oracle's busy Setup page: the whole search is done again from a
        # freshly opened Setup page (shared retry helper)
        page.goto(f"{oracle.HOST}{browser.SETUP_PATH}", wait_until="domcontentloaded", timeout=120000)
        ui.settle()
        ui.check_signed_in()
        panel = page.locator("[title='Tasks']:visible, a[title*='Task']:visible").first
        panel.wait_for(timeout=90000)
        ui.click(panel, "Tasks panel")
        ui.settle()
        page.wait_for_timeout(1500)
        ui.click(page.locator("a:visible").filter(has_text="Search").last, "Search (all tasks)")
        ui.settle()
        page.wait_for_timeout(2000)
        box = page.locator("input[type=text]:visible, input[type=search]:visible").first
        box.fill("Manage Standard Lookups")
        box.press("Enter")
        ui.settle()
    ui.retry("task search did not find Manage Standard Lookups", find, lambda timeout: link.wait_for(timeout=timeout),
             wait=60000, last_wait=60000)
    module = lambda: ui.page.locator(f"[id='{Q}value30::content']")      # noqa: E731 - the screen's Module field

    def open_(attempt):
        if attempt == 1 or ui.page is page and link.count():
            ui.click(link, "Manage Standard Lookups" + (" (again)" if attempt > 1 else ""))
        ui.settle()
        ui.use_newest_page()

    def opened(timeout):
        ui.page.get_by_role("button", name="Search", exact=True).first.wait_for(timeout=timeout)
        module().wait_for(timeout=timeout)
    ui.retry("Setup page did not open Manage Standard Lookups", open_, opened, wait=60000, last_wait=90000)
    ui.page.wait_for_timeout(1500)
    return ui.page


def leave_screen(ui):
    """Cancel, and Yes to leave without saving: nothing is ever saved from here."""
    page = ui.page
    ui.close_lov_dialogs()
    ui.close_messages()
    b = page.get_by_role("button", name=re.compile(r"^Cancel$"))
    if b.count() and b.first.is_visible():
        ui.click(b.first, "Cancel (nothing saved)")
        ui.settle()
        page.wait_for_timeout(1500)
    yes = page.get_by_role("button", name=re.compile(r"^Yes$"))
    if yes.count() and yes.first.is_visible():
        ui.click(yes.first, "Yes (leave without saving)")
        ui.settle()
    screen = page.locator(f"[id='{Q}value30::content']")

    def again(attempt):              # 2026-10-26: a lost Cancel or Yes leaves the screen open (nothing is saved)
        if attempt == 1:
            return
        if yes.count() and yes.first.is_visible():
            ui.click(yes.first, "Yes (leave without saving)")
        elif b.count() and b.first.is_visible():
            ui.click(b.first, "Cancel (nothing saved, again)")
        ui.settle()
    ui.retry("Manage Standard Lookups did not close after Cancel", again,
             lambda timeout: screen.wait_for(state="hidden", timeout=timeout), wait=15000, last_wait=30000)


def module_rows(ui, text):
    """The Module dialog of the Search region, searched for `text` (Oracle matches the start of
    the name): [{"name", "type", "key"}]. The dialog shows at most 500 rows (seen 2026-10-25), so
    the whole list can't be read at once; each name is searched instead."""
    page = ui.page
    icon = page.locator(f"[id='{Q}value30::lovIconId']")
    # 2026-10-26: the list and dialog checked and opened again, and only a fresh search answer counts
    dlg = ui.search_dialog(lambda: ui.click(icon, "Module list"), page.locator("a:text-is('Search...'):visible").last,
                           "Module")
    box = dlg.locator("input[type=text]:visible").first
    box.fill(text)
    rows = ui.fresh_search(lambda: ui.click(dlg.get_by_role("button", name="Search", exact=True), "Module dialog Search"),
                           lambda: ui.lov_rows(dlg), "Module dialog search")
    ui.close_lov_dialogs()
    return [{"name": r[0], "type": r[1] if len(r) > 1 else "", "key": r[2] if len(r) > 2 else ""} for r in rows if r]


def search_by_module(ui, name):
    """Lookup types of a module (screen search by Module): their names, [] when none."""
    page = ui.page
    page.locator(f"[id='{Q}value00::content']").fill("")
    m = page.locator(f"[id='{Q}value30::content']")
    m.fill(name)
    m.press("Tab")
    ui.settle()
    page.wait_for_timeout(1500)
    ui.close_lov_dialogs()
    read = lambda: page.locator("tr[_afrrk]:visible").evaluate_all(        # noqa: E731
        "rs => rs.map(r => [...r.querySelectorAll('td')].map(td => { const i = td.querySelector('input,select'); "
        "return i ? (i.tagName === 'SELECT' ? i.options[i.selectedIndex].text : i.value) : td.innerText.trim(); })"
        ".filter(x => x))")
    # 2026-10-26: only a fresh answer to this Search counts (a lost Search kept the old rows)
    rows = ui.fresh_search(lambda: ui.click(page.get_by_role("button", name="Search", exact=True).first, "Search"),
                           read, "search by Module")
    return [r[0] for r in rows if r and len(r) > 2 and name in r]


def resolve_modules(names, ui_factory):
    """{name: (ModuleId or None, problem text or None, {"name", "type", "key"})}. A name (or Module
    Key) is looked up in Oracle's Module dialog (exact name, else one case-insensitive match); its
    internal ID is read from a lookup that already uses the module (screen search by Module, then
    REST). Everything found is kept in modules.json, so a module is looked up once."""
    cache = module_cache()
    mods = cache["modules"]
    out, todo = {}, []
    for n in dict.fromkeys(names):
        hit = mods.get(n) or next((m for m in mods.values() if m.get("key") == n), None)
        if hit and hit.get("id"):
            out[n] = (hit["id"], None, hit)
        else:
            todo.append(n)
    if not todo:
        return out
    with ui_factory() as ui:
        open_lookups_screen(ui)
        for n in todo:
            rows = module_rows(ui, n)
            exact = [r for r in rows if r["name"] == n or r["key"] == n]
            if not exact:
                low = [r for r in rows if r["name"].lower() == n.lower()]
                exact = low if len({r["key"] for r in low}) == 1 else []
            if not exact:
                close = rows or module_rows(ui, n.split()[0]) if n.split() else []
                names_ = difflib.get_close_matches(n, list(dict.fromkeys(r["name"] for r in close)), n=6, cutoff=0.4)
                out[n] = (None, f"Oracle has no module called '{n}'." +
                          (f" Close matches: {', '.join(names_)}." if names_ else ""), None)
                continue
            if len({r["key"] for r in exact}) > 1:
                out[n] = (None, f"Oracle has more than one module called '{n}' (Module Keys "
                                f"{', '.join(r['key'] for r in exact)}), so it isn't clear which one is meant. Not "
                                "supported yet: use a module whose name is unique.", None)
                continue
            hit = dict(exact[0])
            types = search_by_module(ui, hit["name"])
            mid, via = None, None
            for t in types[:3]:
                item, _ = rest_type(t)
                if item and item.get("ModuleId"):
                    mid, via = item["ModuleId"], t
                    break
            hit.update(id=mid, found=f"learned from lookup {via}" if via else None)
            mods[hit["name"]] = hit
            if mid:
                out[n] = (mid, None, hit)
                print(f"  module {hit['name']} ({hit['type']} {hit['key']}): ID {mid}, learned from lookup {via}")
            else:
                out[n] = (None, f"Oracle has the module '{hit['name']}', but no lookup type uses it yet, so its "
                                "internal number can't be read here. Use a module that has lookups, or create one "
                                "lookup in it by hand first.", hit)
        leave_screen(ui)
    save_module_cache(cache)
    return out


def ui_factory(work=None):
    from common import browser
    work = work or oracle.init_work_dir(HERE)
    return browser.OracleUI(work, headless=True)


# ---------------------------------------------------------------- the plan (Oracle, read-only)

def plan(lookups, rules_per, need_modules=True):
    """For each checked lookup: new or exists (level, existing codes, codes to add / skip), the
    module, a type meaning clash, and every problem. Read-only (REST GETs; the screen only for
    module names not resolved yet)."""
    plans, server_day = [], None
    names = [lk["module"] for lk in lookups if lk and lk["module"] and not lk["ModuleId"]]
    modules = {}
    for lk, rules in zip(lookups, rules_per):
        p = {"lk": lk, "rules": rules, "status": "problems", "level": None, "existing": [], "add": [],
             "skip": [], "module": None, "type_item": None}
        plans.append(p)
        if not lk:
            continue
        item, resp = rest_type(lk["LookupType"])
        server_day = server_day or oracle.server_date(resp)
        p["type_item"] = item
        if item:
            p["level"] = item.get("CustomizationLevel")
            href, existing = rest_codes(item)
            p["existing"] = existing
            have = {c["LookupCode"]: c for c in existing}
            used = {c.get("Meaning"): c["LookupCode"] for c in existing}
            if p["level"] == "S":
                rules.bad("lookup_type", f"{lk['LookupType']} is a System lookup type: Oracle allows no new codes "
                          "in it. Nothing will be sent.", fix="Use a User or Extensible type, or a new one.")
            for i, c in enumerate(lk["codes"], 1):
                if c["LookupCode"] in have:
                    p["skip"].append(c["LookupCode"])
                    continue
                if c["Meaning"] in used:
                    rules.bad("codes", f"Code {i}: Meaning '{c['Meaning']}' is already used by code "
                              f"{used[c['Meaning']]} of {lk['LookupType']} (Oracle FND-7103).", i)
                p["add"].append(c)
            if not lk["existing_only"] and lk["codes"]:
                p.setdefault("notes", []).append(f"{lk['LookupType']} already exists in Oracle, so this type row is "
                                                 "skipped; its codes are added to the existing type.")
            for k, label in (("Meaning", "Meaning"), ("Description", "Item Description")):
                if lk[k] and lk[k] != (item.get(k) or ""):
                    p.setdefault("notes", []).append(f"{label} of the existing type stays '{item.get(k) or ''}' "
                                                     f"(the request says '{lk[k]}'; existing lookups are never changed).")
        elif lk["existing_only"]:
            rules.bad("lookup_type", f"Lookup Type '{lk['LookupType']}' isn't a new type in this request and doesn't "
                      "exist in Oracle, so its codes can't be added to it (names must match exactly: capitals and "
                      "spaces count).", fix="Add the type as a new lookup type, or write the existing type's name exactly.")
        else:
            type_name_problems(lk["LookupType"], rules)
            if not lk["Meaning"]:
                rules.bad("meaning", "Meaning is required for a new lookup type.")
            elif meaning_used(lk["Meaning"]):
                rules.bad("meaning", f"Another lookup type ({meaning_used(lk['Meaning'])[0]}) already has the "
                          f"meaning '{lk['Meaning']}' (Oracle FND-7104).", fix="Choose a different Meaning.")
            if not lk["module"] and not lk["ModuleId"]:
                rules.bad("module", "Module is required for a new lookup type.")
            if not lk["codes"]:            # allowed (Oracle has types without codes, e.g. "2003 SIC")
                p.setdefault("notes", []).append("0 codes: the type is created without codes. Not proven yet: "
                                                 "this folder hasn't created a type without codes by the import.")
            p["add"] = list(lk["codes"])
            if lk["module"] and not lk["ModuleId"]:
                modules.setdefault(lk["module"], []).append(p)
        if item and not lk["codes"] and lk["existing_only"]:
            rules.bad("codes", "No codes are given, so there is nothing to add.")
    if need_modules and modules:
        res = resolve_modules(list(modules), ui_factory)
        for name, ps in modules.items():
            mid, problem, hit = res[name]
            for p in ps:
                if problem:
                    p["rules"].bad("module", problem, fix="Use the module's name exactly as Oracle shows it.")
                else:
                    p["lk"]["ModuleId"] = mid
                    p["module"] = {"name": (hit or {}).get("name") or name, "key": (hit or {}).get("key"), "id": mid}
    if server_day:
        today_pairs(plans, server_day)
    for p in plans:
        if not p["lk"] or p["rules"].problems:
            p["status"] = "problems"
        elif p["type_item"]:
            p["status"] = "exists" if not p["add"] else "add_codes"
        else:
            p["status"] = "new"
            p["new_type"] = True
    return plans, server_day


def today_pairs(plans, server_day):
    """End Date after Start Date also when one of them is the word "today" (only known with Oracle's date;
    before 2026-10-26 such a pair was not compared). Read-only."""
    day = (server_day - timedelta(days=1)).strftime("%Y/%m/%d")
    for p in plans:
        for i, c in enumerate((p["lk"] or {}).get("codes") or [], 1):
            s_, e_ = c.get("StartDateActive"), c.get("EndDateActive")
            if TODAY in (s_, e_) and s_ and e_:
                s_, e_ = (day if x == TODAY else x for x in (s_, e_))
                if e_ <= s_:
                    p["rules"].bad("codes", f"Code {i} ({c.get('LookupCode')}): End Date {e_.replace('/', '-')} must be "
                                   f"after Start Date {s_.replace('/', '-')} (\"today\" = Oracle's today minus one day; "
                                   "Oracle: \"Start Date must be before End Date\").", i)


def upload_problems(lookups, per):
    """Rules across one upload: two NEW lookup types with the same meaning (Oracle's FND-7104 \"Another lookup
    type already has the same meaning\" refuses the second one at import; exact, capitals count: proven
    2026-10-26, ZZ_TEST_LK_6142_TMEAN was saved with another type's meaning in other capitals)."""
    seen = {}
    for lk, r in zip(lookups, per):
        if not lk or lk["existing_only"] or not lk.get("Meaning"):
            continue
        if lk["Meaning"] in seen:
            r.bad("meaning", f"Lookup type {seen[lk['Meaning']]} in this upload already has the meaning "
                  f"'{lk['Meaning']}'; Oracle allows each meaning on one lookup type only (FND-7104).",
                  fix="Give one of them a different Meaning.")
        else:
            seen[lk["Meaning"]] = lk["LookupType"]


def resolve_today(lk, server_day):
    day = (server_day - timedelta(days=1)).strftime("%Y/%m/%d")
    for c in lk["codes"]:
        for k in ("StartDateActive", "EndDateActive"):
            if c[k] == TODAY:
                c[k] = day
                print(f"  NOTE  {lk['LookupType']}/{c['LookupCode']}: {k} \"today\" -> {day} "
                      f"(Oracle's today {server_day.isoformat()} minus one day)")


def plan_text(p):
    """One plain line about what a run would do with this lookup."""
    lk = p["lk"]
    if not lk:
        return "Has problems; nothing will be sent."
    t, level = lk["LookupType"], LEVELS.get(p["level"], p["level"])
    if p["status"] == "problems":
        return f"{t}: has problems; nothing will be sent for it."
    if p["status"] == "new":
        m = p["module"] or {"name": lk["module"] or lk["ModuleId"]}
        codes = f" ({', '.join(c['LookupCode'] for c in p['add'])})" if p["add"] else ""
        return (f"{t}: new lookup type in {m['name']} with {len(p['add'])} code{'s' if len(p['add']) != 1 else ''}"
                f"{codes}, REST access {ACCESS[lk['RestAccessSecured'] or 'SECURE']}.")
    add = ", ".join(c["LookupCode"] for c in p["add"]) or "none"
    skip = ", ".join(p["skip"]) or "none"
    n_add, n_skip = len(p["add"]), len(p["skip"])
    if p["status"] == "exists":
        return (f"{t} already exists in Oracle ({level} type), so it will be skipped; nothing is changed"
                + (f" (its {n_skip} code{'s' if n_skip != 1 else ''} in the request already exist{'s' if n_skip == 1 else ''})."
                   if n_skip else "."))
    return (f"{t}: already exists ({level} type). {n_add} new code{'s' if n_add != 1 else ''} will be added ({add}), "
            f"{n_skip} already exist{'s' if n_skip == 1 else ''} and {'are' if n_skip != 1 else 'is'} skipped ({skip}). "
            "The type and its existing codes are not changed.")


# ---------------------------------------------------------------- export data (building the import)

def read_export(zip_bytes):
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    names = z.namelist()
    if len(names) != len(set(names)):
        oracle.fail(f"Export zip has duplicate names: {names}")
    exp = {"zip": z,
           "type_name": oracle.find_member(z, TYPE_CSV),
           "code_name": oracle.find_member(z, CODE_CSV),
           "meta_name": oracle.find_member(z, METADATA)}
    exp["th"], trows = oracle.read_csv(z, exp["type_name"])
    exp["ch"], crows = oracle.read_csv(z, exp["code_name"])
    for need in ("LookupType", "Meaning", "ModuleId"):
        if need not in exp["th"]:
            oracle.fail(f"{TYPE_CSV} has no '{need}' column: {exp['th']}")
    for need in (CODE_TYPE_COL, "LookupCode", "Meaning"):
        if need not in exp["ch"]:
            oracle.fail(f"{CODE_CSV} has no '{need}' column: {exp['ch']}")
    exp["types"] = {r[exp["th"].index("LookupType")]: dict(zip(exp["th"], r)) for r in trows}
    exp["codes"] = collections.defaultdict(dict)
    for r in crows:
        row = dict(zip(exp["ch"], r))
        exp["codes"][row[CODE_TYPE_COL]][row["LookupCode"]] = row
    return exp


def _row(header, values, csv_name):
    unknown = set(values) - set(header)
    if unknown:
        oracle.fail(f"{csv_name} has no column(s) {sorted(unknown)}; columns are {header}")
    return [values.get(col, "") for col in header]


def type_values(lk):
    v = dict(UI_TYPE_DEFAULTS)
    v.update({k: lk[k] for k in ("LookupType", "Meaning", "Description", "ModuleId", "RestAccessSecured")
              if lk.get(k)})
    return v


def code_values(lk, c):
    v = dict(UI_CODE_DEFAULTS)
    v.update({k: val for k, val in c.items() if val not in ("", None)})
    v[CODE_TYPE_COL] = lk["LookupType"]
    return v


def build_rows(exp, lookups):
    """One type row and its code rows per lookup; every other column stays empty."""
    type_rows, code_rows = [], []
    for lk in lookups:
        type_rows.append(_row(exp["th"], type_values(lk), TYPE_CSV))
        for c in lk["codes"]:
            code_rows.append(_row(exp["ch"], code_values(lk, c), CODE_CSV))
    return type_rows, code_rows


def build_import_zip(exp, type_rows, code_rows):
    """All 3 files, each once; the CSVs hold only the new rows."""
    return oracle.build_zip({
        exp["type_name"]: oracle.write_csv(exp["th"], type_rows),
        exp["code_name"]: oracle.write_csv(exp["ch"], code_rows),
        exp["meta_name"]: exp["zip"].read(exp["meta_name"]),
    })


def import_keep_going(zip_bytes):
    """The CSV import like oracle.import_task, but an import that ends with errors does not stop
    the run: its log files are saved and read, and the read-back decides what was saved
    (2026-10-25). Returns (status, {row identifier: [Oracle's messages]}, saved file paths)."""
    print(f"Importing {TASK} ({len(zip_bytes)} bytes) ...")
    proc_url, _ = oracle.process_urls("Import", TASK, 0)
    r = oracle.call("POST", proc_url, json={"TaskCode": TASK, "FileContent": base64.b64encode(zip_bytes).decode(),
                                            "SourceTargetDiffOkFlag": True})
    pid = r.json().get("ProcessId")
    if pid is None:
        oracle.fail(f"No ProcessId in import response:\n{r.text}")
    print(f"  ProcessId={pid}")
    _, result_url = oracle.process_urls("Import", TASK, pid)
    result = oracle.poll_result(result_url, "import")
    status = result.get("StatusCode")
    if status == "COMPLETED":
        return status, {}, []
    saved = oracle._save_result_attachments(result, f"{TASK}_{pid}_import")
    print(f"  import ended {status}; Oracle's logs saved: {[p.name for p in saved]}")
    rows = {}
    for path in saved:
        rows.update(log_errors(path.read_bytes()))
    return status, rows, saved


def log_errors(data):
    """Failed rows named in an import log or report: {row identifier: [messages]}. The log may be
    plain text or a zip of text files; lines look like "Row Identifier: <key>. Status: Error. ...
    Message Text: ..." (the Payment Terms import log, 2026-10-25)."""
    texts = []
    if data[:2] == b"PK":
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
            texts = [z.read(n).decode("utf-8", "replace") for n in z.namelist()]
        except zipfile.BadZipFile:
            texts = []
    else:
        texts = [data.decode("utf-8", "replace")]
    rows = {}
    for text in texts:
        # The lookups import log (seen 2026-10-25) is one line with written-out \r\n; a failed type
        # shows as "Exception[0]: Lookup1[LookupType:X,LookupCode:Y,...] ... with a JboException:
        # JBO-25013: Too many objects match the primary key ...". Oracle drops the WHOLE type; the
        # code it names was not always the bad one (a 31-character code was named as the next code).
        flat_ = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", "\t").replace("\\/", "/")
        for blk in re.split(r"(?=Exception\[\d+\]: )", flat_)[1:]:
            head = re.match(r"Exception\[\d+\]: \w+\[LookupType:([^,\]]*)(?:,LookupCode:([^,\]]*))?", blk)
            if not head:
                continue
            blk = re.sub(r"\n\s*at [^\n]*", "", blk)
            why = [f"{n}: {x}" for n, x in re.findall(r"<NUMBER>([^<]*)</NUMBER><TEXT>([^<]*)</TEXT>", blk)]
            why += [x.strip() for x in re.findall(r"_Rule_\d+: ([^\n\[]*)", blk)]                 # e.g. dates
            why += [x.strip() for x in re.findall(r"JBO-(?:25009|27040|27014): ([^\n\\]*)", blk)][:1]
            if not why:
                gen = re.search(r"with an? \w*Exception: (JBO-\d+: [^\n]*?)(?:\.\.|\n)", blk)
                why = [(gen.group(1) if gen else "no reason given") + " (Oracle gives no plainer reason)"]
            where = f"code {head.group(2)}: " if head.group(2) else ""
            rows.setdefault(head.group(1), [])
            for w in dict.fromkeys(why):
                if where + w not in rows[head.group(1)]:
                    rows[head.group(1)].append(where + w)
        for block in text.split("Row Identifier: ")[1:]:
            ident = block.split(". Status:", 1)[0].strip()
            if "Status: Error" not in block.split("\n", 1)[0]:
                continue
            body = block.split("Message Text:", 1)[-1].split("\n\n\n", 1)[0]
            msgs = []
            for part in re.split(r"JBO-\d+:\s*", " ".join(body.split())):
                part = re.sub(r"(Failed to validate a row with key .*? in \S+|The data row that caused the "
                              r"exception exists in the \S+ file\.)\s*", "", part).strip(" .")
                if part and "cannot be loaded" not in part and part not in msgs:
                    msgs.append(part)
            rows.setdefault(ident, []).extend(m for m in msgs if m not in rows.get(ident, []))
    return rows


# ---------------------------------------------------------------- read back (REST) and compare

def norm(v):
    return "" if v is None else str(v).replace("/", "-") if isinstance(v, str) else str(v)


def compare_code(want, got):
    """Differences between a requested code and what REST shows (dates as YYYY-MM-DD)."""
    diffs = {}
    for k in ("Meaning", "Description", "EnabledFlag", "StartDateActive", "EndDateActive", "DisplaySequence", "Tag"):
        w = norm(want.get(k) or ("Y" if k == "EnabledFlag" else ""))
        g = norm(got.get(k))
        if w != g:
            diffs[k] = (got.get(k), want.get(k))
    return diffs


def read_back(lookups_done, report):
    """Every type and code the run sent, read through REST: report[type] = {"type": "saved" |
    "not saved" | "existing", "codes": {code: "saved" | "not saved" | "differs: ..."}, "reasons"}."""
    ok = True
    for lk in lookups_done:
        t = lk["LookupType"]
        rep = report.setdefault(t, {"codes": {}, "reasons": []})
        item, _ = rest_type(t)
        if item is None:
            rep["type"] = "not saved"
            ok = False
            for c in lk["codes"]:
                rep["codes"][c["LookupCode"]] = "not saved"
            print(f"  NOT SAVED  {t}" + (f": {'; '.join(rep['reasons'])}" if rep["reasons"] else ""))
            continue
        if rep.get("type") != "existing":
            diffs = {k: (item.get(k), v) for k, v in type_values(lk).items() if norm(item.get(k)) != norm(v)}
            rep["type"] = "saved" if not diffs else f"saved, but differs: {diffs}"
            ok &= not diffs
            print(f"  {'OK  ' if not diffs else 'FAIL'}  {t}: type {rep['type']}")
        _, got = rest_codes(item)
        have = {c["LookupCode"]: c for c in got}
        for c in lk["codes"]:
            g = have.get(c["LookupCode"])
            if g is None:
                rep["codes"][c["LookupCode"]] = "not saved"
                ok = False
                print(f"  NOT SAVED  {t}/{c['LookupCode']}")
                continue
            diffs = compare_code(c, g)
            rep["codes"][c["LookupCode"]] = "saved" if not diffs else f"saved, but differs: {diffs}"
            ok &= not diffs
            print(f"  {'OK  ' if not diffs else 'FAIL'}  {t}/{c['LookupCode']}: {rep['codes'][c['LookupCode']]}")
        rep["after_codes"] = got
        rep["after_type"] = item
    return ok


# ---------------------------------------------------------------- create

def create_lookups(lookups, here, dry_run=False, from_export=None, progress=None, found=None, plans=None):
    """The full run: plan (skip existing types' existing codes, refuse System types), import the
    new types with their codes, POST new codes of existing types, read every one back. Returns the
    report {type: {...}}; stops (oracle.fail) with "Saved: ... / Not saved: ..." when anything
    wasn't saved or differs."""
    work = oracle.init_work_dir(here)
    found = {} if found is None else found
    if plans is None:
        per = [Rules() for _ in lookups]
        plans, server_day = plan(lookups, per)
    else:
        server_day = None
    problems = [p for p in plans if p["rules"].problems]
    if problems:
        oracle.fail("The request has problems:\n  " + "\n  ".join(
            q["text"] for p in problems for q in p["rules"].problems))
    if server_day is None:
        server_day = oracle.server_date(rest_type("YES_NO")[1])
    for p in plans:
        resolve_today(p["lk"], server_day)
    new = [p["lk"] for p in plans if p["status"] == "new"]
    adds = [p for p in plans if p["status"] == "add_codes"]
    for p in plans:
        if p["status"] == "exists":
            print(f"  SKIP  {p['lk']['LookupType']}: exists and every requested code is already there - not touched")
    report = {}
    if not new and not adds:
        print("Nothing to create.")
        oracle.cleanup_work_dir()
        return report

    if new:
        before_bytes = Path(from_export).read_bytes() if from_export else oracle.export_task(TASK, "before")[0]
        before = read_export(before_bytes)
        type_rows, code_rows = build_rows(before, new)
        import_bytes = build_import_zip(before, type_rows, code_rows)
        path = oracle.save_work_file(import_bytes, TASK, "import")
        print(f"Built {len(type_rows)} type row(s), {len(code_rows)} code row(s) -> {path}")
        if dry_run:
            print(f"Dry run: not importing. Files kept in {work}")
            return report
        if progress:
            progress.step("creating")
        found["_imported"] = True
        status, reasons, _ = import_keep_going(import_bytes)
        for lk in new:
            rep = report.setdefault(lk["LookupType"], {"codes": {}, "reasons": []})
            for ident, msgs in reasons.items():
                if ident == lk["LookupType"] or ident.startswith(lk["LookupType"] + ",") or \
                        ident.startswith(lk["LookupType"] + " "):
                    rep["reasons"] += [f"{ident}: {m}" if ident != lk["LookupType"] else m for m in msgs]
        if reasons and not any(r["reasons"] for r in report.values()):
            report.setdefault("_import", {"codes": {}, "reasons": []})["reasons"] = [
                f"{k}: {'; '.join(v)}" for k, v in reasons.items()]
    elif dry_run:
        print("Dry run: nothing to import; new codes of existing types would be sent through REST.")
        return report

    for p in adds:                                   # new codes of existing User / Extensible types
        lk, t = p["lk"], p["lk"]["LookupType"]
        rep = report.setdefault(t, {"codes": {}, "reasons": [], "type": "existing"})
        rep["type"] = "existing"
        href = oracle.link_href(p["type_item"], "lookupCodes")
        if progress:
            progress.step("creating", text=f"Adding {len(p['add'])} code(s) to {t}")
        for c in p["add"]:
            body = {k: v for k, v in c.items() if v not in ("", None)}
            body["EnabledFlag"] = c["EnabledFlag"] or "Y"
            for k in ("StartDateActive", "EndDateActive"):
                if body.get(k):
                    body[k] = body[k].replace("/", "-")
            if body.get("DisplaySequence"):
                body["DisplaySequence"] = int(body["DisplaySequence"])
            found["_imported"] = True
            r, err = oracle.try_call("POST", href, json=body, timeout=120)
            if err:
                rep["reasons"].append(f"{c['LookupCode']}: {plain_rest_error(r, err)}")
                print(f"  REFUSED  {t}/{c['LookupCode']}: {plain_rest_error(r, err)}")
            else:
                print(f"  created {t}/{c['LookupCode']} (HTTP {r.status_code})")
        p["lk"] = dict(lk, codes=p["add"])

    if progress:
        progress.step("verifying")
    print("Reading back every type and code ...")
    done = new + [p["lk"] for p in adds]
    ok = read_back(done, report)
    found.update({t: r for t, r in report.items()})
    def codes_of(r):
        ok_ = [k for k, v in r["codes"].items() if v == "saved"]
        return ", ".join(ok_) if len(ok_) <= 10 else f"{len(ok_)} codes"
    saved = [f"{t}" + (f" ({codes_of(r)})" if r["codes"] else " (no codes)")
             for t, r in report.items() if not t.startswith("_") and
             (any(v == "saved" for v in r["codes"].values()) or str(r.get("type", "")).startswith("saved"))]
    missing = [f"{t}/{k}" for t, r in report.items() if not t.startswith("_")
               for k, v in r["codes"].items() if v != "saved"]
    print("Saved: " + ("; ".join(saved) or "none"))
    print("Not saved or differs: " + (", ".join(missing) or "none"))
    if not ok:
        why = "; ".join(f"{t}: {' | '.join(r['reasons'])}" for t, r in report.items() if r.get("reasons"))
        oracle.fail(f"Saved: {'; '.join(saved) or 'none'}. Not saved or differs: {', '.join(missing)}. "
                    f"Oracle said: {why or 'nothing more (see the FAIL lines)'}")
    print("All requested lookups and codes verified.")
    oracle.cleanup_work_dir()
    return report


def checked_problems(req, p):
    """This folder's own stops found right before sending (e.g. a meaning another code took since the preview)
    in the same structured shape as Oracle's refusals, so the page can ask about them (2026-10-26)."""
    codes = req.get("codes") if isinstance(req.get("codes"), list) else []
    reasons = []
    for q in p["rules"].problems:
        if q.get("key") == "codes" and q.get("row") and q["row"] <= len(codes):
            reasons.append(f"{codes[q['row'] - 1].get('code')}: {q['text']}")
        elif q.get("key") == "meaning":
            reasons.append(f"{req.get('lookup_type')}: {q['text']}")
    return refusal_problems(req, p, {"reasons": reasons})


def refusal_problems(req, p, rep):
    """Oracle's refusal reasons for one lookup -> the page's structured problems [{field, value, reason,
    suggestions, rows?, row?, where?}] for the decision panel (2026-10-26). Reasons are "CODE: message" for a
    code (REST) or the import log's row identifier; a code's value goes into that code row. Suggestions are
    values the type doesn't use yet (exact, as Oracle compares: proven 2026-10-26)."""
    codes = req.get("codes") if isinstance(req.get("codes"), list) else []
    used = {(c.get("Meaning") or "") for c in p.get("existing") or []} | {str(c.get("meaning") or "") for c in codes}
    out = []
    for reason in rep.get("reasons") or []:
        ident, _, msg = reason.partition(": ")
        msg = msg or reason
        t = msg.lower()
        n = next((k for k, c in enumerate(codes, 1) if str(c.get("code")) == ident.strip()), None)
        if n:
            c = codes[n - 1]
            if "meaning" in t:
                base = str(c.get("meaning") or "")
                field, sugg = "meaning", [x for x in [f"{base} ({c.get('code')})"] + [f"{base} {k}" for k in range(2, 9)]
                                          if x not in used and len(x) <= MAX["Meaning"]][:3]
            elif "primary key" in t or ("code" in t and "length" in t):
                field, sugg = "code", [f"{str(c.get('code'))[:27]}_{k}" for k in range(2, 5)]
            elif "date" in t:
                field, sugg = "end_date", []
            elif "long" in t or "sequence" in t:
                field, sugg = "display_sequence", []
            else:
                continue
            out.append({"field": field, "value": c.get(field), "reason": msg, "text": msg, "suggestions": sugg,
                        "rows": "codes", "row": n, "where": f"Code {n} ({c.get('code')})"})
        elif "meaning" in t and req.get("meaning"):
            base = req["meaning"]
            out.append({"field": "meaning", "value": base, "reason": msg, "text": msg,
                        "suggestions": [f"{base} ({req.get('lookup_type')})"][:1]})
        elif ("LookupEO" in msg or "JBO-25017" in msg) and req.get("lookup_type"):
            v = str(req["lookup_type"])
            fixed = v.upper()[3:].lstrip("_") if v.upper().startswith("ORA") else v.upper()
            out.append({"field": "lookup_type", "value": v, "reason": msg, "text": msg,
                        "suggestions": [x for x in [fixed, "XX_" + fixed] if x and x != v][:2]})
    return out


def plain_rest_error(r, err):
    """Oracle's own message from a refused REST call (its first line), else the error text."""
    text = (r.text if r is not None else err) or ""
    m = re.search(r"([A-Z]{2,5}-\d{4,6}[^\n]*|[^\n]*\(FND-\d+\))", text)
    return " ".join((m.group(0) if m else text).split())[:400]


# ---------------------------------------------------------------- page interface

SPEC = {
    "title": "Create a lookup",
    "description": "Creates a new lookup with its codes, or adds new codes to an existing one; nothing existing is changed.",
    "fields": [
        {"key": "lookup_type", "label": "Lookup name", "required": True, "type": "text",
         "placeholder": "XX_ORDER_HOLD_REASONS", "default": None,
         "help": "Up to 30 characters. An existing lookup gets only the codes it doesn't have yet."},
        {"key": "meaning", "label": "Name shown to users", "required": False, "type": "text",
         "placeholder": "Order hold reasons", "default": None,
         "help": "Needed for a new lookup. Up to 80 characters; no other lookup may already use it."},
        {"key": "module", "label": "Module", "required": False, "type": "pick",
         "placeholder": "Order Management", "default": None, "list": "samples",
         "help": "Needed for a new lookup."},
        {"key": "existing_only", "label": "Only add codes to a lookup that already exists", "required": False,
         "type": "yes-no", "placeholder": "no", "default": False},
        {"key": "codes", "label": "Codes", "required": False, "type": "rows", "min_rows": 0,
         "add_label": "Add a code", "row_label": "Code",
         "fields": [
             {"key": "code", "label": "Code", "required": True, "type": "text", "placeholder": "OPEN"},
             {"key": "meaning", "label": "Name shown to users", "required": True, "type": "text",
              "placeholder": "Open"},
             {"key": "description", "label": "Description", "required": False, "type": "text",
              "placeholder": "Waiting for review"},
             {"key": "enabled", "label": "Active", "required": False, "type": "yes-no",
              "placeholder": "yes", "default": True},
             {"key": "start_date", "label": "Start date", "required": False, "type": "date",
              "placeholder": "2026-10-21"},
             {"key": "end_date", "label": "End date", "required": False, "type": "date",
              "placeholder": "2030-12-31"},
             {"key": "display_sequence", "label": "Position in the list", "required": False,
              "type": "number", "placeholder": "1"},
             {"key": "tag", "label": "Tag", "required": False, "type": "text", "placeholder": "HOLD"},
         ]},
        {"key": "description", "label": "Description", "required": False, "type": "text",
         "placeholder": "Reasons an order can be put on hold", "default": None},
        {"key": "rest_access_secured", "label": "Who may read it from other programs",
         "required": False, "type": "pick", "placeholder": "Secure",
         "default": "SECURE"},
    ],
}
WHERE = "Setup and Maintenance > search the task Manage Standard Lookups > Lookup Type {t}"
# Drop-down samples: modules that have created a verified lookup in this project (a value joins
# only after such a create); `--options module --all` gives the cached screen list.
SAMPLES = {"module": ["Order Management"]}


def options_for(key):
    if key == "rest_access_secured":
        return [{"value": c, "label": label} for c, label in ACCESS.items()]
    if key != "module":
        raise page.PageError("FAILED", detail=f"no list for {key!r}")
    if sys.argv[1:2] == ["--options"] and "--all" not in sys.argv:
        return [{"value": n, "label": n} for n in proven_modules()]
    return [{"value": m["name"], "label": m["name"]} for m in module_cache()["modules"].values() if m.get("id")]


def proven_modules():
    """Modules a verified lookup was created in (CLAUDE.md > Module list names + SAMPLES)."""
    return list(dict.fromkeys(SAMPLES["module"] + [n for n, _ in module_list()]))


def run_request(request, progress):
    """--run: one lookup type (new, or new codes for an existing one) through the full run."""
    oracle.check_environment()
    rules = Rules()
    lk = parse_requirements({"lookups": [request]}, "page", rules)
    if rules.problems:
        raise page.PageError("INVALID_REQUEST", " ".join(p["text"] for p in rules.problems), page_problems(rules))
    plans, _ = plan(lk, [rules])
    if rules.problems:
        code = "NOT_IN_ORACLE" if any(p["key"] == "module" for p in rules.problems) else "INVALID_REQUEST"
        raise page.PageError(code, " ".join(p["text"] for p in rules.problems), page_problems(rules))
    t = lk[0]["LookupType"]
    where = WHERE.format(t=t)
    if plans[0]["status"] == "exists":
        item = plans[0]["type_item"]
        return {"text": f"The lookup {t} already exists in Oracle with every requested code, so nothing was "
                        "changed.", "skipped": True, "where": where,
                "created": {k: item.get(k) for k in ("LookupType", "Meaning", "Description", "ModuleId")}}
    found, messages, real_fail = {}, [], oracle.fail

    def fail(message):
        messages.append(str(message))
        real_fail(message)
    oracle.fail = fail
    try:
        create_lookups(lk, HERE, progress=progress, found=found, plans=plans)
    except (SystemExit, Exception) as e:  # noqa: BLE001 - every stop says what was saved
        msg = messages[-1] if messages else f"{type(e).__name__}: {e}"
        rep = found.get(t) or {}
        saved_codes = [k for k, v in rep.get("codes", {}).items() if v == "saved"]
        saved = "yes" if saved_codes or rep.get("type") == "saved" else ("maybe" if found.get("_imported")
                                                                           and not rep else "no")
        if rep.get("reasons") and not saved_codes and rep.get("type") != "saved":
            raise page.PageError("INVALID_REQUEST", f"Oracle refused it: {' | '.join(rep['reasons'])}. Nothing was "
                                 "saved in Oracle.", {"message": msg, "saved": "no", "registry_id": None})
        text = {"no": "Nothing was saved in Oracle.",
                "yes": f"Saved in Oracle: {t}" + (f" ({', '.join(saved_codes)})" if saved_codes else "") +
                       "; the rest wasn't, or doesn't match.",
                "maybe": "Something may have been saved in Oracle."}[saved]
        code = page._classify(msg)
        raise page.PageError(code, f"{page.ERRORS[code]} {text}", {"message": msg, "saved": saved, "registry_id": None})
    finally:
        oracle.fail = real_fail
    progress.step("done")
    rep = found[t]
    after = rep.get("after_type") or {}
    got = {c["LookupCode"]: c for c in rep.get("after_codes", [])}
    added = [c["LookupCode"] for c in plans[0]["add"]]
    return {"text": (f"Created the lookup {t} ({after.get('Meaning')}) with {len(added)} code"
                     f"{'s' if len(added) != 1 else ''}" if plans[0]["status"] == "new" else
                     f"Added {len(added)} code{'s' if len(added) != 1 else ''} to the existing lookup {t}"
                     + (f" ({len(plans[0]['skip'])} already there, not changed)" if plans[0]["skip"] else ""))
                    + ", and checked every value in Oracle.",
            "where": where,
            "created": {"LookupType": t, "Meaning": after.get("Meaning"), "Description": after.get("Description"),
                        "ModuleId": after.get("ModuleId"), "RestAccessSecured": after.get("RestAccessSecured"),
                        "CustomizationLevel": after.get("CustomizationLevel"),
                        "codes": [{k: got[c].get(k) for k in CODE_FIELDS} for c in added if c in got]}}


def page_problems(rules):
    return [{"field": p["key"], "problem": "invalid", "text": p["text"], **({"row": p["row"]} if p["row"] else {})}
            for p in rules.problems]


# ---------------------------------------------------------------- --run-batch (the upload sheet)

def run_batch_command(argv):
    """--run-batch '<JSON list of page requests>' (2026-10-25, the upload sheet): every lookup type of
    an upload in ONE call: the new types in one import, new codes of existing types through REST.
    Progress lines as --run, then one result line: {"step": "result", "ok", "text", "results": [one
    --run style result per request, in order]}. A refused type gets Oracle's reason; Oracle drops a
    whole type when one of its codes is refused, the others are saved; a rerun creates only what is
    missing. A stop with no answer per type (screen, sign-in) also gives a top-level "error" for the
    page's repair rules."""
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
        return {"ok": False, "text": text, "error": {"code": code, "step": current["step"], "detail": {
            "message": message, "saved": saved, "registry_id": None, **({"problems": problems} if problems else {})}}}
    try:
        reqs = json.loads(argv[1] if len(argv) > 1 else "")
        if not isinstance(reqs, list) or not all(isinstance(r, dict) for r in reqs):
            raise ValueError("a list of requests is needed")
    except ValueError as e:
        print(json.dumps({"step": "result", "percent": 100, "ok": False, "text": "The request could not be read.",
                          "error": {"code": "INVALID_REQUEST", "step": "reading", "detail": str(e)}}), file=out)
        return 2
    results, top_error = [None] * len(reqs), None
    with contextlib.redirect_stdout(sys.stderr):
        oracle.check_environment()
        progress.step("reading")
        per = [Rules() for _ in reqs]
        lookups = [parse_requirements({"lookups": [r]}, "page", rr)[0] for r, rr in zip(reqs, per)]
        names = [r.get("lookup_type") for r in reqs]
        for i, n in enumerate(names):
            if n and n in names[:i] and not reqs[i].get("existing_only"):
                per[i].bad("lookup_type", f"Lookup Type '{n}' is listed twice in this upload.")
        upload_problems(lookups, per)
        progress.step("checking")
        crash, found, plans = None, {}, []
        messages, real_fail = [], oracle.fail

        def fail(message):
            messages.append(str(message))
            real_fail(message)
        oracle.fail = fail
        try:
            plans, _ = plan(lookups, per)
            good = [p for p in plans if not p["rules"].problems and p["lk"]]
            for i, p in enumerate(plans):
                if p["rules"].problems or not p["lk"]:
                    results[i] = failed("INVALID_REQUEST", " ".join(q["text"] for q in p["rules"].problems) +
                                        " Nothing was sent for it.", "no",
                                        problems=page_problems(p["rules"]) + checked_problems(reqs[i], p))
            if good:
                create_lookups([p["lk"] for p in good], HERE, progress=progress, found=found, plans=good)
        except page.PageError as e:
            crash = (e.code, e.text, e.detail)
        except (SystemExit, Exception) as e:  # noqa: BLE001 - answered per type below
            msg = messages[-1] if messages else f"{type(e).__name__}: {e}"
            crash = (page._classify(msg), None, msg)
        finally:
            oracle.fail = real_fail
        answered = any(not k.startswith("_") for k in found)
        for i, p in enumerate(plans):
            if results[i] is not None:
                continue
            lk, t = p["lk"], p["lk"]["LookupType"]
            rep = found.get(t) or {}
            codes = rep.get("codes", {})
            ok_codes = [k for k, v in codes.items() if v == "saved"]
            bad_codes = [k for k, v in codes.items() if v != "saved"]
            reasons = " | ".join(rep.get("reasons", []))
            if p["status"] == "exists":
                results[i] = {"ok": True, "skipped": True, "where": WHERE.format(t=t),
                              "text": plan_text(p), "created": {"LookupType": t, "Level": LEVELS.get(p["level"])}}
            elif p["status"] == "new" and str(rep.get("type", "")).startswith("saved") and not bad_codes \
                    and rep.get("type") == "saved":
                results[i] = {"ok": True, "where": WHERE.format(t=t), "created": result_created(t, rep, ok_codes),
                              "text": f"Created the lookup type {t} with {len(ok_codes)} code"
                                      f"{'s' if len(ok_codes) != 1 else ''}, and checked every value in Oracle."}
            elif p["status"] == "add_codes" and ok_codes and not bad_codes:
                results[i] = {"ok": True, "where": WHERE.format(t=t), "created": result_created(t, rep, ok_codes),
                              "text": f"Added {len(ok_codes)} code{'s' if len(ok_codes) != 1 else ''} to the existing "
                                      f"lookup type {t}" + (f"; {len(p['skip'])} already existed and "
                                                            f"{'was' if len(p['skip']) == 1 else 'were'} not changed"
                                                            if p["skip"] else "") + ". Checked in Oracle."}
            elif rep.get("type") == "not saved":
                results[i] = failed("INVALID_REQUEST", f"Oracle refused the lookup type {t}"
                                    + (f": {reasons}" if reasons else "") + ". When one code is refused Oracle "
                                    "drops the whole type, so nothing of it was saved; the other types were. "
                                    "A rerun creates only what is missing.", "no", reasons or None,
                                    problems=refusal_problems(reqs[i], p, rep))
            elif p["status"] == "add_codes" and not ok_codes and bad_codes and rep.get("reasons")                     and all(v == "not saved" for v in codes.values()):
                # 2026-10-26: Oracle refused every new code and the read-back found none: nothing was saved
                # (before, this ended as "may have been saved", because _imported is set before each POST)
                results[i] = failed("INVALID_REQUEST", f"Oracle refused the new code"
                                    f"{'s' if len(bad_codes) != 1 else ''} for {t}: {reasons}. Nothing was saved "
                                    "in Oracle.", "no", reasons, problems=refusal_problems(reqs[i], p, rep))
            elif ok_codes or str(rep.get("type", "")).startswith("saved"):
                results[i] = failed("VERIFY_FAILED" if not reasons else "INVALID_REQUEST",
                                    f"{t}: saved in Oracle: {', '.join(ok_codes) or 'the type'}; not saved or not "
                                    f"matching: {', '.join(bad_codes)}" + (f" ({reasons})" if reasons else "") +
                                    ". A rerun adds only the missing codes.", "yes", reasons or None)
            else:
                code, text, detail = crash or ("FAILED", None, None)
                saved = "maybe" if found.get("_imported") else "no"
                results[i] = failed(code, (text or page.ERRORS.get(code, page.ERRORS["FAILED"])) + " " +
                                    ("Nothing was saved in Oracle." if saved == "no" else
                                     f"{t} may have been saved in Oracle."), saved,
                                    detail if isinstance(detail, str) else json.dumps(detail))
        for i, r in enumerate(results):
            if r is None:  # 2026-10-26: plan() stopped before this type was planned (nothing was sent)
                code, text, detail = crash or ("FAILED", None, None)
                results[i] = failed(code, (text or page.ERRORS.get(code, page.ERRORS["FAILED"])) +
                                    " Nothing was saved in Oracle.", "no",
                                    detail if isinstance(detail, str) else json.dumps(detail))
        if crash and not answered and any(not r["ok"] and r["error"]["code"] not in ("INVALID_REQUEST",)
                                          for r in results if r):
            top_error = {"code": crash[0], "step": current["step"],
                         "detail": crash[2] if isinstance(crash[2], (str, list)) else json.dumps(crash[2])}
        progress.step("done")
    made = sum(1 for r in results if r["ok"] and not r.get("skipped"))
    skipped = sum(1 for r in results if r.get("skipped"))
    bad = sum(1 for r in results if not r["ok"])
    text = (f"Done {made} of {len(results)} lookup types" + (f", {skipped} already there" if skipped else "")
            + (f", {bad} not done" if bad else "") + ".")
    line = {"step": "result", "percent": 100, "ok": not bad, "text": page.plain_check(text, "result"),
            "results": results}
    if top_error:
        line["error"] = top_error
    print(json.dumps(line, ensure_ascii=False), file=out)
    return 0 if not bad else 1


def result_created(t, rep, codes):
    """What Oracle shows now for a type and the codes this run made (the result card)."""
    after = rep.get("after_type") or {}
    got = {c["LookupCode"]: c for c in rep.get("after_codes", [])}
    return {"LookupType": t, "Meaning": after.get("Meaning"), "Description": after.get("Description"),
            "ModuleId": after.get("ModuleId"), "RestAccessSecured": after.get("RestAccessSecured"),
            "CustomizationLevel": after.get("CustomizationLevel"),
            "codes": [{k: got[c].get(k) for k in CODE_FIELDS} for c in codes if c in got]}


# ---------------------------------------------------------------- --plan

def plan_command(argv):
    """--plan [lookups.json | '<JSON>'] (read-only): every rule, then Oracle's state per type
    (REST GETs; the screen only for module names not known yet). One JSON line: {"ok",
    "results": [{"name", "status": "new" | "add_codes" | "exists" | "problems", "level",
    "existing_codes", "add", "skip", "module", "problems": [{"key", "row", "text", "fix"}],
    "summary", "skipped", "found", "fills"}]}. Takes a request file, one page request or a list."""
    import contextlib
    out = sys.stdout
    arg = argv[1] if len(argv) > 1 else str(HERE / "lookups.json")
    try:
        raw = json.loads(Path(arg).read_text(encoding="utf-8") if arg.endswith(".json") and Path(arg).exists()
                         else arg)
        data = raw if isinstance(raw, dict) and "lookups" in raw else {"lookups": raw if isinstance(raw, list) else [raw]}
    except (ValueError, OSError) as e:
        print(json.dumps({"ok": False, "text": f"The request couldn't be read ({e})."}), file=out)
        return 2
    with contextlib.redirect_stdout(sys.stderr):
        oracle.check_environment()
        per = [Rules() for _ in data["lookups"]]
        lookups = [parse_requirements({"lookups": [lk]}, "plan", r)[0] for lk, r in zip(data["lookups"], per)]
        names = [lk.get("lookup_type") if isinstance(lk, dict) else None for lk in data["lookups"]]
        for i, n in enumerate(names):
            if n and n in names[:i]:
                per[i].bad("lookup_type", f"Lookup Type '{n}' is listed twice; each lookup type can be there only once.")
        upload_problems(lookups, per)
        try:
            plans, _ = plan(lookups, per)
        except SystemExit:
            from common import browser
            print(json.dumps({"ok": False, "text": browser.failed_step_text(   # the real failed step (2026-10-26)
                "Oracle couldn't be checked just now.")}), file=out)
            return 1
    results = []
    for p, n in zip(plans, names):
        results.append({"name": n, "ok": True, "status": p["status"],
                        "level": LEVELS.get(p["level"]) if p["level"] else None,
                        "existing_codes": [c["LookupCode"] for c in p["existing"]],
                        "add": [c["LookupCode"] for c in p["add"]] if p["status"] != "problems" else [],
                        "skip": p["skip"], "module": p["module"], "problems": p["rules"].problems,
                        "notes": p.get("notes", []),
                        "summary": " ".join([plan_text(p)] + p.get("notes", [])),
                        "skipped": plan_text(p) if p["status"] == "exists" else None, "found": {}, "fills": {}})
    print(json.dumps({"ok": True, "results": results}, ensure_ascii=False), file=out)
    return 0


# ---------------------------------------------------------------- main

def list_modules(exp):
    """ModuleIds used by lookups in the export, with example lookup types."""
    by_mod = collections.defaultdict(list)
    for t, row in exp["types"].items():
        by_mod[row["ModuleId"]].append(t)
    print(f"{len(by_mod)} ModuleIds in this export (module names are not in the export):")
    for mod, types in sorted(by_mod.items(), key=lambda kv: -len(kv[1])):
        print(f"  {mod}  {len(types):>3} lookups  e.g. {', '.join(sorted(types)[:5])}")


def module_of(exp, lookup_type):
    """ModuleId of one existing lookup: export first, then the REST finder."""
    row = exp["types"].get(lookup_type)
    if row:
        return row["ModuleId"], "export"
    item, _ = rest_type(lookup_type)
    return (item.get("ModuleId"), "standardLookups") if item else (None, None)


def main():
    if sys.argv[1:2] == ["--plan"]:
        sys.exit(plan_command(sys.argv[1:]))
    if sys.argv[1:2] == ["--run-batch"]:            # the upload sheet: every type of an upload in one call
        sys.exit(run_batch_command(sys.argv[1:]))
    if sys.argv[1:2] == ["--modules"]:              # read-only: look modules up by name, show the cache
        oracle.check_environment()
        names = [a for a in sys.argv[2:] if not a.startswith("--")]
        if names:
            for n, (mid, problem, hit) in resolve_modules(names, ui_factory).items():
                print(f"  {n}: " + (f"ID {mid} ({hit['type']} {hit['key']})" if mid else problem))
            oracle.cleanup_work_dir()
        mods = module_cache()["modules"]
        print(f"{len(mods)} module(s) known: " + "; ".join(f"{m['name']} = {m.get('id') or 'no ID'}" for m in mods.values()))
        return
    page.main(SPEC, options_for, run_request)   # --spec / --options / --run; else returns
    here = HERE
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(here / "lookups.json"), help="requirements JSON")
    ap.add_argument("--check", action="store_true",
                    help="read-only: validate, check the task's export/import flags and which "
                         "lookups already exist (REST GET only, no export)")
    ap.add_argument("--dry-run", action="store_true",
                    help="build and save the import zip, do not import")
    ap.add_argument("--from-export", metavar="ZIP",
                    help="use this saved export instead of exporting (dry run only)")
    ap.add_argument("--list-modules", action="store_true",
                    help="export and list the ModuleIds used by existing lookups")
    ap.add_argument("--module-of", metavar="LOOKUP_TYPE",
                    help="export and print the ModuleId of one existing lookup type")
    args = ap.parse_args()

    oracle.check_environment()
    if args.from_export and not args.dry_run:
        oracle.fail("--from-export is only allowed with --dry-run; a real run must "
                    "start from a fresh export so existing records are detected.")
    if args.list_modules:
        oracle.init_work_dir(here)
        mod_bytes, _ = oracle.export_task(TASK, "modules")
        list_modules(read_export(mod_bytes))
        oracle.cleanup_work_dir()
        return
    if args.module_of:
        oracle.init_work_dir(here)
        mod_bytes, _ = oracle.export_task(TASK, "module_of")
        module_id, source = module_of(read_export(mod_bytes), args.module_of)
        if not module_id:
            oracle.fail(f"Lookup type {args.module_of!r} was not found (export and "
                        "standardLookups). Check the exact name with the user.")
        print(f"{args.module_of}: ModuleId {module_id}  (from {source})")
        oracle.cleanup_work_dir()
        return

    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    lookups = parse_requirements(data, args.file)
    print(f"{len(lookups)} lookup type(s) requested in {args.file}")
    if args.check:
        flag, _ = oracle.export_supported(TASK)
        imp = oracle.call("GET", oracle.task_url("Import", TASK)).json().get("ImportSupportedFlag")
        print(f"  {TASK}: ExportSupportedFlag={flag}, ImportSupportedFlag={imp}")
        if flag is not True or imp is not True:
            oracle.fail(f"{TASK} no longer supports CSV export/import (flags {flag}/{imp}).")
        for lk in lookups:
            t = lk["LookupType"]
            print(f"  {t}: " + ("already exists (standardLookups)" if exists_in_oracle(t) else "not found - would be created"))
        print("Check passed: only read (GET) calls were made; nothing was exported, "
              "imported or changed in Oracle.")
        return
    create_lookups(lookups, here, args.dry_run, args.from_export)


if __name__ == "__main__":
    main()
