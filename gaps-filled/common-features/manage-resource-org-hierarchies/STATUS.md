task_code: HZ_MANAGE_RESOURCE_ORGANIZATION_HIERARCHIES
task_name: Manage Resource Organization Hierarchies
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 6
waiting_minutes: 3
fresh_claude_pass: yes (fresh test PASS: GAPFILL_AB_B20_RM6F made ORG4F under ORG1; wording fixed to v0.1.1; R re-test PASS: RM9R made ORG6R under ORG1)
route: REST crm resourceUsers POST: a manager with a new ResourceOrganizationName and ResourceParentOrganizationName = the parent org; no hierarchy resource (crm resourceOrganizationHierarchies, resourceHierarchies 404); no FSM CSV (export refused)
depends_on: manage-resource-org-members (a parent organization with a manager)
test_records: GAPFILL_AB_B20_RM3 300000395370187 made GAPFILL_AB_B20_ORG2 under GAPFILL_AB_B20_ORG1; fresh RM6F 300000395454171 (ORG4F); R RM9R 300000395452321 (ORG6R). No user accounts.
notes: Batch 20 (sitting 9). Was screen-only by guess, set back to open by the audit; REST proof: no hierarchy resource, but the hierarchy is built through resourceUsers (VERIFIED read-back: ResourceParentOrganizationName = parent).
