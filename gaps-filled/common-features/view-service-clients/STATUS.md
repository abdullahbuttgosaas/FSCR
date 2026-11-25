task_code: FUN_VIEW_SERVICE_CLIENTS
task_name: View Service Clients
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 2
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV export (read only) + REST finBusinessUnitsLOV
depends_on: none
test_records: none created (view task); looked up existing business units: live GoSaaS Labs PK, fresh test AKBusiness Unit Corporate
notes: Batch 05. View task: test = read-back of an existing BU's provider relationships (REST + export) by a fresh Claude. view_record.py hides person columns (FUN_BUSINESS_UNIT.csv holds manager names). Fresh test PASS; notes are suggestions, not applied.
