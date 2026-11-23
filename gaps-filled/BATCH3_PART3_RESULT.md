# Batch 3, part 3: party fiscal classifications, shorthand aliases, legal authorities (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-24. Tested on ETIA-TEST only (release 11.13.26.10.0).
- The FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`. No FSCR file was edited.
- Plan and rules: `BATCH3_PLAN.md` (RULES 1 to 18). Reused Part 1's helpers (`template_row.py`, `build_fsm_package.py`, `compare_fsm_exports.py`, `text_png.py`) and its lessons (keep every ProcessId, template rows, no internal IDs).
- **Blocked-task check:** none of the 3 Part 3 tasks needs a tax status, tax rate, tax rule or live tax, so none was blocked and no replacement task was added to `BATCH3_PLAN.md`.
- Part 2's tasks were not touched (another chat ran it).

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 01:15 | 01:18 | 3 | Reading plan, Part 1 result, helpers |
| 01:18:37 | 01:18:40 | 0 | Sign-in on port 8765, after checking that nothing was listening there (the browser was still signed in; not counted in any task) |
| 01:18 | 01:29 | 11 | 3 read-only exports (parallel, 3.5 min), 3 packages, 3 imports (parallel, 2 min), 3 after-exports (parallel, 3 min), compares |
| 01:29 | 01:32 | 3 | 3 skills |
| 01:32 | 01:40 | 8 | 3 fresh tests in parallel; evidence 01 to 05, cards, changelogs |
| 01:40 | 01:43 | 3 | Index, this report, cleanup |

**Waiting for your approvals:** 0 minutes (the brief was the approval). No second sign-in.

## Results

| # | Task | Status | Working min (write + own live test) | Oracle waiting min | Fresh test | Fresh test min |
|---|---|---|---:|---:|---|---:|
| 8 | Manage Party Fiscal Classifications (`ZX_MANAGE_PARTY_FISCAL_CLASSIFICATIONS`) | tested | 5 | 9 | PASS, no deviation | 8 |
| 9 | Manage Shorthand Aliases (`ORA_GL_MANAGE_SHORTHAND_ALIASES`) | tested | 5 | 9 | PASS, no deviation | 3 |
| 10 | Manage Legal Authorities (`XLE_MANAGE_LEGAL_AUTHORITIES`) | tested | 7 | 9 | PASS (1 export retry, allowed by the skill) | 7 |
| | **Total** | 3 of 3 tested | **17** | **9 (shared)** | 3 of 3 | **18** |

- The 3 tasks ran their exports and imports in parallel, so the 9 minutes of Oracle waiting were shared: each card shows 9, but the wall clock only had 9 minutes in total.
- **No `retest_after_wording_fix` is pending.** No skill changed after its fresh test. The testers' notes are in each CHANGELOG and were **not** applied, so the wording on disk is the wording that was tested.
- `rebuild_index.py`: **No problems.** 32 cards applied. Common Features went from 23 to **26 tested** of 148 (17.6 %). All 19 modules: 28 tested of 935.

## Test records created (all new; none edited or deleted; may not be deletable)

| Task | Live test (ProcessId) | Fresh test (ProcessId) |
|---|---|---|
| 8 party fiscal classification types | `GAPFILL_AB_P3_PFC1` (100004741402751) | `GAPFILL_AB_P3_PFC2F` (100004742407045) |
| 9 shorthand aliases, **disabled** | `GAPFILL_AB_P3_SA1` (100004742406277) | `GAPFILL_AB_P3_SA2F` (100004741411037) |
| 10 legal authorities | `GAPFILL_AB_P3_LA1`, site `..._S1` (100004742406310) | `GAPFILL_AB_P3_LA2F`, site `..._S1` (100004741410612) |

Nothing uses them: the fiscal types have no tax regime association and no codes, the aliases cannot be picked, and no legal entity, registration or tax points to the authorities.

Evidence: `evidence/batch-03/<TASK_CODE>/01_missing` to `05_fresh_test` for all 3. They are rendered text with no tokens, server addresses or user names.

## Findings
1. **Shorthand alias code:** aliases made on the screen show `ShorthandAliasCode = <16-17 digit internal number><Name>`. The plan said to drop the task if the code needs that number. It does not: a plain `GAPFILL_...` code was accepted and stored as given (twice). The segment values are copied from an existing alias on the same chart instance, so they are known to be valid.
2. **Party fiscal classification class category:** a new type can **reuse** the TCA class category of an existing type (3 types now point to the same one). So no new class category (a different task) was needed.
3. **Legal authority party number:** Oracle kept the `PartyNumber` and `PartySiteNumber` we gave. The skill says what to do if another environment generates its own numbers: compare by name and never import twice. The template's id columns (party, location and site ids, derived address texts) are all cleared.
4. **Exports:** 12 exports in this part (6 in the main session, 6 by the testers); 1 drop in a tester's run, fixed by the allowed retry. Imports took about 2 minutes.
5. No REST resource was searched for these 3 objects; the after-export compare is the proof for all 3.

## Index and cleanup
- `python rebuild_index.py` in `gaps-filled`: 32 cards applied, **No problems**.
- The work folder `gaps-filled/_work_b3p3` (exports, payloads, import logs, fresh-test folders) is deleted after this report.
- All 3 fresh-test sub-agents have finished. The sign-in listener exited right after sign-in. No Python process or server started by this session is left, and nothing listens on port 8765.
- Nothing is committed or pushed.
