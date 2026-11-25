task_code: PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION
task_name: Configure Procurement Business Function
module: Procurement
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 2
waiting_minutes: 2
fresh_claude_pass: n/a (unsafe to test: changes a live BU's setup)
route: FSM CSV (PO_SYSTEM_PARAMETER per BU, document types, negotiation contract text) --edit-row
depends_on: an existing procurement BU
test_records: none (package built offline, not imported)
notes: Batch 03. Written, unsafe to test. Unsafe to test: every row is a live business unit's setup; the agent permission check blocked a test-and-restore import (2026-11-25) as an unwanted change to an existing BU. Package built offline only. Export: PO_SYSTEM_PARAMETER 14 rows x 123 columns, PO_DOCUMENT_TYPE 84, PON_CONTRACTS 2.
