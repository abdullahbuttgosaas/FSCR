task_code: ZX_MANAGE_TAX_EXCEPTIONS
task_name: Manage Tax Exceptions
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 4
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV
depends_on: ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES (test rate on a not live tax); ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS (test product category code)
test_records: GAPFILL_AB_P3_EXC1 (live, on GAPFILL_AB_TF_RT1 / GAPFILL_AB_P2_PCC1); GAPFILL_AB_P3_EXC2F (fresh test, on GAPFILL_AB_TF_RT2F / GAPFILL_AB_P2_PCC2F); 10 % discounts on not live test taxes
notes: Batch 4 part 3. Full skill, row in full (export was empty), codes only. First try worked. Export compare PASS. Fresh test PASS; tester notes not applied.
