task_code: ORA_FND_MANAGE_DOCUMENT_SEQUENCES_LEGAL
task_name: Manage Legal Document Sequences
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 5
waiting_minutes: 6
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (ORA_FND_APP_DOCSEQ_LEGAL + ORA_FND_APP_DOCSEQ_LEGAL_ASSIGNMENT) + REST documentSequences read-back
depends_on: FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES (a test category on WSH_NEW_DELIVERIES); an existing legal entity
test_records: category GAPFILL_AB_B9_LC1 (100004743405664); GAPFILL_AB_B9_GSQ1 (100004743402677); fresh GAPFILL_AB_B9_GSQ2F (100004743402841); re-test GAPFILL_AB_B9_GSQ3R (100004743406350)
notes: Batch 09. All legal sequences on this environment are on WSH_NEW_DELIVERIES (bill of lading); new test category on that table, sequence type G, assigned to 3 different legal entities. Determinant shows as LE in REST. Fresh test PASS; a wording fix (check the after-export made a ZIP before comparing, found by the BU tester) was applied here too, so re-tested: PASS.
