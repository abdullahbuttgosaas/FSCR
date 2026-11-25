task_code: ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS
task_name: Manage Data Access for Users
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 3
waiting_minutes: 1
fresh_claude_pass: yes
route: REST dataSecurities POST (fscmRestApi) through FSCR's REST client via scripts/rest_call.py; read-only FSM CSV export for reference
depends_on: FND_CREATE_IMPLEMENTATION_USERS (a test user that has the role, Step 5); GL_MANAGE_DATA_ACCESS_SETS (a test data access set)
test_records: GAPFILL_AB_B11_U1 + General Accountant + data access set GAPFILL_AB_B5_DAS2; fresh GAPFILL_AB_B11_U2F + General Accountant + GAPFILL_AB_B5_DAS3F
notes: Batch 11 (re-opened: a grant to our own new test user, which nobody signs in with, is a new record nobody uses). Tries: 1 RoleCommonName only -> 'attribute Role isn't valid'; 2 user without the role -> LOV_RoleNameCr no matching row; 3 after giving the role -> created. Finding: q=UserName returns 0 rows; filter on Userrf. Fresh test PASS.
