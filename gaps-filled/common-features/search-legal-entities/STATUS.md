task_code: XLE_SEARCH_LEGAL_ENTITIES
task_name: Search Legal Entities
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 4
waiting_minutes: 2
fresh_claude_pass: yes
route: FSM CSV export (read only) + REST legalEntitiesLOV
depends_on: none
test_records: none created (view/search task); looked up existing legal entities: live 28Vision America, fresh test PPVision America, re-test 28Vision Corporate HQ
notes: Batch 05. View/search task: nothing to create, so the test is a read-back of an existing record (REST + export) by a fresh Claude. New helper scripts/view_record.py (hides audit and person columns). Wording fixed after the fresh test (match-cols so other entities' rows sharing a registration number are not shown, success signal, file names) and re-tested: PASS (retest R on 28Vision Corporate HQ).
