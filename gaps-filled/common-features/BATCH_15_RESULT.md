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

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records (ProcessId) |
|---|---|---|---:|---:|---|---|
| 1 | Manage Associated Business Entities | tested | 7 + 12 | 6 | PASS, re-test R PASS | LE1 → BU3 (100004743433629; refused 100004743430787, 100004743434305); LE2F → BU4F (100004743435423); LE3R → BU5R (100004743432818) |
| 2 | Manage Application Tax Options | **failed** | 6 + 10 | 7 | FAIL | BU1 / AP (100004744413261; second send refused 100004743431825); fresh BU2F refused (100004743432577); probe with unknown name refused (100004744415341) |
| 3 | Manage Set Assignments for Set Determinant Type | tested | 5 + 8 | 5 | PASS, re-test R PASS | set SET1 (100004743432297) + SET row (100004744413542); SET2F (100004744414204, 100004744415045); SET3R (100004743432588, 100004744415284) |
| 4 | Manage Segment Value Security Rules | tested | 5 + 5 | 3 | PASS, re-test R PASS | SVS1 + T1 (100004744413699); SVS2F (100004743432393); SVS3R (100004743435641) |
| 5 | Manage Chart of Accounts Configurations | tested | 5 + 4 | 3 | PASS, re-test R PASS | policy SVP1 (100004743433661); SVP2F (100004744415062); SVP3R (100004744414677) |
| | **Total** | **4 tested, 1 failed** | **67** | **24** | 4 of 5 (+4 re-tests) | |

Prerequisite (not a task, not counted): test business units `GAPFILL_AB_B15_BU1`, `BU3`, `BU2F`, `BU4F`, `BU5R` (skill test-business-unit; fresh tests PASS).

## Problems and findings
1. **Application tax options: failed.** The import accepts the first AP row (1 processed, 0 failed), but the task export never shows these rows and there is no REST resource. I took the refusal of a second send (`ZX_APPL_OU_UNIQUE`) as proof. The fresh tester's brand-new business unit was refused the same way, and a probe with a business unit name that does not exist was refused too: Oracle does not use `Name` to find the business unit. So the first load most likely stored one AP row whose business unit Oracle did not resolve. **AB to check:** open Manage Application Tax Options on the page for application AP; if a row without a business unit (or for `GAPFILL_AB_B15_BU1`) shows, note it, and remove it there if it should not stay. Next try: find the column that ties the row to a business unit (`EnterpriseId`, `EventClassCode`, `EntityCode` are in the file too).
2. **Associations** need a business unit with a location, `BusinessEntityLocation` = location name and `BusinessEntityAddress` = exactly three spaces (the builder trims spaces, so it is set after the build). Without them: `XLE_ASSOC_OBJECT_ID_REQUIRED`.
3. **Set assignments:** this task's package handles determinant type `SET` only (`BU` gives JBO-27014). Test with an own reference data set as determinant.
4. **Segment value security:** the value set task makes a new secured General Ledger value set (GL `ModuleId` read live); the chart of accounts task adds a policy on it. Neither touches a value set used by a chart of accounts; options and the global usage row are never sent.
5. Network drops: one business unit import before its ProcessId (not repeated; proved absent by exports, then a new BU), two status polls after the ProcessId (result fetched by ProcessId or read back), three exports (run again into new folders).

## What is left
See `MODULE_RESULT.md`.
