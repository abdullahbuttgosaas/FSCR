task_code: ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES
task_name: Manage Legal Entity Tax Profiles
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 5
minutes_to_test: 6
waiting_minutes: 4
fresh_claude_pass: yes
route: FSM CSV (ZX_LEGAL_ENTITY_TAX_PROFILE): update own row
depends_on: a legal entity (test: test-legal-entity skill)
test_records: GAPFILL_AB_B14_LE1 profile (100004743430357); fresh GAPFILL_AB_B14_LE2F (100004744413207); re-test GAPFILL_AB_B14_LE3R (100004743435628)
notes: Batch 14 (sitting 6). Re-opened from written (unsafe): a NEW test legal entity (prefix name) gets its own tax profile, so updating that one row changes no real entity. New prerequisite skill test-legal-entity and helpers scripts/own_row_package.py + compare_own_update.py. Own test PASS (RoundingRuleCode NEAREST, RoundingLevelCode LINE; other rows changed 0). Fresh test PASS on GAPFILL_AB_B14_LE2F, wording fixed, re-test PASS on GAPFILL_AB_B14_LE3R.
