task_code: HZ_MANAGE_RESOURCE_NOTE_DESCRIPTIVE_FLEXFIELDS
task_name: Manage Resource Note Descriptive Flexfields
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 4
minutes_to_test: 7
waiting_minutes: 6
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (flexfield package) on ZMM_NOTE_DFF: new disabled context + one segment; parent read by REST when the export is empty
depends_on: manage-applcore-dffs builder
test_records: GAPFILL_AB_B17_NCX1 + NSG1 on ATTRIBUTE15 (100004743458151); fresh NCX2F + NSG2F (100004743457183); re-test NCX3R + NSG3R (100004743457283)
notes: Batch 17 (sitting 7). Own test Case A PASS (check_dff_rows.py). Fresh test Case B PASS, wording fixed, re-test PASS (contexts 2 -> 3). DEPLOYED before and after.
