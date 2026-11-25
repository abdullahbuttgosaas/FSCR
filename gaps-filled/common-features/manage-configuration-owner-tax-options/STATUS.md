task_code: ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS
task_name: Manage Configuration Owner Tax Options
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 0
waiting_minutes: 1
fresh_claude_pass: not run
route: FSM CSV (ZX_CONFIGURATION_OWNER_TAX_OPTIONS); export VERIFIED, import GUESS
depends_on: a real business unit or legal entity (owner); ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS if a factor set is named
test_records: none
notes: Batch 08. unsafe to test: each row sets tax options of a real business unit or legal entity for one application event class (there is no test owner); a new row changes tax handling of that owner's real transactions. Export VERIFIED (4 rows); build/import GUESS. Next step: load-test only on an environment we own, with written approval. Re-judged 2026-11-25 (sitting 4, new unsafe rule): each row sets options of a real business unit or legal entity; a NEW test legal entity with prefix name (with its own main reporting unit and tax profiles) would make this safe; that is a long chain through the legal entity package (party, address, registration), planned as the next step for a later sitting.
