# Customers

Creates **organization and person customers** (party + one account + one account site
with address and purposes) by filling Oracle's **Create Customer** form with Playwright.
Task: **Create Customer**, Setup and Maintenance > offering **Financials** >
functional area **Customers** (the same task is also listed under Revenue Management).

Route in one line: **Playwright form fill only** - REST cannot create a whole customer
(account, account site, address set, purposes, Supplier Site ID; see Route status).
On the classic layout (back 2026-10-21) `--check` and a full save are proven (ZZ_TEST_2336).

Status summary: Playwright form fill (`browser_flow.py`) PROVEN by clean runs on
2026-10-20 (ZZ_TEST_8757 with all fields, ZZ_TEST_6050 with required fields only,
ZZ_TEST_8757 skipped on the second run); person customers PROVEN 2026-10-20
(ZZ_TEST_4055 required only, ZZ_TEST_9231 Q Tester Jr. with optional fields). No CSV export/import (the task's Actions
entries Export to CSV File / Import from CSV File / Compare Setup Data are disabled,
also for Manage Customers) and no REST. Only manual step: the one-time sign-in.

## Version 2 (2026-10-26): what was wrong and what changed

The user lifted the Customers freeze for this fix. v1 stays in `_frozen/customers_v1` (untouched); v2 is in
`_frozen/customers_v2` (own manifest, answers_v2.json, expected_v2.json); `page/regression_customers.py`
checks v2 and compares the working sheet's preview v1 versus v2 field by field (only the listed, intended
differences may differ).

**What went wrong (investigated 2026-10-26, read-only):**
- **Valid cities refused at Create.** ABSECON (NEW JERSEY), Dallas (TX) and Seattle (WA) exist in Oracle.
  Create typed the City and pressed Tab; because the name starts other names too (ABSECON HIGHLANDS; DALLAS
  in 5 Texas counties and DALLAS FORT WORTH METROPLEX; SEATTLE HEIGHTS) Oracle opened a choice dialog, and
  `lov_type` read its rows before they had loaded, found none and stopped with "... does not exist in Oracle's
  geography ... Nothing was saved." The preview used another path (the City search dialog **without** the
  State on the form), so it passed them. Also, picking a dialog row by matching the value against **any** cell
  (county, state) could pick a wrong row.
- **"Nothing was saved" for saved customers.** Summit Ridge Logistics (Registry ID 130742) and BlueHarbor
  Marine Supply (130745) are complete customers in Oracle (party, account 21473 / 21476, one site with Ship to
  and Bill to, Enterprise Set) at "JERSEY, TENNESSEE" with no postal code, made 2026-10-25 about 20:24 / 20:29
  UTC by Configuration.TEST, by a run on another computer (its logs are not on this PC, so the exact message
  is not known). The only path that reports a saved customer as "Nothing was saved": after Save and Close
  `save()` treated ANY Oracle message dialog as "Oracle did not save", and `run_request` turned every
  value-type stop into "Nothing was saved" (`saved: "no"`) without looking at the note written just before
  Save. Pixel Forge Studios3 / Nightfall Interactive3 (ABSECON) do not exist: their cards were right.
  A JERSEY, TENNESSEE customer without postal code saves normally (proven: ZZ_TEST_CU_2589_JERSEY, 130770).

**What v2 does:**
- **One place path for the preview and Create** (`pick_places`): State, City, Postal Code are each chosen in
  their own Search and Select dialog on Create Customer (the search text committed with Tab; rows waited for;
  "No rows" believed only when a second search agrees), the row picked by its **columns** (state; city +
  county + state; postal + city + county + state), never typed + Tab. The city's county comes from the postal
  code; without a postal code and several counties the one named like the city (else the first) is used and
  the preview says so. The preview runs exactly this on an unsaved form (left with Cancel), so a place that
  passes the preview passes Create. A missing place is a structured refusal with suggestions: the cities Oracle
  has for that postal code in the state, then the closest names (e.g. "Dalas" -> DALLAS, DALHART, ...); a
  postal code of another state -> "isn't one Oracle has for SEATTLE, WA"; a state -> the closest states.
  Other countries: unchanged (typed).
- **Preview reliability:** `--check-address` tries up to 3 times (fresh browser each, waiting 10 s and 30 s);
  the page tries the rest once more after 20 s; still not checked -> the customer is **held** (yellow, "Oracle's
  places couldn't be confirmed just now ... checked again when it is created; if Oracle refuses it, you'll be
  asked"), the rest goes on; never "upload the sheet again". Answers are cached an hour per country / State /
  City / Postal Code and shared across customers (unchanged). Test switch: `CUSTOMERS_TEST_GEO_FAILS=n`.
- **Never a false "Nothing was saved":** a message after Save and Close is closed and Oracle is **searched**
  (the form's Registry ID, else the one new customer with the name): found -> it was saved, the run goes on
  to verify it and says so; not found -> "Oracle did not save X: <message> (checked in Oracle: no new customer
  named X)". Any other stop after Save was clicked says "may have been saved (Registry ID N if it was) ...
  never creates it twice" (rerun guard as before). Test switch: `CUSTOMERS_TEST_FAIL_AFTER_SAVE=1`.
- **Structured refusals** (`error.detail.problems`: field, value, Oracle's reason, suggestions) for places,
  lists (Account Type, Customer Class, Account Address Set -> codes, Purpose, Site Language, ...) and
  Bill-to Site; the page's pause-and-ask panel is on for Customers (registry `ask_on_refusal`), answers are
  checked by `--answer-check` (every list + the place path), then only that customer is run again. Test
  switch: `CUSTOMERS_TEST_REFUSE_CITY=<city>` (a forced refusal).
- **More in the preview:** `--plan` checks Site Language against the form's list and refuses any Customer
  Category Code (the list is empty in this pod), only when such a value is filled (no browser otherwise).
- A State already red from the sheet check keeps its City / Postal Code from a second red line (they are
  checked within the State, again once it is fixed).

**Proven 2026-10-26 (test pod, through the page; sheets in `manual-notes/`, tester notes `manual-notes/v2_tester_notes.md`):**
- `CU_TEST_10.xlsx` preview (3-4 min): the 5 valid customers found (DALLAS, TX (DALLAS county); SEATTLE, WA
  (KING); ABSECON, NEW JERSEY (ATLANTIC); JERSEY, TENNESSEE (HAMILTON); person CUPERTINO, CA), the 5 wrong ones
  red with one reason each ("Oracle has no city 'Dalas' in TX."; "Postal code 75201 isn't one Oracle has for
  SEATTLE, WA."; Ship to without Bill to; State 'Kalifornia'; Site Language 'Klingon'). The 5 valid ones
  created by Create (`CU_TEST_valid5.xlsx`, 14 min 23 s, no repair): ZZ_TEST_CU_2589_01_DALLAS 130783,
  _02_SEATTLE 130786, _03_ABSECON 130789, _05_JERSEY 130792, _04 PERSON 130796; _06 to _10 searched in Oracle:
  none exists.
- Pause and ask (`CU_TEST_ask.xlsx`, `CUSTOMERS_TEST_REFUSE_CITY=CUPERTINO`): 3 questions after the batch with
  suggestions SANTA CLARA / SAN JOSE; _11 answered with the suggestion -> created 130816; _12 typed "Mars City"
  -> refused in the panel ("Oracle has no city 'Mars City' in CA.", new suggestions), then "San Jose" ->
  created 130825; _13 skipped -> not created, the only customer in the failed-only sheet (note on the City
  cell); _14 Dallas created 130810. A page refresh shows the answered questions; the Run summary lists the 3
  decisions.
- Forced stop after Save (`CUSTOMERS_TEST_FAIL_AFTER_SAVE=1`, ZZ_TEST_CU_2589_15_MIDWAY): the card said "was
  saved in Oracle (Registry ID 130828), but checking it didn't finish" (`saved: "yes"`); the same request again
  verified 130828 "saved by the first try ... not created again"; Oracle has one customer of that name.
- Places lookup failing twice (`CUSTOMERS_TEST_GEO_FAILS=2`): the preview finished with every answer (272 s
  instead of 217 s); failing always (`=5`): every customer held with the yellow note, preview ready, no stop.
- Regression: `python page/regression_customers.py` PASS against v2; v1 versus v2 (the frozen v1 code and v2
  replayed with the same recorded Oracle answers) differ only in the intended `modules` line.

## Input rules

Check every request against this before doing any work (root CLAUDE.md > Input rules).
The request says `"customer_type": "Organization"` (default when left out) or
`"Person"`; these are the two values of the form's Customer Type drop-down. Anything
else: stop and ask which one. Person customers: see "Person customers" below; all
other rules and fields are the same for both types.

REQUIRED (what the form's own save check demands; seen 2026-10-20: "Name / Account
Address Set / Supplier Site ID: You must enter a value"). If missing, ask in one
plain message, never for IDs:
- Customer name. **Names are not unique in Oracle** (several "ABC" exist). Since
  2026-10-23 a customer is **never skipped because its name exists**: the run lists the
  customers that already have the name (registry IDs, never touched) and creates a new one.
  Oracle then shows "Warning: Matching Organizations" (or Persons) after Save and Close;
  the script **always chooses Option 2 "Create new organization based on what you
  provided" and OK, never Option 1** (that would tie the account to someone else's
  customer). The new customer is found again by the **Registry ID** the form shows, not by
  name. (Replaces the old rule "an existing name is skipped".)
- Account address set: a name or code from the list below (the user's value is
  matched exactly, or case-insensitively when that is unique). Not in the list: stop,
  list the valid values in plain words, ask the user to pick.
- Supplier site ID: free text on the screen (no list); used exactly as given.

Not required (proven by ZZ_TEST_6050): address lines, city/state/postal code and
business purposes. Oracle saves a site without them.

OPTIONAL - if missing, the UI default (what the form shows when it opens):

| Request key | Screen field (section) | UI default | Kind |
|---|---|---|---|
| `duns_number` | D-U-N-S Number (Organization Information) | empty | text |
| `taxpayer_id` | Taxpayer Identification Number | empty | text |
| `account_description` | Account Description (Account Information) | empty | text |
| `account_type` | Account Type | empty | drop-down: External, Internal |
| `customer_class` | Customer Class | empty | drop-down: Federal class, Public sector companies |
| `account_established_date` | Account Established Date | Oracle's today | date |
| `account_termination_date` | Account Termination Date | empty | date |
| `account_notes_other` | Account Notes Other | empty | multi-line text |
| `shipping_instructions` | Shipping Instrustions (Oracle's spelling) | empty | multi-line text |
| `customer_agreement` | Customer Agreement | empty | multi-line text |
| `address_from_date` | From Date (Account Address) | Oracle's today | date, required on screen but pre-filled |
| `address_to_date` | To Date (Account Address) | empty | date |
| `site_name` | Site Name (Address) | empty | text |
| `mail_stop` | Mail Stop | empty | text |
| `country` | Country | United States | drop-down (full country list) |
| `address_line_1`, `address_line_2` | Address Line 1 / 2 | empty | text |
| `state` | State | empty | Oracle geography list (US: two-letter codes, e.g. CA) |
| `city` | City | empty | Oracle geography list, narrowed by state; stored in capitals |
| `postal_code` | Postal Code | empty | Oracle geography list |
| `responsible_mineral_status` | Responsible Mineral Status | empty | list: Conflict Free, N/A, No Data, Undetermined |
| `address_note` | Address (extra field under the address) | empty | text |
| `url` | URL | empty | text |
| `contact_email` | ContactEmail | empty | text |
| `authorizer` | Authorizer | empty | text |
| `sales_tax_geocode` | Sales Tax Geocode | empty | text |
| `sales_tax_inside_city_limits` | Sales Tax Inside City Limits | ticked (true) | true/false |
| `customer_category_code` | Customer Category Code (Account Address Details) | empty | drop-down, **empty list in this pod** |
| `site_language` | Site Language | empty | drop-down (American English, Arabic, ... 37 languages) |
| `translated_customer_name` | Translated Customer Name | empty | text |
| `key_account` | Key Account | unticked (false) | true/false |
| `trading_partner_identifier` | Trading Partner Identifier | empty | **numbers only** (Oracle: "The value must be a number") |
| `edi_location_code` | EDI Location Code | empty | text |
| `purposes` | Address Purposes table: Purpose, From Date, To Date, Primary, Bill-to Site | no rows | list, see "Address purposes" below |

Read-only on the form (assigned by Oracle when the form opens): Registry ID, Account
Number, Site Number, purpose Site number. Not supported yet: Business Unit (Edit Site page only).

### Address purposes (one row per purpose; added Primary and Bill-to Site 2026-10-23)

| Row key | Screen column (Address Purposes) | Default if empty | Kind / rule |
|---|---|---|---|
| `purpose` | Purpose | - (required in a row) | drop-down, 18 values (below); each purpose once per customer |
| `from_date` | From Date | Oracle's today | date; must lie within the address dates (HZ-120150) |
| `to_date` | To Date | empty | date |
| `primary` | Primary (the table's **Set Primary** action) | no | true/false. **One Primary per type of purpose**: two rows of the same purpose marked Primary are refused before Oracle is opened ("Only one Bill to purpose can be Primary ..."). Note: Oracle **makes the first purpose of each type Primary by itself on save** (seen on ZZ_TEST_2743: Bill to and Ship to both Primary, none requested), so "no" doesn't keep a lone purpose non-Primary; verification checks Primary only when it was asked for and prints a NOTE otherwise |
| `bill_to_site` | Bill-to Site | **empty on a Ship to row = picked automatically** (2026-10-23) | a list field Oracle offers **only on a Ship to row**, holding only this customer's own address, written "Address Line 1,Address Line 2 (if any),CITY, STATE Postal Code" (e.g. `1 Infinite Loop,Suite 5,CUPERTINO, CA 95014`; a customer made here has exactly one address). Empty on Ship to (when the customer has a Bill to purpose): the script picks that one option. A typed value must be one of the options (exact, else the same ignoring case and extra spaces). The page's preview checks all of this before Create (root CLAUDE.md > The upload sheet) |

Request example: `"purposes": [{"purpose": "Bill to", "primary": true}, {"purpose": "Ship to",
"bill_to_site": "1 Main Street,CUPERTINO, CA 95014"}]`.

Dates in the request: `YYYY-MM-DD`. Missing date: the form's default (or empty).
`"today"` = **Oracle's today minus one day**. Oracle's today is read from the form,
never the PC clock: the default From Date (Account Address) that Create Customer shows
when it opens, read before anything is filled. The script prints a NOTE with the date
it used (changed 2026-10-20; before, it used the PC date minus one).

How each pick-from-a-list value is checked live (nothing is ever guessed or renamed;
a value that doesn't match stops the run before saving, lists the valid values in plain
words and asks the user to pick):

| Field | Read live from | When the value isn't there |
|---|---|---|
| Account address set | Create Customer form > Account Address Set > Search... > empty search: every set (name and code) | stop, list all sets (name and code) |
| Country | the form's Country drop-down options | stop, list the countries |
| State, City, Postal Code | typed into the form; Oracle accepts it or opens its Search and Select dialog (an exact match is picked) | stop: the place **does not exist in Oracle's geography**; it cannot be created here; Oracle's search results are shown |
| Purpose | the Address Purposes row's Purpose drop-down | stop, list the purposes |
| Account Type, Customer Class, Site Language, Customer Category Code, Prefix | the form's drop-down options | stop, list the options |
| Responsible Mineral Status | typed into the form, as for geography | stop, show Oracle's search results |

Free text, no list: customer name (first/middle/last name for persons), supplier site
ID, address lines, site name, mail stop, URL, contact email, authorizer, notes, tax and
EDI fields (Trading Partner Identifier: numbers only, Oracle's own check).
REST could list address sets (`setIdSetsLOV`, fscmRestApi) and countries (crmRestApi
`.../Address/CountriesLOV`), but the form's own lists are what the form accepts, so the
script reads them on the form.

Drop-down values, as read from the screen (add new ones when seen; never rename):
- Account address sets (36 on 2026-10-20; name (code)): 001 Customer Site (001 CUSTOMER SITE),
  28REFDATA (28REFDATA), A1 Data Set (A1_DATA_SET), AHSAN RDS NAME (AHSAN RDS),
  AK Referance Data Set (AKREFDATA), ASCEND (ASCEND_001), Asad123 (ASAD123), Ash (25010114),
  Ash BU Reference Data Set (ASH-25010114), Ash Bash (ORA25010114), CUSTOMER_RDS (CUSTOMER_RDS),
  DSSREFDATA (DSSREFDATA), Duck set (221), Enterprise Set (ENTERPRISE),
  GoSaaS Labs Data Set (SET0001), HAHAREFDATA (HAHAREFDATA), ITBY (ITBU), Ln106 (1111),
  MA_CUST_SET (MA_CUST_SET), MG US1 Business Unit (MGREFST), MGREF-AP (MGREF-AP),
  MNC_CUST_OM_RDS (MNC_CUST_OM_RDS), MWBK BU 1 (MWBKBU1), MWBK BU 2 (MWBKBU2),
  Mannan's Set (23), Mominaset (MOMINA12), N24REFDATA (N24REFDATA), Northwind (NMT),
  PPREFDATA (PPREFDATA), PRC100 Reference Data Set (PRC100R), Project Set (S-31),
  S Data Set (S_DATA_SET), T2 set (21), T22 set (7382), TEST (TEST), USAMA SET (25010094).
  The script reads the live list on every run, so new sets are accepted automatically.
- Purposes: Acknowledgments, Bill to, Bills of lading, Correspondence, Credit contact,
  Credit memos, Deliver to, Drawee, Dunning, Installed at, Invoices, Late charges,
  Legal, Self service user, Ship to, Sold to, Statements, Subscription Location.
- Account Type: External, Internal. Customer Class: Federal class, Public sector companies.
- Responsible Mineral Status: Conflict Free, N/A, No Data, Undetermined.
- Geography seen: state CA (also CALIFORNIA exists, so "CA" opens a choice that the
  script resolves to the exact match); CUPERTINO / 95014 valid. **Corrected 2026-10-23:**
  postal code 94105 exists, but only for SAN FRANCISCO, CA (the Postal Code search dialog
  lists "94105, SAN FRANCISCO, SAN FRANCISCO, CA"); the earlier "not found" was 94105 with
  Cupertino.
- Supplier site IDs used so far (free text, all accepted): 12345, 1001, 1002, 2001, 2002, 3001.
- Person Prefix: Mr., Mrs., Ms.

### Person customers

Customer Type "Person" turns the same Create Customer form into **Create Person
Customer** (heading changes; no separate task). Section **Person Information** replaces
Name and D-U-N-S Number (no D-U-N-S for persons); Account Information, Account Address,
Address, Account Address Details and Address Purposes are identical to organizations.

REQUIRED for a person (seen 2026-10-20): **First Name** (the only person field with an
asterisk), Account Address Set, Supplier Site ID. Oracle's save check lists only Account
Address Set and Supplier Site ID; a person with just a first name saves (ZZ_TEST_4055).
Last Name is NOT required. If the first name is missing, ask.

| Request key | Screen field (Person Information) | UI default | Kind |
|---|---|---|---|
| `first_name` | First Name | empty | text, required |
| `prefix` | Prefix | empty | drop-down: Mr., Mrs., Ms. |
| `middle_name` | Middle Name | empty | text |
| `last_name` | Last Name | empty | text |
| `suffix` | Suffix | empty | text (free, e.g. Jr.) |
| `taxpayer_id` | Taxpayer Identification Number | empty | text |

Not allowed for a person (rejected as unknown): `name`, `duns_number`.

The customer's name in Oracle = First Middle Last Suffix, e.g. "ZZ_TEST_9231 Q Tester
Jr."; the prefix is not part of it (Manage Customers shows it in its own column,
Salutary Introduction). The existence check and verification use that name, searched
with Manage Customers > Customer Type Person > Name.

## Route status

- **REST: NOT SUPPORTED for a whole customer** (checked 2026-10-21, read-only: describe +
  GETs, nothing created). The CRM REST API (`/crmRestApi/resources/11.13.18.05`) has
  `hubOrganizations` and `accounts`. They create the **organization (party)**, its
  **address (party site)** and party-site purposes, with Basic auth (HTTP 200 on GET).
  But no REST resource in this pod creates the **customer account**, the **account
  site** with its **account address set**, or the **account site's business purpose**:
  `customerAccounts` and `customerAccountSites` return 404 on both REST bases, and
  `receivablesCustomerAccountSiteActivities` is read-only. The **Supplier Site ID**
  location flexfield is not among the REST address attributes either. A GET of
  ZZ_TEST_8902 shows only the party (130318, usage EXTERNAL_LEGAL_ENTITY); `accounts`
  returns nothing for it. Oracle's docs point to the SOAP CustomerAccountService for
  accounts with sites and uses, which is not used here. So the form fill below stays
  the route; REST would leave a half-made customer.
- **Playwright form fill on the classic layout (back 2026-10-21): `--check` PROVEN**
  2026-10-21 after a repair in this folder. The task opener detects the layout and, on
  classic, uses this folder's classic steps (Offering drop-down, Search Tasks, the
  result in Customers, the task link). Existing customer Abdullah_prince100 skipped with
  its values; Create Organization Customer opened, 36 address sets read, Oracle's today
  10/20/26, left with Cancel. **Full save on classic PROVEN** the same day: ZZ_TEST_2336
  (Enterprise Set, supplier site ID 3008) saved, every account and site value read back
  on Edit Account / Edit Site, the 6 existing ZZ_ customers unchanged; 89 seconds.

- **Playwright form fill: PROVEN** (2026-10-20, clean runs):
  - ZZ_TEST_8757 (all supported fields, two purposes Bill to + Ship to, established
    date "today" -> 2026-10-19): saved, every value read back on Edit Account and Edit
    Site, sites table shows Enterprise Set and "Bill to, Ship to". About 4 minutes.
  - ZZ_TEST_6050 (required only, set CUSTOMER_RDS by code, supplier site ID 1002):
    defaults confirmed (Account Established Date and From Date = Oracle's today
    10/20/26, Country United States, Sales Tax Inside City Limits ticked, Key Account
    unticked, everything else empty, no purposes). ZZ_TEST_8757 in the same run was
    skipped and its values printed. Existing ZZ_ customers unchanged.
- **Person customers, Playwright form fill: PROVEN** (2026-10-20):
  - ZZ_TEST_4055 (required only: first name, Enterprise Set, supplier site ID 2001):
    saved, every value and default read back (Edit Account shows Prefix, First, Middle,
    Last Name and Suffix; defaults as for organizations).
  - ZZ_TEST_9231 Q Tester Jr. (Ms., middle Q, last Tester, suffix Jr., taxpayer ID
    123456789, CUSTOMER_RDS, supplier site ID 2002, account fields, address in
    CUPERTINO CA 95014, key account, trading partner 777, Bill to + Ship to, established
    date "today" -> 10/19/26): saved. The run's own verification first failed only
    because the script expected the name without the suffix; after the name rule was
    fixed, the same `verify()` passed for every value (run read-only from a scratch
    harness, nothing saved again). Existing ZZ_ customers unchanged.
  - `--check` with all three test customers: all skipped with their values; the
    Organization and the Person form both open and are left with Cancel.
- **CSV export/import: NOT SUPPORTED** for this task (Actions entries disabled,
  checked 2026-10-20 in both functional areas and for Manage Customers).
- **REST: not used** (excluded for this folder).

## How to do it

From the project root:

```
python "Customers/browser_flow.py" --check     # fill and check every value on the form, save nothing
                                               # (only existing customers requested: opens the form,
                                               # reads the address-set list and Oracle's today, Cancel)
python "Customers/browser_flow.py"             # full run (headless)
python "Customers/browser_flow.py" --headed    # same, browser visible
```
(Page commands `--spec`, `--options`, `--run`: see Page interface.)

Request file `Customers/customers.json`:

```json
{"customers": [{
  "name": "Acme Widgets",                    // required
  "account_address_set": "Enterprise Set",   // required, name or code from the list
  "supplier_site_id": "1001",                // required, free text
  "account_type": "External",                // optional, see the table above
  "address_line_1": "1 Main Street", "state": "CA", "city": "Cupertino", "postal_code": "95014",
  "purposes": [{"purpose": "Bill to", "primary": true},
               {"purpose": "Ship to", "from_date": "2026-11-01", "bill_to_site": "1 Main Street,CUPERTINO, CA 95014"}]
}, {
  "customer_type": "Person",                 // "Organization" (default) or "Person"
  "first_name": "Jane",                      // required for a person
  "prefix": "Ms.", "middle_name": "Q", "last_name": "Doe", "suffix": "Jr.",   // optional
  "account_address_set": "Enterprise Set",   // required
  "supplier_site_id": "4004"                 // required
}]}
```

(Comments are documentation only; the real file is plain JSON. Unknown keys are
rejected so nothing is dropped silently.)

One-line sample requests (plain words -> the file):
- "Create customer Acme Widgets, address set Enterprise Set, supplier site ID 1001."
- "New customer Beta Ltd in CUSTOMER_RDS, supplier site 2002, bill-to address 1 Main
  Street, Cupertino CA 95014."
- "Add customer Gamma Inc, address set Enterprise Set, supplier site 3003, external
  account, key account, ship to and bill to purposes from today."
- Person: "Create a person customer Jane Doe, address set Enterprise Set, supplier site
  4004." -> `{"customer_type": "Person", "first_name": "Jane", "last_name": "Doe", ...}`
- Person: "New person customer Ms. Ana Q Lee Jr., CUSTOMER_RDS, supplier site 5005,
  bill to 2 Main Street, Cupertino CA 95014."

What `browser_flow.py` does (via `common/browser.py` OracleUI):
1. Prints host and ORACLE_ENV, refuses production, validates the request file.
2. Per customer: Manage Customers search by name (Setup and Maintenance > Financials >
   Search Tasks "Manage Customers"). Customers with the same name are listed (registry
   IDs) and never opened for editing; the run goes on and creates a new one.
   Rerun guard: if `_work/saved_requests.json` says an earlier try of this same request
   (same values) saved a customer within 12 hours, and a new customer with the name is
   there, the run verifies that one instead of filling the form again (written just
   before and after Save and Close; deleted with `_work/` after a verified success).
3. Snapshot of existing customers whose name starts with the same 3 characters.
4. Opens Create Customer (Search Tasks "Create Customer", result in area Customers,
   then the task link; the form "Create Organization Customer" opens in the same page)
   and reads the Registry ID it shows (assigned when the form opens).
5. Reads the Account Address Set list (Search and Select dialog, empty search, all
   rows) and matches the request; fills every requested field in screen order (country
   first; state, city, postal code in that order). Drop-downs are checked against the
   screen's options; list fields (state, city, postal code, mineral status) are typed
   and Tabbed, and when Oracle opens its search dialog the exact match is picked, else
   the script stops with what Oracle's search showed. Any field Oracle marks invalid
   (red border) stops the run with Oracle's message, before saving.
6. Adds one Address Purposes row per purpose (+), picks the purpose, sets dates.
7. Reads the whole form back (requested values + defaults), then Save and Close.
   "Warning: Matching Organizations/Persons": Option 2 (create new) is selected (checked
   it stays selected, Option 1 not) and OK pressed; if the choice can't be found, Cancel on
   the warning and the form, nothing saved, stop. Success = the page goes to Manage
   Customers; an Oracle message dialog = failure with its text.
8. Verification: search by name -> the customer with the form's Registry ID (else the one
   name match that wasn't there before saving), one account, one site;
   sites table address set (shown by name) and purposes; Edit Account (name, DUNS,
   taxpayer ID and every account field incl. established date); Edit Site (every site
   field, purposes with from/to dates by column). Both pages are left with Cancel.
9. Existing customers from the snapshot: name, country and primary address unchanged.
10. Deletes `_work/` after a verified success; keeps it (screenshots, page text) on failure.

Manual click path (reference): Setup and Maintenance > Offering "Financials" >
Search Tasks "Create Customer" > result with functional area Customers > task
"Create Customer" in the Customers list > fill > Address Purposes "+" > Save and Close
(lands on Manage Customers with the new customer selected). To find it again: Search
Tasks "Manage Customers" > Organization Name > Search > click the row (Accounts and
Sites tables fill) > account number = Edit Account, site number = Edit Site.

## Page interface

Contract: root CLAUDE.md > Page interface (helper `common/page.py`). **PROVEN 2026-10-21**
for organizations (ZZ_TEST_4418, below); persons use the same run with
`"customer_type": "Person"` (their checks were tried, a person `--run` save was not).
One customer per `--run`; `customers.json` and the normal commands are unchanged.

```
python "Customers/browser_flow.py" --spec
python "Customers/browser_flow.py" --options account_address_set   # also: customer_type, prefix,
                                     # account_type, customer_class, country, state, purposes.purpose
python "Customers/browser_flow.py" --run '{"name": "Acme Widgets", "account_address_set": "Enterprise Set", "supplier_site_id": "1001"}'
```

**Every request-file field in `SPEC` (2026-10-23).** The page no longer has forms; it
reads an uploaded sheet (root CLAUDE.md > The upload sheet) and sends one customer to
`--run` with every column of the sheet. So `SPEC` now also holds the fields that were only
in the request file (termination date, notes, address to date, mail stop, mineral status,
URL, contact email, authorizer, tax and EDI fields, site language, translated name,
customer category code; all optional). Proven through the page the same day:
ZZ_TEST_6183 (organization, Enterprise Set, supplier site ID 3010, 1 Infinite Loop
CUPERTINO CA 95014, Bill to; registry ID 130508; the saved sign-in had expired, the page
opened the sign-in window and ran the same request again) and **the first person saved
through the page**, ZZ_TEST_1125 Person (same values, no purposes; registry ID 130512).
Both read back on Edit Account / Edit Site, verified.

**Several customers per sheet (2026-10-23, fourth request).** The page sends a sheet's
customers one after another, each as one `--run` (unchanged: one customer per `--run`).
Folder changes for it:
- `--existing` and `--check-address` also take a JSON list (one browser visit; answer
  `{"ok", "results": [...]}`); the page asks `--check-address` once per distinct place.
- Rerun note per customer: a verified customer removes only its own entry from
  `_work/saved_requests.json` (`journal_drop()`); `_work/` is deleted only when no other
  customer's entry is left (else "Kept ...: N other saved customer(s) still to be checked by a
  retry"), so a later retry of a saved-but-unchecked customer still never saves it twice.
- A failed `--run` says in `error.detail` `{"message", "saved": "no" | "yes" | "maybe",
  "registry_id"}` (no = a plain stop before saving or no note; yes = the note says saved;
  maybe = it stopped during Save and Close). The page puts only "no" customers in the
  failed-only sheet.
Tested through the page 2026-10-23 with the user's 3-customer sheet (organizations
ZZ_TEST_6842, ZZ_TEST_5862, ZZ_TEST_7163, Bill to + Ship to each): preview clean for all three
(47 s; the place check was reused from the previous upload, one place for all three). Create:
ZZ_TEST_6842 **130588** (3 min 5 s), ZZ_TEST_5862 **130591** (3 min 6 s), both every value and
both purposes read back OK; ZZ_TEST_7163 stopped after 1 min 7 s with "sign-in expired",
nothing saved (a false alarm, see gotchas), the result offered the failed-only sheet with
exactly its row and two purposes; that sheet uploaded and created **130596** (3 min 6 s, all
values OK). (b) wrong postal code on customer 2 and wrong Bill-to Site on customer 3: both
red and first, Create refused. (c) two customers named ZZ_TEST_6842 / "zz_test_6842 ": stopped
"Two customers are named ZZ_TEST_6842. ...". (d) offline: a refusal in the middle, the others
continued, failed-only sheet right; a saved-but-unchecked one listed apart, not in that sheet.

**Customer Name joins purposes to their customer (2026-10-23, third request).** The sheet's
Address Purposes tab starts with a required "Customer Name" (page only; not a request key,
not sent to Oracle). It must equal the customer's Name (organization) or First Name + space +
Last Name (person; Middle Name and Suffix not part of it), ignoring case and extra spaces;
see root CLAUDE.md > The upload sheet > Join key. The folder itself is unchanged by this:
the page still sends one customer with its `purposes`. Tested through the page: (a) the
user's sheet as is (ZZ_TEST_4836) clean; (b) a row naming ZZ_TEST_9999 -> red "This address
purpose belongs to 'ZZ_TEST_9999', but the customer in this sheet is 'ZZ_TEST_4836'.", Create
refused; (c) empty Customer Name -> red "Customer Name is missing.", Create refused; (d) both
tabs filled with the same name -> the one-customer stop comes first (the same-name stop shows
only when several customers are allowed; checked offline); (e) person ZZ_TEST_4836 Q Person Jr
with Customer Name "zz_test_4836   PERSON" / " ZZ_TEST_4836 Person " -> clean. Created from
(a) as **ZZ_TEST_6619, Registry ID 130584** (Bill to + Ship to, Bill-to Site picked
automatically, 35 fields and both purposes read back OK, 18 existing ZZ_ customers unchanged,
about 3 minutes, no repair).

**Everything checked before Create (2026-10-23, second request).** The preview checks, so a
`--run` from the page only runs:
- Bill-to Site (registry `address_pick`): empty on Ship to -> "Picked automatically" with the
  text built from the sheet's address; a typed value compared ignoring case and extra spaces
  (spaces around commas too); wrong -> red "Use '<text>', or leave it empty to use this one.";
  on a non-Ship to row -> ignored with a note; Ship to without Bill to -> the preview stops.
- City / State / Postal Code: `--check-address '<request>'` (read-only): opens Create
  Customer, uses only the City and Postal Code **Search and Select dialogs** (search text in
  the dialog, rows like "CUPERTINO, SANTA CLARA, CA" and "95014, CUPERTINO, SANTA CLARA, CA"),
  Cancel on each and on the form; nothing is typed into the customer's fields, nothing saved.
  City must exist in the State; Postal Code must exist for that City and State. About 35 s
  (form 14-19 s, 5 s per search). State itself is checked against the live State list
  (`--options state`). Only for country United States (others: checked while creating).
  REST can't do it here (checked 2026-10-23): Oracle's resource catalog lists crmRestApi
  `geographies` (countries only) and `geographiesLOV` (returns no rows for any query, no
  finders); no state, city or postal code is readable by REST.
- Failures after Create: `run_request` turns any stop into plain text with what was and
  wasn't created ("Nothing was saved in Oracle.", or "The customer X was saved in Oracle
  (Registry ID N), but checking it didn't finish. ...", from the rerun note).
Tested through the page 2026-10-23 with ZZ_TEST_8352 (Bill to + Ship to, every column):
(b) Bill-to Site "2 Wrong Road,CUPERTINO, CA 95014" -> red with "Use '1 Infinite Loop,Suite
5,CUPERTINO, CA 95014', or leave it empty to use this one.", Create refused ("not ready");
(c) Ship to without Bill to -> preview stopped; (d) Postal Code 94105 -> red "Postal code
94105 isn't one Oracle has for CUPERTINO, CA." / "Oracle has 94105 only for SAN FRANCISCO,
CA. ...", Create refused; (a) Bill-to Site empty -> preview "1 Infinite Loop,Suite
5,CUPERTINO, CA 95014" + "Picked automatically", City and Postal Code "Found in Oracle";
Create -> **Registry ID 130554**, Bill-to Site picked automatically, every value (35 fields,
both purposes, Bill-to Site, Primary) read back OK, 16 existing ZZ_ customers unchanged,
no repair, about 3 minutes. Offline: typed " 1 infinite loop, suite 5 ,cupertino,  ca 95014"
accepted; a Bill-to Site on the Bill to row ignored with the note.

**Same-name customers and the full sheet test (2026-10-23).** `--existing '<request>'`
(read-only, Manage Customers search, about 20 s, one retry) gives the page its preview note
"N customers named X already exist (Registry IDs ...). Create will make a new one." The
`--run` result names the new Registry ID ("Created the organization customer X with
Registry ID N ... 2 other customers with this name (Registry IDs ...) were not touched.");
`created.registry_id` comes first. Tested through the page with the user's
Customer_upload_sheet (every column filled except Customer Category Code and Site Language,
Bill to + Ship to, both Primary, Ship to with its Bill-to Site):
- both customer tabs filled -> stopped before anything ("More than one customer tab is filled ...").
- organization ZZ_TEST_3727, first upload: preview "No customer named ZZ_TEST_3727 exists in
  Oracle yet."; first Create stopped twice, nothing saved: Set Primary refused (SetId error,
  repaired automatically, see gotchas) and then Bill-to Site refused (Oracle offers
  "1 Infinite Loop,Suite 5,CUPERTINO, CA 95014"). With only that cell corrected: created
  **Registry ID 130524**, every value read back OK, no matching warning.
- same organization copy again: preview "1 customer named ZZ_TEST_3727 already exists
  (Registry ID 130524). Create will make a new one."; Oracle's matching warning came, Option 2
  was chosen. Created **130527** (that try then stopped on the "came back" timing, repaired)
  and, because of the `_work/` bug in the gotchas, the rerun created **130530** too. Both read
  back OK (130530 by the run, 130527 by the read-only guard check). 130524 unchanged.
- person ZZ_TEST_2536 Q Person Jr (Mr.): created **Registry ID 130534**, no warning, every value
  read back OK.
Per column, both rows (organization and person), all **accepted and read back correctly**:
Name / Prefix, First, Middle, Last Name, Suffix; D-U-N-S Number (organization); Taxpayer
Identification Number; Account Description; Account Type; Customer Class; Account Established
Date; Account Termination Date; Account Notes Other; Shipping Instrustions; Customer Agreement;
Account Address Set (sites table); From Date; To Date; Site Name; Mail Stop; Country; Address
Line 1; Address Line 2; City (stored CUPERTINO); State; Postal Code; Responsible Mineral Status;
Address; URL; ContactEmail; Authorizer; Supplier Site ID; Sales Tax Geocode (123456789);
Sales Tax Inside City Limits; Translated Customer Name; Key Account; Trading Partner Identifier
(12345); EDI Location Code; purposes Primary, Purpose, From Date, To Date, Bill-to Site.
Refused: only Bill-to Site as first written (without Address Line 2). Customer Category Code
and Site Language were empty in the sheet and read back empty.

**Form order and type rules (2026-10-21).** Up front, in this order: customer_type
(required, default Organization), then the name that type needs - name ("Organization
name", `required_when` / `shown_when` customer_type Organization) or first_name
(Person) - then account_address_set and supplier_site_id. "More options" holds only
optional fields; the other type's fields are hidden (prefix, middle/last name, suffix only
for a Person; D-U-N-S only for an Organization). These use the contract's optional keys
`required_when` / `shown_when` (common/page.py); a value for the other type stops with
e.g. "Prefix only applies when Customer type is Person."

**Drop-down samples (2026-10-21).** The page's lists are short samples written in `SAMPLES`
in `browser_flow.py`, so the form opens at once with no browser visit. **A value joins the
samples only after a real, verified create in this project** (a customer saved with it and
every value read back on Edit Account / Edit Site); until then it can still be typed.
Current samples, all proven: account address set **Enterprise Set** (ZZ_TEST_2336,
ZZ_TEST_4418, ...), **CUSTOMER_RDS** (ZZ_TEST_6050, ZZ_TEST_9231 Q Tester Jr.), **001
Customer Site** (Abdullah_prince100); country **United States**; state **CA**; purposes
**Bill to**, **Ship to**. The small screen lists keep their full values (customer type
Organization, Person; prefix Mr., Mrs., Ms.; account type External, Internal; customer
class Federal class, Public sector companies). Address set, country,
state and purpose are marked `"list": "samples"`: another value can be typed and `--run`
checks it against the full live list from the form. The full live lists stay behind a switch:
`python "Customers/browser_flow.py" --options FIELD --all` (about 60 s, one form visit).

Form (`SPEC`): required for both types: account_address_set (pick), supplier_site_id
(text). customer_type (pick, default Organization). Organization: name (needed),
duns_number. Person: first_name (needed), prefix (pick), middle_name, last_name, suffix.
Both: taxpayer_id, account_type (pick), customer_class (pick), account_description,
account_established_date, address_from_date (dates; "today" = Oracle's today minus one),
site_name, country (pick, default United States), address_line_1/2, state (pick), city,
postal_code (text, checked against Oracle's geography on the form), key_account (yes-no),
purposes (rows: row label "Purpose", button "Add a purpose"; purpose (pick), from_date,
to_date, primary (yes-no, 2026-10-23), bill_to_site (text, 2026-10-23; checked against the
row's list on the form)). Two Primary rows of one purpose: INVALID_REQUEST in `checking`. The other request-file fields (notes, URL, tax and EDI fields, ...) are not on
the form. The contract has no "required for one type" flag, so name and first_name are
optional in `--spec` (with a help line) and `run_request` asks for the one the type needs;
a field of the other type (e.g. D-U-N-S for a person) stops in plain words.

Pick lists, read live from the Create Customer form in **one** browser visit per process
(`form_lists()`, cached): Customer Type, Account Address Set (Search and Select, every
set; value = code, label = name), Account Type, Customer Class, Country, State (the State
field's Search and Select, **United States** list, 105 incl. CA and CALIFORNIA), a new
Address Purposes row's Purpose list (18), then the person form's Prefix (3). Nothing is
saved: Cancel (and Yes if Oracle asks). About 45-60 s per `--options` call.
State is a United States list: a state of another country is refused by the page check
(known limit). City and postal code have no list (unbounded, narrowed by the state);
the run types them and Oracle accepts them or not.
Plain stops inside the run: while `--run` goes, this folder's `run_request` swaps
`oracle.fail` (in this process only, restored after) so that a value Oracle doesn't
have (a screen list, the geography, a field Oracle rejects) or a refused save comes back
as NOT_IN_ORACLE / INVALID_REQUEST with plain text (the full message stays in detail);
every other stop behaves exactly as before.
Steps: reading 5, checking 20 (the lists), `filling` 35 ("Filling in the customer form",
incl. the existence search and snapshot), creating 60 ("Saving the customer in Oracle"),
verifying 80 ("Checking the customer, its account and its address"), done 100. Result
`created`: registry ID, address set, every requested value as the form showed it, purposes.
Result "where": Setup and Maintenance > Financials > Customers > Manage Customers.
Tried 2026-10-21: `--spec` OK; all eight `--options` OK (Organization/Person; Mr., Mrs.,
Ms.; External/Internal; 2 classes; 250 countries; 105 states; 18 purposes) and
`--options name` -> NOT_A_LIST_FIELD; organization without a name -> "Please fill in
Customer name (needed for an organization)."; person with a D-U-N-S number -> refused;
purpose 2 "Teleport to" -> NOT_IN_ORACLE with the 18 purposes; city "Springfeld" in CA ->
"City: Oracle does not accept 'Springfeld'. Nothing was saved." (NOT_IN_ORACLE).
First real `--run` ZZ_TEST_4418 had purpose Ship to from "today" (10/20) while the
address starts on Oracle's today (10/21): Oracle refused the save (HZ-120150 "The date
range for a child record must be within the date range of its parent record"), nothing
saved; the page then said only "Something went wrong", so refused saves were added to the
plain stops. Rerun ZZ_TEST_4418 (Enterprise Set, supplier site ID 3010, External, 1 Main
Street CUPERTINO CA 95014, Bill to + Ship to from 2026-11-01): not found before, all
progress lines, saved (registry ID 130359), every account and site value and both
purposes read back on Edit Account / Edit Site, the 8 existing ZZ_ customers unchanged.
160 seconds.

## Related folders

None noted. (If this configuration needs another folder's object, note it here, tell
the user and wait for their go-ahead before writing any code.)

## Known gotchas

- 2026-10-26 (repair): Emberlight Interactive Studios D01 (Registry ID 130952, Account Established Date and
  address From Date 11/1/26, Oracle's today 10/26) saved, but Manage Customers showed 0 accounts and 0 sites for
  it (3 tries), so verification failed. Manage Customers lists an account / site only from its start date.
  `verify()` now accepts a customer found by its Registry ID with no account and no site when the requested
  established or address from date is after Oracle's today (kept in the rerun note as `oracle_today`), with a
  NOTE that the account and site values can be read back only from that date. Not yet seen on screen whether
  Manage Customers has a filter to show them earlier.

- 2026-10-26 (later): **Every browser step checked and done again (shared retry helper).** The two retries below
  now use `ui.retry()` from `common/browser.py` (up to 3 tries, a short pause and a fresh wait each time, then one
  clear failure "Oracle's <step> after 3 tries", which `--existing`, `--check-address` and `--plan` pass to the page
  as their `text` through `browser.failed_step_text()`). Checked the same way: the Offering drop-down and option
  (Setup title), Search Tasks (results window), the result row (results window gone and the task listed), the task
  link (`classic_search_task(..., heading)`: Create Customer by the form heading, Manage Customers by its heading),
  the Manage Customers search panel and Search (rows of this name; no rows believed when Oracle's page sent the
  Search, seen by its request, else only when a second search agrees; another name's old rows = a lost search),
  the result row (soft: until its accounts and sites show), Edit Account / Edit Site open and Cancel back
  (`open_edit()`, `back_to_manage()`), the place dialogs (list, Search..., the pick's OK closing the dialog, Cancel
  through `ui.close_dialog()`), the Bill-to Site cell and list (soft: a lost click no longer reads as "Oracle
  offers no Bill-to Site"), and leaving the form unsaved (`leave_form()`: form heading gone). **Never retried:**
  Save and Close, Option 2 + OK, Add Row on Address Purposes, Set Primary (its own 2 tries). The page also runs
  the checks one after another now (one Oracle browser at a time), and re-runs a check that couldn't run up to 2
  more times, 20 s apart. Proven 2026-10-26 (read-only, through the page's upload check,
  `page/_work/proof/check_runs.py`): Best Start (2).xlsx (19 records, six modules) checked 14 times in a row before
  the user cut the proof short, all ready, 180-213 s (average 192 s), no step needed a retry and no check a re-run;
  a generated 5-customer sheet (ZZ_TEST_CU_4871 ..., Dallas TX 75201 / Seattle WA 98101) ready, about 170 s of
  checking. Not done (user's time limit): the 100-customer runs and the busy-machine stress run.
- 2026-10-26: **Lost clicks while three checks open Oracle at once.** The preview starts the Customers checks
  side by side (`--existing`, `--check-address`, `--plan`), three browsers on one sign-in. The busy classic Setup
  page then sometimes drops a search ("Search Tasks showed no results window for 'Create Customer'", the text
  still in the box) or a click on the task link (the task list stays, its Create Customer row highlighted), and
  the preview stopped with "The customers couldn't be checked with Oracle just now (no answer)" (uploads Best
  Start.xlsx 17:09, Best Start (2).xlsx 18:13; reproduced with the three checks at once). Fix in this folder:
  `classic_search_task()` searches again (up to 3 tries, 20 s each, then 60 s) and `open_form()` clicks the task
  link again when Create Customer hasn't opened (up to 3 tries, 40 s each, then 90 s). Proven: two rounds of
  the three checks at once both passed, each needing one retry; the page's own check of Best Start (2).xlsx is
  ready (19 records, all six modules OK).
- 2026-10-23: **Primary and Bill-to Site on Address Purposes** (learned read-only on the
  unsaved form, six looks, Cancel each time):
  - The table's columns on Create Customer: Primary, Site, From Date, To Date, Purpose,
    Bill-to Site; on Edit Site: Primary, To Date, From Date, Purpose, Site, Bill-to Site.
  - Primary = toolbar action "Set Primary" (`_ATp:SetPrimaryFlagToolbar`) on the **selected**
    row; the row then shows an image titled "Primary Purpose" after about 1-3 s. A row is
    selected by clicking its Site number cell. Primary is kept per purpose type (a Bill to
    and a Ship to can both be Primary). On save Oracle makes the first purpose of each
    type Primary anyway.
  - **Rows found by position move**: a new purpose row is inserted at the top, so a locator
    taken from `.all()` (nth) points at another row afterwards (that gave mixed Primary
    results while learning). Rows are now kept by their Purpose select's id and checked
    against the purpose they show (`purpose_row()`).
  - Bill-to Site (`billToSiteUseIdId`, a list field) exists in every row but is shown only
    on a Ship to row, and only after its cell is clicked (its list button appears then).
    Its list = this customer's Bill to addresses; with no Bill to row it is empty, and
    Oracle keeps the list from the first time it is opened, so the script sets Bill-to Site
    only after all rows are added. **A typed value is not checked by the form** (a made-up
    "NO SUCH SITE" stayed; later an "Attribute SetId ... CustomerAccountSiteUseviaSite is
    required" error came up), so the script matches against the list itself.
  - Edit Site: the Bill-to Site cell holds a nested table, which ROWS_JS skips; Primary and
    Bill-to Site are read from the row itself (`PURPOSE_PRIMARY_JS`). The first (b) run
    (ZZ_TEST_2743) saved correctly but its verification read the column wrongly (FAIL);
    fixed, the same verification re-run read-only passed.
  - **Order: Primary first, Bill-to Site last.** Set Primary after a Bill-to Site was set
    made Oracle show "Attribute SetId in ... CustomerAccountSiteUseviaSite is required"
    (ZZ_TEST_1126 run, stopped while filling, nothing saved). `fill_form()` now sets every
    Primary, then every Bill-to Site.
  - 2026-10-23 (repair): ZZ_TEST_3727 (Bill to + Ship to, both Primary, Ship to with a
    Bill-to Site) got the same SetId error on Set Primary for Bill to **before** any Bill-to
    Site was set (stopped while filling, nothing saved). Since a purpose is never listed twice,
    each is the only one of its type and Oracle makes it Primary on save, so `fill_form()` no
    longer clicks Set Primary for such a row (only when a type is there more than once); the
    Edit Site verification still checks Primary = True.
  - **Proven 2026-10-23** through `--run` (the page's own output), each read back on Edit Site:
    (a) ZZ_TEST_2827 (registry ID 130490, Enterprise Set, supplier site ID 3011, 1 Main
    Street CUPERTINO CA 95014, Bill to Primary): ok, Primary = True, 166 s;
    (b) ZZ_TEST_1519 (registry ID 130502, supplier site ID 3015, same address, Bill to Primary
    + Ship to with Bill-to Site "1 Main Street,CUPERTINO, CA 95014"): ok, both read back,
    Ship to shown Primary by Oracle itself (not requested), 11 existing ZZ_ customers
    unchanged, 160 s. Refusals tried: Bill-to Site "99 Nowhere Road" -> NOT_IN_ORACLE "...
    Oracle offers: 1 Main Street,CUPERTINO, CA 95014. Nothing was saved." (ZZ_TEST_8147 not
    created); two Bill to rows Primary -> INVALID_REQUEST (page) / stop (request file);
    Primary "maybe" -> "Primary must be yes or no". `--check` with Primary + Bill-to Site:
    all values accepted, nothing saved (one earlier `--check` stopped at City on the late
    CA/CALIFORNIA dialog, a known timing issue; the rerun passed).
  - Not tried: Bill-to Site on the other 13 purposes; a person customer with these fields;
    a Bill-to Site pointing to another customer's or another site's Bill to (one site per
    customer here); Primary when the account already has a Primary purpose elsewhere.

- 2026-10-23 (repair): ZZ_TEST_3727's matching warning had **Option 1 selected by default**
  (a Name Match, registry ID 130524). The script switched to Option 2 and pressed OK, but the
  warning stayed on screen with OK greyed while Oracle worked, and the next check called it
  "came back after OK". `save()` now waits up to 90 s after OK for the warning to close
  before treating it as returned. (Whether that try saved is settled by the rerun guard.)
  **That try had saved (130527)**, and the rerun still made a third ZZ_TEST_3727 (130530):
  the rerun's `checking` step reads the form lists (`form_lists()`), which emptied `_work/`
  and with it the rerun note `saved_requests.json`. Fixed the same day: `form_lists()` (and
  `--existing`) keep `_work/` when it already has files. Proven read-only with a harness that
  blocks `save()`: given the note for 130527, the run said "an earlier try of this request
  saved ZZ_TEST_3727 (registry ID 130527); verifying it, not creating it again" and read
  every value of 130527 back OK (nothing saved).
  Warning layout (read 2026-10-23): two radios named DQ_CHOICE, labels "Select from existing
  organizations" (`...:sbr2`, checked by default) and "Create new organization based on what
  you provided" (`...:sbr1`); the Option 1 list shows "Name Match | <registry ID>" rows.
- 2026-10-23: false "sign-in expired": customer 3 of a sheet stopped at the first screen with
  a blank page (Oracle's sign-in service was still redirecting the saved session back; the
  sign-in check a minute later said valid). `setup_layout()` now waits up to 30 s for the
  redirect to return to Oracle (`wait_signed_in()`) before calling the sign-in expired.
- 2026-10-23: the Bill-to Site list text includes Address Line 2: with Address Line 2
  "Suite 5" Oracle offers "1 Infinite Loop,Suite 5,CUPERTINO, CA 95014", and the sheet's
  "1 Infinite Loop,CUPERTINO, CA 95014" was refused (NOT_IN_ORACLE, nothing saved).

- 2026-10-21: Manage Customers did not find TESTCUSTOMER3 (saved minutes before,
  registry ID 130453), so the run filled the form again; Save and Close then opened
  "Warning: Matching Organizations" (Option 1 select existing / Option 2 create new,
  OK / Cancel) and the script waited 3 minutes. Nothing was saved. (Then: the warning
  was cancelled and the customer reported as skipped. **Replaced 2026-10-23** at the
  user's request: Option 2, create new, always; see Input rules.)

- 2026-10-21: for Pakistan the site has no Sales Tax Geocode field (read as None on the
  form and on Edit Site); verification compared None with None as text and failed
  (TESTCUSTOMER3, saved correctly). `same()` now treats a missing text field as empty.

- 2026-10-21: Country other than United States (Pakistan, TESTCUSTOMER3) redraws the
  address fields late: Address Line 1 and City were typed, then shown empty. The script
  now waits for the redraw after Country (`wait_redraw()`) and fills any address field
  that came back empty once more before the form check.

- 2026-10-21: a purpose's From Date must lie within the address dates: Ship to from
  10/20/26 with the address from Oracle's today 10/21/26 made Save and Close fail with
  HZ-120150 ("The date range for a child record must be within the date range of its
  parent record"); nothing is saved. So a purpose from "today" (Oracle's today minus
  one) needs an address from date on or before that day.

- 2026-10-21: Oracle is back on the classic Setup and Maintenance layout; the shared
  navigation is Redwood-only, so `--check` stopped ("did not show its 'Set Up' page").
  Repaired in this folder: `setup_layout()` detects the layout (printed once per run)
  and `open_task_page()` uses the shared Redwood helper or this folder's classic steps.
- 2026-10-21: REST can't create the whole customer (no customer account, account site,
  account address set, account site purpose or Supplier Site ID in REST). Don't build a
  partial REST route: it would leave a party without an account.
- 2026-10-20: the "existing customers unchanged" check once found 0 customers for "ZZ_"
  although several exist; the "Abd" prefix searches after it worked (4-7 compared).
  Not investigated; the script never opens existing customers for editing.

- 2026-10-20: Oracle moved Setup and Maintenance to the new Redwood "Set Up Financials" page
  (the profile-menu path leads there too). The Create Customer task is found under
  Financials > Customers in the task list, which loads while scrolling. The form
  itself is unchanged (classic). Save and Close may return to the Set Up page
  instead of Manage Customers; both count as saved when no Oracle message appears.
  Proven by ZZ_TEST_5715 (Enterprise Set, supplier site ID 3001), with every value
  verified.

- 2026-10-20 (persons): Manage Customers shows person results in another table region
  (`pt_r2:0:AT1`, organizations `pt_r1:0:AT1`); accounts and sites tables are the same.
- 2026-10-20: Oracle sometimes opens the State choice dialog (CA or CALIFORNIA) only
  after the shared helper stopped waiting; City then failed ("search found nothing").
  The script now waits up to 6 s more for a late dialog (`late_dialog()`, this folder
  only) and picks the exact match.

- Create Customer does not appear in the Customers task table even with Show = All
  Tasks and scrolling (the list renders lazily); `OracleUI.search_task()` uses Search
  Tasks instead (2026-10-20).
- The Actions menu of the task row shows Export/Import/Compare, but all disabled
  (`aria-disabled="true"`). No CSV route.
- Typed list-of-values fields are NOT checked by the form: "BOGUS_SET" in Account
  Address Set stays without any message. The script therefore matches the address set
  against the live list itself.
- Search and Select dialogs keep hidden copies of fields with the same labels
  (e.g. "City"); only visible fields may be used (`OracleUI.field()`).
- Geography: City and Postal Code lists are narrowed by the state, so fill state
  first. "CA" matches CA and CALIFORNIA, so Oracle opens a choice dialog. Dialogs can
  stack; close the newest first. City is stored in capitals (CUPERTINO).
- ADF checkboxes: clicking the input is intercepted by the drawn box; click its label
  (`OracleUI.set_check()`).
- Trading Partner Identifier accepts numbers only (red border + "The value must be a
  number"), seen 2026-10-20 with "ZZTP1".
- Save errors come as a message dialog (id ends `::msgDlg`) listing each field.
- A new purpose row is inserted at the top of the table; the script finds the row
  whose Purpose is still empty.
- On the form, an earlier purpose row can show To Date 12/31/4712 while another row is
  edited; after saving the To Date is empty (checked on Edit Site, 2026-10-20).
- Manage Customers: a leading wildcard is refused ("Please provide a value that does
  not begin with a wildcard character"); the search matches the start of the name,
  so the script filters exact names itself. Names are not unique in Oracle (three
  "ABC" exist).
- Oracle's "today" on the form was 10/19/26 at 04:30 PC time (PC: 10/20) and 10/20/26
  from about 04:45 on. Defaults are read from the form, not computed.
- Session expiry: every click retry checks for the sign-in page; the script then stops
  and says to run `common/login_once.py`.

## Discovery steps

1. Find the task (done: Search Tasks; Financials > Customers > Create Customer).
2. Check Actions for Export/Import (done: disabled -> form fill route).
3. Learn the form: every field, required markers, defaults, list values (done 2026-10-20).
4. Save one by hand-driven script to learn Save and Close and where to find it again
   (done: ZZ_TEST_7602).
5. Codify in `browser_flow.py`; prove with all fields and with required only (done).
6. Person customers (done 2026-10-20). Later: Bill-to Site on purposes, more than one site/account,
   Business Unit assignments.

## Material

- `manual-notes/` - v2 test sheets `CU_TEST_10.xlsx`, `CU_TEST_valid5.xlsx`, `CU_TEST_ask.xlsx` and
  `v2_tester_notes.md` (what changed for testers, 2026-10-26).
- 2026-10-26 (v2 fix, all Enterprise Set, External, Bill to + Ship to): ZZ_TEST_CU_2589_JERSEY 130770 (Jersey,
  TENNESSEE, no postal code, purpose to-dates 2027-12-31), _01_DALLAS 130783, _02_SEATTLE 130786, _03_ABSECON
  130789, _05_JERSEY 130792, _04 PERSON 130796, _14_OK 130810 (Dallas), _11_ASKSUG 130816 (SANTA CLARA, CA),
  _12_ASKTYPE 130825 (San Jose, CA), _15_MIDWAY 130828 (Dallas). Not in Oracle (by design): _06 to _10, _13.
  Also seen (not made here, 2026-10-25 by another PC's run): Summit Ridge Logistics 130742, BlueHarbor Marine
  Supply 130745.
- 2026-10-23 (sheet test, all fields, Enterprise Set, supplier site ID 3010, 1 Infinite Loop
  Suite 5 CUPERTINO CA 95014, Bill to + Ship to): organizations ZZ_TEST_3727 registry IDs
  130524, 130527 and 130530 (the third is the duplicate from the rerun bug; the user asked
  for two), person ZZ_TEST_2536 Q Person Jr registry ID 130534. ZZ_TEST_8352 registry ID 130554
  (Bill-to Site picked automatically, same values).
  ZZ_TEST_6619 registry ID 130584 (sheet with Customer Name, same values).
  ZZ_TEST_6842 130588, ZZ_TEST_5862 130591, ZZ_TEST_7163 130596 (the 3-customer sheet; 1 / 2 / 3 Infinite Loop
  Suite 5 CUPERTINO CA 95014, supplier site IDs 3001 / 3008 / 3010).
- 2026-10-23 (Primary / Bill-to Site): ZZ_TEST_2827 (Bill to Primary), ZZ_TEST_2743 (Bill to
  + Ship to with Bill-to Site; its first verification read wrongly, re-verified OK),
  ZZ_TEST_1519 (Bill to Primary + Ship to with Bill-to Site), all Enterprise Set, 1 Main
  Street CUPERTINO CA 95014.
- Test customers in this TEST pod (the scripts never delete): ZZ_TEST_7602 (learning
  save: ENTERPRISE, 100 ZZ Test Street, CUPERTINO CA 95014, supplier site ID 12345,
  Bill to), ZZ_TEST_8757 (all fields, browser_flow.py), ZZ_TEST_6050 (required only,
  CUSTOMER_RDS, supplier site ID 1002, browser_flow.py), persons ZZ_TEST_4055 and
  ZZ_TEST_9231 Q Tester Jr., and ZZ_TEST_5715 (Enterprise Set, supplier site ID 3001, the
  first customer on the Redwood Set Up page), all 2026-10-20. ZZ_TEST_4418 (Enterprise
  Set, supplier site ID 3010, External, 1 Main Street CUPERTINO CA 95014, Bill to + Ship
  to from 2026-11-01, registry ID 130359; the first page `--run`, 2026-10-21).
