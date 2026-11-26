task_code: XLE_MANAGE_INTERCOMPANY_EXCEPTIONS
task_name: Manage Intercompany Exceptions
module: Common Features
status: screen-only
filled_by: AB
date: 2026-11-26
minutes_to_write: 3
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: no (screen-only: the CSV package has no record for this task)
route: none: no FSM CSV package that creates this record, no REST create route; set on the page only
depends_on: an existing legal entity (XLE_SEARCH_LEGAL_ENTITIES reads it)
test_records: none
notes: Verification run 2026-11-26 (read only): 1) CSV: export 2026-11-26: flag Y, 7 files; package = legal entity package (7 files: entity, establishment, registrations, address); no intercompany exception file or column. 2) REST: Financials endpoint list read: intercompanyAgreements and intercompanyTransactionSourceDocuments are transactions, intercompany*LOV read only; intercompanyExceptions 404 (earlier). 3) Oracle docs (3 endpoint lists read: Common Features, Financials, part of Sales; plus page searches): Intercompany Transaction Import (FBDI) covers transactions, not exceptions. DECISION: screen-only (no CSV package that can create the record and no REST create route). Nothing was created.
