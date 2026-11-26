task_code: WSH_MANAGE_SHIPPING_COST_TYPES
task_name: Manage Shipping Cost Types
module: Inventory Management
status: tested
filled_by: HF (Claude, Opus)
date: 26/11/2026
minutes_to_write: 4
minutes_to_test: 9
waiting_minutes: 9
fresh_claude_pass: yes (4 fresh runs: F, R, R2 and R3 all passed; R2 and R3 reported no wrong sentence)
route: FSM CSV (task-level export and import)
depends_on: WSH_MANAGE_SHIPPING_LOOKUPS (seeded freight cost type codes; nothing to create)
test_records: FSCRT_HF_GF_SCT1, FSCRT_HF_GF_SCT1F, FSCRT_HF_GF_SCT1R, FSCRT_HF_GF_SCT2R, FSCRT_HF_GF_SCT3R
notes: Own test ProcessId 100004743455953; fresh tests 100004744433483 (F), 100004744435209 (R), 100004744435268 (R2), 100004743458601 (R3). Read back by export compare (existing changed 0) and REST: none (no REST resource). Minutes are batch shares (5 tasks run in parallel).
