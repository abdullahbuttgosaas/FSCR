task_code: ZX_MANAGE_TAX_ZONE_TYPES
task_name: Manage Tax Zone Types
module: Common Features
status: failed
filled_by: AB
date: 2026-11-23
minutes_to_write: 6
minutes_to_test: 0
waiting_minutes: 5
fresh_claude_pass: no
route: FSM CSV
depends_on: none
test_records: none (GAPFILL_AB_ZT1 tried 3 times, never created)
notes: Batch 2 part 2 + batch 3 check (2026-11-23 22:44-22:52). Cannot do by CSV (as tested): 3 imports failed (JBO-27014 CreatedByModule required, then JBO-26041 insert into HZ_GEOGRAPHY_TYPES_B). Batch 3 tried to read the detailed error read-only: ESS requests 4481501/4481510/4481523 exist (SUCCEEDED) but their ESS logs are empty and the import process cannot be reached by those IDs (HTTP 404), so no ORA- cause was found; no extra import was made (the approved retry needed an error showing our file was wrong). Fresh export 22:50: still 1 zone type (US Zone Type, mixed case with spaces, CreatedBy filled). Next step needs a person: read the request log in Scheduled Processes, or create one zone type on the screen and copy its rows.
