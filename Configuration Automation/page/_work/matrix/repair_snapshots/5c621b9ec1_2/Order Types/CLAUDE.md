# Order Types

Adds **lookup codes to an existing lookup type** (the order types). Preferred route:
**REST** (`standardLookups/<type>/child/lookupCodes`); automatic fallback: the Oracle
UI export/import of the task **Manage Order Lookups** (Setup and Maintenance > offering
**Order Management** > functional area **Orders**). Task code (export metadata
`ObjectShortName`): `DOO_MANAGE_ORCHESTRATION_LOOKUPS`.
Lookup type that holds the order types here: **`ORA_DOO_ORDER_TYPES`** (meaning
"Type of Sales Order", module Decomposition, configuration level User,
REST access Authenticated). Found under its default name on 2026-10-19.

Status summary: **REST route PROVEN** 2026-10-21 (ZZ_TEST_2868, created and verified
by GET, offered on Create Order; about 1.5 minutes). The Playwright export/import route
is the automatic fallback: PROVEN on the Redwood Set Up page 2026-10-20, **built for
Redwood, not yet re-proven on the classic layout** that Oracle is back on. Only manual
step: the one-time browser sign-in (for the Create Order check and the fallback).

**A lookup code alone may not complete an order type.** Using a new order type on
sales orders can also need transaction type / assignment rules, orchestration
process assignment, document sequences, etc. Those are separate configuration
steps, to be added later as their own folders or steps.

## Input rules

Check every request against this before doing any work (root CLAUDE.md > Input rules).
One plain request is enough: "add order type X with meaning Y" (everything else has a
default). The request file is `ordertypes.json` (see How to do it).

| Request key | Screen column / REST field | Required? | Default | Kind | Valid values, read live |
|---|---|---|---|---|---|
| `code` | Lookup Code / `LookupCode` | **required** | - | free text, max 30, case-sensitive | must not exist yet: `GET .../lookupCodes?finder=LookupCodeFinder;LookupCode=<code>` |
| `meaning` | Meaning / `Meaning` | **required** | - | free text, max 80 | must be unique in the type: compare with `Meaning` of all codes (`GET .../lookupCodes`) |
| `display_sequence` | Display Sequence / `DisplaySequence` | optional | next number after the highest existing one (printed) | whole number | any; duplicates allowed |
| `enabled` | Enabled / `EnabledFlag` | optional | true (`Y`) | true/false | - |
| `start_date` | Start Date / `StartDateActive` | optional | **empty** | date `YYYY-MM-DD` or `"today"` | `"today"` = Oracle's today minus one day |
| `end_date` | End Date / `EndDateActive` | optional | empty | date `YYYY-MM-DD` or `"today"` | not before the start date |
| `description` | Item Description / `Description` | optional | empty | free text, max 240 | - |
| `tag` | Tag / `Tag` | optional | empty | free text, max 150 | - |
| `lookup_type` (file level) | - | optional | `ORA_DOO_ORDER_TYPES` | pick from Oracle | `GET standardLookups?finder=LookupTypeFinder;LookupType=<type>`; fallbacks DOO_ORDER_TYPES, then meaning "Type of Sales Order"; still not found: ask the user |

There are no pick-from-a-list fields on a code itself; everything is free text, a
number, a flag or a date. REST metadata (`GET standardLookups/describe`, 2026-10-21):
LookupCode, Meaning and EnabledFlag are mandatory on `lookupCodes`; the rest optional.

REQUIRED - if missing or unclear, stop and ask in plain words, all missing items in one message:
- Lookup code (max 30 characters). Codes are case-sensitive (e.g. `Subscription`
  exists in mixed case). An existing code is skipped and reported, never changed.
- Meaning (max 80). Must be **unique within the lookup type**.
  **Before importing, check that the meaning doesn't already exist in the lookup
  type. If it does, stop and tell the user in plain words which code already uses
  it, and ask for a different meaning.** `browser_flow.py` does this check on the
  fresh export and stops before building or importing anything (proven 2026-10-19:
  "ABCABC3: meaning 'ABC ABC Order Type 1' is already used by code ABCABC1").
  Also checked: no meaning twice within one request.

The Manage Order Lookups screen shows no required-field markers in the Lookup Codes
table; Meaning is required by Oracle's lookup data model (lookup code meaning is
mandatory in Oracle's standard lookups REST definition).

OPTIONAL - if missing, the UI default (what a new row on screen gets):

| Field (screen column) | CSV column | UI default |
|---|---|---|
| Display Sequence | `DisplaySequence` | empty on screen; **the script uses the next free number after the highest existing one and reports it** |
| Enabled | `EnabledFlag` | checked (`Y`) |
| Start Date | `StartDateActive` | empty |
| End Date | `EndDateActive` | empty |
| Item Description | `Description` | empty |
| Tag | `Tag` | empty |

The lookup type name is in the request file (`lookup_type`); default
`ORA_DOO_ORDER_TYPES`. If it is not in the export the script tries
`DOO_ORDER_TYPES`, then the type whose meaning is "Type of Sales Order"; if still
not found, ask the user in plain words which lookup type holds the order types.
Never change the lookup type itself (meaning, description, module).

Dates: `YYYY-MM-DD`, or `"today"` = **Oracle's today minus one day**. Oracle's today is
never the PC clock. REST route: the date of Oracle's REST response (`Date` header,
server clock; 2026-10-20 while the PC showed 2026-10-21). Fallback route: read from the
screen: Manage Order Lookups > the lookup type >
Lookup Codes "+" (a new row, never saved) > the empty Start Date's calendar (opened
with the down-arrow key), which opens on Oracle's today with that day selected; the
page is left with Cancel. The script prints a NOTE with the date it used (2026-10-20).

## Route status

- **REST (standardLookups/ORA_DOO_ORDER_TYPES/child/lookupCodes): PROVEN** 2026-10-21.
  ZZ_TEST_2868 (meaning = code, display sequence 24 assigned, enabled, no dates):
  POST HTTP 201, GET by `LookupCodeFinder` returned every field as sent, all 18 other
  codes unchanged, Create Order > Order Type accepts it. My login may create codes
  through REST (no 403). `--check` (GET only) proven the same day. About 95 seconds.
- **Fallback, CSV export/import via Playwright: built for Redwood, not yet re-proven
  on classic.** It runs automatically when REST fails or is refused (the output says
  "REST route failed ... Switching to the Playwright export/import fallback route"),
  or with `--fallback`. It first reports which Setup and Maintenance layout it sees
  (Redwood or classic). If its Redwood-era steps fail on classic, repair them in this
  folder (Self-repair rule) and record the result here.
- **2026-10-20: Oracle moved Setup and Maintenance to the new Redwood "Set Up" page.**
  `common/browser.py` was rewritten for it. On the new screens, `--check` passed and
  so did `--dry-run`: a real export completed with 1/1 objects Successful and was
  downloaded. The new import step (shared `import_csv()`) was proven by a Payment
  Terms import the same day (ZZ_TEST_3593). **Full run PROVEN on the new screens**
  the same day: ZZ_TEST_4833 (meaning = code, start date 2026-10-17 = Oracle's today
  2026-10-20 minus 3 days, display sequence 23 assigned) imported 1/1 Successful. The
  after-export and the screen showed every value (start 10/17/26 on screen, no
  time-zone shift), and the 4 types and 21 other codes were unchanged.
- **CSV via Playwright (UI only): PROVEN** (2026-10-19, clean runs):
  - ABCABC1 (all fields): Display Sequence 10, Enabled, Start Date 2026-10-19,
    Meaning "ABC ABC Order Type 1", Description "Custom POC Order Type for Automation
    Testing". Import 1/1 objects, 0 errors; after-export and screen show every value;
    start date unchanged (2026/10/19 in the file, 10/19/26 on screen: **no time-zone
    shift**); existing types and codes unchanged.
  - ABCABC2 (required only): Meaning "ABC ABC Order Type 2". Defaults confirmed:
    display sequence 11 (script: next after the highest), Enabled Y, start/end date,
    description and tag empty (Oracle does not fill a start date).
  - Each run: about 4 minutes (export + import + export + screen check).
- **REST CSV route (setupTaskCSVExports/Imports for DOO_MANAGE_ORCHESTRATION_LOOKUPS):
  UNTESTED, likely preferred later.** Read-only check 2026-10-19: ExportSupportedFlag
  = true, ImportSupportedFlag = true. Same files as the "Lookup types" folder's CSV
  route. Not used: the direct `lookupCodes` REST route above (PROVEN 2026-10-21) is
  simpler and is the preferred route now.

## How to do it

From the project root:

```
python "Order Types/browser_flow.py" --check     # read-only through REST (GET only)
python "Order Types/browser_flow.py"             # full run: REST, fallback if REST fails
python "Order Types/browser_flow.py" --check-ui  # read-only check of the fallback screens
python "Order Types/browser_flow.py" --fallback  # force the export/import route
python "Order Types/browser_flow.py" --dry-run   # fallback: export + build zip, no import
```
(Page commands `--spec`, `--options lookup_type`, `--run`: see Page interface.)

REST run, step by step: GET the lookup type (with fallbacks) and all its codes -> skip
codes that exist (printed with their values) -> stop on a meaning already used ->
assign missing display sequences -> POST each new code to the `lookupCodes` link Oracle
returned -> GET each new code back and compare every field -> GET all codes again:
every other code unchanged -> Create Order (Order Management work area > Create Order >
Order Type: the new meaning is accepted; left with Cancel > Yes, nothing saved).
`--check`: the same GETs and plan, printing what would be created; no POST, no browser.
If the first POST fails (e.g. HTTP 403 "no permission"), nothing was created and the
whole request goes to the fallback; if a later POST fails, the run stops and says which
codes were created (a rerun skips them).

Request file `Order Types/ordertypes.json`:

```json
{"lookup_type": "ORA_DOO_ORDER_TYPES",
 "codes": [{
   "code": "MY_ORDER_TYPE",            // required
   "meaning": "My Order Type",         // required, unique within the type
   "display_sequence": 11,             // optional; default next free number
   "enabled": true,                    // optional; default true
   "start_date": "2026-10-19",         // optional, YYYY-MM-DD
   "end_date": "2027-12-31",           // optional, YYYY-MM-DD
   "description": "...",               // optional ("Item Description" on screen)
   "tag": "..."                        // optional
 }]}
```

(Comments are documentation only; the real file is plain JSON. Unknown field names
are rejected so nothing is silently dropped.)

What `browser_flow.py` does (via `common/browser.py` OracleUI):
1. Prints host and ORACLE_ENV, refuses production, validates the request.
2. Fresh export: Setup and Maintenance, Offering = Order Management, Orders, task
   list Show = All Tasks, Manage Order Lookups > Actions > Export to CSV File >
   Create New, Show = All, Submit, follow the process by name on View All, require
   Completed successfully / Ready for download / all objects / 0 errors, download.
3. Finds the lookup type; skips codes that already exist; stops if a meaning is
   already used in the type; assigns missing display sequences.
4. Appends the new rows to `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv` (who columns copied
   from the type's most recent user-made code, every other column empty unless
   requested). Every existing row stays byte-for-byte; every file appears once.
5. Import: Actions > Import from CSV File > Create New, `set_input_files`, Submit,
   follow on View All, require Completed successfully / Ready for data validation /
   all objects / 0 errors.
6. Second fresh export: every requested value of every new code (incl. sequence and
   dates; a one-day date difference would mean a time-zone shift) and all existing
   rows unchanged (who columns ignored).
7. On screen: Manage Order Lookups, search the type, select it, read each new code's
   row (sequence, enabled, dates, meaning, description, tag); leave with Cancel.
8. Deletes `_work/` only after a verified success; keeps it (with screenshots) on failure.

Manual click path (reference): Setup and Maintenance > Offering drop-down "Order
Management" (page "Setup: Order Management") > Orders > Show "All Tasks" > Manage
Order Lookups > search Lookup Type > select the row > Lookup Codes "+" > fill the
row > Save and Close.

`--check` (read-only, proven 2026-10-20): validates ordertypes.json; opens Actions > Export
to CSV File > Create New and Import from CSV File > Create New, confirms their fields
and Submit, leaves each with Cancel; searches the lookup type on Manage Order Lookups
and reports for each requested code whether it is on screen (would be skipped) and
whether its meaning is already used; reads Oracle's today (see Dates); leaves with
Cancel. Nothing is saved or submitted.

## File layout (export of Manage Order Lookups)

Only 1 business object; the export holds just the order lookups (4 types on
2026-10-19: ORA_DOO_LINE_TYPES, ORA_DOO_ORDER_TYPES, TEST LINE TYPES,
TEST LINE TYPES 1) and their codes. Same file format as the "Lookup types" folder.

| File | Columns |
|---|---|
| `FND_APP_STANDARD_LOOKUP.csv` | LookupType, Meaning, Description, CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, LastUpdateLogin, ModuleId, CustomizationLevel, RestAccessSecured, BossAppPackageName, BossAppPackageVersion, BossModuleName, BossIdentifier |
| `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv` | FND_APP_STANDARD_LOOKUP.LookupType, LookupCode, Meaning, Description, EnabledFlag, StartDateActive, EndDateActive, DisplaySequence, CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, LastUpdateLogin, Tag |
| `ASM_SETUP_CSV_METADATA.xml` | ObjectShortName DOO_MANAGE_ORCHESTRATION_LOOKUPS; keep unchanged |

Screen column "Item Description" = CSV `Description`. Dates in the CSV are
`YYYY/MM/DD`; on screen `m/d/yy`. UTF-8, no BOM, every field quoted, `\n` line endings.

Existing user-made codes of ORA_DOO_ORDER_TYPES on 2026-10-19 (sequence): Subscription (2),
AMNA_STANDARD_ORDERS (3, not "AMNA_STANDARD"), IMTENAN_STANDARD (4), ABDULLAH_STANDARD (5),
RETURN_STANDARD (6), CH_RETURN (7), CH_TEST (8), ZZ_POC_STANDARD_ORDER (10), STANDARD (none).

## Page interface

Contract: root CLAUDE.md > Page interface (helper `common/page.py`). **PROVEN 2026-10-21.**
One order type per `--run`; the request file and the normal commands are unchanged.

```
python "Order Types/browser_flow.py" --spec
python "Order Types/browser_flow.py" --options lookup_type
python "Order Types/browser_flow.py" --run '{"code": "RUSH_ORDER", "meaning": "Rush Order"}'
```

| Key | Label | Required | Type | Placeholder | Default |
|---|---|---|---|---|---|
| code | Order type code | yes | text | RUSH_ORDER | - |
| meaning | Name shown to users | yes | text | Rush Order | - |
| description | Description | no | text | Orders shipped the same day | empty |
| display_sequence | Position in the list | no | number | 30 | next after the highest |
| enabled | Active | no | yes-no | yes | yes |
| start_date | Start date | no | date | 2026-10-21 | empty ("today" = Oracle's today minus one day) |
| end_date | End date | no | date | 2027-12-31 | empty |
| tag | Tag | no | text | INT | empty |
| lookup_type | Order type list | no | pick | Type of Sales Order | ORA_DOO_ORDER_TYPES |

**Drop-down samples (2026-10-21).** The page's Order type list drop-down shows only values
that have created an order type in this project (`SAMPLES` in `browser_flow.py`,
`"list": "samples"`): **Type of Sales Order (ORA_DOO_ORDER_TYPES)**, proven by ABCABC1,
ABCABC2, ZZ_TEST_4833, ZZ_TEST_2868, ZZ_TEST_9464 and more. **A value joins the samples only
after a real, verified create** (a code created in it and read back by GET and on Create
Order). Another value can be typed: `--run` checks it against the live search (tried:
"Nope" -> NOT_IN_ORACLE). The live search stays behind a switch:
`python "Order Types/browser_flow.py" --options lookup_type --all`.

Pick lists: `lookup_type` is read live through REST the way the run looks for the type
(`standardLookups` LookupTypeFinder for ORA_DOO_ORDER_TYPES and DOO_ORDER_TYPES, then
`q=Meaning='Type of Sales Order'`); value = lookup type, label = its meaning. On
2026-10-21 it returned one: Type of Sales Order (ORA_DOO_ORDER_TYPES).
Extra plain checks in `run_request` (the contract has no field for them): length limits
(code 30, meaning 80, description 240, tag 150), whole-number position, end date not
before start date; then a read-only REST look: an existing code -> `skipped` result with
its values, a meaning already used by another code -> stop in `checking` naming that code.
Steps: reading 5, checking 20, creating 50, verifying 85, `order_screen` 92 ("Checking
that it shows on Create Order"), done 100. If REST is refused, the run uses the
fallback and says "Creating it in Oracle another way". Result `created` = the code as
the REST GET returned it. Result "where": Setup and Maintenance > Order Management >
Orders > Manage Order Lookups > Type of Sales Order; and the Order Type list on Create Order.
Repeating rows: none (one code per run; the command line still takes several).
Tried 2026-10-21: `--spec` OK; `--options lookup_type` OK; `--options code` ->
NOT_A_LIST_FIELD; `--run` without a meaning -> "Please fill in Name shown to users.";
list value "Nope" -> NOT_IN_ORACLE listing "Type of Sales Order"; meaning "abdabd" ->
stopped naming ABDTEST; ABDTEST -> skipped; full `--run` ZZ_TEST_9464 (meaning = code,
description "Page interface test"): all progress lines, POST 201, GET matched every field
(sequence 28 assigned), 22 other codes unchanged, offered on Create Order. 40 seconds.

## Upload sheet (2026-10-25)

The page's upload sheet has an **Order Types** tab (root CLAUDE.md > The upload sheet >
Modules), laid out as the user's `Best_Start_with_Order_Types.xlsx`: Lookup Type (fixed "Type
of Sales Order", empty = filled for you), Lookup Code *, Display Sequence, Enabled (Yes/No,
empty = Yes), Start Date, End Date, Meaning *, Item Description, Tag. One row = one order
type = one `--run` of this folder, run one after another in sheet order. Column -> request key:
lookup_type, code, display_sequence, enabled, start_date, end_date, meaning, description, tag.
Empty Start Date: the preview shows "Oracle's today minus one day (<date>)" and sends that date.

**`--plan '<request or JSON list>'` (read-only, GET only)** gives the preview what a run would
do, with this folder's own rules (`meaning_clashes()` and `assign_sequences()`, split out of
`plan_codes()`, which the run still uses unchanged): an existing code (exact, case counts) ->
`skipped` "already exists ..., so it will be skipped; nothing is changed"; a meaning another code
uses (capitals ignored) -> a problem naming that code; an empty Display Sequence -> the number
the run will assign ("36 (highest existing 35 + 1)"; later rows count the rows above); a given
sequence that others use -> a note; a code that isn't capitals, digits and "_" -> the note "Not
proven: ..." (Oracle hasn't been tried with spaces or small letters). Duplicates inside the sheet,
required columns, dates, End Date after Start Date (and after Oracle's today), whole numbers and
Yes/No are the page's own checks. About 5 s for a sheet.

**Failures say what was saved** (`--run` `error.detail` `{"message", "saved", "registry_id": null}`):
"no" before any create, "yes" after a create (e.g. the check after it failed), "maybe" when the
fallback stopped during its import. Text ends with "Nothing was saved in Oracle." / "Order type X
was created in Oracle, but checking it didn't finish." / "... may have been created ...". Only
"no" rows go into the failed-only sheet.

Tested through the page 2026-10-25 (Oracle test pod, REST route, no repair):
- (a) customers tabs empty, two rows: **ZZ_TEST_3435** (Display Sequence 60, Enabled Yes, Start
  2026-10-22, End 2027-12-31, Meaning "ZZ_TEST_3435 Game Pre-Order", Item Description "Pre-order
  sales for upcoming game releases", Tag GAMING) and **ZZ_TEST_7981** (Display Sequence empty ->
  61, Enabled **No**, Start empty, End 2027-06-30, Meaning "ZZ_TEST_7981 Disabled Order",
  Description "Enabled No test", Tag TAGB). Preview: "Customers: there are no rows ..." and both
  OK. Created in 56 s; every column **accepted and read back** by GET (ZZ_TEST_3435 also offered on
  Create Order; ZZ_TEST_7981 not active, so that check is left out). First proof of End Date,
  Tag, Enabled = No, Start Date and a chosen Display Sequence through REST.
- (b) the same sheet again: preview "Already there: will be skipped" for both; Create: 2 skipped,
  0 created; LastUpdateDate still equals CreationDate for both (nothing changed).
- (c) meaning "abdabd" (ABDTEST), code ZZ_TEST_C2 twice, Start "22/10/2026", End before Start,
  Display Sequence 7.5, Enabled "Maybe", meaning twice with other capitals, code "zz test c4":
  8 red problems at once plus the yellow "Not proven" note; Create refused ("not ready").
- (d) every tab empty: "There is nothing to create ..."; (e) offline (page batch code, folder runs
  replaced): customer + 3 order types, order type 2 refused with saved "no", 3 already there:
  the others ran, cards Created / Failed ("Nothing was saved in Oracle.") / Already there, the
  failed-only sheet "Failed rows.xlsx" holds only order type 2's row, the run summary counts
  "Already in Oracle, skipped (nothing changed): 1".

## Preview versus Create (2026-10-26)

- No Oracle refusal of an order type has ever been recorded (all runs HTTP 201); the rules come from
  the same lookup code object (Lookup types folder).
- **Lengths in the preview:** code 30, meaning 80, description 240, tag 150 are now checked by `--plan`
  (before: only at `--run`).
- **A refused value is a plain refusal, not a repair:** an HTTP 400 on the create (e.g. FND-7103) used to
  switch to the export/import fallback (not re-proven on classic) and could end in an automatic repair.
  Now `RestRefused` -> INVALID_REQUEST, saved "no", `detail.problems` [{field, value, reason}] (tested
  offline with a simulated 400; nothing was sent to Oracle).
- **Capitals:** Oracle compares meanings and codes exactly (proven 2026-10-26 in the Lookup types
  folder: "ALPHA" next to "Alpha", code "a1" next to "A1" were saved). This folder and the sheet still
  treat meanings that differ only in capitals as the same: a folder rule, stricter than Oracle, kept so
  that two order types aren't shown to users with the same name.
- Small letters in a code are proven (teest, test123456), so the "Not proven" note now only names spaces
  and other signs.
- End Date equal to Start Date or in the past: Oracle accepts both (teest); the page refuses them (page rule).

**Still only at Create:** codes with spaces or other signs; Display Sequence above Oracle's number limit.
**Pause and ask (on since 2026-10-26):** a meaning already used (the run's own check) and any HTTP 400 give
`detail.problems` with value, reason and suggestions (`free_values()`: "<meaning> (<code>)", "<meaning> 2", ...;
codes "<code>_2"); the page asks right after that row. Proven 2026-10-26: ZZ_TEST_6142_OTA "ZZ OT 6142 A", meaning
taken after the preview by ZZ_TEST_6142_OTB -> asked -> "ZZ OT 6142 A (ZZ_TEST_6142_OTA)" -> created and offered
on Create Order.

## Related folders

None noted. (If this configuration needs another folder's object, note it here, tell
the user and wait for their go-ahead before writing any code.)

## Sample requests

- "Add order type ZZ_WEB_ORDER." -> ask only for the meaning if it isn't clear; or "with
  the same name as its meaning" -> `{"code": "ZZ_WEB_ORDER", "meaning": "ZZ_WEB_ORDER"}`.
- "Add order type RUSH_ORDER, meaning Rush Order, starting today." -> start_date
  "today" (Oracle's today minus one day).
- "Add order type INTERNAL, meaning Internal Order, sequence 30, disabled, tag INT."
- "Add order types A1 (Alpha) and B1 (Beta) ending 2027-12-31."

## Known gotchas

- 2026-10-26: **Lost clicks on Oracle's busy pages: every screen step checked and done again** with the shared
  retry helper `ui.retry()` (`common/browser.py`: up to 3 tries, a short pause and a fresh wait each time, then one
  clear failure "Oracle's <step> after 3 tries", which `--plan` passes to the page): the Manage Order Lookups search
  (now the helper), the type's row (`codes_shown()`: clicked again until its codes show, soft), the on-screen code
  check (read when the rows stop changing), the add-row of the unsaved table, the Start Date calendar (never a
  second key press while it shows), Cancel (`leave_without_saving()`, the screen has closed), the Navigator (was
  3 s and one look), the Order Management work area, Create Order (heading) and leaving it with Cancel / Yes.
  **Not changed:** this folder opens tasks with the shared Redwood `ui.open_task` also on the classic page (known,
  reported 2026-10-26, not fixed here); the REST create and the export/import fallback's Submit are never retried.
- 2026-10-25: Oracle's date (REST `Date` header, UTC) turned from the 24th to the 25th between a
  preview (05:00 local) and its run a minute later, so `"today"` gave start 2026-10-24 where the
  preview had shown 23 October (ZZ_TEST_7981). The page now sends the preview's date itself.
- 2026-10-25: the `--run` result said "it shows on Create Order" also for a code that is not
  active today (Enabled No / outside its dates), whose Create Order check is left out. It now
  says it isn't active and that check was left out (`active_today()`, shared with `run_rest()`).

- 2026-10-21: Oracle is back on the classic (ADF) layout. The REST route does not
  depend on the layout. The fallback (export/import) was rebuilt for Redwood on
  2026-10-20 and has not run on classic since.
- 2026-10-21: the REST response's server date was 2026-10-20 while the PC showed the
  21st: Oracle's clock is behind the PC.
- 2026-10-21: the browser sign-in had expired; REST (Basic auth) still worked. Only the
  Create Order check and the fallback need the saved sign-in.

- 2026-10-20: since the Redwood Set Up page, the first Search click on the classic Manage
  Order Lookups page could be lost ("No search conducted"). `search_lookup_type()`
  in this folder retries the search up to 3 times.

- Setup and Maintenance opens the user's LAST offering. `OracleUI.open_offering()`
  switches the Offering drop-down (`a[aria-label='Offering']`, options
  `li[role=option]`) when the title is not "Setup: Order Management". The address
  is the same for every offering (`/fscmUI/faces/FuseTaskListManagerTop`).
  Switching changes the user's remembered offering; other scripts switch back
  themselves (Payment Terms -> Financials, checked 2026-10-19).
- The Orders task list defaults to **Required Tasks**, which hides Manage Order
  Lookups. `find_task()` switches it to All Tasks.
- ADF drop-downs: a plain `select_option` was sometimes ignored (no refresh) when
  done after the page had been idle. `OracleUI.choose()` focuses, chooses and
  presses Tab, which refreshes reliably.
- The export page lists no business objects even with Show = All; the results page
  shows the real count (1).
- In the search results, the lookup type's Meaning and Item Description are
  editable fields: never type there. The script only reads the codes table and
  leaves with Cancel.
- Display sequences are not unique (ABCABC1 and ZZ_POC_STANDARD_ORDER both use 10);
  a reused number only affects list order. The script notes it.
- The task list resets to "Required Tasks" every time the area is opened; the
  script switches to All Tasks each time (seen on every run).
- Saved sign-in expired overnight (seen 2026-10-20): the script stopped before the
  first export; after `login_once.py` the same request ran cleanly.
- 2026-10-20: the Start Date calendar icon of a new code row is clipped in the narrow
  column and cannot be clicked; the script opens the calendar with the down-arrow key
  (its own helper `calendar_today()`). The codes table is redrawn while working, so
  the field is pinned by its element id (a position-based locator pointed at another
  row's Start Date).
- Processes here finish fast (often already "Completed successfully" on the first
  history check).

## Discovery steps

1. Find the task and its offering/area (done: Order Management > Orders > Manage
   Order Lookups, task list filter All Tasks).
2. Fresh export, learn the layout from existing codes (done 2026-10-19).
3. Check the screen's defaults for a new code row (done: Enabled checked, rest empty).
4. Prove with dummies ABCABC1 (all fields) and ABCABC2 (required only). (done 2026-10-19)
5. Later: the REST CSV route (supported flags are true), and the other order-type
   setup steps (assignment rules, orchestration).

## Material

- `manual-notes/` - nothing yet.
- Test codes in ORA_DOO_ORDER_TYPES in this TEST pod (the scripts never delete):
  ABCABC1 and ABCABC2 (browser_flow.py, 2026-10-19), ZZ_DEMO_ORDER22 (meaning
  "ZZ Demo Sales Order 22", seq 20, browser_flow.py, 2026-10-20). ZZ_DEMO_ORDER
  (meaning "ZZ Demo Sales Order", seq 20) also exists. ZZ_TEST_6387 (meaning = code,
  start 2026-10-17, seq 22, browser_flow.py, 2026-10-20), ZZ_TEST_4833 (meaning = code,
  start 2026-10-17, seq 23, the first Order Types import on the Redwood screens, 2026-10-20),
  ZZ_TEST_2868 (meaning = code, seq 24, the first code created through REST, 2026-10-21),
  ZZ_TEST_9464 (meaning = code, description "Page interface test", seq 28, the first
  `--run` from the page interface, 2026-10-21), ZZ_TEST_3435 (seq 60, enabled, 2026-10-22 to
  2027-12-31, tag GAMING) and ZZ_TEST_7981 (seq 61, **disabled**, 2026-10-24 to 2027-06-30, tag
  TAGB), the first through the upload sheet, 2026-10-25. ZZ_POC_STANDARD_ORDER was
  created before this folder existed and was left untouched.
