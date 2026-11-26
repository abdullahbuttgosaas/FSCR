task_code: FUN_VIEW_AVAILABLE_ASSET_BOOKS
task_name: View Available Asset Books
module: Common Features
status: screen-only
filled_by: AB
date: 2026-11-26
minutes_to_write: 2
minutes_to_test: 2
waiting_minutes: 2
fresh_claude_pass: no (screen-only)
route: none: no FSM CSV package that creates this record, no REST create route; set on the page only
depends_on: none
test_records: none (read-only checks only)
notes: Verification run 2026-11-26 (read only): 1) CSV: export 2026-11-26: task flag CSVExportImportSupportedFlag N, refused (no CSV package). 2) REST: fixedAssetBooksLOV GET 200, describe get only (VERIFIED today); setIdAssignmentsAssetBook has POST but assigns a set to a book, it does not create books. 3) Oracle docs (3 endpoint lists read: Common Features, Financials, part of Sales; plus page searches): a view task; Financials list: asset books LOV read only. DECISION: screen-only (no CSV package that can create the record and no REST create route). Nothing was created.
