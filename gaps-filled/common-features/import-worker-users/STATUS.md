task_code: HRC_IMPORT_WORKER_USERS
task_name: Import Worker Users
module: Common Features
status: tested
filled_by: AB
date: 2026-11-26
minutes_to_write: 8
minutes_to_test: 6
waiting_minutes: 3
fresh_claude_pass: yes (fresh test PASS: GAPFILL_AB_B21_WU2F PersonNumber 104, 1 account, no roles; wording fixed to v0.2.1; R re-test PASS: GAPFILL_AB_B21_WU3R PersonNumber 108, 1 account, no roles)
route: REST hcm workers POST (Fusion makes the user account) + userAccounts read back; HCM Data Loader for bulk (GUESS); no FSM CSV (export refused)
depends_on: a legal employer and business unit
test_records: GAPFILL_AB_B21_WU1 PersonId 300000395500126 (PersonNumber 103); fresh WU2F 300000395468138 (104); R WU3R 300000395494304 (108). Each: 1 user account, not suspended, 0 roles.
notes: Batch 21 (sitting 9). Re-judged sitting 8 (new user with no roles is not unsafe). Own test: one worker created, Fusion made its user account with no roles (VERIFIED by userAccounts expand=userAccountRoles). Remaining tester notes (not errors): Step 4 PersonId comes from Step 2; check HTTP 201 in the log.
