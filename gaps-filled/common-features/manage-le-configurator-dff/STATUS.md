task_code: XLE_MANAGE_APPLICATION_DESCRIPTIVE_FLEXFIELD
task_name: Manage Legal Entity Configurator Descriptive Flexfield
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 5
minutes_to_test: 7
waiting_minutes: 6
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (flexfield package) on XLE_LE_INFO_DEV: new disabled context + one segment; parent read by REST when the export is empty
depends_on: manage-applcore-dffs builder
test_records: GAPFILL_AB_B17_LCX1 + LSG1 on LE_INFORMATION11 (100004743459017); fresh LCX2F + LSG2F (100004743457166); re-test LCX3R + LSG3R (100004743459430)
notes: Batch 17 (sitting 7). Own test Case A (export empty before; check_dff_rows.py PASS: only own 2 rows created today). Fresh test Case B PASS (contexts 37 -> 38), wording fixed (Case B is now normal, success lines, EnabledFlag check), re-test PASS (38 -> 39). DEPLOYED before and after, no deploy run. Flexfield choice by name is GUESS.
