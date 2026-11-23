task_code: FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES
task_name: Manage Document Sequence Categories
module: Common Features
status: tested
filled_by: AB
date: 2026-11-20
minutes_to_write: 4
minutes_to_test: 3
waiting_minutes: 1
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_DSC_T1; GAPFILL_DSCF1_FRESH1
notes: Batch 1 part 3. Full skill + 5 generic FSM helpers used by 4 other skills; read back by REST and export compare. Records sit on the GL journal header table. --json-out option added to a helper after the fresh test (option only).
