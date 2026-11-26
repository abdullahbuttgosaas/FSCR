# Changelog
- 2026-11-25, batch 13 (AB with Claude). Read skill written; create FAILED in 7 tries (PrimaryHierarchyIds isn't valid). Tries recorded in SKILL.md Step 3.
- 2026-11-26, batch 13 retry (AB with Claude). Docs research, REST probe (no resource), round trip of an existing topic (PASS, no change), column compare, tries HT8 to HT10 each after a written diagnosis: all refused. SKILL.md v0.2.0 records the diagnosis and the conclusion (CSV create not possible). Stays failed.
- 2026-11-26 (AB with Claude). Status failed -> screen-only (proven cause: PrimaryHierarchyIds is rejected on insert; only the page creates the hierarchy ID). Added to screen-only.csv. Skill header updated.
- 2026-11-26, screen-only verification run (AB with Claude, read only): decision screen-only. Proof written on STATUS.md.
