task_code: FND_MANAGE_APPLICATIONS_CORE_PROFILE_CATEGORIES
task_name: Manage Applications Core Profile Categories
module: Common Features
status: tested
filled_by: AB
date: 2026-11-23
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 1
fresh_claude_pass: yes
route: FSM CSV
depends_on: FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS
test_records: GAPFILL_AB_PC1; GAPFILL_AB_PC3F; GAPFILL_AB_PC5R
notes: Batch 2 part 1. New category + link to a GAPFILL_ option; no REST resource (3 names gave 404), export compare is the proof. Fresh test own rows OK (compare hit a parallel run), ModuleId wording fixed, re-test PASS.
