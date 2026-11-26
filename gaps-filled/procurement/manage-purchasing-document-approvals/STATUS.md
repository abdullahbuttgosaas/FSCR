task_code: PO_MANAGE_PURCHASING_DOCUMENT_APPROVALS
task_name: Manage Purchasing Document Approvals
module: Procurement
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 3
minutes_to_test: 5
waiting_minutes: 1
fresh_claude_pass: yes (round F GAPFILL_AB_B6_PO2F PASS; wording fixed after F (pending flag); re-test R GAPFILL_AB_B6_PO3R PASS, no wrong sentence)
route: REST approvalRules (POST, child conditions + actions) through rest_call.py; ids read live; helper procurement/scripts/approval_rule.py
depends_on: none (task rules upgraded from BPM: IsRulesUpgradedFlag True)
test_records: own GAPFILL_AB_B6_PO1 (participant Terms Approval Serial 3); fresh GAPFILL_AB_B6_PO2F (Terms Approval Serial 2); re-test GAPFILL_AB_B6_PO3R (Terms Approval Serial 2). All disabled, condition Document Total Amount > 999999999999, action Automatic/Rejected, pending (never deployed). REST, no ProcessId.
notes: Batch 06 (sitting 4). Same script and pattern as Manage Requisition Approvals. Own test RESULT PASS (rules 0 -> 1, only PO1). Pending rule change, never deployed or discarded; no REST delete. Suggestions NOT applied: grep hint for the 107-line attribute list; say 'rules on this participant now' can be above 0; say sign-in can be skipped with a valid cache. Where it shows: Manage Purchasing Document Approvals page.
