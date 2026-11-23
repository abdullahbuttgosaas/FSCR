# Changelog: journal-categories skill (GoSaaS gap fill, not official FSCR)

## 0.2.0, Run 26c, 2026-11-15 (16:37 to 16:41)
Fixes from the Run 26b cold test (`_fscr_run_26b_skill_test\RUN_REPORT.md`, verdict PASSED WITH FIXES NEEDED).

| # | Change | Why |
|---|---|---|
| 1 | Step 7A command: `python3 -B` instead of `python3 -B -I`. Same fix in the helper's usage text. New Rule 11 says when to use `-I`. | Run 26b: `-I` hid the user site-packages, so pywin32 was not found ("Windows Fusion OAuth storage requires pywin32"). Without `-I` it worked. VERIFIED |
| 2 | Step 7A now says to expect the new rows **plus** all FSCRT_ rows from earlier runs, and gives an exact check. `rest_read_categories.py` got `--before-dir` and `--expect`: it checks that the new names are present and that REST count = FSCRT_ rows in the before export + new rows, then prints `REST CHECK: PASS/FAIL`. Limit raised from 50 to 500, with a warning if `hasMore` is true. | Run 26b: "expect your new rows and no others" was wrong (6 rows came back: 3 from Run 24 + 3 new). VERIFIED |
| 3 | Steps 4 and 7 use placeholders (`FSCRT_RunNN ...`, `NAME1..NAME3`). The worked example is now a two-column table with Run 24 and Run 26b values, both VERIFIED, with a "do not reuse these names" note. Same placeholder in `build_package.py` usage text. | Copying the Run 24 names would hit the helper's clash stop. |
| 4 | Step 5: added the confirmation rule. If the brief already names environment, task and exact rows and says to proceed, that is the approval; log one line and do not ask again. Otherwise stop and ask. | Run 26b: the skill did not say what to do when the brief already approved the import. |
| 5 | Step 2: added a Python unzip one-liner and the expected 3 file names and row counts. | Run 26b: "Unzip it" had no command. |
| 6 | Step 6: says the process log shows `\r\n` as literal text and this is normal. | Run 26b noted it. VERIFIED |
| 7 | Stale "not tested yet" notes updated to VERIFIED (Run 26b): running FSCR in place, cached token reuse, `rest_read_categories.py` (without `-I`), Steps 2 to 7B. Front matter `tested_by_fresh_chat` and `version` updated. Rule 10 lists what is still untested (sign-in on port 8765, the import-result fallback script): kept as GUESS. "Categories cannot be deleted" kept as GUESS. | Run 26b tested these. |
| 8 | `_gap_fills\README.md`: "Tested by a fresh chat" = Yes, Run 26b; helper scripts described as 2 offline + 1 read-only REST. | Asked for in Run 26c; the old "3 offline helper scripts" was not accurate. |

### Checks run in Run 26c (VERIFIED)
- Unzip one-liner on the Run 26b before ZIP: 3 files, identical to Run 26b's unzipped folder.
- `build_package.py` on the Run 26b before export with the Run 26b names: all 3 output files byte-identical to the Run 26b payload.
- `build_package.py` on the Run 26b after export with a Run 26 name: refused ("Already exist in the export"), exit 1, as intended.
- `compare_exports.py` on the Run 26b before/after exports: 147 → 150, `RESULT: PASS`; `verify_rows.csv` identical to Run 26b's.
- `rest_read_categories.py` run exactly as Step 7A says (one GET, read-only): HTTP 200, 6 rows, names present, count 3 + 3 = 6, `REST CHECK: PASS`. No sign-in needed. FSCR file count 6,120 before and after.
- All outputs went to the session scratch folder, not FSCR or a run folder.

## 0.1.0, Run 26a, 2026-11-15
First version, written from Run 24.
