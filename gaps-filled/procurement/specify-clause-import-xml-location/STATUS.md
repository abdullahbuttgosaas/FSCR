task_code: OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_PROFILES
task_name: Specify Contract Clause Import XML File Location
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 6
waiting_minutes: 4
fresh_claude_pass: yes (test-and-restore; no wrong sentence)
route: FSM CSV (profile package, option OKC_CLAUSE_IMP_FILE_LOCATION, app 510) + REST profileOptions read-back
depends_on: none
test_records: no new record (test-and-restore of the SITE value). Own: set 100004744391334, restore 100004744391355. Fresh: NEWDIR /usr/tmp/gapfill_ab_f3/ set 100004744396393, restore 100004744395169; SITE back to /usr/tmp/
notes: Batch 02. Shared site setting, tested only as test-and-restore. Own test hit the Git Bash path rewrite (value stored with a Windows prefix) -> MSYS_NO_PATHCONV=1 rule; restore proved SAME: PASS. Fresh test PASS (read-back = NEWDIR exactly, restore SAME: PASS). Suggestions NOT applied: 'CSVs may be empty' is misleading (fresh run had 1+3+1 rows; REST stays the source); send rest_call output to a file; say the restore ProcessId can be lower.
