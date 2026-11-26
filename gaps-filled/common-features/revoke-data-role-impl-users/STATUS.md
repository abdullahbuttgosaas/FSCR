task_code: FND_REVOKE_DATA_ROLE_FROM_IMPLEMENTATION_USERS
task_name: Revoke Data Role from Implementation Users
module: Common Features
status: written
filled_by: AB
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 0
waiting_minutes: 2
fresh_claude_pass: not run (unsafe)
route: REST hcm userAccounts child userAccountRoles (create, delete, get; describe VERIFIED); no FSM CSV (export refused)
depends_on: FND_CREATE_DATA_ROLE_FOR_IMPLEMENTATION_USERS
test_records: none
notes: Batch 20 (sitting 9). unsafe to test: the task's only action is a delete (revoke a role grant), which the test rules forbid even on own records; on another user it removes access. Safe way would need the person's written approval to delete, on an own test user given an own test role first.
