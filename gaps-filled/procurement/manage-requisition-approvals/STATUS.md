task_code: POR_MANAGE_REQUISITION_APPROVALS
task_name: Manage Requisition Approvals
module: Procurement
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 6
minutes_to_test: 8
waiting_minutes: 2
fresh_claude_pass: yes (round F GAPFILL_AB_B6_RQ2F PASS; testers' notes on the pending flag fixed in wording; re-test R GAPFILL_AB_B6_RQ3R PASS, no wrong sentence)
route: REST approvalRules (POST, child conditions + actions) through rest_call.py; ids read live from approvalTasks, participants, approvalAttributesLOV; helper procurement/scripts/approval_rule.py
depends_on: none (task rules upgraded from BPM: IsRulesUpgradedFlag True)
test_records: own GAPFILL_AB_B6_RQ1 (participant Header Hierarchy, RuleId read back); fresh GAPFILL_AB_B6_RQ2F (Header Consensus); re-test GAPFILL_AB_B6_RQ3R (Header Hierarchy 3). All disabled, condition Requisition Amount > 999999999999, action Automatic/Rejected, pending (never deployed). REST, no ProcessId.
notes: Batch 06 (sitting 4). Re-judged from 'later': a NEW disabled prefix rule is not unsafe. Own tries: ConditionTypeCode/ActionNumber and ConditionAttributeKey 'cannot be set' (HTTP 400, nothing created); ConditionAttributeId works. Rules GET needs q=ParticipantId (POR-2011550); Task and AttributeKey not queriable. REST create = pending rule change (task HasPendingRuleChangesFlag True); no deploy, no discard (discard would drop others' pending changes); no DELETE in REST. Fresh F notes fixed (flag may already be True; mkdir RUN; --prefix meaning; 401 grep; grep hint) and re-tested. Suggestions NOT applied: grep hint for the attribute list; note KEY needs DIM; mkdir line inside Step 1. Where it shows: Manage Requisition Approvals page (rule list of the participant, pending changes).
