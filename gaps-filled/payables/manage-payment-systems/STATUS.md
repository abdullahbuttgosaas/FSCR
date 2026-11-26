task_code: IBY_MANAGE_PAYMENT_SYSTEMS
task_name: Manage Payment Systems
module: Payables
status: failed
filled_by: AK
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 5
fresh_claude_pass: no (not run: own test failed)
route: FSM setup CSV import, IBY_PAYMENT_SYSTEM.csv + 7 child CSVs; no REST resource (404)
depends_on: an existing bank (BankName); seeded format, transmission protocol and payment scheme codes
test_records: none created (FSCRT_AK_GF_PS1 refused in every try; export after shows added 0)
notes: create refused with FND_CMN_CMPLT_FLDS "You must complete the required fields" even for an exact round trip of a working screen-created payment system (ProcessId 100004743428187), so the export lacks a field the import requires; next step: try a 10-character Suffix (FSCRT_AK_2), then compare with the task's CSV template export for mandatory attributes
