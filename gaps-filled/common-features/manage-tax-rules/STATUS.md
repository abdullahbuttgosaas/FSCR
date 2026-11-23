task_code: ZX_MANAGE_TAX_RULES
task_name: Manage Tax Rules
module: Common Features
status: failed
filled_by: AB
date: 2026-11-24
minutes_to_write: 8
minutes_to_test: 0
waiting_minutes: 8
fresh_claude_pass: no
route: FSM CSV
depends_on: ZX_MANAGE_TAXES; ZX_MANAGE_TAX_CONDITION_SETS
test_records: none (GAPFILL_AB_P2_RL1 rejected 3 times, not created)
notes: Batch 3 part 2. Disabled applicability rule on test tax GAPFILL_AB_P1_TX1 with condition set GAPFILL_AB_P2_CS1, template row from the one existing rule. All 3 imports rejected with ZX_RECRATE_DATE_INVALID (date range of the parent tax, placeholders not filled, so the tax was not found): owner GCO from the tax start, owner GCO a month later, owner = the test BU that subscribes the regime. Rules export after: nothing added. Likely the same cause as tax statuses (tax not live on a GCO-subscribed regime). Stopped at 3 attempts.
