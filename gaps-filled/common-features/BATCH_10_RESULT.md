# Batch 10 result: Common Features (AB), billing extensions, worker users, data access for users

GoSaaS work, not official FSCR. AB with Claude, 2026-11-25 (third Common Features sitting, after batch 09). Tested on one test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file was edited. Work folder outside the repo. Record names `GAPFILL_AB_B10_<name>`. No existing record was edited or deleted.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 15:43 | 15:46 | 3 | 2 read-only exports in parallel (waiting); REST describes of userAccounts and dataSecurities |
| 15:46 | 15:51 | 5 | Billing extension tries 1 and 2 (lookup codes read live), export compare |
| 15:51 | 15:55 | 4 | Billing extension skill; fresh test started (waiting) |
| 15:52 | 15:57 | 5 | Skills for implementation/worker users and the 3 data access tasks; context filters verified |
| 15:58 | 16:10 | 12 | Cards, evidence, tracker, reports (shared with batch 09) |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records / ProcessIds |
|---|---|---|---:|---:|---|---|
| 1 | Manage Billing Extensions (`PJB_MANAGE_BILLING_EXTENSIONS`) | tested (try 2) | 5 + 5 | 4 | PASS | `GAPFILL_AB_B10_BX1` (refused PJB_BILL_EXT_PROC_INVALID, 100004743405841); `BX2` (100004743406265); fresh `BX3F` (100004744392322) |
| 2 | Import Worker Users (`HRC_IMPORT_WORKER_USERS`) | written (unsafe to test) | 3 + 0 | 0 | not run | none |
| 3 | Manage Data Access for Users (`ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS`) | written (unsafe to test) | 5 + 0 | 2 | not run | none |
| 4 | Manage Business Unit Data Access for Users (`ORA_FUN_MANAGE_BUSINESS_UNIT_DATA_ACCESS_FOR_USERS`) | written (unsafe to test) | 2 + 0 | 1 | not run | none |
| 5 | Manage Reference Data Set Data Access for Users (`ORA_FUN_MANAGE_REFERENCE_DATA_SET_DATA_ACCESS_FOR_USERS`) | written (unsafe to test) | 1 + 0 | 1 | not run | none |
| | **Total** | **1 tested, 4 written** | **21** | **8** | 1 of 1 | |

## Why 4 tasks are "written", not tested
- **Import Worker Users:** a load creates HR person records and sign-in accounts on the shared environment; role auto-provisioning may give them roles.
- **The 3 data access tasks:** each row gives a real user access to real company data (business unit, ledger, set...). The only user we could use is our own sign-in user, and giving ourselves more access is a security change the security owner did not approve.
Read steps VERIFIED (export with 4 files and 516 access rows; `dataSecurities` reads, describe and context filters); grant steps GUESS. Evidence 01 to 03 only.

## Problems and findings
1. **Billing extension `CallingProcess` takes the lookup code** (`I` / `R` from `PJB_BILL_EXT_CALL_PROCESS`), not the meaning: try 1 with `INVOICE` failed with `PJB_BILL_EXT_PROC_INVALID`, nothing created (not in the after-export).
2. Oracle does not check that the billing extension's procedure exists when the definition is saved. A new, unassigned definition changes nothing.
3. **REST `billingExtensions`: 404**; the export compare is the read-back.
4. The two billing extension assignment tasks (invoice and revenue methods) now have test extensions to use (`BX2` = Invoice, `BX3F` = Revenue). An assignment changes an existing method, so the next sitting must first check whether a test method can be made (noted in `my_gaps.csv`).
5. `dataSecurities` full rows hold user names; every read in this batch passed `fields=` without them.

## What is left
Sitting limit reached (10 tasks: 4 tested, 6 written, 0 failed; plus 4 screen-only). 72 Common Features gaps open. Next candidates: billing extension assignments (check test methods), segment value security rules and data role tasks (likely unsafe), descriptive flexfields (deploy), country-only tasks (Italy, China, Brazil, EMEA), the remaining "neither" tasks (languages, territories, time zones as read-only skills; the rest one by one).
