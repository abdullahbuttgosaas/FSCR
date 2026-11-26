task_code: DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES
task_name: Manage Order Attachment Categories
module: Order Management
status: tested
filled_by: AK
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 4
waiting_minutes: 6
fresh_claude_pass: yes (F pass, no wrong sentence)
route: FSM CSV (task-level export/import)
depends_on: DOO ModuleId (read live by REST from a DOO lookup type)
test_records: FSCRT_AK_GF_AC2, FSCRT_AK_GF_ACF (plus FSCRT_AK_GF_AC1 created outside the DOO module by try 2; own test record, left in place)
notes: Own test and fresh test F passed; read back by after-export compare (0 existing changed). No wording change after F, so no re-test was needed. retest_after_wording_fix: none
