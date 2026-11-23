# CHANGELOG: manage-tax-zone-types (GoSaaS gap fill, not official FSCR)

## 0.0.1, 2026-11-23 (batch 2 part 2, AB with Claude): FAILED
- Read-only export: 9 files, 1 existing zone type (TAX use, limited by one country).
- Import attempt 1 (no CreatedByModule): JBO-27014 CreatedByModule is required. Nothing created.
- Import attempt 2 (+ CreatedByModule=HZ_GEO_HIERARCHY): row validated, then JBO-26041 database insert error into HZ_GEOGRAPHY_TYPES_B. Nothing created (after-export checked).
- Import attempt 3 (+ the 4 country-limit columns copied from the existing zone type): same JBO-26041. Nothing created (after-export checked).
- Stopped at the 3-attempt limit. SKILL.md documents the package, the attempts and 4 ideas for the next try.
- No fresh test: a fresh tester cannot pass a recipe that does not work.

## Test records created
None. `GAPFILL_AB_ZT1` was tried 3 times and does not exist.

## 0.0.1 check, 2026-11-23 (batch 3 part 1, AB with Claude): still FAILED, cannot do by CSV so far
- Read-only look for the detailed error of the 3 failed imports: ESS requests 4481501, 4481510 and 4481523 exist and show SUCCEEDED (erpintegrations ESSJobStatusRF), but their ESS logs download as empty ZIPs (ESSJobExecutionDetailsRF, fileType ALL/LOG/OUT), and the setup-import process is not found under those IDs (HTTP 404; the FSM ProcessId is a different number and was not kept). No ORA- cause could be read.
- No extra import: the approved one extra try was only for an error that shows our file is wrong, and no such error could be read.
- New read-only export (22:50): still exactly 1 zone type (`US Zone Type`, use TAX, CreatedBy and LastUpdatedBy filled, code mixed case with spaces). Nothing from batch 2 was created.
- Status stays failed; listed as "cannot do by CSV (as tested)". To go further a person must read the request log in Scheduled Processes, or create one zone type on the screen and export it.
