task_code: ZCA_MANAGE_SEARCH_PROFILE_OPTIONS
task_name: Manage Search Profile Options
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 2
waiting_minutes: 1
fresh_claude_pass: yes
route: REST profileOptions/ZCA_SEARCH_DEFAULT_OPTION/child/userProfileOptionValues POST (USER level, via scripts/rest_call.py); SITE route (FSM CSV / siteProfileOptionValues) written, not run
depends_on: FND_CREATE_IMPLEMENTATION_USERS (a test user; its SCIM id is the LevelValue)
test_records: USER value REAL-TIME_SEARCH for GAPFILL_AB_B11_U1; fresh: USER value REAL-TIME_SEARCH for GAPFILL_AB_B11_U2F; SITE value KEYWORD_SEARCH unchanged (read before and after)
notes: Batch 11 (re-opened: the option allows USER level, so a value for our own test user is a new record nobody uses; the SITE change stays unrun). Try 1 LevelValue = user name refused (LOV_UserName no matching row), nothing created; try 2 LevelValue = SCIM id: created. ZCA_SEARCH_HIDE_SENSITIVE_ATTR not in this release (404). Fresh test PASS.
