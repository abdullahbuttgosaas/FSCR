task_code: ZX_MANAGE_TRANSACTION_FISCAL_CLASSIFICATIONS
task_name: Manage Transaction Fiscal Classifications
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 8
minutes_to_test: 13
waiting_minutes: 9
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P2_TBC1 (live try 2, code + translation only, no denormalized row); GAPFILL_AB_P2_TBC2 (live, all 4 rows); GAPFILL_AB_P2_TBC3F (fresh test); transaction business category codes under PURCHASE_PREPAYMENTTRANSACTION
notes: Batch 4 part 2. Full skill + new helper scripts/fiscal_code_rows.py. Needs the seeded type row (ORA_ZX_TRANSACTION) sent unchanged, or 0 objects are processed; needs the denormalized rows. Export compare PASS, type row changed 0. Fresh test PASS; tester notes not applied.
