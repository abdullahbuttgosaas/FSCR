task_code: ORA_CJM_MANAGE_PROGRAM_TYPES
task_name: Manage Channel Program Types
module: Order Management
status: tested
filled_by: AK
date: 2026-11-26
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 6
fresh_claude_pass: yes (F pass; wording fixed; R pass)
route: FSM CSV load; REST channelProgramTypes read-back
depends_on: a seeded program template (e.g. SUPPLIER_REBATE)
test_records: FSCRT_AK_GF_PT1, FSCRT_AK_GF_PTF, FSCRT_AK_GF_PTR (Draft, Supplier Rebate, each with 2 qualifiers)
notes: Own test, fresh test F and re-test R after wording fixes all passed; read back by after-export compare (0 existing changed) and REST. retest_after_wording_fix: done
