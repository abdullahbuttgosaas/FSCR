# Run 27b: cold test of the alternate-name-mapping-rules skill

## Verdict: PASSED WITH FIXES NEEDED
Both rules were made and proven using only the skill. But the skill's commands did not run as written in Git Bash on Windows, and sign-in took 3 tries. VERIFIED

## Time and attempts
| Item | Value |
|---|---|
| Start | 2026-11-16 12:07:27 (local) |
| End | 2026-11-16 12:19:18 (local) |
| Total | about 12 minutes (about 8 of them waiting on sign-in timeouts) |
| Sign-in attempts | 3 (2 timed out, 3rd worked). VERIFIED |
| Step 2 command attempts | 3 (2 failed on shell path handling). VERIFIED |
| POSTs | 2, both HTTP 201 on first try, 0 fixes. VERIFIED |

## What was made (VERIFIED, ETIA-TEST, user Configuration.TEST)
| AlternateNameId | AlternatePayerName | Account | Customer | Bank / Branch | Active |
|---|---|---|---|---|---|
| 300000395049051 | FSCRT_R27 Payer A | 21541 | ZZ_TEST_CU_2589_14_OK | - | Y |
| 300000395044061 | FSCRT_R27 Payer B | 21541 | ZZ_TEST_CU_2589_14_OK | FSCRT_R27 Test Bank / FSCRT_R27 Test Branch | Y |

## Proof (all in this folder)
- `before_all.json`: 2 rules (FSCRT_R25 Payer A and B). VERIFIED
- `post_rule1.json`, `post_rule2.json`: HTTP 201 responses. VERIFIED
- `after_all.json`: 4 rules. VERIFIED
- `verify_result.txt`: helper `RESULT: PASS` (total 2 + 2 = 4, FSCRT_ 2 + 2 = 4, nothing missing, account 21541, active). VERIFIED
- `verify_by_id_1.json`, `verify_by_id_2.json`: reads by ID, HTTP 200. VERIFIED
- `unchanged_check.txt`: the 2 earlier rules have the same ID, name, account, Active, ObjectVersionNumber and LastUpdateDate before and after. VERIFIED
- `verify_rows.csv`, `precheck.txt`, `describe.json`, `accounts.json`, `run_log.md`, `login_27b*.log` (no tokens in them).
- No PATCH, DELETE or Upsert-Mode was sent. VERIFIED (only the commands in `run_log.md` were run)

## Where the skill was unclear, wrong or missing a detail
| # | Step | Problem | Suggested fix |
|---|---|---|---|
| 1 | 2, 3, 5, 7 | Commands are in `bash` blocks. In Git Bash on Windows, the resource path `/fscmRestApi/...` is rewritten into a Windows file path, and the client fails with "REST URL must have a valid HTTPS authority without credentials". VERIFIED. I fixed it with `MSYS_NO_PATHCONV=1` plus `E:/...` style file paths; this was my own shell knowledge, not from the skill. | Add a Windows note: run in PowerShell, or in Git Bash set `MSYS_NO_PATHCONV=1` and write file paths as `E:/...` (not `/e/...`). Quote the error text so readers spot it. |
| 2 | 1 | "Try Step 2 first, the client signs in by itself" hides that the client then blocks up to 300 s waiting for the browser. Two sign-ins timed out; the third finished by itself. VERIFIED. Why it failed twice: GUESS (browser state). | Say: sign in on purpose first (Step 1 command), run it in the background, allow ~5 min, and if it times out retry once before stopping. Mention the exact timeout text. |
| 3 | 1 | Without `--open-browser` the script still printed "Opening Oracle Identity Cloud login in your browser" and completed. VERIFIED (log). So the flag's effect is unclear. | State what `--open-browser` changes, or drop it. |
| 4 | 1 | Output of `fusion_login.py` is buffered when sent to a file, so the sign-in link and progress are not visible until it ends. VERIFIED (empty log mid-run). | Suggest `python -u -B ...` when logging to a file. |
| 5 | 3 | `limit=100` returned `hasMore: true`; skill does not say this is fine. VERIFIED. ZZ_TEST_ accounts were in the first 100. | Add: "hasMore can be true; you only need one ZZ_TEST_ account. If none in the first page, use offset or the q filter." |
| 6 | 5b | "Fresh GET right before each POST" is only in Step 1, not repeated before POST 2 in Step 5b. VERIFIED (text). | Repeat it in 5b: "GET, POST rule 1, GET, POST rule 2". |
| 7 | 7 | Helper checks earlier rules are not missing, but not that they are unchanged. I added my own check. VERIFIED (helper output). | Add an "unchanged" check (same ObjectVersionNumber and LastUpdateDate) to `verify_rules.py verify`. |
| 8 | Top | `tested_by_fresh_chat: "not yet"` and Step 0 "honest note" say client commands were never run. Now they have been, for GET, describe, POST and by-ID read. VERIFIED | Update both to point at Run 27b. |

## Clean-up
- All sign-in processes I started have ended; the first one I stopped. Port 8765 has no listener. VERIFIED (netstat)
- I did not edit any FSCR file or the skill. VERIFIED
