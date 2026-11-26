task_code: AP_MANAGE_AGING_PERIODS
task_name: Manage Aging Periods
module: Payables
status: tested
filled_by: AK
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 3
waiting_minutes: 3
fresh_claude_pass: yes (fresh F passed, no errors)
route: FSM setup CSV import, AP_AGING_PERIOD.csv + AP_AGING_PERIOD_LINE.csv (header + lines in one package); no REST resource (404)
depends_on: -
test_records: FSCRT_AK_GF_AGE1; FSCRT_AK_GF_AGE1F
notes: stand-alone; the import log counts only the header, the export compare proves the lines
