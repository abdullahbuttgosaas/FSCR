task_code: ZX_MANAGE_TAX_STATUSES
task_name: Manage Tax Statuses
module: Common Features
status: failed
filled_by: AB
date: 2026-11-23
minutes_to_write: 11
minutes_to_test: 0
waiting_minutes: 21
fresh_claude_pass: no
route: FSM CSV
depends_on: ZX_MANAGE_TAXES
test_records: none (GAPFILL_AB_P1_ST1, ST2, ST3 rejected, not created); made for the attempts: simulation tax GAPFILL_AB_P1_TX4S, subscription of GAPFILL_AB_TR1 by test BU ZZ_TEST_BU_1932
notes: Batch 3 part 1. Import rejected: ZX_INVALID_VALUE "You must provide a valid value for the Tax attribute" for test tax GAPFILL_AB_P1_TX1 (not live, regime GAPFILL_AB_TR1 with no subscription). A formula on the same tax imported fine. Every existing tax with a status is live (Y) or simulation (S) on a subscribed regime. Attempt 2 (AB approved a simulation tax): new tax GAPFILL_AB_P1_TX4S (S) created, status on it rejected the same way, so not-live is ruled out; attempt 3 (AB approved a subscription): test BU ZZ_TEST_BU_1932 subscribed to the regime, status still rejected. Stopped at 3 attempts. Remaining idea: a global configuration owner subscription (needs internal IDs, or the screen). Blocks rates (batch 3 part 2).
