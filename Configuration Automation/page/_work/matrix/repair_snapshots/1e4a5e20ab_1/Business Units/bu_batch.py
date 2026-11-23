"""Business units from a sheet (2026-10-26): every check up front, then many business units in
one go, with Oracle's answer per business unit.

  python "Business Units/browser_flow.py" --plan '<JSON list or one request>'      # read-only
  python "Business Units/browser_flow.py" --run-batch '<JSON list of requests>'

A request has only the fields of Oracle's Create Business Unit screen:
  {"name": "Karachi Sales",                  # required
   "location": "Go Saas Lahore Office",      # optional; left out: the standing default;
                                             #   "none" (or null): no location, as on the screen
   "manager": "Yaqub, Younas",               # optional: full name or person number; only MANAGERS
   "default_set": "001 CUSTOMER SITE",       # code or name; left out: the standing default
   "active": true}                           # optional, default true (also "yes" / "no")

Step 2 is always the required data access (browser_flow.REQUIRED_ROLES for the configured user).

Order, the same for --plan and --run-batch (nothing is sent for a business unit unless all of
its checks pass, the access user and roles included):
  1. rules without Oracle (name, values, listed twice);
  2. read-only Oracle checks (GET only): business units (exists? only capitals differ?),
     locations (active, code, its reference set; one Manage Business Unit export only for a
     location outside the common set), reference data sets, the manager (publicWorkers),
     the access user and its roles, access rows already on an existing business unit;
  3. --run-batch only: the new business units in ONE Setup task file sent to Oracle
     (setupTaskCSVImports, FUN_MANAGE_BUSINESS_UNIT, only the new rows); Oracle's result and log
     are read (per business unit: saved / not saved with Oracle's reason); every business unit
     read back (finBusinessUnitsLOV: active, location, manager; every other business unit
     unchanged) and in a second export of Manage Business Unit (default set, location code and
     set, status, manager columns exactly as sent);
  4. the missing required access rows (dataSecurities, REST), each read back; then the pricing
     visibility check and common/created_business_units.json (never test names, see TEST_PREFIX).
An existing business unit is never changed and never sent: only its missing access is added.
"""
import base64
import collections
import contextlib
import csv
import io
import json
import re
import sys
import time
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import oracle, page  # noqa: E402

import browser_flow as bf  # noqa: E402  (this folder's main script; its REST helpers are reused)

TASK = "FUN_MANAGE_BUSINESS_UNIT"
HERE = Path(__file__).resolve().parent
NAME_MAX = 240                 # Oracle's limit, see CLAUDE.md > Proven limits (2026-10-26)
KEYS = ("name", "location", "manager", "default_set", "active")
NO_LOCATION = ("none", "(none)", "no location")
# The only managers allowed (the user's decision, 2026-10-26). The import columns are the ones
# Oracle writes for them in the Manage Business Unit export (US1 / Huzaima BU); PersonId is what
# finBusinessUnitsLOV shows as ManagerId. Checked live through publicWorkers before each use.
MANAGERS = [
    {"name": "Yaqub, Younas", "display": "Younas Yaqub", "person_number": "300000002688269",
     "person_id": 300000002688269, "first": "Younas", "last": "Yaqub",
     "start": "2017/01/01", "end": "4712/12/31"},
    {"name": "Smith, Aron", "display": "Aron Smith", "person_number": "4",
     "person_id": 300000326995006, "first": "Aron", "last": "Smith",
     "start": "2023/04/22", "end": "4712/12/31"},
]
# Business units whose names start like this are test data: never written to the shared file
# common/created_business_units.json, so the price list drop-down (demos) doesn't show them.
TEST_PREFIX = "ZZ_TEST_"
WHERE = bf.WHERE


# ---------------------------------------------------------------- rules (no Oracle)

class Unit:
    """One requested business unit: its values, its problems and what Oracle has."""

    def __init__(self, req, index):
        self.req, self.index = req, index
        self.name = req.get("name") if isinstance(req, dict) else None
        self.problems, self.notes = [], []
        self.status = None            # new | exists | problems
        self.existing = None          # Oracle's business unit (finBusinessUnitsLOV item)
        self.location = None          # {"name", "code", "set", "id"} or None (no location)
        self.set = None               # (code, name)
        self.manager = None           # MANAGERS entry
        self.active = True
        self.access = []              # [{"role", "code", "status": "will be added" | "already there"}]

    def bad(self, field, value, reason, suggestions=None, fix=None):
        self.problems.append({"business_unit": self.name, "field": field, "value": value,
                              "reason": reason, "suggestions": list(suggestions or [])[:12],
                              "fix": fix or (f"Pick one of: {', '.join(suggestions[:12])}." if suggestions
                                             else "Please correct it in the sheet.")})


def plain(v):
    return re.sub(r"\s+", " ", str(v)).strip().lower()


def as_bool(v):
    if isinstance(v, bool):
        return v
    t = plain(v) if v is not None else ""
    return {"yes": True, "y": True, "true": True, "no": False, "n": False, "false": False}.get(t)


def check_rules(u):
    req = u.req
    if not isinstance(req, dict):
        u.bad("name", None, "This row could not be read.")
        return
    unknown = sorted(set(req) - set(KEYS))
    if unknown:
        u.bad(unknown[0], req[unknown[0]], f"These can't be set when creating a business unit: "
              f"{', '.join(unknown)}. Only {', '.join(KEYS)} are on Oracle's create screen.")
    n = req.get("name")
    if not isinstance(n, str) or not n.strip():
        u.bad("name", n, "The business unit name is missing.")
    elif n != n.strip():
        u.bad("name", n, "The name starts or ends with a space. Oracle keeps such a space as part of the "
              "name, so it would look like a different business unit; please remove it.",
              [n.strip()], fix="Remove the space at the start or end.")
    elif len(n) > NAME_MAX:
        u.bad("name", n, f"The name is {len(n)} characters long; Oracle takes at most {NAME_MAX}.",
              fix=f"Shorten it to {NAME_MAX} characters or fewer.")
    for k in ("location", "default_set", "manager"):
        v = req.get(k)
        if v is not None and not isinstance(v, str):
            u.bad(k, v, f"{k.replace('_', ' ').capitalize()} must be text.")
        elif isinstance(v, str) and v != v.strip():
            u.bad(k, v, f"{k.replace('_', ' ').capitalize()} starts or ends with a space; please remove it.",
                  [v.strip()])
    a = as_bool(req.get("active", True))
    if a is None:
        u.bad("active", req.get("active"), "Active must be yes or no.", ["yes", "no"])
    else:
        u.active = a


def find_manager(text):
    t = plain(text)
    return next((m for m in MANAGERS if t in (plain(m["name"]), plain(m["display"]), m["person_number"])), None)


# ---------------------------------------------------------------- Oracle's lists (GET only)

class Lists:
    """Each list is read once per run, the slow export only when a location needs it."""

    def __init__(self):
        self._bus = self._locs = self._sets = self._export_rows = None
        self.workers = {}

    def bus(self, fresh=False):
        if self._bus is None or fresh:
            self._bus = bf.rest_all(f"{oracle.API_BASE}/finBusinessUnitsLOV", "business units")
        return self._bus

    def locs(self):
        if self._locs is None:
            self._locs = bf.rest_all(f"{bf.HCM_BASE}/locations", "locations",
                                     fields="LocationId,LocationCode,LocationName,SetId,ActiveStatus")
        return self._locs

    def sets(self):
        if self._sets is None:
            self._sets = bf.rest_all(f"{oracle.API_BASE}/setIdSetsLOV", "reference data sets")
        return self._sets

    def export_rows(self):
        """The Manage Business Unit export (read-only): which reference set each location is in,
        for a location outside the common set (the location list shows only a set id)."""
        if self._export_rows is None:
            print("Reading the Manage Business Unit export (a location outside the common set) ...")
            data = export_zip("plan")
            self._export_rows = csv_rows(data, bf.BU_CSV)
        return self._export_rows

    def worker(self, m):
        """The manager as Oracle has him now (publicWorkers by person number)."""
        pn = m["person_number"]
        if pn not in self.workers:
            items = bf.rget(f"{bf.HCM_BASE}/publicWorkers", "people", q=f"PersonNumber='{pn}'",
                            fields="PersonId,PersonNumber,ListName,DisplayName").get("items", [])
            self.workers[pn] = items[0] if items else None
        return self.workers[pn]


def close(word, choices, n=8):
    """Choices that look like the word: same start, then containing it, then sharing a word."""
    w = plain(word)
    out = [c for c in choices if plain(c).startswith(w[:3])] if w else []
    out += [c for c in choices if w and w in plain(c) and c not in out]
    words = set(w.split())
    out += [c for c in choices if words & set(plain(c).split()) and c not in out]
    return sorted(dict.fromkeys(out), key=str.lower)[:n]


def location_set(lists, loc):
    """The reference set code of a location: COMMON for set id 0; else the set Oracle shows for
    business units that use this location, or another location of the same set (export)."""
    if loc.get("SetId") == 0:
        return "COMMON"
    rows = lists.export_rows()
    used = collections.Counter(r["LocationSetCode"] for r in rows
                               if r["InternalLocationCode"] == loc["LocationCode"] and r["LocationSetCode"])
    if not used:
        same = {l["LocationCode"] for l in lists.locs() if l.get("SetId") == loc.get("SetId")}
        used = collections.Counter(r["LocationSetCode"] for r in rows
                                   if r["InternalLocationCode"] in same and r["LocationSetCode"])
    return used.most_common(1)[0][0] if used else None


def check_oracle(units, lists):
    """Read-only checks of every unit against Oracle's lists (GET only, one export at most)."""
    bus = lists.bus()
    for u in units:
        if not isinstance(u.req, dict) or not isinstance(u.name, str) or not u.name.strip():
            continue
        same = [b for b in bus if b.get("BusinessUnitName") == u.name]
        caps = [b for b in bus if b.get("BusinessUnitName", "").lower() == u.name.lower() and b not in same]
        if same or caps:
            u.existing = (same or caps)[0]
            if not same:
                u.notes.append(f"Oracle already has the business unit '{u.existing['BusinessUnitName']}', "
                               f"which differs from '{u.name}' only in capitals. It is treated as that "
                               "business unit, so no new one is made.")
        # location
        if u.existing:
            pass
        elif "location" in u.req and (u.req["location"] is None or plain(u.req["location"] or "none") in NO_LOCATION):
            u.location = None
        elif not any(p["field"] == "location" for p in u.problems):
            wanted = u.req.get("location") or bf.DEFAULTS["location"]
            locs = lists.locs()
            names = sorted({l["LocationName"] for l in locs if l.get("ActiveStatus") == "A"}, key=str.lower)
            hit = bf.match_value(wanted, [l["LocationName"] for l in locs])
            loc = next((l for l in locs if l["LocationName"] == hit), None) if hit else None
            if loc is None:
                u.bad("location", wanted, f"Oracle has no location called '{wanted}' (a location can't be made "
                      "here).", close(wanted, names) or names[:12])
            elif loc.get("ActiveStatus") != "A":
                u.bad("location", wanted, f"The location '{hit}' exists but isn't active.", close(wanted, names))
            else:
                s = location_set(lists, loc)
                if not s:
                    u.bad("location", wanted, f"The location '{hit}' is in a reference set that no business unit "
                          "uses yet, so its set can't be read safely. Please pick another location.",
                          close(wanted, names))
                else:
                    u.location = {"name": hit, "code": loc["LocationCode"], "set": s, "id": loc["LocationId"]}
        # default set
        if not u.existing and not any(p["field"] == "default_set" for p in u.problems):
            wanted = u.req.get("default_set") or bf.DEFAULTS["default_set"]
            sets = lists.sets()
            code = bf.match_value(wanted, [s["SetCode"] for s in sets])
            if code is None:
                nm = bf.match_value(wanted, [s["SetName"] for s in sets if s.get("SetName")])
                code = next((s["SetCode"] for s in sets if s.get("SetName") == nm), None) if nm else None
            if code is None:
                u.bad("default_set", wanted, f"'{wanted}' is not one of Oracle's {len(sets)} reference data sets.",
                      [f"{s['SetCode']}" for s in sets if s["SetCode"] in close(wanted, [x["SetCode"] for x in sets])
                       or (s.get("SetName") or "") in close(wanted, [x.get("SetName") or "" for x in sets])]
                      or [s["SetCode"] for s in sets][:12])
            else:
                u.set = (code, next(s.get("SetName") or code for s in sets if s["SetCode"] == code))
        # manager
        m = u.req.get("manager")
        if not u.existing and isinstance(m, str) and m.strip() and not any(p["field"] == "manager" for p in u.problems):
            hit = find_manager(m)
            allowed = [x["name"] for x in MANAGERS]
            if hit is None:
                u.bad("manager", m, f"'{m}' can't be the manager: only {' or '.join(allowed)} can be chosen.", allowed)
            else:
                w = lists.worker(hit)
                if not w or w.get("ListName") != hit["name"] or int(w.get("PersonId") or 0) != hit["person_id"]:
                    u.bad("manager", m, f"Oracle doesn't show {hit['name']} (person number {hit['person_number']}) "
                          "as expected any more, so it can't be set safely.", allowed)
                else:
                    u.manager = hit
        if u.existing and any(u.req.get(k) not in (None, "") for k in ("location", "manager", "default_set")) \
                or (u.existing and "active" in u.req and u.active != u.existing.get("ActiveFlag")):
            u.notes.append("It already exists, so the values in this row are not applied: an existing business "
                           "unit is never changed.")


def check_access(units):
    """The required user and roles (GET only): if the access can't be given, nothing is created.
    Returns (user, [(role name, code)]) or (None, [])."""
    try:
        user = bf_user()
        roles = bf.rest_roles(user) if user else []
    except bf.RestUnavailable as e:
        for u in units:
            u.bad("access", None, f"Oracle couldn't be asked whether the access can be given ({bf.oracle_reason(str(e))}); "
                  "nothing is made without it.")
        return None, []
    if not user:
        for u in units:
            u.bad("access", bf.REQUIRED_USER["user"], f"{bf.REQUIRED_USER['user']} (or {bf.REQUIRED_USER['user_fallback']}) "
                  "isn't an active Oracle user, so the required access can't be given; nothing is made.")
        return None, []
    names = {r["RoleName"]: r["RoleCommonName"] for r in roles}
    req = []
    for role in bf.REQUIRED_ROLES:
        hit = bf.match_value(role, list(names))
        if hit is None:
            for u in units:
                u.bad("access", role, f"{user} doesn't hold the role {role}, so that access can't be given on the "
                      "business unit; nothing is made.", close(role, list(names)))
        else:
            req.append((hit, names[hit]))
    return user, req


def bf_user():
    """The required user or its fallback, active; None when neither is (no stop)."""
    href = bf.ds_lov("userNames")
    for user in (bf.REQUIRED_USER["user"], bf.REQUIRED_USER["user_fallback"]):
        hits = [x for x in bf.rget(href, "user names", q=f"DisplayName='{user}'").get("items", [])
                if x.get("DisplayName") == user and x.get("ActiveFlag") == "Y"]
        if hits:
            return user
    return None


def plan(reqs, lists=None):
    """Every check, nothing sent. Returns (units, user, required roles, lists)."""
    lists = lists or Lists()
    units = [Unit(r, i) for i, r in enumerate(reqs)]
    seen = {}
    for u in units:
        check_rules(u)
        if isinstance(u.name, str) and u.name.strip():
            k = u.name.lower()
            if k in seen:
                first = seen[k].name
                if first == u.name:
                    u.bad("name", u.name, f"'{u.name}' is listed twice; each business unit can be there only once.",
                          fix="Keep one of the two rows.")
                else:
                    u.bad("name", u.name, f"'{u.name}' differs from '{first}' (listed earlier) only in capitals. "
                          "Oracle treats them as the same business unit, so only one can be made.",
                          fix="Keep one of the two rows, or give one a different name.")
            seen.setdefault(k, u)
    check_oracle(units, lists)
    for u in units:                  # a capitals-only twin of another row that Oracle also has: say both
        if u.existing and u.existing["BusinessUnitName"] != u.name:
            for p in u.problems:
                if p["field"] == "name" and "only in capitals" in p["reason"]:
                    p["reason"] += (f" Oracle also already has '{u.existing['BusinessUnitName']}', so this row "
                                    "would be skipped and never sent.")
    user, req_roles = check_access([u for u in units if isinstance(u.req, dict)])
    for u in units:
        if u.problems:
            u.status = "problems"
            continue
        u.status = "exists" if u.existing else "new"
        have = bf.rest_access_on(u.existing["BusinessUnitName"], user) if u.existing else []
        u.access = [{"role": rn, "code": c, "status": "already there" if any(
            r.get("RoleCommonName") == c and r.get("SecurityContext") == bf.SECURITY_CONTEXT
            and r.get("ActiveFlag") is True for r in have) else "will be added"} for rn, c in req_roles]
    return units, user, req_roles, lists


def will_get(u):
    """What Oracle will get for a new business unit, in the screen's words."""
    return {"Name": u.name, "Location": u.location["name"] if u.location else "(none)",
            "Manager": u.manager["name"] if u.manager else "(none)",
            "Default Set": f"{u.set[1]} ({u.set[0]})" if u.set else None,
            "Active": "Yes" if u.active else "No"}


def plan_text(u, user):
    if u.status == "problems":
        return " ".join(p["reason"] for p in u.problems) + " Nothing will be sent for it."
    add = [a["role"] for a in u.access if a["status"] == "will be added"]
    had = [a["role"] for a in u.access if a["status"] == "already there"]
    acc = (f"{' and '.join(add)} access for {user} will be added" if add else "") + \
          ("; " if add and had else "") + (f"{' and '.join(had)} access is already there" if had else "")
    if u.status == "exists":
        lead = f"Already in Oracle as '{u.existing['BusinessUnitName']}'; it is not changed. "
        return lead + (acc + "." if add else "Nothing to do: " + acc + ".") + \
            ("" if not u.notes else " " + " ".join(u.notes))
    g = will_get(u)
    return (f"New: {g['Name']} at {g['Location']}, manager {g['Manager']}, default set {g['Default Set']}, "
            f"active {g['Active'].lower()}; then {acc}.")


# ---------------------------------------------------------------- files sent to and read from Oracle

def csv_rows(zip_bytes, name):
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    member = next((n for n in z.namelist() if n.endswith(name)), None)
    if member is None:
        return []
    return list(csv.DictReader(io.StringIO(z.read(member).decode("utf-8-sig"))))


def export_zip(tag):
    """One Manage Business Unit export (read-only), kept in _work while the run lasts."""
    proc_url, _ = oracle.process_urls("Export", TASK, 0)
    r = oracle.call("POST", proc_url, json={"TaskCode": TASK})
    pid = r.json().get("ProcessId")
    _, result_url = oracle.process_urls("Export", TASK, pid)
    res = oracle.poll_result(result_url, f"read {tag}")
    if res.get("StatusCode") != "COMPLETED":
        oracle.fail(f"Oracle's Manage Business Unit export ended {res.get('StatusCode')}.")
    data = oracle.call("GET", f"{result_url}/enclosure/FileContent").content
    if oracle.WORK_DIR is not None:
        (oracle.WORK_DIR / f"export_{tag}_{pid}.zip").write_bytes(data)
    return data


def bu_row(u):
    row = dict(bf.BU_FIXED, Name=u.name, DefaultSetCode=u.set[0],
               InternalLocationCode=u.location["code"] if u.location else "",
               LocationSetCode=u.location["set"] if u.location else "",
               Status="A" if u.active else "I")
    m = u.manager
    if m:
        row.update(ManagerListName=m["name"], PersonNumber=m["person_number"], FirstName=m["first"],
                   LastName=m["last"], MiddleNames="", EffectiveStartDate3=m["start"], EffectiveEndDate3=m["end"])
    return row


def build_zip(rows):
    """Every file of the task once; every file header-only except the business unit file, which holds
    only the new rows (nothing that exists is in it). Headers: bu_import_template.json."""
    files = bf.load_template()
    if files is None:
        files = bf.read_zip(io.BytesIO(export_zip("template")))
        bf.save_template(files)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for name, f in files.items():
            if "header" not in f:
                zo.writestr(name, f["raw"])
                continue
            body = f["head_line"] + "\n"
            if name == bf.BU_CSV:
                body += "".join(bf.csv_line(f["header"], r) for r in rows)
            zo.writestr(name, body.encode("utf-8"))
    return buf.getvalue()


def send(zip_bytes):
    """The new rows to Oracle in one Setup task process; an ending with errors doesn't stop the run.
    Returns (status, Oracle's log texts)."""
    proc_url, _ = oracle.process_urls("Import", TASK, 0)
    r = oracle.call("POST", proc_url, json={"TaskCode": TASK, "FileContent": base64.b64encode(zip_bytes).decode(),
                                            "SourceTargetDiffOkFlag": True})
    pid = r.json().get("ProcessId")
    if pid is None:
        oracle.fail(f"Oracle gave no process number for the business units:\n{r.text[:500]}")
    print(f"  process {pid}")
    _, result_url = oracle.process_urls("Import", TASK, pid)
    result = oracle.poll_result(result_url, "business units")
    status = result.get("StatusCode")
    texts = []
    for link in result.get("links", []):
        if link.get("rel") == "enclosure" and link.get("name") in ("ProcessLog", "ProcessResultsReport",
                                                                    "ProcessResultsSummaryReport"):
            rr, err = oracle.try_call("GET", link["href"], timeout=180)
            if err or rr is None:
                continue
            path = oracle.WORK_DIR / f"{TASK}_{pid}_{link['name']}"
            path.write_bytes(rr.content)
            texts += unpack(rr.content)
    return status, pid, texts


def unpack(data):
    if data[:2] == b"PK":
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
            return [z.read(n).decode("utf-8", "replace") for n in z.namelist()]
        except zipfile.BadZipFile:
            return []
    return [data.decode("utf-8", "replace")]


# Oracle's attribute names in its messages -> the screen's field (request key, label)
ATTRS = {"DefaultSetCode": ("default_set", "Default Set"), "InternalLocationCode": ("location", "Location"),
         "LocationCode": ("location", "Location"), "LocationSetCode": ("location", "Location"),
         "ManagerListName": ("manager", "Manager"), "PersonNumber": ("manager", "Manager"),
         "Name": ("name", "Name"), "Status": ("active", "Active")}


def log_failures(texts):
    """The failed rows in Oracle's process log: [{"reasons": [plain text], "field", "raw"}]. The log
    names a failed row only by Oracle's internal key, never by the business unit name (2026-10-26,
    ZZ_TEST_BU_3138_B2BAD): "Row Identifier: <ids>. Status: Error. ... Message Text: ... JBO-25072:
    Applying List binding LOV_DefaultSetCode with given set of values leads to no matching row ...
    JBO-27014: Attribute OrgInformation4 in BusinessUnitDetailEO is required." """
    out = []
    for text in texts:
        flat = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\t", " ").replace("\\/", "/")
        for blk in flat.split("Row Identifier: ")[1:]:
            head, _, body = blk.partition("Message Text:")
            if "Status: Error" not in head:
                continue
            body = body.split("Total Objects", 1)[0]
            raw = " ".join(body.split())
            reasons, field = [], None
            for attr in re.findall(r"LOV_(\w+) with given set of values leads to no matching row", raw):
                key, label = ATTRS.get(attr, (None, attr))
                field = field or key
                reasons.append(f"Oracle has no matching value for {label}")
            for attr in re.findall(r"JBO-27040: Value .*? for field (\w+) exceeds the maximum length allowed", raw):
                key, label = ATTRS.get(attr, (None, attr))
                field = field or key
                reasons.append(f"{label} is longer than Oracle allows" + (f" ({NAME_MAX} characters)" if attr == "Name" else ""))
            for attr, _obj in re.findall(r"JBO-27014: Attribute (\w+) in (\w+) is required", raw):
                if not reasons:                 # alone it is the reason; after a list error it follows from it
                    key, label = ATTRS.get(attr, (None, attr))
                    field = field or key
                    reasons.append(f"Oracle says {label} is required")
            for code, msg in re.findall(r"(JBO-\d+|FND-\d+|FUN-\d+): (.*?)(?=JBO-\d+|FND-\d+|FUN-\d+|$)", raw):
                if code in ("JBO-25026", "JBO-25072", "JBO-27024", "JBO-27014", "JBO-27040"):
                    continue
                reasons.append(f"{msg.strip(' .')} ({code})")
            if not reasons:
                reasons = [raw[:300] or "Oracle gave no reason"]
            out.append({"reasons": list(dict.fromkeys(reasons)), "field": field, "raw": raw[:1500]})
    return out


def group_refusal(texts):
    """Oracle's refusal of the WHOLE group, named on the business object, not on a row (2026-10-26:
    a name Oracle already has with other capitals gave "Status details: JBO-27023: Failed to validate
    all rows in a transaction." and NOTHING of the group was saved, not even the good rows)."""
    for text in texts:
        m = re.search(r"Business object: Business Unit\. Status: Completed with errors\. Status details: "
                      r"(JBO-\d+): ([^.\\]*)", text)
        if m:
            return f"{m.group(2).strip()} ({m.group(1)})"
    return None


# ---------------------------------------------------------------- create, verify, access

def verify_rows(units, after_rows):
    """Second export: each saved business unit's row exactly as sent. {name: [differences]}."""
    got = {r["Name"]: r for r in after_rows}
    out = {}
    for u in units:
        row, want = got.get(u.name), bu_row(u)
        if row is None:
            out[u.name] = ["not in Oracle's Manage Business Unit export"]
            continue
        keys = ("DefaultSetCode", "InternalLocationCode", "LocationSetCode", "Status", "ManagerListName",
                "PersonNumber", "EffectiveStartDate3", "EffectiveEndDate3")
        out[u.name] = [f"{k}: Oracle has '{row.get(k, '')}', sent '{want.get(k, '')}'"
                       for k in keys if (row.get(k) or "") != (want.get(k) or "")]
    return out


def give_access(u, name, user, progress=None):
    """The missing required access rows on the business unit, each read back (exactly one active
    row). Returns ([added], [already], [(role, reason)])."""
    added, had, missing = [], [], []
    for a in u.access:
        it = {"user": user, "role_name": a["role"], "code": a["code"], "b": {"name": name}}
        rows = [r for r in bf.rest_access_on(name, user) if bf.is_mine(r, [it])]
        if rows:
            had.append(a["role"])
            continue
        if progress:
            progress.step("access", 80, f"Giving {a['role']} access on {name}")
        try:
            bf.rest_create_access(it)
        except bf.RestUnavailable as e:
            missing.append((a["role"], bf.oracle_reason(str(e))))
            continue
        rows = [r for r in bf.rest_access_on(name, user) if bf.is_mine(r, [it])]
        if len(rows) == 1 and rows[0].get("ActiveFlag") is True:
            added.append(a["role"])
        else:
            missing.append((a["role"], "Oracle doesn't show it after saving"))
    return added, had, missing


def create(units, user, lists, progress):
    """New business units in one go, read back, then the access. Returns {name: outcome}."""
    new = [u for u in units if u.status == "new"]
    out = {}
    if new:
        before = {b["BusinessUnitId"]: b for b in lists.bus(fresh=True)}
        clash = [u for u in new if any(b["BusinessUnitName"].lower() == u.name.lower() for b in before.values())]
        for u in clash:          # made by someone else since the check: never sent
            u.status, u.existing = "exists", next(b for b in before.values()
                                                  if b["BusinessUnitName"].lower() == u.name.lower())
            u.notes.append("It appeared in Oracle after the check, so it was not sent.")
        new = [u for u in new if u.status == "new"]
    if new:
        progress.step("creating", 40, f"Creating {len(new)} business unit{'s' if len(new) != 1 else ''} in one go")
        print(f"Sending {len(new)} new business unit row(s): {', '.join(u.name for u in new)}")
        zip_bytes = build_zip([bu_row(u) for u in new])
        (oracle.WORK_DIR / "business_units_sent.zip").write_bytes(zip_bytes)
        status, pid, texts = send(zip_bytes)
        fails = log_failures(texts) if status != "COMPLETED" else []
        group = group_refusal(texts) if status != "COMPLETED" and not fails else None
        print(f"  Oracle: {status}" + (f"; failed rows in Oracle's log: {[f['raw'] for f in fails]}" if fails else ""))
        progress.step("checking_bu", 55, "Reading the business units back from Oracle")
        after = lists.bus(fresh=True)
        by_id = {b["BusinessUnitId"]: b for b in after}
        # every business unit that was there before is unchanged (all users' data)
        keys = ("BusinessUnitName", "ActiveFlag", "LocationId", "ManagerId", "PrimaryLedgerId", "LegalEntityId",
                "ProfitCenterFlag")
        changed = [b["BusinessUnitName"] for i, b in before.items()
                   if i not in by_id or any(by_id[i].get(k) != b.get(k) for k in keys)]
        saved = []
        gone = [u for u in new if not any(b["BusinessUnitName"] == u.name and b["BusinessUnitId"] not in before
                                          for b in after)]
        for u in new:
            hits = [b for b in after if b["BusinessUnitName"] == u.name and b["BusinessUnitId"] not in before]
            if not hits:
                # The log names no business unit: with one missing business unit and one failed row the
                # reason is that row's; with several, every reason is given and it is said plainly that
                # Oracle doesn't tell which row is which (never guessed).
                if len(gone) == 1 and len(fails) == 1:
                    why, field = fails[0]["reasons"], fails[0]["field"]
                elif group:
                    why = [f"Oracle refused the whole group sent together, so none of it was saved: {group}. "
                           "In the tests this came from a name Oracle already has with other capitals"]
                    field = "name"
                elif fails:
                    why = [f"Oracle refused {len(fails)} of the {len(new)} business units sent together without "
                           "saying which is which; its reasons: " + " | ".join("; ".join(f["reasons"]) for f in fails)]
                    field = fails[0]["field"] if len({f["field"] for f in fails}) == 1 else None
                else:
                    why, field = (["Oracle ended with errors and doesn't name a reason for it"] if status != "COMPLETED"
                                  else ["Oracle doesn't show it after saving"]), None
                out[u.name] = {"saved": False, "reasons": why, "field": field}
                continue
            b = hits[0]
            diffs = []
            if b.get("ActiveFlag") is not u.active:
                diffs.append(f"Active: Oracle has {b.get('ActiveFlag')}, sent {u.active}")
            if (b.get("LocationId") or None) != (u.location["id"] if u.location else None):
                diffs.append(f"Location: Oracle has id {b.get('LocationId')}, sent {u.location and u.location['id']}")
            if int(b.get("ManagerId") or 0) != (u.manager["person_id"] if u.manager else 0):
                diffs.append(f"Manager: Oracle has person id {b.get('ManagerId')}, sent "
                             f"{u.manager['person_id'] if u.manager else 'none'}")
            out[u.name] = {"saved": True, "item": b, "diffs": diffs, "reasons": []}
            saved.append(u)
        if changed:
            print(f"  FAIL  other business units changed: {changed}")
            for u in saved:
                out[u.name]["diffs"].append(f"other business units look different afterwards: {', '.join(changed[:5])}")
        if saved:
            progress.step("checking_bu", 62, "Checking every value of the new business units")
            rows = csv_rows(export_zip("after"), bf.BU_CSV)
            for name, d in verify_rows(saved, rows).items():
                out[name]["diffs"] += d
                row = next((r for r in rows if r["Name"] == name), {})
                out[name]["row"] = {k: row.get(k) for k in ("Name", "DefaultSetCode", "InternalLocationCode",
                                                            "LocationSetCode", "Status", "ManagerListName",
                                                            "PersonNumber", "OrganizationCode")}
        for name, o in out.items():
            print(f"  {'OK  ' if o['saved'] and not o.get('diffs') else 'FAIL'}  {name}: "
                  + ("saved" + (f", differs: {o['diffs']}" if o.get("diffs") else ", every value as sent")
                     if o["saved"] else f"NOT SAVED: {'; '.join(o['reasons'])}"))
    # access: new and saved exactly as sent, and existing business units
    for u in units:
        if u.status == "exists":
            name = u.existing["BusinessUnitName"]
            out[u.name] = {"saved": False, "existing": True}
        elif u.status == "new" and out.get(u.name, {}).get("saved") and not out[u.name].get("diffs"):
            name = u.name
        else:
            continue
        added, had, missing = give_access(u, name, user, progress)
        out[u.name].update(added=added, had=had, missing=missing, oracle_name=name)
        for r in added:
            print(f"  OK    {name}: {r} access for {user} added and read back")
        for r, why in missing:
            print(f"  FAIL  {name}: {r} access for {user} missing: {why}")
        active = u.active if u.status == "new" else u.existing.get("ActiveFlag") is not False
        if not missing and (added or u.status == "new") and not active:
            print(f"  NOTE  {name} is inactive: no pricing check, not written to {bf.REGISTRY.name}")
        elif not missing and (added or u.status == "new"):
            progress.step("pricing", 90, f"Checking that {name} shows for pricing")
            items = [{"user": user, "role_name": a["role"], "code": a["code"], "b": {"name": name}} for a in u.access]
            ready = all(bf.wait_for_pricing(it) for it in items)
            if name.upper().startswith(TEST_PREFIX):
                print(f"  NOTE  {name} is test data: not written to {bf.REGISTRY.name}")
            else:
                bf.registry_add(name, "ready" if ready else "pending", "" if ready else bf.FRESH_SIGNIN_TEXT,
                                user, [a["role"] for a in u.access])
            out[u.name]["pending"] = not ready
    return out


# ---------------------------------------------------------------- results

def failed(code, text, saved, problems=None, message=None):
    return {"ok": False, "text": text, "error": {"code": code, "detail": {
        "message": message, "saved": saved, "registry_id": None, **({"problems": problems} if problems else {})}}}


def result_of(u, o, user):
    """One --run style result per requested business unit."""
    where = WHERE.format(name=u.name)
    if u.status == "problems":
        return failed("INVALID_REQUEST", " ".join(p["reason"] for p in u.problems) + " Nothing was sent for it.",
                      "no", problems=u.problems)
    o = o or {}
    access_txt = lambda xs: " and ".join(xs)
    if u.status == "exists":
        name = u.existing["BusinessUnitName"]
        if o.get("missing"):
            return failed("FAILED", f"The business unit {name} was already in Oracle and wasn't changed; access "
                          f"missing: {'; '.join(f'{r} ({w})' for r, w in o['missing'])}. A rerun adds only what is "
                          "missing.", "yes", message=json.dumps(o["missing"]))
        if o.get("added"):
            return {"ok": True, "where": where, "text": f"The business unit {name} was already in Oracle and wasn't "
                    f"changed; {user} was missing {access_txt(o['added'])} access on it. Added: "
                    f"{access_txt(o['added'])} access." + (" " + " ".join(u.notes) if u.notes else ""),
                    "created": {"business_unit": name, "access_added": o["added"], "access_had": o.get("had", [])}}
        return {"ok": True, "skipped": True, "where": where,
                "text": f"The business unit {name} is already in Oracle with {access_txt(o.get('had') or [])} access "
                        f"for {user}, so nothing was changed." + (" " + " ".join(u.notes) if u.notes else ""),
                "created": {"business_unit": name}}
    if not o.get("saved"):
        why = "; ".join(o.get("reasons") or ["Oracle gave no reason"])
        return failed("INVALID_REQUEST", f"Oracle didn't save the business unit {u.name}: {why}. Nothing of it was "
                      "saved, so no access was given; a rerun sends only what is missing.", "no",
                      problems=[{"business_unit": u.name, "field": o.get("field"), "value": value_of(u, o.get("field")),
                                 "reason": why, "suggestions": suggestions_for(u, o.get("field")),
                                 "fix": "Please correct it in the sheet."}],
                      message=why)
    if o.get("diffs"):
        return failed("VERIFY_FAILED", f"The business unit {u.name} was saved, but Oracle shows it differently: "
                      f"{'; '.join(o['diffs'])}. No access was given.", "yes", message="; ".join(o["diffs"]))
    if o.get("missing"):
        return failed("FAILED", f"Business unit {u.name} saved and checked, access missing: "
                      f"{'; '.join(f'{r} ({w})' for r, w in o['missing'])}. A rerun adds only the missing access.",
                      "yes", message=json.dumps(o["missing"]))
    g = will_get(u)
    text = (f"Created the business unit {u.name} (location {g['Location']}, manager {g['Manager']}, default set "
            f"{g['Default Set']}, active {g['Active'].lower()}) and gave {user} {access_txt(o.get('added') or [])} "
            "access on it. Saved and checked in Oracle, every value as sent.")
    if o.get("pending"):
        text += f" {bf.FRESH_SIGNIN_TEXT} Sign out of Oracle and sign in again."
    return {"ok": True, "where": where, "text": text,
            "created": {"business_unit": o.get("row"), "BusinessUnitId": o["item"].get("BusinessUnitId"),
                        "access_added": o.get("added"),
                        "pricing": "not checked: inactive" if not u.active else
                        "pending" if o.get("pending") else "ready"}}


def value_of(u, field):
    """The value as the row gave it (the default when it was left out)."""
    if field == "location":
        return u.location["name"] if u.location else None
    if field == "default_set":
        return u.set[0] if u.set else u.req.get("default_set")
    if field == "manager":
        return u.manager["name"] if u.manager else None
    return u.req.get(field) if field else None


SUGGEST = {}         # field -> Oracle's own list, read once per run


def suggestions_for(u, field):
    """Suggested values from Oracle's own lists for a refused value (the page asks the user with them)."""
    try:
        if field == "default_set":
            if "default_set" not in SUGGEST:
                SUGGEST["default_set"] = [s["SetCode"] for s in bf.rest_all(f"{oracle.API_BASE}/setIdSetsLOV",
                                                                            "reference data sets")]
            return close(value_of(u, field) or "", SUGGEST["default_set"]) or SUGGEST["default_set"][:12]
        if field == "location":
            if "location" not in SUGGEST:
                SUGGEST["location"] = sorted({l["LocationName"] for l in bf.rest_all(
                    f"{bf.HCM_BASE}/locations", "locations", fields="LocationName,ActiveStatus")
                    if l.get("ActiveStatus") == "A"}, key=str.lower)
            return close(value_of(u, field) or "", SUGGEST["location"]) or SUGGEST["location"][:12]
        if field == "manager":
            return [m["name"] for m in MANAGERS]
    except bf.RestUnavailable:
        pass
    return []


def read_requests(arg):
    raw = json.loads(Path(arg).read_text(encoding="utf-8") if arg.endswith(".json") and Path(arg).exists() else arg)
    if isinstance(raw, dict) and "business_units" in raw:
        raw = raw["business_units"]
    return raw if isinstance(raw, list) else [raw]


def found_notes(u):
    """Yellow notes per field for the sheet's preview."""
    out = {}
    if u.existing and u.existing["BusinessUnitName"] != u.name:
        out["name"] = (f"Oracle already has '{u.existing['BusinessUnitName']}', which differs only in capitals. Oracle "
                       "treats it as the same business unit, so this row is skipped and never sent (if it were sent, "
                       "Oracle would refuse it and drop every business unit sent with it). Only missing access is added.")
    elif u.existing:
        out["name"] = ("Already exists in Oracle: it will be skipped and not changed; only missing access would be "
                       "added.")
    if u.existing and any(n.startswith("It already exists, so the values") for n in u.notes):
        out.setdefault("location", "Not applied: the business unit already exists and is never changed.")
    return out


def oracle_values(u):
    """What Oracle will get per field, in the screen's words (new business units only)."""
    if u.status != "new":
        return {}
    return {"name": u.name,
            "location": (f"{u.location['name']} (code {u.location['code']}, set {u.location['set']})"
                         if u.location else "(none)"),
            "manager": (f"{u.manager['name']} (person number {u.manager['person_number']})" if u.manager else "(none)"),
            "default_set": f"{u.set[0]} ({u.set[1]})" if u.set else None,
            "active": "Yes" if u.active else "No"}


def plan_command(argv):
    """--plan '<JSON>' (read-only): one JSON line {"ok", "results": [{"name", "status": "new" | "exists" |
    "problems", "problems": [{"business_unit", "field", "value", "reason", "suggestions", "fix"}],
    "access", "oracle_will_get", "notes", "summary", "skipped"}], "text"}."""
    out = sys.stdout
    try:
        reqs = read_requests(argv[1] if len(argv) > 1 else str(HERE / "request.json"))
    except (ValueError, OSError) as e:
        print(json.dumps({"ok": False, "text": f"The request couldn't be read ({e})."}), file=out)
        return 2
    with contextlib.redirect_stdout(sys.stderr):
        oracle.check_environment()
        oracle.init_work_dir(HERE)
        try:
            units, user, _, _ = plan(reqs)
        except (SystemExit, bf.RestUnavailable) as e:
            from common import browser
            print(json.dumps({"ok": False, "text": browser.failed_step_text(   # the real failed step (2026-10-26)
                "Oracle couldn't be checked just now."), "detail": str(e)[:500]}), file=out)
            return 1
        oracle.cleanup_work_dir()
    # For the upload sheet (page/server.py apply_oracle_check): "ok" = the check ran; problems also carry
    # "key" / "text"; "found" = yellow notes on a field; "oracle" = what Oracle will get per field.
    results = [{"name": u.name, "ok": True, "status": u.status,
                "problems": [dict(p, key=p["field"], text=p["reason"]) for p in u.problems],
                "access": u.access, "notes": u.notes,
                "oracle_name": u.existing["BusinessUnitName"] if u.existing else None,
                "oracle_will_get": will_get(u) if u.status == "new" else None,
                "found": found_notes(u), "oracle": oracle_values(u),
                "summary": plan_text(u, user) if u.status != "problems" else None,
                "skipped": plan_text(u, user) if u.status == "exists" else None} for u in units]
    c = collections.Counter(u.status for u in units)
    text = (f"{c['new']} new, {c['exists']} already in Oracle, {c['problems']} with problems "
            "(nothing was changed in Oracle).")
    print(json.dumps({"ok": not c["problems"], "text": text, "results": results}, ensure_ascii=False), file=out)
    return 0


def run_batch_command(argv):
    """--run-batch '<JSON list>': every business unit of an upload in one call. Progress lines as --run,
    then {"step": "result", "ok", "text", "results": [one result per request, in order]}."""
    out = sys.stdout
    progress = page.Progress(out)
    try:
        reqs = read_requests(argv[1] if len(argv) > 1 else "")
    except (ValueError, OSError) as e:
        print(json.dumps({"step": "result", "percent": 100, "ok": False, "text": "The request could not be read.",
                          "error": {"code": "INVALID_REQUEST", "step": "reading", "detail": str(e)}}), file=out)
        return 2
    t0 = time.time()
    top_error, outcome, units, user = None, {}, [], None
    with contextlib.redirect_stdout(sys.stderr):
        oracle.check_environment()
        bf.browser.refuse_production()
        oracle.init_work_dir(HERE)
        messages, real_fail = [], oracle.fail

        def fail(message):
            messages.append(str(message))
            real_fail(message)
        oracle.fail = fail
        try:
            progress.step("checking", 20, "Checking every business unit with Oracle")
            units, user, _, lists = plan(reqs)
            for u in units:
                print(f"  {u.name}: {plan_text(u, user)}")
            outcome = create(units, user, lists, progress)
        except (SystemExit, Exception) as e:  # noqa: BLE001 - answered per business unit below
            msg = messages[-1] if messages else f"{type(e).__name__}: {e}"
            top_error = {"code": page._classify(msg), "step": "creating", "detail": msg[:1500]}
            print(f"STOPPED: {msg[:1500]}")
        finally:
            oracle.fail = real_fail
        results = []
        for i, r in enumerate(reqs):
            u = units[i] if i < len(units) else Unit(r, i)
            if top_error and u.status != "problems" and u.name not in outcome:
                saved = "maybe" if u.status == "new" else "no"
                results.append(failed(top_error["code"], page.ERRORS.get(top_error["code"], page.ERRORS["FAILED"])
                                      + (" It may have been saved in Oracle; a rerun skips what is saved."
                                         if saved == "maybe" else " Nothing was changed for it."), saved,
                                      message=top_error["detail"]))
            else:
                results.append(result_of(u, outcome.get(u.name), user))
        progress.step("done")
    made = [u.name for u, r in zip(units, results) if r["ok"] and not r.get("skipped")]
    saved_bad = [u.name for u, r in zip(units, results) if not r["ok"] and r["error"]["detail"].get("saved") == "yes"]
    skipped = sum(1 for r in results if r.get("skipped"))
    bad = sum(1 for r in results if not r["ok"])
    text = (f"Done {len(made)} of {len(results)} business units" + (f", {skipped} already there" if skipped else "")
            + (f", {bad} not done" if bad else "") + ".")
    if bad and (made or saved_bad):
        text += " Saved in Oracle: " + ", ".join(made + saved_bad) + "."
    print(f"Whole run: {bf.elapsed_text(time.time() - t0)}", file=sys.stderr)
    if not bad and not top_error:
        oracle.cleanup_work_dir()
    line = {"step": "result", "percent": 100, "ok": not bad, "text": page.plain_check(text, "result"),
            "results": results}
    if top_error:
        line["error"] = top_error
    print(json.dumps(line, ensure_ascii=False, default=str), file=out)
    return 0 if not bad else 1
