task_code: ZX_MANAGE_TAX_STATUSES
task_name: Manage Tax Statuses
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 17
minutes_to_test: 12
waiting_minutes: 24
fresh_claude_pass: yes
route: FSM CSV
depends_on: ZX_MANAGE_TAXES; ZX_MANAGE_TAX_REGIMES (Step 7 GCO option row)
test_records: GAPFILL_AB_TF_ST1; GAPFILL_AB_TF_ST2F; GAPFILL_AB_TF_ST3R; for the tests also tax GAPFILL_AB_TF_TX2 (regime GAPFILL_AB_TR2F) and GCO option rows on GAPFILL_AB_TR1/TR2F/TR3R
notes: Batch 3 part 1 failed 3 times (ZX_INVALID_VALUE Tax attribute). Batch taxfix 2026-11-24: real cause = the test regime had no global configuration owner option row (ORA_ZX_BU_GCO_TAX_SUB); every regime with tax content has one; tax rows differ only in option flags. After manage-tax-regimes Step 7 the status imported first try (ProcessId 100004741413261), compare PASS. Fresh test PASS on a regime with the GCO row only, no BU subscription (ST2F, ProcessId 100004741414186); wording fixed (file count, template tax column, totals line); re-test PASS (ST3R, ProcessId 100004741415225), no wording change after it.
