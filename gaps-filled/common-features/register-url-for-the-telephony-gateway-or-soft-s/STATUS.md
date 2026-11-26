task_code: MCT_MANAGE_TELEPHONY_SIP_DOMAIN
task_name: Register URL for the telephony gateway or soft switch for SIP domain
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
notes: Verification run 2026-11-26 (read only): 1) CSV: export 2026-11-26: task flag CSVExportImportSupportedFlag N, refused (no CSV package). 2) REST: crm telephonyDomains 404. 3) Oracle docs (3 endpoint lists read: Common Features, Financials, part of Sales; plus page searches): implementation guide: done on the page or in Topology Manager (host, port), no API. DECISION: screen-only (no CSV package that can create the record and no REST create route). Nothing was created.
