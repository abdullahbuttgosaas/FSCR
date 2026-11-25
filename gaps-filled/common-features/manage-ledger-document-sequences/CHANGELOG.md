# CHANGELOG: manage-ledger-document-sequences (GoSaaS gap fill)

- 2026-11-25, batch 08 (AB with Claude). Skill written from a read-only export and live tries.
  - Try 1 `GAPFILL_AB_B8_LSQ1`, ProcessId 100004742423686: refused, JBO-27014 ValidateTransactionDate required; nothing created.
  - Try 2 `GAPFILL_AB_B8_LSQ2`, ProcessId 100004743403613: 2 rows, 0 failed; REST and compare PASS.
  - Fresh test `GAPFILL_AB_B8_LSQ3F`, ProcessId 100004742423742: refused FND-7020 UNIQUE-DATE OVERLAP (same category and ledger as LSQ2). Fixed: new Prerequisite 3 with a check one-liner, a START default, and a failure note for FND-7020.
  - Re-test `GAPFILL_AB_B8_LSQ4R` on another primary ledger, ProcessId 100004742423771: PASS (REST and compare: sequence 1, assignment 1 added).
  - Tester suggestions, not applied: put the category export command and a one-liner for its APP, MODULE, TABLE here; move Prerequisite 3 into Step 2; a one-liner listing all assignments for CAT.
