task_code: ZCA_MANAGE_SEARCH_PROFILE_OPTIONS
task_name: Manage Search Profile Options
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: no
route: FSM CSV (FND_APP_PROFILE_OPTION/VALUE/LEVEL); read by REST profileOptions + siteProfileOptionValues
depends_on: FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS recipe (parent row unchanged)
test_records: none (not loaded)
notes: unsafe to test: the export scope is 2 named seeded options (ZCA_SEARCH_DEFAULT_OPTION, ZCA_SEARCH_HIDE_SENSITIVE_ATTR) in edit mode; any load changes the SITE search setting of every user. Export and REST reads VERIFIED (SITE value KEYWORD_SEARCH; the hide option is not in this release). Import steps GUESS. Next step: load-test only on an environment we own.
