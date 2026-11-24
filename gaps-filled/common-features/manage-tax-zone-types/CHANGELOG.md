# CHANGELOG: manage-tax-zone-types (GoSaaS gap fill, not official FSCR)

## 0.0.1, 2026-11-23 (batch 2 part 2, AB with Claude): FAILED
- Read-only export: 9 files, 1 existing zone type (TAX use, limited by one country).
- Import attempt 1 (no CreatedByModule): JBO-27014 CreatedByModule is required. Nothing created.
- Import attempt 2 (+ CreatedByModule=HZ_GEO_HIERARCHY): row validated, then JBO-26041 database insert error into HZ_GEOGRAPHY_TYPES_B. Nothing created (after-export checked).
- Import attempt 3 (+ the 4 country-limit columns copied from the existing zone type): same JBO-26041. Nothing created (after-export checked).
- Stopped at the 3-attempt limit. SKILL.md documents the package, the attempts and 4 ideas for the next try.
- No fresh test: a fresh tester cannot pass a recipe that does not work.

## Test records created (batch 2)
None. `GAPFILL_AB_ZT1` was tried 3 times and does not exist.

## 0.0.1 check, 2026-11-23 (batch 3 part 1, AB with Claude): still FAILED, cannot do by CSV so far
- Read-only look for the detailed error of the 3 failed imports: ESS requests 4481501, 4481510 and 4481523 exist and show SUCCEEDED (erpintegrations ESSJobStatusRF), but their ESS logs download as empty ZIPs (ESSJobExecutionDetailsRF, fileType ALL/LOG/OUT), and the setup-import process is not found under those IDs (HTTP 404; the FSM ProcessId is a different number and was not kept). No ORA- cause could be read.
- No extra import: the approved one extra try was only for an error that shows our file is wrong, and no such error could be read.
- New read-only export (22:50): still exactly 1 zone type (`US Zone Type`, use TAX, CreatedBy and LastUpdatedBy filled, code mixed case with spaces). Nothing from batch 2 was created.
- Status stays failed; listed as "cannot do by CSV (as tested)". To go further a person must read the request log in Scheduled Processes, or create one zone type on the screen and export it.

## 0.0.2, 2026-11-24 (batch taxfix, AB with Claude): still FAILED, cause narrowed to outside the file
- REST re-check: the old ProcessIds cannot be listed (`SetupTaskCSVImportProcess` returns 0 items without an id); results have only the `ProcessLog` enclosure; the ESS log of new request 4,483,619 is an empty ZIP too.
- Attempt 4 (ProcessId 100004742410256): no translation row, country by names only. Same `JBO-26041`, but the log now shows the SQL: `INSERT INTO HZ_GEOGRAPHY_TYPES_B(GEOGRAPHY_TYPE, OBJECT_VERSION_NUMBER, GEOGRAPHY_USE, POSTAL_CODE_RANGE_FLAG, CREATED_BY_MODULE, who columns, GEOGRAPHY_TYPE_ID)`. Names do not set the country limit. Translation row ruled out.
- Attempt 5 (ProcessId 100004742410458): the whole working zone type row copied (`template_row.py`, limit id from the export), only code and name new. Same error; the SQL now has `LIMITED_BY_GEOGRAPHY_ID`.
- Attempt 6 (ProcessId 100004742411036, request 4,483,683): as 5 with the working row's code style (mixed case, spaces). Same error. Stopped (3 tries this session).
- Export after attempt 6: still 1 zone type; nothing created.
- Browser (last resort, only to read the request log): the browser pane reached Oracle's sign-in page and no sign-in was available in this run, so the log was not read.
- SKILL.md: attempts table, what is proven, best package (attempt 6), exact next steps.
- 2026-11-24 follow-up: AB checked request 4,483,683 in Scheduled Processes: Succeeded, Log and Output attachment None; no ORA- line there either. Next step: Oracle SR or one screen-made reference zone type.
- 2026-11-24 follow-up 2: AB made GAPFILL_AB_TF_ZT1 on the screen; it saved. Read-only export 100004742409666: TAX, N, HZ_GEO_HIERARCHY, no country limit. Same Oracle user as the import. Same shape by CSV was refused in batch 2 attempt 2, so the cause is the setup CSV import (not access, not the file). Next: Oracle SR. Evidence 06_screen_reference.txt.

## 0.1.0, 2026-11-24 (batch taxfix2, AB with Claude): TESTED, fixed
- Read-only export 100004742409723: 2 zone types (screen-made GAPFILL_AB_TF_ZT1, US Zone Type).
- Round trip: the export's own ZT1 rows, only code/name changed to GAPFILL_AB_TF2_ZT2, imported fine (ProcessId 100004741416084); after-export 100004741416143 shows it. So the CSV import works: not an Oracle defect, not access.
- Byte compare with our builder's package of the same values: only `CreatedBy` and `LastUpdatedBy` differ (ours empty; zip order also differs and does not matter). All 6 failed tries had them empty.
- Fix: new helper `scripts/zone_type_rows.py` fills both columns (type and translation row) from the export's `SubmittedBy` (the signed-in user; never printed). GAPFILL_AB_TF2_ZT3 imported first try (ProcessId 100004742412123); after-export 100004741415297, compare PASS.
- SKILL.md rewritten (status tested, 6 steps, no Oracle prerequisite). Fresh test PASS: GAPFILL_AB_TF2_ZT4F (ProcessId 100004742411691), read back by me.
- Wording fixed from its notes: log read prints only result lines (the log has a `Submitted By` user line); what to do with a re-run export folder; what a good Step 2 looks like; name style for codes like `ZT4F`.
- Re-test PASS: GAPFILL_AB_TF2_ZT5R (ProcessId 100004742412240), read back by me. Its notes, not applied (no further wording change): "Step 0" heading has no own actions; `@rows.txt` and `--prefix-col` not explained; the repeated `Business object ... In progress` lines are normal; Step 6 gives no command for the row check (use `added_rows.csv`); no way to confirm the same sign-in user.
- Not tested: `--limit-like` (country limit), zones and zone ranges.

## Test records created (all kept, none deleted)
GAPFILL_AB_TF2_ZT2, GAPFILL_AB_TF2_ZT3, GAPFILL_AB_TF2_ZT4F, GAPFILL_AB_TF2_ZT5R (all use TAX, no country limit, no zones).
