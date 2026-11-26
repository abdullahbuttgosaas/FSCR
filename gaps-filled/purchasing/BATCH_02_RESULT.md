# Batch 02 result: Purchasing gap fill (sitting 1)

## Time log
| Start | Finish | Note |
|---|---|---|
| 25/11/2026 15:40 | 25/11/2026 15:52 | read-only research, own live tests, skills (run alongside batch 01's fresh tests) |
| 26/11/2026 14:53 | 26/11/2026 15:08 | retests 2R and 3R on the final wording |

## Tasks
| Task | Status | Working min | Waiting min | Own test record | Own import ProcessId(s) | Final fresh retest (record, import ProcessId) |
|---|---|---:|---:|---|---|---|
| ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP | tested | 17 | 6 | FSCRT_MZ_GF_RS1 | try 1 100004743404860 (refused), try 2 100004743404898 | FSCRT_MZ_GF_RS3R, 100004743448053 |
| PO_MANAGE_CHANGE_ORDER_TEMPLATES | tested | 16 | 6 | FSCRT_MZ_GF_CO1 | 100004744391044 | FSCRT_MZ_GF_CO3R, 100004744422018 |
| ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES | written (unsafe to test) at the time; tested later in batch 03 | 6 | 1 | none | none | see BATCH_03_RESULT.md |
| PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS | written (unsafe to test) at the time; tested later in batch 03 | 7 | 1 | none | none | see BATCH_03_RESULT.md |

## Problems and findings
- Rule sets lookup: try 1 sent only the new code; Oracle skipped it ("Parent row is missing in file FND_APP_STANDARD_LOOKUP.csv ... Row will be skipped", 0 processed, nothing created). Fix: the seeded parent type row, read live by REST, sent unchanged. REST proof before/after: parent unchanged True, existing codes (DEFAULT) unchanged True. `build_fsm_package.py` got an `_unchanged_parents` section for this.
- Change order templates: round trip works. The new template copies the attribute rows (132) of an existing template under the new code; the source is only read.
- Buyer assignment rules: unsafe to test. A rule assigns an existing buyer (by e-mail) to other people's requisition lines; rules in DEFAULT drive real assignment. Skill written from the read-only export (columns VERIFIED, import GUESS).
- Purchasing DFFs: unsafe to test. A context or segment on a seeded Purchasing DFF needs a flexfield deploy that changes pages for every user. Skill written from the read-only export (13 CSVs, all 0 rows).

## What is left
The two tasks written as unsafe here were tested on 26/11/2026 in batch 03, after the tester confirmed the environment
is for testing only. Their evidence is under evidence/batch-03/.
