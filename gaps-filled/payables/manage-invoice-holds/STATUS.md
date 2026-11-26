task_code: AP_MANAGE_INVOICE_HOLDS_AND_RELEASES
task_name: Manage Invoice Holds and Releases
module: Payables
status: tested
filled_by: AK
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 5
waiting_minutes: 3
fresh_claude_pass: yes (fresh F passed; wording fixed; retest R passed with no errors)
route: FSM setup CSV import, AP_HOLD_CODE.csv (business object Approval Code); no REST resource (404)
depends_on: -
test_records: FSCRT_AK_GF_HLD1; FSCRT_AK_GF_HLD1F; FSCRT_AK_GF_HLD1R
notes: stand-alone; read-back by export compare (109 -> 112 rows, only the 3 test rows added)
