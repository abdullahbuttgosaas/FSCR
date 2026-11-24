task_code: ORA_ATK_ADMIN_PROFILE_OPTION_VALUES
task_name: Manage Application Toolkit Administrator Profile Values
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 4
minutes_to_test: 3
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P1_APO1 + SITE value GAPFILL_AB_P1_AV1 (live); GAPFILL_AB_P1_APO2F + GAPFILL_AB_P1_AV2F (fresh test); values only on own new ATK options
notes: Batch 4 part 1. Card over manage-profile-options + manage-admin-profile-values; prerequisite (own ATK option) made in the same package as its SITE value (5 rows); ATK ids by REST. REST option + value read-back and export compare PASS. Fresh test PASS; tester notes not applied.
