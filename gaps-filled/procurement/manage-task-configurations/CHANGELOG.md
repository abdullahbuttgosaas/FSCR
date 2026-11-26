# Changelog: Manage Task Configurations for Procurement

- 2026-11-27, batch-06 (AB with Claude, sitting 4). Status: screen-only.
- Test records: none
- Fresh test: n/a (screen-only)
- Notes: Batch 06 (sitting 4), proven screen-only 2026-11-27: (1) FSM CSV: task export refused 3 times, 'CSVExportImportSupportedFlag is N for PO_MANAGE_TASK_CONFIGURATIONS ... no setup task CSV export was created'; (2) REST GET (read only) of taskConfigurations, bpmTaskConfigurations, workflowTaskConfigurations, humanTaskConfigurations, approvalTaskConfigurations, workflowTasks, bpmTasks, taskConfiguration: all HTTP 404; (3) approvalTasks (REST) holds only rules, participants and deployment jobs, no task configuration fields (expiration, escalation, notifications, assignment); those live in BPM Worklist Task Configuration, reached from the task's page (GUESS from Oracle's docs; no Fusion REST resource found). Approval RULES of the procurement tasks are covered by the 4 Manage ... Approvals skills.
