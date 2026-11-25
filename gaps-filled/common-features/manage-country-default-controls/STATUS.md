task_code: ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS
task_name: Manage Country Default Controls
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 2
waiting_minutes: 3
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (ZX_COUNTRY_DEFAULTS: a NEW row for a country nobody transacts in, every default flag N); export compare read-back
depends_on: none for the test row; ZX_MANAGE_TAX_REGIMES and ZX_MANAGE_TAXES if a real row names a default regime and tax
test_records: AQ (100004743428300); fresh BV (100004743427417); re-test HM (100004744404860). Country rows have no name column, so no prefix is possible
notes: Batch 13 (was written in batch 06; re-judged safe in sitting 4: a row for an unused country with every default N has no effect). Export had 0 rows. CountryCode + 4 flags N imported first try; Oracle adds RegimeTypeFlag I. Fresh test PASS; wording fixed (process log, not import.log, holds the result; StatusCode unknown is normal; retry folder names); re-test PASS. The CSV route has no delete: the 3 rows stay.
