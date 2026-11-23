# Gaps plan: Common Features, batch 1

GoSaaS work, not official FSCR. Paper only: no Oracle call was made in this run, and no FSCR file was changed.

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 2026-11-18 21:19 | 2026-11-18 21:26 | 7 | Run 37. Work folder `E:\GoSaaS\gw\r37` (start time + index script). |
| 2026-11-18 23:23 | 2026-11-18 23:36 | 13 | Run 37c: swap + read-only export of the 2 lookup tasks. First try timed out at sign-in (token expired after about an hour); about 10 min was lost to that and the second sign-in. |
| 2026-11-18 22:04 | 2026-11-18 22:22 | 18 | Run 37b: read-only export of the 10 batch-1 tasks (see section 3a). About 5 min of this was the sign-in wait. |

## 0. Update 2026-11-20: batch 1 done (real times)

All 10 batch-1 tasks are **tested** (live test + fresh-Claude test PASS), filled by AB with Claude on ETIA-TEST, in three parts (`BATCH1_PART1_RESULT.md`, `BATCH1_PART2_RESULT.md`, `BATCH1_PART3_RESULT.md`). **Tax Lookup Codes and LE Configurator Lookups are done** (part 2). Each finished skill now has a `STATUS.md` card; see README.

| # | Task | Plan write | Plan test | Working min (write + own live test) | Fresh test min | Oracle waiting min |
|---|---|---:|---:|---:|---:|---:|
| 4 | Standard Lookups | 20 | 15 | 11 | 2 | 3 |
| 5 | Geography Lookups | 10 | 10 | 1 | 2 | 1 |
| 8 | Resource Note Type | 30 | 20 | 1 | 2 | 1 |
| 10 | Tax Lookup Codes | 20 | 15 | 4 | 3 | 3 |
| 9 | LE Configurator Lookups | 10 | 10 | 2 | 3 | 2 |
| 3 | Document Sequence Categories | 30 | 20 | 4 | 3 | 1 |
| 1 | Conversion Rate Types | 25 | 15 | 2 | 2 | 1 |
| 7 | Attachment Categories | 20 | 15 | 2 | 3 | 1.5 |
| 6 | Value Sets | 25 | 20 | 3 | 3 | 11 |
| 2 | Transaction Calendars | 35 | 20 | 3 | 2 | 2.5 |
| | **Total** | **225** | **160** | **33** | **25** | **27** |

- Wall clock: part 1 15:45:54 to 16:10, part 2 16:13:08 to 16:31:17, part 3 16:32:17 to 17:07:37 (about 77 minutes for all 10, including reading, sign-ins, reports and cleanup). Fresh tests ran in the background while the next task was written.
- Sign-in is not counted in any task. Value Sets' waiting includes about 8.5 minutes of a REST call that hung on an expired token.
- Lesson: one full skill per FSM package (5 to 11 working minutes), then short cards (1 to 3 minutes). Oracle waiting is now as large as working time.
- Not re-tested after wording fixes: 8 batch-1 skills have `retest_after_wording_fix: pending` on their card (all except Document Sequence Categories and Attachment Categories), plus the 2 older GL/AR skills.
- **Test prefix from now on: `GAPFILL_<INITIALS>_`** (for example `GAPFILL_AB_`). Batch 1 used plain `GAPFILL_`; Runs 24 to 27 used `FSCRT_`. Section 3 below still shows the old plan (`ZZ_TEST_`) as it was written.
- Scope widened: `gap_index.csv` now has all 935 missing tasks of the 19 ERP/SCM modules (see README), not only Common Features.

## 1. Counts (authority: Run 36 scope map)

Source: `fscr-main\_fscr_run_36_scope_map\module_scope_map.csv`, row "Common Features".

| Level | Meaning | Tasks |
|---|---|---:|
| a | has an FSCR skill or guide | 79 |
| b | no skill, catalog CSV flag Y (route only) | 99 |
| c | no skill, no CSV route (neither) | 49 |
| **Missing (b + c)** | | **148 of 227** |
| Skill but no route | has a skill that names no FSM CSV or REST route (inside the 79, not missing) | 10 |

The 10 "skill but no route" tasks: Manage Configuration Set Migration Target Security Policy, Manage Help Security Groups, Manage Currencies, Manage Applications Security Preferences, Manage Users, Manage Chart of Accounts Value Set Values, Manage Account Combinations, Run User and Roles Synchronization Process, Import User Login History, Import Users and Roles into Application Security.

**Run 29 disagrees.** Run 29 had 144 tasks (65 a, 49 b, 30 c, 79 missing). The scope map moved 6 tasks out and 89 in (mostly 32 Transaction Tax tasks and generic lookups, value sets, flexfields). I used the scope map.

**The two finished gaps are not Common Features.** Journal Categories is in General Ledger and Alternate Name Mapping Rules is in Receivables (scope map). So their copies are in `general-ledger\` and `receivables\`, and they are 2 extra rows in `gap_index.csv` (148 + 2 = 150 rows). `common-features\` was empty then; since 2026-11-20 it holds the 10 batch-1 skills. (Since 2026-11-20 the index has 935 rows for 19 modules; see section 0.)

## 2. How I ranked (b tasks only)

Desk judgment from the catalog, FSCR files and earlier run evidence. **No live export was run**, so "export returns data" is confirmed only where an earlier run exported the object (Conversion Rate Types, Standard Lookups).

- **1 easy**: creates a new stand-alone record, small object, no or one prerequisite, and FSCR or an earlier run already shows the route.
- **2 medium**: new record but needs one existing object (ledger, tax, party, report), or changes a value that can be tested safely.
- **3 hard**: changes existing settings that others use (shared pod), long dependency chain, large object, country-only, or a wizard/process instead of a record.

Result for the 99 b tasks: **12 easy, 40 medium, 47 hard.** The 49 c tasks are all marked 3 and not ranked further; check each for a REST route before counting it against FSCR (Alternate Name Mapping Rules was a c task with REST).

## 3. First batch: 10 easy, independent tasks

**Status 2026-11-20: all 10 done and tested; real times in section 0.** No task in this batch needs another task in the batch. Planned test names were `ZZ_TEST_`; the batch actually used `GAPFILL_`, and from now on the prefix is `GAPFILL_<INITIALS>_`. Minutes = writing the skill, then a fresh-chat test. Estimates are based on Journal Categories (live fill 6 min, test 4 min) plus skill writing time, which was not recorded.

| # | Task (code) | Skill would contain | Likely route | Main risk | Write | Test |
|---|---|---|---|---|---:|---:|
| 1 | Manage Conversion Rate Types (`GL_MANAGE_CONVERSION_RATE_TYPES`) | export, add ZZ_TEST_ rate type rows, import, compare before/after | FSM CSV (journal-categories recipe) | rate type may not be deletable | 25 | 15 |
| 2 | Manage Transaction Calendars (`GL_MANAGE_TRANSACTION_CALENDARS`) | export, new calendar with business days, import, verify | FSM CSV | CSV may hold more than one file (header + days) | 35 | 20 |
| 3 | Manage Document Sequence Categories (`FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES`) | export, new category on a table, import, verify | FSM CSV | needs a valid application table name | 30 | 20 |
| 4 | Manage Applications Core Standard Lookups (`FND_MANAGE_APPLCORE_STANDARD_LOOKUPS`) | thin card: task values + point to FSCR `core/fusion-api/apps-common/lookups`; new ZZ_TEST_ lookup type and codes | REST (FSCR generic skill), FSM CSV backup | lookup type module/ownership rules | 20 | 15 |
| 5 | Manage Geography Lookups (`HZ_MANAGE_GEOGRAPHY_LOOKUPS`) | same card as #4, other lookup types | REST / FSM CSV | adding codes to a shared type | 10 | 10 |
| 6 | Manage Applications Core Value Sets (`FND_MANAGE_APPLCORE_VALUE_SETS`) | thin card over FSCR `value-sets`; new independent ZZ_TEST_ value set + values | REST / FSM CSV | value set create may need FSM CSV, not REST | 25 | 20 |
| 7 | Manage Applications Core Attachment Categories (`FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_CATEGORIES`) | thin card over FSCR `attachments`; new ZZ_TEST_ category | FSM CSV (named in FSCR skill) | category may need an entity to be useful | 20 | 15 |
| 8 | Manage Resource Note Type (`HZ_MANAGE_RESOURCE_NOTE_TYPE`) | export, new ZZ_TEST_ note type code, import, verify | FSM CSV | object shape unknown (may be a lookup) | 30 | 20 |
| 9 | Manage Legal Entity Configurator Lookups (`XLE_MANAGE_APPLICATION_LOOKUP`) | same lookup card as #4, LE lookup types | REST / FSM CSV | adding codes to a shared, seeded type | 10 | 10 |
| 10 | Manage Tax Lookup Codes (`ORA_ZX_MANAGE_TAX_LOOKUP_CODES`) | same lookup card as #4, tax lookup types | REST / FSM CSV | new codes may show in tax screens for all users | 10 | 10 |
| | **Total** | | | | **215** | **155** |

**Swapped on 2026-11-18 (your choice):** #9 and #10 were Tax Reporting Types and Tax Zone Types; the export showed 13 and 8 files, so they moved to the second batch. Batch 1 now has 5 lookup tasks.

**Two lookup packages, not one** (export check, 2026-11-18):
- #4, #5, #8 use the standard lookup package (`FND_APP_STANDARD_LOOKUP` + `ORA_FND_APP_STANDARD_LOOKUP_CODE`).
- #9, #10 use the Financials generic lookup package (`ORA_FINANCIALS_GENERIC_LOOKUP_TYPE`, `FUN_APP_GENERIC_LOOKUP` and their translation files, 4 CSVs). LE lookups returned 0 rows; tax lookup codes returned 23.
- So write #4 first and reuse it for #5 and #8; write #10 (it has data to copy) and reuse it for #9. Estimates for #9 and #10 raised to 20 + 15 and 10 + 10 below.

| # | Write | Test |
|---|---:|---:|
| 10 Tax Lookup Codes (first of its package): **done, tested 2026-11-20** | 20 | 15 |
| 9 LE Configurator Lookups (reuses #10): **done, tested 2026-11-20** | 10 | 10 |
| **New batch total** | **225** | **160** |

About 6.4 hours for 10 gaps (about 38 min each). Measure each one; the time per pattern is the real result.

## 3a. Export check, 2026-11-18 (read-only, ETIA-TEST)

One FSCR `export_setup_task_csv.py --data` per task. All 10 finished with exit 0 in 31 to 124 seconds, so **every export object exists** and its file and column list is known. Full list of files, columns and row counts: `batch1_export_check.csv` (column names only, no data). Exports and logs were deleted afterwards.

| # | Task | Files | Data rows | What it means |
|---|---|---:|---|---|
| 1 | Conversion Rate Types | 2 | 13 types + 10 rules | ready; same shape as Journal Categories |
| 2 | Transaction Calendars | 2 | 0 | no calendars in the pod yet; build from headers |
| 3 | Document Sequence Categories | 1 | 69 | ready; simplest package of the 10 |
| 4 | Standard Lookups | 2 | 16 types + 36 codes | ready; export is scoped, not every lookup |
| 5 | Geography Lookups | 2 | 0 | same files as #4; verify with a REST lookup read |
| 6 | Value Sets | 6 | 0 | 0 although the pod has value sets: the task export is scoped. Verify by REST. Ease raised to 2 |
| 7 | Attachment Categories | 2 | 1 | ready |
| 8 | Resource Note Type | 2 | 0 | **it is a lookup** (same files as #4), so it moves to group P1 |
| 9 | Tax Reporting Types | 13 | 3 in total | bigger package than expected. Ease raised to 2 |
| 10 | Tax Zone Types | 8 | 1 geography type | geography types + zones + ranges. Ease raised to 2 |

**Changes to the plan:**
- An empty export is not proof that nothing exists (#6). Where the export is empty, the skill must check its result with a REST read or an after-export, not only a before/after row count.
- #4, #5 and #8 share one lookup package: write #4 first, then reuse it for #5 and #8. That is a good test of recipe reuse.
- #9 and #10 (the tax tasks) are now ease 2, and on 2026-11-18 they were swapped out for Legal Entity Configurator Lookups and Tax Lookup Codes (see section 3).
- b ease after the check: **9 easy, 43 medium, 47 hard.**

## 4. Second batch candidates

| Task | Ease | Why second |
|---|---:|---|
| Manage Tax Reporting Types (`ZX_MANAGE_TAX_REPORTING_TYPES`) | 2 | moved from batch 1; 13-file package (export checked) |
| Manage Tax Zone Types (`ZX_MANAGE_TAX_ZONE_TYPES`) | 2 | moved from batch 1; 8-file package (export checked) |
| Manage Daily Rates (`GL_MANAGE_DAILY_RATES`) | 2 | needs #1 |
| Manage Document Sequences (`FND_MANAGE_DOCUMENT_SEQUENCES`) | 2 | needs #3 |
| Manage Resource Note Type Mapping (`HZ_MANAGE_RESOURCE_NOTE_TYPE_MAPPING`) | 2 | needs #8 |
| Manage Tax Determining Factor Sets (`ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS`) | 2 | stand-alone, opens condition sets |
| Manage Tax Regimes (`ZX_MANAGE_TAX_REGIMES`) | 2 | root of the tax chain |
| Manage Withholding Tax Calendars (`ORA_ZX_MANAGE_WITHHOLDING_TAX_CALENDARS`) | 2 | new record, object not confirmed |
| Manage Data Access Sets (`GL_MANAGE_DATA_ACCESS_SETS`) | 2 | new record on existing ledger |
| Manage Intercompany Exceptions (`XLE_MANAGE_INTERCOMPANY_EXCEPTIONS`) | 2 | new row between two existing LEs |

## 5. Pattern groups (one recipe per group)

| Group | b tasks | Recipe |
|---|---:|---|
| P1 lookups (**done 2026-11-20, 5 of 5 tested**) | 5 | thin card over FSCR generic lookups skill (Resource Note Type joined after the export check). Two FSM packages: standard lookups (3 tasks) and Financials generic lookups (LE and tax lookups) |
| P2 value sets | 1 | thin card over FSCR value-sets skill |
| P3 profile option values | 9 | change a value at user/site level, read back, set it back |
| P4 attachments | 2 | thin card over FSCR attachments skill |
| P5 trees and labels | 4 | thin card over FSCR trees skill |
| P6 descriptive flexfields | 3 | edit + deploy; FSCR DFF skill |
| P7 simple new record (FSM CSV) | 7 | journal-categories recipe: export, add rows, import, compare |
| P8 document sequences | 5 | P7 recipe, in chain order |
| P9 transaction tax (ZX) | 22 | P7 recipe, in chain order; one shared ZZ_TEST_ regime |
| P10 legal entity sub-settings | 8 | needs a ZZ_TEST_ legal entity first |
| P11 chart of accounts add-ons | 8 | P7 recipe, records created disabled |
| P12 resource notes | 1 | P7 recipe (mapping only; note type is now P1) |
| P13 data access and security | 3 | needs a test user |
| P14 view / search only | 5 | read-only guide (export + read) |
| P15 project billing | 5 | needs PL/SQL extension names |
| P16 admin / help / ESS | 7 | mostly manual; low value |
| P17 country only | 4 | leave for last |

P1, P2, P4, P5 are the cheapest: FSCR already has generic skills for lookups, value sets, attachments and trees; they just name no task code. A short card that maps the task to the generic skill may be enough.

## 6. Dependencies (must exist first)

- Conversion Rate Types → Daily Rates
- Document Sequence Categories → Document Sequences → BU / Ledger / Legal Document Sequences
- Tax Regimes → Taxes → Tax Statuses, Tax Jurisdictions, Tax Formulas → Tax Rates → Tax Exceptions
- Tax Determining Factor Sets → Tax Condition Sets → Tax Rules (also needs Taxes)
- Party Tax Profiles → Tax Registrations (also needs Regimes), Tax Exemptions (also needs Rates)
- Tax Regimes → Configuration Owner Tax Options
- Tree Structures → Tree Labels, Trees and Tree Versions
- Account Hierarchy Labels → Account Hierarchies → Publish Account Hierarchies
- Resource Note Type → Resource Note Type Mapping
- Billing Extensions → Invoice / Revenue Method Extension Assignments
- Data Access Sets → Data Access for Users
- Value Sets → the 3 descriptive flexfield tasks (usually)
- c tasks: Implementation Users → Data Role → Revoke Data Role; Load Geography Interface Data → Run Geography Loader; Resource Organizations → Members, Hierarchies, Teams; Deploy WebLogic Communication Services → Telephony tasks

All dependencies are in `gap_index.csv`, column `depends_on`.

## 7. Risks

- **Export not confirmed** for 8 of the 10 batch-1 tasks. The first step of each fill is a read-only export; if it returns no object or no rows, swap in a batch-2 task.
- **Records may not be deletable** (journal categories were not). Every test leaves ZZ_TEST_ rows on the shared pod.
- **Shared pod.** Profile values, tax options, set assignments and security changes affect other users. Those are all ease 3 or tested only at user level.
- **Sign-in time.** Run 27b lost 8 of 12 minutes to sign-in timeouts. Time sign-in separately so it does not distort minutes per gap.
- **Ease is a desk guess.** Shape of the CSV package and REST support were not checked live.

## 8. Questions for you

1. The two finished gaps are General Ledger and Receivables, not Common Features. OK to keep them in those module folders (as done), or do you want them under `common-features\`?
2. ~~May the next run do read-only exports for batch 1?~~ Done 2026-11-18 (section 3a). Swapped the two tax tasks for two lookup tasks (your answer, 2026-11-18).
3. ~~Test names: `ZZ_TEST_` (your rule) or `FSCRT_` (used in Runs 24–27)?~~ Answered 2026-11-20: `GAPFILL_<INITIALS>_` from now on (batch 1 used plain `GAPFILL_`).
4. For P1/P2/P4/P5, is a short "task card" that points to FSCR's generic skill enough to count as filled, or do you want a full step-by-step skill each time?
5. Should c tasks with a manual FSCR card only (10 tasks, e.g. Manage Time Zones) be counted as "no CSV or API in Oracle" and dropped from the gap count?
