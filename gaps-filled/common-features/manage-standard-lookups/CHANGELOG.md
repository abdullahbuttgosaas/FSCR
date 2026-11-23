# CHANGELOG: manage-standard-lookups (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-20 (batch 1 part 1, filled by AB with Claude)
- Wrote SKILL.md and 4 helper scripts: `build_lookup_package.py`, `read_lookup.py` (wraps FSCR's generic lookups REST read), `compare_lookup_exports.py`, `render_readback.py`.
- Live test on the test environment: export (16 types / 36 codes) -> before-read 404 -> import 1 attempt, 3 rows, 0 failed -> REST read-back PASS -> after-export compare PASS (+1 type, +2 codes, 0 removed, 0 changed).
- Lesson: from Git Bash, `/e/...` paths given to Windows Python become `E:\e\...`. Use `E:/...`. A stray empty folder was created once and removed (its one export ZIP moved into the work folder).

## Test records created (may not be deletable; never edit or delete without a person's decision)
| When | Who | Lookup type | Codes |
|---|---|---|---|
| 2026-11-20 live test | Claude (main session) | `GAPFILL_SL_T1` "GAPFILL SL T1 Lookup" | `GAPFILL_A`, `GAPFILL_B` |
| 2026-11-20 fresh test | fresh sub-agent (no context, skill only) | `GAPFILL_SLF1_TYPE` "GAPFILL SLF1 Fresh Lookup" | `GAPFILL_F1_ONE`, `GAPFILL_F1_TWO` |

## Fresh test, 2026-11-20: PASS
- Sub-agent given only the task name and this SKILL.md path. 1 import attempt, REST READBACK PASS, export compare PASS (17 -> 18 types, 38 -> 40 codes), about 2 min 15 s, no help. Verified again by the main session (READBACK PASS).
- Its notes were applied afterwards as wording only (not re-tested): how to find the FSCR root, ZIP name pattern, how to read the process log, counts grow between runs, steps 2/3 order, code uniqueness.
