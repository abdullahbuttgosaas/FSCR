# Run 38: cold test of fscr-module-test-pack

**Verdict: Pass with fixes.** A person with nothing but the pack tested a whole module end to end on ETIA-TEST and the independent `verify.md` check passed, but only after 27 pack problems were found and fixed in v2.

> This is a test only. The tracker row and images below are **not** a real tracker entry.

- **Module:** PLM - Quality Management (5 tasks, all route-only CSV; the smallest no-contact module with at least 4 loadable tasks: Transportation 1, Global Trade 7). Initials TC; records `FSCRT_TC_` only.
- **Result:** 5/5 tasks loaded through the Data Loader and read back (status `FSCRT_TC_REVIEW`, issue type `FSCRT_TC_QI1`, action type `FSCRT_TC_QA1`, template `FSCRT_TC_WF1`, lookup `FSCRT_TC_QLKP`/`FSCRT_TC_C1`); 266 existing rows unchanged. Scores: coverage None, Missing 5/5, Plan 3, Runbook 2, Execution 3, Fit Medium.
- **Independent check (`verify.md`, evidence folder only):** round 1 **FAIL** (513 double-counted rows, request numbers not traceable, Execution 4 / Fit Low not supported by the playbook) → fixed; round 2 **PASS** with doubts (no Task Hook proof, Oracle row wording, finish time) → fixed; evidence rebuilt last: `build_evidence.py` PASS, `secret_scan.py` 0 findings.
- **Pack v2:** `fscr-main/fscr-module-test-pack_v2.zip` (6,137 files, `CHANGES.md` first). No official FSCR file changed. Scan: 0 findings in any v2 file; the remaining hits are Oracle's own code and text, already listed in v1.

## Problem log

| # | What a new person hit | Fix | Where in the pack |
|---|---|---|---|
| 1 | No list of the sign-in values (env, URL, Client ID, scope) or the fixed redirect | Listed, with trust prompt and "local file, not chat" | `SETUP.md`; `PLAYBOOK.md` Step 0 |
| 2 | FSCR scripts crash on Windows (`UnicodeEncodeError`) | `PYTHONUTF8=1` | `SETUP.md`, `CLAUDE.md`, `PLAYBOOK.md`, `module_test.md` |
| 3–4 | Step 2a had no commands; project ID `FSCRT_TC_…` rejected | `fscr_project_input.py`, exact commands, lowercase-hyphen ID rule | `PLAYBOOK.md` 2a; new script |
| 5–6 | Unquoted comma silently cut a quote; wrong URL saved the landing page | Strict CSV reader; check each saved page | `kitlib.py`, `plan_builder.py`, `link_checker.py`; 2c |
| 7 | Run Book name, absolute path, `runID`, read-back command missing | Exact Step 3 commands + `runbook_create.json` | `PLAYBOOK.md` Step 3 |
| 8–9 | No CSV-route commands; a full export would re-load every record | 7-step recipe; `fsm_package.py` (only `FSCRT_` rows) | `PLAYBOOK.md` Step 4; new script |
| 10–11 | One-group module gives only 2 sample tasks; image title said "Six" | Fill-up rule (≥4, max 6, labelled); title "N of up to 6" | Step 4, `module_test.md`, `verify.md`, `make_images.py` |
| 12–15 | Upload approval, skipped Task Hook, export timeout, logs in home folder | Rules for each | `PLAYBOOK.md` Step 4/5 |
| 16, 23–26 | Evidence lacked read-back and Task Hook proof; counts double-counted; checker only checked that files exist | `readback_compare.py` (readback, load_log, task_hook, distinct counts); consistency checks | new script; `build_evidence.py`; Step 4 |
| 17–19 | User names in command lines, false name hits, names in exports | `--names @file`, whole names, exports deleted | `kitlib.py` + 4 scripts; Steps 7–8 |
| 20 | `--help` paths did not match where scripts run | `../../work/…` everywhere | 7 scripts; Folders |
| 21 | Scoring rules led to Execution 4 / Fit Low | Clarified rules for hand-built CSV and coverage None | Step 5 |
| 22, 27 | `verify.md` paths/commands wrong; finish time before rework | Fixed paths, commands, step 9 checks; finish time includes rework | `verify.md`; Step 8 |
| Ex. | Example rows used old counts | Common Features 227 / 148/227, Procurement 41 / 26/41, SSM 58 / 26/58; coverage and tracker-row images rebuilt | `examples/*`; `CHANGES.md` |

Full detail: `CHANGES.md` rows 1–27 in the v2 zip.

## Could not be fixed in the pack

- **Sign-in values.** The 4 values cannot ship in the pack, so a new person must get them from an admin. In this test they were recovered from this machine's earlier sign-in, which is outside the pack and counts as a failure of the "nothing of ours" rule.
- **No FSCR content for these tasks.** FSCR has no skill, guide or Task Hook rule for the 5 tasks, so every Run Book step is manual and the Task Hook result is `not_applicable`. That is a gap in FSCR for GoSaaS to build, not something the pack can fix.
- **Example plan figures.** The examples' plan, Run Book and six-task figures and their images are those runs' own measurements on the older scope. They are labelled, not redone.

## Time log

| Part | Start | Finish | Minutes |
|---|---|---|---:|
| Module test, including rework after both checks | 17/11/2026 16:38 | 17/11/2026 17:15 | 37 |
| Pack v2 build, scan and this report | 17/11/2026 17:15 | 17/11/2026 17:22 | 7 |
| **Total** | 17/11/2026 16:38 | 17/11/2026 17:22 | **44** |

Files here: `tracker_row.md` and `images/01–04` (copied from the evidence folder). Nothing is left running (port 8765 free, no Python or browser processes started by this test).
