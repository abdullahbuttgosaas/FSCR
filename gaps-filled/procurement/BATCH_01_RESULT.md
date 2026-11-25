# Procurement batch 01: result (2026-11-25, AB with Claude)

5 easiest open tasks (after the 2 demo-reserve tasks). Every skill was written and passed AB's own live test. **No fresh test finished**: all 5 fresh testers stopped mid-run when the org reached its monthly Claude spend limit (API error 429; limit resets 2026-11-28 20:00 PKT). So all 5 are **written (fresh test pending)**, not tested.

## Time log
| Step | Start | Finish | Minutes |
|---|---|---|---|
| Read-only exports of all 19 CSV tasks + REST checks (sign-in waits included) | 16:59 | 17:12 | 13 |
| Batch 01 own live tests (5 tasks, 9 imports) | 17:12 | 17:22 | 10 |
| Batch 01 skills written | 17:22 | 17:25 | 3 (plus writing done between imports) |
| Sign-in renewal (waiting) | 17:25 | 17:25 | 0.5 |
| Fresh tests (5 in parallel) | 17:26 | ~17:30 | stopped by the spend limit |
Sign-in: 17:05 and 17:25 (waiting time, not task time). Clock times are local (PKT).

## Tasks
| Task | Status | Write / test / wait min | Test records (ProcessId) |
|---|---|---|---|
| ORA_PO_MANAGE_SPECIAL_HANDLING_TYPES, Manage Special Handling Types | written (fresh test pending) | 4 / 3 / 3 | GAPFILL_AB_B1_SH1 (100004743406576). Fresh SH2F: not created |
| OKC_MANAGE_CONTRACT_LINE_TYPES, Manage Contract Line Types | written (fresh test pending) | 4 / 4 / 3 | LT1 refused (100004744392804); GAPFILL_AB_B1_LT2 (100004744392822); fresh GAPFILL_AB_B1_LT3F created (100004744393348) |
| OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_LOOKUPS, Manage Contract Clause Types | written (fresh test pending) | 5 / 3 / 2 | code GAPFILL_AB_B1_CT1 on OKC_SUBJECT (100004744392840); fresh code GAPFILL_AB_B1_CT2F created (100004744393360) |
| OKC_MANAGE_CONTRACT_TERMS_VALUE_SETS, Manage Contract Terms Value Sets | written (fresh test pending) | 4 / 3 / 3 | GAPFILL_AB_B1_VS1 + 2 values (100004744391249); fresh GAPFILL_AB_B1_VS2F + 2 values created (100004744393376) |
| OKC_MANAGE_CONTRACTS_DELIVERABLE_PROCUREMENT_SYSTEM_LOOKUPS, Manage Contract and Procurement System Integrations | written (fresh test pending) | 5 / 6 / 6 | TS1, TS2, TS3 refused (100004744391264, 100004743405950, 100004744393274); round trip GAPFILL_AB_B1_TS4R (100004744392872). Fresh TS5F: not created |

## What the stopped fresh testers left (checked by AB, nothing imported twice)
- Clause types: CT2F imported (2 rows, 0 failed); AB's REST read: present, enabled.
- Line types: LT3F imported; after-export done; AB's compare: added 1, removed 0, changed 0.
- Value sets: VS2F imported (3 rows, 0 failed); AB's REST read: 2 values enabled.
- Special handling and integrations: only the before-export ran; no import.
These are **not** fresh passes (the testers did not finish on their own).

## Problems and findings
1. **Line type source:** a new line type must use an existing `SourceCode` (refused `OKC_SETUP_INVALID_LINE_SOURCE` otherwise). The `LineTypeCode` is the key: a fresh 32-character code makes a new row.
2. **Clause types:** the task export is empty (scope `OKC_SUBJECT`). The seeded type row, copied unchanged from REST, plus the new code row imported cleanly. The type and its 16 codes did not change (even its LastUpdateDate). The same pattern fits the 2 demo-reserve tasks (FOB, FREIGHT TERMS).
3. **System integrations:** an external target needs Endpoint URL + User Name (and likely a password). Not tested: an agent must not enter credentials. The internal (DIRECT) path works (round trip). One import's connection dropped after start. Its log was fetched by ProcessId and it was not re-imported (rule kept).
4. **Spend limit:** the fresh testers (sub-agents) all stopped at the same moment (org monthly spend limit). This is not a skill fault.
5. New helpers in `procurement/scripts`: `build_csv_package.py` (new-rows-only FSM ZIP from an export), `compare_exports.py` (before/after compare, ZIP check first), `lookup_type_row.py` (unchanged parent type row from REST), `build_module_tracker.py` (copied; now also shows written-untested).

## What is left
- Fresh tests of these 5 skills, with new names (SH3F, LT4F, CT3F, VS3F, TS6F), after the limit resets. Then set each card to tested.
