task_code: ORA_OKC_MANAGE_TIME_UNIT_MAPPINGS
task_name: Manage Time Unit Mappings
module: Order Management
status: tested
filled_by: AK
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 4
waiting_minutes: 5
fresh_claude_pass: yes (F pass, no wrong sentence)
route: REST unitsOfMeasure (prerequisite POST) + FSM CSV mapping
depends_on: a new test unit of measure of class Time (created by REST in the skill)
test_records: units ZK1 (FSCRT_AK_GF_U1), ZKF (FSCRT_AK_GF_UF); mappings FSCRT_AK_GF_TU1, FSCRT_AK_GF_TUF
notes: Own test and fresh test F passed; read back by after-export compare (0 existing changed) and REST. No wording change after F, so no re-test was needed. retest_after_wording_fix: none
