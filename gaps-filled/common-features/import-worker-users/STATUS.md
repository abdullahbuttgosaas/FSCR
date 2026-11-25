task_code: HRC_IMPORT_WORKER_USERS
task_name: Import Worker Users
module: Common Features
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 3
minutes_to_test: 0
waiting_minutes: 0
fresh_claude_pass: not run
route: HCM Data Loader Worker.dat (GUESS) or REST workers + userAccounts; no FSM CSV (export refused)
depends_on: FND_CREATE_IMPLEMENTATION_USERS rules; a legal employer and business unit
test_records: none
notes: Batch 10. unsafe to test: a load creates HR person records and sign-in accounts on the shared environment; role auto-provisioning may grant roles; test people would show in HR reports. Read resource VERIFIED (userAccounts describe); loads GUESS. Next step: load-test only on an environment we own, with HR and security owners' written approval. Re-judged 2026-11-25 (sitting 4, new unsafe rule): a NEW test worker with prefix name nobody uses would be safe under the new rule, but it needs a legal employer assignment and may get roles by auto-provisioning; planned next (also unlocks Partner Organizations: worker -> resource -> partner owner).
