task_code: XLE_SEARCH_LEGAL_REPORTING_UNITS
task_name: Search Legal Reporting Units
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 2
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV export (read only) + REST legalReportingUnitsLOV
depends_on: none
test_records: none created (view/search task); looked up existing units: live 28Vision America, fresh test N24Vision America
notes: Batch 05. View/search task: test = read-back of an existing unit (REST + export) by a fresh Claude. Uses search-legal-entities/scripts/view_record.py. Fresh test PASS first time; tester notes are suggestions, not applied.
