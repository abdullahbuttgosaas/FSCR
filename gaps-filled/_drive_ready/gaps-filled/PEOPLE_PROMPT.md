Fill the FSCR gaps for my module. My module is: (module name as written in the tracker).

Do every step yourself. Work in this pack folder. Do not change any FSCR file.

SIGN IN: Set up sign-in from the sign-in file. Do not print sign-in values. Ask me for my initials and use them as <INITIALS>. If the browser says the page can't be reached, ask me to copy the full address from the address bar and paste it here.

MY MISSING TASKS: Read evidence\<my module>\data\coverage.csv. If it does not exist, stop and tell me to run the module test first. Missing tasks are those with no FSCR skill or guide (route only, or neither). Write them to gaps-filled\<module-folder>\my_gaps.csv (module-folder: lower case, hyphens, short).

CHECK EACH TASK (change nothing): does Oracle have a setup file (FSM CSV) or a web service (REST) for it? Use the export and a read-only REST describe. If yes, it can be filled. If no (it needs clicking in screens), do NOT fill it and do not attempt screen automation: add it to gaps-filled\<module-folder>\screen-only.csv with columns task_code, task_name, reason. Sort fillable tasks easy to hard (easy = new stand-alone record, no prerequisites; hard = changes existing settings, long dependency chain, large package, or country-only). Skip any task that would change settings other people use on the shared test environment, and list it in my_gaps.csv with the reason.

BATCHES: 5 tasks per batch, easy first. After each batch, stop and show a short summary (filled, failed, skipped, left). Tell me to upload gaps-filled\<module-folder>\ to the Drive folder FSCR > gaps-filled, then message Abdullah "batch N done". Continue only when I say so.

FOR EACH TASK:
1. Read-only export first.
2. Write gaps-filled\<module-folder>\<task-folder>\SKILL.md (lower case, hyphens, short names) with sections: When to use; Task code; Route (FSM CSV or REST); Steps (export, build rows, import, read back); Checks; Test records created; Risks and limits; Untested parts. The skill must be generic: it must work in any Oracle environment, with no server names, environment names, customer data or values copied from ETIA-TEST.
3. Run the recipe live on ETIA-TEST with a new record named GAPFILL_<INITIALS>_<short name> (uppercase, underscores, no spaces, short). Create new records only. Never edit or delete existing records. Read the result back from Oracle.
4. Fresh test: start a fresh sub-agent with no context. Give it only the task name and the SKILL.md path, and ask it to do the task with a new GAPFILL_<INITIALS>_ record and read it back. It passes only if it finishes and the read-back matches, without help. If it fails, fix the skill and test again. Record failures honestly.
5. Write STATUS.md beside SKILL.md, one "key: value" per line, keys in this order: task_code, task_name, module (exact tracker module name), status (tested only if the fresh test passed, otherwise written or failed), filled_by (my initials), date (yyyy-mm-dd), minutes_to_write, minutes_to_test, waiting_minutes, fresh_claude_pass (yes or no), route, depends_on (task codes or none), test_records, notes (one line).
6. Write CHANGELOG.md: test records created and any fixes.
7. Save 2 or 3 screenshots (rendered before and after read-back, no secrets) in gaps-filled\<module-folder>\evidence\batch-NN\<task-folder>\.

TIME: note start and finish times. Log working minutes (writing and testing) separately from waiting minutes (sign-in, Oracle waits, timeouts). Sign-in time is never counted in a task's minutes.

END OF EACH BATCH: write gaps-filled\<module-folder>\BATCH_NN_RESULT.md with a table of tasks, status, working and waiting minutes, problems, and what is left.

END OF EVERY SESSION: stop and delete every server and process you started. Leave nothing running.
