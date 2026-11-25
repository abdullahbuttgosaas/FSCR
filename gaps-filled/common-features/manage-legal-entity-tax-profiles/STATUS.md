task_code: ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES
task_name: Manage Legal Entity Tax Profiles
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run
route: FSM CSV (ZX_LEGAL_ENTITY_TAX_PROFILE); export VERIFIED, import GUESS
depends_on: an existing legal entity (its profile is created with it)
test_records: none
notes: Batch 08. unsafe to test: Oracle creates one tax profile with each legal entity (67 entities, 67 profile rows), so every load updates an existing profile and changes tax on that legal entity's real transactions. Export and read steps VERIFIED; change/import/read-back GUESS. Next step: load-test only on an environment we own, with written approval.
