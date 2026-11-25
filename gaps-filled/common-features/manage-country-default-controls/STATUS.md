task_code: ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS
task_name: Manage Country Default Controls
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: no
route: FSM CSV (ZX_COUNTRY_DEFAULTS)
depends_on: ZX_MANAGE_TAX_REGIMES; ZX_MANAGE_TAXES (if defaults name them)
test_records: none (not loaded)
notes: unsafe to test: one row per country; a row changes tax defaulting for every transaction and registration in that country (no test country exists). Export VERIFIED (52 columns, 0 rows). Build/import GUESS. Next step: load-test only on an environment we own.
