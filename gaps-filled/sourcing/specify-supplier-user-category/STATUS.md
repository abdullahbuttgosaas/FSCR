task_code: ORA_POZ_SPECIFY_SUP_USER_CATEGORY
task_name: Specify User Category for New Supplier Users
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
notes: Sourcing batch 04 (sitting 2). screen-only: no FSM CSV (task export refused, CSVExportImportSupportedFlag N, 2026-11-28) and no REST resource (5 names tried, all HTTP 404, 2026-11-28); it picks the Security Console user category given to new supplier user accounts; also checked: the 6 profile options of application POZ (REST profileOptions, ApplicationShortName POZ) hold no user category option. Proof (2026-11-28, read only): (1) FSCR task-level export --data for ORA_POZ_SPECIFY_SUP_USER_CATEGORY answered 'CSVExportImportSupportedFlag is N ... no setup task CSV export was created' (no ZIP). (2) REST GET ?limit=1 on fscm supplierUserCategories, fscm userCategories, fscm supplierUserCategorySettings, fscm supplierUserAccountSettings, hcm userCategories: every one HTTP 404. (3) The page is the only route found; not automated (rule: screen-only tasks are not filled). A REST name not tried could still exist (GUESS); a later release could add a CSV route.
