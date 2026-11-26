task_code: IBY_MANAGE_PAYMENT_METHODS
task_name: Manage Payment Methods
module: Payables
status: tested
filled_by: AK
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes (fresh F passed first try, no errors)
route: FSM setup CSV import, ORA_IBY_FD_PARENT_PAY_MET.csv + IBY_FD_PAYMENT_METHOD.csv (usage rows in the same package); REST read-back disbursementPaymentMethodsLOV
depends_on: -
test_records: FSCRT_AK_GF_PM1; FSCRT_AK_GF_PM1F
notes: Payables-only method with 6 "all" usage rules; translation automatic; no defaulting rule changed
