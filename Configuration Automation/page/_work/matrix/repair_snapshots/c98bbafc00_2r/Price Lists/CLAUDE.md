# Price Lists

Task: Manage Price Lists (Pricing). REST resource `priceLists`
(`/fscmRestApi/resources/11.13.18.05/priceLists`), same `.env` login and ORACLE_ENV
rules as everything else.
Status summary: REST route PROVEN for creating a price list header, attaching
access set(s) and approving it (by hand in Postman, then by `run.py` on 2026-10-19).
Items/lines are out of scope for now.

"DONE" means all four: header created, at least one access set attached, status
APPROVED, and the re-read verification passed. Report success only then.

## Scope A: every header field, --plan and --run-batch (2026-10-26, PROVEN, `pl_batch.py`)

Scope (the user's decision): the Create Price List screen's fields only - Name*, Item Description,
Type, Currency*, Business Unit*, Start Date*, End Date, the line defaults Pricing Charge Definition,
Line Type and Calculation Method - plus access sets (one or more) and the approval. **Never** items,
charges, tiers, matrices, rate plans, component / covered items, flexfields or Returns price lists.
Field by field, with Oracle's messages: `sheet_fields.md`.

```
python "Price Lists/run.py" --plan '[{"name": "X", "currency": "USD", "business_unit": "ABD", ...}]'   # read-only
python "Price Lists/run.py" --run-batch '[{...}, {...}]'
python "Price Lists/run.py" --time-zone        # read the Oracle user's time zone from the screen again
```
`--run` (page, one price list), `--check` and the plain command line use the same engine.

**Dates and the time zone (the old "local midnight +05:00" was wrong).** Oracle stores a price
list's dates in UTC; the screen shows them in the Oracle USER's time zone (Settings and Actions >
Set Preferences > Regional: "(UTC-05:00) New York - Eastern Time (ET)" for Configuration.TEST,
date format M/d/yy, time format h:mm a, read 2026-10-26). So ZZ_TEST_4832 (sent as +05:00
midnight) shows 10/17/26 3:00 PM. Now a plain date (YYYY-MM-DD, or "today" = today in the user's
zone) is sent as 12:00 AM of that date in the user's zone, daylight saving included (America/
New_York: -04:00 until 1 November 2026, -05:00 after). PROVEN on the screen's Manage Price Lists
table: 10/27/26 12:00 AM, 12/31/27 12:00 AM, and across the change 11/2/26 12:00 AM - 3/15/27
12:00 AM. The zone is read from the screen (read-only, about 40 s) and kept in
`oracle_time_zone.json` for a week; no REST resource shows it (scim Users, userAccounts: no time
zone; userPreferences: 404). If it can't be read and nothing is saved, nothing is sent ("Dates
can't be stored correctly ...").

**Business unit = the user's pricing access list.** The Create screen's Business Unit list is
exactly the business units where the user has an active **Pricing Administrator** data access row
(dataSecurities, SecurityContext Business unit, ORA_QP_PRICING_ADMINISTRATOR_JOB): 43 on
2026-10-26 (the screen showed 42 names: the 43rd, "ZZ_TEST_BU_3138_CAPS ", differs only by a
trailing space); Order Manager access alone (e.g. "tyty") doesn't put it there. The folder checks
that list (all access rows read once, a few seconds), plus active (the screen also lists an inactive
one; the folder refuses it). Not in the list: "Configuration.TEST has no Pricing Administrator
access on the business unit 'X' ..." with the closest names that are. The page's drop-down is that
list too. `business_unit_pending: true` (a business unit made earlier in the same upload): the plan
says "waits for the business unit"; at create the list is read again every 15 s for up to 5
minutes; not there -> "Oracle doesn't show the business unit X for pricing yet (waited ...), so the
price list wasn't made." (offline-proven with a made-up name and a 30 s limit). Real timing:
ZZ_TEST_BU_8034_PL made by the Business Units folder at 05:22:37 was in the list at once; the
price list ZZ_TEST_PL_8034_NEWBU on it was made 13 s later, first try.

Per price list (one after another; nothing sent unless all its checks pass): POST header ->
POST each access set -> PATCH APPROVED -> read back (header, every line default, dates as
moments, access sets, status). Results: "Created ... Saved and verified in Oracle, every value as
sent" / skipped (exists, never changed) / "Oracle didn't save the price list X: <Oracle's words>"
with a structured problem (price_list, business_unit, field, value, reason, suggestions) /
"Saved but incomplete: ... missing ... A rerun completes only what is missing." A **half-made**
price list (same header, In progress) is completed by a rerun: only its missing access sets and
the approval (PROVEN: ZZ_TEST_PL_8034_HALF, same PriceListId; the next rerun skipped it). An
approved one is never changed (missing access sets are not added; said plainly); an In progress
one with other values is left alone.

**In the upload sheet (2026-10-26):** tabs Price Lists and Price List Access Sets, registry group
"Price Lists" (`--plan` for the preview, `--run-batch` for Create, `depends_on` Business Units,
`ask_on_refusal`), see root CLAUDE.md > Price Lists module. `--plan` also returns `found` (yellow:
already there / half-made / a capitals-only twin, "Oracle treats price list names as case-sensitive,
so it would make this one as a NEW price list") and `oracle` (what Oracle will get per field, dates as
the screen shows them). Test workbooks: `manual-notes/Price_Lists_TEST_good.xlsx` (ZZ_SHEET_PL_8003_*,
business unit ZZ_SHEET_BU_8970 on the same sheet) and `..._bad.xlsx`; previews only, nothing created.

### What Oracle does (deliberate tests, 2026-10-26, test number 8034)

| Case | Oracle's answer | Rule |
|---|---|---|
| End Date before Start Date (one bad row of three) | "You must enter a start date that's on or before the end date."; only that one not saved, the other two saved (B1, B3) | End Date on or after Start Date |
| Same name, same business unit | "A price list with the name ZZ_TEST_PL_8034_ALL already exists. (QP-2715100)" | names are unique in all of Oracle |
| Same name, another business unit (US1) | the same message (QP-2715100) | **global, not per business unit** |
| Same name in other capitals | **accepted** (zz_test_pl_8034_all, left In progress) | capitals count; the plan notes a capitals-only twin |
| Name of 81 characters | "Value ... for field PriceListName exceeds the maximum length allowed." | max 80 (80 accepted) |
| Description of 1001 characters | "Value ... for field PriceListDescription exceeds the maximum length allowed." | max 1000 (1000 accepted) |
| Approval without an access set | "StatusCode: You cannot approve this price list because it is not associated with an access set. (QP-2715317)" | at least one access set; added before the approval |
| Each Type (Segment, Floor, GSA, Ceiling), each Calculation Method (Price, Cost, Covered item price percent, Source document cost), both Charge Definitions (Sale Price, Recurring Sale Price), Line Type Buy | all accepted, in the combinations tried (Floor+Cost+Sale Price, Segment+Price+Recurring, GSA+Covered, Ceiling+Source document cost, Floor+Cost+Recurring) | none refused |

Speed: about 6-11 s per price list (16 s for one with two access sets incl. the checks, 17 s for 3).

## Input rules

Check every request against this before doing any work (root CLAUDE.md > Input rules).

REQUIRED - if missing or unclear, stop and ask in plain words, all missing items in one message:
- Price list name. It must not already exist (existing ones are skipped, never changed).
- Business unit, by NAME (e.g. "ABD").
- Currency, by code or name (e.g. "USD" or "US Dollar").
- Start date (a plain date; see time zone below).
- At least one access set, by name or code (e.g. "001 Customer Site").
Never ask for IDs or codes; `run.py` resolves names with read-only lookups (below).
If a name can't be resolved, stop and tell the user in plain words.

OPTIONAL - if missing, use the Oracle UI default:

| Field | UI default | Supported by run.py |
|---|---|---|
| Description | empty | yes (max 1000, PROVEN) |
| End date | empty (no end) | yes (PROVEN 2026-10-26) |
| Type | Segment (`SEGMENT`) | yes: Segment, Floor, GSA, Ceiling (PROVEN 2026-10-26) |
| Line type | Buy (`ORA_BUY`) | yes: Buy (PROVEN) |
| Calculation method | Price (`PRICE`) | yes: Price, Cost, Covered item price percent, Source document cost (PROVEN) |
| Pricing charge definition | empty | yes: Sale Price, Recurring Sale Price (PROVEN) |

Values by code or name, from Oracle's lookups ORA_QP_PRICE_LIST_TYPES (without RETURN),
ORA_QP_ORDER_LINE_TYPES, ORA_QP_PRCLT_CALC_METHODS (without the pricing matrix) and
chargeDefinitionsLOV (see "Scope A" above).

Time zone (2026-10-26, replaces the old rule): a plain date is sent as 12:00 AM of that date in
the Oracle USER's time zone (see "Scope A" above). Before 2026-10-26 it was sent as midnight
+05:00, which the screen shows as 3:00 PM the day before (ZZ_TEST_4832 and the other older
price lists keep those dates; they are never changed).

Relative dates ("3 days before today", "today"): Oracle's today is the date of a REST
response from Oracle (`Date` header, `oracle.server_date()`), never the PC clock; the
date is worked out before writing `start_date` (2026-10-21: Oracle 2026-10-21, so "3
days before today" = 2026-10-18). "today" alone = today in the Oracle user's time zone (since 2026-10-26; before: Oracle's today
minus one day).

## Route status

- **REST route (priceLists): PROVEN** (2026-10-19). Create -> access set -> approve
  -> verify. Tested with ZZ_POC_PRICELIST3 (PriceListId 300000393684129).
- **Upsert action** on the collection: UNTESTED. Do not use.
- **CSV route / package route**: not evaluated (not needed; REST works).

## How to do it

From the project root:

```
python "Price Lists/run.py" --check   # validate, resolve names, check existence; no changes
                                      # (names are resolved only for price lists that do not exist yet)
python "Price Lists/run.py"           # full run: create, access sets, approve, verify
```
(Page commands `--spec`, `--options`, `--run`: see Page interface.)

Requirements file `Price Lists/pricelists.json`:

```json
{"price_lists": [{
  "name": "My Price List",            // required
  "business_unit": "ABD",             // required, name
  "currency": "USD",                  // required, code or name
  "start_date": "2026-10-19",         // required, YYYY-MM-DD (local midnight)
  "access_sets": ["001 Customer Site"],  // required, at least one, name or code
  "description": "...",               // optional
  "end_date": "2027-12-31"            // optional, YYYY-MM-DD
}]}
```

(Comments are documentation only; the real file is plain JSON.)

What `run.py` does, per price list:
1. Prints host and ORACLE_ENV; validates the JSON.
2. Skips it if `GET priceLists?q=PriceListName='<name>'` finds one (never modifies it).
3. Resolves names (read-only):
   - Business unit: `GET finBusinessUnitsLOV?finder=KeywordFinder;SearchTerm=<name>`,
     then keeps only the exact (case-insensitive), active match.
   - Currency: `GET currenciesLOV?finder=CurrencyCodeAllRowsFinder;CurrencyCode=<code>`
     or `q=Name='<name>'`; must be enabled.
   - Access set: `GET setIdSetsLOV?finder=SetCodeFinder;SetCode=<CODE>`, else
     `q=SetName='<name>'` (price list access sets are reference data sets).
4. `POST priceLists` with `{"PriceListName", "BusinessUnit" (name), "CurrencyCode",
   "StartDate"}` (+ description / end date if given). Oracle defaults: Type SEGMENT,
   LineType ORA_BUY, CalculationMethod PRICE, Status IN_PROGRESS.
5. `POST priceLists/{PriceListId}/child/accessSets` `{"AccessSetCode": "<CODE>"}` per set.
6. `PATCH priceLists/{PriceListId}` `{"StatusCode": "APPROVED"}`.
7. Re-reads `GET priceLists?q=PriceListName='<name>'&expand=accessSets` and checks
   status APPROVED, business unit id, currency, start date (same instant), optional
   fields, and every access set code.
8. Deletes `_work/` (request/response log) only if everything passed.

## Page interface

Contract: root CLAUDE.md > Page interface (helper `common/page.py`). **PROVEN 2026-10-21.**
One price list per `--run`; `pricelists.json` and the normal commands are unchanged.

```
python "Price Lists/run.py" --spec
python "Price Lists/run.py" --options business_unit
python "Price Lists/run.py" --options currency
python "Price Lists/run.py" --options access_sets.name
python "Price Lists/run.py" --run '{"name": "X", "business_unit": "ABD", "currency": "USD", "start_date": "today", "access_sets": [{"name": "001 Customer Site"}]}'
```

| Key | Label | Required | Type | Placeholder | Default |
|---|---|---|---|---|---|
| name | Price list name | yes | text | Retail USD 2027 | - |
| business_unit | Business unit | yes | pick | ABD | - |
| currency | Currency | yes | pick | USD | - |
| start_date | Start date | yes | date | 2026-10-21 | - ("today" = Oracle's today minus one day) |
| access_sets | Access sets | yes | rows (at least 1) | - | - |
| description | Description | no | text | Prices for retail customers | empty |
| end_date | End date | no | date | 2027-12-31 | empty (no end) |

Rows field `access_sets`: row label "Access set", button "Add an access set", at least
1 row; one sub-field `name` (Access set, required, pick, 001 Customer Site).

**Drop-down samples (2026-10-21).** The page's business unit, currency and access set
drop-downs show only verified values, so a user can't pick a value Oracle refuses for a
price list. **A value counts as verified once a real create in this project or the user's
own test has used it** (a price list created with it, given an access set and approved);
only then does it join the samples. They are in `SAMPLES` in `run.py`, in Oracle's exact
spelling:
- business unit: **ABD** (ZZ_POC_PRICELIST3, ZZ_TEST_4832, ZZ_TEST_1567, ZZ_TEST_6183),
  **US1** and **ABC Procurement BU** (the user's own test, 2026-10-21; Oracle spells
  "US1" with no space);
- currency: **USD (US Dollar)** (the creates above), **PKR (Pakistan Rupee)** and **AFN
  (Afghani)** (the user's own tests; Oracle's names are "Pakistan Rupee" and "Afghani");
- access set: **001 CUSTOMER SITE** (the creates above), **ENTERPRISE (Enterprise Set)**
  and **SET0001** (Oracle's name "GoSaaS Labs Data Set") (the user's own tests).

| Value | Verified by |
|---|---|
| business unit ABD, currency USD, access set 001 CUSTOMER SITE | real creates in this project |
| business unit US1, business unit ABC Procurement BU, currency PKR | the user's own test, 2026-10-21 |
| currency AFN, access set ENTERPRISE, access set SET0001 | the user's own test, 2026-10-21 |

All were confirmed in Oracle's live lists on 2026-10-21. Each sample is confirmed live
whenever the list is read; one Oracle no longer has is left out with a NOTE.

**Plus created business units (2026-10-21).** The business unit drop-down also shows every
name in `common/created_business_units.json` (the business units the Business Units folder
created and verified with Order Manager and Pricing Administrator access), read from that
file each time the list loads; nothing is imported from that folder. Each name is
confirmed in Oracle's live list; one that isn't there is left out with a NOTE (tried with
a made-up name on a temporary copy). These extra names come from created business units,
not from the samples above. Proven 2026-10-21: price list **ZZ_TEST_8202** on
**ZZ_TEST_8131** (the newest created business unit), USD, start 2026-10-20 (Oracle's today
minus one day), access set 001 CUSTOMER SITE: accepted at the first try (no refusal),
approved, every value read back (PriceListId 300000393936112), and ZZ_TEST_8131 marked
`pricing_confirmed` in the shared file (written atomically). 8 seconds.
The `--spec` fields carry `"list": "samples"`: the page shows the samples but still
accepts a typed value, and `--run` checks anything typed against the **full live list**
(a value Oracle doesn't have stops with NOT_IN_ORACLE; tried 2026-10-21 with "Mars BU").
The full live lists stay in the code behind a switch, to turn on later:

```
python "Price Lists/run.py" --options business_unit --all   # 126 business units (2026-10-21)
python "Price Lists/run.py" --options currency --all        # 268 currencies
python "Price Lists/run.py" --options access_sets.name --all   # 37 access sets
```

Pick lists, read live through REST (all pages, 200 per page):
- `business_unit`: `finBusinessUnitsLOV` (no filter, about 1 s), active ones; value =
  label = BusinessUnitName. 123 on 2026-10-21 (126 later the same day). Drop-down: the samples.
- `currency`: `currenciesLOV?q=EnabledFlag='Y'`; value = CurrencyCode, label = Name, so
  "USD" and "US Dollar" both match. 268 on 2026-10-21. Drop-down: the samples.
- `access_sets.name`: `setIdSetsLOV`; value = SetCode, label = SetName. 37 on 2026-10-21
  (full list, no samples).
Type / line type / calculation method stay off the form (not supported yet, see Input rules).
Extra plain checks in `run_request`: no single quote in the name or description, end date
not before start date, an access set listed twice (row-numbered). Then a read-only
`GET priceLists?q=PriceListName=...`: an existing price list -> `skipped` result with its
status and access sets. "today" uses the `Date` header of that GET.
Steps: reading 5, checking 20, creating 50 (header + access sets), `approving` 70
("Approving it"), verifying 85 (the re-read), done 100. Result `created` = the price list
as re-read (id, business unit id, currency, start date in UTC, status, access sets).
Result "where": Order Management > Pricing Administration > Manage Price Lists, search
for the name (navigation not checked on screen).
Tried 2026-10-21: `--spec` OK; all three `--options` OK; `--options name` ->
NOT_A_LIST_FIELD; no access set -> "Please add at least 1 access set (Add an access
set)."; currency "Martian Dollar" and access set 2 "Nope" -> NOT_IN_ORACLE, both in one
message with the valid lists; a name with ' -> stopped; ZZ_TEST_4832 -> skipped. Full
`--run` ZZ_TEST_1567 (ABD, USD, start "today" -> 2026-10-20 local midnight +05:00 =
2026-10-19T19:00Z, 001 CUSTOMER SITE, description "Page interface test"): all progress
lines, PriceListId 300000393775950, APPROVED, re-read matched every value. 8 seconds.
Seen the same day: one `--options` attempt failed because the PC could not resolve the
Oracle host name for a moment (network); the same commands worked a minute later.

## Preview versus Create (2026-10-26)

- **Currency code longer than 3 characters:** currency 1214 is enabled in Oracle's currency list, but a
  create refused it on 2026-10-21 ("Value 1214 for field CurrencyCode exceeds the maximum length allowed.");
  `priceLists/describe` gives CurrencyCode precision 3. `--plan` now refuses such a currency in red with
  three-letter suggestions (`CURRENCY_MAX`).
- The 2026-10-21 refusal "The value of the attribute BusinessUnit isn't valid." (business unit Ascend Money)
  is Oracle's message for a business unit outside the user's pricing access; already checked (folder rule).
- A refusal about Item Description or Line Type now names that field (`field_of()`), so the decision panel
  can ask about it.

**Still only at Create:** name characters beyond those tried; access sets other than the five proven (the
access set list exists only after the header is saved); Type x Calculation Method x Charge Definition
combinations other than the five proven. Refusals after the header is saved (access set, approval) are
"saved", so they are never asked (a rerun finishes them).

## Related folders

- **Business Units** (agreed by the user 2026-10-21): reads `common/created_business_units.json`,
  which that folder writes, and marks a business unit `pricing_confirmed` after the first
  price list with it (see "New business units" below). No code is shared between the folders.

## New business units from the Business Units folder (2026-10-21)

Oracle caches a user's data access, so a business unit just created (and given access) by
the Business Units folder may be refused for a price list until the user signs out and in
again. That folder lists what it created in `common/created_business_units.json`
(`status` ready / pending, `pricing_confirmed`). For a business unit in that file that no
price list has used yet, the header POST (`create_header()`) is retried when Oracle's
refusal names the business unit: 3 more tries, 40 s apart (the price list is checked not
to exist before each retry, so nothing is made twice). Still refused -> the run stops with
"Oracle needs a fresh sign-in before this business unit shows for pricing. Sign out of
Oracle and sign in again, then create the price list for <business unit> again. Nothing
was created." On the page this is a plain stop on the business unit field (code
INVALID_REQUEST), **not a failure of this folder** (no automatic repair). Any other error
stops as before. The first price list made with such a business unit marks it
`pricing_confirmed` / ready in the file. Business units not in the file (e.g. ABD) use
the normal call. Tried 2026-10-21 offline with pretend answers (nothing sent to Oracle):
always refused -> 4 tries then the plain stop; refused twice then accepted -> created
and marked ready.

## Known gotchas

- 2026-10-26: **Lost clicks: the time zone read checked and done again** with the shared retry helper
  `ui.retry()` (`common/browser.py`): Settings and Actions, Set Preferences, Regional, until a Time Zone shows;
  `user_zone()` treats an unread label as "couldn't be read" (the saved answer if there is one), never as a zone.
  `--plan` passes the real failed step to the page. Price lists themselves are made by REST (never retried here).
- A price list CANNOT be approved without at least one access set (UI error
  "access list required"). Lines/items are NOT required for approval.
- There is no approve action in `describe`; `PATCH StatusCode=APPROVED` is what works.
- `describe` shows a `delete` item action: never use it. Never delete or overwrite.
- If a run fails after the create step, the price list stays as created (e.g.
  IN_PROGRESS without access set). Since 2026-10-26 a rerun with the same header COMPLETES it
  (missing access sets, then the approval); one with other values is left alone and named.
- `finBusinessUnitsLOV` with a plain `q=BusinessUnitName='...'` timed out after 300s
  (2026-10-19). Use `KeywordFinder` (about 2s); it is fuzzy, so filter exact names.
- `currenciesLOV` once returned a connection reset; a single retry worked
  (transient network issue, 2026-10-19).
- Names containing a single quote are refused by run.py (they would break `q=` filters).
- StartDate comes back in UTC (`+00:00`); compare as instants, not strings.

## Discovery steps

1. Decide the route: here the REST resource was proven by hand (Postman), so the
   CSV ExportSupportedFlag check was skipped. (done)
2. Prove one record by hand: ZZ_POC_PRICELIST1 and ZZ_POC_PRICELIST2 (Postman, by user). (done)
3. Read `priceLists/describe` (attributes, child accessSets, actions). (done 2026-10-19)
4. Script it, test with a dummy, verify by re-read: ZZ_POC_PRICELIST3. (done 2026-10-19)
5. Open: items/lines, non-default type / line type / calculation method, upsert,
   end date behaviour. Record findings here.

## Material

- `manual-notes/postman-steps.md` - the user's proven manual steps.
- 2026-10-26 (scope A proofs, all read back by REST, dates also on the screen): ZZ_TEST_PL_8034_ALL
  (Floor, Cost, Sale Price, USD, ABD, 10/27/26-12/31/27, 001 CUSTOMER SITE + ENTERPRISE, description),
  _SEG (Segment, Price, Recurring Sale Price, PKR, US1), _GSA (GSA, Covered item price percent, AFN,
  ABC Procurement BU, 11/2/26-3/15/27, COMMON), _CEIL (Ceiling, Source document cost, EUR, ABD,
  SET0001), _B1 and _B3 (the good rows next to the bad one), _N80_XXX... (80-character name, 1000-
  character description), _HALF (made header-only, approval refused, completed by a rerun), _NEWBU
  (on the new business unit ZZ_TEST_BU_8034_PL), _RUN (page --run: Floor, Cost, Recurring Sale Price,
  10/28/26-12/31/26, 001 CUSTOMER SITE + SET0001), all approved; and **zz_test_pl_8034_all** (the
  capitals-only duplicate Oracle accepted; header only, In progress, no access set). Not made:
  _B2BAD, the 81-character name, _D1001, _NEVER, the two exact duplicates. Business unit
  ZZ_TEST_BU_8034_PL (Business Units folder, defaults).
- No package-route folder: not applicable to this REST route.
- Test price lists in this TEST pod (cannot be deleted by the scripts):
  ZZ_POC_PRICELIST1/2 (by hand), ZZ_POC_PRICELIST3 (run.py), ZZ_TEST_4832 (ABD, USD,
  start 2026-10-18, 001 CUSTOMER SITE, approved; run.py 2026-10-21, 8 seconds),
  ZZ_TEST_1567 (ABD, USD, start 2026-10-20, 001 CUSTOMER SITE, approved; the first page
  `--run`, 2026-10-21, 8 seconds).
