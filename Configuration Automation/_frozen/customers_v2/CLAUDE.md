# Configuration Automation (Oracle Fusion Cloud)

Automates Oracle Fusion setup configuration from requirement files, without UI
clicking where possible. Lookups are the proof of concept; Order Management
configuration comes later. Works on any Oracle Fusion environment; which one is
set explicitly in `.env` (see Environment rules).

## How to use this project

New here? Unzip the project, open the folder in Claude and say anything: Claude
runs the one-time setup for this PC (see First-run setup). You only fill in your own
Oracle login in `.env` and sign in once in a browser window. `README.md` describes
the same steps. After that, just describe what you want in plain words, e.g. "add
a lookup type for order hold reasons in Order Management with codes A and B".
Claude works out which configuration it is, asks for anything that's missing, then
creates it in Oracle and checks the result. You never need to name folders,
scripts, task codes or IDs.

## First-run setup

At the start of any session, if `.setup_ok` does not exist in the project root
(setup has not passed on this PC) or the user asks to set up, run this procedure
before doing anything else. Claude runs every command itself; never ask the user to
run commands. Commands below are for Windows PowerShell; adapt if needed.

a. `python --version` (on Windows also try `py -3.12 --version`). If Python 3.12+
   is missing: `winget install Python.Python.3.12`. If winget needs admin approval,
   is blocked, or Python is still not found afterwards (a new terminal may be
   needed), tell the user in plain words and stop and wait.
b. `python -m pip install -r requirements.txt` (requests, python-dotenv, playwright).
c. `python -m playwright install chromium`. If that is blocked (company policy,
   no download access), set `CHANNEL = "chrome"` in `common/browser.py` (uses the
   installed Google Chrome) and tell the user.
d. If `.env` does not exist: copy `.env.example` to `.env` (empty values) and tell
   the user in plain words to open `.env`, fill in ORACLE_USER, ORACLE_PASS,
   ORACLE_HOST and ORACLE_ENV themselves, save it, and say "done". Never read,
   print or ask for the values.
e. After "done": `python common/check_setup.py`. It checks Python, packages, that all
   `.env` keys are filled (values never shown), ORACLE_ENV rules, one read-only REST
   call and that the browser starts. Fix what you can; for anything else give the
   user the exact plain-language fix from its output.
f. Run `python common/login_once.py` yourself (in the background). A browser window
   opens; tell the user to sign in there themselves and say "done" (the window
   closes by itself once signed in). Skip this on production (ORACLE_ENV prod).
g. `python common/check_setup.py --final`. When everything passes it creates the
   `.setup_ok` marker; tell the user the project is ready.

`.setup_ok`, `.session/` (saved browser sign-in) and `.env` are per PC: never share
them (see SHARING.md). To redo setup, delete `.setup_ok`.

## Clean-up rule (every response, the user's standing rule since 2026-10-26)

When a response is finished, stop everything Claude started during it: demo or stub servers, fake Claude or
Oracle tools, headless browsers, Playwright processes, background jobs, browser-pane tabs and any other process
Claude launched. Leave only the real page on port 8765, and only if it was running before or Claude restarted it
for the user.
- Never stop the real page while a run is active: check first (its `page/_work/server.log` and `/api/job/...`).
- Stop only processes Claude started; never touch anything else (the user's own page, editors, apps).
- Temporary working files may stay in `page/_work/`.

## Routing rule

When a user gives a request, do this first:
1. Read the Configuration index below and pick the folder that matches the request.
2. Read that folder's CLAUDE.md fully (Route status, Input rules, How to do it).
3. Check the request against its Input rules. Ask in plain words for anything
   required that is missing, all in one message.
4. Use the route marked PROVEN. If it is PARTIAL or UNTESTED, follow that folder's
   Discovery steps and wait for my confirmation.
5. If no folder matches, say so in plain words and offer to start a new
   configuration folder by copying `_template/` (see New folder template). Never
   improvise against Oracle without a folder.
6. If more than one folder could match, ask which one the user means.
Users speak in plain business language. Never require them to name folders, scripts,
task codes or IDs.

## Configuration index

| Folder | Handles requests like | Status |
|---|---|---|
| Lookup types | create lookup types and lookup codes, "add a lookup", "new lookup type in <module>", "add codes to lookup X" | **everything Manage Standard Lookups can create PROVEN 2026-10-25** (new types by CSV import, several per run; new codes on existing User / Extensible types by REST; modules by name from the screen; read-back per type and code with Oracle's reasons; read-only `--plan`; ZZ_TEST_LK_8806_*, see `Lookup types/sheet_fields.md`); **upload sheet tabs Lookup Types / Lookup Codes 2026-10-25** (preview through `--plan`, Create through `--run-batch`; previews proven, the sheet's Create not yet run in Oracle); CSV route PROVEN; Page interface PROVEN 2026-10-21 (`--spec`, `--options module` / `rest_access_secured`, `--run` with codes as rows, ZZ_TEST_4423) |
| Price Lists | create and approve a price list (header + access set), "new price list for <business unit> in <currency>" | REST route PROVEN (no items/lines yet); Page interface PROVEN 2026-10-21 (`--spec`, `--options business_unit` / `currency` / `access_sets.name`, `--run` with access sets as rows, ZZ_TEST_1567) |
| Payment Terms | create payment terms (installments, due days), "new payment term net 30" | CSV via Playwright UI PROVEN (`browser_flow.py`; classic layout via the folder's `classic_setup.py`, proven 2026-10-21; only manual step: one-time sign-in); Page interface PROVEN 2026-10-21 (`--spec`, `--options set_assignments.set`, `--run` with installments as rows, ZZ_TEST_7166); **every Create Payment Terms field PROVEN 2026-10-25** (percent or amount, Days / Fixed Date / Day of Month + Months Ahead / Calendar, three discounts, any set code, exact name match; read-only `--plan`; several terms per import, a refused term named with Oracle's reason from the import log while the others are saved; ZZ_TEST_PT_8505_*, see `Payment Terms/sheet_fields.md`); **upload sheet tabs Payment Terms / Payment Term Lines / Payment Term Sets 2026-10-25** (preview through `--plan`, Create in one import through `--run-batch`; previews proven, the sheet's Create not yet run in Oracle) |
| Order Types | add order types = new lookup codes in an existing lookup type (ORA_DOO_ORDER_TYPES), "add order type X with meaning Y" | REST route PROVEN (`browser_flow.py`: standardLookups lookupCodes, verified by GET and the Create Order Order Type list); automatic fallback: CSV export/import via Playwright (built for Redwood, not yet re-proven on classic); Page interface PROVEN 2026-10-21 (`--spec`, `--options lookup_type`, `--run`, ZZ_TEST_9464); **upload sheet tab "Order Types" PROVEN 2026-10-25** (module of the sheet, read-only preview check `--plan`, one row = one order type; ZZ_TEST_3435 every column, ZZ_TEST_7981 Enabled No + start date from the preview; same sheet again: both skipped, nothing changed) |
| Customers | create customers (organization or person), Playwright form fill, no export/import: "create customer X with address set Y and supplier site ID Z", "new person customer Jane Doe" | Playwright form fill PROVEN for organizations and persons (`browser_flow.py`; Create Customer form, verified on Manage Customers / Edit Account / Edit Site; only manual step: one-time sign-in). REST can't create a whole customer (no account / account site / address set / purpose / Supplier Site ID), so no REST route. Classic layout (2026-10-21): `--check` and full save proven (ZZ_TEST_2336); Page interface PROVEN 2026-10-21 for organizations (`--spec`, 8 `--options` read from the form, `--run` with purposes as rows, ZZ_TEST_4418); through the upload sheet 2026-10-23 with every field: organization ZZ_TEST_6183 and person ZZ_TEST_1125 Person. **Same name never skipped** (2026-10-23): Oracle's matching warning always answered with Option 2 (create new), the new customer verified by its Registry ID, the preview shows existing same-name customers (`--existing`); proven ZZ_TEST_3727 x2 (130524, then 130527/130530) and person ZZ_TEST_2536 Q Person Jr (130534). **Checked before Create** (2026-10-23): Bill-to Site picked automatically or compared with the address, City / Postal Code against Oracle's geography (`--check-address`, read-only), sign-in renewed at the preview; proven ZZ_TEST_8352 (130554). Address Purposes joined by Customer Name (2026-10-23), proven ZZ_TEST_6619 (130584). **Several customers per sheet** (up to 100, one after another, result card per customer, failed-only sheet; 2026-10-23), proven ZZ_TEST_6842 / 5862 / 7163 (130588, 130591, 130596; about 3 min each); **v2 2026-10-26**: one place path for preview and Create (ABSECON / Dallas / Seattle), place and list refusals red in the preview with suggestions, held instead of stopped when Oracle's places can't be looked up, pause and ask, a message after Save checked in Oracle (see The upload sheet > Customers v2) |
| Business Units | create a business unit: "create business unit X", "also give Configuration Buyer access on it" (defaults: Go Saas Lahore Office, 001 CUSTOMER SITE; always, never replaced: Configuration.TEST (fallback Configuration) as Order Manager and as Pricing Administrator; More options = extra access in addition, added last) | Step 1 business unit: CSV export/import via Playwright PROVEN (REST can't create a BU; classic layout via the folder's `classic_setup.py`); required access Order Manager then Pricing Administrator: REST `dataSecurities` PROVEN (ZZ_TEST_5115, ZZ_TEST_8131), export/import fallback not yet re-proven on classic; then Create Order list, cache check and `common/created_business_units.json`; extra access last, REST only, a rejection is a partial success (no failure, no repair); up-front extra role check (business unit access rows + security context mapping). New run order PROVEN 2026-10-21 (ZZ_TEST_9754 + Buyer), existing business unit "add only missing access" PROVEN the same day; partial result checked offline only (Oracle accepts any held role, so the up-front check is the guard); Page interface PROVEN 2026-10-21 (`--spec`, `--options` location / default_set / user / role / pricing_role, `--run`, ZZ_TEST_5115). **Fast run PROVEN 2026-10-23** (three in a row through `--run`, ok first time, no repair, no sign-in window, both roles verified by REST read-back: ZZ_TEST_1097 37 s, ZZ_TEST_7361 54 s, ZZ_TEST_6290 40 s; was 224-338 s): no before-export (import file from `bu_import_template.json`), import submitted and the new business unit polled by REST every 3 s (no status screen), access rows read only for that user and business unit, parallel reads, browser only to create a business unit; screen checks (second export, Manage Business Units, Users with Data Access, Create Order) only with More options "Check on screen too" or `--check`; Create Order checked in a fresh context without the cached app session cookie (sign-in window last resort only); 6-minute limit per step with timer and slow note; half-made business unit gets only its missing rows, named in the result (ZZ_TEST_5115, 13 s) |

Maintenance rule: Whenever a new configuration folder is created or its status
changes, update this index in the same step. A folder is not complete until it has
a row here and an Input rules section.

## Isolation rules (one folder per request)

- Work inside ONE folder per request. Never edit, import from or run another folder's
  code. Scripts import only `common/` (and code inside their own folder).
- Shared code in `common/` is additive only: add new helpers, never change an existing
  one's behavior. If a folder needs different behavior, give it a helper inside that
  folder.
- Self-repair applies to the current folder only (see Self-repair rule). If a fix
  would need a change in `common/` or another folder, stop and tell the user in plain
  words what and why, and wait.
- Folders don't depend on each other. If a configuration relates to another folder
  (e.g. one object needs another to exist first), don't build the link: write it
  under "Related folders" in that folder's CLAUDE.md, tell the user, and wait for
  their go-ahead before writing any code.
- Each folder's CLAUDE.md documents only that folder: its own PROVEN status, gotchas
  and sample requests.

## Dates: Oracle's today

Oracle's own default date flips at a different time than the PC clock. Never compute
"today" from the PC: read the default date the form or screen shows and use that as
Oracle's today. "today" in a request means Oracle's today minus one day (the user's
rule), and the script prints a NOTE saying which date it used. Where each folder
reads Oracle's today is in its CLAUDE.md. Shared helpers: `OracleUI.parse_screen_date()`
(m/d/yy on screen) and `OracleUI.picker_today()` (an empty date field's calendar opens
on Oracle's today with that day selected; read-only).

## New folder template

New configuration folders are always made by copying `_template/` (script skeleton
`browser_flow.py` with `--check` and the page commands `--spec` / `--options` / `--run`,
`request.json`, `CLAUDE.md` with Input rules, Route
status, Related folders, Gotchas and Sample requests, `manual-notes/`). `_template/` is
not a configuration and has no index row.

Checklist - no folder is marked PROVEN until all hold (and all eight steps of "Adding a
new configuration folder" below are done):
- [ ] Input rules (REQUIRED and OPTIONAL with UI defaults, drop-down values)
- [ ] `--check`: read-only, proves the screens or calls still work, creates/changes/deletes nothing
- [ ] Verification step that reads every requested value back from Oracle
- [ ] Timeouts on every step, with a clear message naming the step
- [ ] Route status section
- [ ] Configuration index row in this file
- [ ] Its own clean `--check` run (and a clean full run with a ZZ_TEST_ dummy)
- [ ] Page interface (see below): `--spec`, `--options FIELD` for every pick-from-a-list
      field, and `--run 'JSON'`, each tried once, plus a `--run` with a missing value
      that stops with a plain message

## Adding a new configuration folder

Every new folder is built the same way, so it shows up on the page as a new card
without any change to the page: the page only reads the Configuration index and asks
each folder's script for `--spec`, `--options` and `--run` (Page interface below). The
script is `<folder>/browser_flow.py` (older REST-only folders use `run.py`; keep the name
a folder already has). Do the steps in order; a folder is **not marked PROVEN until all
eight are done**.

1. **Copy `_template/`** to a new root folder named for the configuration in plain
   words (e.g. `Shipping Methods/`). Rename the request file, fill every TODO.
2. **Learn and prove the chain with a dummy record**, as for the existing folders:
   find the task (offering, functional area) and its screens, and the REST resources
   (`GET <resource>/describe`, finders, LOVs; only documented endpoints or links Oracle
   returns). Check ExportSupportedFlag (Standard workflow for a new configuration type).
   Prove one ZZ_TEST_<4 digits> record end to end: create, read every value back,
   existing records unchanged. Record every finding in the folder's CLAUDE.md.
3. **Implement the Page interface** (`common/page.py`): `SPEC` with plain labels,
   `--options` for every pick-from-a-list field read live from Oracle by the folder's
   route, `--run` with the standard plain-language progress lines (and the folder's own
   steps in between), `rows` fields for repeating groups, a skip result for an existing
   record, plain stops for values Oracle doesn't have. The command line keeps working
   exactly as before (shared flow function, called by both).
4. **Choose the route in this order:** (a) REST for the whole job; (b) otherwise a mix:
   REST for what it can do (lists, existence checks, steps REST can create) and the
   Oracle screens for the rest; (c) the screens (CSV export/import, or form fill when
   there is no export/import) as the **automatic fallback** when a REST call fails or is
   refused (HTTP 403 = no permission). Never a half-made record: if REST can't create
   the whole object, the screens do that part. Say in Route status which route each
   step uses.
5. **Write the folder's CLAUDE.md** from the template: Input rules (REQUIRED, OPTIONAL
   with UI defaults, how each list is read live), Route status per route and step, How
   to do it, Page interface (field table, lists, steps, what was tried), Known gotchas
   (dated), Related folders, Sample requests, Material (test records left in Oracle).
6. **Add a row to the Configuration index** (folder, plain request examples, status per
   route and the Page interface), and the folder to the Layout section.
7. **Test through the page's own output:** the folder's `--check` (read-only) and
   `--spec`; every `--options` (read-only); a `--run` with a missing or invalid value
   (stops with a plain message, nothing created); then one `--run` with a ZZ_TEST_ dummy,
   reading the JSON progress lines and the final result line exactly as the page gets
   them, and checking the verified record. A failure is repaired in the folder
   (Self-repair rule) and the `--run` repeated until it is clean.
8. **Tell the user** in plain words that the folder is ready, which route it uses, what
   the dummy run created and how long it took, and that the page will show it as a new
   card (no page change needed).

Independence (Isolation rules): every folder has its own helpers; it never imports
from, runs or edits another folder; shared code in `common/` only gets additions; a
link to another folder's object is written under Related folders and waits for the
user's go-ahead.

## Page interface

Every configuration folder's script offers three page commands on top of its normal
command line, so a local page can show a form, fill its lists and run a request. The
normal commands (`--check`, `--dry-run`, a plain run from the request file, ...) keep
working exactly as before. The shared helper is `common/page.py`: the script calls
`page.main(SPEC, options_for, run_request)` first thing in `main()`; it handles the
three commands and exits, or returns when none is given. `_template/browser_flow.py`
shows the wiring.

1. `--spec` prints one JSON object describing the form:
   `{"contract": 1, "title", "description", "groups": ["main", "more options"], "fields": [...]}`.
   Title is plain language, description one line. Each field has `key`, `label` (plain
   words), `required` (true/false), `type` (`text`, `number`, `date`, `yes-no` or `pick`
   = pick from a list), `placeholder` (an example), `default` (the Oracle UI default,
   or null) and `group`: required fields are in "main", optional ones in "more options".
   (Types: `text`, `number`, `date`, `yes-no`, `pick`, and `rows` below.)
   `pick` fields also say `"options": "--options <key>"`. Optional `help`: one plain line.
   Optional (added 2026-10-21): `required_when` / `shown_when` `{"<field>": "<value>"}` -
   a field needed or shown only when another field has that value (or its default), e.g.
   Customers' Organization name / First name by Customer type; such a field is in "main"
   and `--run` checks it ("Please fill in ...", "... only applies when ..."). A required
   `pick` with a default uses the default when left out. `"list": "samples"`: the
   drop-down offers short samples, another typed value is checked live by `--run`
   (Price Lists, Customers; their full lists: `--options FIELD --all`).
   Type `rows` is a repeating group (installments: percent and days; codes: code and
   meaning; access sets: name). It has `fields` (its sub-fields, each with `key`,
   `label`, `required`, `type` = one of the five plain types, no rows inside rows, and
   `placeholder` = the example), `min_rows` (0 or more; at least 1 when required),
   `add_label` (the add-row button, e.g. "Add an installment"), `row_label` (one row's
   name, e.g. "Installment") and `default` `[]`. A `pick` sub-field's list is
   `--options <rows key>.<sub key>` (e.g. `--options access_sets.name`).
2. `--options FIELD` prints one JSON object with the valid values of a `pick` field,
   read live from Oracle by the route the folder already uses (REST where possible):
   `{"ok": true, "field", "label", "values": [{"value", "label"}], "read_at": "<UTC time>"}`.
   A field that isn't a pick list gives `{"ok": false, "error": {"code": "NOT_A_LIST_FIELD"}}`.
3. `--run '<JSON request>'` (one record, keys from `--spec`) validates first, then runs
   the folder's normal flow (same skip-existing, never-change, verify rules), printing
   one JSON line per step: `{"step": key, "percent": 0-100, "text": plain words}`.
   Standard steps: `reading` (5, "Reading your request"), `checking` (20, "Checking the
   details with Oracle"), `creating` (50), `verifying` (85, "Checking the result"),
   `done` (100). A folder may add its own lines in between with its own text and percent.
   The last line is always `{"step": "result", "percent": 100, "ok": ...}`:
   - success: `"text"` (what was created, plain), `"created"` (the values as Oracle
     shows them), `"skipped"` (true if it already existed and nothing was touched) and
     `"where"` (where to see it in Oracle, plain navigation words).
   - failure: `"text"` (plain words) and `"error": {"code", "step", "detail"}` for the
     repair handoff. `detail` is machine-readable and may be technical (the exact
     error, screenshot path, list of problems); `text` never is.
   Validation stops before anything touches Oracle data: missing required values,
   unknown keys, wrong numbers, dates (`YYYY-MM-DD` or "today") and yes-no values are
   reported in `reading`; pick values are checked against the live list in `checking`
   (exact or one unique case-insensitive match, never a guess) and the message lists
   the valid ones (`detail[].valid`). A `rows` field arrives as a JSON list of objects
   (`"installments": [{"percent": 50, "days": 30}, ...]`); each row is checked the same
   way, fewer than `min_rows` rows is a mistake, and messages name the row by number
   ("Installment 2: Days is missing."; `detail[].row` holds the number). Pick sub-fields
   are checked against their live list in `checking` (each list read once per run).
   Error codes: `INVALID_REQUEST`, `NOT_IN_ORACLE` (exit 2: the user must change a
   value), `SIGN_IN_NEEDED`, `NO_PERMISSION`, `PRODUCTION_REFUSED`, `SETUP_NEEDED`,
   `TIMEOUT`, `STEP_FAILED`, `VERIFY_FAILED`, `FAILED` (exit 1). Success exits 0.
   Exception (2026-10-23): **Customers never skips by name** (names are not unique in
   Oracle); it always creates a new customer and verifies it by its Registry ID. A rerun of
   the same request after a save (sign-in window, automatic repair) still never duplicates:
   the folder remembers what that request saved (its `_work/`) and verifies that one.
4. Optional, read-only, named by the registry's `same_name_check` (2026-10-23):
   `--existing '<JSON request>'` prints `{"ok": true, "name", "matches": [{"registry_id",
   "name"}]}` (records Oracle already has with this name) or `{"ok": false, "text"}`.
   Only Customers has it; the page shows the result on the preview. Also optional, named by
   the registry's `address_check`: `--check-address '<JSON request>'` prints `{"ok": true,
   "problems": [{"key", "text", "fix"}], "found": {key: text}}` (Customers: City and Postal
   Code against Oracle's geography for the State, read-only). Both also take a JSON list of
   requests and answer `{"ok", "results": [...]}` in the same order, in one browser visit
   (several customers per sheet, 2026-10-23). A `--run` failure may carry `error.detail`
   `{"saved": "no" | "yes" | "maybe", "registry_id"}` (Customers does) for the result card.

Rules: stdout carries only that JSON during a page command (the script's usual prints
go to stderr). No technical words in any text meant for the user: never REST, CSV,
Playwright, export, import, API or JSON in titles, labels, help, step texts, result
or error texts (`page.plain_check()` refuses them, also in `add_label` and `row_label`).
Repeating rows (installments, codes, access sets) use the `rows` type.

## Layout

The root may only contain: `common/`, `_template/`, `page/`, `_frozen/` (snapshots for
regression checks, see The upload sheet > Customers frozen), one folder per configuration
type, `CLAUDE.md`, `README.md`, `SHARING.md`, `requirements.txt`, `.gitignore`,
`.env.example`, the starters `start.cmd` / `start.sh`, and the per-PC files `.env`,
`.setup_ok`, `.session/`. Never create work folders or other files at the root.

`page/` is the local page (not a configuration folder, no index row):
`page/server.py` (standard library only, 127.0.0.1:8765), `page/setup_check.py` (runs one
check of `common/check_setup.py`), `page/look.py` (read-only screen look for repairs),
`page/oracle_today.py` (Oracle's today for the date rules),
`page/workbook.py` and `page/run_summary.py` (the Run summary of a finished run, from the logs),
`page/regression_customers.py` (the Customers regression check),
`page/matrix/` (the offline behaviour matrix: `test_matrix.py` and its Oracle / Claude stubs),
`page/static/` (HTML, CSS, JavaScript) and
`page/_work/` (list cache, run logs, `server.log` with repair costs; never shared).

## The upload sheet (2026-10-23)

The page has no folder cards and no forms: it has one upload of an Excel workbook.
- `page/sheet_definition.json`: every tab and column (label, section, required, type
  text / long-text / digits / date / yes-no / pick, `values` = drop-down, `live` = the
  folder's `--options` field, `check: false`, `default` shown in the preview, `role`/`pair`
  for start/end dates, `key` = the request-file key, `hint` = the sheet's hint row). Every
  column with a `key` is an Oracle field; the one column of our own is Address Purposes'
  **Customer Name** (no `key`, never sent to Oracle; it joins the row to its customer). The
  "Customer Ref" column was removed 2026-10-23. `column_sets` hold columns shared by tabs (`{"use": name}`). The empty
  sheet ("Download the empty sheet") is generated from it: row 1 sections, row 2 labels
  (yellow + " *" required, blue optional), row 3 hints ("Required · ..." / "Optional · ..."),
  drop-downs on rows 4-500, widths = label length + 6 (16 to 30), frozen at B4. Matches the
  user's Customer_upload_sheet layout of 2026-10-23 except the Read me's dummy-row lines and
  the Name / First Name hints (they said "Unique" / "Purposes link to it"; names are not unique).
- `page/sheet_registry.json`: which folder runs which tabs (`record_tabs` with `fixed`
  values, `child_tabs` into a request list, child rules `unique`, `one_yes_per`,
  `within_parent`), `max_records`, `same_name_check`.
  **Several records per upload (Customers, 2026-10-23, replaces "exactly one"):** rows from
  both customer tabs, mixed, up to `max_records` (100; more stops with "The sheet has N
  customers. One upload holds at most 100 customers: split it ..."). Each record is checked
  on its own; the preview shows a summary (customers, how many with problems, about 3 minutes
  per customer to create) and the customers as a list: those with problems first and open,
  then the OK ones, each in sheet order, each with an OK / "N problems" badge and the usual
  table (what the sheet says / what Oracle will get) with its purposes. Create is for the
  whole sheet and stays off until every customer is OK. ("Ship to without Bill to" is now a
  red problem on that customer's Ship to row instead of a stop for the whole sheet.)
  **Join key (2026-10-23, user's sheet design):** Address Purposes starts with the required
  column **Customer Name**; the registry's child `"link": {"column": "Customer Name"}` joins
  each purpose row to the customer whose `link_name` equals it, ignoring upper/lower case and
  extra spaces (also around commas): organization = Name; person = First Name + one space +
  Last Name (First Name alone when Last Name is empty; Middle Name and Suffix not part of it).
  A row naming no customer of the sheet is red ("This address purpose belongs to 'X', but the
  customer in this sheet is 'Y'.", shown in the purposes table, never sent); an empty
  Customer Name is red (required); two customers of one sheet with the same link name stop
  ("Two customers are named X. Give them different names or upload them separately.").
  Names are never assumed unique in Oracle (same-name customers: Option 2, as before). The
  "Ship to without Bill to" stop waits until every purpose row has its customer.
  `same_name_check` (Customers: `--existing`): before Create, the server runs that read-only
  folder command for the record and shows "N customers named X already exist (Registry IDs
  ...). Create will make a new one." on the preview (Customers: Manage Customers search,
  about 20 s; one retry).
  **Everything is checked before Create (2026-10-23)**, so "Create in Oracle" only runs:
  `address_check` (Customers: `--check-address`, the Create Customer form's City and Postal
  Code search dialogs, read-only, about 35 s; runs beside the same-name check) puts a
  City / Postal Code Oracle doesn't have for that City and State in red with the fix; a
  check that couldn't run stops the preview. A child tab's `address_pick` (Customers:
  Bill-to Site) = a column Oracle fills from a list holding only the record's own address,
  offered only on `only_on` rows (Ship to): empty = "Picked automatically" (the text built
  from `text` parts, e.g. "1 Infinite Loop,Suite 5,CUPERTINO, CA 95014"); a typed value must
  equal it ignoring case and extra spaces (else red: "Use '<text>', or leave it empty to use
  this one."); a value on another row is ignored with a note; an `only_on` row without a
  `needs_row` row (Ship to without Bill to) stops the preview. The saved Oracle sign-in is
  checked first: missing or expired -> the sheet is checked offline, the sign-in window
  opens at once ("Please sign in to Oracle" on the preview), and the checks with Oracle run
  after it; Create stays off until then, and Create checks the sign-in once more before the
  run starts.
- `page/workbook.py`: reads the upload (openpyxl, no Claude), checks it, builds the request,
  makes the empty sheet. Tabs in no registry group: "The tab 'X' isn't set up yet"; the
  rest still works. Flow: upload, check, preview (sheet value next to what Oracle gets),
  "Create in Oracle" -> the folder's `--run`, progress, result; automatic repair unchanged.
**How to add a tab:** add the tab and its columns to `sheet_definition.json`; add a group
(or a tab to an existing group) in `sheet_registry.json` naming the folder; every column
`key` must be a field of that folder's `--spec`. Changing a column, drop-down or required
rule = editing `sheet_definition.json` only.
**Checks with Oracle for a whole sheet (2026-10-23):** `same_name_check` and `address_check`
get a JSON **list** of requests (one browser visit for all; the folder answers
`{"ok", "results": [...]}` in order). Address checks are done once per distinct
country / State / City / Postal Code (server `ADDRESS_CACHE`, answers reused for an hour), so
ten customers in one city cost one lookup.
**The run (2026-10-23):** "Create in Oracle" makes one job for the sheet (`new_batch()` /
`run_batch()` in server.py): the records one after another in sheet order, each through its
folder's `--run` exactly as a single run (progress lines, automatic repair, plain failure);
progress shows "Customer 2 of 3: <name>" over the record's own step line. A failed record
doesn't stop the others; nothing asks the user anything. Duplicates after a failed try are
prevented per record by the folder (Customers: one rerun note per customer in its `_work/`;
a verified customer removes only its own note, and `_work/` is kept while another customer's
note is left). Result: a summary (created N of M) and one card per record: created (name,
Registry ID, what Oracle shows now) or failed (plain reason; "Nothing was saved in Oracle.",
or saved / may have been saved with the Registry ID). The failure detail's `saved` ("no" /
"yes" / "maybe") and `registry_id` (Page interface, `error.detail`) decide: if any failed
record saved nothing, "Download a sheet with only the failed customers"
(`/api/job/<id>/failed.xlsx`, `workbook.subset_sheet()`: the empty sheet's layout with only
those records' rows and their child rows); saved-but-unchecked ones are listed separately
with their Registry ID and are not in that sheet.
**Run summary (2026-10-23):** under the result cards of a finished sheet run, a "Run summary"
block: Time (whole run first start to last end; each customer's start, end and duration; the
check before Create when logged), Results (created, failed, saved but not fully checked),
Repairs (each repair with its customer, tokens: total, new, re-read, written, and dollars,
plus a total; or "No repairs. Claude was not used: 0 tokens, $0."), a line when the run came
from a "Failed customers" sheet, and the note that creating a customer uses no Claude tokens.
It comes from `page/run_summary.py`: `summary(run id, job)` returns a plain dictionary of
numbers (what a database could store per run later) built only from what the page already
records: `page/_work/server.log` (event lines with their time; since 2026-10-23 the upload
line says "checked in N s" and the queued line names its upload), `page/_work/logs/<run>.log`
(names the customer of older single runs) and `page/_work/logs/<run>.repair.log` (one
"result" record per repair attempt with its usage and cost), plus the run in memory while
the page runs (each customer's saved state). Nothing missing is guessed: a line without its
number is left out. `lines(summary)` turns it into the plain sentences. Older runs:
`#/summary/<run id>` on the page (`/api/summary/<run id>`) or
`python page/run_summary.py <run id>` (read-only). To add a number: put it in the
dictionary in `summary()` (from a log line the page writes; add the log line in server.py
first if needed), then a sentence in `lines()`.
**How to extend:** more per upload = raise `max_records`. A record tab's `link_name` lists
its name columns; a new child tab joins with `"link": {"column": "<its name column>"}`. A
new folder's `--run` failure should give `error.detail` `{"saved", "registry_id"}` so the
result card can say what was saved (without it: "may have been saved", not in the
failed-only sheet).

### Modules: several kinds of setup in one sheet (2026-10-25)

Each registry group is a **module** (Customers, Order Types). One upload may hold rows for
any of them; each module is checked and previewed on its own, and Create runs them all, one
record after another, in registry order (Customers first, then Order Types).
- **Empty-module rule:** a module whose tabs are missing or have no rows gets one plain line
  in the preview, "<Module>: there are no rows for this in the sheet, so nothing will be
  created." (`modules[].text`; child rows without a record are counted in that line). It is not
  an error and doesn't block Create for the other modules. **No module with rows** = the stop
  "There is nothing to create: ...". A tab the page doesn't know is still reported and left out.
- `workbook.preview()` returns `modules: [{"name", "record", "count", "minutes_each", "text"}]`;
  the page shows the empty-module lines and, with one module, exactly the old wording
  ("3 customers in the sheet", "about 3 minutes each"); with several, "1 customer and 2 order
  types". Run cards use each record's own word; the closing line counts skipped ones
  ("Created 2 of 4 rows: 1 already existed and was skipped (nothing changed), 1 failed.").
- **How a module plugs in** (additive; Customers' entries are never edited): (1) its tab in
  `sheet_definition.json` (columns with `key` = the folder's `--spec` keys); optional column
  keys `width` / `format: "general"` (copy a user's sheet), `default_text` (preview wording),
  `default: "today-1"` + `send_default: true` (the preview shows Oracle's today minus one day
  and sends **that date**, not the word "today", so Oracle gets what the preview showed even
  if Oracle's date turns before the run; seen 2026-10-25 at midnight UTC). (2) a group in
  `sheet_registry.json`: `folder`, `record` (the word), `max_records`, `minutes_each` (preview
  estimate, default 3), `record_tabs`, `child_tabs` (`{}` = none), optional
  `unique_records` (`[{"column", "ignore_case"}]`: a value only once per sheet, later rows red)
  and optional `oracle_check` (a read-only folder command, e.g. Order Types `--plan`, given the
  JSON list of the group's requests in sheet order, answering `{"ok", "results": [{"ok",
  "skipped", "problems": [{"key","text","fix"}], "found": {key: note}, "fills": {key: text}}]}`;
  the server puts `problems` in red (Create off), `found` as notes, `fills` as "What Oracle will
  get" with "Filled in by the automation", and `skipped` as "Already there: will be skipped";
  a check that can't run stops the preview). (3) the folder's `--run` result `skipped: true`
  for an existing record and `error.detail.saved` on failures. Failed-only download name:
  "Failed customers.xlsx" / "Failed order types.xlsx" / "Failed rows.xlsx" (several modules).

### Payment Terms module (2026-10-25)

Three tabs: **Payment Terms** (one row per term: Name *, From Date, To Date, Item Description,
Cutoff Day, Rank), **Payment Term Lines** (one row per installment, in order: Payment Term
Name *, Due (%), Amount Due, Days, Fixed Date, Day of Month, Months Ahead, Calendar, then
Discount (%), Days, Day of Month, Months Ahead for the First, Second and Third Discount) and
**Payment Term Sets** (Payment Term Name *, Set Code *). Additions to the shared sheet code
(Customers and Order Types unchanged; regression check PASS):
- child `"link": {"column", "exact": true}`: lines and sets join their term by the name exactly
  as written (capitals and spaces count, Oracle's own rule); a name twice is reported by the
  folder, not the "Two ... are named" stop.
- column type `number` (decimals; ranges are the folder's rules) and `"check": "folder"` on a
  dropdown (Calendar, Set Code): the value is passed on and the folder checks it against
  Oracle's live list (`--plan`), so the rules live in one place.
- a group with several child tabs: the preview shows one table per child tab (`child_tables`);
  the folder's `--plan` problems that name an installment (`"row"`) or quote a set go red on
  that sheet row; `"summary"` = "Oracle will get: N installments ... M sets ... From ...".
- group key `"batch_run": "--run-batch"`: Create sends ALL the group's records of the upload
  in one folder call (Payment Terms: one import); the folder answers one result per record
  (created / skipped / refused with Oracle's reason / saved but not matching), each on its own
  card; only a stop without per-record answers goes through the repair rules, and the rerun
  skips what was saved (exact names). `"minutes_total"` = one estimate for the whole group.
- `/api/sheet/peek` (offline, a moment): which modules have rows, so the upload's checking
  text names each one (a customers-only sheet keeps the old text).
Test workbooks: `Payment Terms/manual-notes/Payment_Terms_TEST_good.xlsx` (6 terms) and
`..._bad.xlsx` (one mistake per term), made by the page's own generator.

### Lookup Types module (2026-10-25)

Two tabs: **Lookup Types** (one row per NEW lookup type: Lookup Type *, Meaning *, Item
Description, Module * (a name, checked by the folder), REST Access Secured) and **Lookup Codes**
(Lookup Type *, Lookup Code *, Display Sequence, Enabled, Start Date, End Date, Meaning *, Item
Description, Tag), joined by Lookup Type exactly. Additions to the shared sheet code (Customers,
Order Types and Payment Terms unchanged; regression check PASS):
- child `"link": {"orphans": {"what", "key", "fixed"}}`: code rows whose Lookup Type isn't on the
  Lookup Types tab become their own entry "Codes for lookup type X" (`orphan_record()`), sent with
  `existing_only: true`; the folder's `--plan` then says the type exists (User / Extensible: "N
  new codes will be added, M already exist and are skipped"), is a System type (red) or exists
  nowhere (red, on that code row). Such an entry's labels come from the record tab (`label_tab`).
- group `"reserved": [{"column", "values", "text", "fix"}]`: a value another tab manages (the
  order type list ORA_DOO_ORDER_TYPES / DOO_ORDER_TYPES -> "use the Order Types tab for these").
- a folder problem about the n-th code goes red on that code row also when the group has one
  child tab (`child_problem()`).
- Create: `"batch_run": "--run-batch"`: all lookup types of the upload in one folder call (new
  types in one import, codes for existing types through REST), one result card per type. Oracle
  drops a WHOLE type when one of its codes is refused; the card says so, the others are saved, a
  rerun creates only what is missing; the failed-only sheet holds the failed types with their codes.
- the upload's checking text names the module search (a module name not looked up before opens an
  Oracle screen once, about a minute).
Test workbooks: `Lookup types/manual-notes/Lookup_Types_TEST_good.xlsx` and `..._bad.xlsx`.

### Business Units module (2026-10-26)

One tab **Business Units** (Name *, Active, Location, Manager, Default Set *), only the Create
Business Unit screen's fields; Order Manager and Pricing Administrator access is automatic (no
column). Empty Location / Manager = none; Manager only Yaqub, Younas or Smith, Aron. Every value
is checked by the folder's `--plan` (`"check": "folder"`), not by page code. Additions to the
shared sheet code (other modules unchanged; regression check PASS):
- column `"values_live": "<--options field>"`: the drop-down is Oracle's whole live list when the
  sheet is made (`make_template(lists)`; locations, sets); without Oracle the definition's values.
  A list whose values hold a comma ("Yaqub, Younas") goes on the hidden Lists tab.
- column `"keep_spaces": true`: the cell as typed, outer spaces kept (Name: the folder refuses
  them, because Oracle would make a second business unit "X " next to "X").
- the folder's `--plan` may return `"oracle": {key: text}` (what Oracle will get per field) and
  group `"plan_skips_red_fields"` drops a folder problem on a field the sheet check already made red.
- group `"ask_on_refusal": {"fields": [...]}` (**pause and ask**, Business Units only): after the
  module's batch, a record the folder refused for one of those fields (INVALID_REQUEST, saved "no",
  problem with field / value / reason / suggestions) gets a `question` and the run stays open
  (state `asking`, the rest is already done). The run screen shows a "Needs your decision" panel
  per question: the reason, the sheet row, the suggested values as buttons, a box for another
  value, "Skip this one". `POST /api/job/<id>/answer {"n", "value" | "skip"}`: a value is checked
  with the folder's `--plan` first (not accepted -> the panel says why, still open); then only that
  record goes through `--run-batch` again (rerun rules, never doubled; `run_batch` now sends only
  records still "waiting", the same as before on a first run). The questions live in the run, so
  a page refresh shows them again; server.log lines "question N (name): ... refused / answered /
  skipped" feed the Run summary's "Decisions" section. The failed-only sheet (also while asking)
  puts a note on the refused cell (Oracle's reason, the suggestions; the last answer written in).
- Create: `--run-batch`, all business units in one go, one card per business unit (created /
  already there / "saved and checked, access missing: X" / not saved with Oracle's reason); the Run
  summary says they were created together.
Test workbooks: `Business Units/manual-notes/Business_Units_TEST_good.xlsx` and `..._bad.xlsx`.

### Price Lists module (2026-10-26)

Two tabs: **Price Lists** (Name *, Item Description, Type, Currency *, Business Unit *, Start Date *,
End Date, Pricing Charge Definition, Line Type, Calculation Method; scope A, header only) and **Price
List Access Sets** (Price List Name *, Set Code *), joined by Price List Name exactly. Every value is
checked by the folder's `--plan`; the preview shows dates as Oracle's screen will (12:00 AM, the Oracle
user's time zone). Additions to the shared sheet code (other modules unchanged; regression PASS):
- column `"dropdown_warn": true`: Excel only warns for a value outside the drop-down (Business Unit:
  it may be one on the Business Units tab).
- group `"depends_on": {"group", "column", "match_column", "key", "request_key", "note"}` (Price
  Lists on Business Units): a price list whose Business Unit is a Name on the sheet's Business Units
  tab (exactly) is sent with `business_unit_pending: true` (the folder waits until Oracle shows it for
  pricing) and its line says so (`Upload.depends()`). In the run, the dependency group runs first
  (registry order); `hold_dependents()` holds such a price list while its business unit waits for a
  decision or hasn't run ("Waits for its business unit X, which needs your decision first." - a
  Waiting card), runs it once the business unit is done, and doesn't send it when the business unit
  failed or the user skipped it ("Not sent: its business unit X wasn't made ready in this run (you
  chose to skip it)." - in the failed-only sheet). `run_batch` runs each batch group once per pass.
- `ask_on_refusal` for Price Lists (the same panel as Business Units).
- Run summary: rows never sent are counted ("not sent"), and "price list" joins the "created
  together" note.
Test workbooks: `Price Lists/manual-notes/Price_Lists_TEST_good.xlsx` (with one row on the Business
Units tab) and `..._bad.xlsx`.

### Pause and ask for Order Types, Payment Terms and Lookup Types (2026-10-26)

`ask_on_refusal` is now on for every module (registry). Additions to the shared code (other modules unchanged):
- a folder problem may name a **child row**: `{"field", "value", "reason", "suggestions", "rows": "<request rows
  key>", "row": n, "where": "Installment 2"}`. The question then points at that sheet row (`child_row_of()`:
  the n-th row of the child tab whose `into` is that key), its label is that child tab's column
  (`label_of(group, key, rows_key)`), the panel says "Installment 2: Months Ahead", and the answer is written into
  that row of the request (`answer_question`) before the folder's check and the retry.
- Order Types (one `--run` per row) asks right after the refused row; Payment Terms and Lookup Types after their
  batch. Refusals the folders turn into questions: Order Types a meaning already used (run check) and any HTTP
  400 (field from Oracle's text); Payment Terms the import reasons for Months Ahead, Rank, a 0% discount, Name /
  Description length; Lookup Types FND-7103 / FND-7104 (meaning), a code key clash, dates, Display Sequence, a
  type name Oracle can't take (JBO-25017).
- **A refusal no rule recognises (2026-10-26):** a value refusal (INVALID_REQUEST / NOT_IN_ORACLE, saved "no")
  with no askable problem goes to Claude (`propose_value()`: one `claude -p` with the repair's limits:
  `--max-budget-usd` REPAIR_BUDGET_USD, REPAIR_MINUTES, `--strict-mcp-config`, `--no-chrome`, `dontAsk`, read-only
  settings: the folder's notes and the root CLAUDE.md, no edits, no commands). It proposes ONE field and value; the
  panel shows "Claude suggests changing X to 'Y': <why>. Nothing is changed until you choose." The value is a
  suggestion like any other: the user accepts it, types another or skips; it is never applied by itself. The same
  do-not-start rules as the repair: Claude's tool not installed or not signed in -> not started, a plain card.
  Logged as `job <run>_<n>p proposal: cost $x` with `logs/<run>_<n>p.repair.log`; the Run summary shows
  "Claude's proposal for <name>: tokens ..., $". Real call 2026-10-26 (Payment Terms, "You must enter months
  ahead ..."): proposed Months Ahead 1 on Installment 1, $0.50, 117,404 tokens.
- **One repair path for every module (2026-10-26):** a record that fails for a reason that isn't the user's (not
  INVALID_REQUEST / NOT_IN_ORACLE / NO_PERMISSION / PRODUCTION_REFUSED / SETUP_NEEDED / SIGN_IN_NEEDED, nothing
  "maybe" saved) goes to `repair()`, also inside a batch module (Payment Terms, Lookup Types, Business Units, Price
  Lists): before, a batch was repaired only when the whole call failed. The repair is for that record's request
  only (`<run>_<n>r`); the folder's batch command skips what is saved.
- **Offline behaviour matrix:** `python page/matrix/test_matrix.py` (about 2 minutes, nothing sent to Oracle or
  Claude): 6 modules x 8 behaviours (suggestion, typed value, skip, page refresh over HTTP, forced script failure ->
  repair, unknown refusal -> Claude proposes, unknown refusal with Claude not signed in, script failure in 1 of 2
  records -> repair) through the page's real server code, with every folder script replaced by
  `page/matrix/stub_folder.py` and Claude's tool by `page/matrix/stub_claude.py`; logs in `page/_work/matrix`.
  48 of 48 PASS on 2026-10-26 (plus 12 of 12 for a check that can't run, see Lost clicks). Run it after every
  change to the questions, the repair or the run code.

### Customers frozen: snapshot and regression check (2026-10-25)

Customers is in testing by someone else and must not change while other modules are added.
`_frozen/customers_v1/` holds copies of `page/`, `common/`, `Customers/` (without `_work/`,
`__pycache__/`) and this file as they were **before** Order Types was wired in, `manifest.json`
(SHA-256 of each), `input/customer_sheet.xlsx` (the user's 3-customer sheet that previewed
ready, `E:\GoSaaS\positive cases\Best Start.xlsx`), `answers.json` (Oracle's read-only answers
of one recorded preview: lists, Oracle's today, `--existing`, `--check-address`),
`expected.json` (the preview the frozen code builds from those answers, 1382 values) and
`ui_before/` / `ui_after/` (the page's preview text fingerprint and data). Never edit it.
`python page/regression_customers.py` (offline, about 2 s, nothing sent to Oracle): (a) every
Customers file has its snapshot hash (page/, common/, CLAUDE.md changes are listed for
information); (b) the current page code's preview of that sheet, Oracle answers replayed,
equals `expected.json` field by field (new keys are listed as ADDED, not as differences);
(c) the same with the other modules' tabs added empty. Exit 0 = PASS. **Run it after every
change to `page/` or `common/`**; a FAIL means stop and tell the user exactly what differs.
`--freeze` / `--record` made the snapshot (refuses to overwrite it).

### Customers v2 (2026-10-26, the freeze lifted by the user for this fix)

`_frozen/customers_v1` stays untouched; the fixed version is `_frozen/customers_v2` (own
`manifest.json`, `answers_v2.json`, `expected_v2.json`). `python page/regression_customers.py`
now checks v2 ((a)-(c) as before) and (d) compares the working customer sheet's preview v1
versus v2 field by field (the frozen v1 code and v2 both replayed with v2's recorded Oracle answers, so
only code differences count, not Oracle's data since v1 was recorded); only the differences in its `ALLOWED_V1_V2` list may differ
(`--v1` runs the old check, `--freeze-v2` made the snapshot). What changed (details in
`Customers/CLAUDE.md` > Version 2):
- one place path for preview and Create (State, City, Postal Code chosen in their Search and
  Select dialogs, rows matched by column); place problems are red in the preview with
  suggestions;
- registry `address_check_hold`: an address check that still can't run after its retries
  (folder 3 tries, the server once more after 20 s) marks the customer **held** (yellow
  note) instead of stopping the preview;
- registry `oracle_check: "--plan"` for Customers (Site Language, Customer Category Code)
  with `plan_skips_red_fields`;
- `ask_on_refusal` for Customers (a per-record module: the question is asked right after
  that customer's `--run`, `run_batch` -> `ask_questions(job, [it])`), and registry
  `answer_check` = the folder command that checks an answer (Customers `--answer-check`:
  lists and places; default the group's `oracle_check`, else `--plan`; 600 s limit);
- never a false "Nothing was saved": a message after Save is checked in Oracle first, and a
  stop after Save says "may have been saved" (`saved: "maybe"`).

### Lost clicks: one Oracle browser at a time, every step checked (2026-10-26)

**Cause:** Oracle's busy classic Setup page accepts a click or a search Enter and then ignores it (no error), so a
step "succeeded" without effect and a later wait failed ("no answer" on the preview). It happened most when the
preview opened three Oracle browsers on one sign-in at once. `ui.click()` retries only when Playwright itself
fails, so a lost click was never seen.
- **One Oracle browser at a time** (`page/server.py`): `ORACLE_LOCK` (a re-entrant lock) is held by a preview's
  checks (`full_check`, `session_valid`), an answer's check and a run (`run_batch` / `run_folder`, `repair` after an
  answer); the preview's checks run one after another (same name, then places, then the folders' `oracle_check`);
  `OPT_SEM` 1 (was 3). While a run is active a preview's checks don't wait (they answer "another task is running",
  as before). Places found that opened several Oracle browsers at once: the preview's three Customers checks; the
  live lists (`sheet_list`, up to 3 side by side); a preview beside an answer's check or a run.
- **Shared retry helper** `OracleUI.retry(plain, act, done, tries=3, pause=3, wait, last_wait, soft=False)` in
  `common/browser.py`: does the step, checks its result really appeared, up to 3 tries with a short pause (sign-in
  check, pop-ups closed) and a fresh wait each time, then one clear failure "Oracle's <plain> after 3 tries"
  (`soft=True`: returns 0 for the caller to decide). Also `fresh_search()` (a read-only Search believed only when
  its answer is fresh, or two searches agree), `search_dialog()` (list icon + Search..., each checked) and
  `close_dialog()` (Cancel until the dialog has closed). The common steps use them: `choose()` (the label is really
  selected), Redwood offering / area / task link / task menu, `lov_type`, `lov_search_all`, `close_lov_dialogs`.
  **Never retried: any step that may already have saved data** (Save, Save and Close, Submit of an import,
  Import, Option 2 + OK, Add Row of a form that is saved later). Each folder's notes list its checked steps.
- **The real reason:** `FAILED_STEP` / `browser.failed_step_text(default)` keep the first failed step of the
  process; each folder's read-only check (`--plan`, Customers `--existing` / `--check-address`) puts it in its
  `{"ok": false, "text"}`. `folder_batch()` passes that text on (before: "no answer"), and logs "N browser step(s)
  needed another try" when the helper had to repeat a step.
- **A check that couldn't run** (`folder_check()`): run again up to `CHECK_RERUNS` 2 more times, `CHECK_RERUN_PAUSE`
  20 s apart (not while a run is active); still failing -> the stop "The customers couldn't be checked with Oracle:
  Oracle's Setup page did not open Create Customer after 3 tries. Nothing was created. Please upload the sheet
  again." in `oracle_stops`, which the Check screen shows under "Oracle" (not "Sheet"); Create stays off, no run
  starts. Checks are read-only, so a re-run is always safe.
- Tested: `page/matrix/test_matrix.py` adds, per module with a check, "check can't run" (3 calls, the real reason
  under Oracle, no run) and "check fails once" (the re-run answers): 12 of 12 PASS beside the 48 of 48. Proof runs
  (read-only, through the page's upload check, `page/_work/proof/check_runs.py`): see the Customers notes.

## The page

**When the user asks to open the page:** start `python page/server.py` in the background
from the project root (it says where it runs, or that it already runs), check that
http://127.0.0.1:8765 answers, and give the user that link. Don't open Oracle yourself
for it; the page does its own setup checklist.

**The look (2026-10-26): an exact copy of the user's approved mockup** (dark and light themes, Manrope and
JetBrains Mono from Google Fonts with system fallbacks). Visual only: every endpoint, check, question, repair
and summary is unchanged.
- **Where:** `page/static/style.css` holds the mockup's two token sets (`html[data-theme="dark"|"light"]`: --bg,
  --surface..3, --line, --text, --muted, --accent, --accentInk, --accentGlow, --violet, --warn(Bg), --bad(Bg),
  --glowA/B, --bar) and its CSS rules as written (.card, .chip, .btn/.btnp, .pill, .label, .mono, .field,
  pulse/floaty/stripes, reduced motion); the other screens (setup checklist, detail tables, run summary) use the
  same tokens. `page/static/index.html` has the header (logo, "Setup Assistant", the environment chip: "<ENV> pod
  · production blocked", red "PRODUCTION" on production; the theme switch, remembered in localStorage inside
  try/catch) and the rail. `page/static/app.js` builds each stage with the mockup's markup and inline styles.
- **The rail** (Upload, Check, Create, Done) is persistent markup; only `setStage(n)` in app.js moves it, from
  the route and the real state: `#/` = 0; reading a sheet and its preview `#/sheet/<id>` = 1; a run with work or
  an open question `#/job/<id>` = 2; the run finished (no open question) and `#/summary/<id>` = 3; the setup
  checklist hides it. Nobody clicks it; there are no stage buttons.
- **Stages:** Upload (Choose workbook, Get the blank template = `/api/sheet/template`, How a run goes); Check
  (module cards from `/api/sheet/peek` while reading, then the preview's problems with the fix and read-only
  "Suggested" chips taken from the fix text, or "Every check passed"; problems clear only after the sheet is
  fixed in Excel and uploaded again; bottom bar "Create N items", disabled until ready); Create (run card with
  real progress, the "Tell me when it finishes" switch, one amber "Needs your decision" card per open question
  with the existing pause-and-ask hooks `.question[data-n]`, `.q-pick`, `.q-text`, `.q-use`, `.q-skip`); Done
  (stat cards from the job and the Run summary numbers; Result cards grouped by module in the module order, each
  group a real button with aria-expanded, monogram, item count and status-count pills, "Collapse all / Expand
  all", cards inside a module ordered: needs attention, then skipped, then created; search and the status filters
  apply live and hide a module with no match; no Export since 2026-10-26; the Run summary as five cards built from
  `summary.numbers` (Overview, By module, Timeline, Claude and repairs, Decisions and problems), every fact of
  its sentences kept, the sentences themselves only when an older run has no numbers; the failed-only sheet
  button when it exists). Checked with `page/_work/redesign/shoot_done.py` against the demo server (mixed and
  clean runs, screenshots in `page/_work/redesign/shots_done/`).
- **Notify:** when the switch is on (default on, localStorage), a run seen running on the page that ends after
  more than 60 s while the tab isn't focused gives a browser Notification "Setup run finished: X created, Y
  skipped" and a short Web Audio chime; permission is asked only when the switch is turned on or Create is pressed.
- **Checking the look:** `page/_work/redesign/demo/demo_server.py` runs the page's real server code on port 8797
  with Oracle stubbed; `page/_work/redesign/shoot.py` drives every stage in Playwright (dark and light at 1360 px,
  dark at 390 px) next to the reference mockup (`page/_work/redesign/reference/`, rendered with a small
  `support.js`) and checks console errors, the theme after a reload, the rail position and that the rail has no
  buttons. Screenshots: `page/_work/redesign/shots/`. Both are work files (never shared).

What the page does (it never changes a configuration folder or `common/`):
- Finds the folders from the Configuration index and uses only their Page interface
  (`--spec`, `--options`, `--run`). Runs are queued, one at a time.
- Setup checklist on **every start** (a few seconds on a set-up PC), before the cards:
  helper packages, the automation's browser, "Enter your Oracle details" (creates `.env`
  from `.env.example` and opens it in Notepad; the user fills in their own values, the
  page carries on when Notepad closes or the file is saved; values are never read or
  shown), the Oracle connection, **the saved Oracle sign-in** (`common/session_check.py`:
  a hidden browser opens the start page once with the saved session, about 5 s; missing
  or expired -> the sign-in window (`common/login_once.py`) opens right away with "Sign in
  to Oracle once; it closes by itself", the session is saved, the page carries on), then
  "Looking at Oracle's screens" (first time on a PC only: `check_setup.check_screen_look()`
  runs `page/look.py` on Customers > Create Customer, reads "Account Address Set" and
  leaves with Cancel; plain fix text if it can't), then Claude's command-line tool
  (optional, never blocks setup; one-click `claude auth login`). Installed per user without
  admin rights by `common/claude_tool.py` (2026-10-23), routes in order: `npm install -g` (as
  before), Anthropic's standalone installer steps (downloads.claude.ai + checksum +
  `claude install`), portable Node.js zip into `%LOCALAPPDATA%\ConfigAutomation\tools`
  (long-path safe) + npm `--prefix`, existing Node.js + npm `--prefix`. The tools folder goes
  on the PATH of the page's own processes only. If all are refused, the step lists each plain
  reason with "Continue without automatic fixes" (remembered in `page/_work/claude_skipped`,
  "Try again" retries). Failed runs then get a plain error and a copyable message. Tested on
  2026-10-23: portable route 74 s and npm-prefix route 16 s into scratch folders (2.1.308
  started); every route blocked via `python page/server.py --simulate-claude-blocked`
  (or `common/claude_tool.py --install --simulate-blocked`) -> skip -> setup complete.
  `common/check_setup.py --final` (which also runs the screen-look check) only when
  `.setup_ok` is missing.
  The saved session is kept between starts; only a missing or expired one asks again.
- The sign-in is renewed at the preview, never during a run (2026-10-23, The upload sheet).
  A run that still finds it expired (SIGN_IN_NEEDED) ends with a plain failure card saying
  what was and wasn't created and "Upload the sheet again"; nothing asks mid-run.
  One sign-in window at a time (a second caller waits and then finds the session valid).
  Session lifetime seen: one saved 2026-10-20 22:20 UTC was still valid 7 h 23 min later
  (2026-10-21 05:43 UTC) and expired by 06:24 UTC (about 8 hours; the page then opened
  the sign-in window by itself at start); earlier ones expired after about 4 hours
  (2026-10-19) and overnight (2026-10-20). A plain page request can't check it: the start
  page always goes to Oracle's identity service, which signs the session back in by script.
- Happy-path dates on every form (2026-10-21; `common/page.py` `happy_dates()` /
  `date_role()` / `date_pairs()`, added only, used by the page, plus the same rules in
  `page/static/app.js`). Oracle's today = the date of a read-only REST answer
  (`page/oracle_today.py`, kept 10 minutes). The role of a date comes from its key
  (start/from/established = start; end/to/until/termination = end). An end date is empty
  by default; its picker starts the day after Oracle's today (and after the start), and an
  end on or before Oracle's today or the start is refused next to the field. A start later
  than Oracle's today is allowed with "This won't be active until <date>". "Use today"
  shows "Today: <date> (Oracle's today minus one day)" and sends that date. A purpose
  (Customers) can't start before its address from date (empty = Oracle's today), so it gets
  no "Use today" unless the address starts on that day too (HZ-120150). The server checks
  the same rules before queuing a run and returns the problems for the fields.
- Pick lists: the form opens at once; each list fills its own field (from
  `page/_work/cache/` at once, read again when the form opens). A field whose list isn't
  there yet says "Loading the list ..." and the rest can be filled meanwhile; if it can't
  be loaded, the value can be typed (checked with Oracle). No refresh button and no
  "updated" label (removed 2026-10-21). Lists are never read while a request runs or is
  being repaired: the server answers "busy" and the page asks again a little later.
- Refuses to run when ORACLE_ENV is production without ALLOW_PROD=yes.
- Automatic repair: a failed run whose code isn't the user's to fix (STEP_FAILED,
  VERIFY_FAILED, TIMEOUT, FAILED) goes to `claude -p` in the project folder (stream-json,
  a fixed result schema, `--permission-mode dontAsk`, `--strict-mcp-config` (no claude.ai
  connectors such as Gmail), `--no-chrome`, `--max-budget-usd` 2 per attempt; at most 5
  attempts and 20 minutes). Its settings file allows only: reading that folder, `common/`,
  the root CLAUDE.md, `page/look.py` and its screenshots (not other folders); edits inside
  that one folder (incl. its CLAUDE.md gotchas); and `python page/look.py`. `.env`,
  `.session/`, `common/`, `page/`, `_template/` are denied for edits. (A deny rule such as
  "./CLAUDE.md" also matched the folder's own CLAUDE.md, 2026-10-21, so edits are limited
  by the allow list.) Claude
  does NOT run the folder's script: it finds the cause (log, `<folder>/_work/fail_*`,
  the live screen through `page/look.py`), fixes the folder (Self-repair rule) or says it
  was temporary, and returns `fixed` / `no_change_needed` / `needs_user` / `failed`.
  The server then compares the folder with a copy taken before the repair, refuses any
  added code line that touches the login file, the saved sign-in, environment settings,
  other programs, new network libraries or deleting files (it puts the files back and
  stops), and only then reruns the same `--run` itself (the folder skips what exists).
  `page/look.py --folder X --task T --area A --offering O [--heading H] [--label L]
  [--click link] [--buttons] [--text] [--screenshot name]` opens a task screen with the saved sign-in
  using the folder's pre-repair code (PAGE_LOOK_SNAPSHOT), reads labels / text / a
  screenshot (page/_work/look/), never types, refuses save-type clicks and always
  leaves with Cancel. **After Create nothing asks the user anything (2026-10-23):** progress
  lines, the automatic repair, then the result card. A run that can't finish (a value
  Oracle refused, an expired sign-in or MFA, a missing permission, production, a fix outside
  the folder, no signed-in command-line tool, repair given up) ends with one plain failure
  card: what happened, what was and wasn't created (the folder's text; Customers says
  "Nothing was saved in Oracle." or the saved Registry ID), what to do next, and a copyable
  text for Claude where it helps. No buttons that continue the run.
- Claude sign-in is one click: a "Sign in to Claude" button in the page header (on every
  screen while needed), in the setup checklist and on the failure card. It opens
  `claude auth login` (Claude's sign-in page in the browser) and the server checks
  `claude auth status` every few seconds, so the page carries on by itself; nothing to
  press afterwards.
- Real repair proven 2026-10-21 on a temporary copy of Payment Terms whose script looked
  for a "Create Payment Term" button: with the failure screenshot removed, Claude ran
  `page/look.py --buttons` on Manage Payment Terms, found the icon titled "Create", fixed
  the copy (exactly the real folder's selector) and added a dated gotcha; the edit check
  passed; the server's rerun skipped the existing term ttttttttt (nothing created).
  $0.71, about 3.5 minutes. (A first try with the screenshot present cost $0.43 and fixed
  it from the screenshot and page text, without the live look.)
- `python page/server.py --test-mode` adds a "make this run fail once" switch to the
  forms (the run gets a browser that doesn't exist) to test the repair.

```
common/oracle.py      shared code: export/import a task, poll status, CSV/zip helpers,
                      safety checks, _work/ handling
common/browser.py     Playwright helpers: start page, saved sign-in, browser CHANNEL,
                      OracleUI (CSV export/import, Search Tasks, ADF form helpers)
common/login_once.py  user signs in once in a visible window; session -> .session/
common/check_setup.py setup checks (no secrets printed); --final writes .setup_ok
common/session_check.py quick read-only check of the saved Oracle sign-in (JSON line)
common/claude_tool.py Claude's command-line tool: --find / --diagnose / --install per user,
                      no admin (optional; for automatic fixes only)
common/page.py        Page interface contract: --spec, --options FIELD, --run 'JSON'
common/created_business_units.json  business units the Business Units folder created
                      (status ready | pending, pricing_confirmed); read by Price Lists.
                      Oracle caches a user's data access, so a new business unit may need
                      the user to sign out and in again before it shows for pricing:
                      Business Units waits up to 2 min (fresh REST reads) and marks it
                      pending if needed; Price Lists retries a refused pending one and then
                      says a fresh sign-in is needed (not a folder failure). Agreed link
                      between the two folders (user, 2026-10-21); see both CLAUDE.md files.
Lookup types/         Manage Standard Lookups (FND_MANAGE_STANDARD_LOOKUPS)
  run.py              reads lookups.json; new types by CSV import, new codes on existing types by REST,
                      read-back per type and code; --plan (read-only); modules by name
  lookups.json        requirements file
  modules.json        modules looked up on the screen (name, type, key, ID); rebuilt on use
  sheet_fields.md     every field, rule and Oracle message (for an upload sheet)
  CLAUDE.md           route status for this configuration
  manual-notes/       manual-run notes (describe output, notes, screenshots)
  package-route/      package-route scripts
  _work/              temporary files for a run (exists only during/after a failed run)
Price Lists/          Price lists (REST resource priceLists)
  run.py              reads pricelists.json, creates + approves, verifies, cleans _work/
  pricelists.json     requirements file
  CLAUDE.md           route status, input rules, gotchas
  manual-notes/       manual (Postman) steps
Payment Terms/        Manage Payment Terms (AP_MANAGE_PAYMENT_TERMS), UI export/import
  browser_flow.py     reads terms.json; export, add rows, import, verify via Playwright
  classic_setup.py    this folder's Setup and Maintenance steps for the classic or Redwood layout
  terms.json          requirements file
  CLAUDE.md           input rules, route status, file layout, gotchas
  manual-notes/       manual-run notes
Order Types/          Order type lookup codes: REST (standardLookups) with UI export/import fallback
  browser_flow.py     reads ordertypes.json; REST create + GET verify (fallback: export/import)
  ordertypes.json     requirements file (lookup type + codes)
  CLAUDE.md           input rules, route status, file layout, gotchas
  manual-notes/       manual-run notes
Customers/            Create Customer form (Financials > Customers), no export/import, no REST
  browser_flow.py     reads customers.json; fills the form, Save and Close, verifies on screen
  customers.json      requirements file (list of customers)
  CLAUDE.md           input rules, fields, drop-down values, route status, gotchas
  manual-notes/       manual-run notes
Business Units/       Manage Business Unit + Manage Data Access for Users (Order Management), UI export/import
  browser_flow.py     reads request.json; BU import, then data access by REST (fallback import), verify
  classic_setup.py    this folder's Setup and Maintenance steps for the classic or Redwood layout
  bu_import_template.json  header lines of the business unit export (no data rows), for the fast run
  request.json        requirements file (name, location, default set, user, role)
  CLAUDE.md           input rules, file layouts, drop-down values, route status per step, gotchas
  manual-notes/       manual-run notes
_template/            copy this to start a new configuration folder (not a configuration)
  browser_flow.py     skeleton with --check, timeouts (ui.step), verify
  request.json        request file skeleton
  CLAUDE.md           Input rules, Route status, Related folders, Gotchas, Sample requests
  manual-notes/
```

## Folder rules

- Every configuration type has one folder at the root. Do all work for it inside
  that folder, using `_work/` for temporary files (export zips, import zips,
  intermediate CSVs). Never write them anywhere else.
- After a verified success, delete `_work/`. After a failure, keep it.
  (`run.py` does this automatically via `oracle.cleanup_work_dir()`, which only
  ever deletes `<config folder>/_work/`.)
- Never leave exports, zips or credentials in the project. The project must stay
  small and shareable.
- What stays permanently in a config folder: `run.py`, the requirements JSON,
  `CLAUDE.md`, `manual-notes/` and `package-route/` (small documentation and
  reference only; no export zips, generated zips or response.bin copies).
- Template for a new config folder: copy `_template/` (see New folder template).
  The script calls `oracle.init_work_dir(<folder>)` first and
  `oracle.cleanup_work_dir()` only after verification passed.
- Every folder has a read-only `--check` (see each folder's CLAUDE.md for what it
  opens or calls). Run it on its own, one folder at a time.

## Route status rule

Every configuration folder has its own CLAUDE.md with a Route status section.
Before any work in a folder, read it and use the route marked PROVEN. If a route
is PARTIAL or UNTESTED, don't improvise against the environment: follow that file's
'Discovery steps', report what you find, and wait for my confirmation. After any new
finding, update that folder's CLAUDE.md so the knowledge stays in the folder. For a
new configuration type, first check ExportSupportedFlag via GET
setupTaskCSVExports/<task>; if supported use the CSV route, otherwise the package route.

When asked for a new record in a configuration with a PROVEN route, just do it
end to end and report the verification result. Don't ask first (but see Input rules).

## Input rules

Every configuration folder's CLAUDE.md has an 'Input rules' section listing REQUIRED
and OPTIONAL fields, with the Oracle UI default for each optional one. Before doing
any work, check the request against it. If a required field is missing or unclear,
stop and ask me for exactly what is missing, in plain, non-technical words, listing
all missing items in one message. Never guess a required value and never ask me for
technical codes or IDs; look those up yourself from the documented lists. Optional
fields that are missing just use the UI default. Every new configuration folder must
have an Input rules section before it is marked PROVEN.

## Environment rules (enforced in `common.oracle.check_environment`)

- `.env` must set `ORACLE_ENV` (dev, test, uat, sit, prod or any custom label) and
  `ORACLE_HOST`. If either is missing, the code stops with a clear message.
- If `ORACLE_ENV` is `prod` or `production` (any case), the code refuses to run
  unless `ALLOW_PROD=yes` is also set.
- Every run prints the host and `ORACLE_ENV` before doing anything else.
- There is no hostname pattern matching anywhere in the code.
- **Claude must never set `ALLOW_PROD` or change `ORACLE_ENV` on its own.** Only the
  user edits those lines. Claude may check whether a key exists (e.g.
  `grep -q '^ORACLE_ENV=' .env`) but never reads or prints other lines.

## Browser sign-in (Oracle UI work)

- Claude never reads `ORACLE_USER`/`ORACLE_PASS` and never types credentials into any
  page. The user signs in.
- Start page: `<ORACLE_HOST>/fscmUI/faces/AtkHomePageWelcome` (take the host from
  `ORACLE_HOST`, e.g. as printed by `oracle.check_environment()`; never hardcode it).
- If a sign-in page, MFA prompt or anything unexpected appears: stop, tell the user,
  and wait until they sign in in that browser window and say "done".
- If the session expires mid-task: stop at that point, ask the user to sign in again,
  then continue from where it stopped.
- If `ORACLE_ENV` is prod or production: don't open Oracle in the browser; stop and
  tell the user.
- Downloads land in the user's Downloads folder: move them into `<config>/_work/`
  straight away (no copies left in Downloads).
- Scripted browser work (Playwright, `common/browser.py`) reuses the session the user
  saved with `common/login_once.py` in `.session/`. If it shows the sign-in page,
  the session expired: run `login_once.py` again and let the user sign in.
  Claude never opens or reads `.session/`.

## Safety rules (also enforced in code)

- If any call fails, show the exact error and stop. Never invent endpoints: use only
  the proven ones below, or links Oracle itself returns in a response.
- Never overwrite or delete existing records. Skip records that already exist.
  An export may not contain every record (lookups export uses scope `mode=search`),
  so check existence through a documented REST finder as well, not only the export.
- Never commit or share `_work/`, `.env`, `.session/` or `.setup_ok` (see SHARING.md).

## Credentials

`.env` in the project root with `ORACLE_USER`, `ORACLE_PASS`, `ORACLE_HOST`,
`ORACLE_ENV` (and `ALLOW_PROD=yes` only for production, set by the user).
Loaded by `common/oracle.py` with python-dotenv, searching upward from the script's
folder; real environment variables override the file.
**Never open, print, log or copy the contents of `.env`.**

## Proven API facts

- Host: from `ORACLE_HOST` (no default). Proven so far on
  `https://fa-etia-test-saasfaprod1.fa.ocs.oraclecloud.com` (ORACLE_ENV=test).
- API base: `/fscmRestApi/resources/11.13.18.05`, Basic auth. Send no global
  `Accept: application/json` header: enclosure downloads then fail with HTTP 406.
- Export: `POST setupTaskCSVExports/<TASK>/child/SetupTaskCSVExportProcess`
  body `{"TaskCode": "<TASK>"}` -> `ProcessId`.
- Status: `GET .../SetupTaskCSVExportProcess/{id}/child/SetupTaskCSVExportProcessResult/{id}`
  -> `StatusCode` NOT_STARTED, IN_PROGRESS, COMPLETED, COMPLETED_WARNINGS, COMPLETED_ERRORS.
  The result collection returns empty; only the item URL by id works. Poll every 10s.
- Download: result URL + `/enclosure/FileContent` -> zip of CSVs + `ASM_SETUP_CSV_METADATA.xml`.
- Import: `POST setupTaskCSVImports/<TASK>/child/SetupTaskCSVImportProcess`
  body `{"TaskCode", "FileContent": <base64 zip>, "SourceTargetDiffOkFlag": true}`.
  Poll the import result the same way (`SetupTaskCSVImportProcessResult/{id}`).
- Import result attachments (from `describe`): ProcessLog, ProcessResultsReport,
  ProcessResultsSummaryReport. On failure the code saves them to `_work/` via the
  `enclosure` links returned in the result item.
- `GET <resource>/describe` works with Basic auth and shows attributes, finders and LOVs.
- Direct REST resources (POST/PATCH/GET on API_BASE, e.g. `priceLists`) work with the
  same Basic auth; use `oracle.rest()` / `oracle.rest_items()`. Name -> ID lookups
  proven: `finBusinessUnitsLOV` (KeywordFinder), `currenciesLOV`, `setIdSetsLOV`
  (details in "Price Lists/CLAUDE.md").
- BOSS resources under `/api/boss/data/objects/...` (e.g. taxonomyNodes) return
  HTTP 401 with Basic auth. Do not use them without a different, user-approved auth.

## UI-only workflow (when there is no usable API route)

For tasks that can only be done through the Oracle UI (e.g. Export/Import to CSV
File in Setup and Maintenance), work like this:
a. **Learn** the task by driving the browser once (Playwright with the saved
   session, or the built-in browser): click path, menus, confirmations, status
   pages, file layout. Record every finding in that folder's CLAUDE.md.
b. **Codify** it into a Playwright script in that folder (`<folder>/browser_flow.py`)
   using `common/browser.py` `OracleUI`. Everything is by name:
   `export_csv(task, area, offering)` / `import_csv(task, area, zip, offering)`,
   `open_task(task, area, offering)` for the task's own screen (on-screen checks),
   `open_offering()` (switches the offering on the Set Up page; Setup and Maintenance
   always opens the user's last offering), `find_task()` / `load_task()` (the area's
   task list loads 25 tasks at a time while scrolling), `task_menu()` (the task's
   "<task> Actions" menu: Export, Export History, Import, Import History),
   `choose()` for ADF drop-downs (focus + choose + Tab), process tracking by name on
   Export/Import History, downloads into `_work/`, file chooser for uploads, Guided
   Learning widget blocked, session-expiry check. Always pass the
   offering, so scripts don't depend on what another script left selected. Robust
   selectors (titles, roles, visible text) and explicit waits; fixed sleeps only
   for polling. For form-fill routes (no export/import, e.g. Customers):
   `search_task()` (opens a task by name and functional area), `field(label)` (visible field by label), `lov_type()` /
   `lov_search_all()` (list-of-values fields and their Search and Select dialogs),
   `match_value()` (exact, or unique case-insensitive; never guesses),
   `set_check()`, `field_error()`, `page_messages()` (Oracle message dialogs),
   `wait_heading()` and `step(name)` (a failure names the step and keeps a screenshot).

   **Oracle's Setup and Maintenance is the Redwood page since 2026-10-20.**
   `/fscmUI/faces/FuseTaskListManagerTop`, and also the profile menu > Setup and
   Maintenance, redirect to `/fscmUI/redwood/setup/functional-setup/...`, titled
   "Set Up <offering>". The offering is chosen with the switcher on that title. The
   functional areas are on the left and the tasks on the right, each task with a
   "<task> Actions" menu. Export is now "New Setup Export" (File Format "CSV or JSON",
   Name filled in, Export button), with status, totals (Total Business Objects / Total
   Completed / Successful) and Download on "Setup Export History". Import is now "New
   Setup Import" (a file drop area, then Import), tracked on "Setup Import History".
   The task screens themselves (Create Customer, Manage Payment Terms, Manage Order
   Lookups) are still the classic pages; Cancel on them returns to the Set Up page.
   `common/browser.py` navigation and export/import were rewritten for this on
   2026-10-20 (the user asked to fix all folders; the classic version is gone).
   Proven the same day: export, download and import (Payment Terms ZZ_TEST_3593,
   verified by a fresh export).
c. **Prove** it with a dummy record (e.g. ZZ_POC_...), verified by a fresh export,
   and mark the route PROVEN in the folder's CLAUDE.md only after a clean run.
d. **Later requests just run the script** (after the Input rules check). The only
   manual step is the user's one-time sign-in (`common/login_once.py`).

### Self-repair rule (Playwright scripts)

When a Playwright script fails, don't give up and don't ask the user what to do.
Read the error and the failure screenshot (`<folder>/_work/fail_*.png` / `.txt`),
open the page in the browser (using the saved session), work out what changed in
Oracle's screen, fix the selector, wait or step in the CURRENT folder's script (or a
helper inside that folder), rerun the same request, and confirm the result. Never
change the values in the request. If the cause is an expired sign-in, MFA or
something destructive, stop and tell the user. If the fix would need a change in
`common/` or in another folder, stop and tell the user in plain words what and why,
and wait (Isolation rules). After a fix, add a line to that folder's CLAUDE.md
gotchas saying what changed and when, rerun that folder's `--check`, and make sure
its verification step still checks the real values.

## Standard workflow for a new configuration type

1. Check ExportSupportedFlag (`GET setupTaskCSVExports/<task>`) -> pick CSV or package route.
2. Prove ONE record manually in the UI: export before, add the record, export after.
3. Diff before/after to learn which files/rows/columns change.
4. Generate a dummy record by script from the diff: build the row from the export's
   column headers, fill only the requested fields plus the UI defaults.
5. Import it, then verify by re-export.
6. Document everything in that folder's CLAUDE.md (route status, input rules,
   command, gotchas).
7. Only then run the full batch from the requirements file.

## Config folder CLAUDE.md template

```
# <Configuration name>
Task code / Status summary
## Input rules    (REQUIRED fields; OPTIONAL fields with the Oracle UI default for each;
                   lists used to turn names into codes/IDs, e.g. a module list)
## Route status   (REST / mixed / CSV / form fill / package route per step: PROVEN | PARTIAL |
                   UNTESTED | NOT SUPPORTED, with notes)
## How to do it   (preferred route and exact command, plus fallback steps)
## Page interface (field table, how each list is read live, progress steps, what was tried)
## Sample requests
## Related folders
## Known gotchas
## Discovery steps (check ExportSupportedFlag; export before, add one manually,
   export after, diff; generate a dummy, import, verify; record findings here)
```
