# Batch 14 result: Common Features (AB), test legal entity chain: tax profiles, owner tax options, financial information

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (sixth Common Features sitting). One test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file edited. Work folder outside the repo. No existing record was edited or deleted: every change was on a NEW test legal entity made for the test (prefix `GAPFILL_AB_`), its main reporting unit and its own tax profiles.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 01:12 | 01:12 | 0 | Sign-in (renewed 01:48 and 02:16) |
| 01:13 | 01:16 | 3 | 5 read-only exports in parallel (waiting) |
| 01:16 | 01:28 | 12 | Test legal entity chain: package studied, 2 tries (address needs `OrigSystemReference`), `GAPFILL_AB_B14_LE1` created; skill test-legal-entity |
| 01:28 | 01:45 | 17 | 5 own tests (helpers own_row_package.py, compare_own_update.py); LE financial info needs its own task export and a NAICS code |
| 01:45 | 01:58 | 13 | 5 skills written / rewritten |
| 01:58 | 02:12 | 14 | Fresh tests F on a fresh test legal entity `GAPFILL_AB_B14_LE2F` (5 in parallel + prerequisite), wording fixes (waiting most of it) |
| 02:12 | 02:40 | 28 | Prerequisite re-test (`GAPFILL_AB_B14_LE3R`), then 5 re-tests R in 3 parallel agents (waiting most of it) |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records (ProcessId) |
|---|---|---|---:|---:|---|---|
| 1 | Manage Legal Entity Tax Profiles | tested (was written, unsafe) | 5 + 6 | 4 | PASS, re-test R PASS | LE1 profile (100004743430357); LE2F (100004744413207); LE3R (100004743435628) |
| 2 | Manage Legal Reporting Unit Tax Profiles | tested (was written, unsafe) | 5 + 5 | 4 | PASS, re-test R PASS | LE1 unit (100004744411602); LE2F (100004743432165); LE3R (100004744416787) |
| 3 | Manage Configuration Owner Tax Options | tested (was written, unsafe) | 5 + 5 | 3 | PASS, re-test R PASS | LE1 AP row (100004743430482); LE2F (100004743430917); LE3R (100004744416273) |
| 4 | Manage Legal Entity Financial Information | tested | 6 + 7 | 5 | PASS, re-test R PASS | LE1 ActivityCode 541511 (100004743429645; refused 100004743429588); LE2F (100004744413318); LE3R (100004744415193) |
| 5 | Manage Legal Reporting Unit Financial Information | tested | 5 + 5 | 4 | PASS, re-test R PASS | LE1 unit (100004743429712); LE2F (100004743432273); LE3R (100004744414665) |
| | **Total** | **5 tested** | **54** | **20** | 5 of 5 (+5 re-tests) | |

Prerequisite (not a task, not counted): test legal entities `GAPFILL_AB_B14_LE1` (100004743430091), `LE2F` (100004744412079, fresh PASS), `LE3R` (100004743433839, re-test PASS).

## Problems and findings
1. **A new test legal entity makes 3 "unsafe" tasks safe:** Oracle creates its main reporting unit, its legal entity tax profile and its reporting unit tax profile with it. Updating only those rows changes no real entity. The legal entity package needs 5 files; the address row needs `OrigSystemReference` (JBO-27014 without it).
2. **Updating one own row:** new helper `scripts/own_row_package.py` (refuses any row that does not start with the prefix, can copy an unchanged parent row) and `scripts/compare_own_update.py` (PASS only if no other row changed).
3. **Financial information** packages must be built from the same task's export (a Manage Legal Entity package gives HTTP 400). `ActivityCode` must be a NAICS 1997 code. The reporting unit row needs its parent legal entity row unchanged in the package, copied from a fresh export.
4. Testers' wording notes fixed: safe log grep (the process log holds the environment name and user), quoted paths, retry folder names, export times (up to 5 minutes), "In progress" lines are normal.
5. Two exports dropped on network errors; each was run again into a new folder. No import was sent twice.

## What is left
See `MODULE_RESULT.md`.
