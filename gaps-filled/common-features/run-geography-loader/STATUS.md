task_code: HZ_RUN_GEOGRAPHY_LOADER
task_name: Run Geography Loader
module: Common Features
status: written
filled_by: AB
date: 2026-11-26
minutes_to_write: 6
minutes_to_test: 0
waiting_minutes: 2
fresh_claude_pass: not run (unsafe)
route: file import activity of the Geography object (Oracle docs) through REST crm importActivities (create, get, update, upsert; GET 200); crm geographyImportActivities 404; no FSM CSV (export refused)
depends_on: HZ_LOAD_GEOGRAPHY_INTERFACE_DATA
test_records: none
notes: Batch 21 (sitting 9). unsafe to test: master geography is shared reference data used by every address entry, address validation and tax jurisdiction; a test geography would show to all users; geographies cannot be deleted.
