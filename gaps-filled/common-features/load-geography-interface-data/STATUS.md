task_code: HZ_LOAD_GEOGRAPHY_INTERFACE_DATA
task_name: Load Geography Interface Data
module: Common Features
status: written
filled_by: AB
date: 2026-11-27
minutes_to_write: 6
minutes_to_test: 7
waiting_minutes: 3
fresh_claude_pass: not run (unsafe to test)
route: REST: erpintegrations uploadFileToUCM (account crm$/geography$/import$, VERIFIED) + crm importActivities create with ObjectCode GeographyInterface (VERIFIED create); file columns RecordTypeCode, PrimaryGeographyName, CountryCode, LevelNumber, SourceId, ParentSourceId, LanguageCode (VERIFIED metadata). Open point: DataFiles InputFileContentId needs the content name, which REST did not return
depends_on: none to load; then HZ_RUN_GEOGRAPHY_LOADER
test_records: activities GAPFILL_AB_B24_GIM1 (300000395558015) and GAPFILL_AB_B24_GIM2 (300000395567166): 0 rows read, no geography created; uploaded file GAPFILL_AB_B24_Geography.csv (DocumentId 4544821, content repository only)
notes: Batch 24 (sitting 11). 3 tries for one level-2 test geography under AQ: 1) inline InputFileContent refused (HTTP 400 Invalid attribute, nothing created); 2) InputFileContentId UCMFA0+DocumentId: COMPLETE_WITH_ERRORS, it read another document, ReadFromFile empty; 3) numeric DocumentId: ERROR, ReadFromFile empty. erpintegrations DocumentIdsByFilePrefixRF gives no content name. No row was read, so nothing was created. Re-judged written (unsafe to test), same reason as Run Geography Loader (batch 21): master geography is shared by every address, validation and tax jurisdiction and has no delete; a prefix geography would still show in all users' address lists. The tries above should not have been run under that rule; they created nothing. What would make it safe: a customer-owned environment, their file, written approval; then read the content name once on the Import Management page (skill Step 3).
