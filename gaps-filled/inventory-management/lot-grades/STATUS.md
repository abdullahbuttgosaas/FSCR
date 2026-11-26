task_code: INV_MANAGE_LOT_GRADES
task_name: Manage Lot Grades
module: Inventory Management
status: tested
filled_by: HF (Claude, Opus)
date: 26/11/2026
minutes_to_write: 3
minutes_to_test: 8
waiting_minutes: 7
fresh_claude_pass: yes (4 fresh runs: F, R, R2 and R3 all passed; R2 and R3 reported no wrong sentence)
route: FSM CSV (task-level export and import)
depends_on: none
test_records: FSCRT_HF_GF_LG1, FSCRT_HF_GF_LG1F, FSCRT_HF_GF_LG1R, FSCRT_HF_GF_LG2R, FSCRT_HF_GF_LG3R
notes: Own test ProcessId 100004744431804; fresh tests 100004744435059 (F), 100004744435197 (R), 100004744433685 (R2), 100004744435515 (R3). Read back by export compare (existing changed 0) and REST: inventoryLotGrades (count 1). Minutes are batch shares (5 tasks run in parallel).
