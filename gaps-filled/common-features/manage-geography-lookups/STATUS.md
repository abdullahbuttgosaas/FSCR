task_code: HZ_MANAGE_GEOGRAPHY_LOOKUPS
task_name: Manage Geography Lookups
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 1
minutes_to_test: 2
waiting_minutes: 1
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_GEO_T2; GAPFILL_GEO_A; GAPFILL_GEOF2_TYP; GAPFILL_GEOF2_K1; GAPFILL_GEOF2_K2
notes: Batch 1 part 1. Card over manage-standard-lookups. Tested with a new GAPFILL_ type; adding codes to the 7 seeded HZ_GEO types is not tested. Export is empty, REST is the check.
retest_after_wording_fix: pending
