task_code: ORA_ZX_MANAGE_LOCATION_FINAL_DISCHARGE
task_name: Manage Location of Final Discharge
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV
depends_on: none (seeded lookup HZ_CREATED_BY_MODULES read live)
test_records: GAPFILL_AB_P3_LFD1 (live, try 3); GAPFILL_AB_P3_LFD2F (fresh test); US test locations of final discharge at test streets
notes: Batch 4 part 3. Full skill, rows in full (export was empty). Needs CreatedByModule (HZ_WS), OrigSystemReference, StatusFlag A and EntityCode HZ_LOCATIONS (Oracle table docs). Tries 1 and 2 refused, nothing created. Export compare PASS. Fresh test PASS; tester notes not applied.
