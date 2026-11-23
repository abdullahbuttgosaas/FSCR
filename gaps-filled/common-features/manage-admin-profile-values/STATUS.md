task_code: FND_MANAGE_APPLICATIONS_CORE_ADMINISTRATOR_PROFILE_VALUES
task_name: Manage Applications Core Administrator Profile Values
module: Common Features
status: tested
filled_by: AB
date: 2026-11-23
minutes_to_write: 4
minutes_to_test: 5
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV
depends_on: FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS
test_records: GAPFILL_AB_V1 on GAPFILL_AB_PO1; GAPFILL_AB_V3F on GAPFILL_AB_PO3; GAPFILL_AB_V2R on GAPFILL_AB_PO2F
notes: Batch 2 part 1. Card over manage-profile-options. SITE value on own GAPFILL_ option only; parent option row must be copied unchanged (copy_parent_rows.py) or 0 rows process. Seeded options, PRODUCT/USER levels not tested. Fresh test PASS, wording fixed, re-test PASS.
