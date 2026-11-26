# Batch 15 result: Common Features (AB), business entities, application tax options, set assignments, segment value security

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (sixth Common Features sitting, second batch). One test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file edited. Work folder outside the repo. No existing record was edited or deleted: every record is new and has the prefix `GAPFILL_AB_` (test business units, a reference data set, value sets, policies), or is a link between test records.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 01:40 | 01:44 | 4 | 6 read-only exports in parallel (waiting); REST lookups for entity types, determinant types, AP defaulting codes |
| 01:44 | 01:58 | 14 | Test business units `GAPFILL_AB_B15_BU1` (no location) and `BU3` (with location); one import timed out before its ProcessId (not repeated, proved by 2 exports) |
| 01:58 | 02:08 | 10 | Association (3 tries), application tax options (2 sends), set assignments (2 refused BU tries, own set, SET row) |
| 02:05 | 02:12 | 7 | Secured value set and policy (role read by SCIM) |
| 02:12 | 02:16 | 4 | 5 skills + test-business-unit written |
| 02:16 | 02:45 | 29 | Fresh tests F (5 in parallel), probe for the tax options failure, wording fixes, 4 re-tests R (waiting most of it) |
| 16:30 | 16:40 | 10 | Tax options final check (read only, no Oracle call): column list, decision screen-only, files |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records (ProcessId) |
|---|---|---|---:|---:|---|---|
| 1 | Manage Associated Business Entities | tested | 7 + 12 | 6 | PASS, re-test R PASS | LE1 → BU3 (100004743433629; refused 100004743430787, 100004743434305); LE2F → BU4F (100004743435423); LE3R → BU5R (100004743432818) |
| 2 | Manage Application Tax Options | **screen-only** (was failed) | 6 + 10 | 7 | FAIL | BU1 / AP (100004744413261; second send refused 100004743431825); fresh BU2F refused (100004743432577); probe with unknown name refused (100004744415341) |
| 3 | Manage Set Assignments for Set Determinant Type | tested | 5 + 8 | 5 | PASS, re-test R PASS | set SET1 (100004743432297) + SET row (100004744413542); SET2F (100004744414204, 100004744415045); SET3R (100004743432588, 100004744415284) |
| 4 | Manage Segment Value Security Rules | tested | 5 + 5 | 3 | PASS, re-test R PASS | SVS1 + T1 (100004744413699); SVS2F (100004743432393); SVS3R (100004743435641) |
| 5 | Manage Chart of Accounts Configurations | tested | 5 + 4 | 3 | PASS, re-test R PASS | policy SVP1 (100004743433661); SVP2F (100004744415062); SVP3R (100004744414677) |
| | **Total** | **4 tested, 1 screen-only** | **67** | **24** | 4 of 5 (+4 re-tests) | |

Prerequisite (not a task, not counted): test business units `GAPFILL_AB_B15_BU1`, `BU3`, `BU2F`, `BU4F`, `BU5R` (skill test-business-unit; fresh tests PASS).

## Problems and findings
1. **Application tax options: screen-only (was failed).** The import accepts the first AP row (1 processed, 0 failed), but the task export never shows these rows and there is no REST resource. I took the refusal of a second send (`ZX_APPL_OU_UNIQUE`) as proof. The fresh tester's brand-new business unit was refused the same way, and a probe with a business unit name that does not exist was refused too: Oracle does not use `Name` to find the business unit. So the first load most likely stored one AP row whose business unit Oracle did not resolve. **AB to check:** open Manage Application Tax Options on the page for application AP; if a row without a business unit (or for `GAPFILL_AB_B15_BU1`) shows, note it, and remove it there if it should not stay. Next try: find the column that ties the row to a business unit (`EnterpriseId`, `EventClassCode`, `EntityCode` are in the file too).
   **Read-only check (2026-11-26, asked by AB):** YES, one row is left. Oracle's error line in all 3 refused imports names the key it checked: `Row Identifier: 200, .` = application 200 (Payables) with an **empty business unit**. So the first load (ProcessId 100004744413261) made ONE Payables row with **no business unit** (values: no defaulting order, every flag N, rounding NEAREST, precision 2, record type USER_DEFINED); `GAPFILL_AB_B15_BU1` got nothing. The export (0 rows) and REST (6 resource names, all 404) cannot show it. Risk: a shared row tied to no test record; whether Oracle uses it as a default for business units without their own Payables options is not proven. Fix: **page only** (Setup and Maintenance, Manage Application Tax Options, application Payables, business unit blank, created 2026-11-25): delete it. A CSV cannot update it (Name never reaches the key; the import only creates and refuses) and CSV has no delete.
   **Final check (2026-11-26, asked by AB):** read only, no Oracle call. The package has one file, ZX_APPLICATION_TAX_OPTIONS.csv (34 columns); only Name names the business unit; no business unit ID or code, legal entity, ledger or reference data set column; EnterpriseId is the enterprise, ApplicationShortName the application, EventClassCode / EntityCode the event class; the key Oracle checks is 'Row Identifier: 200, .' = application + business unit, and the business unit part is always empty. Name was already tried 3 ways, so no other column (no ID) can carry the business unit and no live try was made. AB checked the page: the stray row is not visible (nothing at Application = Payables with business unit % or empty), so no cleanup is possible; low risk. Status **screen-only**, listed in `screen-only.csv`; skill kept as a guide only.
2. **Associations** need a business unit with a location, `BusinessEntityLocation` = location name and `BusinessEntityAddress` = exactly three spaces (the builder trims spaces, so it is set after the build). Without them: `XLE_ASSOC_OBJECT_ID_REQUIRED`.
3. **Set assignments:** this task's package handles determinant type `SET` only (`BU` gives JBO-27014). Test with an own reference data set as determinant.
4. **Segment value security:** the value set task makes a new secured General Ledger value set (GL `ModuleId` read live); the chart of accounts task adds a policy on it. Neither touches a value set used by a chart of accounts; options and the global usage row are never sent.
5. Network drops: one business unit import before its ProcessId (not repeated; proved absent by exports, then a new BU), two status polls after the ProcessId (result fetched by ProcessId or read back), three exports (run again into new folders).

## What is left
See `MODULE_RESULT.md`.
