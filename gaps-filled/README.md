# gaps-filled

**Everything here was built by GoSaaS. It is not official FSCR.** Each skill fills an FSCR "gap": a setup task that has no FSCR skill or guide. The skills use FSCR's own scripts in place; they do not change FSCR files.

## Scope

`gap_index.csv` has one row for every missing task (level b "route only" or c "neither") in these 19 tracker modules of the Run 36 scope map: Common Features, Security, General Ledger, Payables, Receivables, Cash Management, Fixed Assets, Expenses, Revenue Management, Project Financial Management, Purchasing, Procurement, Sourcing and Supplier Management, Inventory Management, Order Management, Manufacturing, Cost Management, Supply Planning, Maintenance. That is 935 rows (Security has none). There are no rows for HCM, Logistics or PLM.

## Layout

```
gaps-filled\
  README.md            this file
  gap_index.csv        one row per gap (935): level, ease, dependencies, status, times, screen_only
  gap_progress.tsv     per-module progress, written by rebuild_index.py (do not edit by hand)
  rebuild_index.py     rebuilds gap_index.csv and gap_progress.tsv from the cards
  GAPS_PLAN.md         counts, ranking, batches, times, risks, open questions
  BATCH1_PART*_RESULT.md  batch 1 run reports
  SETUP_RESULT.md      report of the 2026-11-20 setup (cards, 19-module index, rebuild script)
  batch1_export_check.csv files, column names and row counts from the batch-1 exports (no data)
  gap_index_backup_2026-11-20.csv  the index before the 19-module extension
  (module)\            one folder per tracker module, e.g. common-features, general-ledger
    screen-only.csv    tasks of this module that can only be done on screen (when present)
    (task)\            one folder per task, named from the task, e.g. manage-journal-categories
      SKILL.md         the gap skill
      STATUS.md        the status card (see below); one per SKILL.md
      CHANGELOG.md     changes and test notes
      scripts\         helper scripts (when present)
    evidence\
      batch-NN\
        (task)\        screenshots and rendered read-backs for that task in batch NN (no secrets)
```

- Module folder = the tracker module name in lower case with hyphens (`project-financial-management`, `sourcing-and-supplier-management`). Task folder names are lower case with hyphens too. Keep paths short (Windows fails over 260 characters).
- **Batch 1 evidence is still in the old place**, `gaps-filled\evidence\batch-01\<task-folder>\`, and the batch 1 reports point there. New batches put evidence inside the module folder: `<module>\evidence\batch-NN\<task-folder>\`. The rebuild script skips every `evidence` folder.

## STATUS.md card

One `key: value` per line, keys in this order (all required; write `unknown` when a number was not measured, never a guess):

```
task_code: GL_MANAGE_JOURNAL_CATEGORIES
task_name: Manage Journal Categories
module: General Ledger                 exact tracker module name (one of the 19)
status: tested                         tested | written | failed
filled_by: AB                          initials
date: 2026-11-20                       yyyy-mm-dd
minutes_to_write: 4                    writing the skill + your own live test
minutes_to_test: 3                     the fresh-Claude test
waiting_minutes: 1                     Oracle export/import/REST time; sign-in not counted
fresh_claude_pass: yes                 yes | no
route: FSM CSV                         how the record is created: FSM CSV | REST | both
depends_on: none                       task codes separated by ; or none
test_records: GAPFILL_AB_X1; GAPFILL_AB_X2
notes: one line
```

(The text after the values above is explanation only; a real card has just `key: value`.) If the skill's wording changed after its fresh test, add a last line `retest_after_wording_fix: pending` and remove it after a new fresh test passes.

## Screen-only tasks

Some tasks have no FSM CSV and no REST route; they can only be done on the Oracle screens. **Skip them.** List each one in its module's `screen-only.csv` (columns `task_code,task_name,reason`, one row per task) and run the rebuild. The rebuild marks the row `status = screen-only`, `screen_only = yes`, and leaves it out of the "% done" base. A task that has a card cannot also be screen-only (the rebuild reports it and keeps the card).

## Rebuild the index and progress

From the gaps-filled folder:

```
python rebuild_index.py
```

Standard library only. It reads every `STATUS.md` under the module folders and every `screen-only.csv`, updates the matching `gap_index.csv` rows by task code (`status`, `skill_path`, `filled_by`, `date`, `minutes_to_write`, `minutes_to_test`, `fresh_claude_pass`, `depends_on`, `screen_only`), writes `gap_progress.tsv` (Module, Missing, Tested, Written, Open, Screen-only, % done, Last update) and prints the table. It changes no other file and keeps CRLF line endings. Running it twice gives the same result.

- `% done` = Tested / (Missing - Screen-only) x 100, 0 if that base is 0. `open` and `failed` rows count as Open (an old `not started` value would too). A `tested` or `written` card sets `screen_only = no`.
- It prints PROBLEMS and exits 1 for: a `tested` card with no `SKILL.md` beside it, a task code not in the index, two cards for one task code (neither is applied), a missing key or unknown status, a module (or module folder) not in the list. Fix the card and run it again; good cards are applied anyway.
- The card's `notes`, `waiting_minutes`, `route` and `test_records` stay on the card; the index has no columns for them, and the index `notes` column is never overwritten.

## How Claude should use this folder

1. If this folder is present, read `gap_index.csv` before planning a setup task.
2. Find the task by `task_id` (the FSCR task code). If `status` is `tested` or `written` and `skill_path` is filled, open that `SKILL.md` (path is relative to this folder) and follow it. Prefer a `tested` skill; treat a `written` skill as untested. Read the `STATUS.md` beside it for test records and open retests.
3. If `status` is `screen-only`, do not try to fill it; say it is a screen task.
4. If the task has an official FSCR skill or guide, use FSCR's. Use a gap skill only where FSCR has none.
5. If `depends_on` names other tasks, make sure those records exist first.
6. **Test names: `GAPFILL_<INITIALS>_`** from now on (for example `GAPFILL_AB_RT1`), so records from different people never clash. The batch 1 pilot used plain `GAPFILL_`; earlier runs used `FSCRT_` and `ZZ_TEST_`. Never use customer or demo names.
7. When you finish a gap skill, add its folder here with a `STATUS.md` card, then run `python rebuild_index.py`. Do not edit the status columns of `gap_index.csv` by hand.

## Notes on the two older gaps

- `general-ledger\manage-journal-categories` and `receivables\manage-alternate-name-mapping-rules` are **copies** of `fscr-main\_gap_fills\journal-categories` and `fscr-main\_gap_fills\alternate-name-mapping-rules` (copied 2026-11-18, byte-identical). The originals were not changed.
- Inside those copies, some paths still point to `fscr-main\_gap_fills\...`. That still works because the originals are in place.
- Neither task is a Common Features task in the Run 36 scope map (they sit in General Ledger and Receivables), so they live in those module folders.
