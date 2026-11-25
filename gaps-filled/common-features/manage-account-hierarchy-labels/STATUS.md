task_code: ORA_GL_MANAGE_ACCOUNT_HIERARCHY_LABELS
task_name: Manage Account Hierarchy Labels
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV (FND_APP_TREE_LABEL + parent structure and data source rows copied unchanged) + REST fndLabels read-back
depends_on: none (seeded GL_ACCT_FLEX structure)
test_records: GAPFILL_AB_B7_AHL1 (100004743403129); fresh GAPFILL_AB_B7_AHL2F (100004743403403); re-test GAPFILL_AB_B7_AHL3R (100004743404147)
notes: Batch 07. New label on GL_ACCT_FLEX parent values data source; DataSourceId read live by REST fndLabels; LabelId generated and kept. Fresh test PASS but found a wrong sentence (export row counts: custom structures and labels made later also appear); fixed (and export retry added), re-test R PASS on the final wording.
