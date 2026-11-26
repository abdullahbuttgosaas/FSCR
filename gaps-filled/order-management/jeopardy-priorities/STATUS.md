task_code: DOO_MANAGE_JEOPARDY_PRIORITIES
task_name: Manage Jeopardy Priorities
module: Order Management
status: tested
filled_by: AK
date: 2026-11-26
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 6
fresh_claude_pass: yes (F pass; wording fixed; R pass)
route: FSM CSV (task-level export/import); no REST resource (jeopardyPriorities 404)
depends_on: none
test_records: FSCRT_AK_GF_JP1 (1000-1010), FSCRT_AK_GF_JPF (1020-1030), FSCRT_AK_GF_JPR (1040-1050)
notes: Own test, fresh test F and re-test R after wording fixes all passed; read back by after-export compare (0 existing changed) and REST. retest_after_wording_fix: done
