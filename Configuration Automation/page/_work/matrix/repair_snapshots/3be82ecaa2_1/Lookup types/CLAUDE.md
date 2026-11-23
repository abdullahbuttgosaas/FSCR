# Manage Standard Lookups

Task code: `FND_MANAGE_STANDARD_LOOKUPS`
Status summary (2026-10-25): **everything Manage Standard Lookups can create is PROVEN** by
real runs (ZZ_TEST_LK_8806_*): new lookup types with every field and their codes (one CSV
import for all new types of a run), new codes on existing User and Extensible types (REST, as
the Order Types folder), modules by NAME, every value read back through REST with "Saved: ... /
Not saved: X (Oracle's reason)". Read-only `--plan`. Field reference for an upload sheet:
`sheet_fields.md`.

## Input rules

Check every request against this before doing any work (root CLAUDE.md > Input rules).
`python "Lookup types/run.py" --plan <file or JSON>` checks a request read-only (every rule,
Oracle's state, modules) and says what a run would do.

REQUIRED - if missing or unclear, stop and ask in plain words, all missing items in one message:
- Lookup Type (max 30). For a **new** type: Meaning (max 80, unique among lookup types) and
  Module (its NAME as Oracle shows it). An existing type needs only its name.
- At least one code with Lookup Code (max 30) and Meaning (max 80).

OPTIONAL - if missing, the screen's default:

| Field | Default |
|---|---|
| Item Description (type) | empty |
| REST Access Secured | Secure (the screen's default, seen 2026-10-25) |
| Code Item Description | empty |
| Enabled | yes |
| Start Date / End Date | empty |
| Display Sequence | empty |
| Tag | empty |

Lookup Configuration Level is always **User** for a new type (shown on the screen, can't be
changed). An existing type is never changed: its meaning, description, module and access stay
as they are; a request's different values only give a note.

Dates: `YYYY-MM-DD` or `"today"` = Oracle's today (REST `Date` header) minus one day.

## Field rules (all checked before anything is sent, all problems at once)

Proven by real runs on 2026-10-25 unless marked otherwise. Oracle drops the WHOLE type when one
of its rows is refused in the import (batch B: a 31-character code also lost F1 and F3 of type
B2; B1 and B3 in the same file were saved).

| Rule | Oracle's behaviour / message |
|---|---|
| Lookup Type required, max 30 | REST describe; screen box holds 30 |
| New type name: no small letters | refused, whole type dropped: "JBO-25017: New entity row of type LookupEO__DefCustomizer__ cannot be created" (ZZ_TEST_LK_8806_lower). No plainer reason in the log. |
| New type name: not starting with ORA | refused the same way (ORA_ZZ_TEST_LK_8806); Oracle's docs say ORA is kept for its own lookups |
| Spaces, "-" and "." in a type name | **accepted** (ZZ_TEST_LK_8806 SPACE, ZZ_TEST_LK_8806-DASH.DOT; Oracle's own "2003 SIC") |
| Type meaning unique | screen at once and import: "Another lookup type already has the same meaning. (FND-7104)" (ZZ_TEST_LK_8806_TMEAN dropped) |
| Item Description max 240, Tag max 150, Meaning max 80 | REST describe / screen boxes |
| Module: an Oracle module name | the screen's Module dialog (see Modules); unknown name -> close matches |
| REST Access Secured: Secure, Authenticated, Anonymous | the screen's drop-down; codes SECURE, AUTH, ANON (all three proven) |
| Code listed twice in one type | folder rule: Oracle **silently keeps the last row** in an import (ZZ_TEST_LK_8806_DUPCODE: X1 got the second row's meaning "Two"); REST refuses an existing code: "Too many objects match the primary key ... [type A1 ...]" |
| Code meaning twice in one type (capitals count) | "Lookup Type X already has lookup code meaning Same. (FND-7103)" on the screen, in the import (MEAN2 dropped) and through REST (HTTP 400) |
| Code meaning against the existing codes of an existing type | checked through REST before sending (FND-7103) |
| Code with small letters and spaces | **accepted** ("my code x", "p 2"; Oracle's own "My Mansion") |
| End Date not before Start Date | import: "Start Date must be before End Date" (ENDB4 dropped). The same day for both is in Oracle's data (not re-tried) |
| Display Sequence whole number, 0 or more | "abc" refused: "Cannot create an object of type:java.lang.Long from type:java.lang.String with value:abc" (SEQTXT dropped). **-1 was accepted by Oracle** (ZZ_TEST_LK_8806_SEQNEG); "0 or more" is the folder's rule (asked for), 0 proven |
| Enabled yes/no | yes default; No proven (B2, H1, "p 2") |
| System type: no new codes | the folder refuses before sending (no POST was tried against a System type on purpose) |
| Extensible type: new codes yes, Oracle's codes unchanged | proven: ZZ_TEST_LK_8806 added to ORA_DGV_SERVICE_TYPE, its 2 codes and the type unchanged |
| An existing type re-sent in the import | Oracle merged it (ZZ_TEST_LK_8806_ANON with identical values: no error, LastUpdateDate unchanged). With different values it would change the type, so the folder NEVER puts an existing type in the import (existing types only get new codes through REST) |
| Number of codes in a type | 1000 accepted in one import (ZZ_TEST_LK_8806_MANY); no maximum found |

## Route status

- **New types: CSV import PROVEN** (`setupTaskCSVImports`, rows built from a fresh export's
  column headers, CustomizationLevel U). Several types per import PROVEN (3, then 12). An import
  that ends COMPLETED_ERRORS no longer stops the run blind: Oracle's ProcessLog is saved and read
  (`log_errors()`: per failed type Oracle's reason, e.g. FND-7103 / FND-7104 / "Start Date must
  be before End Date"; the code it names is not always the bad one), then everything is read back.
- **New codes on existing User / Extensible types: REST PROVEN** (POST to the type's
  `lookupCodes` link, one per code, HTTP 201, read back by GET; existing codes and the type
  unchanged). About 2 seconds per code.
- **Read-back: REST** for every type and code sent (fields compared; dates as YYYY-MM-DD).
- **Modules by name: screen + REST PROVEN** (see Modules).
- Package route (Manage Configuration Packages, XML): not used any more (kept as reference).

## Modules

The request gives the module NAME. Oracle's REST has only a 32-character ModuleId (no names, no
list; taxonomyNodes gives HTTP 401). So:
1. The name is searched in the screen's Module dialog (Manage Standard Lookups > Search > Module
   > Search...; Oracle matches the start of the name; columns User Module Name, Module Type,
   Module Key). The dialog shows **at most 500 rows** (seen 2026-10-25: an empty search stopped at
   "BG Payroll Balances"), so the whole list can't be read; names are looked up one by one.
   Exact name, else one case-insensitive match; otherwise "Oracle has no module called 'X'. Close
   matches: ..." (e.g. "Order Managment" -> Order Management, Order Promising, ...).
2. Some names exist more than once (e.g. "Absence Management": Module Keys ANC, HcmAbsMgmtTop,
   HcmAbsMgmtAbsences): refused in plain words (not supported yet).
3. The ID is learned from a lookup that already uses the module: the screen's search by Module
   lists them, REST gives that lookup's ModuleId. A module no lookup uses can't be resolved
   (plain message; not proven otherwise).
4. Everything found is cached in `modules.json` (name, type, key, ID), so a module is looked up
   once (about 60 s for a few modules). `python "Lookup types/run.py" --modules "Name" ...` looks
   names up and shows the cache.
Task location: Manage Standard Lookups is in Application Extensions, which the offerings'
Search Tasks don't search; the script opens it through Setup and Maintenance > Tasks panel >
Search (`open_lookups_screen()`). Every screen visit only reads and leaves with Cancel.

### Module list (name -> ModuleId)

| Module name | ModuleId | Source |
|---|---|---|
| Order Management | EDC7E0B04D5D8CD9E040F00A172014AD | given by the user, 2026-10-15 (module of ZZ_POC_TEST, created in the UI) |

(Names the user gave; the script reads this table and `modules.json`. Proven by creates: Order
Management, Concepts (C64FF81360AA6C68E040F00A17206780), Oracle Middleware Extensions for
Applications (40B3FA7250D19380E040449823C67A1A).)

## How to do it

From the project root:

```
python "Lookup types/run.py" --plan [lookups.json | '<JSON>']   # read-only: what a run would do
python "Lookup types/run.py"                  # full run (lookups.json)
python "Lookup types/run.py" --modules "Name" # look modules up (screen, read-only), show the cache
python "Lookup types/run.py" --check          # read-only: task flags + which types exist
python "Lookup types/run.py" --dry-run        # export + build the import zip, no import
```

Request file `Lookup types/lookups.json`:

```json
{"lookups": [{
  "lookup_type": "XX_MY_TYPE",          // required, max 30; new: capitals, not ORA...
  "meaning": "My type",                 // new type: required, max 80, unique
  "description": "...",                 // optional, max 240
  "module": "Order Management",         // new type: the module NAME (or "module_id")
  "rest_access_secured": "Secure",      // optional: Secure | Authenticated | Anonymous (or SECURE/AUTH/ANON)
  "codes": [{
    "code": "CODE1",                    // required, max 30 (small letters and spaces allowed)
    "meaning": "Code 1",                // required, max 80, unique in the type (capitals count)
    "description": "...",               // optional, max 240
    "enabled": true,                    // optional, default true
    "start_date": "2026-01-01",         // optional, YYYY-MM-DD or "today"
    "end_date": "2030-12-31",           // optional, not before start_date
    "display_sequence": 1,              // optional whole number, 0 or more
    "tag": "..."                        // optional, max 150
  }]
}]}
```

What `run.py` does:
1. Checks every rule that needs no Oracle (lengths, required, code twice, code meaning twice,
   dates, Display Sequence, access value).
2. `plan()`, read-only: for each type REST says whether it exists, its level and codes. Existing:
   System -> refused; User/Extensible -> new codes to add, existing codes skipped (exact code),
   code meanings checked against the existing ones. New: name rules, type meaning (REST
   `q=Meaning=`), module resolved (cache, else the screen).
3. New types: a fresh export for the column layout, one import for all of them
   (`import_keep_going()`); on COMPLETED_ERRORS the ProcessLog is saved and read.
4. New codes of existing types: one REST POST each (refusals kept with Oracle's message).
5. Read-back through REST of every type and code: "Saved: ... / Not saved or differs: ..." and
   Oracle's reasons; any miss stops the run (oracle.fail) saying exactly that. A rerun skips
   what is saved (existing type -> only missing codes; existing code -> skipped).
6. `_work/` deleted only after a verified run.
Never deletes or changes an existing lookup type or code.

`--plan` (read-only): one JSON line `{"ok", "results": [{"name", "status": "new" | "add_codes" |
"exists" | "problems", "level", "existing_codes", "add", "skip", "module", "problems": [{"key",
"row", "text", "fix"}], "notes", "summary", "skipped", "found", "fills"}]}`. A few seconds (plus
about 60 s the first time a module name is looked up).

## Page interface

Contract: root CLAUDE.md > Page interface (helper `common/page.py`). One lookup type per `--run`
(new, or new codes for an existing one).

| Key | Label | Required | Type |
|---|---|---|---|
| lookup_type | Lookup name | yes | text |
| meaning | Name shown to users | for a new lookup | text |
| module | Module | for a new lookup | pick (samples: modules proven by a create; `--all`: every module looked up so far) |
| codes | Codes | yes | rows: code, meaning, description, enabled, start_date, end_date, display_sequence, tag |
| description | Description | no | text |
| rest_access_secured | Who may read it from other programs | no | pick: Secure, Authenticated, Anonymous (default Secure) |

A stop says in `error.detail` `{"message", "saved", "registry_id"}`; a type Oracle refused gives
INVALID_REQUEST with Oracle's reason. Tried 2026-10-25: `--run` ZZ_TEST_LK_8806_PAGE (Concepts,
Anonymous, codes P1 with tag and position, "p 2" disabled with an end date): created, every value
read back; System type XCC_BC_FUNDS_STATUSES -> "XCC_BC_FUNDS_STATUSES is a System lookup type:
Oracle allows no new codes in it. Nothing will be sent."; a code twice -> "Code 2: Lookup Code
'A' is already listed as code 1.".

## Upload sheet (2026-10-25)

The page's upload sheet has two tabs for this folder (root CLAUDE.md > The upload sheet > Lookup
Types module): **Lookup Types** (new types) and **Lookup Codes** (codes, joined by Lookup Type
exactly). A code row whose type isn't on the Lookup Types tab is sent as `"existing_only": true`
(add these codes to a type Oracle already has).
- Preview: the page sends every entry to `--plan`. `existing_only` and the type doesn't exist ->
  "Lookup Type 'X' isn't a new type in this request and doesn't exist in Oracle, so its codes can't
  be added to it (names must match exactly: capitals and spaces count)."; System type -> refused;
  User / Extensible -> "N new codes will be added (...), M already exist and are skipped (...)".
  A type row that already exists -> "X already exists in Oracle (...), so it will be skipped;
  nothing is changed." (with codes: "its codes are added to the existing type"). A new type with
  no codes is allowed: "0 codes ... Not proven yet: this folder hasn't created a type without codes
  by the import."
- Create: `--run-batch '<JSON list>'` = every entry in one call: new types in one import, codes
  for existing types through REST, then one result per entry (created / codes added / already
  there / "Oracle refused the lookup type X: <reason>. When one code is refused Oracle drops the
  whole type ..." / saved but not matching). A stop with no answer per type gives a top-level
  error for the page's repair rules.
- Rule changes 2026-10-25: End Date must be AFTER Start Date (Oracle's words "Start Date must be
  before End Date"); a new type may have 0 codes (not proven by an import yet).
- Tested through the page, previews only (nothing created): `manual-notes/
  Lookup_Types_TEST_good.xlsx` (ZZ_SHEET_LK_7495_ALL, _CON, _ANON, "ZZ_SHEET_LK_7495 SPACE", and
  codes ZZ_SHEET_LK_1 / _2 for ORA_DGV_SERVICE_TYPE): ready in 13 s; `..._bad.xlsx`: 12 red
  problems (small letters, ORA, type meaning used, unknown module, module typo with close matches,
  code meaning twice, a type that exists nowhere, a System type, the order type list, Display
  Sequence -1, End Date before Start Date, a type twice) and the "0 codes" note; 58 s (two module
  names looked up on the screen). `--run-batch` and the page's one-call run tested offline only.

## Preview versus Create (2026-10-26)

Proven by real creates on 2026-10-26: Oracle's meaning and code checks are **exact (capitals count)**.
ZZ_TEST_LK_6142_TMEAN was created with the meaning "ZZ TEST LK 8806 B1" next to type ZZ_TEST_LK_8806_B1
("ZZ test LK 8806 B1"); in ZZ_TEST_LK_8806_ALL the code A2 with meaning "ALPHA" (next to A1 "Alpha") and
the code "a1" (next to "A1") were added. So FND-7103 / FND-7104 and the code key compare exactly, as this
folder already did.

Added to `--plan` and `--run-batch` (`upload_problems()`, `today_pairs()`):
- two NEW lookup types in one upload with the same meaning (exact): red on the second (FND-7104 would
  refuse it at import);
- End Date after Start Date also when one of them is "today" (resolved with Oracle's date).

**Still only at Create:** type names with characters beyond letters, digits, "_", space, "-", "."; codes
starting with ORA; lengths of multi-byte text; Display Sequence above Oracle's number limit. **Pause and ask (on since 2026-10-26):** refusals carry `detail.problems` (`refusal_problems()`,
`checked_problems()` for this folder's own stops right before sending): a meaning in use (FND-7103 per code,
FND-7104 per type; suggestions "<meaning> (<code>)", "<meaning> 2", ...), a code key clash, dates, Display
Sequence, a type name Oracle can't take (JBO-25017). A code's answer goes into that code row. Also fixed: every new
code of an existing type refused and none read back -> "Nothing was saved" (it said "may have been saved").
Proven 2026-10-26: code Z2 "Yankee 6142" in ZZ_TEST_LK_8806_ALL, meaning taken after the preview by code Y0 ->
asked ("Code 1 (Z2)", Lookup Codes row) -> "Yankee 6142 (Z2)" -> added and read back.

## Related folders

None noted. (The Order Types folder adds codes to ORA_DOO_ORDER_TYPES through the same REST
resource; the two folders don't share code.)

## Known gotchas

- 2026-10-26: `--run-batch` crashed ("'NoneType' object is not subscriptable") when the check step itself stopped
  before planning any type (seen: Oracle's host name couldn't be resolved, a passing network problem). Every type
  without an answer now gets a plain failure "Nothing was saved in Oracle." with the real reason, and the run's
  top-level error goes to the page's repair rules as before.

- 2026-10-26: **Lost clicks on Oracle's busy pages: every screen step checked and done again** with the shared
  retry helper `ui.retry()` (`common/browser.py`: up to 3 tries, a short pause and a fresh wait each time, then one
  clear failure "Oracle's <step> after 3 tries", which `--plan` passes to the page): the task search for Manage
  Standard Lookups (done again from a freshly opened Setup page), its link (the screen's Search and Module fields),
  the Module dialog (`ui.search_dialog()`) and its search (`ui.fresh_search()`: a lost Search kept the old rows),
  the search by Module, and leaving the screen (Cancel / Yes until it has closed). Nothing on this screen is saved.
- 2026-10-25: Oracle drops the whole lookup type when one of its rows fails in the import; the
  log names the type but may name the wrong code (a 31-character code was reported as "code F3:
  JBO-25013: Too many objects match the primary key").
- 2026-10-25: the import log (ProcessLog) is one line with written-out `\r\n`; reasons are inside
  `<NUMBER>FND-...</NUMBER><TEXT>...</TEXT>` or after `_Rule_0:`.
- 2026-10-25: the screen's Module dialog shows at most 500 rows; search by name.
- 2026-10-25: Manage Standard Lookups is not found by an offering's Search Tasks (Application
  Extensions isn't an enabled area); use the Tasks panel's Search.
- 2026-10-25: on the screen a new type's codes "+" stays greyed out until the type is saved; the
  import sends type and codes together, so this doesn't apply to the script.
- The import zip MUST contain all 3 files (`FND_APP_STANDARD_LOOKUP.csv`,
  `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv`, `ASM_SETUP_CSV_METADATA.xml`), each once; the CSVs may
  hold only the NEW rows. CSVs fully quoted, `\n`, UTF-8, no BOM. Dates `YYYY/MM/DD`.
- Export scope is `mode=search` (about 111 types): never treat "not in export" as "doesn't
  exist"; existence is checked through REST.
- `GET .../enclosure/FileContent` returns HTTP 406 with `Accept: application/json`.
- HTTP 401 on the first call = Oracle rejected the login: don't retry with unchanged credentials.

## Not proven

- Whether Save on the screen refuses what the import refused (the screen showed no message on
  the field for small letters, ORA, spaces, a duplicate type or code, a bad Display Sequence or
  dates; only FND-7103 / FND-7104 come at once).
- Adding a code to a System type through REST (never tried on purpose; refused by the folder).
- An existing type re-sent with DIFFERENT values in the import (would change it; never sent).
- Creating a type through REST (`POST standardLookups`): our test was refused for a missing
  language attribute ("Definition Language of type Attribute is not found in StandardLookupTypes"),
  not for the duplicate name, so it proves nothing; the import is the route.
- A module no lookup uses yet; module names that exist more than once.
- The highest number of codes in a type (1000 worked).
- Translations and the code flexfield (lookupsDFF) exist in REST; not supported.

## History / material

- `modules.json` - modules looked up so far (name, type, key, ID); safe to delete (rebuilt on use).
- `manual-notes/describe_imports.json`, `manual-notes/poc_hits.txt`, `package-route/*` - early
  reference material.
- Test lookups in this TEST pod (the scripts never delete): ZZ_POC_TEST2/3/6/7/8, ZZ_TEST_4831,
  ZZ_TEST_4423 (earlier). 2026-10-25 (ZZ_TEST_LK_8806_*): _ALL (Order Management, Authenticated;
  A1 Alpha with every field, B2 disabled, "my code x", H1 added later through REST), _ANON
  (Concepts, Anonymous, C1), _OME (Oracle Middleware Extensions for Applications, Secure, D1),
  _B1 (E1, E2), _B2 (F1, BADCODE, F3; created on the rerun), _B3 (G1), "ZZ_TEST_LK_8806 SPACE"
  (S1), "ZZ_TEST_LK_8806-DASH.DOT" (D1), _DUPCODE (X1 "Two"), _SEQNEG (N1, position -1), _MANY
  (1000 codes), _PAGE (Concepts, Anonymous; P1, "p 2"); code ZZ_TEST_LK_8806 in the Extensible
  type ORA_DGV_SERVICE_TYPE. Refused, not in Oracle: ZZ_TEST_LK_8806_lower, ORA_ZZ_TEST_LK_8806,
  _SEQTXT, _ENDB4, _MEAN2, _TMEAN, and _B2's first try (31-character code).
