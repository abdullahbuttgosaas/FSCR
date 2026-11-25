task_code: ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS
task_name: Manage Data Access for Users
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 0
waiting_minutes: 2
fresh_claude_pass: not run
route: FSM CSV (ORA_FUN_ALL_USER_DATA_ACCESS + context mapping + provisioning rules) or REST dataSecurities (get, create, upsert)
depends_on: a user who has the role; GL_MANAGE_DATA_ACCESS_SETS for the data access set context
test_records: none
notes: Batch 10. unsafe to test: every row gives a real user access to real company data; the only usable user is our own sign-in user, and self-granting access is an unapproved security change. Read-only export (4 files, 516 access rows) and REST reads VERIFIED; grant GUESS. Next step: load-test only on an environment we own, with written approval.
