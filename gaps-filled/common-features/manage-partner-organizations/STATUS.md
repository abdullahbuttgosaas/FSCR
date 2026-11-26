task_code: HZ_MANAGE_PARTNER_ORGANIZATIONS
task_name: Manage Partner Organizations
module: Common Features
status: failed
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 6
waiting_minutes: 2
fresh_claude_pass: not run (failed before a working step)
route: REST crmRestApi partners (get, create, upsert, runAssignment); no FSM CSV (export refused)
depends_on: an owner resource (CRM resource of a person)
test_records: none created: POST GAPFILL_AB_B9_PRT1 (2026-11-25, no owner) and GAPFILL_AB_B21_PRT1 twice (2026-11-26: ResourceId attribute invalid; OwnerPartyNumber of own resource GAPFILL_AB_B20_RM1 refused 'Provide a valid value for ResourceId'); GET 0 rows
notes: Batch 21 (sitting 9). Was written-untested (SAFE WAY FOUND, sitting 8). Tested 2026-11-26 with an own owner resource (GAPFILL_AB_B20_RM1, active, no user account): Oracle refused the owner, nothing created. FAILED. Next step: an owner resource with a user account (e.g. the Import Worker Users test worker made a resource), with approval.
