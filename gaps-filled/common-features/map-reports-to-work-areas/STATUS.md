task_code: ATK_DEFINE_REPORT_MAPPING
task_name: Map Reports to Work Areas
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: no
route: FSM CSV (ATK_RPANE_REPORT_MAPPING + ORA_REPORTS_AND_ANALYTICS_MAPPING_REPORT)
depends_on: an existing BI catalog report and work area
test_records: none (not loaded)
notes: unsafe to test: a mapping shows the report in the work area's Reports and Analytics panel to every user. Export VERIFIED (11 work area rows, 13 report rows; child report file has no parent key column). Build/import GUESS. Next step: load-test only on an environment we own, with a report nobody uses.
