Model: Opus. (Long, careful multi-step work with Oracle: Opus makes fewer mistakes and needs no help between batches.)

MY MODULE: <module name exactly as in the tracker, e.g. General Ledger>
MY INITIALS: <2 or 3 letters, e.g. AB>

Fill every FSM CSV / REST gap of my module, batch after batch, until none is left. Do every step yourself. Do not ask me anything after this message, between batches or at the end; decide by the rules below and write your reasons in the reports. Work in this pack folder. Never change an FSCR file. Never print or save sign-in values, tokens, secrets, server addresses or user names. Do not commit or push.

Names used below: MOD = my module folder = the module name in lower case with hyphens (General Ledger -> general-ledger; Project Financial Management -> project-financial-management). GF = the pack's gaps-filled folder. WORK = a folder OUTSIDE the pack and outside any git repo, e.g. a "gw\<MOD>" folder next to the pack folder (no folder in its path named exactly "project"): every export, payload, log and run folder goes there, because exports hold user names. PREFIX = GAPFILL_<INITIALS>_ (upper case).

1. SIGN IN
- Set up sign-in from the sign-in file (fscr-signin-values.txt). Never type or print its values. FSCR's listener uses port 8765: check the port is free first; if it is busy, wait and retry for up to 10 minutes.
- If the browser says the page can't be reached, ask me once to paste the full address from the address bar (http://127.0.0.1:8765/oauth/callback?code=...). This is the only thing you may ask me.
- A sign-in lasts about an hour; an expired one makes calls fail with 401/403 or hang. Note the sign-in time; after about 50 minutes, or on any 401/403, sign in again (same steps) and carry on. Sign-in time is waiting time, never task time.

2. MY GAPS (every sitting starts here, so pasting this prompt again resumes the work)
- Read evidence\<my module>\data\coverage.csv. If it does not exist, STOP and tell me: "Run the module test for <module> first; coverage.csv is missing." Also read GF\gap_index.csv (the rows of my module) and GF\README.md.
- Missing tasks = tasks with no FSCR skill or guide (level "route only" or "neither"). Write or update GF\MOD\my_gaps.csv (task_code, task_name, level, ease, depends_on, decision, reason).
- Skip tasks that are already done: a STATUS.md card under GF\MOD\ with status tested, or failed with a proven cause and a next step. Re-open a card that has retest_after_wording_fix: pending, or a known wrong sentence in its CHANGELOG: fix and re-test it first.
- Screen-only: a task with no FSM CSV (check with a read-only export) and no REST resource (check with a read-only REST GET) is screen-only. Do NOT fill it and do not automate screens: add it to GF\MOD\screen-only.csv (task_code, task_name, reason). Skip a task that would change settings other people use on the shared test environment (shared options, seeded records, existing users, security, live tax); write it in my_gaps.csv with the reason (it is not screen-only).
- Order the rest easiest first: easy = a new stand-alone record with no prerequisite; then a record that needs a prerequisite you can create; hard = long dependency chain, large package, rows written in full, or country-only. Group tasks that share a package (same export files).

3. BATCHES
- 5 tasks per batch, easiest first. Number batches from 01 in GF\MOD (continue the numbering of earlier sittings).
- After each batch write GF\MOD\BATCH_NN_RESULT.md (time log, table of tasks with status and working/waiting minutes, test records and ProcessIds, problems and findings, what is left), run python rebuild_index.py in GF, fix any problem it prints, then start the next batch at once. Do not stop between batches and do not wait for me.
- Keep going until every CSV/API gap of my module is tested, or failed with a proven cause (step 7), or listed as screen-only or skipped with a reason.
- Fresh tests of tasks that share an FSM package AND an export scope run one after the other; tasks with different packages or scopes may run in parallel.

4. BEFORE EACH TASK: PREREQUISITES
- Read the task's FSCR knowledge (catalog, product guidance) and Oracle's docs for it (docs.oracle.com: the task, its tables and REST resources). List what must exist first (a parent record, a regime option row, a party or profile, a customer, a code from another task).
- Every prerequisite becomes a numbered step in the SKILL.md and is named in depends_on (task codes; or a short description when it is data, e.g. "a test customer with a third-party tax profile").
- Create prerequisite records yourself through CSV or REST with PREFIX names (reuse a tested gap skill from GF if there is one), never by hand on a screen. Check first that it does not already exist (REST GET or a new export); never create it twice.

5. EACH TASK
a. Read-only export first (FSCR shared/setup-export/task-level-export, --data, run folder under WORK). Look at the files, columns and row counts. Reuse the helpers in GF\common-features\*\scripts (build_fsm_package.py, compare_fsm_exports.py, rest_read.py, inspect_export.py, text_png.py, template_row.py, copy_parent_rows.py) instead of writing new ones.
b. Write GF\MOD\<task-folder>\SKILL.md (task folder: lower case, hyphens, short). Generic: it must work in any Oracle environment, with placeholders; never ETIA-TEST data, environment or server names, hard-coded IDs, internal numbers, local paths or user names. Read any id the row needs live by REST in the skill; never copy an id from an export. Sections: what it is and when to use; placeholders; sign-in; prerequisites (numbered steps); export; build rows; import; read back; rules and limits; worked example (codes and ProcessIds only). Label claims VERIFIED (seen live) or GUESS.
c. Load ONE new test record named PREFIX<short name> (upper case, underscores, short; e.g. GAPFILL_AB_JC1) through FSCR's import or REST. New records only: never edit or delete an existing record. Approval: this prompt approves new test records on the shared test environment.
d. Read it back from Oracle: a second export compared with the first (only your rows added, nothing removed or changed) and REST when a resource exists. Keep the FSCR ProcessId of every import; it is the only key to the full process log.
e. Fresh test: a fresh sub-agent with no context, given ONLY the task name and the SKILL.md path (plus FSCR root, PREFIX, a new record name ending in F, a run folder under WORK, the approval and "never print tokens, server addresses or user names"). It passes only if it finishes without help and its record reads back. Read its record back yourself.
f. Any wording change to the SKILL.md after its fresh test, or any wrong sentence a tester reports: fix it and run the fresh test again in this sitting (new name ending in R). Never leave retest_after_wording_fix: pending or a known error behind. Tester notes that are only suggestions may stay unapplied; list them in the CHANGELOG.
g. STATUS.md beside SKILL.md, one key: value per line, keys in exactly this order (see GF\README.md): task_code, task_name, module, status (tested | written | failed), filled_by, date, minutes_to_write, minutes_to_test, waiting_minutes, fresh_claude_pass, route, depends_on, test_records, notes. "tested" only when the fresh test passed. Plus CHANGELOG.md (test records, ProcessIds, fixes, tester notes).
h. Evidence in GF\MOD\evidence\batch-NN\<TASK_CODE>\: 01_missing, 02_found, 03_skill, 04_test_result, 05_fresh_test (.png, rendered from UTF-8 text with text_png.py). Scan them: no user names, tokens, server addresses or environment names (FSCR puts the environment name in its output file names: never copy those).
i. Time: note start and finish times. Working minutes (writing, own live test, fresh test) are separate from waiting minutes (Oracle export/import/REST waits, sign-in, timeouts).

6. LESSONS (from batches 1 to 4; follow them)
- Generic database error at the insert (JBO-26041 or similar, often after "1 rows processed, 0 failed" at validation): fill CreatedBy and LastUpdatedBy with the export metadata's SubmittedBy value, read at run time. Never hard-code or print a user name.
- Round trip: take a working record from a read-only export and re-import it unchanged under a new PREFIX code; it proves whether the CSV path works for the object.
- Hierarchical (profile-style) packages: a child row is processed only when its parent row is in the same ZIP. Copy the parent unchanged with copy_parent_rows.py; a seeded parent may go in only unchanged, and the after-export must show it "changed 0". The import log counts only the top object, so the after-export compare is the proof.
- Some objects need extra rows to be complete (for example denormalized rows of fiscal classification codes); compare with a working record to find them.
- Rows written in full (empty export): read the required values from Oracle's errors (JBO-27014 "... is required" names the column) and Oracle's table docs; read lookup codes live by REST (standardLookups/<TYPE>/child/lookupCodes).
- Dropped connection after an import started: the import still runs. Never import again. Wait 2 minutes, then check whether the record exists (new export or REST) and continue from there.
- Length limits: names and text may have a maximum (e.g. 15 or 30 characters) or a minimum (MinLength for TEXT reporting types). Find the limit in the live test, give the builder --max-len, and count the fresh tester's name (PREFIX + about 4 characters) against it.
- A party already has a profile when another skill created it (e.g. a legal authority comes with a tax authority profile): never send a second one, it would update the first. Make a new test party without it.
- Records that are data, not setup (e.g. a customer for tax exemptions) can be created by FSCR's REST client (core/fusion-api/rest-api-client/scripts/fusion_rest_client.py supports /crmRestApi and POST). Always GET first, POST once.
- Tax content: work only on your own not-live test taxes; a tax regime needs its global configuration owner option row before statuses, rates or rules can be loaded (see GF\common-features\manage-tax-regimes Step 7).

7. FAILURE PROTOCOL (same sitting)
- Up to 3 tries per task, each after a written diagnosis (read the process log through the ProcessId; change one thing at a time). A refused row creates nothing; confirm with an export before the next try.
- After 3 failed tries: check for a missing prerequisite (step 4); do the round trip; compare your row column by column with a working record. Fix and retry if that finds the cause.
- Only then write status failed, with the proven cause (the exact error and what proves it) and the exact next step, in STATUS.md notes, CHANGELOG.md and the batch report. Never write "parked", "pending" or "blocked" without a cause.

8. FINAL CHECK (before you finish the sitting)
- Every task of my module is tested, failed with a proven cause and next step, screen-only, or skipped with a reason. No retest is pending; no known wrong sentence is left in a SKILL.md.
- Run python rebuild_index.py in GF; it must print "No problems".
- Write GF\MOD\MODULE_RESULT.md: counts (tested, failed, screen-only, skipped, left), working and waiting minutes per task and in total, failed tasks with their causes and next steps, what is left for the next sitting, and the test records created.
- Tell me, in 6 lines or fewer: the counts, and "Upload the folder gaps-filled\MOD to the Drive folder FSCR > gaps-filled, then message Abdullah: done".
- Stop and delete every server and process you started (no Python left, port 8765 free). Leave WORK outside the pack; never add it to git.
