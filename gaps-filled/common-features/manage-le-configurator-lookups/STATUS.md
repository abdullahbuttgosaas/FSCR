task_code: XLE_MANAGE_APPLICATION_LOOKUP
task_name: Manage Legal Entity Configurator Lookups
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 2
minutes_to_test: 3
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_LE_T2; GAPFILL_LE_A; GAPFILL_LEF2_TYPE; GAPFILL_LEF2_A; GAPFILL_LEF2_B; GAPFILL_AB_RT_LE; GAPFILL_AB_RT_LE_A
notes: Batch 1 part 2. Card over manage-tax-lookup-codes (standard view). After-export stays empty, so REST is the only check. Adding codes to seeded LE types is not tested. Re-tested 2026-11-24 after the wording fix: PASS.
