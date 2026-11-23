task_code: ORA_ZX_MANAGE_TAX_LOOKUP_CODES
task_name: Manage Tax Lookup Codes
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 4
minutes_to_test: 3
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_TAX_T1; GAPFILL_TAX_A; GAPFILL_TAXF1_TYPE; GAPFILL_TAXF1_A; GAPFILL_TAXF1_B
notes: Batch 1 part 2. Full skill + 4 scripts (Financials generic lookup package, set-enabled view); import attempt 1 failed (ChangeSinceLastRefresh required). Risk: test types may show in tax screens for all users.
retest_after_wording_fix: pending
