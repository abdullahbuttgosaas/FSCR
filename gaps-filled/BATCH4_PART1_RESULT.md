# Batch 4, part 1: XLE and ZX profile options, ATK admin profile values, attachment entities (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-24. Tested on ETIA-TEST only (release 11.13.26.10.0).
- The FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`. No FSCR file was edited.
- Plan and rules: `BATCH4_PLAN.md` (RULES 1 to 26). Reused batch 2's `manage-profile-options` and `manage-admin-profile-values` skills and the batch 1 to 3 helpers.
- Work folder `E:\GoSaaS\gw\b4p1` (outside the repo; exports there hold user names).

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 17:04 | 17:12 | 8 | Start session, reading (plan time, not in any task) |
| 17:11:50 | 17:11:59 | 0 | Sign-in on port 8765 (browser was still signed in; not counted in any task) |
| 17:12 | 17:21 | 9 | 16 planning exports (read-only), REST id look-ups, choosing (plan time) |
| 17:18 | 17:29 | 11 | 4 live tests: exports, builds, 5 imports (1 refused), REST read-backs, 4 compares |
| 17:29 | 17:32 | 3 | `BATCH4_PLAN.md`, 4 skills |
| 17:32 | 17:36 | 4 | 4 fresh tests in parallel (disjoint export scopes, rule 26); my REST re-check of their records |
| 17:36 | 17:42 | 6 | Cards, changelogs, evidence, this report, index, cleanup |

**Waiting for your approvals:** 0 minutes (the brief was the approval). No second sign-in.

## Results

| # | Task | Status | Working min (write + own live test) | Oracle waiting min | Fresh test | Fresh test min |
|---|---|---|---:|---:|---|---:|
| 1 | Manage Legal Entity Configurator Profile Options (`XLE_MANAGE_LEGAL_ENITTY_PROFILE_OPTIONS`) | tested | 4 | 3 | PASS | 4 |
| 2 | Manage Tax Profile Options (`ORA_ZX_MANAGE_TAX_PROFILE_OPTIONS`) | tested | 3 | 3 | PASS | 3 |
| 3 | Manage Application Toolkit Administrator Profile Values (`ORA_ATK_ADMIN_PROFILE_OPTION_VALUES`) | tested | 4 | 3 | PASS | 3 |
| 4 | Manage Applications Core Attachment Entities (`FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_ENTITIES`) | tested (try 2) | 6 | 5 | PASS | 3 |
| | **Total** | **4 of 4 tested** | **17** | **14** | 4 of 4 | **13** |

- The 4 fresh tests ran in parallel, so their 3 to 4 minutes each were about 4 minutes of wall clock in total.
- **No `retest_after_wording_fix` is pending.** No SKILL.md changed after its fresh test. The testers' notes are in each CHANGELOG and were **not** applied, so the wording on disk is the wording that was tested.
- `rebuild_index.py`: see the end of this report.

## Test records created (all new; none edited or deleted; may not be deletable)

| Task | Live test (ProcessId) | Fresh test (ProcessId) |
|---|---|---|
| 1 XLE profile option | `GAPFILL_AB_P1_XPO1` (100004741415488) | `GAPFILL_AB_P1_XPO2F` (100004741418512) |
| 2 ZX profile option | `GAPFILL_AB_P1_ZPO1` (100004741416712) | `GAPFILL_AB_P1_ZPO2F` (100004741415633) |
| 3 ATK option + SITE value | `GAPFILL_AB_P1_APO1` + `GAPFILL_AB_P1_AV1` (100004741419235) | `GAPFILL_AB_P1_APO2F` + `GAPFILL_AB_P1_AV2F` (100004741415574) |
| 4 attachment entity | `GAPFILL_AB_P1_AE2` (100004741416829); `GAPFILL_AB_P1_AE1` refused, not created (100004741418453) | `GAPFILL_AB_P1_AE3F` (100004741416861) |

Nothing uses them: no code reads the new options; the ATK values sit only on our own options (seeded ATK values untouched); the entities have no category link, so no screen shows them.

Evidence: `evidence/batch-04/<TASK_CODE>/01_missing` to `05_fresh_test` (.png) for all 4. Rendered text, checked: no tokens, server addresses, environment names or user names.

## Problems and findings
1. **Attachment entities, try 1 refused:** `JBO-27014: Attribute DataObjectCode in FndDocumentEntitiesEO is required` (0 rows processed, nothing created). Cause proved by comparing with working records: a read-only export of the all-modules task `FND_MANAGE_ATTACHMENT_ENTITIES` had 22 entities, each with `DataObjectCode` = upper-case entity name. Try 2 with that value: created, compare PASS. Fresh test passed first time. The round trip (rule 20) was not needed: the error named the column.
2. **Ids live by REST, not from exports:** `profileOptions` filtered by `ApplicationShortName` gives exactly one (ApplicationId, ModuleId) pair for XLE, ZX and ATK (FND has several modules, so FND uses the `YES_NO` lookup as in batch 2). This keeps rule 16.
3. **ZX export leaves seeded options out:** REST shows 9 seeded ZX options, the export showed 0. A new option with the ZX module id **does** appear in the export, so the compare works.
4. **Prerequisite inside the package (ATK, rule 21):** the value task needs an option; our own option, its 3 levels and its SITE value went in **one** import (5 rows). No separate task or screen step.
5. **Out after the planning exports:** Search Profile Options and Common CRM BU Profile Options (their scope is named seeded options in `edit` mode, so the only use is changing shared settings), Tax Registrations (legal reporting unit only), Map Reports to Work Areas (shows reports to all users). Details in `BATCH4_PLAN.md` section 1.
6. **Follow-up found by a tester (not fixed, needs a re-test):** the full skill `manage-profile-options` Step 5 log one-liner prints the whole process log, which holds a `Submitted By` user name. Cards 1 to 3 point to it. Fix: filter the log as the attachment entities skill does, then re-test the full skill and the 3 cards (and batch 2's admin values / categories cards). Testers also noted: FSCR puts the environment name in its output file names (harmless in a private run folder; never copy them into evidence).
7. **Fresh-test numbering:** testers did not need help; all 4 used the saved sign-in (no second sign-in).

## What Parts 2 and 3 can reuse
- **Driver pattern:** export, inspect, build with `build_fsm_package.py`, import, log summary, after-export, `compare_fsm_exports.py`. The log summary one-liner in `manage-attachment-entities` Step 5 prints only row counts, totals and `JBO-` messages (no user names). Use it.
- **Ids by REST at run time** (finding 2) when an export has no row to copy and a row needs a module id.
- **Diagnosis order that worked:** read the `JBO-` message first; if it names a column, look at working records of the same object (a wider read-only export) column by column. Keep rule 20 (who columns, round trip) for generic errors.
- **Parallel fresh tests are fine when export scopes differ;** keep tasks 5 to 7 (one fiscal classification package and scope) one after the other.
- **Planning exports already checked** (read-only, all worked first try): transaction, transaction-based and product-based fiscal classifications (same 73-file package), note type mapping, party tax profiles (87 files; `ZX_TAX_AUTHORITY_PROFILE` 3 rows), tax exceptions, location of final discharge, tax exemptions. Export again in the part itself (the planning copies are in `E:\GoSaaS\gw\b4p1\plan`, outside the repo).
- **Timing:** XLE/ZX/ATK exports 25 to 45 s, imports 40 to 80 s; fiscal classification exports 120 to 150 s.

## Index and cleanup
- `python rebuild_index.py` in `gaps-filled`: 36 cards applied, **No problems**. Common Features: 34 tested of 148. All 19 modules: 36 tested of 935, 0 failed.
- All 4 fresh-test sub-agents have finished. The sign-in listener exited right after sign-in (17:11:59). No Python process or server started by this session is left, and nothing listens on port 8765.
- The work folder `E:\GoSaaS\gw\b4p1` stays outside the repo (exports, payloads, logs, fresh-test folders) for Parts 2 and 3 to look at; it is not in git.
- Nothing is committed or pushed.
