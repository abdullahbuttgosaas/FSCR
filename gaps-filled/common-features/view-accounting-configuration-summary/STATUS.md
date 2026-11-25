task_code: GL_VIEW_ACCOUNTING_CONFIGURATION_SUMMARY
task_name: View Accounting Configuration Summary
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 4
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV export (read only) + REST ledgersLOV, chartOfAccountsLOV
depends_on: none
test_records: none created (view task); looked up existing ledgers: live 28Ledger US, fresh test MG Primary ledger, re-test AKLedger IN
notes: Batch 05. View task: test = read-back of an existing ledger (REST + export) by a fresh Claude. Fresh test PASS but found a wrong sentence (GL_PRIMARY_LEDGER rows also hold reporting-currency ledgers); fixed with relationship flag/level wording, full COA command, timings, and re-tested: PASS (AKLedger IN).
