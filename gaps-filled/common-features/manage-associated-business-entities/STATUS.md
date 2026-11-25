task_code: XLE_MANAGE_ASSOCIATED_BUSINESS_ENTITIES
task_name: Manage Associated Business Entities
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 7
minutes_to_test: 12
waiting_minutes: 6
fresh_claude_pass: yes
route: FSM CSV (XLE_ASSOCIATION): new row
depends_on: a reporting unit and a business unit with a location (test: test-legal-entity, test-business-unit)
test_records: GAPFILL_AB_B14_LE1 -> GAPFILL_AB_B15_BU3 (100004743433629; refused tries 100004743430787, 100004743434305); fresh GAPFILL_AB_B14_LE2F -> GAPFILL_AB_B15_BU4F (100004743435423); re-test GAPFILL_AB_B14_LE3R -> GAPFILL_AB_B15_BU5R (100004743432818)
notes: Batch 15 (sitting 6). New prerequisite skill test-business-unit (BU1, BU3). The business unit needs a location and BusinessEntityAddress must be three spaces, else XLE_ASSOC_OBJECT_ID_REQUIRED. Own test PASS (3 -> 4 rows). Fresh test PASS (BU4F), wording fixed in this skill and test-business-unit, re-test PASS (BU5R).
