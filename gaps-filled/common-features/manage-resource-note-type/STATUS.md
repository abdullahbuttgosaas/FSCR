task_code: HZ_MANAGE_RESOURCE_NOTE_TYPE
task_name: Manage Resource Note Type
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 1
minutes_to_test: 2
waiting_minutes: 1
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_NOTE_T3; GAPFILL_NOTE_A; GAPFILL_NTR_F3; GAPFILL_NTR_F3A; GAPFILL_AB_RT_NOTE; GAPFILL_AB_RT_NOTE_A
notes: Batch 1 part 1. Card over manage-standard-lookups. Tested with a new GAPFILL_ type (AB choice); adding a code to seeded ZMM_NOTE_TYPE is not tested. Re-tested 2026-11-24 after the wording fix: PASS.
