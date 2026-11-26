task_code: ORA_QP_MANAGE_PRICING_TOTALS_DEFINITIONS
task_name: Manage Pricing Totals
module: Order Management
status: tested
filled_by: AK
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 4
waiting_minutes: 5
fresh_claude_pass: yes (F pass, no wrong sentence)
route: FSM CSV (task-level export/import)
depends_on: an existing pricing algorithm (referenced by name)
test_records: FSCRT_AK_GF_TOA, FSCRT_AK_GF_TOF (FSCRT_AK_GF_TO1 refused, nothing created)
notes: Own test and fresh test F passed; read back by after-export compare (0 existing changed). No wording change after F, so no re-test was needed. retest_after_wording_fix: none
