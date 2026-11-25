task_code: ORA_FUN_MANAGE_REFERENCE_DATA_SET_DATA_ACCESS_FOR_USERS
task_name: Manage Reference Data Set Data Access for Users
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 1
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run
route: REST dataSecurities, SecurityContext 'Reference data set' (or the CSV of ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS); no FSM CSV for this task code
depends_on: ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS (same resource and rules)
test_records: none
notes: Batch 10. unsafe to test: a grant gives a real user access to a reference data set (security change); only our own user is usable. Context filter read VERIFIED (24 rows); grant GUESS. Next step: load-test only on an environment we own, with written approval.
