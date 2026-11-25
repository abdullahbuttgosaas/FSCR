task_code: ZX_MANAGE_APPLICATION_TAX_OPTIONS
task_name: Manage Application Tax Options
module: Common Features
status: failed
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 10
waiting_minutes: 7
fresh_claude_pass: no
route: FSM CSV (ZX_APPLICATION_TAX_OPTIONS): import runs, but the row is not tied to the named business unit
depends_on: a NEW business unit (test-business-unit skill)
test_records: GAPFILL_AB_B15_BU1 / AP (100004744413261; proof refusal 100004743431825); fresh GAPFILL_AB_B15_BU2F / AP refused ZX_APPL_OU_UNIQUE (100004743432577); probe with a name that does not exist refused the same way (100004744415341)
notes: Batch 15 (sitting 6). FAILED. My test: try 1 on new test BU GAPFILL_AB_B15_BU1 loaded (1 processed, 0 failed) but the export never shows rows and there is no REST resource; the second send was refused with ZX_APPL_OU_UNIQUE, which I took as proof. The fresh test on another brand-new BU was refused the same way, and a probe with a business unit name that does not exist was also refused with ZX_APPL_OU_UNIQUE: Oracle does not use Name to find the business unit, so try 1 most likely stored one AP row whose business unit was not resolved (cannot be seen by export or REST; AB to check on the page Manage Application Tax Options and remove it there if it shows). Next step: look on the page, find which column ties the row to a business unit (export also has EnterpriseId, EventClassCode, EntityCode), then retry on a new test BU.
