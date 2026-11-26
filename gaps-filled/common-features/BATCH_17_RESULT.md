# Batch 17 result: Common Features (AB), legal entity and note flexfields, chart of accounts sync with DRM, archive and purge policies, screen-only sweep

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26 (seventh Common Features sitting, second batch). One test environment (release 11.13.26.10.0). FSCR scripts ran in place; no FSCR file edited. Work folder outside the repo. No existing record was edited or deleted: every new record has the prefix `GAPFILL_AB_`.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 18:00 | 18:06 | 6 | Legal entity and note flexfields: parent read by REST, own imports (Case A), `check_dff_rows.py` |
| 18:06 | 18:09 | 3 | Archive and purge: try 1 refused (needs ledger and balancing segment), export proves nothing created; ledgers read |
| 18:09 | 18:14 | 5 | Flexfield fresh tests F (parallel), wording fixes, re-tests R; 3 more read-only exports |
| 18:14 | 18:22 | 8 | Chart of accounts sync with DRM: GL profile option own test, card, fresh test, fixes, re-test |
| 18:16 | 18:24 | 8 | REST probes for the "neither" tasks (GET and describe only); 40 tasks proven screen-only |
| 18:24 | 18:40 | 16 | Cards, evidence, archive skill, re-judged written cards, tracker, reports |

## Results
| # | Task | Status | Working min (write + test) | Waiting min | Fresh test | Test records (ProcessId) |
|---|---|---|---:|---:|---|---|
| 1 | Manage Legal Entity Configurator Descriptive Flexfield | tested | 5 + 7 | 6 | PASS, re-test R PASS | `XLE_LE_INFO_DEV`: LCX1 + LSG1 (100004743459017); LCX2F (100004743457166); LCX3R (100004743459430) |
| 2 | Manage Resource Note Descriptive Flexfields | tested | 4 + 7 | 6 | PASS, re-test R PASS | `ZMM_NOTE_DFF`: NCX1 + NSG1 (100004743458151); NCX2F (100004743457183); NCX3R (100004743457283) |
| 3 | Manage Chart of Accounts Synchronization with DRM | tested | 6 + 5 | 5 | PASS, re-test R PASS | GL option `GAPFILL_AB_B17_GPO1` (100004743459537); GPO2F (100004743459557); GPO3R (100004743460308) |
| 4 | Manage Archive and Purge Policies | written (unsafe) | 6 + 4 | 3 | not run | none; try 1 refused (100004743458273), export after: 0 detail rows |
| | **Total** | **3 tested, 1 written** | **44** | **20** | 3 of 3 (+3 re-tests) | |

**Corrected by the screen-only audit (2026-11-26): 16 of these 40 were set back to open (15 had no REST probe, and Tax Box Allocation Rules may have a route); 24 stay. See `SCREEN_ONLY_AUDIT.md`.** Screen-only (as first written): 40, listed with reasons in `screen-only.csv` (Intercompany Exceptions re-judged from written; Associated Balancing Segments, Task Configurations and Tax Box Allocation Rules from their packages; 36 "neither" tasks after REST probes).

## Problems and findings
1. **Archive and purge: written (unsafe).** The global policy row (`ORA_ACCOUNTING_DATA` 99/98 years) hits every ledger; a detail row needs a real ledger and balancing segment value (`JBO-27014` without them) and changes when that ledger's data may be purged. No test ledger exists.
2. **Flexfields:** the first load of a flexfield with no user context is Case A (export empty before; check with `check_dff_rows.py`); every later run is Case B (normal compare). Fresh testers pointed this out; the skills now say it.
3. **Chart of accounts sync with DRM:** the CSV package holds only 2 GL profile options; the DRM connection is screen-only. GL owns options in 2 modules: the module is taken from the export's own rows.
4. **REST probes:** 22 resource names tried by GET; 404 for most; `languagesLOV`, `naturalLanguagesLOV`, `fixedAssetBooksLOV`, crm `geographies` and hcm `guidedJourneys` are read only (describe lists only get). crm `resourceUsers` allows create: Manage Resource Organization Members stays open.
5. **Re-judged written cards:** CRM BU profile options, Map Reports to Work Areas, Import Worker Users and Partner Organizations stay unsafe (reasons in their cards).

## What is left
See `MODULE_RESULT.md`.
