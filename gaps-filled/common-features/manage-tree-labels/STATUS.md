task_code: FND_MANAGE_TREE_LABELS
task_name: Manage Tree Labels
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 4
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV (FND_APP_TREE_LABEL + parent structure and data source rows copied unchanged) + REST fndLabels read-back
depends_on: a label-enabled tree structure (seeded GL_ACCT_FLEX)
test_records: GAPFILL_AB_B7_TL1 (100004742423488); fresh GAPFILL_AB_B7_TL2F (100004743403630)
notes: Batch 07. New label on GL_ACCT_FLEX (labeling scheme GROUP). Parents copied unchanged; after-export shows them changed 0. LabelId is a generated GUID and is kept. Live compare also showed our own AHL1 label because the before export was older; wording covers this. Wording fixed before the fresh test (row counts, export retry). Fresh test PASS; its notes are suggestions (in CHANGELOG).
