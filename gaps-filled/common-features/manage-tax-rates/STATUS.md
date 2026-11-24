task_code: ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES
task_name: Manage Tax Rates and Tax Recovery Rates
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 12
minutes_to_test: 6
waiting_minutes: 6
fresh_claude_pass: yes
route: FSM CSV
depends_on: ZX_MANAGE_TAX_STATUSES; ZX_MANAGE_TAX_REGIMES (Step 7 GCO option row)
test_records: GAPFILL_AB_TF_RT1; GAPFILL_AB_TF_RT2F
notes: Batch 3 part 2 (blocked: no status could be made) then batch taxfix 2026-11-24. Root cause was in the chain: the test regime had no global configuration owner option row (ORA_ZX_BU_GCO_TAX_SUB), so no status could exist. After manage-tax-regimes Step 7 and a status, a GCO percentage rate (template = GCO rate with no jurisdiction, parent status re-sent unchanged, no account row) imported first try (ProcessId 100004741411939), export compare PASS. Fresh test PASS (RT2F, 7 %, ProcessId 100004741413676), no wording change after it.
