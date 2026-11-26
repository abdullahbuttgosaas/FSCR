task_code: INV_MANAGE_TASK_CONFIGURATIONS
task_name: Manage Task Configurations for Supply Chain Management
module: Common Features
status: screen-only
filled_by: AB
date: 2026-11-26
minutes_to_write: 2
minutes_to_test: 2
waiting_minutes: 2
fresh_claude_pass: no (screen-only)
route: none: no FSM CSV package that creates this record, no REST create route; set on the page only
depends_on: none
test_records: none (read-only checks only)
notes: Verification run 2026-11-26 (read only): 1) CSV: export 2026-11-26: flag Y, 2 files; package = 2 standard lookup files, 0 rows; no task configuration object. 2) REST: taskConfigurations 404 (earlier); /bpm/api/4.0/tasks GET 200 but it is runtime worklist tasks, a different object. 3) Oracle docs (3 endpoint lists read: Common Features, Financials, part of Sales; plus page searches): workflow rules spreadsheet covers only Payables invoice and GL journal approval, not SCM task configuration. DECISION: screen-only (no CSV package that can create the record and no REST create route). Nothing was created.
