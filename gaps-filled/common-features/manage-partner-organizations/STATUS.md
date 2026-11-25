task_code: HZ_MANAGE_PARTNER_ORGANIZATIONS
task_name: Manage Partner Organizations
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 0
waiting_minutes: 2
fresh_claude_pass: not run
route: REST crmRestApi partners (get, create, upsert, runAssignment); no FSM CSV (export refused)
depends_on: an owner resource (CRM resource of a person)
test_records: none (POST GAPFILL_AB_B9_PRT1 refused: ResourceId required; nothing created)
notes: Batch 09. unsafe to test: a partner must have an owner ResourceId (HTTP 400 without it, VERIFIED); the sign-in user is not a CRM resource (VERIFIED), so a test partner would be owned by a real colleague, who would see it and get its assignment work. Read steps VERIFIED; create GUESS. Next step: load-test only on an environment we own (or with our own resource), with written approval.
