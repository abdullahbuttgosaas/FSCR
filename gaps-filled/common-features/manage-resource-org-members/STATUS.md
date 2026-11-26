task_code: HZ_MANAGE_RESOURCE_ORGANIZATION_MEMBERS
task_name: Manage Resource Organization Members
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 12
minutes_to_test: 10
waiting_minutes: 4
fresh_claude_pass: yes (fresh test PASS: GAPFILL_AB_B20_RM4F manager of ORG3F + member RM5F; wording fixed to v0.1.1; R re-test PASS: RM7R manager of ORG5R + member RM8R)
route: REST crm resourceUsers POST (manager with a new ResourceOrganizationName; member with ResourceParentOrganizationName); no FSM CSV (export refused)
depends_on: a legal entity and business unit used by existing resources; resource roles (crm resourceRoles)
test_records: ResourceProfileIds: GAPFILL_AB_B20_RM1 300000395380145 (manager, made org GAPFILL_AB_B20_ORG1); GAPFILL_AB_B20_RM2 300000395370158 (member); fresh RM4F 300000395370617, RM5F 300000395452292; R RM7R 300000395392208, RM8R 300000395454601. No user accounts.
notes: Batch 20 (sitting 9). Own test: 3 refused tries created nothing (HZ-120845 role required; HZ-120896 member needs parent organization; HZ-120839 manager email of a manager with no user); then manager + member created, read back 2 rows, resources 4 -> 6. Finding (fresh and R tests): a manager sent with no ResourceParentOrganizationName shows null in the POST answer but later reads back with parent GAPFILL_AB_B20_ORG1 (own test org); the skill says to check it. Remaining tester notes (not wording errors): pre-check once per new name; member's ResourceParentOrganizationName is its own organization.
