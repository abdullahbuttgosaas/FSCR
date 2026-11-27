# CONTEXT: full memory of the FSCR work

Read this first in every session. Plain words. "unconfirmed" = not confirmed from files. "per Abdullah" = stated by Abdullah, not found in a file. Last full rewrite: 2026-11-23 on the PC (DESKTOP-TJ1S90V). Sections 9, 11, 12 updated 2026-11-27 (after Procurement sitting 4, module finished except the demo reserve) on the PC.

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

`gaps-filled\gap_index.csv` is **built, never hand-edited**. Run `python rebuild_index.py` in `gaps-filled\`: it reads every `STATUS.md`, updates `gap_index.csv` and writes `gap_progress.tsv` (standard library only; keeps CRLF). Expected now (2026-11-27): **935 rows, 156 tested, 19 written, 55 screen-only** (failed cards count as open in the index; Procurement 19 / 3 / 3, 1 open). Screen-only tasks are listed in each module's `screen-only.csv` and on their own cards.

## 9. What is done

### Gaps filled (from the 44 STATUS.md cards, 2026-11-24)

**44 tested** in total: Common Features **42**, General Ledger **1**, Receivables **1**. Each passed a fresh Claude test on its final wording (no `retest_after_wording_fix` is pending). **0 failed**: the 4 tax chain gaps were fixed on 2026-11-24 (below). All filled by AB. Routes: FSM CSV for all but alternate name mapping rules (REST); Tax Exemptions uses CRM REST for its prerequisite customer + tax profile, then FSM CSV. Per-module open gaps and hour estimates: `gaps-filled\MODULE_ESTIMATES.tsv` (891 open, 185 likely screen-only, 706 CSV/API, about 118 to 294 hours).

| Batch | Date | Result | Report |
|---|---|---|---|
| runs 24-27 | 2026-11-15/16 | 2 tested: Journal Categories (GL), Alternate Name Mapping Rules (Receivables) | run folders 24, 25, 26b, 27b |
| batch 1 | 2026-11-20 | 10 of 10 tested (Common Features) | `gaps-filled\BATCH1_PART1..3_RESULT.md` |
| batch 1 re-test | 2026-11-24 | all 10 re-test cards pass (8 batch 1 Common Features + the 2 older skills); journal categories and alternate name mapping skills fixed and now **portable** (no `fscr-main\_gap_fills\` paths, no ETIA-TEST names) | `gaps-filled\RETEST_BATCH1_RESULT.md` |
| batch 2 | 2026-11-23 | **9 of 10** tested; Tax Zone Types failed | `gaps-filled\BATCH2_PLAN.md`, `BATCH2_PART1..3_RESULT.md` |
| batch 3 | 2026-11-23/24 | **7 of 10** tested; Tax Statuses, Tax Rates, Tax Rules failed | `gaps-filled\BATCH3_PLAN.md`, `BATCH3_PART1..3_RESULT.md` |
| batch taxfix | 2026-11-24 | Tax Statuses, Rates, Rules now **tested**; new Step 7 in Manage Tax Regimes (GCO option row) tested; Zone Types still failed | `gaps-filled\BATCH_TAXFIX_RESULT.md` |
| batch taxfix2 | 2026-11-24 | Tax Zone Types now **tested** (who columns fix); new helper `zone_type_rows.py` | `gaps-filled\BATCH_TAXFIX2_RESULT.md` |
| batch 4 | 2026-11-24 | **11 of 12** tested (profile options, ATK values, attachment entities, 3 fiscal classifications, note type mapping, party tax profiles, tax exceptions, location of final discharge); Tax Exemptions failed | `gaps-filled\BATCH4_PLAN.md`, `BATCH4_PART1..3_RESULT.md` |
| batch 4 fix | 2026-11-24 | Tax Exemptions now **tested** (test customer + THIRD_PARTY tax profile by CRM REST); Party Tax Profiles Step 3 wording fixed and re-tested | `gaps-filled\BATCH4_FIX_RESULT.md` |
| batches 05+06 | 2026-11-25 | **6 tested** (Search Legal Entities, Search Legal Reporting Units, View Accounting Configuration Summary, View Service Clients, Manage Data Access Sets, Manage Daily Rates), **4 written** (unsafe: Search / CRM BU profile options, Map Reports to Work Areas, Country Default Controls) | `gaps-filled\common-features\BATCH_05_RESULT.md`, `BATCH_06_RESULT.md` |
| batches 07+08 | 2026-11-25 | **6 tested** (Account Hierarchy Labels, Tree Labels, Trees and Tree Versions, Account Hierarchies, Tree Structures, Ledger Document Sequences), **4 written** (unsafe: Legal Entity Tax Profiles, Configuration Owner Tax Options, Intercompany Exceptions, LRU Tax Profiles); all 49 "neither" tasks checked: none has an FSM CSV | `gaps-filled\common-features\BATCH_07_RESULT.md`, `BATCH_08_RESULT.md` |
| Procurement sitting 1 + continuation | 2026-11-25 | **9 tested** (Special Handling Types, Contract Line Types, Contract Clause Types, Contract Terms Value Sets, Contract and Procurement System Integrations, Purchasing Profile Options, Clause Import XML File Location, Collaboration Messaging Configuration, Channel Settings; last 3 as test-and-restore), **1 written** (unsafe: Electronic Signature) | `gaps-filled\procurement\BATCH_01_RESULT.md`, `BATCH_02_RESULT.md`, `MODULE_RESULT.md` |
| Procurement sitting 2 | 2026-11-25 | **4 tested** (Compliance Checklist Sections, Questions, Templates; B2B Configuration by REST), **3 written** (unsafe: Configure Procurement Business Function, Supplier Contract Management BF Properties, Contract Terms DFF), **2 screen-only** (Collaboration Messaging DVM, SSP Messages) | `gaps-filled\procurement\BATCH_03_RESULT.md`, `BATCH_04_RESULT.md` |
| batches 09+10 | 2026-11-25 | **4 tested** (Tax Registrations by REST, Legal Document Sequences, BU Document Sequences, Billing Extensions), **6 written** (unsafe: Partner Organizations, Create Implementation Users, Import Worker Users, Data Access for Users, BU and Reference Data Set Data Access for Users), **4 screen-only** (3 message tasks, Cross-Validation Rules) | `gaps-filled\common-features\BATCH_09_RESULT.md`, `BATCH_10_RESULT.md` |
| batches 11+12 | 2026-11-25 | **10 tested** under the new rule "a new prefix record nobody uses is not unsafe": re-opened from written Create Implementation Users (FSCR SCIM scripts), Data Access, BU Data Access and Reference Data Set Data Access for Users (REST `dataSecurities` on our own test user), Search Profile Options (USER level); new: Invoice and Revenue Method Billing Extension Assignments, custom ESS job LOV sources (FSCM, CRM, HCM); **3 screen-only** (Languages, Territories, Time Zones) | `gaps-filled\common-features\BATCH_11_RESULT.md`, `BATCH_12_RESULT.md` |
| batch 13 | 2026-11-25/26 | **4 tested** (Country Default Controls re-opened: rows for unused countries AQ/BV/HM, every default N; Set Help Options and Enable Click to Dial / Configure Guided Learning by test-and-restore), **1 screen-only** (Manage Help Content: CSV cannot create a new topic, retried with a round trip and 3 more tries; failed until 2026-11-26) | `gaps-filled\common-features\BATCH_13_RESULT.md` |
| batches 14+15 | 2026-11-26 | **9 tested, 1 failed** (sitting 6). Batch 14, test legal entity chain (`GAPFILL_AB_B14_LE1/LE2F/LE3R`, new prerequisite skill `test-legal-entity`): Legal Entity Tax Profiles, LRU Tax Profiles, Configuration Owner Tax Options (re-opened from written-unsafe), LE and LRU Financial Information. Batch 15 (new prerequisite skill `test-business-unit`): Associated Business Entities, Set Assignments for Set Determinant Type, Segment Value Security Rules, Chart of Accounts Configurations; **Application Tax Options failed** (row not tied to the named business unit) | `gaps-filled\common-features\BATCH_14_RESULT.md`, `BATCH_15_RESULT.md` |
| batches 16+17 | 2026-11-26 | **7 tested** (Project Process Configurator, Applications Core DFFs, Tax Authority Profiles Brazil, Data Roles, LE Configurator DFF, Resource Note DFFs, CoA Sync with DRM), 1 written unsafe (Archive and Purge), **2 failed** (Italy, China: export access denied) | `BATCH_16_RESULT.md`, `BATCH_17_RESULT.md` |
| screen-only audit + verification | 2026-11-26 | read only: of 40 screen-only from sitting 7, 29 confirmed with proof on own cards, rest set back to open; Application Tax Options failed | `common-features\SCREEN_ONLY_AUDIT.md` |
| batches 18+19 | 2026-11-26 | read only: 9 proven screen-only, 1 written unsafe (Avalara indirect tax), Import Worker Users and Partner Organizations re-judged (safe way) | `BATCH_18_RESULT.md`, `BATCH_19_RESULT.md` |
| batches 20+21 | 2026-11-26 | **3 tested** (Resource Org Members and Hierarchies, Import Worker Users), 4 written unsafe (Revoke Data Role, Jurisdiction Rates Upload, Geography Loader, Project User-Defined Rules), 1 failed (Partner Organizations), 1 screen-only (Help Text Admin Duty) | `BATCH_20_RESULT.md`, `BATCH_21_RESULT.md` |
| batches 22+23 | 2026-11-26 | **3 tested** (Internal Resource Orgs, Data Role for Implementation Users, Tax Box Allocation Rules), 3 written unsafe (2 Thomson Reuters, Publish Account Hierarchies), 2 screen-only (Guided Journeys, Resource Teams), **2 failed** (Manage Messages, Applications Core Messages: job name not published) | `BATCH_22_RESULT.md`, `BATCH_23_RESULT.md` |
| batches 24+25 | 2026-11-27 | **1 tested** (Establish Enterprise Structures: draft only, never loaded), 4 written unsafe (Geography Interface Data, Tax Geographies, Cross-Validation Rules, Associated Balancing Segments), 1 failed (Messages for GL). **Common Features: 0 open** | `BATCH_24_RESULT.md`, `BATCH_25_RESULT.md` |
| Procurement sitting 4 (batches 06+07) | 2026-11-27 | **5 tested** (Requisition + Purchasing Document Approvals by REST, disabled pending rules; re-opened from written: Contract Terms DFF, Configure Procurement BF, Supplier Contract BF Properties on own test units), 3 written unsafe (Work Confirmation + Intake Request Approvals: POR-2011627; Electronic Signature), 1 screen-only (Task Configurations). **Procurement: only the demo reserve open** | `procurement\BATCH_06_RESULT.md`, `BATCH_07_RESULT.md` |

**Since Procurement sitting 4 (batches 06 and 07, 2026-11-27):** Procurement is **finished except the demo reserve**: of 26, **19 tested, 3 written (unsafe), 3 screen-only, 0 failed, 1 open** (Manage Freight Terms Lookup, reserved, untouched). All 19 modules: **156 tested, 19 written, 55 screen-only** of 935. New helper `procurement\scriptspproval_rule.py` (one disabled approval rule by REST, ids read live, before/after compare). `procurement\scriptsuild_module_tracker.py` now reads `screen-only` cards and sets skill_written from a real `SKILL.md`. Records: disabled pending approval rules `GAPFILL_AB_B6_RQ1/RQ2F/RQ3R`, `PO1/PO2F/PO3R`; disabled OKC Clause contexts `GAPFILL_AB_B7_CCX1/CCX2F` (segments `CSG1/CSG2F`); Procurement function 110 + procurement configuration on own units `GAPFILL_AB_B15_BU1/BU2F/BU5R`; contract properties on `BU1/BU2F`. Work folder `E:\GoSaaS\gw\proc\s4` (outside repo).

**Since Common Features sittings 7 to 11 (batches 16 to 25, 2026-11-26/27):** Common Features is **finished**: of 148, **95 tested, 15 written, 7 failed, 31 screen-only, 0 open** (`common-features\MODULE_RESULT.md`). All 19 modules: **131 tested, 20 written, 45 screen-only** of 935 (index shows failed as open). The 7 failed: Application Tax Options, Italy and China options (localization privilege), Partner Organizations (owner resource), 3 message tasks (scheduled process job name). Colleague folders Payables, Purchasing and Supply Planning were copied in from the shared Drive (no secrets found); `rebuild_index.py` reads dd/mm/yyyy dates and open cards; `build_module_tracker.py` knows `written-untested` and reads the skill column from real `SKILL.md`. New helpers in `common-features\scripts\`: `dff_context_package.py`, `check_dff_rows.py`, `copy_data_role.py`, `impl_data_role.py`. Dashboard redeployed 2026-11-26. Evidence `common-features\evidence\batch-16..25`.

**Since Common Features sitting 6 (batches 14 and 15, 2026-11-26):** totals now **97 tested, 9 written, 1 failed, 10 screen-only** of 935. Common Features: **81 tested, 5 written, 1 failed, 8 screen-only, 53 open** of 148. New test records: legal entities `GAPFILL_AB_B14_LE1`, `LE2F`, `LE3R` (each with its own main reporting unit and tax profiles), business units `GAPFILL_AB_B15_BU1`, `BU2F`, `BU3`, `BU4F`, `BU5R` (BU3/BU4F/BU5R with location `GoSaaS Location`), associations LE1→BU3, LE2F→BU4F, LE3R→BU5R, reference data sets `GAPFILL_AB_B15_SET1/SET2F/SET3R` (SET assignments `PJF_RATES`→`COMMON`), secured value sets `GAPFILL_AB_B15_SVS1/SVS2F/SVS3R` (value `T1`), policies `GAPFILL_AB_B15_SVP1/SVP2F/SVP3R`. New helpers `common-features\scripts\own_row_package.py` (update ONE own row) and `compare_own_update.py` (PASS only if no other row changed).

**Since Common Features sittings 4 and 5 (batches 11 to 13, 2026-11-25/26):** totals now **88 tested, 12 written, 0 failed, 10 screen-only** of 935. Common Features: **72 tested, 8 written, 0 failed, 8 screen-only, 60 open** of 148. New test records: users `GAPFILL_AB_B11_U1`, `U2F`, `U3R` (example.com mailbox, nobody signs in; U1 and U2F have 3 roles and data access grants), billing methods `GAPFILL_AB_B12_IM2/IM3F/IM4R`, `RM1/RM2F`, LOV sources `GAPFILL_AB_B12_LOV1` to `LOV6F`, country default rows `AQ`, `BV`, `HM`. New helper `common-features\set-help-options\scripts\one_value_package.py`. `rebuild_index.py` and `build_module_tracker.py` now accept a card with status `screen-only`.

**Procurement sitting 3 (2026-11-25, demo task only):** Manage FOB Lookup (`PO_MANAGE_FOB_LOOKUP`) released by AB from the demo reserve and **tested** (own `GAPFILL_AB_B5_FOB1`, re-test `GAPFILL_AB_B5_FOB3R` PASS; fresh round F broke on a network drop before a ProcessId, nothing created, skill rule added). Skill `procurement\manage-fob-lookup`, report `procurement\BATCH_05_RESULT.md`, evidence `evidence\batch-05` (5 PNGs). Freight Terms stays reserved. Totals now **74 tested, 18 written, 0 failed, 6 screen-only**; Procurement 14 / 4 / 2, **6 open**.

**Dashboard (2026-11-25):** new `dashboard\` folder: a public gap dashboard at https://fscr-gap-dashboard.vercel.app (Vercel project `fscr-gap-dashboard`, deployed from this folder, no GitHub). `update.py` builds `data\` from the index; steps in `dashboard\UPDATE_STEPS.md`, number definitions in `dashboard\README.md`. `dashboard\.env.local` (Vercel token) and `.vercel\` are git-ignored.

**Since Procurement sittings 1 and 2 (2026-11-25):** totals now **73 tested, 18 written, 0 failed, 6 screen-only**. Procurement: 13 tested, 4 written (unsafe), 2 screen-only, **7 open** of 26 (2 reserved for a live demo: FOB and Freight Terms lookups, `procurement\DEMO_RESERVE.md`; 5 approval / task-configuration tasks). Sitting 1 was stopped at about 17:30 by the org's monthly Claude spend limit and finished after the reset. Module files: `gaps-filled\procurement\` (`my_gaps.csv`, `MODULE_TRACKER.csv`, `MODULE_RESULT.md`, `screen-only.csv`, 17 skill folders, evidence). New helpers in `procurement\scripts\`: `build_csv_package.py` (`--copy-row`, `--edit-row`), `compare_exports.py`, `lookup_type_row.py`, `build_module_tracker.py`, `read_import_log.py`, `profile_option_row.py`. Records: `GAPFILL_AB_B1_..` to `GAPFILL_AB_B4_..` (see `MODULE_RESULT.md`); 3 shared settings changed and restored (clause XML location, collab messaging parameter, 2 channel setting values).

**Since batches 09+10 (2026-11-25):** totals now **60 tested, 14 written, 0 failed**, plus 4 proven screen-only (`common-features\screen-only.csv`). Common Features: **72 open**. New helper `common-features\scripts\rest_call.py` (runs FSCR's REST client unchanged but shows Oracle's real error text). Records `GAPFILL_AB_B9_..`, `GAPFILL_AB_B10_..` (incl. test customer `GAPFILL_AB_B9_CUST3R`, test doc sequence categories `B9_LC1`, `B9_BC1`, billing extensions `B10_BX2` Invoice, `B10_BX3F` Revenue).

**Since 2026-11-25 (batches 05 to 08):** totals now **56 tested, 8 written (unsafe to test), 0 failed**. Common Features: 54 tested, 8 written, **86 open** of 148. Module summary and per-task list: `gaps-filled\common-features\MODULE_RESULT.md`, `MODULE_TRACKER.csv`, `my_gaps.csv` (built by `common-features\scripts\build_module_tracker.py`). New helpers: `search-legal-entities\scripts\view_record.py` (read-only export viewer), `tree_rows.py`. Records: `GAPFILL_AB_B5_..` to `GAPFILL_AB_B8_..` (see each batch result). The new STATUS cards are in the per-task folders; the table below lists only the first 44. Also made: `gaps-filled\GAP_LEVEL_COUNT.md` (b/c count per module, files only) and `fscr-main\fscr-module-test-pack\evidence\Security\SECURITY_IMPACT.md` (what each of the 6 Security tasks would change, read only; raw reads in `E:\GoSaaS\gw\secimpact`, outside repo).

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
| ZX_MANAGE_TAX_ZONE_TYPES | Manage Tax Zone Types | Common Features | tested | 2026-11-24 | 24 / 8 / 14 (taxfix2 only) |
| ZX_MANAGE_TAX_REGIMES | Manage Tax Regimes | Common Features | tested | 2026-11-23 | 7 / 6 / 5 |
| ZX_MANAGE_TAX_REPORTING_TYPES | Manage Tax Reporting Types | Common Features | tested | 2026-11-23 | 5 / 5 / 4 |
| ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS | Manage Tax Determining Factor Sets | Common Features | tested | 2026-11-23 | 4 / 4 / 3 |
| ZX_MANAGE_TAXES | Manage Taxes | Common Features | tested | 2026-11-23 | 8 / 9 / 5 |
| ZX_MANAGE_TAX_STATUSES | Manage Tax Statuses | Common Features | tested | 2026-11-24 | 17 / 12 / 24 |
| ORA_ZX_MANAGE_TAX_FORMULAS | Manage Tax Formulas | Common Features | tested | 2026-11-23 | 5 / 5 / 3 |
| ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES | Manage Tax Rates and Tax Recovery Rates | Common Features | tested | 2026-11-24 | 12 / 6 / 6 |
| ZX_MANAGE_TAX_JURISDICTIONS | Manage Tax Jurisdictions | Common Features | tested | 2026-11-24 | 12 / 11 / 7 |
| ZX_MANAGE_TAX_CONDITION_SETS | Manage Tax Condition Sets | Common Features | tested | 2026-11-24 | 9 / 6 / 5 |
| ZX_MANAGE_TAX_RULES | Manage Tax Rules | Common Features | tested | 2026-11-24 | 14 / 6 / 11 |
| ZX_MANAGE_PARTY_FISCAL_CLASSIFICATIONS | Manage Party Fiscal Classifications | Common Features | tested | 2026-11-24 | 5 / 8 / 9 |
| ORA_GL_MANAGE_SHORTHAND_ALIASES | Manage Shorthand Aliases | Common Features | tested | 2026-11-24 | 5 / 3 / 9 |
| XLE_MANAGE_LEGAL_AUTHORITIES | Manage Legal Authorities | Common Features | tested | 2026-11-24 | 7 / 7 / 9 |
| XLE_MANAGE_LEGAL_ENITTY_PROFILE_OPTIONS | Manage Legal Entity Configurator Profile Options | Common Features | tested | 2026-11-24 | 4 / 4 / 3 |
| ORA_ZX_MANAGE_TAX_PROFILE_OPTIONS | Manage Tax Profile Options | Common Features | tested | 2026-11-24 | 3 / 3 / 3 |
| ORA_ATK_ADMIN_PROFILE_OPTION_VALUES | Manage Application Toolkit Administrator Profile Values | Common Features | tested | 2026-11-24 | 4 / 3 / 3 |
| FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_ENTITIES | Manage Applications Core Attachment Entities | Common Features | tested | 2026-11-24 | 6 / 3 / 5 |
| ZX_MANAGE_TRANSACTION_FISCAL_CLASSIFICATIONS | Manage Transaction Fiscal Classifications | Common Features | tested | 2026-11-24 | 8 / 13 / 9 |
| ORA_ZX_MANAGE_TRANSACTION_BASED_FISCAL_CLASSIFICATIONS | Manage Transaction-Based Fiscal Classifications | Common Features | tested | 2026-11-24 | 4 / 7 / 6 |
| ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS | Manage Product-Based Fiscal Classifications | Common Features | tested | 2026-11-24 | 3 / 3 / 5 |
| HZ_MANAGE_RESOURCE_NOTE_TYPE_MAPPING | Manage Resource Note Type Mapping | Common Features | tested | 2026-11-24 | 5 / 6 / 2 |
| ORA_ZX_MANAGE_PARTY_TAX_PROFILES | Manage Party Tax Profiles | Common Features | tested | 2026-11-24 | 5 / 8 / 9 |
| ZX_MANAGE_TAX_EXCEPTIONS | Manage Tax Exceptions | Common Features | tested | 2026-11-24 | 4 / 4 / 3 |
| ORA_ZX_MANAGE_LOCATION_FINAL_DISCHARGE | Manage Location of Final Discharge | Common Features | tested | 2026-11-24 | 4 / 6 / 2 |
| ORA_ZX_MANAGE_TAX_EXEMPTIONS | Manage Tax Exemptions | Common Features | tested | 2026-11-24 | 12 / 9 / 7 |
| GL_MANAGE_JOURNAL_CATEGORIES | Manage Journal Categories | General Ledger | tested | 2026-11-15 (re-test 2026-11-24) | unknown / 4 / unknown |
| ORA_MANAGE_ALTERNATE_NAME_MAPPING_RULES | Manage Alternate Name Mapping Rules | Receivables | tested | 2026-11-16 (re-test 2026-11-24) | unknown / 12 / unknown |

**Tax chain fixed (2026-11-24):**
- **Tax Statuses, Rates, Rules:** real cause = the test regime had no **global configuration owner (GCO) option row** (`ORA_ZX_BU_GCO_TAX_SUB.csv`, in the taxes/regimes package). Added as **Step 7 of `manage-tax-regimes`** (fresh test + re-test pass). After that all three imported first try and passed fresh tests. No live tax and no business unit subscription needed.
- **Tax Zone Types:** real cause = `CreatedBy` and `LastUpdatedBy` left empty. Fill them from the export's `SubmittedBy` (helper `manage-tax-zone-types\scripts\zone_type_rows.py`). The taxfix "Oracle defect, needs SR" conclusion was **wrong**; no SR needed.
- Records made: GCO rows on `GAPFILL_AB_TR1`, `TR2F`, `TR3R`; tax `GAPFILL_AB_TF_TX2` (not live); statuses `GAPFILL_AB_TF_ST1/ST2F/ST3R`; rates `GAPFILL_AB_TF_RT1/RT2F`; rules `GAPFILL_AB_TF_RL1/RL2F` (disabled); zone types `GAPFILL_AB_TF_ZT1` (screen, by AB), `GAPFILL_AB_TF2_ZT2..ZT5R`.

**Batch 4 (2026-11-24):** 12 Common Features gaps, all **tested** after the fix. Records: `GAPFILL_AB_P1_..`, `P2_..`, `P3_..` (see each Part result), plus `GAPFILL_AB_B4FIX_CUST1/CUST2F` (test customers with THIRD_PARTY tax profiles, no account site or transactions), exemptions `GAPFILL_AB_B4FIX_EXM1/EXM2F` (on test tax `GAPFILL_AB_P1_TX1`, not live), legal authority `GAPFILL_AB_B4FIX_LA5R`. New helper `manage-transaction-fiscal-classifications\scripts\fiscal_code_rows.py` (writes the 4 code/denorm rows). Work folders `E:\GoSaaS\gw\b4p1..b4p3`, `b4fix` (outside repo). `PEOPLE_PROMPT.md` rewritten: one paste runs all batches of a module without stopping (Opus, sign-in renewal, prerequisites, re-test rule).

**Security re-check (2026-11-24, read only):** `boss_scope` set in the pack's git-ignored `fusionEnv.properties`; BOSS sign-in works. 6 of 6 Security tasks read OK; no load done; Execution stays blank. Blocked by: no `rmc_scope` (tasks 3, 4), no Risk Administrator role (tasks 2, 5, 6), and safety approval (tasks 1, 2, 5, 6). Report: `fscr-main\fscr-module-test-pack\evidence\Security\SECURITY_RERUN_RESULT.md`.

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
| batch taxfix | `gaps-filled\BATCH_TAXFIX_RESULT.md` | 2026-11-24 | tax statuses, rates, rules fixed (GCO row); regimes Step 7 |
| batch taxfix2 | `gaps-filled\BATCH_TAXFIX2_RESULT.md` | 2026-11-24 | tax zone types fixed (who columns) |
| batch 4 | `gaps-filled\BATCH4_PLAN.md`, `BATCH4_PART1..3_RESULT.md` | 2026-11-24 | 12 Common Features gaps: 11 tested, Tax Exemptions failed |
| batch 4 fix | `gaps-filled\BATCH4_FIX_RESULT.md` | 2026-11-24 | Tax Exemptions tested (CRM REST customer + profile); Party Tax Profiles wording re-tested |
| batches 09+10 | `gaps-filled\common-features\BATCH_09_RESULT.md`, `BATCH_10_RESULT.md` | 2026-11-25 | 10 Common Features gaps: 4 tested, 6 written (unsafe), plus 4 screen-only |
| batches 11+12 | `gaps-filled\common-features\BATCH_11_RESULT.md`, `BATCH_12_RESULT.md` | 2026-11-25 | 10 Common Features gaps tested (5 re-opened from written), plus 3 screen-only |
| batch 13 | `gaps-filled\common-features\BATCH_13_RESULT.md` | 2026-11-25/26 | 4 Common Features gaps tested, 1 screen-only (help content) |
| batches 14+15 | `gaps-filled\common-features\BATCH_14_RESULT.md`, `BATCH_15_RESULT.md` | 2026-11-26 | 10 Common Features gaps: 9 tested (3 re-opened from written), 1 failed (application tax options) |
| Procurement 3 (demo) | `gaps-filled\procurement\BATCH_05_RESULT.md` | 2026-11-25 | Manage FOB Lookup tested for the demo |
| Procurement 1, 1b, 2 | `gaps-filled\procurement\BATCH_01..04_RESULT.md`, `MODULE_RESULT.md` | 2026-11-25 | 19 Procurement tasks moved: 13 tested, 4 written (unsafe), 2 screen-only |
| Sourcing 1 | `gaps-filled\sourcing\BATCH_01_RESULT.md`, `BATCH_02_RESULT.md` | 2026-11-27 | 10 Sourcing gaps tested (5 lookups, 2 value sets, negotiation styles, attribute lists, qualification areas) |
| Sourcing 2 | `gaps-filled\sourcing\BATCH_03_RESULT.md`, `BATCH_04_RESULT.md`, `MODULE_RESULT.md` | 2026-11-28 | 7 tested (models, 2 DFFs, rule sets, supplier match, qualification controls, create supplier by REST), 3 screen-only; Sourcing 17 tested, 3 screen-only, 6 open |
| Security re-check | `fscr-main\fscr-module-test-pack\evidence\Security\SECURITY_RERUN_RESULT.md` | 2026-11-24 | read-only, boss_scope set; 6 of 6 read OK, loads blocked |

## 10. Time measured

- Easy gap: about **10 min per gap elapsed** (first of a pattern about 11, reuse 1 to 3 working minutes). Batch 1: 10 gaps in about 77 minutes wall clock; working 33 + fresh test 25 + Oracle waiting 27 minutes (`gaps-filled\GAPS_PLAN.md` section 0).
- Medium about 25 min and hard about 50 min: **guesses**, not measured.
- Estimate: about 2 to 3 weeks with active people, expecting **700 to 800 filled** (75 to 85% of 935).
- About **150 screen-only** tasks, up to 186 (all "c"): a later phase.

## 11. Rules and decisions

- Screen-only tasks are deferred.
- Security scopes: `boss_scope` is now set (exact registered string, in the git-ignored `fusionEnv.properties`); `rmc_scope` (Risk Cloud) is still **missing**, the admin must add it to the sign-in app.
- Keep answers short and in simple words.
- Oracle test record names: only `ZZ_TEST_`, `FSCRT_`, `GAPFILL_<INITIALS>_` style; never real company names.
- Secrets never go in git or chat (SYNC_RULES.md).
- **Test record names:** `GAPFILL_AB_P<part>_<name>` (for example `GAPFILL_AB_P2_RT1`), so parts running at the same time never see each other's records. Give `copy_parent_rows.py` the **parent's** own prefix (it can differ from the child's).
- **Never import twice** after a dropped connection: first check by REST or a new export whether the record exists. Re-run a failed export into a new folder, one at a time, up to 3 tries. Keep every FSM ProcessId (ESS request numbers do not open the process log). `0 rows were processed` is a failure.
- **Text minimum lengths** (for example a TEXT tax reporting type needs MinLength) and **name maximum lengths** (for example 15 characters for withholding tax calendar names): find them in the live test and give the builder `--max-len`.
- **Profile-style (hierarchical) imports need the parent row** in the file: copy it unchanged with `common-features\manage-profile-options\scripts\copy_parent_rows.py` (only your own `GAPFILL_` parents).
- **Skills must be generic:** never mention ETIA-TEST, never hard-code paths (use `FSCR`/`GAP`/`PREFIX` placeholders; the FSCR copy is the one whose `fusionEnv.properties` is filled in), never take internal IDs from an export. In Git Bash pass `E:/...`, never `$PWD` (`/e/...`).
- **Fresh tests that share an FSM package run one after the other**, not in parallel.
- **Tax content prerequisite:** statuses, rates, rules (and likely exemptions, exceptions, other content under a GCO tax) need the regime's **GCO option row** (`manage-tax-regimes` Step 7). A tax does not need to be live; no business unit subscription is needed. Keep test rules disabled. Still: do not make test taxes live or add subscriptions without AB's decision.
- **Who columns:** if a row validates (`1 rows processed, 0 failed`) and then fails with `JBO-26041` at the insert, fill `CreatedBy` / `LastUpdatedBy` from the export's `SubmittedBy` first. A round trip of a screen-made record's own export splits "file problem" from "import problem".
- **Diagnosis order:** read the `JBO-` message first; if it names a column, compare with working records of the same object (a wider read-only export). Use the who-columns / round-trip rule for generic errors.
- **Child-only tasks:** a seeded parent row may go in the file only **unchanged** (`copy_parent_rows.py`), and the after-export compare must show it changed 0. The import log counts only the top object; the compare is the proof for child rows.
- **Fiscal classification codes** need 4 rows (code, translation, denorm, denorm translation): use `fiscal_code_rows.py`.
- **Tax exemptions** live only on a customer (THIRD_PARTY) tax profile. Make a `GAPFILL_` test customer and its profile by CRM REST (`accounts`, `partyTaxProfiles`; GET first, POST only if missing) through FSCR's REST client.
- **Read ids live by REST** (for example `profileOptions` by `ApplicationShortName`), never from an export.
- **Prerequisites inside one package** (for example an ATK option + its value) go in one import when the package allows it.
- **Safe wording for reports:** "tested by a fresh Claude on ETIA-TEST, record created and read back".
- **"Written (unsafe to test)"** is a status: a task whose load changes a shared or seeded setting (seeded profile values, a work-area link, country tax defaults, the profile Oracle makes for each legal entity / reporting unit, configuration owner options, the legal entity package) gets a skill but no load. Read steps VERIFIED, load steps GUESS. Load-test only on an environment we own, with written approval.
- **Import log counts only the top object:** child rows can drop silently (daily rates: rule rows with `EnabledFlag=Y` are dropped; use `N`). The after-export compare is the proof.
- **Fresh-test briefs must use their own parent** (ledger, category, etc.) when the object allows one open row per parent (FND-7020 on ledger document sequences).
- **"Neither" tasks:** check read-only export and REST GET per task before calling one screen-only; write the result in `my_gaps.csv`. Proven screen-only tasks go in `common-features\screen-only.csv`. A task that has a skill (for example a read step) keeps its STATUS card with `status: screen-only` and the same reason as in `screen-only.csv` (decided 2026-11-26 for Manage Help Content).
- **REST errors:** FSCR's REST client shows gzip error bodies as garbage; use `common-features\scripts\rest_call.py` to read Oracle's real message.
- **REST `q=` filters:** on some resources (for example `taxRegistrations`) `q=A and B` returns 0 rows; use `q=A;B`. A duplicate check must be proven to find a known row first.
- **After-export compare:** if the export gave no ZIP, the compare shows false "removed" rows; check the ZIP exists first.
- **Lookup-coded columns** (for example billing extension `CallingProcess`) take the lookup code, not the meaning; read codes live.
- **Also unsafe (written, not loaded):** anything that creates users or HR persons, grants a real user data access, or needs a real person as owner resource (partner organizations).
- **Demo reserve:** Procurement Freight Terms lookup (`PO_MANAGE_FREIGHT_TERM_LOOKUP`) stays open for a live demo; never fill or test it in a sitting (`procurement\DEMO_RESERVE.md`). FOB was released by AB and filled on 2026-11-25 (sitting 3).
- **Import dropped before a ProcessId:** do not import again; poll REST for about 10 minutes and prove with a new export that nothing was created; a second try needs AB's approval (rule in `manage-fob-lookup`).
- **Dashboard:** "update the dashboard" = follow `dashboard\UPDATE_STEPS.md` exactly (rebuild index, `update.py` must say all checks passed, `vercel --prod --yes` in a visible tab, check the live link). Never print or commit `dashboard\.env.local`; no names of people, environments or users in `dashboard\`; no GitHub link.
- **Test-and-restore** is allowed for a single shared setting when the old value is read first, the change is proved, and the old value is put back and proved (clause XML location, collab messaging, channel settings). Settings with one row per live business unit stay written-unsafe.
- **Extensible seeded lookup types:** the export has 0 rows, so the load carries the seeded type row **unchanged** (from REST) plus the new code (`lookup_type_row.py`).
- **Compliance checklists:** section and question usage `ORA_CHECKLIST`, template usage `CHECKLIST` (`ORA_CHECKLIST` imports "successfully" but the template is invisible); a template section row needs `ObjectVersionNumber1=1`; an active section needs at least 1 active question.
- **Credentials:** a task that needs provider or endpoint credentials (electronic signature, external integration targets) is written-unsafe; an agent never enters them.
- **New unsafe rule (2026-11-25, sitting 4):** creating a NEW prefix record nobody uses is not unsafe, even for users, security, tax or partners (own test user, own grants, own test methods). Re-judge every written card against it.
- **Data access grants by REST `dataSecurities`:** the user must already hold the role; `RoleNameCr` takes the role's display name; filter rows with `q=Userrf='...'` (`UserName` returns 0). FSCR's SCIM role PATCH answers with an empty body and FSCR shows a false "error": check roles with a single-user SCIM GET.
- **USER profile values by REST** (`userProfileOptionValues`): `LevelValue` = the user's GUID (SCIM id), not the user name.
- **SITE-only profile options** (click to dial, guided learning): REST PATCH `siteProfileOptionValues/SITE` as test-and-restore; write both body files first, so the value is changed only for seconds. A task's option name can be read from the export's metadata scope even when the CSV has 0 rows.
- **FSM import result** is in `<out>/*_process_log.txt`; FSCR's import log may end with `StatusCode: (unknown)`, which is normal.
- **Country default controls:** a test row for an uninhabited territory (AQ, BV, HM) with every default `N` is safe; the CSV route cannot delete it.
- **Help content:** the CSV cannot create a new topic (`PrimaryHierarchyIds` rejected on insert, whatever value is sent; only the page creates the hierarchy ID). Screen-only for create; read by export works.
- **Sign-in expiry:** a token lasts about 1 hour; an export that hits an expired token waits for an OAuth callback. Stop it, free port 8765, sign in again.
- **Test legal entity chain (2026-11-26):** a NEW prefix legal entity (`test-legal-entity` skill; address row needs `OrigSystemReference`) gets its own main reporting unit and tax profiles; updating only those rows is safe. Update one own row with `own_row_package.py` and prove with `compare_own_update.py`. Financial information packages must come from the same task's export (other task's package: HTTP 400); `ActivityCode` = NAICS 1997 code; the reporting unit row needs its parent legal entity row unchanged.
- **Test business unit:** `test-business-unit` skill (`OrganizationCode <BU>$$?$$FUN_BUSINESS_UNIT`, set COMMON). Legal associations need a business unit with a location; `BusinessEntityAddress` = exactly three spaces (builder trims; set after build), else `XLE_ASSOC_OBJECT_ID_REQUIRED`. A prerequisite skill gets its own RUN folder.
- **Set assignments task** handles determinant type `SET` only (BU gives JBO-27014); test with an own reference data set.
- **Segment value security:** test only on a NEW secured value set (GL `ModuleId` read live from `standardLookups GL_%`) and a policy on it; never send the chart of accounts options or the global usage row.
- **A refused re-send is not proof** unless a control shows the check really uses your key: application tax options refuses ANY AP row with `ZX_APPL_OU_UNIQUE` (even an unknown business unit name). Test a probe with a name that does not exist before trusting a uniqueness refusal.
- **Approval rules** (REST `approvalRules`) need a `ParticipantId` and change who approves live documents: read participants first, then decide disabled-rule test or unsafe.
- **Screen-only needs proof on its own card (2026-11-26):** task export refused (flag N), direct REST GETs (404 or read-only describe), Oracle docs. The version-level REST describe does not list every resource, so a missing name there proves nothing. A guess is never screen-only (16 were set back after the audit).
- **Flexfields:** load a new context DISABLED with the parent row unchanged; no deploy needed. First load of a flexfield with no user context = export empty before (check with `check_dff_rows.py`).
- **Resource organizations:** crm `resourceUsers` builds members, hierarchy and new internal organizations (no separate resource).
- **A new worker or user with no roles is not unsafe** (Import Worker Users tested). A partner owner must be a resource with a user account (refused otherwise).
- **Tax partners (Avalara, Thomson Reuters):** `taxPartnerRegistrations` needs a real partner account and password, has no delete: written unsafe.
- **Shared with no delete = unsafe:** geography loads (master geography), cross-validation rules (Replace mode deletes), archive and purge policies, publish account hierarchies (balances cube), associated balancing segments (whole ledger setup). Do not try a load once a task is judged unsafe (batch 24 slip).
- **Tax box rules:** `DET_TAX_BOX`, periodicity `PERIODIC`/`ANNUAL`, result `CODE` needs `AlphanumericResult`; rule order (`Priority`) must be unused on the same tax.
- **Enterprise structures:** the task CSV makes only a configuration draft; never press Load Configuration for a test draft.
- **Messages tasks:** route is a MESSAGES file + scheduled process, but the job name is not published; AB must read it once on the Scheduled Processes page.
- **Approval rules (Procurement):** REST `approvalRules` POST needs `ConditionAttributeId` read live from `approvalAttributesLOV` (`q=TaskId=..`); `ConditionTypeCode`, `ActionNumber`, `ConditionAttributeKey` cannot be set. `Task` and `AttributeKey` are not queriable. A REST rule is a pending change (task `HasPendingRuleChangesFlag`); never deploy or discard (discard drops others' changes); no REST delete. Test rule = disabled, LOW, amount > 999999999999, Automatic/Rejected.
- **Tasks not upgraded from BPM** (`IsRulesUpgradedFlag=False`, POR-2011627): written unsafe; the upgrade is a shared one-time page action with no REST undo.
- **Business-function tasks:** test on an own prefix business unit: first `FUN_ASSIGN_BUSINESS_UNIT_BUSINESS_FUNCTION` with `ModuleId` 110 (Procurement), then the task's row. Procurement config needs an inventory org code (value only); contract properties need `GlobalBusUnitYn=N` and `LedgerYn=N` on a unit with no ledger.
- **Empty-flexfield DFF tasks** (OKC too): disabled context, parent by REST, no deployment needed; the old 'needs deployment = unsafe' reason was wrong.
- **Sourcing (2026-11-28):** rule-set status values come from lookup `POQ_RULE_SET_STATUS` (ACTIVE/INACTIVE; only `standardLookups` shows it, DRAFT refused): test with INACTIVE. Qualification model export lists only some models: read back by REST too.
- **Relationship types (HZ_MANAGE_RELATIONSHIP_TYPES) by CSV:** need role texts (Name), `CreatedByModule=HZ_RM_UI`, different subject and object plurals; a refused try leaves an RM_USER_ROLE lookup that makes the next try a duplicate (use new texts). REST `relationshipTypes` is read only. Supplier match list (shared, no delete): add only an own new type.
- **One-global-row tasks with no create** (Supplier Qualification Controls): test-and-restore one low-impact flag, both packages built first, restore proved by compare with the first export.
- **Create Supplier in Procurement:** CSV flag N; REST `suppliers` POST works (PROSPECTIVE, no sites).

## 12. Pending

- Drive upload of `gaps-filled\_drive_ready\gaps-filled`.
- Gap tracker sheet with an "Assigned to" column.
- Phase 2 and `PEOPLE_PROMPT.md` in the tester guide doc.
- Pilot `PEOPLE_PROMPT.md` with one person (Zaid).
- Status email to Younas bhai.
- Owners for HCM, Logistics and PLM.
- How to split the big modules (PFM, GL, Common Features).
- Imtenan (Supply Planning) agreement.
- Security admin asks: add Risk Cloud scope to the sign-in app and send the `rmc_scope` value (tasks 3, 4); give the test user Risk Administrator (tasks 2, 5, 6); written OK before any load (tasks 1, 2, 5, 6); real EPM connector details (task 3). Update the Security tracker row with the wording in `SECURITY_RERUN_RESULT.md`.
- Delete the empty folder tree `E:\e\` by hand (left by a `/e/...` path slip in batch 3 part 2; it holds no files).
- Open tester notes (not applied, each needs a re-test if applied): see "Problems and findings" in `BATCH4_PART1..3_RESULT.md` and `BATCH4_FIX_RESULT.md`; the `manage-profile-options` Step 5 log one-liner still prints a `Submitted By` user name (Part 1 finding 6).
- Pilot the new `PEOPLE_PROMPT.md` (one paste, all batches) with one person.
- Security: send the 5-line ask in `SECURITY_IMPACT.md` to the senior (audit OK, which algorithms, default owners, Risk Administrator role, `rmc_scope`).
- Approval to load-test the 12 "written (unsafe to test)" tasks on an environment we own (or leave them written). Common Features has 5 left: CRM BU profile options and Map Reports to Work Areas (no safe way), Intercompany Exceptions (needs a test ledger), Import Worker Users and Partner Organizations (safe way = a new test worker chain). The 3 legal-entity tax tasks were tested on 2026-11-26 with a test legal entity.
- FSCR has an implementation-users skill (SCIM) its catalog does not map to `FND_CREATE_IMPLEMENTATION_USERS`: worth telling Oracle / the team.
- **Procurement:** finished except the demo reserve (Freight Terms lookup). AB to upload `gaps-filled\procurement` to Drive (FSCR > gaps-filled, Replace). The 6 test approval rules are pending changes on Requisition and Purchasing Document Approvals: never deploy them; remove on the page if the pending flag bothers anyone. 3 written-unsafe (Work Confirmation and Intake Request Approvals need the rules upgraded from BPM; Electronic Signature needs provider credentials) need an environment we own. Tester suggestions "not applied" are listed in each STATUS.md.
- **Next:** Common Features has **0 open**. Left are the 7 failed, each needs AB first: (1) check the Manage Application Tax Options page (application AP) for a row from ProcessId 100004744413261, then retry with the column that ties the row to a business unit; (2) localization privilege for Italy and China options (pod owner); (3) approval for a partner owner resource with a user account; (4) read the MESSAGES upload job name once on the Scheduled Processes page (3 message tasks). Then the 15 written-unsafe tasks need an environment we own. Sourcing has 6 open (see the Sourcing line); Procurement is finished except the demo reserve.
- **Sourcing:** 17 tested, 3 screen-only, **6 open**, all "neither": Load Supplier Interface through Scheduled Process, Upload Supplier Import File (FBDI pair), Supplier Negotiation Approvals and Award Approvals (check approval REST), Sourcing Messages and Supplier Qualification Messages (MESSAGES job name, see rule). AB to upload `gaps-filled\sourcing` to Drive (FSCR > gaps-filled, Replace). 2 orphan role lookups (own texts) from refused relationship-type tries stay.
- Commit is done; **AB to run `git push`**.

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
