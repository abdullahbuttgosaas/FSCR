task_code: ORA_FUN_MANAGE_BUSINESS_UNIT_DATA_ACCESS_FOR_USERS
task_name: Manage Business Unit Data Access for Users
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 2
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run
route: REST dataSecurities, SecurityContext 'Business unit' (or the CSV of ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS); no FSM CSV for this task code
depends_on: ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS (same resource and rules)
test_records: none
notes: Batch 10. unsafe to test: a grant gives a real user access to a business unit's data (security change); only our own user is usable. Context filter read VERIFIED (358 rows); grant GUESS. Next step: load-test only on an environment we own, with written approval.
