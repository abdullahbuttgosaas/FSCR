task_code: INV_MANAGE_PICKING_RULES
task_name: Manage Picking Rules
module: Inventory Management
status: tested
filled_by: HF (Claude, Opus)
date: 26/11/2026
minutes_to_write: 4
minutes_to_test: 8
waiting_minutes: 7
fresh_claude_pass: yes (F and R passed; R reported no wrong sentence)
route: FSM CSV (task-level export and import)
depends_on: none
test_records: FSCRT_HF_GF_PR1, FSCRT_HF_GF_PR1F, FSCRT_HF_GF_PR1R
notes: Own test ProcessId 100004743457097; fresh tests 100004743459117 (F), 100004743458585 (R). Read back by export compare (existing changed 0) and REST: none (pickingRules returns 404). Minutes are batch shares (5 tasks run in parallel).
