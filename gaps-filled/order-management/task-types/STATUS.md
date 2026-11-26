task_code: DOO_MANAGE_TASK_TYPES
task_name: Manage Task Types
module: Order Management
status: tested
filled_by: AK
date: 2026-11-26
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 6
fresh_claude_pass: yes (F pass; wording fixed; R pass)
route: FSM CSV (task-level export/import)
depends_on: none
test_records: FSCRT_AK_GF_TT1, FSCRT_AK_GF_TTF, FSCRT_AK_GF_TTR (each with services Create and Inbound)
notes: Own test, fresh test F and re-test R after wording fixes all passed; read back by after-export compare (0 existing changed). retest_after_wording_fix: done
