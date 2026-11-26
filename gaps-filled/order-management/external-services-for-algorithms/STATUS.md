task_code: ORA_QP_MANAGE_EXT_SERVICES_FOR_ALGORITHMS
task_name: Manage External Service Details for Algorithms
module: Order Management
status: tested
filled_by: AK
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 4
waiting_minutes: 6
fresh_claude_pass: yes (F pass, no wrong sentence)
route: FSM CSV load; REST omWebServiceDefinitions read-back
depends_on: an existing source system (referenced by name); lookups ORA_DOO_INVOCATION_MODE, ORA_DOO_RESPONSE_PROCESS_OPTNS
test_records: FSCRT_AK_GF_WS1, FSCRT_AK_GF_WSF
notes: Own test and fresh test F passed; read back by after-export compare (0 existing changed) and REST. No wording change after F, so no re-test was needed. retest_after_wording_fix: none
