task_code: GL_MANAGE_CROSS-VALIDATION_RULES
task_name: Manage Cross-Validation Rules
module: Common Features
status: written
filled_by: AB
date: 2026-11-27
minutes_to_write: 5
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run (unsafe to test)
route: FBDI Cross-Validation Rules Import (interface GL_CROSS_VALIDATION_RULES_INT; Increment or Replace mode), uploaded with Upload Rules on the page (Load Interface File for Import) or erpintegrations importBulkData (Oracle docs); FSM CSV = chart of accounts flexfield package, no rule file (VERIFIED); REST 404
depends_on: a chart of accounts structure instance; the FBDI template
test_records: none (not loaded)
notes: Batch 24 (sitting 11). unsafe to test: a rule belongs to the shared chart of accounts instance; once enabled it blocks account combinations for every ledger and user on that chart; Replace mode deletes every rule not in the file; no own test chart here. What would make it safe: an environment with its own test chart of accounts and written approval; Increment mode, rule loaded disabled.
