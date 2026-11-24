task_code: ORA_ZX_MANAGE_PARTY_TAX_PROFILES
task_name: Manage Party Tax Profiles
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 5
minutes_to_test: 8
waiting_minutes: 9
fresh_claude_pass: yes
route: FSM CSV
depends_on: XLE_MANAGE_LEGAL_AUTHORITIES (Step 1: a test legal authority made WITHOUT its tax authority profile row)
test_records: GAPFILL_AB_P3_LA3 profile (live; legal authority GAPFILL_AB_P3_LA3 made without a profile as Step 1); GAPFILL_AB_P3_LA4F profile (fresh test; legal authority GAPFILL_AB_P3_LA4F, site GAPFILL_AB_P3_LA4F_S1); GAPFILL_AB_B4FIX_LA5R profile (fresh re-test after wording fix; legal authority GAPFILL_AB_B4FIX_LA5R); tax authority profiles on test legal authorities
notes: Batch 4 part 3. Full skill. The batch 3 test authorities already had profiles (the legal authority skill sends one), so Step 1 makes a new authority without it; then one profile row copied from a test profile. Third-party profiles are not in this package. Export compare PASS. Fresh test PASS. Batch 4 fix: Step 3 flag sentence corrected (ProcessForApplicabilityFlag is Y too), fresh re-test PASS; other tester notes not applied.
