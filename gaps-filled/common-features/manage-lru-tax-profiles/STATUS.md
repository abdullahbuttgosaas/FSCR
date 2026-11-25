task_code: ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES
task_name: Manage Legal Reporting Unit Tax Profiles
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 5
minutes_to_test: 5
waiting_minutes: 4
fresh_claude_pass: yes
route: FSM CSV (ZX_ESTABLISHMENT_TAX_PROFILE, 73-file package): update own row
depends_on: a reporting unit (test: main unit of a test legal entity)
test_records: GAPFILL_AB_B14_LE1 unit profile (100004744411602); fresh GAPFILL_AB_B14_LE2F (100004743432165); re-test GAPFILL_AB_B14_LE3R (100004744416787)
notes: Batch 14 (sitting 6). Re-opened from written (unsafe): the test legal entity's main reporting unit has its own profile. Own row package, other 72 files header only. Own test PASS (other rows changed 0). Fresh test PASS on LE2F, wording fixed, re-test PASS on LE3R.
