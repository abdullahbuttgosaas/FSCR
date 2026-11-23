# CHANGELOG: manage-tax-lookup-codes (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-20 (batch 1 part 2, filled by AB with Claude)
- Wrote SKILL.md and 4 helper scripts for the Financials generic lookup package (4 CSVs): `build_generic_lookup_package.py`, `read_generic_lookup.py` (wraps FSCR's generic lookups REST reads: setEnabledLookups / standardLookups / commonLookups), `compare_generic_exports.py`, `render_readback.py`.
- Live test on the test environment: export (0 types / 23 codes) -> reference group read by REST -> before-read 404 in all three views -> import attempt 1 FAILED (`JBO-27014: Attribute ChangeSinceLastRefresh ... is required`; builder now writes `N`) -> attempt 2: type 1 row + code 1 row, 0 failed -> REST read-back PASS -> after-export compare PASS (+1 type, +1 code with translations, 0 removed, 0 changed).
- Lesson: Git Bash rewrites `/fscmRestApi/...` arguments into a Windows path; set `MSYS_NO_PATHCONV=1` before calling FSCR's REST client directly.

## Test records created (may not be deletable; never edit or delete without a person's decision)
| When | Who | Lookup type (view) | Codes (set) |
|---|---|---|---|
| 2026-11-20 live test | Claude (main session) | `GAPFILL_TAX_T1` "GAPFILL TAX T1 Lookup" (set-enabled, tax classification reference group) | `GAPFILL_TAX_A` "GAPFILL TAX T1 Alpha" (COMMON) |
| 2026-11-20 fresh test | fresh sub-agent (no context, skill only) | `GAPFILL_TAXF1_TYPE` "GAPFILL TAXF1 Lookup" (set-enabled) | `GAPFILL_TAXF1_A` "GAPFILL TAXF1 Alpha", `GAPFILL_TAXF1_B` "GAPFILL TAXF1 Beta" (COMMON) |

Visibility risk: both types are user-level (U) set-enabled types in the tax module and may be listed in Manage Tax Lookup Codes for all users. No code was added to a seeded tax type.

## Fresh test, 2026-11-20: PASS
- Sub-agent given only the task name and this SKILL.md path. 1 import attempt (type 1 row, codes 2 rows, 0 failed), REST READBACK PASS, export compare PASS, about 3 minutes, no help. Verified again by the main session (READBACK PASS, 2 codes, set COMMON).
- Its notes were applied afterwards as wording only (not re-tested): several codes (repeat `--expect-code`, list after `--require-codes`), row counts grow with every test, export also prints "No matching pillar setup-task metadata" and `StatusCode: (unknown)` on success, non-ASCII characters in existing codes, why checking the type name is enough, where to write the approval.

## Re-test after wording fix, 2026-11-24: PASS
- Fresh sub-agent given only the task name and the current SKILL.md: set-enabled type + 1 code, 1 import, REST READBACK PASS and export compare PASS, about 6 min, no help, no deviation. Main session read the record back from Oracle. Evidence: `gaps-filled/evidence/batch-01-retest/ORA_ZX_MANAGE_TAX_LOOKUP_CODES/`.
- Notes not applied (wording unchanged after this test): which FSCR folder to use is not obvious when several copies exist; worked-example counts go out of date; the log one-liner leaves `\t` and `\/`.
