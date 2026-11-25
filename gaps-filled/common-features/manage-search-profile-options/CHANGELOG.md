# CHANGELOG: manage-search-profile-options (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-25 (batch 06, AB with Claude)
- Read-only export: Read-only export ZCA_MANAGE_SEARCH_PROFILE_OPTIONS: 4 files, 0 rows (seeded options left out); metadata scope = 2 named options, mode edit. REST: ZCA_SEARCH_DEFAULT_OPTION (ZCA) SITE KEYWORD_SEARCH; ZCA_SEARCH_HIDE_SENSITIVE_ATTR 0 rows.
- Status written (not load-tested): unsafe to test: the export scope is 2 named seeded options (ZCA_SEARCH_DEFAULT_OPTION, ZCA_SEARCH_HIDE_SENSITIVE_ATTR) in edit mode; any load changes the SITE search setting of every user. Export and REST reads VERIFIED (SITE value KEYWORD_SEARCH; the hide option is not in this release). Import steps GUESS. Next step: load-test only on an environment we own.

## Test records created
- none (not loaded)
