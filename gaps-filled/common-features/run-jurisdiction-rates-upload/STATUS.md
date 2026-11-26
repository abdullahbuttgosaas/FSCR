task_code: ORA_ZX_RUN_JURISDICTION_AND_RATES_UPLOAD_PROGRAM
task_name: Run Jurisdiction and Rates Upload Program
module: Common Features
status: written
filled_by: AB
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 0
waiting_minutes: 2
fresh_claude_pass: not run (unsafe)
route: scheduled process Import Tax Configuration Content (Oracle docs) through REST fscm erpintegrations (create, get; describe VERIFIED); no FSM CSV (export refused)
depends_on: a tax partner content file from the customer's licence
test_records: none
notes: Batch 20 (sitting 9). unsafe to test: loads a partner's full content file into the shared US tax regime, jurisdictions, rates and master geography; updates existing records; no undo; needs the customer's licensed file.
