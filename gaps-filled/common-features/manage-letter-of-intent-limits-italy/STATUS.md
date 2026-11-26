task_code: ORA_JE_MANAGE_EXEMPTION_LIMITS_FOR_ITALY
task_name: Manage Letter of Intent Limits for Italy
module: Common Features
status: failed
filled_by: AB
date: 2026-11-26
minutes_to_write: 3
minutes_to_test: 3
waiting_minutes: 3
fresh_claude_pass: not run (export refused)
route: FSM CSV route exists (flag Y) but blocked: export refused, access denied (WSFunctionPermission on the European localization service)
depends_on: none
test_records: none created; data export 100004744431855 COMPLETED_ERRORS; template export also refused
notes: Batch 16 (sitting 7). FAILED: the sign-in user lacks the web service permission for this object's export, so no read and no safe import. Next step: ask the pod owner for the Italian localization privilege (or a user with it), then retry the export.
