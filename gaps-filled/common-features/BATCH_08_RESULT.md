# Batch 08 result: Common Features (AB), ledger document sequences, 4 tax/legal entity tasks, "neither" checks

GoSaaS work, not official FSCR. AB with Claude, 2026-11-25 (second Common Features sitting, after batch 07). Tested on one test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file was edited. Work folder outside the repo. Record names `GAPFILL_AB_B8_<name>`; no existing record was edited or deleted.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 03:34 | 03:44 | 10 | Exports of 5 tasks; 4 "unsafe to test" skills; ledger sequence tries 1 and 2 |
| 03:44 | 03:50 | 6 | Fresh test of ledger sequences (waiting), FND-7020 diagnosis, skill fix |
| 03:50 | 03:55 | 5 | Re-test (waiting); read-only exports and REST probes of the 49 "neither" tasks |
| 03:55 | 04:00 | 5 | Cards, evidence, tracker, reports |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records / ProcessIds |
|---|---|---|---:|---:|---|---|
| 1 | Manage Ledger Document Sequences (`ORA_FND_MANAGE_DOCUMENT_SEQUENCES_LEDGER`) | tested (try 2) | 5 + 6 | 5 | PASS on re-test | `GAPFILL_AB_B8_LSQ1` (refused 100004742423686); `LSQ2` (100004743403613); fresh `LSQ3F` (refused FND-7020, 100004742423742); re-test `LSQ4R` (100004742423771) |
| 2 | Manage Legal Entity Tax Profiles (`ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES`) | written (unsafe to test) | 4 + 0 | 1 | not run | none |
| 3 | Manage Configuration Owner Tax Options (`ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS`) | written (unsafe to test) | 3 + 0 | 1 | not run | none |
| 4 | Manage Intercompany Exceptions (`XLE_MANAGE_INTERCOMPANY_EXCEPTIONS`) | written (unsafe to test) | 3 + 0 | 1 | not run | none |
| 5 | Manage Legal Reporting Unit Tax Profiles (`ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES`) | written (unsafe to test) | 3 + 0 | 1 | not run | none |
| | **Total** | **1 tested, 4 written** | **24** | **9** | 1 of 1 | |

## Why 4 tasks are "written", not tested
- **Legal entity tax profiles** and **reporting unit tax profiles:** Oracle makes one profile with each legal entity / reporting unit (67 rows each); every load updates an existing profile and changes tax on real transactions.
- **Configuration owner tax options:** each row belongs to a real business unit or legal entity; there is no test owner.
- **Intercompany exceptions:** the package is the whole legal entity package; any load changes or creates a legal entity.
Read steps VERIFIED; change/import/read-back GUESS. Evidence 01 to 03 only.

## Problems and findings
1. **Ledger sequence needs `ValidateTransactionDate`** (try 1: JBO-27014, nothing created).
2. **FND-7020 UNIQUE-DATE OVERLAP:** one category may have only one open assignment per ledger. My fresh-test brief reused the category and ledger of try 2, so the fresh test was refused (my brief's fault, but the skill did not warn). Added Prerequisite 3 with a check one-liner, a START default and a failure note; re-test on another ledger PASS.
3. **REST `documentSequences`** rejects `TableName` in `fields` (HTTP 400).
4. **The 49 "neither" tasks:** none has an FSM CSV route (each read-only export refused or the Oracle task flag says no CSV). REST routes found for messages (3 tasks), partner organizations, user accounts (2 tasks), and read-only LOVs (time zones, territories, languages); 404 for industries, natural/ISO languages, approval groups, resource teams/organizations, geographies, user preferences, asset books, simulator transactions, tax geographies. Each result is in the task's reason in `my_gaps.csv`. None was marked screen-only yet: a screen-only call needs the REST check per task to be finished.

## What is left
Sitting limit reached (10 tasks: 6 tested, 4 written, 0 failed). 86 Common Features gaps open. Next candidates: the REST routes found above (messages, partner organizations, user accounts), cross-validation rules (check FBDI/REST), descriptive flexfields (deploy), then the remaining "neither" tasks one by one.
