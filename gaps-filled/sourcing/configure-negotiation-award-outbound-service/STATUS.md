task_code: ORA_PON_CONFIGURE_OUTBOUND_PURCHASING_SERVICE
task_name: Configure Negotiation Award Outbound Service
module: Sourcing and Supplier Management
status: screen-only
filled_by: AB
date: 2026-11-28
minutes_to_write: 2
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: n/a (screen-only, nothing loaded)
route: none (page only)
depends_on: none
test_records: none
notes: Sourcing batch 04 (sitting 2). screen-only: no FSM CSV (task export refused, CSVExportImportSupportedFlag N, 2026-11-28) and no REST resource (5 names tried, all HTTP 404, 2026-11-28); it sets the web service endpoint (and its credentials) that sends negotiation awards to an external purchasing application. Proof (2026-11-28, read only): (1) FSCR task-level export --data for ORA_PON_CONFIGURE_OUTBOUND_PURCHASING_SERVICE answered 'CSVExportImportSupportedFlag is N ... no setup task CSV export was created' (no ZIP). (2) REST GET ?limit=1 on negotiationAwardOutboundServices, sourcingOutboundServices, outboundPurchasingServices, negotiationOutboundServices, supplierNegotiationAwardServices: every one HTTP 404. (3) The page is the only route found; not automated (rule: screen-only tasks are not filled). A REST name not tried could still exist (GUESS); a later release could add a CSV route.
