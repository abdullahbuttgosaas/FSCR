task_code: INV_MANAGE_MATERIAL_STATUSES
task_name: Manage Material Statuses
module: Inventory Management
status: tested
filled_by: HF (Claude, Opus)
date: 26/11/2026
minutes_to_write: 6
minutes_to_test: 10
waiting_minutes: 9
fresh_claude_pass: yes (F and R passed; R reported no wrong sentence)
route: FSM CSV (task-level export and import)
depends_on: INV_MANAGE_INVENTORY_TRANSACTION_SOURCES_AND_TYPES (seeded status-controlled types; nothing to create)
test_records: FSCRT_HF_GF_MS1, FSCRT_HF_GF_MS1F, FSCRT_HF_GF_MS1R
notes: Own test ProcessId 100004744435347; fresh tests 100004743458194 (F), 100004744435568 (R). Read back by export compare (existing changed 0) and REST: inventoryMaterialStatuses (count 1). Minutes are batch shares (5 tasks run in parallel).
