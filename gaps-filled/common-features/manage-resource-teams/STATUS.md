task_code: HZ_MANAGE_RESOURCE_TEAMS
task_name: Manage Resource Teams
module: Common Features
status: screen-only
filled_by: AB
date: 2026-11-26
minutes_to_write: 7
minutes_to_test: 0
waiting_minutes: 4
fresh_claude_pass: no (screen-only: no route creates a resource team)
route: none: no FSM CSV (flag N), no REST resource, no Import Management object for resource teams
depends_on: none
test_records: none (the import activity was refused; nothing created)
notes: Batch 23 (sitting 10), 2026-11-26. Proof: 1) CSV: task export refused, CSVExportImportSupportedFlag N (verification run 2026-11-26). 2) REST: crm resourceTeams, teams 404 (earlier); queues child resourceTeams only links an existing team to a queue. 3) Import Management (crm importActivities): the full object list (importExportObjectMetadata finder objectRowFinder, 433 objects, hasMore false, VERIFIED) has no resource team object; the only team objects are QueueResourceTeam / QueueResourceOnCallTeam (team to queue links), AccountTeam, CampaignTeam and other record teams. Test POST of an import activity with ObjectCode ResourceTeam (one row GAPFILL_AB_B23_TEAM1): HTTP 400 "The value of the attribute ObjectCode isn't valid", nothing created. The Oracle doc 'Resource Team Import' object is not available on this release. Resource teams are made on the page only.
