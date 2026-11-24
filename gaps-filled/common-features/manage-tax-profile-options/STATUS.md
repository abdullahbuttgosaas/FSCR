task_code: ORA_ZX_MANAGE_TAX_PROFILE_OPTIONS
task_name: Manage Tax Profile Options
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 3
minutes_to_test: 3
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P1_ZPO1 (live); GAPFILL_AB_P1_ZPO2F (fresh test); new ZX profile options, site level only, no values
notes: Batch 4 part 1. Card over manage-profile-options; ZX ids read live by REST. Export leaves seeded ZX options out but shows new ones. REST read-back + export compare PASS. Fresh test PASS, no deviation; tester notes not applied.
