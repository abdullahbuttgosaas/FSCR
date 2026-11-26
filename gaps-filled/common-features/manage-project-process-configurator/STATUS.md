task_code: ORA_PJF_MANAGE_PROJECT_PROC_CONFIGURATOR
task_name: Manage Project Process Configurator
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 8
waiting_minutes: 4
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (configurator + translation + sources): new inactive configurator
depends_on: none
test_records: GAPFILL_AB_B16_PPC1 (100004744435100; refused tries 100004744435070 PJB_CONFIG_NO_SOURCE, 100004744436034 PJB_CONFIG_INVALID_NUM_ALIAS, nothing created); fresh GAPFILL_AB_B16_PPC2F (100004744434608); re-test GAPFILL_AB_B16_PPC3R (100004744436338)
notes: Batch 16 (sitting 7). New configurator for business process Asset Line Grouping (PJC_CAP_LINE_GROUPING), Active N, one source (Expenditure Type, alias 1). Own test PASS (compare: only own rows in 3 files; REST ActiveFlag False). Fresh test PASS (PPC2F), wording fixed, re-test PASS (PPC3R).
