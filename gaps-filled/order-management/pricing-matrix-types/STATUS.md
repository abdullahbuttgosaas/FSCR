task_code: ORA_QP_MANAGE_PRICING_MATRIX_TYPES
task_name: Manage Pricing Matrix Types
module: Order Management
status: tested
filled_by: AK
date: 2026-11-26
minutes_to_write: 4
minutes_to_test: 6
waiting_minutes: 6
fresh_claude_pass: yes (F pass; wording fixed; R pass)
route: FSM CSV load; REST pricingMatrixTypes read-back
depends_on: a dynamic matrix class (seeded; read by name)
test_records: FSCRT_AK_GF_MT1, FSCRT_AK_GF_MTF, FSCRT_AK_GF_MTR (inactive)
notes: Own test, fresh test F and re-test R after wording fixes all passed; read back by after-export compare (0 existing changed) and REST. retest_after_wording_fix: done
