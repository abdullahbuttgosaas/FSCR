task_code: PO_MANAGE_TASK_CONFIGURATIONS
task_name: Manage Task Configurations for Procurement
module: Procurement
status: screen-only
filled_by: AB
date: 2026-11-27
minutes_to_write: 0
minutes_to_test: 2
waiting_minutes: 3
fresh_claude_pass: n/a (screen-only)
route: none: no FSM CSV, no REST resource
depends_on: none
test_records: none
notes: Batch 06 (sitting 4), proven screen-only 2026-11-27: (1) FSM CSV: task export refused 3 times, 'CSVExportImportSupportedFlag is N for PO_MANAGE_TASK_CONFIGURATIONS ... no setup task CSV export was created'; (2) REST GET (read only) of taskConfigurations, bpmTaskConfigurations, workflowTaskConfigurations, humanTaskConfigurations, approvalTaskConfigurations, workflowTasks, bpmTasks, taskConfiguration: all HTTP 404; (3) approvalTasks (REST) holds only rules, participants and deployment jobs, no task configuration fields (expiration, escalation, notifications, assignment); those live in BPM Worklist Task Configuration, reached from the task's page (GUESS from Oracle's docs; no Fusion REST resource found). Approval RULES of the procurement tasks are covered by the 4 Manage ... Approvals skills.
