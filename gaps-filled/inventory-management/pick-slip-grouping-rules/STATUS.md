task_code: INV_MANAGE_PICK_SLIP_GROUPING_RULES
task_name: Manage Pick Slip Grouping Rules
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
test_records: FSCRT_HF_GF_PSG1, FSCRT_HF_GF_PSG1F, FSCRT_HF_GF_PSG1R
notes: Own test ProcessId 100004744433919; fresh tests 100004744436942 (F), 100004743460112 (R). Read back by export compare (existing changed 0) and REST: pickSlipGroupingRules (count 1). Minutes are batch shares (5 tasks run in parallel).
