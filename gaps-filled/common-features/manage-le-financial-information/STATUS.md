task_code: XLE_MANAGE_LEGAL_ENTITY_FINANCIAL_INFORMATION
task_name: Manage Legal Entity Financial Information
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 7
waiting_minutes: 5
fresh_claude_pass: yes
route: FSM CSV (XLE_ENTITY_PROFILE): update own row
depends_on: a legal entity (test: test-legal-entity skill)
test_records: GAPFILL_AB_B14_LE1 ActivityCode 541511 (100004743429645; refused try 100004743429588); fresh LE2F (100004744413318); re-test LE3R (100004744415193)
notes: Batch 14 (sitting 6). ActivityCode must be a NAICS 1997 code; the package must come from this task's own export (a Manage Legal Entity package gives HTTP 400). Own test PASS (other rows changed 0). Fresh test PASS on LE2F, wording fixed, re-test PASS on LE3R.
