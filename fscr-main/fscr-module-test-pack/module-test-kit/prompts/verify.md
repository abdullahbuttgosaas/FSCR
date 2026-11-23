# Prompt: independent check of a finished module run

Give this to a **new** Claude chat (Opus 5.5) opened on this pack's folder. It must not have run the test itself.
Replace `{MODULE}` with the module name. The check only reads files: it never signs in to Oracle and never changes
the evidence.

---

Check the finished FSCR module test in `evidence/{MODULE}/` independently. Read only: do not sign in to Oracle, and do not
change any file in `evidence/`. Put any helper output in `work/verify_{MODULE}/`. Use the scripts in
`module-test-kit/scripts/` and the rules in `module-test-kit/PLAYBOOK.md` and `module-test-kit/SHEET_FILL_GUIDE.md`.

1. **Counts.** Run `scope_filter.py --module "{MODULE}" --out work/verify_{MODULE}`. Compare Total Tasks, Missing (N/total),
   a/b/c and the proposed coverage with `tracker_row.md`, `RESULT.md` and `data/coverage.csv`. Every number must match.
2. **Plan.** Run `plan_builder.py` with `evidence/{MODULE}/data/links_input.csv` and `data/oracle_docs`, writing to
   `work/verify_{MODULE}`. The (a), (b) and (c) numbers must equal those in `RESULT.md` and `data/plan_summary.json`.
   Every link with status `sourced` must pass the quote check. A link presented as verified without a URL and a quote that
   passes is a FAIL.
3. **Run Book.** Compare `RESULT.md` with `data/runbook_summary.json` (steps, route, manual, manual with CSV, prerequisites,
   links in order). Owner or validation-step fields must not be used as criteria.
4. **Scores.** For each of Plan accuracy, Runbook quality and Execution & validation, quote the Guide's 1/3/5 wording
   from the playbook and say whether the score and its reason fit it. Check the Fit rating and FSCR coverage against
   their Guide meanings. Execution must not count tasks that have no CSV or API in Oracle.
5. **Images.** Open each of the 4 PNGs in `images/`. Check that every number and value in them equals the source file
   named in its footer (`coverage.csv`, `plan_summary.json`/`runbook_summary.json`, `six_tasks.csv`, `tracker_row.md`).
   No more than 4 images. No tokens, user names, e-mail or environment addresses visible.
6. **Tracker row.** Run `tracker_row.py check evidence/{MODULE}/tracker_row.md`. It must PASS (formats: Missing N/total,
   dates dd/mm/yyyy, Status Completed, bullets, no owners in the gap column).
7. **Known mistakes.** Flag any of these:
   - a Run Book create that was resent after a timeout (two Run Books for one run);
   - a REST object load attempted when the Data Loader can't load it, with no switch to the FSM CSV package;
   - more than 2 tries at an import that needs an internal ID column;
   - Task Hook rule results with no real check behind them;
   - an existing business unit (or any existing record) edited or deleted, or a record not named `FSCRT_<initials>_`;
   - a task with no CSV or API in Oracle counted against FSCR;
   - owner or validation-step fields used as criteria;
   - an unsourced dependency presented as verified.
8. **Secrets.** Run `secret_scan.py evidence/{MODULE}`. It must find nothing.
9. **Time and clean-up.** `RESULT.md` has the Start/Finish/Minutes table and says all processes were stopped.

Report **PASS** or **FAIL** at the top, then a table: check, result, reason (with file and number). List every
mistake found. Finally, stop any process you started and confirm nothing is left running.
