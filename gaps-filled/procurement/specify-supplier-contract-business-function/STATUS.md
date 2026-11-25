task_code: OKC_SPECIFY_PROCUREMENT_CONTRACT_MGMT_BUSINESS_FUNC_PROP
task_name: Specify Supplier Contract Management Business Function Properties
module: Procurement
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 2
waiting_minutes: 2
fresh_claude_pass: n/a (unsafe to test: changes a live BU's setup)
route: FSM CSV (OKC_BU_IMPL_OPTIONS, one row per BU) --edit-row
depends_on: an existing BU with contract options
test_records: none (package built offline, not imported)
notes: Batch 03. Written, unsafe to test. Unsafe to test: every row is a live business unit's setup; the agent permission check blocked a test-and-restore import (2026-11-25) as an unwanted change to an existing BU. Package built offline only. Export: OKC_BU_IMPL_OPTIONS 1 row.
