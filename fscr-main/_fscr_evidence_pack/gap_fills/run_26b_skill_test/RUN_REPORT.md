# Run 26b report: cold test of the Journal Categories skill

## Verdict: PASSED WITH FIXES NEEDED
The 3 categories were created in ETIA-TEST using only the skill. One verify command in the skill (Step 7A) failed as written and needed a one-flag change. VERIFIED

## Time
| Start | End | Minutes | Attempts |
|---|---|---|---|
| 16:12:51 | 16:17 | about 4 | Import: 1 (0 fixes). REST verify: 2 (first failed, see Gap 1). |

## What was done
- Environment: ETIA-TEST, release 11.13.26.10.0. VERIFIED (process log)
- Sign-in: not needed; the cached token worked. Nothing was started on port 8765. VERIFIED
- Export before: process 100004736427677, 147 rows. VERIFIED
- Import: process 100004737392040, Oracle request 4,461,602. Log: "3 rows were processed. 0 rows of them failed", Total Objects Failed: 0. VERIFIED
- New rows: `FSCRT_Run26 Accrual`, `FSCRT_Run26 Payroll`, `FSCRT_Run26 Reclass` (19 characters each, under the 25 limit). VERIFIED
- No deletes, no updates. VERIFIED (compare: 0 removed, 0 changed)
- FSCR folder: 6,120 files before and after, no new files. VERIFIED

## Proof (in `proof/`)
- `verify_rest.json`: REST GET on `journalCategoriesLOV`, HTTP 200, shows the 3 Run26 rows (plus the 3 Run24 rows from before). VERIFIED
- `verify_rows.csv` and `step7b_compare.log`: export after = 150 rows (was 147), added exactly the 3, removed 0, existing changed 0, each has a US translation row, `RESULT: PASS`. VERIFIED
- Import process log. VERIFIED

## Gaps in the skill, with suggested fixes (not applied)
1. **Step 7A command fails (wrong).** `python3 -B -I ... rest_read_categories.py` stops with "Windows Fusion OAuth storage requires pywin32". `-I` hides the user site-packages, where pywin32 is installed on this PC. VERIFIED. Fix: use `python3 -B` (no `-I`) for this helper, since it imports FSCR auth code that needs pywin32. Keep `-I` only for the offline helpers.
2. **Step 7A expectation is out of date (wrong).** "Expect your new rows and no others" is false once earlier runs left FSCRT_ rows (Run 24 rows are still there). VERIFIED. Fix: say "expect your new rows plus any FSCRT_ rows already in the before export", or add a `--prefix FSCRT_Run26` example.
3. **Step 4 example hard-codes Run 24 names (minor).** A reader could copy them and the helper would stop on a clash. Fix: use `FSCRT_RunNN ...` placeholders, and the same in the Step 7B `--expect` lines.
4. **Step 5 "confirm with the person" (minor).** It does not say what to do when the brief already approves the import. Fix: "If the request already names the environment, task and rows, that counts as confirmation."
5. **Step 0 and Rule 10 notes are now stale (minor).** Running in place, and reusing the cached token, now worked. VERIFIED. Fix: mark them as tested in Run 26b; mark `rest_read_categories.py` tested with the `-B` fix.
6. **Step 2 "Unzip it" has no command (minor).** Fix: give a one-line unzip command (for example Python `zipfile`).
7. **Process log has literal `\r\n` text (cosmetic).** Fix: mention it so readers are not confused, or note that the search strings still match.

## Not done / not verified
- Sign-in path (Step 1, port 8765) was not exercised, so it is still untested in a cold run. VERIFIED
- The 3 test rows stay in ETIA-TEST (the skill never deletes). VERIFIED
