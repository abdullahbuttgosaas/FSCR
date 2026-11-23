# Run 26b log
Start: 2026-11-15 16:12:51 (local). VERIFIED

| Time | Step | Action | Result |
|---|---|---|---|
| 16:12 | Read | Read SKILL.md; made run folder; env line says ETIA-TEST | VERIFIED |
| 16:13 | 0 | Ran FSCR in place with -B and --output-dir; FSCR file count 6120 before | VERIFIED |
| 16:13 | 1 | Sign-in skipped: cached token worked on the first export | VERIFIED |
| 16:13-16:14 | 2 | Export before, process 100004736427677, 11,451 bytes, 147 rows (incl. 3 FSCRT_Run24 rows), no Run26 rows | VERIFIED |
| 16:14 | 3-4 | build_package.py: 3 rows, names 19 chars each, zip written | VERIFIED |
| 16:15 | 5 | Import, process 100004737392040, attempt 1, ~22 s | VERIFIED |
| 16:15 | 6 | Process log: "3 rows were processed. 0 rows of them failed", Total Objects Failed: 0, Oracle request 4,461,602 | VERIFIED |
| 16:15 | 7A try 1 | rest_read_categories.py with `-B -I` (as written in skill): FAILED, "Windows Fusion OAuth storage requires pywin32" | VERIFIED |
| 16:16 | 7A try 2 | Cause: `-I` hides user site-packages where pywin32 is installed. Re-ran with `-B` only: HTTP 200, 6 rows (3 Run24 + 3 Run26) | VERIFIED |
| 16:16 | 7B | Export after, process 100004736418683, 11,684 bytes; compare_exports.py: 147 -> 150, added 3, removed 0, changed 0, RESULT: PASS | VERIFIED |
| 16:16 | Check | FSCR file count still 6120, no files newer than run start; nothing listening on 8765 | VERIFIED |

## Step clarity
| Step | Clear? | Note |
|---|---|---|
| 0 | Clear | In-place run worked; untested note can now be removed. VERIFIED |
| 1 | Clear | Not needed. |
| 2 | Clear | "Unzip it" gives no command; trivial. |
| 3 | Clear | |
| 4 | Clear, small edit | Example uses Run24 names; I changed them to Run26. |
| 5 | Mostly clear | Says confirm with the person; my brief already gave approval, so I went ahead. |
| 6 | Clear | Log text has literal `\r\n`; still readable. |
| 7A | WRONG | `-I` breaks the helper on this machine. Also "expect your new rows and no others" is wrong once earlier runs left FSCRT_ rows. |
| 7B | Clear | |
