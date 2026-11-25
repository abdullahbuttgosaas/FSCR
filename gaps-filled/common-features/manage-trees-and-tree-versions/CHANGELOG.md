# CHANGELOG: manage-trees-and-tree-versions (GoSaaS gap fill)

- 2026-11-25, batch 07 (AB with Claude). Skill and helper `scripts/tree_rows.py` written.
  - Live test: `GAPFILL_AB_B7_TR1` + version `GAPFILL_AB_B7_TR1_V1` (DRAFT), 6 parameters on test value set `GAPFILL_AB_RT_VS`, ProcessId 100004742423501, first try; REST fndTreeVersions 1 row DRAFT; compare PASS (tree 1, version 1, parameters 6).
  - Helper dry-run checked against the live rows (same columns and values); `--template-value-set` made optional (read from the template nodes) before the fresh test.
  - Fresh test: `GAPFILL_AB_B7_TR2F`, ProcessId 100004743403418: PASS.
  - Tester suggestions, not applied (no wrong sentence): a one-liner listing trees with node counts; a START default; explain the `template value set:` line (often named like the tree); retry an export that times out before it starts; a loop building the `--expect` flags.
  - REST notes: `fndTrees` with `q` on two columns joined by `and` returned 0 rows; one column works.
