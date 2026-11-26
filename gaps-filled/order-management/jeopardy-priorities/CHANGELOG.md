# CHANGELOG - Manage Jeopardy Priorities (DOO_MANAGE_JEOPARDY_PRIORITIES)

## 2026-11-26 (sitting 1, batch 01)
- Skill written from the live export; own test: FSCRT_AK_GF_JP1: export 100004743455297, import 100004744431219 (1 row, 0 failed), after-export 100004743456337: 1 new row, 0 existing changed. Safe way: a new code with its own non-overlapping range; seeded HIGH/MEDIUM/LOW untouched.
- Fresh test F: FSCRT_AK_GF_JPF: export 100004744431265, import 100004744422985, after-export 100004744431351: 1 new row, 0 changed. PASS.
- Wording fixes after F (all skills): "Notes for every run" added (empty before/after folders, file names hold the environment name, --find code check, interim import status lines are harmless, code length tested at 15).
- Tester F WRONG: worked-example range 1000-1010 is now taken (fixed: read highest maximum of all rows, never copy example ranges).
- Tester F WRONG: column list missed CreatedBy/LastUpdatedBy (fixed).
- Tester F: shared end points unclear (fixed: avoid them, untested).
- Tester F: interim status lines (fixed: Notes).
- Tester R suggestion (not applied): mention the .txt log next to the ZIP.
- Re-test R after the fixes: FSCRT_AK_GF_JPR: export 100004743455825, import 100004744431540, after-export 100004744432765: 1 new row, 0 changed. PASS, no wrong sentence.
