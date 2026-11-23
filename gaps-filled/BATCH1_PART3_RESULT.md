# Batch 1, part 3: five stand-alone Common Features tasks (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-20. Tested on ETIA-TEST only (release 11.13.26.10.0). No FSCR file was changed; nothing was written outside `gaps-filled` except temporary files in Claude's scratchpad (deleted at the end).

| Start | Finish | Note |
|---|---|---|
| 16:32:17 | 17:07:37 | Reading docs, sign-in check, 5 read-only exports (run together, 16:33:24 to 16:34:04), 5 tasks, 5 fresh tests in the background, index, report, cleanup. |

Sign-in (not counted in any task):
- 16:32:44 to 16:33:16: the sign-in values matched the sign-in file (checked without printing them) and the cached token was still valid.
- 16:55:40 to 16:56:18: the token had expired (it lasts about an hour), so a second browser sign-in was needed. No address paste was needed.

## Results

| # | Task | Status | Working min (write + own live test) | Waiting min (Oracle, hangs) | Fresh test | Fresh test min |
|---|---|---|---:|---:|---|---:|
| 1 | Manage Document Sequence Categories (`FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES`) | tested | 4 | 1 | PASS (yes) | 3 |
| 2 | Manage Conversion Rate Types (`GL_MANAGE_CONVERSION_RATE_TYPES`) | tested | 2 | 1 | PASS (yes) | 2 |
| 3 | Manage Applications Core Attachment Categories (`FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_CATEGORIES`) | tested | 2 | 1.5 | PASS (yes) | 3 |
| 4 | Manage Applications Core Value Sets (`FND_MANAGE_APPLCORE_VALUE_SETS`) | tested | 3 | 11 | PASS (yes) | 3 |
| 5 | Manage Transaction Calendars (`GL_MANAGE_TRANSACTION_CALENDARS`) | tested | 3 | 2.5 | PASS (yes) | 2 |
| | **Total** | 5 of 5 tested | **14** | **17** | 5 of 5 | **13** |

- Minutes are rounded from the run's time log, with Oracle export, import and REST times split out as waiting.
- Task 4's waiting includes about 8.5 minutes lost to a REST read that hung because the token had expired: the REST client silently waits for a browser sign-in. The sign-in itself is not counted.
- The fresh tests ran in the background while the next task went on. All 5 fresh testers finished on 1 import attempt each with no help.
- The main session then read each fresh record back from Oracle: REST for tasks 1, 2 and 4, a new export for tasks 3 and 5. All matched.
- Plan estimate (GAPS_PLAN.md section 3) for these 5 tasks: write 25 + 35 + 30 + 25 + 20 = 135, test 15 + 20 + 20 + 20 + 15 = 90. Actual: 14 working and 13 testing, plus 17 waiting.

## What was reused
- **From FSCR, in place:**
  - the export and import scripts (`shared/setup-export`, `shared/setup-import`);
  - the REST client;
  - the lookups resource (once, for the Applications Core module id);
  - the value-sets REST resources (read-back);
  - the attachments skill's route (FSM CSV import).
- **From earlier parts:**
  - the journal-categories recipe and rules (new rows only, keep metadata XML, quoted CSV, the process log is the real result, compare exports);
  - the log-reading one-liner, the Git Bash rules and the evidence renderer idea.
- **New generic helpers.** Task 1 wrote 5 helpers in `common-features/manage-docseq-categories/scripts/`. They work on any FSM CSV package because the files, keys and columns are given as arguments:
  - `inspect_export.py`
  - `build_fsm_package.py`
  - `compare_fsm_exports.py`
  - `rest_read.py`
  - `render_readback.py`
- **Tasks 2 to 5 used those helpers unchanged**, apart from two options added on the way: `--json-out` for export-based read-backs, and `@file` arguments for calendar dates. The only new script was `calendar_rows.py` (task 5). This is why tasks 2 to 5 took 2 to 3 working minutes each.

## Test records created (all new; none edited or deleted; may not be deletable)
| Task | Live test (main session) | Fresh test (sub-agent) |
|---|---|---|
| 1 | doc sequence category `GAPFILL_DSC_T1` | `GAPFILL_DSCF1_FRESH1` |
| 2 | rate type `GAPFILL_CRT_T1` | `GAPFILL_CRTF1_A1` |
| 3 | attachment category `GAPFILL_ATC_T1` | `GAPFILL_ATCF1_A1` |
| 4 | value set `GAPFILL_VS_T1` + values `GAPFILL_A`, `GAPFILL_B` | `GAPFILL_VSF1_FRESH1` + `GAPFILL_F1A`, `GAPFILL_F1B` |
| 5 | calendars `GAPFILL_TC_T1` (no dates) and `GAPFILL_TC_T2` (7 dates) | `GAPFILL_TCF1_DEC07` (7 dates) |

Each task's CHANGELOG.md lists its records. None is assigned or linked to anything:
- no document sequence;
- no daily rates;
- no attachment entity;
- no flexfield;
- no ledger.

**Risks:** the rate types appear in every rate type list. The document sequence categories sit on the General Ledger journal header table.

Evidence is in `evidence/batch-01/<task-folder>/`, 2 or 3 images per task, before and after. They are rendered read-backs with no secrets:
- tasks 1, 2 and 4 show REST read-backs;
- tasks 3 and 5 show export rows, because those objects have no REST resource.

## Problems and findings
1. **Two objects have no REST resource.** Attachment categories and transaction calendars returned HTTP 404 for 5 likely resource names each. Their read-back is the after-export plus the compare. Both exports did show the new rows.
2. **Value sets cannot be created by REST.** This matches FSCR's own skill. The FSM CSV package works, and FSCR's REST resources read the result back. Two traps:
   - The REST key is the value set **code**: the numeric id gives HTTP 404.
   - The Applications Core `ModuleId` is required. An empty one fails with `ORA-01400`. That was my own scripting error on attempt 1.
   - The ModuleId is read generically from the seeded `YES_NO` lookup. With it, the new value set also shows in the scoped export (0 rows before).
3. **Transaction calendar dates need `DayOfWeek`.** Without it, Oracle rejects the whole calendar (`JBO-27014`) and creates nothing. With `MON`..`SUN` and dates as `yyyy/mm/dd`, the import passed. A calendar header alone imports cleanly, but Oracle then makes no dates itself.
4. **Document sequence categories need a real table.** The table, its ApplicationId and its ModuleId are taken together from an existing export row, so nothing is guessed. The export also shows that General Ledger makes one category for each journal category. Earlier journal-category test rows (FSCRT_) appear in it.
5. **Token expiry hangs REST silently.** After about an hour, a REST call waited for a browser sign-in with no output. The value-sets and calendar skills now say to put `timeout 120` in front of REST calls, and what a hang means.
6. **The builder's prefix check caught my own mistake.** In task 3 I gave a display name without the prefix; the check stopped it. This cost seconds, not an import.
7. **Fresh testers' notes.**
   - Applied as wording, not re-tested: the step order in task 2, and the token-hang advice.
   - Left as notes in each CHANGELOG: example counts go out of date, the FSCR folder is only described, and the helpers live in another skill's folder.
8. **Cleanup.** The work folder `gaps-filled/_work_b1p3` (exports, logs, payloads, read-back JSON) and the scratchpad test folders were deleted. The sign-in listener exited after the sign-in, and no Python process was left running.

## What should change in GAPS_PLAN.md
1. **Mark these 5 tasks tested** in sections 3 and 5. With parts 1 and 2, batch 1 is complete: 10 of 10 tested. Update the counts in section 1.
2. **Make the generic helpers the default for group P7 and similar.** Move `manage-docseq-categories/scripts` to a neutral shared folder, for example `gaps-filled/_shared/fsm-scripts`, so cards do not depend on another task's folder. Several fresh testers raised this.
3. **New estimates for a simple FSM-CSV task with the helpers:** about 2 to 4 working minutes, 1 to 2 minutes of Oracle waiting, and 2 to 3 minutes for a fresh test. The first skill of a new package, without helpers, was about 5 to 11 minutes in parts 1 and 2.
4. **Add a rule:** check for a REST read resource first. Where there is none (attachment categories, transaction calendars), the after-export plus compare is the proof, and the card must say so.
5. **Add a rule:** where an export is empty or scoped, get the ModuleId by REST from a seeded record of the same module. Never leave it empty and never copy it into a skill. This is the same lesson as part 2.
6. **Add a rule about sign-in:** plan a second sign-in after about 50 minutes of a run. Put a timeout on REST calls so that an expired token shows as a stop, not a hang.
7. **The second batch is unblocked:**
   - Daily Rates can use `GAPFILL_CRT_T1`.
   - Document Sequences can use `GAPFILL_DSC_T1`.
   - The 3 descriptive flexfield tasks can use `GAPFILL_VS_T1`.
   Each needs your decision before it touches shared setup (for example, assigning a sequence).
8. **Test names:** this part used `GAPFILL_` again, while README rule 5 still says `ZZ_TEST_` or `FSCRT_`. Please pick one so that the README can be updated.
