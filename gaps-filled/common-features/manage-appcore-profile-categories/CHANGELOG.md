# CHANGELOG: manage-appcore-profile-categories (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-23 (batch 2 part 1, filled by AB with Claude)
- Wrote SKILL.md on the batch 1 generic helpers. No REST resource found (`profileCategories`, `profileOptionCategories`, `applicationProfileCategories`: HTTP 404), so the after-export compare is the read-back.
- Live test: export (2 categories, 1,574 links) -> import 1 attempt, 2 rows, 0 failed -> compare PASS (added `GAPFILL_AB_PC1` + link to `GAPFILL_AB_PO1`).

## Fresh test 1, 2026-11-23 19:56-19:59: own rows correct, overall compare FAIL (not the skill's fault)
- Created `GAPFILL_AB_PC3F` + link to `GAPFILL_AB_PO1`; 1 import, 2 rows, 0 failed. The compare also saw `GAPFILL_AB_PC4F`, made at the same time by the Manage Profile Categories tester (same package). My mistake: two testers on one package at once.
- Real wording bug found: Step 3.1 said all application-0 category rows share one ModuleId; the seeded ones carry a different id than YES_NO. Fixed: always use the YES_NO ModuleId (the tested one). Also added: how to judge a compare with another person's concurrent rows; the REST command for the option check; counts grow; several FSCR copies.

## Re-test after the wording fix, 2026-11-23 20:00-20:03 (run alone): PASS
- Created `GAPFILL_AB_PC5R` + link to `GAPFILL_AB_PO1`; ModuleId from YES_NO; 1 import; compare PASS (6 -> 7 categories, only its 2 rows).
- Notes NOT applied: the module-id command prints the id (not a secret); the FSCR root may be the pack folder itself.

## Test records created (may not be deletable; they show in the profile categories screen)
| When | Who | Record |
|---|---|---|
| live test | main session | category `GAPFILL_AB_PC1` -> option `GAPFILL_AB_PO1` |
| fresh test 1 | sub-agent | category `GAPFILL_AB_PC3F` -> option `GAPFILL_AB_PO1` |
| re-test | sub-agent | category `GAPFILL_AB_PC5R` -> option `GAPFILL_AB_PO1` |
