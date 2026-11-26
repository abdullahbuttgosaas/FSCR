task_code: ORA_PJF_MANAGE_USER_DEFINED_RULES
task_name: Manage User-Defined Rules for Project Management
module: Common Features
status: written
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 0
waiting_minutes: 2
fresh_claude_pass: not run (unsafe)
route: FSM CSV package (BPM rule upload set, 11 files, 0 rows, export VERIFIED 2026-11-26); REST projectUserDefinedRules 404
depends_on: none
test_records: none
notes: Batch 21 (sitting 9). unsafe to test: a rule upload replaces a project workflow's whole approval rule set (no single new record), changing approvals for every project user; no existing rule to copy (0 rows).
