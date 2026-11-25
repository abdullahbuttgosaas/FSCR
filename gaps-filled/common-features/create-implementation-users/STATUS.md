task_code: FND_CREATE_IMPLEMENTATION_USERS
task_name: Create Implementation Users
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 4
waiting_minutes: 1
fresh_claude_pass: yes (re-test R after a wording fix)
route: REST SCIM /hcmRestApi/scim/Users through FSCR's own core/getting-started/implementation-users scripts (run unchanged, plan roles emptied); read-back SCIM + hcm userAccounts; no FSM CSV
depends_on: none (sign-in user needs user-management rights)
test_records: GAPFILL_AB_B11_U1 (own test, no roles; later 3 roles for the data access tests); fresh GAPFILL_AB_B11_U2F (no roles; later roles added by the data access fresh tests); re-test GAPFILL_AB_B11_U3R (no roles). All mailboxes @example.com, nobody signs in
notes: Batch 11 (re-opened from written-unsafe under the new rule: a new prefix user with no roles is a new record nobody uses). FSCR plan lists 3 setup roles; emptied in the plan copy. Finding: FSCR executor reports assign_role_via_scim_roles 'error' although the role is added (Oracle answers the SCIM PATCH with an empty body); prove roles with a single-user SCIM GET. Fresh test PASS; 5 wording fixes (run folder, full Step 4 options, USERGUID reader, 'no roles key', count Resources); re-test PASS.
