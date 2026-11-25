# CHANGELOG: manage-account-hierarchy-labels (GoSaaS gap fill)

- 2026-11-25, batch 07 (AB with Claude). Skill written from a read-only export and a live test.
  - Live test: `GAPFILL_AB_B7_AHL1`, ProcessId 100004743403129, first try: 3 rows processed, 0 failed; compare PASS (label added, parents changed 0).
  - Fresh test: `GAPFILL_AB_B7_AHL2F`, ProcessId 100004743403403: PASS. Wrong sentence reported: Step 2 said the structure file has 1 row, data sources 2 rows; later exports also hold custom structures and their labels (3 structures, 4 data sources). Fixed to "at least" + explanation; added the export retry on a time-out.
  - Re-test: `GAPFILL_AB_B7_AHL3R`, ProcessId 100004743404147: PASS on the final wording.
  - Tester suggestions, not applied: say which start date (today); a payload row-count one-liner; point to the REST output for DS; use the csv module, not `wc -l`, for row counts; the worked example's "9 labels" grows as test labels stay.
