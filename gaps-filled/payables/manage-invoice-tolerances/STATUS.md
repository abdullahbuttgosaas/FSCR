task_code: AP_MANAGE_INVOICE_TOLERANCES
task_name: Manage Invoice Tolerances
module: Payables
status: tested
filled_by: AK
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 4
waiting_minutes: 3
fresh_claude_pass: yes (fresh F passed; wording and helper fixed; retest R passed with no errors)
route: FSM setup CSV import, AP_TOLERANCE_TEMPLATE.csv (business object Invoice Tolerance Set); REST read-back payablesInvoiceTolerances
depends_on: -
test_records: FSCRT_AK_GF_TOL1; FSCRT_AK_GF_TOL1F; FSCRT_AK_GF_TOL1R
notes: stand-alone; QUANTITY BASED verified live, AMOUNT BASED columns still GUESS
