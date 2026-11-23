task_code: ORA_ZX_MANAGE_WITHHOLDING_TAX_CALENDARS
task_name: Manage Withholding Tax Calendars
module: Common Features
status: tested
filled_by: AB
date: 2026-11-23
minutes_to_write: 5
minutes_to_test: 4
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_WHT1; GAPFILL_AB_WT3R
notes: Batch 2 part 2. New GENERAL monthly calendar + 12 periods (AP_OTHER_PERIOD_TYPE/PERIOD); new helper scripts/period_rows.py. No REST resource; export compare with 13 expects is the read-back. Fresh test 1 FAILED on a skill bug (CalendarName max 15, JBO-27040; nothing created); wording fixed, re-test PASS (no wording change after it).
