task_code: ZX_MANAGE_TAX_REGIMES
task_name: Manage Tax Regimes
module: Common Features
status: tested
filled_by: AB
date: 2026-11-23
minutes_to_write: 7
minutes_to_test: 6
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_TR1; GAPFILL_AB_TR2F; GAPFILL_AB_TR3R
notes: Batch 2 part 3. New regime header + translation copied from an existing regime (new helper scripts/template_row.py), no subscription. REST taxRegimesLOV before-read and read-back + export compare (subscription and usage files unchanged). Fresh test PASS, wording fixed, re-test PASS (no wording change after it).
