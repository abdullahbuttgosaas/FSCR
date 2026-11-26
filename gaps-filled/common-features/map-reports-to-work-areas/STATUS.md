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
notes: unsafe to test: a mapping shows the report in the work area's Reports and Analytics panel to every user. Export VERIFIED (11 work area rows, 13 report rows; child report file has no parent key column). Build/import GUESS. Next step: load-test only on an environment we own, with a report nobody uses. Re-judged 2026-11-25 (sitting 4, new unsafe rule): a mapping has no name or owner: any new mapping row shows a report in a seeded work area to every user, and the CSV route cannot remove it again (no delete), so no new-record or test-and-restore way exists. Stays written. Re-judged 2026-11-26 (sitting 7): still unsafe, no new safe route (every mapping shows to all users of the work area). Re-judged 2026-11-26 (sitting 8): still unsafe: a mapping is not a named new record (it changes what every user of a seeded work area sees) and cannot be removed by CSV, so neither a new-record nor a test-and-restore way exists.
