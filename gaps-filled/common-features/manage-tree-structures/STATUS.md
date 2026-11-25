task_code: FND_MANAGE_TREE_STRUCTURES
task_name: Manage Tree Structures
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 6
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV (FND_APP_TREE_STRUCTURE + data source, parameter and root relationship rows; seeded rows copied unchanged) + export compare
depends_on: a seeded structure to copy data sources from (GL_ACCT_FLEX)
test_records: GAPFILL_AB_B7_TS1 (refused 100004742421534; created 100004742441558, relationship row replaced); GAPFILL_AB_B7_TS2 (100004742423588); fresh GAPFILL_AB_B7_TS3F (100004743404182)
notes: Batch 07. New DRAFT tree structure with one data source, its parameter and the root relationship row. Try 1 refused (NumberOfTrees, RestrictByDate required); try 2 showed a self relationship row replaces the root row, so the skill sends the root row only; try 3 PASS. Fresh test PASS first try; its notes are suggestions (in CHANGELOG).
