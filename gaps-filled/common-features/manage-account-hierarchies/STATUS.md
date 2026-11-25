task_code: GL_MANAGE_ACCOUNT_HIERARCHIES
task_name: Manage Account Hierarchies
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 6
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV (tree, parameters, DRAFT version, nodes) + REST fndTreeNodes; ids read live by REST (helper manage-trees-and-tree-versions/scripts/tree_rows.py)
depends_on: FND_MANAGE_APPLCORE_VALUE_SETS (test value set with a parent value SummaryFlag Y and a child value); a template GL_ACCT_FLEX tree with nodes
test_records: prerequisite value set GAPFILL_AB_B7_AHVS with P100, D110 (100004742423615); GAPFILL_AB_B7_AH1 (100004742421559); fresh GAPFILL_AB_B7_AH2F (100004743402217)
notes: Batch 07. New account hierarchy on GL_ACCT_FLEX: tree, DRAFT version, root P100 (parent values data source) and child D110 (detail values), on a test value set made first. Not audited, activated or published. Wording improved before the fresh test (export retry, template one-liner, value set line). Fresh test PASS; its notes are suggestions (in CHANGELOG).
