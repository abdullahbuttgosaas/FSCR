# CHANGELOG: search-legal-entities (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-25 (batch 05, AB with Claude)
- Read-only export: Read-only export XLE_SEARCH_LEGAL_ENTITIES: 8 files (XLE_ENTITY_PROFILE 67 rows, XLE_ETB_PROFILE 67, XLE_REGISTRATION 68, ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION 67, XLE_LE_LEGAL_ADDRESS 57, 2 registration-function files 0) + metadata. REST legalEntitiesLOV answers by Name (LIKE is case-sensitive).
- Live (AB): REST legalEntitiesLOV 1 row; export viewed with view_record.py: profile (US, legal employer Y, PSU Y, transacting Y), identifying registration (United States Income Tax), main reporting unit and its registration. READ-BACK PASS.
- Fresh test (task name + SKILL.md only): PASS on PPVision America, no help; found 2 extra rows of another entity whose registration number equals the identifier -> wording fix (--match-cols). Re-test R on 28Vision Corporate HQ: PASS, 4 rows, all of this entity.
- Tester notes not applied (suggestions): time estimates (48 to 65 s seen), explain that Name in registration files is the jurisdiction, table row for the 2 registration-function files.

## Test records created
- none created (view/search task); looked up existing legal entities: live 28Vision America, fresh test PPVision America, re-test 28Vision Corporate HQ
