# CHANGELOG: manage-crm-bu-profile-options (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-25 (batch 06, AB with Claude)
- Read-only export: Read-only export ORA_ZCA_MANAGE_COMMON_CRM_BUSINESS_UNIT_PROFILE_OPTIONS: 4 files, 0 rows; scope = HZ_ENABLE_MULTIPLE_BU_CRM, mode edit. REST: option in HZ, SITE value N.
- Status written (not load-tested): unsafe to test: the export scope is the single seeded option HZ_ENABLE_MULTIPLE_BU_CRM (edit mode); a load switches multiple-BU behaviour for every CRM user. Reads VERIFIED (SITE value N); import GUESS. Next step: load-test only on an environment we own.

## Test records created
- none (not loaded)
- 2026-11-26, sitting 8 (AB with Claude). Re-judged against the unsafe rule: still unsafe: the only object is the seeded SITE option (USER level disabled); test-and-restore is not allowed because turning multiple BU on for CRM changes how other users' CRM records are stamped while it is on (GUESS from Oracle's description of the option), so the change may create other records.
