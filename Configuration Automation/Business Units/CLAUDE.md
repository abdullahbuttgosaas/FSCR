# Business Units

Creates a **business unit** and always gives Configuration.TEST (fallback Configuration)
**Business unit data access** to it as **Order Manager** and as **Pricing Administrator**;
extra access from the request comes last (see "Required access and extra access" below).
The business unit and the access are made in two steps, both by CSV export/import on the Redwood Setup page
(Setup and Maintenance > offering **Order Management**):

1. **Manage Business Unit** (functional area **Organization Structures**; the task is
   called "Manage Business Unit", singular; its page is titled "Manage Business Units").
   Task code `FUN_MANAGE_BUSINESS_UNIT`.
2. **Manage Data Access for Users** (functional area **Users and Security**).
   Task code `ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS`.

**Normal run since 2026-10-23: fast, about 40-55 s** (no before-export, no import status
screen, filtered access reads, no screen checks unless "Check on screen too"; PROVEN by
ZZ_TEST_1097, ZZ_TEST_7361, ZZ_TEST_6290, see Known gotchas "Fast first-time runs").

Routes per step (2026-10-21):
- **Step 1, business unit: export/import** (REST has no way to create a business unit).
  Since 2026-10-26 sent as a Setup task process (`setupTaskCSVImports`, the same file, no
  browser) by `--run`, `--run-batch` and the command line, with Oracle's result and log read
  (PROVEN: ZZ_TEST_BU_3138_*). Without REST: the classic layout through this folder's own
  `classic_setup.py` (PROVEN on classic by ZZ_TEST_5950).
- **Step 2, data access: REST** (`dataSecurities`, PROVEN 2026-10-21 by ZZ_TEST_5950),
  with the export/import route as automatic fallback (built for Redwood, its screens
  checked on classic, **a real create on classic not yet re-proven**).
- The lists (location, default set, user, role) are read live through REST.

Status summary: both steps PROVEN by a clean run on 2026-10-20 (ZZ_TEST_1424, Redwood,
both export/import) and again on 2026-10-21 (ZZ_TEST_5950, classic, step 1 export/import
+ step 2 REST). Only manual step: the one-time sign-in. Not built on purpose (the user said they are not
needed): the Business Unit Data Access scope step and the Set Assignment step.

## Sheet route: --plan and --run-batch (2026-10-26, PROVEN, `bu_batch.py`)

Scope (the user's decision): only the Create Business Unit screen's fields - Name*, Location
(optional), Manager (optional, only the two people above), Default Set* (37 sets), Active (default
yes) - then the required access (Order Manager, Pricing Administrator for the configured user).
**Never** business functions, ledger, legal entity, currency, profit center, service providers or
set assignments. Field by field: `sheet_fields.md`.

```
python "Business Units/browser_flow.py" --plan '[{"name": "X", "manager": "Smith, Aron"}]'   # read-only
python "Business Units/browser_flow.py" --run-batch '[{"name": "X"}, {"name": "Y", "location": "none"}]'
```
- `--plan` (changes nothing; one Manage Business Unit export only for a location outside the
  common set): per business unit `status` new / exists / problems, `problems` [{business_unit,
  field, value, reason, suggestions (from Oracle's own lists), fix}], `access` (will be added /
  already there), `oracle_will_get` (screen labels), `notes`, `summary`.
- `--run-batch`: the same checks first; **nothing is sent for a business unit unless all of
  its checks pass, the access user and its roles included** (no user or role -> nothing is
  created). Just before sending, the names are read again (one made meanwhile is never sent).
  Then ONE Setup task process for all new business units (`setupTaskCSVImports`
  FUN_MANAGE_BUSINESS_UNIT, only the new rows, headers from `bu_import_template.json`); Oracle's
  result and process log are read; every business unit read back (finBusinessUnitsLOV: active,
  LocationId, ManagerId = the manager's PersonId; every other business unit unchanged) and in a
  second export (default set, location code and set, status, manager columns exactly as sent);
  then the missing access rows (REST, each read back), the pricing check, the shared file.
  Result per business unit: "Created ... Saved and checked in Oracle, every value as sent" /
  "Oracle didn't save the business unit X: <reason>" with a structured problem for the page /
  "Business unit X saved and checked, access missing: <role> (<reason>). A rerun adds only the
  missing access." The closing line names what was saved when something failed.
- An existing business unit (also one that differs only in capitals: treated as that one, said
  plainly) is never sent and never changed; only its missing access is added; nothing missing ->
  `skipped`. A rerun skips what is saved and never doubles anything (proven).
- `--run` (page, one business unit) now uses the same Setup task process and reads Oracle's
  answer: a refused row stops at once with Oracle's reason (before: a 6-minute wait). No browser
  opens to create a business unit any more while REST answers (the classic screen route stays
  as the fallback without REST). Not proven yet: a real Oracle refusal through `--run`.

**In the upload sheet (2026-10-26):** tab Business Units, registry group "Business Units"
(`--plan` for the preview, `--run-batch` for Create, `ask_on_refusal` for the pause-and-ask
panel), see root CLAUDE.md > Business Units module. `--plan` also returns per business unit
`found` (yellow notes: already there / only capitals differ), `oracle` (what Oracle will get per
field), problems with `key` / `text`, and `ok: true` whenever the check ran. Two sheet rows with
the same name: "'X' is listed twice"; differing only in capitals: "'x' differs from 'X' (listed
earlier) only in capitals. Oracle treats them as the same business unit ..." (plus "Oracle also
already has 'X'" when it does). Test workbooks: `manual-notes/Business_Units_TEST_good.xlsx`
(ZZ_SHEET_BU_8010_*) and `..._bad.xlsx`; previews only, nothing created.

### What Oracle does (deliberate tests, 2026-10-26, test number 3138)

| Case | Oracle's answer | Rule in the folder |
|---|---|---|
| One bad row among three (default set ZZNOSET) | process COMPLETED_ERRORS; **only that row dropped, the other two saved** (B1, B3). Log: "JBO-25072: Applying List binding LOV_DefaultSetCode with given set of values leads to no matching row ... JBO-27014: Attribute OrgInformation4 in BusinessUnitDetailEO is required" | default set checked against setIdSetsLOV before sending; log -> "Oracle has no matching value for Default Set" |
| Name of 241 characters (with two good rows) | only that row dropped: "JBO-27040: Value ... for field Name exceeds the maximum length allowed" | Name at most 240 (240 accepted: ZZ_TEST_BU_3138_L240_...) |
| Name with a trailing space ("ZZ_TEST_BU_3138_CAPS ") | **accepted as a second, separate business unit**; the one without the space unchanged | names with outer spaces refused before sending |
| Capitals-only variant of an existing name ("zz_test_bu_3138_caps") | refused: "Status details: JBO-27023: Failed to validate all rows in a transaction." on the business object, no row named; the existing one unchanged | treated as the existing business unit (never sent) |
| Capitals-only variant **together with a good row** (ZZ_TEST_BU_3138_D1) | **the whole group dropped**: D1 was not saved either | as above; the result says "Oracle refused the whole group" if it ever happens |
| Access refused after the business unit was saved (simulated refusal of Pricing Administrator) | business unit and Order Manager saved | "Business unit ... saved and checked, access missing: Pricing Administrator (...)"; the rerun added only Pricing Administrator (proven) |
| Required role the user doesn't hold (simulated: "Chief Dreamer") | - | nothing sent: "Configuration.TEST doesn't hold the role Chief Dreamer, so that access can't be given ...; nothing is made." |
| Access on an inactive business unit | accepted (both rows, active) | no pricing check, not written to the shared file |

Oracle's log names a failed row only by internal keys, never by the business unit name: the
business unit not found afterwards is the failed one; with one missing and one failed row the
reason is that row's; with several, every reason is given and the result says Oracle doesn't
tell which is which (never guessed). A process with no row error but a business object error
(JBO-27023) dropped everything sent with it.

Speed: 1 business unit 1 min 18 s - 1 min 36 s, 3 in one go 2 min 04 s (about 50 s of it is the
second export that checks every value); `--run` 26 s; `--plan` a few seconds (+ about 35 s for a
location outside the common set). A network blip (host name not resolving for a moment) happened
once: reads are asked once more after 8 s (`rget`); nothing that writes is ever repeated.

Shared file `common/created_business_units.json`: names starting with ZZ_TEST_ (test data) and
inactive business units are never written (2026-10-26, so the price list drop-down doesn't show
them). The older entries stay as they were (test names among them).

## Input rules

REQUIRED - if missing, ask in one plain message (never for codes or IDs):
- `name`: business unit name (max 240). If a BU with this name already exists
  (case-insensitive), the business unit itself is never changed and its values are
  printed; only the required and requested extra access rows it is **missing** are added
  (same safeguards; needs REST), and the result says what was added.

DEFAULTS - the user's standing choice. Use them without asking; only a value the
request names replaces its default (the script prints each default it used):

| Request key | Default | Rule |
|---|---|---|
| `location` | Go Saas Lahore Office | location **name** as the screen shows it; checked in the Create Business Unit form's Location search; not found: stop, list the locations that start like it, ask the user to pick |
| `default_set` | 001 CUSTOMER SITE | reference data set code or name; checked against the form's Default Set list; not found: stop, list all sets (name and code), ask the user to pick |
ALWAYS (2026-10-21, the user's rule; not request keys, never replaced or skipped by
anything in the request): Configuration.TEST (fallback Configuration, when that user isn't
an active user) gets **Order Manager** and **Pricing Administrator** access on the business
unit, in that order, each verified. **Do not ask the user about this access.**

EXTRA ACCESS - optional, in addition (never instead), added **last**, after everything
required is verified (see "Required access and extra access"):

| Request key | Default | Rule |
|---|---|---|
| `user` | Configuration.TEST (the required user) | the login that gets the extra access; a named user must be an active user (no fallback); a user without a role is a mistake |
| `role` | none | extra role **name**; must be a role that user holds **and** one that can be given for a business unit (checked before anything is created; else stop and list the valid roles) |
| `pricing_role` | none | a second extra role for the same user, same check (the key name is kept for old requests) |

An extra role that is already part of the required access (e.g. Order Manager for
Configuration.TEST) is reported as "already there".

The security context is always **Business unit** and its value is the new BU itself.

OPTIONAL - if missing, the UI default:

| Request key | Screen field (Create Business Unit) | UI default | Kind |
|---|---|---|---|
| `active` | Active | ticked (true) -> Status A; false -> I | true/false |
| `screen_check` | (not a screen field) "Check on screen too" | false | true/false: also the screen checks and the second export (slow, see Known gotchas 2026-10-23) |

Manager (2026-10-26, PROVEN): request key `manager`, by full name ("Yaqub, Younas" / "Younas Yaqub")
or person number; ONLY Yaqub, Younas (300000002688269) or Smith, Aron (4), the user's decision. Any
other value is refused with those two. No location: `"location": "none"` (or null); left out = the
standing default. Both work in `request.json`, `--run`, `--plan` and `--run-batch`.

Dates: the access row's start date is **Oracle's today**, read from the
business unit export (`SysEffectiveDate`, 2026/10/20 on 2026-10-20), never the PC clock.

How each pick-from-a-list value is read live (the script stops before creating
anything, lists the valid values in plain words and asks the user to pick):

| Field | Read live from (REST, GET only) | When the value isn't there |
|---|---|---|
| Location | HCM `GET /hcmRestApi/resources/11.13.18.05/locations` (all, fields LocationCode, LocationName, SetId, ActiveStatus; 130 on 2026-10-21) | stop: **the location does not exist in Oracle and cannot be created here**; all location names listed. Inactive location: stop |
| Default set | `GET setIdSetsLOV` (SetCode, SetName) | stop, list all sets (name and code) |
| User | `dataSecurities` > `userNames` list, `q=DisplayName='<user>'`, active only | try `user_fallback`; else stop |
| Role | `dataSecurities` > `userRoleDetails` list of **the user's own** access row, `q=Username='<user>'` (RoleName = screen name, RoleCommonName = code; 281 roles for Configuration.TEST) | stop: the user doesn't hold that role; similar role names listed |

List links are taken from a `dataSecurities` item Oracle returns (never built by hand).
If REST is unavailable, the script falls back to the screen checks: the Create Business
Unit form's Location and Default Set searches and the Manage Data Access for Users Role
list (see Known gotchas for how those work).

Drop-down values seen on the screen (add new ones when seen; never rename):
- Default Set (code - name, 37 on 2026-10-20): 001 CUSTOMER SITE - 001 Customer Site,
  28REFDATA, A1_DATA_SET - A1 Data Set, AHSAN RDS - AHSAN RDS NAME, AKREFDATA - AK Referance
  Data Set, ASCEND_001 - ASCEND, ASAD123 - Asad123, 25010114 - Ash, ASH-25010114 - Ash BU
  Reference Data Set, ORA25010114 - Ash Bash, CUSTOMER_RDS, COMMON - Common Set, DSSREFDATA,
  221 - Duck set, ENTERPRISE - Enterprise Set, SET0001 - GoSaaS Labs Data Set, HAHAREFDATA,
  ITBU - ITBY, 1111 - Ln106, MA_CUST_SET, MGREFST - MG US1 Business Unit, MGREF-AP,
  MNC_CUST_OM_RDS, MWBKBU1 - MWBK BU 1, MWBKBU2 - MWBK BU 2, 23 - Mannan's Set, MOMINA12 -
  Mominaset, N24REFDATA, NMT - Northwind, PPREFDATA, PRC100R - PRC100 Reference Data Set,
  S-31 - Project Set, S_DATA_SET - S Data Set, 21 - T2 set, 7382 - T22 set, TEST, 25010094 -
  USAMA SET.
- Location (name = code), confirmed through the Location search: Go Saas Lahore Office =
  LHEGS, Lahore Head Office = LHR_HO. Other names in the list (first page): Headquarters_ZS,
  LOC01_BLR_IND, GoSaaS Labs Location, GoSaaS Location, PRC02, Test_Location_V3 ... V7.
- Role (name = code), confirmed by matching screen and export rows: Order Manager =
  ORA_DOO_ORDER_MANAGER_JOB. Also seen: Order Entry Specialist =
  ORA_FOM_ORDER_ENTRY_SPECIALIST_JOB, Pricing Administrator = ORA_QP_PRICING_ADMINISTRATOR_JOB.
- Security Context list: Academic Organization, Academic Organization by Campus, All,
  Asset book, Award Organization Hierarchy, Business unit, Campus, Control budget, Cost
  organization, Data access set, Intercompany organization, Inventory organization, Item
  organization, Ledger, Legal entity, Manufacturing plant, Project organization
  classification, Reference data set.

## Route status

- **2026-10-21, discovery (read-only):** REST for a **business unit** create: none.
  `finBusinessUnitsLOV` (fscm) and HCM `organizations` / `hcmBusinessUnitsLOV` are
  GET-only; `businessUnits` returns 404 on the fscm, hcm and crm REST bases. REST for
  **data access**: `fscmRestApi/.../dataSecurities` (create, get, update, upsert;
  fields UserName, RoleCommonName (code), RoleNameCr (name), SecurityContext,
  SecurityContextValue, ActiveFlag; finder ManageDataAccessRF on Userrf / Rolerf).
- **Step 1 export/import on classic: PROVEN** 2026-10-21 (ZZ_TEST_5950, defaults):
  import 1/1 objects 0 errors, after-export row as built, REST GET (finBusinessUnitsLOV)
  active with location LHEGS's LocationId, 125 other BUs and their usages, providers
  and 8363 set assignments unchanged, Manage Business Units shows it.
- **Step 2 REST: PROVEN** 2026-10-21: POST dataSecurities HTTP 201
  (Configuration.TEST / ORA_DOO_ORDER_MANAGER_JOB / Business unit / ZZ_TEST_5950,
  active, id 300000393685816); GET finds exactly that row; all 377 other access rows
  (every user) unchanged; "Users with Data Access" shows it; Create Order's Business
  Unit list shows ZZ_TEST_5950 (10 BUs). Whole run about 4 minutes.
- **Step 2 export/import fallback: built for Redwood, screens checked on classic
  (`--check`), a real create on classic not yet re-proven.** It runs automatically if
  the REST POST fails or is refused (HTTP 403 is reported as "no permission"), or with
  `--fallback`. If REST created some rows before failing, those are reported and only
  the missing ones go through the fallback.

- **Step 1 Manage Business Unit, CSV export/import: PROVEN** (2026-10-20, ZZ_TEST_1424,
  Go Saas Lahore Office / LHEGS, 001 CUSTOMER SITE). Import 1/1 objects successful. The
  after-export shows the row exactly as built (Oracle assigned the OrganizationCode), all
  123 other BUs, 1068 usages, 264 service providers and 8363 set assignments unchanged.
  Manage Business Units shows it Active at Go Saas Lahore Office.
- **Step 2 Manage Data Access for Users, CSV export/import: PROVEN** (2026-10-20):
  Configuration.TEST / ORA_DOO_ORDER_MANAGER_JOB / ZZ_TEST_1424, active, from 2026/10/20.
  Import 4/4 objects successful; the after-export has the row, and all 368 other access
  rows (every other user, role and BU) are unchanged, as are the mapping and provisioning
  files. "Users with Data Access" shows Configuration.TEST / Order Manager / ZZ_TEST_1424.
- **Create Order check: PROVEN** (read-only): the Business Unit list on Create Order
  showed ZZ_TEST_1424 right after step 2 (before: 0012, 01PRC Exam BU, 04PRC Exam, abcde,
  qwe, ui, wer, yu).
- UI form route: not needed (both exports and imports work).
- One full run: about 9 minutes (4 exports, 2 imports, screen checks).

## How to do it

```
python "Business Units/browser_flow.py" --check     # read-only, nothing imported or saved
python "Business Units/browser_flow.py"             # full run (headless)
python "Business Units/browser_flow.py" --headed    # same, browser visible
```
(Page commands `--spec`, `--options`, `--run`: see Page interface.)

Request file `Business Units/request.json`:

```json
{"business_units": [
  {"name": "ZZ_TEST_1424"},                  // only the name: every default is used
  {"name": "Karachi Sales",                  // required
   "location": "Lahore Head Office",         // default Go Saas Lahore Office
   "default_set": "COMMON",                  // default 001 CUSTOMER SITE (code or name)
   "user": "Configuration",                  // extra access: user (default Configuration.TEST)
   "role": "Buyer",                          // extra access: role (none by default)
   "active": true}                           // default true
   // Order Manager + Pricing Administrator for Configuration.TEST: always, not keys
]}
```

The default `request.json` holds only `{"name": "ZZ_TEST_5950"}` (that BU exists, so a
run skips it and shows its values and access rows).

What `--check` does (2026-10-21): prints the Setup and Maintenance layout; the BU export
(an export process only, no data change) and Oracle's today; all data access rows,
locations, sets, the user and the user's roles through REST (GET only); existence of each
BU (export + finBusinessUnitsLOV) and, for an existing BU, its data access rows; the plan
with the route per step; opens Export and Import > Create New of both tasks and leaves
each with Cancel; reads the Create Order Business Unit list (Cancel > Yes, nothing saved)
and says for each requested BU whether it is in it. Proven clean on classic 2026-10-21.

Step 2 by REST: `POST dataSecurities` {UserName, RoleCommonName (code), RoleNameCr
(name), SecurityContext "Business unit", SecurityContextValue (the BU), ActiveFlag true};
an existing row for the same user, role and BU is skipped. Verify: GET all access rows:
exactly one new row, active; every other row identical (all users).

What the full run does (after the same checks):
1. Import zip 1 = every file of the BU export once, every CSV **header-only** except
   `FUN_BUSINESS_UNIT.csv`, which holds only the new row. Import, second export: the new
   row as built; every other row of every file unchanged (who columns and
   SysEffectiveDate ignored); Manage Business Units search shows it.
2. Import zip 2 = every file of the data access export once, header-only except
   `ORA_FUN_ALL_USER_DATA_ACCESS.csv`, which holds only the new access row. **No other
   user's access is ever in the file.** An access row that already exists for the same
   user, role and BU is skipped. Second export: the new row present; every other row
   identical; "Users with Data Access" shows it; Create Order lists the BU.
3. Deletes `_work/` only after everything is verified; keeps it (screenshots) on failure.

## File layouts

Manage Business Unit export (1 business object):

| File | Columns (key ones) |
|---|---|
| `FUN_BUSINESS_UNIT.csv` | Name, DefaultSetCode (set **code**), PrimaryLedgerName, OrganizationCode (Oracle key "GUID id timestamp", assigned on import), LegalEntityName, InternalLocationCode (location **code**), Status (A/I), ManagerListName, FinancialBUShortCode, DefaultCurrencyCode, who columns, Classification / ClassificationCode / OrgInformationContext (FUN_BUSINESS_UNIT), EffectiveStartDate 0001/01/01, EffectiveEndDate 4712/12/31, LocationSetCode (from the location: COMMON for LHEGS), ProfitCenterFlag (N), PersonNumber / EffectiveStartDate3 / EffectiveEndDate3 / FirstName / LastName / MiddleNames (manager) |
| `FUN_BU_USAGE.csv` | FUN_BUSINESS_UNIT.Name, ModuleId, ConfigurationStatus (business functions) |
| `FUN_BU_SERVICE_PROVIDERS.csv` | ClientBuName, ProviderBuName, UpstreamFunctionId, DownstreamFunctionId, ... SysEffectiveDate |
| `LE_1214416713655.csv` | set assignments: SetCode, OrganizationCode, ReferenceGroupName, Name (BU), DeterminantType BU, SysEffectiveDate (68 reference groups per UI-made BU) |
| `ASM_SETUP_CSV_METADATA.xml` | ObjectShortName FUN_MANAGE_BUSINESS_UNIT; kept unchanged |

New BU row = Name, DefaultSetCode, InternalLocationCode, LocationSetCode, Status plus the
fixed values above; everything else empty (learned from UI-made BUs "ui", "abcde").

Manage Data Access for Users export (4 business objects):

| File | Columns (key ones) |
|---|---|
| `ORA_FUN_ALL_USER_DATA_ACCESS.csv` | RoleName (role **code**), UserName, BuName (BU name, for Business unit), SetName, OrganizationCode, ... (one column per security context), ActiveFlag, CreatedBy, EndDateActive, LastUpdatedBy, RecordTypeCode (USER_DEFINED), StartDateActive, DatasecContextTypeCode, DatasecContextValue5, ObjectName (FUN_ALL_BUSINESS_UNITS_V = Business unit) |
| `ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` | RoleName, ObjectName, ApplName, RecordTypeCode, SecurityContext |
| `ORA_FUN_DATA_PROVISIONING_RULES.csv` / `..._RULE_DETAIL.csv` | provisioning rules (not used) |
| `ASM_SETUP_CSV_METADATA.xml` | ObjectShortName ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS |

Links: the access row's BuName = FUN_BUSINESS_UNIT.Name; RoleName = role code (screen
shows the role name); UserName = login; ObjectName FUN_ALL_BUSINESS_UNITS_V = security
context "Business unit". Import order: step 1 before step 2 (the BU must exist).
Format: UTF-8 without BOM, every field quoted, `\n` line endings.

## Click paths (reference)

- Setup and Maintenance (profile icon or Navigator) > Set Up **Order Management** >
  Organization Structures > Manage Business Unit > "+" above the table > Name, Location,
  Default Set > Save and Close.
- Users and Security > Manage Data Access for Users > "Users with Data Access" >
  Security Context "Business unit" > "+" > User Name, Role, Security Context Value >
  Save and Close.
- Order Management work area: Navigator > Order Management > Order Management >
  Tasks > Create Order > Business Unit list.

## Sample requests

Every request below also gets the required access first: Configuration.TEST (fallback
Configuration) as Order Manager and as Pricing Administrator.
- "Create business unit ZZ_TEST_1424." -> `{"name": "ZZ_TEST_1424"}`: Go Saas Lahore
  Office, 001 CUSTOMER SITE, the required access only.
- "New BU Karachi Sales at Lahore Head Office with Common Set." -> location and set from
  the request; the required access only.
- "New BU Retail East, also give Configuration the Order Entry Specialist role." -> extra
  access: user Configuration (no fallback), role Order Entry Specialist, added last.
- "Create BU Retail West and also make Configuration.TEST a Buyer on it." -> extra access
  Buyer for the required user, added last.
- "Give ZZ_TEST_8131 Buyer access too." -> existing business unit: not changed; missing
  rows only (the required ones are already there, Buyer is added).

## Page interface

Contract: root CLAUDE.md > Page interface (helper `common/page.py`). **PROVEN
2026-10-21** by a clean `--run` (ZZ_TEST_5115, below). The first real `--run`
(ZZ_TEST_3079) had ended VERIFY_FAILED on a false "other access rows changed" (unstable
unsorted pages, fixed, see Known gotchas). One business unit per `--run`;
`request.json` and the normal commands are unchanged.

```
python "Business Units/browser_flow.py" --spec
python "Business Units/browser_flow.py" --options location
python "Business Units/browser_flow.py" --options default_set
python "Business Units/browser_flow.py" --options user
python "Business Units/browser_flow.py" --options role          # also pricing_role
python "Business Units/browser_flow.py" --run '{"name": "Karachi Sales"}'
python "Business Units/browser_flow.py" --run '{"name": "Karachi Sales", "role": "Buyer"}'
```

| Key | Label | Required | Type | Placeholder | Default |
|---|---|---|---|---|---|
| name | Business unit name | yes | text | Karachi Sales | - |
| location | Location | yes (pre-filled) | pick, samples | Go Saas Lahore Office | Go Saas Lahore Office |
| default_set | Default set | yes (pre-filled) | pick, samples | 001 Customer Site | 001 CUSTOMER SITE |
| user | Extra access user | no | pick | Configuration.TEST | - (empty: Configuration.TEST) |
| role | Extra access role | no | pick | Buyer | - |
| pricing_role | Second extra access role | no | pick | Pricing Analyst | - |

The form's description, shown near the top, says "These will always be set up: Order
Manager and Pricing Administrator access for Configuration.TEST" (a note, not fields).
"More options" = extra access in addition to those two.
| active | Active | no | yes-no | yes | yes |

**Up front and samples (2026-10-21).** Name, location and default set are up front;
location and default set are `required` picks with the standing defaults, so the form
shows them pre-filled (a left-out value still means the default). "More options" holds
only optional fields (user, role, active). Location and default set offer only verified
samples (`SAMPLES` in `browser_flow.py`, `"list": "samples"`). **A value counts as verified
once a real create in this project or the user's own test has used it** (a business unit
created with it); only then does it join the samples. Current samples, in Oracle's exact
spelling (all confirmed in the live lists 2026-10-21):
- location: **Go Saas Lahore Office** (pre-filled default; ZZ_TEST_1424, ZZ_TEST_5950,
  TEstBU, ZZ_TEST_3079, ZZ_TEST_5115), **GoSaaS Labs Location** and **Headquarters_ZS**
  (the user's own test, 2026-10-21);
- default set: **001 Customer Site** (001 CUSTOMER SITE, pre-filled default; the creates
  above), **Enterprise Set** (ENTERPRISE) and **CUSTOMER_RDS** (the user's own test).
Another value can be typed: `--run` checks it
against the full live list (tried: "Mars Office" -> NOT_IN_ORACLE). The full lists stay
behind a switch: `--options location --all` (129) / `--options default_set --all` (37).

Pick lists, read live through REST (GET only), the same lists the run checks against:
- `location`: HCM `locations`, active ones; value = label = LocationName (129 on 2026-10-21).
- `default_set`: `setIdSetsLOV`; value = SetCode, label = SetName (37).
- `user`: `dataSecurities` > `userNames`, active; value = label = DisplayName. That list
  **stops at 500 rows** (totalResults 528, offset 500 returns nothing), so it is read
  sorted by DisplayName both ways and joined: all 528 (works up to 1000; a NOTE is
  printed above that).
- `role` / `pricing_role` (extra access): the roles the required user holds
  (`userRoleDetails`, 281 on 2026-10-21) that **can be given for a business unit**, i.e.
  some user already has an access row with that role on a business unit (`dataSecurities`,
  Security context "Business unit"): 59 roles, incl. Buyer, Order Manager, Pricing Analyst.
  During `--run` the page check accepts any role the user holds, then the run's own
  up-front check decides (below). (A role only another named user holds is refused by the
  page check: known limit.)
**Up-front extra role check (before the browser starts, nothing created):** the named
extra user must be active; each extra role must be one that user holds and one that can be
given for a business unit: an existing Business unit access row with that role (any user),
else Oracle's security context mapping (`ORA_FUN_SECURITY_CONTEXT_MAPPING.csv` of a fresh
data access export, read-only, only when needed; progress `checking_roles` 25). Otherwise
NOT_IN_ORACLE: "The role '<name>' can't be given for a business unit ... Roles that can:
...". Why both: Oracle has no list of roles per security context (the Security Context list
is the same for every role), and the mapping holds only 45 roles (39 for business units,
Buyer included; **not** Order Manager or Pricing Administrator, which work), so the mapping
can prove a role works but not that it doesn't.
Steps: reading 5, checking 20, (`checking_roles` 25), creating 40 ("Creating the business
unit (this takes a few minutes)", new business unit only), `checking_bu` 50,
`access_order_manager` 60 "Giving Order Manager access", `access_order_manager_done` 65
"Order Manager access: done", `access_pricing_administrator` 70 / `..._done` 75 "Pricing
Administrator access: done", verifying 85 (Create Order list, cache check, shared file),
`extra_access` 95 "Adding the extra access", done 100. The page keeps the ": done" lines
under the progress bar. Result: `text`, `steps` (one plain line per part: "Business unit:
created and checked", "Order Manager access: done", "Pricing Administrator access: done",
"Extra access Buyer for Configuration.TEST: done"), `partial` (true when the extra access
wasn't added; the page shows "Done, with one note"), `created` (business unit row,
`required_access` and `extra_access` rows with their status, Create Order list, pricing).
Tried 2026-10-21: `--spec` OK; `--options` location / default_set / user / role OK;
`--options name` -> NOT_A_LIST_FIELD; location "Mars Office" + set "Nope" ->
NOT_IN_ORACLE, both in one message with the valid lists; role "Chief Dreamer" ->
NOT_IN_ORACLE; ZZ_TEST_5950 -> skipped with its access row (Configuration.TEST / Order
Manager). Real `--run` ZZ_TEST_3079 (defaults, classic layout): all progress lines;
step 1 import, after-export row as built (LHEGS, 001 CUSTOMER SITE, A), REST GET active,
all other BUs and files unchanged, Manage Business Units shows it; step 2 POST
dataSecurities HTTP 201 (Configuration.TEST / ORA_DOO_ORDER_MANAGER_JOB, active, id
300000393684844), "Users with Data Access" shows it, Create Order lists ZZ_TEST_3079;
then the false FAIL above. 233 seconds.
Clean `--run` ZZ_TEST_5115 (defaults, classic, after the sorted-read fix): all progress
lines and a successful result; step 1 after-export row as built (LHEGS, COMMON, 001
CUSTOMER SITE, A), REST GET active, the other 128 BUs, 1068 usages, 264 providers and 8363
set assignments unchanged, Manage Business Units shows it; step 2 POST HTTP 201
(Configuration.TEST / Order Manager / ORA_DOO_ORDER_MANAGER_JOB, active, id
300000393685821), **every other access row unchanged (380 rows, all users)**, "Users with
Data Access" shows it, Create Order lists ZZ_TEST_5115. 224 seconds.

## Preview versus Create (2026-10-26)

Every refusal seen for business units (default set not in the list, name over 240, a name differing only in
capitals or by a trailing space, required access) is already checked by `--plan`. Unsaved screen probe
2026-10-26: the Create Business Unit Name box holds 240 characters (241 typed -> 240 kept, no message on
Tab); Location, Manager and Default Set are search lists. **Still only at Create (not proven):** a name equal
to another organization's name (department, legal entity); characters beyond those tried; a location and
default set pair Oracle might refuse; access refused after the business unit was saved (never seen; a rerun
adds missing access). `ask_on_refusal` is on (name, location, manager, default_set, active).

## Related folders

- **Price Lists** (agreed by the user 2026-10-21): this folder writes every created business
  unit to `common/created_business_units.json`; Price Lists reads it to handle Oracle's
  data-access cache (see Pricing visibility above). No code is shared between the folders.

- None built. Note for discussion: the Default Set values are the same reference data
  sets the Customers folder calls "account address set", and a new BU without set
  assignments may matter for other folders' data (see gotchas). Nothing links the folders.

## Required access and extra access (2026-10-21, the user's rule; PROVEN by ZZ_TEST_9754)

Run order (`run_units`), the same for the command line and the page:
1. **Business unit** (new only): export/import, verified (unchanged).
2. **Order Manager**, then **Pricing Administrator** access for Configuration.TEST
   (fallback Configuration): one `add_access()` each (REST, export/import fallback), each
   verified by REST read-back (exactly one active row) with every other row of every user
   unchanged, and on screen. A failure here stops the run (verify failure, repair).
3. Create Order list (fresh sign-in if missing), the pricing cache check for both rows
   (`wait_for_pricing`), then `common/created_business_units.json` (skips a duplicate).
4. **Extra access** (More options / request keys `user`, `role`, `pricing_role`), one row
   per role, `add_access(..., tolerant=True)`: REST only, no fallback, verified the same
   way. If Oracle rejects it (or REST is unavailable, or the read-back fails) it is **not a
   failure**: the result is `ok` with `partial: true` and the text "The business unit is
   ready: Order Manager and Pricing Administrator were given. The extra access wasn't
   added: <Oracle's reason>" (no repair). Steps 1-3 are never undone or blocked by it.
Existing business unit: never changed; with REST, only its missing required rows (steps
2-3) and missing extra rows (step 4) are added; nothing missing -> `skipped`. Without REST
it is skipped as before.
Proven 2026-10-21 through `--run` (the page's own output):
- **ZZ_TEST_9754** + extra role Buyer: step 1 export/import (LHEGS, COMMON, 001 CUSTOMER
  SITE, A; 135 BUs, 1068 usages, 264 providers, 8363 set assignments unchanged; on screen),
  Order Manager (HTTP 201, id 300000393936117, 390 other rows unchanged, on screen) "Order
  Manager access: done", Pricing Administrator (id 300000393936118, 391 unchanged) "Pricing
  Administrator access: done", Create Order lists it, both visible in 2-3 s, shared file
  "ready", then Buyer as extra (id 300000393897577, 392 unchanged, on screen). 338 s, ok.
- Existing business unit (ZZ_TEST_9754 again, extra role check bypassed by a test harness
  to see what Oracle does with a role that has no business unit evidence): both required
  rows "already there" (skipped, verified), shared file skipped the duplicate, the extra
  row was added. **Oracle accepted Anonymous User** (`ORA_FND_ANONYMOUS_USER_ABSTRACT`,
  HTTP 201, id 300000393973567): `dataSecurities` doesn't check the role against the
  security context, so the up-front check is the only guard against a meaningless row.
  That row is left in Oracle (test data, Configuration.TEST's own row only).
- The partial result ("The business unit is ready: ... The extra access wasn't added:
  <reason>", `ok` + `partial`, exit 0, no repair) is checked offline only (a simulated
  rejection); a real rejection hasn't been seen, since Oracle accepted even that role.
Earlier proof of the same building blocks:

### Step 3 (old order): pricing access (2026-10-21, PROVEN by ZZ_TEST_8131)

Default, like the Order Manager row: after the business unit **and** the first access row
are fully verified (never after a failure), the same user (Configuration.TEST, fallback
Configuration) gets **Pricing Administrator** (`ORA_QP_PRICING_ADMINISTRATOR_JOB`, found in
that user's live role list; Pricing Analyst and Pricing Manager are there too) on the new
business unit: one REST `dataSecurities` row, with the export/import fallback, exactly
like step 2 (`add_access()`): only this user's row is added, an existing one is skipped,
no other user's access is touched. The request key `pricing_role` (form: "Pricing role
for that access", default Pricing Administrator) changes the role; a role the user doesn't
hold stops before anything is created and names the pricing roles they hold. Progress
line: "Giving pricing access" (92). Verified: REST read-back (exactly one active row),
every other access row of every user unchanged, and "Users with Data Access" on screen.
Then, and only then, the name goes to `common/created_business_units.json` (see below).
ZZ_TEST_8131 (defaults): step 1 export/import, step 2 REST (Order Manager, id
300000393986083, 385 other rows unchanged), Create Order lists it, step 3 REST (Pricing
Administrator, HTTP 201, id 300000393985033, 386 other rows unchanged, on screen), both
visible through fresh reads in 2 s, added to the shared file as ready. 280 seconds.

## Pricing visibility and common/created_business_units.json (2026-10-21)

Oracle caches a user's data access: a role newly given on a business unit may not show
(for pricing, or in Create Order) until that user signs out and signs in again. So after
the access rows are written and verified, the run:
1. re-checks through fresh REST reads for up to 2 minutes (every 30 s): the business unit
   is listed and active (`finBusinessUnitsLOV`) and the user's new access row is there and
   active (`dataSecurities`). No REST list shows the login's pricing access as such (the
   priceLists resource has no business unit list; `finBusinessUnitsLOV` shows every
   business unit at once), so the first price list is the final proof (Price Lists);
2. reads the Create Order Business Unit list; if the new business unit isn't there, the
   saved browser sign-in may hold the old access: it says "Oracle needs a fresh sign-in
   before this business unit shows for pricing" and opens the sign-in window
   (`common/login_once.py`, which starts without the saved session; the user signs in,
   nothing is read or typed), then checks Create Order once more. If the window can't
   finish (no desktop, or the user doesn't sign in), it says in plain words to sign out
   and in again later;
3. after step 3 (pricing access) is verified too, adds the business unit to
   `common/created_business_units.json` (shared with Price Lists; a new file, created on
   the first add): name, `status` "ready", or "pending" with that note when it still
   wasn't visible, user, both roles, `pricing_confirmed` false until Price Lists has made a
   price list with it. A name already there is skipped (never doubled or changed, tried
   2026-10-21); the file is written atomically (a `.tmp` file next to it, then replaced).
   Never written after a failure. The fresh-read wait (1.) runs for both access rows. A pending business unit is **not** a failure of this folder: the
   business unit and its access are verified as before; the page result says the user
   should sign out and in again.
Tried 2026-10-21 without creating anything: the fresh-read check on the existing
ZZ_TEST_5115 (visible in 4 s), the wait loop with a pretend "not visible yet" (retries every
30 s, gives up after 2 minutes), and the shared file on a temporary copy.

## Known gotchas

- 2026-10-26: **Lost clicks on Oracle's busy pages: every browser step checked and done again** with the shared
  retry helper `ui.retry()` (`common/browser.py`: up to 3 tries, a short pause and a fresh wait each time, then one
  clear failure "Oracle's <step> after 3 tries", which `--plan` passes to the page). `classic_setup.py`: the
  Offering drop-down and option, Search Tasks (results window, or the task row when Oracle opens it directly), the
  result row (the task's Actions button; replaces the one extra click of 2026-10-21), the Actions menu, its
  submenu and entry (the task list has gone), the history's results link (Summary), the task link (`open_task`:
  a new tab or the task list gone), Cancel in `check_actions`. `browser_flow.py`: the + on Manage Business Units
  (a + without a position yet is tried again), Cancel on the form, the Location and Role dialogs
  (`ui.search_dialog()`, `ui.close_dialog()`), their searches and the Manage Business Units / Users with Data
  Access searches (`ui.fresh_search()`: a lost Search kept the old rows), Users with Data Access, the Navigator,
  the Order Management work area, Create Order (heading), its Business Unit list (soft: read again while empty)
  and leaving it with Cancel / Yes. **Never retried:** the import Submit (`submit_import`, `import_csv`), the
  export Submit keeps its own one extra click of 2026-10-21 (an export saves nothing).
- 2026-10-23: **Fast first-time runs** (the user's list of known causes; none of it was in
  the code yet). Causes and fixes:
  1. *Create Order cache.* Oracle caches the Create Order Business Unit list in the app
     session cookie of the saved sign-in (`JSESSIONID`, path `/fscmUI`; the sign-in itself
     is in the `ORA_FND_SESSION_*` / identity cookies). A new business unit stayed hidden
     there however long one waited, so the run looked failed: repair, then "already there"
     on the rerun. Fix: `create_order_fresh()` opens a fresh context from the saved sign-in
     (Playwright loads it; the script never reads or changes `.session/`) and drops ONLY
     that cookie in memory (`clear_cookies(name="JSESSIONID", path="/fscmUI")`). The
     sign-in window (`fresh_signin_and_recheck()`) is a last resort only.
  2. *Import status screen.* Never waited on any more: `classic_setup.submit_import()`
     submits and returns; the run polls `finBusinessUnitsLOV` every 3 s until the new
     business unit exists (Redwood: the shared import_csv, which still waits).
  3. *Access reads.* `rest_access_on(bu, user)` reads only that user's rows on that business
     unit (`q=UserName=...;SecurityContextValue=...`, 0.8 s) instead of all ~400 rows four or
     more times; the role list is read once for both roles; user, location, set and existing
     rows are read at the same time; no before-export when REST shows the name is free: the
     import file is built from `bu_import_template.json` (header lines only, saved from any
     export). A location outside the common set (SetId not 0) still needs one export.
  4. *Screen checks.* The after-export compare and Manage Business Units screen ("Checking
     the business unit's details", 418 s on 2026-10-22), Users with Data Access, the full
     "every other access row unchanged" reads and Create Order run only with "Check on
     screen too" (`screen_check`, More options, default no; `--screen-check`) or `--check`.
     The result says what was checked in Oracle and that the screens weren't looked at.
  5. *Limits and progress.* Every step (`Phase`) shows plain sub-steps with a timer (a line
     every 10 s), adds "Oracle is responding slowly right now" after 90 s and stops after 6
     minutes (TIMEOUT) with a plain line on what is and isn't done. The limit is checked
     between sub-steps and in every wait loop (a single Oracle screen wait can't be cut off
     midway; each has its own 60-120 s timeout).
  6. *Half-made business units.* An existing one gets only its missing rows, and the result
     names them ("... was missing Pricing Administrator access on it. Added: ...").
  The browser opens only when a business unit is created (LazyUI): adding missing access
  to an existing one needs no browser. The old import zip names had a ":" ("import_required:
  Order Manager.zip", only used by the access fallback); now "_".
  **Proven 2026-10-23** (defaults, each through `--run` exactly as the page calls it, each
  ok first time, exit 0, no repair, no sign-in window, both roles verified by REST
  read-back, active, pricing "ready"):
  | Business unit | Whole run | Lists | Create (submit + Oracle) | Each role | Pricing check |
  |---|---|---|---|---|---|
  | ZZ_TEST_1097 | 37 s | 2 s | 25 s | 1 s | 1 s |
  | ZZ_TEST_7361 | 54 s | 3 s | 39 s | 2 s | 2 s |
  | ZZ_TEST_6290 | 40 s | 2 s | 30 s | 1 s | 1 s |
  (before: 224-338 s, plus repair and the sign-in window). Of the create step about 20 s is
  opening the classic setup screen, the rest Oracle's own work. Then `--check` on those three
  (2 min 26 s, mostly the export): the Create Order list in the fresh app session showed all
  three, no sign-in. Half-made ZZ_TEST_5115 (Order Manager only): 13 s, no browser, "was
  missing Pricing Administrator access on it. Added: ...". The 90 s note and the 6-minute
  stop were tried offline with a shortened limit (StepTimeout with its plain state line).
  `bu_import_template.json` (this folder, header lines and Oracle's metadata file of one
  export, no data rows) is rewritten by any export; delete it to make the next run export once.

- 2026-10-21: TESTBU7 rerun: on classic "Export Setup Data to CSV File" the Submit click
  didn't register (form unchanged after 120 s, no message) -> "No confirmation after
  submitting the export". `classic_setup._confirm()` now clicks Submit once more for an
  **export only** if no confirmation shows within 30 s and Submit is still there (an
  export changes no data; an import is never submitted twice).

- 2026-10-21: TESTBU7 run: on classic Search Tasks, the click on "Manage Business Unit"
  (Organization Structures) in "Search Task Results" didn't register (window stayed open,
  area stayed Initial Users) -> "did not show in the task list". The screen itself was
  unchanged (opened fine right after). `classic_setup._task_row()` now clicks the result
  once more if the task's Actions button hasn't shown after 20 s.

- 2026-10-21: `add_access()` compared "every other access row" with the business unit's
  own rows still in the before-list, so an existing (skipped) row showed as "1 gone"
  (VERIFY_FAILED on an existing business unit, nothing posted). Fixed: both lists leave
  those rows out.
- 2026-10-21: Oracle's `dataSecurities` POST accepts any role the user holds on the
  Business unit context, even Anonymous User; it never refuses a role for not fitting.
  Keep the up-front extra role check (business unit access rows + security context mapping).

- 2026-10-21: the Create Order recheck after the fresh sign-in opened a second
  `OracleUI` inside the running one, and Playwright refused ("Sync API inside the asyncio
  loop"; TESTBU5 run, after the business unit and its Buyer access were already created and
  verified). Fixed: `fresh_signin_and_recheck()` now opens a new context (from the fresh
  sign-in) in the browser that is already open and goes back to the old one afterwards.

- 2026-10-21: **unsorted `dataSecurities` pages are not stable.** A read of all 380
  access rows (200 per page) gave 98 duplicates and missed 98 rows, so the "every other
  access row unchanged" check reported "98 gone/changed, 98 new" although nothing had
  changed (ZZ_TEST_3079 run). Fixed in this folder: `rest_access_rows()` sorts by
  UserRoleDataAssignmentId; three sorted reads right after were identical (380 rows,
  380 unique ids) with exactly one row on ZZ_TEST_3079. "Every other row unchanged" for
  that one run can't be re-checked now (its before-read was unsorted).
- 2026-10-21: the `userNames` list stops at 500 rows (see Page interface); `rest_user()`
  is not affected (it filters by DisplayName).

- 2026-10-21: Oracle is back on the classic layout; the shared export/import code is
  Redwood-only. This folder has its own `classic_setup.py` (Setup class: detects the
  layout, classic Offering drop-down, Search Tasks, Actions > Export/Import to CSV File >
  Create New / View All, status page, Download File; Redwood: the shared helpers).
- 2026-10-21: Search Tasks with a single match skips the "Search Task Results" window
  and opens the area with the task selected (Manage Data Access for Users); the classic
  step accepts both.
- 2026-10-21: the `userRoleDetails` list belongs to the access row it is read from:
  read from another user's row it returned 0 roles; it also returned nothing with
  `limit=500` (200 works). The script reads it from the requested user's own row.
- 2026-10-21: the Navigator sometimes needs more than 3 s to fill its links; the Create
  Order check waits up to 45 s and reopens it once.
- 2026-10-21: **ZZ_TEST_7669** (made by the run the user stopped on 2026-10-20) exists as
  a business unit (Go Saas Lahore Office) **without** a data access row: that run stopped
  between step 1 and step 2. It is left as it is (an existing BU is always skipped).

- 2026-10-20: the task is "Manage Business Unit" (singular) on the Set Up page.
- 2026-10-20: the "+" on Manage Business Units only reacts to a real mouse click on the
  icon (a locator click did nothing); the script clicks its centre.
- 2026-10-20: the Location search shows names only and needs a Name or Code ("%" alone
  finds nothing); the code is found by searching each location code that existing BUs
  use. A location no BU uses yet cannot be resolved; the script stops and asks.
- 2026-10-20: the Role list shows names only (the extra "Role Name" field is not the
  code either); the code comes from matching the user's screen rows with export rows.
- 2026-10-20: the data access search form uses different element ids on "Users with"
  and "Users without Data Access"; the script finds the Role list icon from the visible
  Role field. The page opens on "Users without Data Access".
- 2026-10-20: **a BU created by import gets no reference data set assignments** (0 rows
  in LE_*.csv; a UI-created BU gets 68, all to its default set). The user said the Set
  Assignment step is not needed; tell the user if a BU later needs them.
- Create Order: Cancel asks "Your changes aren't saved ... continue?"; the script answers
  Yes. Nothing is saved.

## Discovery steps

1. Tasks and their Actions (done: Export/Import enabled for both, 2026-10-20).
2. Exports and file layouts, learned from UI-made rows (done).
3. Screens: Create Business Unit lists, data access search, Role list (done).
4. Prove with ZZ_TEST_1424 and the Create Order list (done, 2026-10-20).
5. Later (only if asked): Manager, set assignments, BU data access scope.

## Material

- 2026-10-23 (fast runs, defaults): ZZ_TEST_1097, ZZ_TEST_7361, ZZ_TEST_6290, each with
  Configuration.TEST as Order Manager and Pricing Administrator, in
  `common/created_business_units.json` as ready; ZZ_TEST_5115 got its missing Pricing
  Administrator row.

- ZZ_TEST_9754 (2026-10-21, new run order): business unit; Configuration.TEST as Order
  Manager, Pricing Administrator, Buyer and Anonymous User (the last from the bypassed-check
  test); in `common/created_business_units.json` as ready.

- 2026-10-26 (sheet route proofs, all read back by REST and a second export, both access rows
  active for Configuration.TEST; none in the shared file): ZZ_TEST_BU_3138_ALL (Go Saas Lahore
  Office, Yaqub, Younas, 001 CUSTOMER SITE, active), _SMITH (Smith, Aron, ENTERPRISE), _INACTIVE
  (Status I), _NOLOC (no location), _OUTSIDE (GoSaaS Labs Location, set SET0001, default set
  COMMON), _B1 and _B3 (the good rows next to the bad one), _CAPS, "ZZ_TEST_BU_3138_CAPS " (trailing
  space, made by Oracle as a separate business unit), ZZ_TEST_BU_3138_L240_XXX... (240 characters),
  _ACC (access-missing test, completed by the rerun), _RUN (page `--run`, Smith, Aron, no location).
  Refused / never made: _B2BAD, _L241_..., zz_test_bu_3138_caps, _D1, _NOROLE.
- `manual-notes/` - nothing yet.
- Test data in this TEST pod (the scripts never delete): business unit ZZ_TEST_1424
  (Go Saas Lahore Office, 001 CUSTOMER SITE, active) and its data access row
  Configuration.TEST / Order Manager, 2026-10-20; ZZ_TEST_7669 (BU only, no access row,
  2026-10-20); ZZ_TEST_5950 (defaults, BU by export/import on classic + access row by
  REST, 2026-10-21); ZZ_TEST_3079 (defaults, the first page `--run`, BU + access row
  Configuration.TEST / Order Manager + Create Order list all verified, 2026-10-21);
  ZZ_TEST_5115 (defaults, the clean page `--run` that proved the interface, 2026-10-21).
