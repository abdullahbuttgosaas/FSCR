task_code: GL_MANAGE_CONVERSION_RATE_TYPES
task_name: Manage Conversion Rate Types
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 2
minutes_to_test: 2
waiting_minutes: 1
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_CRT_T1; GAPFILL_CRTF1_A1; GAPFILL_AB_RT_CRT
notes: Batch 1 part 3. Skill on the generic helpers in manage-docseq-categories/scripts. Cross rates (pivot + rule rows) not tested. Test rate types show in every rate type list. Re-tested 2026-11-24 after the wording fix: PASS.
