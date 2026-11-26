task_code: ORA_RCS_GUIDED_JOURNEY
task_name: Guided Journeys
module: Common Features
status: screen-only
filled_by: AB
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 0
waiting_minutes: 2
fresh_claude_pass: no (screen-only: the REST route refuses to create a guided journey)
route: none that creates: FSM CSV task export refused (flag N); REST hcm journeys has create and duplicateJourney but refuses the guided journey category
depends_on: none
test_records: none (every try refused; read back 0 rows each time)
notes: Batch 23 (sitting 10), 2026-11-26. Screen-only with proven cause (a route exists but cannot create the record). 1) CSV: task export refused, CSVExportImportSupportedFlag N (verification run 2026-11-26). 2) REST hcm journeys (describe: create, update, delete, duplicateJourney; 36 guided journeys exist, all Category ORA_GUIDED, Level ORA_GLOBAL): try 1 POST Name GAPFILL_AB_B23_GJ1, Category ORA_GUIDED: HTTP 400 "The value of the attribute Category isn't valid"; try 2 with Level ORA_GLOBAL: HTTP 400 "Attribute Level in view object Worker Journeys cannot be set" (create defaults Level to ORA_PERSONAL); try 3 duplicateJourney body without the action wrapper: HTTP 400 invalid structure; round trip: duplicateJourney action on an existing working guided journey under the new name: HTTP 400 "The value of the attribute Category isn't valid" (same refusal). GET after each try: 0 GAPFILL rows, nothing created. Cause: the journeys resource works on worker journeys (personal level) and refuses the guided category even when copying a working guided journey. Oracle REST docs pages for journeys could not be read (landing page only). Not tried: HCM Data Loader ChecklistTemplate (not a CSV/REST setup route). Guided journeys are made on the page (Setup and Maintenance > Guided Journeys).
