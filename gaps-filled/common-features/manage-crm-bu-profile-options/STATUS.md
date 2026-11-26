task_code: ORA_ZCA_MANAGE_COMMON_CRM_BUSINESS_UNIT_PROFILE_OPTIONS
task_name: Manage Common CRM Business Unit Profile Options
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: no
route: FSM CSV (FND_APP_PROFILE_OPTION/VALUE/LEVEL); read by REST
depends_on: ZCA_MANAGE_SEARCH_PROFILE_OPTIONS skill (card over it)
test_records: none (not loaded)
notes: unsafe to test: the export scope is the single seeded option HZ_ENABLE_MULTIPLE_BU_CRM (edit mode); a load switches multiple-BU behaviour for every CRM user. Reads VERIFIED (SITE value N); import GUESS. Next step: load-test only on an environment we own. Re-judged 2026-11-25 (sitting 4, new unsafe rule): HZ_ENABLE_MULTIPLE_BU_CRM allows only SITE level (REST profileOptionLevels: USER EnabledFlag N, VERIFIED 2026-11-25), so no own-user value is possible; a SITE flip changes multiple-BU behaviour for every CRM user and is not a single value we can safely prove restored for others during the test. Stays written. Re-judged 2026-11-26 (sitting 7): still unsafe. The export scope is the one seeded option in edit mode, so a new own option (the safe route used for LE, tax and GL options) would not land in this task (GUESS from mode=edit). No safe route found. Re-judged 2026-11-26 (sitting 8): still unsafe: the only object is the seeded SITE option (USER level disabled); test-and-restore is not allowed because turning multiple BU on for CRM changes how other users' CRM records are stamped while it is on (GUESS from Oracle's description of the option), so the change may create other records.
