task_code: FND_MANAGE_REFERENCE_DATA_SET_ASSIGNMENTS
task_name: Manage Set Assignments for Set Determinant Type
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 5
minutes_to_test: 8
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV (FND_APP_REFERENCE_DATA_SET_ASSIGNMENT): new row, determinant type SET
depends_on: own reference data set as determinant (Manage Reference Data Sets)
test_records: set GAPFILL_AB_B15_SET1 (100004743432297); assignment SET1 PJF_RATES -> COMMON (100004744413542; refused BU tries 100004743432285, 100004743434516); fresh set GAPFILL_AB_B15_SET2F (100004744414204) + assignment (100004744415045); re-test set GAPFILL_AB_B15_SET3R (100004743432588) + assignment (100004744415284)
notes: Batch 15 (sitting 6). The package handles determinant type SET only (BU gives JBO-27014). Own test PASS (0 -> 1); status poll dropped once, result fetched by ProcessId (no re-import). Fresh test PASS (SET2F), wording fixed, re-test PASS (SET3R).
