task_code: ORA_FND_MANAGE_DOCUMENT_SEQUENCES_LEDGER
task_name: Manage Ledger Document Sequences
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 6
waiting_minutes: 5
fresh_claude_pass: yes (re-test)
route: FSM CSV (FND_APP_DOCSEQ_LEDGER + ORA_FND_APP_DOCSEQ_ASSIGNMENT_LEDGER) + REST documentSequences read-back + export compare
depends_on: FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES (test category GAPFILL_DSC_T1); an existing primary ledger with no open assignment for that category
test_records: GAPFILL_AB_B8_LSQ1 (refused 100004742423686); GAPFILL_AB_B8_LSQ2 (100004743403613); fresh GAPFILL_AB_B8_LSQ3F (refused FND-7020, 100004742423742); re-test GAPFILL_AB_B8_LSQ4R (100004742423771)
notes: Batch 08. New ledger document sequence assigned to a test category on an existing ledger (adds an assignment; changes no existing row). Try 1 refused (ValidateTransactionDate required); try 2 PASS. Fresh test refused FND-7020 because the brief reused the same category and ledger; skill got Prerequisite 3 (no open assignment for CAT+LEDGER) and a re-test on another ledger PASSED. Re-test notes are suggestions (in CHANGELOG).
