task_code: INV_MANAGE_LOT_EXPIRATION_ACTIONS
task_name: Manage Lot Expiration Actions
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
test_records: FSCRT_HF_GF_LEA1, FSCRT_HF_GF_LEA1F, FSCRT_HF_GF_LEA1R, FSCRT_HF_GF_LEA2R, FSCRT_HF_GF_LEA3R
notes: Own test ProcessId 100004743456540; fresh tests 100004744433492 (F), 100004744436085 (R), 100004743456900 (R2), 100004743457232 (R3). Read back by export compare (existing changed 0) and REST: none (no REST resource). Minutes are batch shares (5 tasks run in parallel).
