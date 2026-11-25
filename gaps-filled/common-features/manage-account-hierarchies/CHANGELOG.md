# CHANGELOG: manage-account-hierarchies (GoSaaS gap fill)

- 2026-11-25, batch 07 (AB with Claude). Skill written; uses the trees helper `tree_rows.py`.
  - Prerequisite: test value set `GAPFILL_AB_B7_AHVS` (values `P100` summary, `D110` detail) by the value set skill, ProcessId 100004742423615, REST read-back PASS.
  - Live test: `GAPFILL_AB_B7_AH1`, version DRAFT, 2 nodes, ProcessId 100004742421559, first try; REST fndTreeNodes 2 rows; compare PASS (tree 1, version 1, parameters 6, nodes 2).
  - Before the fresh test: export retry note, a one-liner listing trees with node counts, a START default, and the meaning of the helper's `template value set:` line.
  - Fresh test: `GAPFILL_AB_B7_AH2F`, ProcessId 100004743402217: PASS (value set already existed, reused).
  - Tester suggestions, not applied: a REST check of the two values and their SummaryFlag; a note to quote template codes with spaces; a loop that builds the parameter `--expect` flags; the export may print `StatusCode: (unknown)` (normal).
