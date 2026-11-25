task_code: XLE_MANAGE_INTERCOMPANY_EXCEPTIONS
task_name: Manage Intercompany Exceptions
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run
route: FSM CSV (legal entity package: XLE_ENTITY_PROFILE, XLE_ETB_PROFILE, XLE_REGISTRATION, XLE_LE_LEGAL_ADDRESS, ...); export VERIFIED, import GUESS
depends_on: an existing legal entity (XLE_SEARCH_LEGAL_ENTITIES reads it)
test_records: none
notes: Batch 08. unsafe to test: the task package is the legal entity package with no separate exception record; any load changes an existing legal entity (used by every ledger, business unit and intercompany transaction) or creates a full new legal entity with party, address and registrations. Export VERIFIED (8 files, 67 entities); import GUESS. Next step: load-test only on an environment we own, with written approval.
