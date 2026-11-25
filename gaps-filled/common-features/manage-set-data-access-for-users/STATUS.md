task_code: ORA_FUN_MANAGE_REFERENCE_DATA_SET_DATA_ACCESS_FOR_USERS
task_name: Manage Reference Data Set Data Access for Users
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 2
minutes_to_test: 2
waiting_minutes: 1
fresh_claude_pass: yes
route: REST dataSecurities POST, SecurityContext 'Reference data set' (via scripts/rest_call.py); no FSM CSV for this task code
depends_on: ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS (same resource and rules); FND_CREATE_IMPLEMENTATION_USERS (test user with the role); an existing reference data set
test_records: GAPFILL_AB_B11_U1 + Order Administrator + Common Set; fresh GAPFILL_AB_B11_U2F + Order Administrator + Enterprise Set
notes: Batch 11 (re-opened: grant to our own new test user nobody signs in with). Set only named, not changed; set checked by setIdSetsLOV. Created first try; read back by Userrf and by id. Fresh test PASS.
