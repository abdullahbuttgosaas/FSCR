task_code: ORA_MANAGE_COA_CONFIG
task_name: Manage Chart of Accounts Configurations
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 5
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV (ORA_SEG_VAL_SECURITY_POLICIES): new policy
depends_on: a secured value set (GL_MANAGE_SEGMENT_VALUE_SECURITY_RULES)
test_records: policy GAPFILL_AB_B15_SVP1 on GAPFILL_AB_B15_SVS1 (100004743433661); fresh GAPFILL_AB_B15_SVP2F (100004744415062); re-test GAPFILL_AB_B15_SVP3R (100004744414677)
notes: Batch 15 (sitting 6). Policy on an own secured value set that no chart of accounts uses; options and the global usage row never sent. Own test PASS (policies 0 -> 1, rest unchanged). Fresh test PASS (SVP2F), wording fixed, re-test PASS (SVP3R; 2 small notes added after it).
