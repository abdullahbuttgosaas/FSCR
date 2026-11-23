task_code: FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_CATEGORIES
task_name: Manage Applications Core Attachment Categories
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 2
minutes_to_test: 3
waiting_minutes: 1.5
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_ATC_T1; GAPFILL_ATCF1_A1
notes: Batch 1 part 3. Card over FSCR attachments skill. No REST resource (5 names 404), so the after-export is the read-back. Entity links not tested.
