task_code: ORA_ZX_MANAGE_TRANSACTION_BASED_FISCAL_CLASSIFICATIONS
task_name: Manage Transaction-Based Fiscal Classifications
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 4
minutes_to_test: 7
waiting_minutes: 6
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P2_UDC1 (live); GAPFILL_AB_P2_UDC2F (fresh test); user-defined fiscal classification codes (type USER_DEFINED), level 1
notes: Batch 4 part 2. Card over manage-transaction-fiscal-classifications (family user; keys without the parent column; type row USER_DEFINED sent unchanged). Export compare PASS. Fresh test PASS; tester notes not applied.
