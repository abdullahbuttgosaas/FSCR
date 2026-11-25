# CHANGELOG: manage-tree-structures (GoSaaS gap fill)

- 2026-11-25, batch 07 (AB with Claude). Skill written from a read-only export and three live tries.
  - Try 1 `GAPFILL_AB_B7_TS1`, ProcessId 100004742421534: refused, JBO-27014 for NumberOfTrees and RestrictByDate; nothing created.
  - Try 2 same name with NumberOfTrees=1, RestrictByDate=N, ProcessId 100004742441558: created DRAFT, but the self relationship row replaced the root row. Skill now sends the root row only.
  - Try 3 `GAPFILL_AB_B7_TS2`, ProcessId 100004742423588: 4 rows processed, 0 failed; compare exactly 4 rows added: PASS.
  - Fresh test `GAPFILL_AB_B7_TS3F`, ProcessId 100004743404182: PASS first try.
  - Tester suggestions, not applied (the skill already says it lower down): say early that the structure count grows with each earlier run; the export may end with `StatusCode: (unknown)` (normal); give an example for Description and DataSourceName; save DS and PID to a file in RUN; check that the payload holds only the 4 new rows.
