# Changelog: alternate-name-mapping-rules skill (GoSaaS gap fill, not official FSCR)

## 0.2.0, Run 27c, 2026-11-16
Fixes from the Run 27b cold test (`_fscr_run_27b_skill_test\RUN_REPORT.md`, verdict PASSED WITH FIXES NEEDED). Only files in `_gap_fills` were edited.

| # | Change | Why |
|---|---|---|
| 1 | New Step 0 "Shell, paths and Python flags". Every `/fscmRestApi` command now starts with `MSYS_NO_PATHCONV=1`, and all paths are full `E:/...` paths (FSCR and GAP filled in; only RUN, names and ACCOUNT stay placeholders). The error text is quoted. Notes for PowerShell/cmd (drop the prefix), Linux/macOS, and the no-leading-`/` form (FROM FSCR `rest_client_common.py:70-74`); those three are GUESS. | Run 27b: Git Bash rewrote `/fscmRestApi/...` and the client failed with "REST URL must have a valid HTTPS authority without credentials"; with `MSYS_NO_PATHCONV=1` but `/e/...` paths Python looked for `E:\e\...`. The `MSYS_NO_PATHCONV=1` + `E:/...` form worked. VERIFIED |
| 2 | Step 1 rewritten: run one describe GET first to see if sign-in is needed; if needed, run `fusion_login.py` in the background, wait up to the timeout (280 s; default 300 s, FROM FSCR `fusion_auth.py:32`), check the log every 30 to 60 s; success = `Login complete for standard.` + exit 0; timeout = `Error: Timed out waiting for authorization callback` + exit 1; retry at most 2 more times (3 tries total), then stop and report "sign-in needs a person". Cause of the timeouts kept as GUESS. | Run 27b: the client's own sign-in blocked 300 s and timed out, then `fusion_login.py` timed out at 280 s, the third try worked. VERIFIED |
| 3 | `--open-browser` dropped from the sign-in command, with a note that it is already the default (FROM FSCR `fusion_login.py:61-72`) and that "Opening ... in your browser." prints either way (FROM FSCR `fusion_auth.py:1090`). Added `-u` and a note that output to a file is buffered without it. | Run 27b: the script opened the browser without the flag, and the log was empty until the script ended. VERIFIED |
| 4 | Step 3: check `hasMore`; `true` is fine, you need only one `ZZ_TEST_` account; otherwise use `offset` or the `q` filter (both not tried). | Run 27b got `hasMore: true` and 30 `ZZ_TEST_` accounts in the first 100. VERIFIED |
| 5 | Step 5 now says the order "GET, precheck, POST rule 1, GET, precheck, POST rule 2", with the full commands for rule 2. The second GET is a full read into `fresh_get_before_post2.json`, prechecked for NAME2 only; `before_all.json` stays the Step 7 before file. | Run 27b: the fresh GET was only in Step 1. Also, Run 27b's fresh GET used `limit=1` (token refresh only), so it could not catch a reused name; a full read plus precheck does. VERIFIED (file shows limit 1, hasMore true) |
| 6 | `verify_rules.py verify` has a new check: every earlier rule still has the same payer name, account, bank names, Active, ObjectVersionNumber and LastUpdateDate. It prints `earlier rules unchanged: True/False`. Step 7 lists it as check 5. | Run 27b had to write its own unchanged check. VERIFIED |
| 7 | "Not yet tested" notes updated: front matter `tested_by_fresh_chat`, `origin`, `version` 0.2.0; header note; Step 0 "honest note" removed; Steps 2, 3, 4, 6, 7 now cite Run 27b as VERIFIED; worked example has Run 25 and Run 27b columns; new Rule 10 lists what is still GUESS (PowerShell form, no-leading-`/` form, `offset`/`q` on accounts, a failed POST and its error text, DELETE, the privilege). | Run 27b ran describe, GET, POST, by-ID read and sign-in with FSCR's client. VERIFIED |
| 8 | `_gap_fills\README.md`: "Tested by a fresh chat" = "Yes, Run 27b: worked using only the skill, 2 records, first attempt; wording fixed in Run 27c". "not yet run for this resource" changed to "run for this resource in Run 27b". The "ours, not official FSCR" line kept. | Asked for in Run 27c. |

### Checks run in Run 27c (VERIFIED)
- Helper `verify` on Run 27b `before_all.json` / `after_all.json`, both R27 names, `--account 21541`: `earlier rules unchanged: True (2 checked)`, `RESULT: PASS`, exit 0. `verify_rows.csv` byte-identical to Run 27b's.
- Same, with one earlier rule's ObjectVersionNumber raised by 1 in a scratch copy: `FAIL: earlier rule 300000395050002 'FSCRT_R25 Payer A' changed: ObjectVersionNumber`, exit 1, as intended.
- Helper `verify` on the Run 25 files: still PASS.
- `precheck` with `FSCRT_R27 Payer A` against Run 27b `after_all.json`: FAIL "already exists", as intended. Against Run 27b's `limit=1` fresh GET: FAIL "hasMore=true", as intended.
- One read-only GET, run exactly as Step 2 says (collection, `limit=500`) in Git Bash (MINGW64, bash 5.2.37) with `MSYS_NO_PATHCONV=1` and `E:/...` paths: `HTTP 200`, exit 0, saved token worked (no sign-in, port 8765 never used). 4 rules, `hasMore` false; IDs, names, ObjectVersionNumber, LastUpdateDate and Active identical to Run 27b's `after_all.json`. No POST, PATCH or DELETE sent.
- All outputs went to the session scratch folder, not FSCR or a run folder.

## 0.1.0, Run 27a, 2026-11-16
First version, written from Run 25 (`_fscr_run_25_fill_no_route`). No Oracle calls were made in Run 27a.

| # | What | Source |
|---|---|---|
| 1 | `SKILL.md`: sign-in, read-only describe and count, finding a test customer account, POST body (required, useful and do-not-send fields), sending the POST with FSCR's `fusion_rest_client.py`, reading the response, verifying. Also Rules and limits and a worked example with the Run 25 values. | Run 25 files (VERIFIED), FSCR REST client code (FROM FSCR), Oracle REST docs |
| 2 | `scripts/verify_rules.py`: an offline helper. `precheck` checks planned names before the POST; `verify` compares the before and after collection reads (names present, exact counts, nothing removed, account, active). | New |
| 3 | `_gap_fills\README.md`: one row added for this gap, "Tested by a fresh chat" = not yet. The existing lines are unchanged. | — |

### Lessons carried over from journal-categories
- Do not use `-I` with FSCR scripts (pywin32 lives in the user site-packages folder).
- Run FSCR scripts in place with `-B`.
- Keep every output in a run folder.
- Use placeholders in commands and a "do not reuse these names" note on the worked example.
- If the brief already names the environment, task and rows, that is the approval.

### Checks run in Run 27a (VERIFIED, offline, on Run 25 evidence files)
- `precheck` with the Run 25 names against the before file (0 rules): PASS.
- `verify`, before = `anmr_all.json`, after = `verify_all_rules.json`, both names, `--account 21541`: PASS. Its `verify_rows.csv` matches Run 25's `verify_rows.csv` exactly.
- `precheck` with a name that already exists, and with a name without `FSCRT_`: FAIL, as intended.
- `verify` with only 1 expected name (count 0 + 1 is not 2): FAIL, as intended.
- `verify` with a wrong account: FAIL, as intended.
- `verify` given the describe file instead of a collection: exit 2 ("BAD INPUT"), as intended.
- Test outputs went to the session scratch folder, not into FSCR or a run folder.

### Open points (not tested, GUESS)
- Run 25 sent its GET and POST calls with its own `api.py` and a copy of FSCR's `core/auth`, not with `fusion_rest_client.py`. The client commands in `SKILL.md` follow the client's code but have not been run for this resource. Differences from Run 25: the client sends no `REST-Framework-Version` header, and it does not retry a POST on 401/403.
- The query filter `q=CustomerName LIKE 'ZZ_TEST_%'` on `receivablesCustomerAccountActivities` has not been tried.
- The error text for a bad account or a duplicate name has not been seen.
- Whether DELETE works on these rules has not been tried.
- The required privilege has not been checked.
- A fresh-chat cold test is still to do.
