# Batch 16 result: Common Features (AB), project process configurator, flexfields, tax authority profiles, data roles, Italy and China options

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (seventh Common Features sitting, first batch). One test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file edited. Work folder outside the repo. No existing record was edited or deleted: every new record has the prefix `GAPFILL_AB_`; the tax authority profile change is on own test legal authorities only.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 17:39 | 17:45 | 6 | Sign-in (cached); 14 read-only exports for the open tasks (waiting) |
| 17:45 | 17:52 | 7 | Italy and China exports refused (access denied); project process configurator (2 refused tries, then PASS) |
| 17:52 | 17:58 | 6 | Flexfield builder `dff_context_package.py`, attachments flexfield context; tax authority profile update |
| 17:58 | 18:02 | 4 | Data role copier `copy_data_role.py`; 6 skills written |
| 17:53 | 18:06 | 13 | Fresh tests F (4 in parallel), wording fixes, re-tests R (waiting most of it) |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records (ProcessId) |
|---|---|---|---:|---:|---|---|
| 1 | Manage Project Process Configurator | tested | 6 + 8 | 4 | PASS, re-test R PASS | `GAPFILL_AB_B16_PPC1` (100004744435100; refused 100004744435070, 100004744436034); PPC2F (100004744434608); PPC3R (100004744436338) |
| 2 | Manage Applications Core Descriptive Flexfields | tested | 8 + 8 | 4 | PASS, re-test R PASS | `FND_ATTACHED_DOCUMENTS`: CTX1 + SEG1 (100004744435230); CTX2F (100004744434847); CTX3R (100004744433960) |
| 3 | Manage Tax Authority Profiles for Brazil | tested | 5 + 7 | 4 | PASS, re-test R PASS | `GAPFILL_AB_P3_LA3` flag Y → N (100004743457053; rounding try 100004743457000 not kept); LA4F (100004744433945); `GAPFILL_AB_B4FIX_LA5R` (100004743458058) |
| 4 | Manage Data Role and Security Profiles | tested | 6 + 7 | 4 | PASS, re-test R PASS | `GAPFILL_AB_B16_DR1` (100004744433931); DR2F (100004743457132); DR3R (100004744435396) |
| 5 | Manage Letter of Intent Limits for Italy | **failed** | 3 + 3 | 3 | not run | none; export 100004744431855 access denied |
| 6 | Manage Enterprise Financial Data Export Options for China | **failed** | 3 + 3 | 3 | not run | none; export 100004744431867 access denied |
| | **Total** | **4 tested, 2 failed** | **67** | **22** | 4 of 4 (+4 re-tests) | |

## Problems and findings
1. **Italy and China: failed.** Both task exports end `COMPLETED_ERRORS` with access denied (`WSFunctionPermission` on the localization web service); the template export is refused too. The sign-in user lacks the localization privilege. Next step: get that privilege (or a user with it) from the pod owner, then retry.
2. **Project process configurator** needs at least one source (`PJB_CONFIG_NO_SOURCE`) and a whole-number alias 1-8 (`PJB_CONFIG_INVALID_NUM_ALIAS`). Tested inactive (`Active N`).
3. **Flexfields:** a new context is loaded DISABLED with the parent row unchanged; no deploy was needed (DEPLOYED before and after). The export lists a flexfield only once it has a user context.
4. **Tax authority profiles:** the rounding columns are accepted (0 failed) but not kept; the skill changes `CollectingAuthorityFlag` instead.
5. **Data roles:** a copy of a test data role; nobody is assigned the new role.
6. One re-test agent started on the old skill text after a failed edit; it was stopped before it did anything and run again on the fixed text.

## What is left
See `MODULE_RESULT.md`.
