task_code: FND_MANAGE_TREES_AND_TREE_VERSIONS
task_name: Manage Trees and Tree Versions
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 5
waiting_minutes: 4
fresh_claude_pass: yes
route: FSM CSV (FND_APP_TREE + ORA_FND_APP_TREE_DATA_SOURCE_PARAMETER + ORA_FND_APP_TREE_VERSION) + REST fndTreeVersions; ids read live by REST (helper scripts/tree_rows.py)
depends_on: FND_MANAGE_APPLCORE_VALUE_SETS (a test value set); an existing active structure and a template tree with nodes
test_records: GAPFILL_AB_B7_TR1 (100004742423501); fresh GAPFILL_AB_B7_TR2F (100004743403418)
notes: Batch 07. New tree with one DRAFT version on GL_ACCT_FLEX, parameters copied from a template tree with the value set replaced by a test value set. New helper scripts/tree_rows.py reads data source and parameter ids live by REST (fndTreeNodes, fndTreeDataSourceParams finders). Fresh test PASS first try; its notes are suggestions (in CHANGELOG).
