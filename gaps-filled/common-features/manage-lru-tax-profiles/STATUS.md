task_code: ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES
task_name: Manage Legal Reporting Unit Tax Profiles
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run
route: FSM CSV (ZX_ESTABLISHMENT_TAX_PROFILE + fiscal classification files); export VERIFIED, import GUESS
depends_on: an existing legal reporting unit (its profile is created with it); fiscal classification skills for codes
test_records: none
notes: Batch 08. unsafe to test: one profile per existing reporting unit (67 rows); every load updates an existing profile and changes tax and tax reporting of that unit. Export VERIFIED (about 70 files); import GUESS. Next step: load-test only on an environment we own, with written approval. Re-judged 2026-11-25 (sitting 4, new unsafe rule): every existing profile belongs to a real reporting unit; a NEW test legal entity with prefix name (with its own main reporting unit and tax profiles) would make this safe; that is a long chain through the legal entity package (party, address, registration), planned as the next step for a later sitting.
