task_code: FND_CREATE_IMPLEMENTATION_USERS
task_name: Create Implementation Users
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 0
waiting_minutes: 0
fresh_claude_pass: not run
route: REST SCIM /hcmRestApi/scim/Users and /Roles through FSCR's own core skill core/getting-started/implementation-users; also hcm userAccounts (get, create, upsert); no FSM CSV
depends_on: none (sign-in user needs user/role admin rights)
test_records: none
notes: Batch 09. Finding: FSCR has a skill for this (core/getting-started/implementation-users) that the catalog does not map to this task code. unsafe to test: creates a sign-in account with IT Security Manager and setup roles on the shared environment. FSCR's read-only preflight was not run (our tool permissions blocked account-related calls), so live steps are GUESS. Next step: run only on an environment we own, with the security owner's written approval.
