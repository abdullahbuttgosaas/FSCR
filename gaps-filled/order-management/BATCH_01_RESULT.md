# Batch 01 - Order Management gap fill (sitting 1, 2026-11-26)

## Time log
| Step | Start | End | Kind |
|---|---|---|---|
| Sign-in (browser) | 17:20 | 17:22 | waiting |
| Gap list, tracker, screen-only checks (9 exports refused, REST 404s) | 17:22 | 17:28 | working (screen-only, not counted) |
| Read-only exports (5 tasks, parallel) | 17:23 | 17:24 | waiting |
| Rows, packages, imports (5 parallel), after-exports | 17:28 | 17:31 | working 2 / waiting 2 |
| 5 SKILL.md written | 17:31 | 17:32 | working |
| Fresh tests F (5 parallel sub-agents) | 17:32 | 17:35 | working (tests) / waiting (Oracle) |
| Wording fixes + re-tests R (5 parallel) | 17:35 | 17:39 | working |
| Cards, evidence, this report | 17:39 | 17:41 | working |

## Tasks
| Task | Status | Working min | Waiting min | Test records | Own-test ProcessIds (export / import / after) |
|---|---|---:|---:|---|---|
| Manage Status Values (DOO_MANAGE_STATUS_VALUES) | tested | 10 | 6 | FSCRT_AK_GF_ST1, _STF, _STR | 100004744432201 / 100004743455333 / 100004744422896 |
| Manage Task Types (DOO_MANAGE_TASK_TYPES) | tested | 10 | 6 | FSCRT_AK_GF_TT1, _TTF, _TTR | 100004744422798 / 100004743456286 / 100004743455410 |
| Manage Jeopardy Priorities (DOO_MANAGE_JEOPARDY_PRIORITIES) | tested | 10 | 6 | FSCRT_AK_GF_JP1, _JPF, _JPR | 100004743455297 / 100004744431219 / 100004743456337 |
| Manage Channel Program Types (ORA_CJM_MANAGE_PROGRAM_TYPES) | tested | 10 | 6 | FSCRT_AK_GF_PT1, _PTF, _PTR | 100004744431194 / 100004744432477 / 100004744432496 |
| Manage Pricing Matrix Types (ORA_QP_MANAGE_PRICING_MATRIX_TYPES) | tested | 10 | 6 | FSCRT_AK_GF_MT1, _MTF, _MTR | 100004743456213 / 100004744422848 / 100004744431234 |

Fresh-test and re-test ProcessIds are in each task's CHANGELOG.md. Every read-back: only FSCRT_AK_GF_ rows added,
0 existing rows changed or missing; Channel Program Types and Pricing Matrix Types also read back by REST.

Screen-only (not counted toward the sitting limit): 9 tasks in `screen-only.csv` (export refused with no ProcessId,
no REST resource; 5 of them are scheduled processes, not setup records).

## Problems and findings
- All 5 loaded first time through FSCR's task-level CSV import; no CreatedBy/LastUpdatedBy needed.
- Jeopardy Priorities: unsafe-looking (seeded HIGH/MEDIUM/LOW ranges are shared), but a new code with its own
  non-overlapping score range is accepted, so no shared value was touched.
- Pricing Matrix Types: Oracle resolves the matrix class id from DynamicMatrixClassName; no id copied.
- Fresh testers F found real wording gaps (one wrong example range in Jeopardy, an incomplete column list, no
  code-free command); fixed in all 5 skills and re-tested R: 5/5 pass, no wrong sentence left.
- FSCR's own output file names and import logs hold the environment and submitting user: kept in WORK only;
  `read_import_log.py` masks the submitter.

## What is left
21 CSV tasks open (see MODULE_TRACKER.csv). Batch 02 (already started): Pricing Results Presentations, Pricing
Totals, Time Unit Mappings, External Service Details for Algorithms, Order Attachment Categories.
