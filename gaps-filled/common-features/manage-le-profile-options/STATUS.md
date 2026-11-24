task_code: XLE_MANAGE_LEGAL_ENITTY_PROFILE_OPTIONS
task_name: Manage Legal Entity Configurator Profile Options
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 4
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P1_XPO1 (live); GAPFILL_AB_P1_XPO2F (fresh test); new XLE profile options, site level only, no values
notes: Batch 4 part 1. Card over manage-profile-options; XLE application id and module id read live by REST (profileOptions by ApplicationShortName). REST read-back + export compare PASS. Fresh test PASS, no deviation; tester notes not applied.
