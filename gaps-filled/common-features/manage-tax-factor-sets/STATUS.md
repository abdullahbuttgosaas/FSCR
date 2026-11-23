task_code: ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS
task_name: Manage Tax Determining Factor Sets
module: Common Features
status: tested
filled_by: AB
date: 2026-11-23
minutes_to_write: 4
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_FS1; GAPFILL_AB_FS2F
notes: Batch 2 part 3. New factor set (header + translation + factor lines) copied from an existing set with no regime, using manage-tax-regimes/scripts/template_row.py. No REST resource; export compare is the read-back (condition sets and rules unchanged). Fresh test PASS; no wording change after it.
