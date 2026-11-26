task_code: DOO_MANAGE_STATUS_VALUES
task_name: Manage Status Values
module: Order Management
status: tested
filled_by: AK
date: 2026-11-26
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 6
fresh_claude_pass: yes (F pass; wording fixed; R pass)
route: FSM CSV (task-level export/import); no REST resource (orchestrationStatusValues 404)
depends_on: none
test_records: FSCRT_AK_GF_ST1, FSCRT_AK_GF_STF, FSCRT_AK_GF_STR
notes: Own test, fresh test F and re-test R after wording fixes all passed; read back by after-export compare (0 existing changed) and REST. retest_after_wording_fix: done
