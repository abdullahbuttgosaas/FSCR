# CHANGELOG: manage-geography-lookups (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-20 (batch 1 part 1, filled by AB with Claude)
- Short card over `common-features/manage-standard-lookups` (same package and scripts).
- Found: export has 0 rows; its scope is a fixed list of 7 seeded geography lookup types. ModuleId taken by REST from a seeded scope type.
- Live test: before-read 404 -> import 1 attempt, 2 rows, 0 failed -> REST read-back PASS.
- Choice (made by AB for the note-type task and applied here too): test with a new GAPFILL_ type, not by adding codes to seeded types.

## Test records created (may not be deletable; never edit or delete without a person's decision)
| When | Who | Lookup type | Codes |
|---|---|---|---|
| 2026-11-20 live test | Claude (main session) | `GAPFILL_GEO_T2` "GAPFILL GEO T2 Lookup" | `GAPFILL_GEO_A` |
| 2026-11-20 fresh test | fresh sub-agent (no context, card only) | `GAPFILL_GEOF2_TYP` "GAPFILL GEOF2 Lookup" | `GAPFILL_GEOF2_K1`, `GAPFILL_GEOF2_K2` |

## Fresh test, 2026-11-20: PASS
- Sub-agent given only the task name and this SKILL.md path. 1 import attempt (3 rows, 0 failed), READBACK PASS, about 1.5 min, no help. Verified again by the main session.
- Its notes applied afterwards as wording only (not re-tested): say what `<STD>` is and that all STD steps (incl. unzip and before-read) still apply.
