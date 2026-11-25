task_code: XLE_MANAGE_LEGAL_REPORTING_UNIT_FINANCIAL_INFORMATION
task_name: Manage Legal Reporting Unit Financial Information
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 5
minutes_to_test: 5
waiting_minutes: 4
fresh_claude_pass: yes
route: FSM CSV (XLE_ETB_PROFILE with parent XLE_ENTITY_PROFILE row): update own row
depends_on: a reporting unit (test: main unit of a test legal entity)
test_records: GAPFILL_AB_B14_LE1 unit ActivityCode (100004743429712); fresh LE2F (100004743432273); re-test LE3R (100004744414665)
notes: Batch 14 (sitting 6). Child row needs its parent legal entity profile row unchanged in the package (copied from a fresh export). Own test PASS (other rows changed 0). Fresh test PASS on LE2F, wording fixed, re-test PASS on LE3R.
