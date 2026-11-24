task_code: ZX_MANAGE_TAX_RULES
task_name: Manage Tax Rules
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 14
minutes_to_test: 6
waiting_minutes: 11
fresh_claude_pass: yes
route: FSM CSV
depends_on: ZX_MANAGE_TAXES; ZX_MANAGE_TAX_REGIMES (Step 7 GCO option row); ZX_MANAGE_TAX_CONDITION_SETS
test_records: GAPFILL_AB_TF_RL1; GAPFILL_AB_TF_RL2F (both disabled)
notes: Batch 3 part 2 failed 3 times (ZX_RECRATE_DATE_INVALID, empty placeholders = tax not found). Batch taxfix 2026-11-24: real cause = the test regime had no global configuration owner option row (ORA_ZX_BU_GCO_TAX_SUB); every regime with tax content has one. After manage-tax-regimes Step 7 the same disabled GCO applicability rule imported first try (ProcessId 100004742410090), export compare: 3 rows added, nothing changed. Fresh test PASS (RL2F on a new tax of a regime with only the GCO row, ProcessId 100004741413821), no wording change after it.
