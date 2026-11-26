# Batch 01 result: Purchasing gap fill (sitting 1)

## Time log
| Start | Finish | Note |
|---|---|---|
| 25/11/2026 15:33 | 25/11/2026 15:52 | read-only exports, own live tests, skills, first fresh tests (F) and retests (R) |
| 26/11/2026 14:53 | 26/11/2026 15:08 | after the API spend-limit stop: new sign-in, retests 2R and 3R on the final wording |

Sign-in waits (25/11 15:25, 26/11 14:53) are waiting time, not task time. Minutes are estimates from the run timestamps.

## Tasks
| Task | Status | Working min | Waiting min | Own test record | Own import ProcessId | Final fresh retest (record, import ProcessId) |
|---|---|---:|---:|---|---|---|
| PO_MANAGE_HAZARD_CLASSES | tested | 15 | 6 | FSCRT_MZ_GF_HC1 | 100004743405677 | FSCRT_MZ_GF_HC3R, 100004743448041 |
| PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES | tested | 13 | 5 | FSCRT_MZ_GF_AS1 | 100004743402666 | FSCRT_MZ_GF_A3R, 100004743447599 |
| ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_LOOKUPS | tested | 16 | 6 | FSCRT_MZ_GF_LK1 | 100004742441892 | FSCRT_MZ_GF_LK3R, 100004744417642 |
| PO_MANAGE_UN_NUMBERS | tested | 16 | 7 | FSCRT_MZ_GF_UN1 | 100004742441905 | FSCRT_MZ_GF_UN3R, 100004743436725 |
| PO_MANAGE_PURCHASING_VALUE_SETS | tested | 17 | 6 | FSCRT_MZ_GF_VS1 | 100004743402716 | FSCRT_MZ_GF_VS3R, 100004743436599 |

Every own test and every fresh test: import completed successfully, 0 failed; after-export compare: only FSCRT_MZ_GF_ rows added, existing rows changed 0.

## Problems and findings
- FSCR's task-level CSV import (setupTaskCSVImports) works for all 5 objects with new rows only; no who-columns or internal IDs needed.
- Module IDs must be read live: External Purchase Prices lookups use the module of the `ORA_SCH_EPP%` lookup types; Purchasing value sets use the module of the `ORA_PO_*` lookup types.
- Oracle codes, not meanings: value sets need `INDEP`, `VARCHAR2`, `TEXT`.
- Fresh testers found wording errors (mostly in the shared COMMON_STEPS.md): `--match` output, extra prefix keys from parallel testers, environment names in FSCR file names and console lines, import status lines, the `$S` variable, free-text rule. All fixed; every skill passed again on the final wording (3R round) with no wrong sentence.
- The R retest of UN Numbers created and read back its records but stopped on an API spend limit before reporting; the 2R and 3R retests passed.
- Privacy: two early inspection outputs in the working chat showed the export's "submitted by" sign-in name and one existing buyer's e-mail; the scripts now mask them (`log_summary.py`, `inspect_export.py`). Nothing of that is in this folder.

## What is left
Nothing from this batch.
