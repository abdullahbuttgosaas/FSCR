task_code: ORA_FND_MANAGE_DOCUMENT_SEQUENCES_BU
task_name: Manage Business Unit Document Sequences
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 5
waiting_minutes: 5
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (ORA_FND_APP_DOCSEQ_BU + ORA_FND_APP_DOCSEQ_ASSIGNMENT_BU) + REST documentSequences read-back
depends_on: FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES (a test category on WIE_WORK_ORDERS_B); an existing business unit
test_records: category GAPFILL_AB_B9_BC1 (100004742441924); GAPFILL_AB_B9_BSQ1 (100004742423977); fresh GAPFILL_AB_B9_BSQ2F (100004743405852); re-test GAPFILL_AB_B9_BSQ3R (100004744392361)
notes: Batch 09. No BU sequence existed before (export 0 rows); Oracle accepted a sequence on WIE_WORK_ORDERS_B with determinant BU (REST). OrganizationCode = business unit name. Fresh test PASS but found a wrong sentence ('pick another legal entity') and a false FAIL when the after-export made no ZIP; both fixed; re-test PASS.
