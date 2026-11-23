task_code: GL_MANAGE_TRANSACTION_CALENDARS
task_name: Manage Transaction Calendars
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 3
minutes_to_test: 2
waiting_minutes: 2.5
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_TC_T1; GAPFILL_TC_T2; GAPFILL_TCF1_DEC07; GAPFILL_AB_RT_TC
notes: Batch 1 part 3. Full skill + calendar_rows.py; no REST resource, so the after-export is the read-back. Attempt 1 rejected (DayOfWeek required). Long date ranges not tested. Re-tested 2026-11-24 after the wording fix: PASS.
