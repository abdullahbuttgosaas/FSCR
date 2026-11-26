task_code: HZ_MANAGE_RESOURCE_ORGANIZATIONS
task_name: Manage Internal Resource Organizations
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 4
waiting_minutes: 2
fresh_claude_pass: yes (fresh F PASS; wording fixed, R PASS; one wrong sentence fixed, R2 PASS with no errors)
route: REST crm resourceUsers POST: a manager resource with a new ResourceOrganizationName creates the organization (no FSM CSV: task export refused, flag N; resourceOrganizations 404)
depends_on: a legal entity and business unit already used by resources (read live); a manager resource role (read live)
test_records: GAPFILL_AB_B22_ORG1 (manager GAPFILL_AB_B22_RM1); fresh GAPFILL_AB_B22_ORG2F (RM2F); R GAPFILL_AB_B22_ORG3R (RM3R); R2 GAPFILL_AB_B22_ORG4R (RM4R). No user accounts, example.invalid emails
notes: Batch 22 (sitting 10). Re-judged from screen-only/open: the route found in batch 20 creates organizations. Own test and 3 tester runs read back 1 row each with role SALES_MANAGER and no account. Oracle filled ResourceParentOrganizationName with an earlier own test organization (GAPFILL_AB_B20_ORG1) each time; the skill says so. Tester suggestions not applied: heredoc for org.json, say outright the LE/BU pair comes from the Counter output.
