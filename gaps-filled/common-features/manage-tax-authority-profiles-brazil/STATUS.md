task_code: ORA_ZX_MANAGE_TAX_AUTHORITY_TAX_PROFILES
task_name: Manage Tax Authority Profiles for Brazil
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 5
minutes_to_test: 7
waiting_minutes: 4
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (ZX_TAX_AUTHORITY_PROFILE): update of an own test legal authority's profile (own_row_package + compare_own_update)
depends_on: a test legal authority (manage-legal-authorities)
test_records: GAPFILL_AB_P3_LA3 CollectingAuthorityFlag Y -> N (100004743457053; rounding try 100004743457000 not kept); fresh GAPFILL_AB_P3_LA4F (100004744433945); re-test GAPFILL_AB_B4FIX_LA5R (100004743458058)
notes: Batch 16 (sitting 7). Only own GAPFILL test legal authorities are changed; rounding columns are accepted but not kept (VERIFIED). Own test PASS (own row changed, other rows unchanged). Fresh test PASS, wording fixed (re-test agent restarted once on the fixed text), re-test PASS.
