task_code: ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS
task_name: Manage Configuration Owner Tax Options
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 5
minutes_to_test: 5
waiting_minutes: 3
fresh_claude_pass: yes
route: FSM CSV (ZX_CONFIGURATION_OWNER_TAX_OPTIONS): new row
depends_on: a legal entity as owner (test: test-legal-entity skill)
test_records: AP / STANDARD INVOICES row for GAPFILL_AB_B14_LE1 (100004743430482); fresh LE2F (100004743430917); re-test LE3R (100004744416273)
notes: Batch 14 (sitting 6). Re-opened from written (unsafe): a new row for a NEW test legal entity as owner changes no real owner. PartyTypeCode FIRST_PARTY, DetFactorTemplCode TAXREGIME, who columns empty. Own test PASS (4 -> 5 rows). Fresh test PASS on LE2F, wording fixed, re-test PASS on LE3R (2 path/quote fixes after it).
