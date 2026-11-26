task_code: IBY_MANAGE_PAYMENT_CODES
task_name: Manage Payment Codes
module: Payables
status: tested
filled_by: AK
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes (fresh F passed first try, no errors)
route: FSM setup CSV import, IBY_PAYMENT_CODE.csv (US translation automatic); REST read-back paymentCodesLOV
depends_on: -
test_records: FSCRT_AK_GF_PR1; FSCRT_AK_GF_PR1F
notes: EndDate is required (4712/12/31 = no end); PAYMENT_REASON verified, other types same columns (GUESS)
