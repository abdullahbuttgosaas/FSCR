# CHANGELOG: map-reports-to-work-areas (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-25 (batch 06, AB with Claude)
- Read-only export: Read-only export ATK_DEFINE_REPORT_MAPPING: 3 files (ATK_RPANE_REPORT_MAPPING 11 rows on 4 work areas, ORA_REPORTS_AND_ANALYTICS_MAPPING_REPORT 13 rows) + metadata (isAdminUi=Y, BIPSConnName).
- Status written (not load-tested): unsafe to test: a mapping shows the report in the work area's Reports and Analytics panel to every user. Export VERIFIED (11 work area rows, 13 report rows; child report file has no parent key column). Build/import GUESS. Next step: load-test only on an environment we own, with a report nobody uses.

## Test records created
- none (not loaded)
