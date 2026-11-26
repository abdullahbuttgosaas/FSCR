task_code: ORA_PO_MANAGE_WORK_CONFIRMATION_APPROVALS
task_name: Manage Work Confirmation Approvals
module: Procurement
status: written
filled_by: AB
date: 2026-11-27
minutes_to_write: 2
minutes_to_test: 1
waiting_minutes: 1
fresh_claude_pass: n/a (unsafe to test on the shared environment: the task's rules are not upgraded from BPM)
route: REST approvalRules (same script as Requisition / Purchasing Document Approvals); refused here with POR-2011627
depends_on: the task's approval rules upgraded from BPM (one-time, shared action on the task's page)
test_records: none: GAPFILL_AB_B6_WC1 on participant Preapproval Serial refused HTTP 400 POR-2011627 (not created; participant rules 0)
notes: Batch 06 (sitting 4). Written, unsafe to test: approvalTasks shows IsRulesUpgradedFlag False for this task; Oracle refuses every new rule with POR-2011627 'You can't create approval rules until the rules for the approval task have been upgraded from BPM'. The upgrade is a one-time action on the task's page that switches the rule source for everyone; REST has no upgrade action and the only way back (clearApprovalRules) deletes the task's rules, so it cannot be put back. Steps 1-2 (reads, dry run) VERIFIED on this task; the POST and read-back are VERIFIED on Requisition and Purchasing Document Approvals. Safe when: the task is already upgraded (another environment) or the approval-setup owner upgrades it on purpose; then run the skill unchanged. Not screen-only (the REST route exists and works on upgraded tasks).
