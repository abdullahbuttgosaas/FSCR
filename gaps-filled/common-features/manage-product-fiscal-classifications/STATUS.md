task_code: ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS
task_name: Manage Product-Based Fiscal Classifications
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 3
minutes_to_test: 3
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P2_PCC1 (live); GAPFILL_AB_P2_PCC2F (fresh test); product category fiscal classification codes (type PRODUCT_CATEGORY), level 1
notes: Batch 4 part 2. Card over manage-transaction-fiscal-classifications (family product; keys without the parent column; type row PRODUCT_CATEGORY sent unchanged). No item catalog needed for a category code. Export compare PASS. Fresh test PASS; tester notes not applied.
