task_code: PER_MANAGE_DATA_ROLE_AND_SECURITY_PROFILES
task_name: Manage Data Role and Security Profiles
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 7
waiting_minutes: 4
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (PER_HCM_DATA_ROLE + ORA_PER_HCM_DATA_ROLE_PROFILE): copy of a test data role under a new name; builder scripts/copy_data_role.py
depends_on: an existing test data role to copy
test_records: GAPFILL_AB_B16_DR1 copied from HCM_DATA_ROLE_TEST_DATA (100004744433931); fresh GAPFILL_AB_B16_DR2F (100004743457132); re-test GAPFILL_AB_B16_DR3R (100004744435396)
notes: Batch 16 (sitting 7). New data role, assigned to nobody (a security administrator would have to assign it). Own test PASS (roles +1, profiles +11, nothing else changed). Fresh test PASS, wording fixed, re-test PASS.
