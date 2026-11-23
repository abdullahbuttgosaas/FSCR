task_code: FND_MANAGE_DOCUMENT_SEQUENCES
task_name: Manage Document Sequences
module: Common Features
status: tested
filled_by: AB
date: 2026-11-23
minutes_to_write: 5
minutes_to_test: 6
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_DS1; GAPFILL_AB_DS2F; GAPFILL_AB_DS3R
notes: Batch 2 part 2. New type A document sequence without an assignment; ApplicationId, ModuleId and TableName copied together from one existing type A row. REST documentSequences before-read and read-back + export compare. Fresh test PASS, wording fixed, re-test PASS (no wording change after it).
