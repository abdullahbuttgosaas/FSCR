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
notes: unsafe to test: the export scope is the single seeded option HZ_ENABLE_MULTIPLE_BU_CRM (edit mode); a load switches multiple-BU behaviour for every CRM user. Reads VERIFIED (SITE value N); import GUESS. Next step: load-test only on an environment we own.
