task_code: GL_MANAGE_SEGMENT_VALUE_SECURITY_RULES
task_name: Manage Segment Value Security Rules
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 5
minutes_to_test: 5
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV (FND_APP_FLEX_VALUE_SET + values): new secured value set
depends_on: GL ModuleId read live (standardLookups)
test_records: value set GAPFILL_AB_B15_SVS1 + value T1 (100004744413699); fresh GAPFILL_AB_B15_SVS2F (100004743432393); re-test GAPFILL_AB_B15_SVS3R (100004743435641)
notes: Batch 15 (sitting 6). New General Ledger value set with SecurityEnabledFlag Y; no existing value set touched. Own test PASS (105 -> 106 value sets, 1161 -> 1162 values). Fresh test PASS (SVS2F), wording fixed, re-test PASS (SVS3R).
