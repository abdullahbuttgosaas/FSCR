task_code: FND_CREATE_DATA_ROLE_FOR_IMPLEMENTATION_USERS
task_name: Create Data Role for Implementation Users
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 7
minutes_to_test: 5
waiting_minutes: 4
fresh_claude_pass: yes
route: FSM CSV of Manage Data Role and Security Profiles (PER_HCM_DATA_ROLE + ORA_PER_HCM_DATA_ROLE_PROFILE), job role set to an implementation job role; builder scripts/impl_data_role.py (this task's own export is refused, flag N)
depends_on: PER_MANAGE_DATA_ROLE_AND_SECURITY_PROFILES (same package); a data role with View All profiles to copy; the implementation job role (read live by SCIM Roles)
test_records: GAPFILL_AB_B22_IDR1 (job ORA_HRC_HUMAN_CAPITAL_MANAGEMENT_APPLICATION_ADMINISTRATOR_JOB, 11 View All profiles, ProcessId 100004743461592); fresh GAPFILL_AB_B22_IDR2F (ProcessId 100004743462761). Assigned to nobody
notes: Batch 22 (sitting 10). Re-judged from screen-only/open. Own test: compare PASS (roles 16->17, profiles 160->171, 0 changed), SCIM role category DATA. Fresh test PASS (roles 17->18, profiles 171->182), no wrong sentence. Tester suggestions not applied: say whether SRC must already use JOB; write out the exp2 export command in full.
