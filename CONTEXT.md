# CONTEXT: full memory of the FSCR work

Read this first in every session. Plain words. "unconfirmed" = not confirmed from files. "per Abdullah" = stated by Abdullah, not found in a file. Last full rewrite: 2026-11-23 on the PC (DESKTOP-TJ1S90V). Sections 9, 11, 12 updated 2026-11-24 on the PC.

---

## 1. Who and what

- **Abdullah Butt**: QA engineer at GoSaaS / Argano, Lahore. FSCR point person and acting PM (per Abdullah). Initials **AB**.
- The work: evaluating **Oracle's FSCR toolkit** (`https://github.com/oracle/fscr`, commit `2801695` "FSCR 26D Release") with about 16 colleagues, one tracker module each.
- **Pack** = the official FSCR repo + our kit (`fscr-main\fscr-module-test-pack\`, zip `fscr-main\fscr-module-test-pack_v3.zip`). Kit files: `module-test-kit\`, `work\`, `evidence\`, `project\`, `CHANGES.md`, `CLAUDE.md`, `SETUP.md`, `README_PACK.md`, `PACK_VERSION.txt`, `check_boss_scope.md`.
- Oracle test pod: **ETIA-TEST**.

## 2. Folder map (repo root = `E:\GoSaaS\Configuration Automation v2.1` on the PC)

| Path | What it is | In git? |
|---|---|---|
| `CONTEXT.md`, `README.md`, `SYNC_RULES.md`, `CHANGELOG.md`, `BIG_FILES.md`, `LAPTOP_SETUP.md`, `HANDOFF_RESULT.md` | memory and sync files | yes |
| `_patches\` | our one code fix to an Oracle file + `fusionEnv.properties.example` | yes |
| `fscr-access-requirements.md` | what a new person's Oracle account needs on ETIA-TEST | yes |
| `fscr-signin-values.txt` | **secret**: environment, Fusion URL, OAuth client ID, sign-in steps. Shared by Abdullah one person at a time | **no** (template `fscr-signin-values.txt.example`) |
| `gaps-filled\` | gap-fill work: `README.md`, `gap_index.csv` (935 gaps), `gap_progress.tsv`, `rebuild_index.py`, `GAPS_PLAN.md`, `PEOPLE_PROMPT.md`, `BATCH1_PART1..3_RESULT.md`, `SETUP_RESULT.md`, `batch1_export_check.csv`, one folder per module (`common-features\`, `general-ledger\`, `receivables\`) with one folder per task (`SKILL.md`, `STATUS.md`, `CHANGELOG.md`, `scripts\`), `evidence\batch-01\`, `_drive_ready\gaps-filled\` (empty folder tree, for the Drive upload) | yes |
| `_fscr_run_38_cold_test\` | Run 38 report: cold test of the module test pack (`REPORT.md`, `tracker_row.md`, `images\`) | yes |
| `Configuration Automation\` | our separate tool (Oct–Nov 2026): sets up Oracle Order Management from one Excel workbook through a local page (`start.cmd`, http://127.0.0.1:8765). `CLAUDE.md`, `ARCHITECTURE_OVERVIEW.md`, one folder per object, `common\`, `_frozen\`, `page\` | yes, except `.env`, `.session\` (secrets) and page logs/cache. Has its own `.gitignore` |
| `fscr-main\` | our FSCR work folder (not a git repo by itself) | partly |
| `fscr-main\FSCR_Full_Context.md`, `FSCR_Run_Facts.md`, `FSCR_Creation_Tokens.md`, `FSCR_Creation_Tokens_calls.csv`, `RECEIVABLES_MODULES_PLAN.md` | context notes, run facts, token counts | yes |
| `fscr-main\_fscr_run_*\` | one folder per run (section 3) | yes, except the Oracle repo copy inside |
| `fscr-main\_fscr_spec\` | specs: AutoInvoice grouping rules, receivables payment terms, transaction sources/types, dependency map, route audit | yes |
| `fscr-main\_fscr_evidence_pack\` | evidence pack: `INDEX.md`, `LIFECYCLE.md`, coverage, gap fills, procurement, purchasing, ripple test, runs, screenshots | yes |
| `fscr-main\_evidence_upload\` | upload-ready evidence: Common Features, Procurement, Sourcing and Supplier Management | yes |
| `fscr-main\_fscr_all_module_counts\` | per-module counts (`REPORT.md`, `module_totals.csv`) | yes |
| `fscr-main\_gap_fills\` | older place of the first 2 gap skills (journal categories, alternate name mapping rules) | yes |
| `fscr-main\fscr-module-test-pack\` | the pack (kit files tracked; Oracle part ignored) | kit only |
| `fscr-main\fscr-module-test-pack_v3.zip` | latest pack zip (26.7 MB) | yes |
| `fscr-main\fscr-main\` | baseline Oracle copy used by runs 1–22 (+ project `draft-impl-project-20261028`) | no (restore: clone oracle/fscr at 2801695 + `_patches\`) |
| `fscr-official-clone\` | clean git clone of oracle/fscr at 2801695 | no |
| Outside the repo: `E:\GoSaaS\FSCR_INVENTORY\` | the 2026-11-23 inventory (`INVENTORY.md`, CSVs) that the git rules came from | no |
| Outside the repo: `E:\GoSaaS\gw\r37\` | work folder of Run 37 (index scripts, times) | no |

## 3. How we work

**Sign-in (FSCR to ETIA-TEST):** ask Claude "Set up sign-in from the sign-in file…" (it reads `fscr-signin-values.txt`; values are never typed into chat). FSCR's listener waits on port **8765**. Fallback: if the browser cannot reach the listener, paste the full address `http://127.0.0.1:8765/oauth/callback?code=...` back to Claude together with your initials within **5 minutes**. Claude Desktop must be linked to the computer. On Linux, Claude Code installs with `curl -fsSL https://claude.ai/install.sh | bash`. The sign-in lasts about an hour; an expired sign-in makes REST calls hang (seen in batch 1 and runs 26b/27b). On Windows set `PYTHONUTF8=1` for FSCR scripts.

**Where runs are written:** `fscr-main\_fscr_run_<NN>_<short_name>\` (Run 1 is `_fscr_run_01`). A re-run gets a letter: `_fscr_run_11b_project_intake`, `_fscr_run_26b_skill_test`, `_fscr_run_27b_skill_test`. Demo: `_fscr_run_demo_FSCR_Demo_Sheet_1_Run_Now`. Exception: Run 38 is at the top level, `_fscr_run_38_cold_test\`.

**What a run folder holds:** a report (`RUN_REPORT.md`, `RESULT.md` or `REPORT.md`); results (`ledger.csv`, `mapping.csv`, `plan.csv`, `verify_rows.csv`, `area_counts.csv`, `tracker_row.*`, `*_ETIA-TEST.xlsx`); times (`run_times.txt` or `start_time.txt` / `finish_time.txt`); `scripts\`, `payload(s)\`, `runbook\`, `input\`; `evidence\` (REST/SOAP read-backs, screenshots, saved Oracle doc pages); raw exports (`export_before\`, `export_after\`, `import_result\`, zips); hash lists (`*.md5`). Runs 1–6, 8, 9, 11–22 and the demo also hold a full FSCR copy (`fscr-workNN\`, `fscr-main\` or `repo\`, 70.9 MB, not in git); its `project\<id>\` folder (FSCR's workspace: state, artifacts, exports) is in git.

**Missing run folders:** Run 31 has no folder or file here: **unconfirmed, ask Abdullah**. Runs 26 and 27 exist only as 26b and 27b; the STATUS cards mention "Runs 26a-c" and "27a-c": **unconfirmed where 26a/26c/27a/27c are, ask Abdullah**. Run 37 (37, 37b, 37c, 2026-11-18) has no run folder here; its work folder is `E:\GoSaaS\gw\r37` (outside the repo) and its times are in `gaps-filled\GAPS_PLAN.md`.

## 4. Tracker rules (FSCR Module Test Tracker)

- **34 rows** (modules).
- **Coverage:** a = an FSCR skill or guide exists; b = route only (CSV); c = neither.
- **Missing** = b + c, written as a plain number.
- **Guide rubric** is only defined at 1, 3 and 5.
- **Runbook** = 3 for a complete list with 0 prerequisites.
- **Execution** stays blank when blocked by access or safety (that is not an FSCR fault).
- Tasks with no CSV or API in Oracle are **not scored**, but they **are** counted in Total Tasks and Missing.

## 5. Numbers

From files (`fscr-main\_fscr_all_module_counts\REPORT.md`, `fscr-main\_fscr_run_36_scope_map\REPORT.md`, `gaps-filled\README.md`):
- Tracker rows: **1,842 tasks, 1,138 missing** (882 b, 256 c).
- Whole catalog: **2,616 tasks, 1,768 missing**; 774 tasks belong to no tracker row (630 of the missing are outside the tracker rows).
- Owned rows: **19** (11 ERP, 8 SCM), **935 missing** (749 b, 186 c). Security has no gap rows.
- Unowned: HCM (10 rows), Logistics (2), PLM (3).
- Test status (per Abdullah): **11 completed, 3 in progress** (Fixed Assets, Revenue, Order Management), **5 not started** (Payables, Cash, Expenses, PFM, Maintenance).

## 6. Owners (per Abdullah)

| Module | Owner |
|---|---|
| Common Features, Procurement, Sourcing | Abdullah Butt |
| Security | Younas Yaqub |
| General Ledger | Sufian Shafi |
| Payables | Aleeza Khan |
| Receivables | Ahmed Mujtaba |
| Cash Management | Ammar Varaich |
| Fixed Assets | Zujaja Ali |
| Expenses | Maruf Mehdi |
| Revenue Management | Ahsan Rehman |
| Project Financial Management (PFM) | Ahsan Ahmed |
| Purchasing | Muhammad Zaid |
| Inventory | Hussain Faiz |
| Order Management | Amna Kashif |
| Manufacturing | Hassan Ashfaq |
| Cost Management | Hamna Ahsan |
| Supply Planning | Imtenan Raashid |
| Maintenance | Asif Jahangir |

Open: owners for HCM, Logistics and PLM; how to split the big modules (PFM, GL, Common Features), which is Abdullah's decision; Imtenan's agreement.

## 7. Gap-filling method

1. Export the task from ETIA-TEST (read-only).
2. Write a generic `SKILL.md`.
3. Load a `GAPFILL_<INITIALS>_P<part>_` test record on ETIA-TEST (FSM CSV or REST). (Batch 1 used plain `GAPFILL_`, batch 2 `GAPFILL_AB_`; runs 24–27 used `FSCRT_`.)
4. Read it back.
5. Run a fresh sub-agent test using only the task name + `SKILL.md`.
6. Write the `STATUS.md` card.
- Skip screen-only tasks (listed in each module's `screen-only.csv`).
- Batches of 5, easy first.
- Log working minutes and waiting minutes separately (sign-in is not counted in any task).

**STATUS.md keys, in this order:** `task_code, task_name, module, status (tested|written|failed), filled_by, date, minutes_to_write, minutes_to_test, waiting_minutes, fresh_claude_pass, route, depends_on, test_records, notes`. Optional last key: `retest_after_wording_fix`.

## 8. Index rule

`gaps-filled\gap_index.csv` is **built, never hand-edited**. Run `python rebuild_index.py` in `gaps-filled\`: it reads every `STATUS.md`, updates `gap_index.csv` and writes `gap_progress.tsv` (standard library only; keeps CRLF). Expected now: **935 rows, 28 tested** (32 cards, 4 failed).

## 9. What is done

### Gaps filled (from the 32 STATUS.md cards, 2026-11-24)

**28 tested** in total: Common Features **26**, General Ledger **1**, Receivables **1**. Each passed a fresh Claude test on its final wording (no `retest_after_wording_fix` is pending). **4 failed** (tax chain, below). All filled by AB. Routes: 31 FSM CSV, 1 REST (alternate name mapping rules).

| Batch | Date | Result | Report |
|---|---|---|---|
| runs 24-27 | 2026-11-15/16 | 2 tested: Journal Categories (GL), Alternate Name Mapping Rules (Receivables) | run folders 24, 25, 26b, 27b |
| batch 1 | 2026-11-20 | 10 of 10 tested (Common Features) | `gaps-filled\BATCH1_PART1..3_RESULT.md` |
| batch 1 re-test | 2026-11-24 | all 10 re-test cards pass (8 batch 1 Common Features + the 2 older skills); journal categories and alternate name mapping skills fixed and now **portable** (no `fscr-main\_gap_fills\` paths, no ETIA-TEST names) | `gaps-filled\RETEST_BATCH1_RESULT.md` |
| batch 2 | 2026-11-23 | **9 of 10** tested; Tax Zone Types failed | `gaps-filled\BATCH2_PLAN.md`, `BATCH2_PART1..3_RESULT.md` |
| batch 3 | 2026-11-23/24 | **7 of 10** tested; Tax Statuses, Tax Rates, Tax Rules failed | `gaps-filled\BATCH3_PLAN.md`, `BATCH3_PART1..3_RESULT.md` |

| Task code | Task | Module | Status | Date | Write / test / wait min |
|---|---|---|---|---|---|
| FND_MANAGE_APPLCORE_STANDARD_LOOKUPS | Manage Applications Core Standard Lookups | Common Features | tested | 2026-11-20 | 11 / 2 / 3 |
| HZ_MANAGE_GEOGRAPHY_LOOKUPS | Manage Geography Lookups | Common Features | tested | 2026-11-20 | 1 / 2 / 1 |
| HZ_MANAGE_RESOURCE_NOTE_TYPE | Manage Resource Note Type | Common Features | tested | 2026-11-20 | 1 / 2 / 1 |
| ORA_ZX_MANAGE_TAX_LOOKUP_CODES | Manage Tax Lookup Codes | Common Features | tested | 2026-11-20 | 4 / 3 / 3 |
| XLE_MANAGE_APPLICATION_LOOKUP | Manage Legal Entity Configurator Lookups | Common Features | tested | 2026-11-20 | 2 / 3 / 2 |
| FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES | Manage Document Sequence Categories | Common Features | tested | 2026-11-20 | 4 / 3 / 1 |
| GL_MANAGE_CONVERSION_RATE_TYPES | Manage Conversion Rate Types | Common Features | tested | 2026-11-20 | 2 / 2 / 1 |
| FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_CATEGORIES | Manage Applications Core Attachment Categories | Common Features | tested | 2026-11-20 | 2 / 3 / 1.5 |
| FND_MANAGE_APPLCORE_VALUE_SETS | Manage Applications Core Value Sets | Common Features | tested | 2026-11-20 | 3 / 3 / 11 |
| GL_MANAGE_TRANSACTION_CALENDARS | Manage Transaction Calendars | Common Features | tested | 2026-11-20 | 3 / 2 / 2.5 |
| FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS | Manage Applications Core Profile Options | Common Features | tested | 2026-11-23 | 5 / 6 / 2 |
| FND_MANAGE_APPLICATIONS_CORE_ADMINISTRATOR_PROFILE_VALUES | Manage Applications Core Administrator Profile Values | Common Features | tested | 2026-11-23 | 4 / 5 / 2 |
| FND_MANAGE_APPLICATIONS_CORE_PROFILE_CATEGORIES | Manage Applications Core Profile Categories | Common Features | tested | 2026-11-23 | 4 / 6 / 1 |
| FND_MANAGE_PROFILE_CATEGORIES | Manage Profile Categories | Common Features | tested | 2026-11-23 | 2 / 6 / 2 |
| FND_MANAGE_DOCUMENT_SEQUENCES | Manage Document Sequences | Common Features | tested | 2026-11-23 | 5 / 6 / 2 |
| ORA_ZX_MANAGE_WITHHOLDING_TAX_CALENDARS | Manage Withholding Tax Calendars | Common Features | tested | 2026-11-23 | 5 / 4 / 2 |
| ZX_MANAGE_TAX_ZONE_TYPES | Manage Tax Zone Types | Common Features | **failed** | 2026-11-23 | 6 / 0 / 5 |
| ZX_MANAGE_TAX_REGIMES | Manage Tax Regimes | Common Features | tested | 2026-11-23 | 7 / 6 / 5 |
| ZX_MANAGE_TAX_REPORTING_TYPES | Manage Tax Reporting Types | Common Features | tested | 2026-11-23 | 5 / 5 / 4 |
| ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS | Manage Tax Determining Factor Sets | Common Features | tested | 2026-11-23 | 4 / 4 / 3 |
| ZX_MANAGE_TAXES | Manage Taxes | Common Features | tested | 2026-11-23 | 8 / 9 / 5 |
| ZX_MANAGE_TAX_STATUSES | Manage Tax Statuses | Common Features | **failed** | 2026-11-23 | 11 / 0 / 21 |
| ORA_ZX_MANAGE_TAX_FORMULAS | Manage Tax Formulas | Common Features | tested | 2026-11-23 | 5 / 5 / 3 |
| ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES | Manage Tax Rates and Tax Recovery Rates | Common Features | **failed** | 2026-11-24 | 4 / 0 / 2 |
| ZX_MANAGE_TAX_JURISDICTIONS | Manage Tax Jurisdictions | Common Features | tested | 2026-11-24 | 12 / 11 / 7 |
| ZX_MANAGE_TAX_CONDITION_SETS | Manage Tax Condition Sets | Common Features | tested | 2026-11-24 | 9 / 6 / 5 |
| ZX_MANAGE_TAX_RULES | Manage Tax Rules | Common Features | **failed** | 2026-11-24 | 8 / 0 / 8 |
| ZX_MANAGE_PARTY_FISCAL_CLASSIFICATIONS | Manage Party Fiscal Classifications | Common Features | tested | 2026-11-24 | 5 / 8 / 9 |
| ORA_GL_MANAGE_SHORTHAND_ALIASES | Manage Shorthand Aliases | Common Features | tested | 2026-11-24 | 5 / 3 / 9 |
| XLE_MANAGE_LEGAL_AUTHORITIES | Manage Legal Authorities | Common Features | tested | 2026-11-24 | 7 / 7 / 9 |
| GL_MANAGE_JOURNAL_CATEGORIES | Manage Journal Categories | General Ledger | tested | 2026-11-15 (re-test 2026-11-24) | unknown / 4 / unknown |
| ORA_MANAGE_ALTERNATE_NAME_MAPPING_RULES | Manage Alternate Name Mapping Rules | Receivables | tested | 2026-11-16 (re-test 2026-11-24) | unknown / 12 / unknown |

**The 4 failed or blocked (tax chain):**
- **Tax Zone Types:** the import validates, then fails at the database insert with `JBO-26041`; 3 tries; the ORA- cause is **unconfirmed** (the FSM ProcessId was not kept, so the full log cannot be opened).
- **Tax Statuses:** rejected 3 times (`ZX_INVALID_VALUE ... Tax attribute`), even with a simulation tax and a business unit subscription (test BU `ZZ_TEST_BU_1932` subscribes `GAPFILL_AB_TR1`, made with AB's approval). Likely missing piece: a subscription for the global configuration owner, which needs internal IDs.
- **Tax Rates:** blocked by Tax Statuses (a rate needs a status).
- **Tax Rules:** rejected 3 times with `ZX_RECRATE_DATE_INVALID`; likely the same root cause as statuses.
- **Plan:** park all 4 with the screen-only group and look at them once with a screen step.

### Runs (dates = file dates in each run folder)

| Run | Folder | Date | What (from its report title / verdict) |
|---|---|---|---|
| 01 | `_fscr_run_01` | 2026-11-02/03 | OM and Financials setup on ETIA-TEST: all 24 input records created and read back |
| 02 | `_fscr_run_02_understand` | 2026-11-03 | Test 4: can FSCR read and explain an existing environment |
| 03 | `_fscr_run_03_change` | 2026-11-03 | Test 4b: change existing setup: 5 of 6 changes made and verified |
| 04 | `_fscr_run_04_create16` | 2026-11-03 | Test 1: do the 16 "full create set" skills work |
| 05 | `_fscr_run_05_breadth` | 2026-11-03 | Test 2: breadth of FSCR's other skills |
| 06 | `_fscr_run_06_requirements` | 2026-11-03 | existing configuration + new requirements |
| 07 | `_fscr_run_07_inventory` | 2026-11-04 | FSCR inventory on one page (+ xlsx) |
| 08 | `_fscr_run_08_compare` | 2026-11-04 | best start vs current deployment (automated comparison) |
| 09 | `_fscr_run_09_impact` | 2026-11-04 | impact analysis of a change (read only) |
| demo | `_fscr_run_demo_FSCR_Demo_Sheet_1_Run_Now` | 2026-11-04 | create demo from `FSCR_Demo_Sheet_1_Run_Now.xlsx` |
| 10 | `_fscr_run_10_drive_reference` | 2026-11-05 | human-made reference examples for scoring |
| 11, 11b | `_fscr_run_11_project_intake`, `_fscr_run_11b_project_intake` | 2026-11-05 | project intake from the Twelve SCM SOW |
| 12 | `_fscr_run_12_project_planning` | 2026-11-05 | project planning for Twelve |
| 13 | `_fscr_run_13_twelve_manual_baseline` | 2026-11-05 | Twelve manual planning baseline |
| 14 | `_fscr_run_14_part2_intake` | 2026-11-05 | Part 2 project intake (FSCR + Claude) |
| 15 | `_fscr_run_15_part2_planning` | 2026-11-05 | Part 2 project planning (wave plan xlsx) |
| 16 | `_fscr_run_16_sow_only_wave_plan` | 2026-11-05 | SOW-only wave plan vs the team's final plan |
| 17 | `_fscr_run_17_change_impact_discovery` | 2026-11-09 | change-impact discovery (read only) |
| 18 | `_fscr_run_18_best_subject` | 2026-11-09 | best setup for a change-impact test |
| 19 | `_fscr_run_19_bu_workbook` | 2026-11-09 | business unit workbook |
| 20 | `_fscr_run_20_cross_module_subject` | 2026-11-09 | a setup whose change reaches another module |
| 21 | `_fscr_run_21_calendar_workbook` | 2026-11-09 | accounting calendar workbook |
| 22 | `_fscr_run_22_calendar_change_impact` | 2026-11-09 | calendar change-impact test |
| 23 | `_fscr_run_23_gap_pick` | 2026-11-15 | pick the gaps to fill (read only) |
| 24 | `_fscr_run_24_fill_route_only` | 2026-11-15 | fill a route-only gap (Journal Categories): FILLED |
| 25 | `_fscr_run_25_fill_no_route` | 2026-11-15 | fill a "neither" gap (Alternate Name Mapping Rules, REST): FILLED |
| 26b | `_fscr_run_26b_skill_test` | 2026-11-15 | cold test of the Journal Categories skill: passed with fixes needed |
| 27b | `_fscr_run_27b_skill_test` | 2026-11-16 | cold test of the alternate-name-mapping-rules skill: passed with fixes needed |
| 28 | `_fscr_run_28_token_estimate` | 2026-11-16 | token estimate for runs 24, 25, 26b, 27b |
| 29 | `_fscr_run_29_common_features` | 2026-11-16 | FSCR coverage of Common Features (tracker row) |
| 30 | `_fscr_run_30_common_features_test` | 2026-11-16 | Common Features test: "Mostly" (144 tasks planned, 4 of 6 test tasks created) |
| 31 | none | – | unconfirmed, ask Abdullah |
| 32 | `_fscr_run_32_procurement_coverage` | 2026-11-17 | FSCR coverage of Procurement |
| 33 | `_fscr_run_33_procurement_test` | 2026-11-17 | Procurement test: "Mostly" (60 tasks planned, 2 of 4 loadable loaded) |
| 34 | `_fscr_run_34_sourcing_supplier_test` | 2026-11-17 | Sourcing and Supplier test: "Mostly" (91 planned, 3 of 4 loaded) |
| 35 | `_fscr_run_35_purchasing_test` | 2026-11-17 | Purchasing test: "Mostly" (16 planned, 3 of 5 loaded) |
| 36 | `_fscr_run_36_scope_map` | 2026-11-17 | one FSCR scope map for the Module Test Tracker (2,616 tasks mapped) |
| 37, 37b, 37c | `E:\GoSaaS\gw\r37` (outside repo) | 2026-11-18 | gaps plan batch 1, read-only exports of the 10 batch-1 tasks (see `gaps-filled\GAPS_PLAN.md`) |
| 38 | `_fscr_run_38_cold_test` (top level) | 2026-11-17 | cold test of the module test pack: pass with fixes (27 pack problems fixed in v2) |
| batch 1 | `gaps-filled\BATCH1_PART1..3_RESULT.md` | 2026-11-20 | 10 Common Features gaps filled and fresh-tested |
| setup | `gaps-filled\SETUP_RESULT.md` | 2026-11-20 | STATUS cards, 19-module index (935 rows), `rebuild_index.py` |
| batch 2 | `gaps-filled\BATCH2_PLAN.md`, `BATCH2_PART1..3_RESULT.md` | 2026-11-23 | 10 Common Features gaps: 9 tested, Tax Zone Types failed |
| batch 3 | `gaps-filled\BATCH3_PLAN.md`, `BATCH3_PART1..3_RESULT.md` | 2026-11-23/24 | 10 Common Features gaps: 7 tested, Tax Statuses / Rates / Rules failed |
| batch 1 re-test | `gaps-filled\RETEST_BATCH1_RESULT.md` | 2026-11-24 | 10 re-test cards: 10 pass; 2 older skills made portable |

## 10. Time measured

- Easy gap: about **10 min per gap elapsed** (first of a pattern about 11, reuse 1 to 3 working minutes). Batch 1: 10 gaps in about 77 minutes wall clock; working 33 + fresh test 25 + Oracle waiting 27 minutes (`gaps-filled\GAPS_PLAN.md` section 0).
- Medium about 25 min and hard about 50 min: **guesses**, not measured.
- Estimate: about 2 to 3 weeks with active people, expecting **700 to 800 filled** (75 to 85% of 935).
- About **150 screen-only** tasks, up to 186 (all "c"): a later phase.

## 11. Rules and decisions

- Screen-only tasks are deferred.
- The Security BOSS scope (`boss_scope`, `rmc_scope`) comes from the Oracle-side sign-in app and is **unconfirmed**; the Security rerun waits for it.
- Keep answers short and in simple words.
- Oracle test record names: only `ZZ_TEST_`, `FSCRT_`, `GAPFILL_<INITIALS>_` style; never real company names.
- Secrets never go in git or chat (SYNC_RULES.md).
- **Test record names:** `GAPFILL_AB_P<part>_<name>` (for example `GAPFILL_AB_P2_RT1`), so parts running at the same time never see each other's records. Give `copy_parent_rows.py` the **parent's** own prefix (it can differ from the child's).
- **Never import twice** after a dropped connection: first check by REST or a new export whether the record exists. Re-run a failed export into a new folder, one at a time, up to 3 tries. Keep every FSM ProcessId (ESS request numbers do not open the process log). `0 rows were processed` is a failure.
- **Text minimum lengths** (for example a TEXT tax reporting type needs MinLength) and **name maximum lengths** (for example 15 characters for withholding tax calendar names): find them in the live test and give the builder `--max-len`.
- **Profile-style (hierarchical) imports need the parent row** in the file: copy it unchanged with `common-features\manage-profile-options\scripts\copy_parent_rows.py` (only your own `GAPFILL_` parents).
- **Skills must be generic:** never mention ETIA-TEST, never hard-code paths (use `FSCR`/`GAP`/`PREFIX` placeholders; the FSCR copy is the one whose `fusionEnv.properties` is filled in), never take internal IDs from an export. In Git Bash pass `E:/...`, never `$PWD` (`/e/...`).
- **Fresh tests that share an FSM package run one after the other**, not in parallel.
- **Tax chain parked:** Tax Zone Types, Statuses, Rates and Rules go with the screen-only group; one screen step later. Do not add subscriptions or make test taxes live without AB's decision.
- **Safe wording for reports:** "tested by a fresh Claude on ETIA-TEST, record created and read back".

## 12. Pending

- Drive upload of `gaps-filled\_drive_ready\gaps-filled`.
- Gap tracker sheet with an "Assigned to" column.
- Phase 2 and `PEOPLE_PROMPT.md` in the tester guide doc.
- Pilot `PEOPLE_PROMPT.md` with one person (Zaid).
- Status email to Younas bhai.
- Owners for HCM, Logistics and PLM.
- How to split the big modules (PFM, GL, Common Features).
- Imtenan (Supply Planning) agreement.
- Tax chain (Zone Types, Statuses, Rates, Rules): parked with the screen-only group; one screen step later.
- Delete the empty folder tree `E:\e\` by hand (left by a `/e/...` path slip in batch 3 part 2; it holds no files).
- **Next:** batch 4, about 10 easy Common Features gaps, avoiding the tax chain.

## 13. Session commands (Claude: follow exactly when Abdullah types these words)

### "Start session"
1. Run `git pull` in the repo root. If it fails or conflicts, stop and say exactly what failed (follow SYNC_RULES.md for STATUS.md conflicts).
2. Read `CONTEXT.md`, `CHANGELOG.md` and `BIG_FILES.md`.
3. Run `python rebuild_index.py` in `gaps-filled\` and note the counts.
4. Tell Abdullah in **5 lines**: where we are, what changed since the last session on the other machine (from `CHANGELOG.md` and `git log` since the last line from this machine), the index counts, and what is next from section 12.

### "End session"
a. Update `CONTEXT.md` sections **9** (done), **11** (rules and decisions) and **12** (pending), and add one line to `CHANGELOG.md`: date, machine name, what changed.
b. For every new or changed file that is over 50 MB, or is ignored by `.gitignore`, and is not a secret: add a line to `BIG_FILES.md` (name, path, machine, size, date, what it is, which run or task made it, how to get it back).
c. For every new run: check a short summary file exists in the run folder (`RUN_REPORT.md`, `RESULT.md` or `REPORT.md`); create one if not.
d. Run `python rebuild_index.py` in `gaps-filled\`.
e. `git add -A`, then check the staged list (`git diff --cached --name-only`): no secret files (`fscr-signin-values.txt`, `.env`, `state.json`, `fusionEnv.properties`, token or cache files) and no file over 50 MB. Fix and re-check if anything is wrong. Then `git commit -m "<clear message>"`. Do **not** push: Claude never pushes; Abdullah runs `git push` himself. Never force-push. Note: new files in `Configuration Automation\page\_work\` need `git add -f` (that project's own `.gitignore` hides `_work\`).
f. Tell Abdullah in **3 lines**: what was committed (commit, files), anything not synced (big files, secrets, failures), and remind him to run `git push`.
