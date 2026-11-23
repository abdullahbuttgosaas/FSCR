# Batch 1, part 1: standard lookups (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-20. Tested on ETIA-TEST only (release 11.13.26.10.0). No FSCR file was changed (checked: no new file in the FSCR tree after the run).

| Start | Finish | Note |
|---|---|---|
| 15:45:54 | 16:10 | Reading docs, sign-in, 3 tasks, 3 fresh tests, index and report. Work folder (exports, logs, read-back JSON) deleted at the end; no process left running (no listener on the sign-in port, no Python process). Skills checked: no environment name, server address, user name or ModuleId in them. Sign-in 15:46:33 to 15:47:38 (about 1 min, not counted in any task). |

## Results

| # | Task | Status | Working min (write + own live test) | Waiting min (Oracle) | Fresh test | Fresh test min |
|---|---|---|---:|---:|---|---:|
| 1 | Manage Applications Core Standard Lookups (`FND_MANAGE_APPLCORE_STANDARD_LOOKUPS`) | tested | 11 | 3 | PASS (yes) | 2 |
| 2 | Manage Geography Lookups (`HZ_MANAGE_GEOGRAPHY_LOOKUPS`) | tested | 1 | 1 | PASS (yes) | 2 |
| 3 | Manage Resource Note Type (`HZ_MANAGE_RESOURCE_NOTE_TYPE`) | tested | 1 | 1 | PASS (yes) | 2 |
| | **Total** | 3 of 3 tested | **13** | **5** | 3 of 3 | **6** |

Minutes are rounded from the run time log. Task 1 working minutes include about 1 minute waiting for your answer on how to test task 3 (not measured separately). The fresh tests ran in the background in parallel with the next task, so wall-clock time for all three tasks plus their tests was about 21 minutes (15:47:50 to 16:08:16).

Plan estimate (GAPS_PLAN.md section 3): write 20 + 10 + 30 = 60, test 15 + 10 + 20 = 45. Actual: 13 working + 6 testing.

## What reuse saved
- Task 1 (first of the pattern) took 11 working minutes: reading FSCR's lookups skill, reading the export, writing 4 helper scripts and the full SKILL.md.
- Tasks 2 and 3 took about 1 working minute each: same scripts and package; the card only names the task code, how to get the ModuleId when the export is empty, and that the export compare is skipped. **Reuse cut writing time by about 90%** (11 to 1).
- Fresh tests took 1.5 to 2.3 minutes for all three: the short cards worked as well as the full skill.
- Oracle wait was the same for each (export about 25 to 80 s, import about 22 to 38 s). For cards, waiting is now as large as working time.

## What was reused
- FSCR in place: export and import scripts (`shared/setup-export`, `shared/setup-import`), REST client and the generic lookups skill (`core/fusion-api/apps-common/lookups`, standard lookups reference) for every read-back.
- The journal-categories structure and rules (export, new rows only, quoted CSV, keep metadata XML, process log is the real result, compare exports).
- Task 1's 4 scripts in `common-features/manage-standard-lookups/scripts/` are used unchanged by tasks 2 and 3.

## Test records created (all new; none edited or deleted; may not be deletable)
| Task | Live test (main session) | Fresh test (sub-agent) |
|---|---|---|
| 1 | `GAPFILL_SL_T1` + `GAPFILL_A`, `GAPFILL_B` | `GAPFILL_SLF1_TYPE` + `GAPFILL_F1_ONE`, `GAPFILL_F1_TWO` |
| 2 | `GAPFILL_GEO_T2` + `GAPFILL_GEO_A` | `GAPFILL_GEOF2_TYP` + `GAPFILL_GEOF2_K1`, `GAPFILL_GEOF2_K2` |
| 3 | `GAPFILL_NOTE_T3` + `GAPFILL_NOTE_A` | `GAPFILL_NTR_F3` + `GAPFILL_NTR_F3A` |

All 6 types were read back from Oracle by the main session at the end: READBACK PASS for each. Each task's CHANGELOG.md lists its records.

Evidence: `evidence/batch-01/<task-folder>/01_before_readback.png`, `02_after_readback.png`, `03_fresh_test_readback.png` (rendered REST read-backs, no secrets).

## Problems and findings
1. **Tasks 2 and 3 are scoped to seeded lookup types.** The geography export's scope is 7 seeded `HZ_GEO...` types, and the note type export's scope is only `ZMM_NOTE_TYPE` (mode `edit`). Their real use is adding codes to those seeded types. You chose to test with a new GAPFILL_ type in the same module instead, so that the shared seeded types were not touched. **So for tasks 2 and 3, "tested" proves the package, the module and the import route, not adding a code to a seeded type.** The cards say this, and say that the real use is untested.
2. **Empty export gives no ModuleId.** Solved generically: read the ModuleId by REST from a seeded type named in the export's scope (`read_lookup.py --module-of`).
3. **Git Bash path trap.** `/e/...` passed to Windows Python became `E:\e\...`: one export landed in a stray folder `E:\e\...` outside gaps-filled. Its ZIP was moved into the work folder and the empty folders were removed. The skill now says to use `E:/...`.
4. **The token had expired** (last sign-in the day before); one browser sign-in, about 1 minute; no paste needed.
5. **Fresh testers' notes** (FSCR root not obvious, ZIP name, how to read the one-line process log, step order, what `<STD>` means) were applied as wording after the tests. These wording changes were **not re-tested**.
6. Pillow and `pywin32` live in the user site-packages, so `read_lookup.py` and `render_readback.py` must run without `python -I`.

## What should change in GAPS_PLAN.md
1. **Lower P1 estimates:** first skill of a package about 15 min (write + live), each reuse card about 2 to 3 min, fresh test about 2 min. Use the same split for P2, P4 and P5 thin cards.
2. **Write #10 Tax Lookup Codes next, then #9 as a card**, the same way (one full skill, scripts, then cards). Expect the same scoped-to-seeded-type pattern and decide up front whether a new test type or a code in a seeded type is the test.
3. **Add a rule:** for tasks whose export scope names seeded types (mode `edit`), the test proves the route only; adding codes to seeded types needs a separate decision and stays "untested" until then.
4. **Test names:** the plan and README say `ZZ_TEST_` or `FSCRT_`; this batch used `GAPFILL_` (your brief). Pick one and update README rule 5 and GAPS_PLAN section 3.
5. **Answer to question 4:** a short card that points to a full first skill of the same package was enough. Fresh agents passed with the card alone.
6. **Run fresh tests in the background** while writing the next card: it saved most of the test wall-clock time.
7. Counts: group P1 had 5 tasks; 3 are now tested and 2 are left (#9 and #10). Update section 1 or add a "done" column when the next batch starts.
