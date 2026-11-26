task_code: WSH_MANAGE_RELEASE_SEQUENCE_RULES
task_name: Manage Release Sequence Rules
module: Inventory Management
status: tested
filled_by: HF (Claude, Opus)
date: 26/11/2026
minutes_to_write: 4
minutes_to_test: 9
waiting_minutes: 9
fresh_claude_pass: yes (4 fresh runs: F, R, R2 and R3 all passed; R2 and R3 reported no wrong sentence)
route: FSM CSV (task-level export and import)
depends_on: none
test_records: FSCRT_HF_GF_RSR1, FSCRT_HF_GF_RSR1F, FSCRT_HF_GF_RSR1R, FSCRT_HF_GF_RSR2R, FSCRT_HF_GF_RSR3R
notes: Own test ProcessId 100004744434147; fresh tests 100004744434457 (F), 100004744433597 (R), 100004744436226 (R2), 100004744435524 (R3). Read back by export compare (existing changed 0) and REST: none (no REST resource). Minutes are batch shares (5 tasks run in parallel).
