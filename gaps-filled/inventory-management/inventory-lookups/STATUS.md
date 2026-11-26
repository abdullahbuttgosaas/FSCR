task_code: INV_MANAGE_INVENTORY_LOOKUPS
task_name: Manage Inventory Lookups
module: Inventory Management
status: tested
filled_by: HF (Claude, Opus)
date: 26/11/2026
minutes_to_write: 5
minutes_to_test: 9
waiting_minutes: 9
fresh_claude_pass: yes (F and R passed; R reported no wrong sentence)
route: FSM CSV (task-level export and import)
depends_on: none
test_records: FSCRT_HF_GF_LK1, FSCRT_HF_GF_LK1F, FSCRT_HF_GF_LK1R
notes: Own test ProcessId 100004744436620; fresh tests 100004744435460 (F), 100004744435537 (R). Read back by export compare (existing changed 0) and REST: standardLookups/<type>/child/lookupCodes (count 1). Minutes are batch shares (5 tasks run in parallel).
