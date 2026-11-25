# Batch 05 result: Common Features (AB), view/search tasks and data access sets

GoSaaS work, not official FSCR. AB with Claude, 2026-11-25 (one sitting with batch 06). Tested on ETIA-TEST only (release 11.13.26.10.0). FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`; no FSCR file was edited. Work folder `E:\GoSaaS\gw\cf5\b05` (outside the repo; exports there hold user names). Record names `GAPFILL_AB_B5_<name>`, fresh tests end in F, re-tests in R.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 02:17 | 02:20 | 3 | Reading CONTEXT, batch 4 plan and results, helpers (sitting set-up, not in any task) |
| 02:19:58 | 02:22:20 | 2.5 | Sign-in (saved sign-in had expired; browser page completed). Waiting, not in any task |
| 02:22:30 | 02:27:03 | 4.5 | 12 read-only planning exports in 4 lanes (all worked first try). Waiting |
| 02:27 | 02:29 | 2 | my_gaps.csv, MODULE_TRACKER.csv, `scripts/build_module_tracker.py` |
| 02:29 | 02:38 | 9 | Live tests: data access set (2 tries), REST reads, new viewer `search-legal-entities/scripts/view_record.py`, 5 skills |
| 02:38 | 02:42 | 4 | 5 fresh tests in parallel (wall clock) |
| 02:42 | 02:46 | 4 | Wording fixes (2 skills + viewer option), 2 re-tests in parallel |
| 02:47 | 02:50 | 3 | Cards, changelogs, evidence, tracker, index |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records / ProcessIds |
|---|---|---|---:|---:|---|---|
| 1 | Search Legal Entities (`XLE_SEARCH_LEGAL_ENTITIES`) | tested | 4 + 4 | 2 | PASS, re-test R PASS | none created (search task); looked up 3 existing entities |
| 2 | Search Legal Reporting Units (`XLE_SEARCH_LEGAL_REPORTING_UNITS`) | tested | 3 + 2 | 2 | PASS | none created (search task) |
| 3 | View Accounting Configuration Summary (`GL_VIEW_ACCOUNTING_CONFIGURATION_SUMMARY`) | tested | 4 + 4 | 2 | PASS, re-test R PASS | none created (view task) |
| 4 | View Service Clients (`FUN_VIEW_SERVICE_CLIENTS`) | tested | 3 + 2 | 2 | PASS | none created (view task) |
| 5 | Manage Data Access Sets (`GL_MANAGE_DATA_ACCESS_SETS`) | tested (try 2) | 8 + 4 | 5 | PASS | `GAPFILL_AB_B5_DAS1` refused, not created (100004743395885); `GAPFILL_AB_B5_DAS2` (100004743395906); `GAPFILL_AB_B5_DAS3F` (100004742421450) |
| | **Total** | **5 of 5 tested** | **38** | **13** | 5 of 5 | |

- **View and search tasks (1 to 4) create nothing.** Their skill is a read-only guide (REST look-up + task export + viewer). The test is: a fresh Claude, given only the task name and SKILL.md, finds a named existing record and reports its setup; I checked its answer against my own read. No record was created for them. Reports should say "tested by a fresh Claude on ETIA-TEST, read-only guide, existing record read back".
- **No `retest_after_wording_fix` is pending.** Skills 1 and 3 changed after their fresh tests and were re-tested (R). Skills 2, 4, 5 are on disk as tested; their testers' notes are suggestions and are listed, not applied, in each CHANGELOG.
- `view_record.py` got an optional `--match-cols` after the fresh tests of 2 and 4; their commands do not use it, so their tested behaviour is unchanged.

## Problems and findings
1. **Data access set, try 1 refused:** `GL_INVALID_LEDGER: You must enter a valid ledger value` (1 row processed, 1 failed). Export check: 0 GAPFILL sets, nothing created. Cause, proved by try 2 (one change): `StructureInstanceCode` was empty; every working set has it. It is read live by REST: `chartOfAccountsLOV` filtered by `StructureInstanceNumber` = the ledger's `ChartOfAccountsId` (`ledgersLOV`). No internal id is copied from an export.
2. **Search results leak across entities:** a plain value search showed rows of another legal entity whose reporting-unit registration number equals the searched identifier. Fixed with `--match-cols` (identifier and name columns only); re-test showed only the entity's own rows.
3. **Wrong sentence found by a tester (fixed, re-tested):** `GL_PRIMARY_LEDGER.csv` holds rows for reporting-currency (ALC) ledgers too, not only secondary ledgers; relationships also have `JOURNAL` level and `RelationshipEnabledFlag=N` rows.
4. **Person data in exports:** `FUN_BUSINESS_UNIT.csv` holds manager names and person numbers. `view_record.py` hides person and audit columns; evidence images hold none.
5. **REST `LIKE` is case-sensitive** (an all-lower-case search found 0 rows).
6. **FSCR prints file names that hold the environment name** (export ZIP and import logs). Never copied into evidence or reports.
7. Timings: these exports took 30 s to 2 min; imports 25 to 95 s.

## What is left
Batch 06 ran in the same sitting (`BATCH_06_RESULT.md`). After it the sitting limit (10 tasks) was reached. 96 Common Features gaps are open: see `my_gaps.csv` and `MODULE_TRACKER.csv`.
