task_code: ORA_FND_MANAGE_ROLES_TO_SYNCHRONIZE
task_name: Migrate Enterprise Roles and Assignments to PaaS Identity Store
module: Common Features
status: screen-only
filled_by: AB
date: 2026-11-26
minutes_to_write: 2
minutes_to_test: 2
waiting_minutes: 2
fresh_claude_pass: no (screen-only: no CSV package and no REST resource to test)
route: none: no FSM CSV package that creates this record, no REST create route; set on the page only
depends_on: none
test_records: none (read-only checks only)
notes: Verification run 2026-11-26 (read only): 1) CSV: export 2026-11-26: task flag CSVExportImportSupportedFlag N, refused (no CSV package). 2) REST: fscm roleSynchronizations, hcm roles 404; SCIM Roles has no POST. 3) Oracle docs (3 endpoint lists read: Common Features, Financials, part of Sales; plus page searches): Oracle docs (synchronize user identities and roles with a PaaS account): roles are picked on the page, limit profile FND_ROLE_SYNC_MAX_SELECTED_ROLES_SIZE. DECISION: screen-only (no CSV package that can create the record and no REST create route). Nothing was created.
