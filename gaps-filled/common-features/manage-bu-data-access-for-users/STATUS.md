task_code: ORA_FUN_MANAGE_BUSINESS_UNIT_DATA_ACCESS_FOR_USERS
task_name: Manage Business Unit Data Access for Users
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 2
waiting_minutes: 1
fresh_claude_pass: yes
route: REST dataSecurities POST, SecurityContext 'Business unit' (via scripts/rest_call.py); no FSM CSV for this task code
depends_on: ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS (same resource and rules); FND_CREATE_IMPLEMENTATION_USERS (test user with the role); an existing business unit
test_records: GAPFILL_AB_B11_U1 + Buyer + business unit USA Business Unit1; fresh GAPFILL_AB_B11_U2F + Buyer + business unit GoSaaS
notes: Batch 11 (re-opened: grant to our own new test user nobody signs in with). Business unit only named, not changed. Created first try after the role was on the test user; read back by Userrf and by id. Fresh test PASS.
