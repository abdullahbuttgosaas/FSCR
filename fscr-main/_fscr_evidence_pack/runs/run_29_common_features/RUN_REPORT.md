# Run 29: how well does FSCR cover ERP "Common Features"?

Generic, read-only desk review. **No Oracle calls were made.** Nothing was created or changed in Oracle, in the tracker or in FSCR files. All new files are in this folder.

**Tags:** VERIFIED = seen in a file or output (path given) · FROM FSCR = FSCR file and line · GUESS = my judgment.

## Time log

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 2026-11-16 19:57 | 2026-11-16 20:05 | 8 | Times from `start_time.txt` and `finish_time.txt`. Reading the catalog started before the folder existed, so total work was longer; the exact start was not recorded. |

## 1. Common Features tasks per functional area

Levels use the Run 23 definition, applied to Run 07 `tasks.csv` (VERIFIED, `scripts/build.py`, output `area_counts.csv`):
- **Route + instructions** = the task has an FSCR skill or task guide (Run 07 "Skill" column is not "none").
- **Route, no instructions** = no skill, catalog CSV flag Y.
- **No route, no instructions** = no skill, CSV flag N or UNKNOWN.
- **438 column** = the "neither" tasks plus the skill tasks whose skill names no FSM_CSV or REST route.

| Functional area (catalog code) | Tasks | Route + instructions | Route, no instructions | No route, no instructions | Skill names no CSV/REST route | No route under 438 definition |
|---|---:|---:|---:|---:|---:|---:|
| Initial Users (ORA_ASK_INITIAL_USER) | 6 | 4 | 0 | 2 | 4 | 6 |
| Enterprise Profile (ORA_ASK_ENTERPRISE_PROFILE) | 15 | 9 | 3 | 3 | 0 | 3 |
| Legal Structures (ORA_ASK_LEGAL_STRUCTURES) | 19 | 8 | 11 | 0 | 0 | 0 |
| Financial Reporting Structures (ORA_ASK_FIN_REPORTING_STRUCT) | 30 | 15 | 13 | 2 | 3 | 5 |
| Organization Structures (ORA_ASK_ORGANIZATION_STRUCTURE) | 19 | 10 | 2 | 7 | 0 | 7 |
| Workforce Structures (ORA_ASK_WORKFORCE_STRUCTURE) | 6 | 6 | 0 | 0 | 0 | 0 |
| Users and Security (ORA_ASK_USERS_AND_SECURITY) | 9 | 5 | 3 | 1 | 1 | 2 |
| Application Extensions (ORA_ASK_APPLICATION_EXTENSIONS) | 45 | 11 | 18 | 16 | 3 | 19 |
| **All (unique tasks)** | **144** | **65** | **49** | **30** | **10** | **40** |
| Financials offering only (unique) | 123 | 54 | 41 | 28 | 10 | 38 |

- 5 tasks sit in two areas (for example Manage Currencies, Manage Reference Data Sets), so the area rows add up to 149, not 144. VERIFIED.
- **Under the 438 definition** the totals change: Route + instructions **55**, Route, no instructions **49**, no route **40** (30 + 10). The 10 that move are 4 Initial Users tasks (ESS or none), 3 security tasks, Manage Account Combinations and Manage Chart of Accounts Value Set Values (FBDI only), and Manage Currencies (manual only). VERIFIED (`common_features_tasks.csv`, column `level_under_438_definition`).
- These 144 tasks are a slice of the 2,616. Run 07 put only 46 of them in "ERP"; 56 are "Multiple", 17 HCM, 9 CX, 6 Common and the rest mixed, because Run 07 uses the skill's pillar or the pillars of all offerings. So they do not add up to the 730 ERP figure. VERIFIED.
- Where the instructions live: of the 65 tasks with a skill, only 23 have a skill under `pillars/erp`. 17 use HCM skills, 10 use `pillars/common/security-console`, 9 CX and 5 SCM. VERIFIED.

**Unlinked FSCR content (does not change the counts above).** 17 of the 79 tasks with no skill are still named in an FSCR file that Run 07 did not link (VERIFIED, `unlinked_mentions.csv`):
- 13 one-line manual cards in `shared/common/manual-tasks/` (for example Manage Time Zones, Manage Languages). FROM FSCR `shared/common/manual-tasks/SKILL.md:4`: the skill "never automates the change".
- 2 attachment references in `core/fusion-api/apps-common/attachments/references/`.
- 2 implementation-user references in `core/getting-started/implementation-users/references/`.
- If these counted as instructions, 5 would move out of "Route, no instructions" and 12 out of "No route, no instructions". GUESS: most are manual cards, so they would not add a working route.
- The generic `core/fusion-api/apps-common` skills (lookups, value sets, profile options, descriptive flexfields) name no task code, so tasks such as Manage Applications Core Standard Lookups show as having no skill. GUESS: those skills do cover them in a generic way.

## 2. Proposed tracker row: ERP / Common Features

| Column | Proposed value | One-line reason |
|---|---|---|
| Test status | **In progress** | Real tests touched 11 Common Features tasks (business units: create, blocked update and reads; 10 others: export or read only), but there has been no dedicated Common Features test (VERIFIED, section 5). |
| FSCR coverage | **Partial** | 65 of 144 tasks have a skill or guide. The core structures (legal entity, business unit, chart of accounts, calendar, ledger) are covered, but Application Extensions (11 of 45) and approvals are mostly not (VERIFIED, section 1). |
| Fit rating | **Medium** | FSCR's export, rules and sign-in worked as they are, but each create, update or impact step needed a GoSaaS script or a manual workaround (VERIFIED, Runs 01, 03, 18–22). |
| Plan accuracy | **not run** | No Common Features plan was tested against a reference. Runs 11b, 14 and 15 planned enterprise structure on paper for one SOW and were not scored. |
| Runbook quality | **not run** | Run 01 used FSCR's Run Book for the business unit task (2 of 5 tasks marked done), but runbook quality was not scored. |
| Execution and validation | **not run** (PROPOSED 3 if a score is wanted) | Evidence: 2 BUs created and read back, but only with a GoSaaS builder (Run 01); a BU update was blocked by FSCR's own rule (Run 03); 10 more tasks exported or read; the BU and calendar workbook checks found no mismatch (Runs 19, 21), but the currencies export held only 9 of 268 rows (Run 18). This is from mixed tests, not one planned test. |
| FSCR skills / workflows used | `shared/setup-export/task-level-export`; `pillars/erp/financials/organization-structures` (manage-business-unit.md + ora-resource rules); `core/data-loader` + Task Hook; `core/runbook`; `pillars/erp/financials/financial-reporting-structures/manage-accounting-calendars`; `core/fusion-api/rest-api-client`; FSCR sign-in. | VERIFIED, Runs 01, 02, 03, 18, 20, 22. |
| Test scenario | Create 2 test BUs through FSM CSV; read them back; update a BU manager; export BUs, reference data sets, currencies, ledgers, calendars, chart-of-accounts values and conversion rate types; trace a calendar change through ledgers and BUs to Receivables in a workbook copy. | VERIFIED, Runs 01, 03, 18–22. |
| Fusion env / release | ETIA-TEST, 11.13.26.10.0 | VERIFIED, `_fscr_run_01/RUN_REPORT.md:4`. |
| Last tested | 2026-11-09 (Run 22, analysis on a copy; last live read Run 21). Last Oracle write on a Common Features task: 2026-11-03 (Run 01). | VERIFIED. |
| Key findings | see below | |
| GoSaaS gap / build needed | see below | |
| Evidence | `_fscr_run_29_common_features/` (this report, CSVs); `_fscr_run_01`, `_fscr_run_02_understand`, `_fscr_run_03_change`, `_fscr_run_05_breadth`, `_fscr_run_09_impact`, `_fscr_run_18_best_subject` … `_fscr_run_22_calendar_change_impact` RUN_REPORT.md files. | |

**Key findings (5)**
1. FSCR's generic setup export reads any Common Features task with a CSV flag, and it worked every time we used it: BUs (186), reference data sets, ledgers, calendars, chart-of-accounts values, conversion rate types. VERIFIED (Runs 02, 18, 20, 21).
2. The skills are guides, not builders: BU create needed a GoSaaS CSV builder, and FSCR's own rule blocked a BU update. VERIFIED (`_fscr_run_01/RUN_REPORT.md:19`, `_fscr_run_03_change/RUN_REPORT.md:35-39`).
3. Under half the tasks (65 of 144) have a skill, and most of those skills live under HCM, CX or SCM, not ERP. Application Extensions and approvals are the weakest. VERIFIED (section 1).
4. FSCR has no step that finds what uses a record (no impact walk). GoSaaS did all cross-module tracing for BUs and calendars. VERIFIED (`_fscr_run_18_best_subject/RUN_REPORT.md:154`, `_fscr_run_22_calendar_change_impact/RUN_REPORT.md:109`).
5. Some FSCR rules are useful as they are, for example the calendar continuity rule (FROM FSCR `manage-accounting-calendars/SKILL.md:179-229`) and the BU "align to one primary ledger" advice (FROM FSCR `manage-business-unit.md:56`). But the pod has 94 of 183 BUs with no ledger, so the advice does not match real data. VERIFIED (`_fscr_run_02_understand/RUN_REPORT.md:27`).

**GoSaaS gap / build needed (what GoSaaS built beyond FSCR)**
- GoSaaS built a BU CSV package builder (`_fscr_run_01/scripts/build_bu_package.py`) and a BU update builder (`_fscr_run_03_change/scripts/build_bu_update.py`). VERIFIED.
- GoSaaS built a REST reader for records FSCR does not read (`rget.py`, Runs 18–22) and an export-result fetcher (`_fscr_run_03_change/scripts/fetch_export_result.py`). VERIFIED.
- GoSaaS built the cross-file join and impact scripts (`bu_links.py`, `chains.py`, `impact.py`) and the BU and calendar workbooks. VERIFIED.
- GoSaaS wrote the Task Hook rule results itself, because FSCR only checks their shape. VERIFIED (`_fscr_run_03_change/RUN_REPORT.md`, "Amended (A1)").
- Still needed (GUESS): create/update recipes for the 49 route-only tasks (for example conversion rate types, daily rates, cross-validation rules), task links for the apps-common skills, and an approvals skill.

## 3. Scope: what "ERP Common Features" means in FSCR's catalog

**Rule used (VERIFIED):**
- Catalog file `fscr-main/knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`: fields `offerings.<code>.functionalAreas.<functionalAreaShortName>`, `functionalAreaName` and `tasks[].taskShortName`, `taskName`, `csvExportImportSupportedFlag`.
- Pillar comes from `pillars-offerings-mapping.json`, field `pillar`. Only offerings with pillar "ERP" were used (10 offerings).
- A functional area counts as Common Features when its `functionalAreaShortName` starts with **ORA_ASK_**. These 8 areas are the shared setup Oracle repeats across offerings: they appear in ERP, SCM and CX offerings alike (VERIFIED: 8 to 21 offerings each).
- FSCR itself uses the name "Application Common Features" for `core/fusion-api/apps-common` (FROM FSCR `core/fusion-api/apps-common/SKILL.md:4`).
- Skill, guide, CSV flag and routes come from Run 07 `_fscr_run_07_inventory/out/tasks.csv`, so the counts match the 2,616 / 848 / 1,373 / 395 totals. All 144 task codes were found in it. VERIFIED.

**Areas counted:** Initial Users, Enterprise Profile (reference data sets, geographies, locations), Legal Structures, Financial Reporting Structures (chart of accounts, calendars, currencies, rates, ledgers), Organization Structures (business units), Workforce Structures, Users and Security, Application Extensions (lookups, value sets, profile options, flexfields, attachments, languages, time zones).

**Unclear areas (flagged, not guessed silently):**
- **Financial Reporting Structures:** the catalog marks it ORA_ASK_, so it is counted. Some teams count ledgers, calendars and chart of accounts under General Ledger instead. GUESS.
- **Workforce Structures:** in ERP offerings, but the objects (departments, jobs) are HCM. Counted, but all 6 skills are HCM skills. VERIFIED.
- **Initial Users and Users and Security:** counted. FSCR keeps their skills in a separate "common" pillar (`pillars/common/security-console`). VERIFIED.
- **Organization Structures:** includes SCM and CX objects (inventory organizations, facility schedules, resource organizations, partner organizations). Counted because the catalog puts them there. GUESS that a GoSaaS ERP team would leave them out.
- **Application Extensions:** includes 6 project-only tasks (billing extensions, project process configurator, user-defined rules) from the Project offerings. The "Financials offering only" row leaves these out.
- **Approvals:** no ORA_ASK_ area holds approval tasks. Approvals are set up inside each module, so they are **not counted**. FSCR has only `shared/best-practices/approval-workflow-guidance/SKILL.md` (2 KB, one file). VERIFIED.
- **Not counted:** Banking Configurations, Resources, Transaction Tax, General Ledger (module areas, not ORA_ASK_). GUESS that Banking Configurations could be argued either way.

## 4. FSCR skills, guides and workflows for these areas

Full per-task paths are in `common_features_tasks.csv` (column `skill_paths`; 78 distinct files). Main ones:

| Path (under `fscr-main/`) | What it does | Stub? |
|---|---|---|
| `pillars/erp/financials/organization-structures/` (SKILL.md + 4 task guides + 11 ora-resource files) | BU, set assignment, business function and service-provider rules, checks and REST look-ups | No: rich rules, but no builder script (VERIFIED, 0 .py) |
| `pillars/erp/financials/legal-structures/` (SKILL.md + 6 task skills) | Legal entity, legal reporting unit, jurisdictions, addresses, registrations | No; Run 05 found the jurisdictions skill names 1 of 49 template columns (VERIFIED) |
| `pillars/erp/financials/financial-reporting-structures/` (SKILL.md + 7 task skills) | Chart of accounts, value sets and values, mappings, calendars | No; 0 scripts (VERIFIED) |
| `pillars/erp/financials/general-ledger/` (6 skills in scope) | Primary ledger, ledger options, balancing segments, legal entity assignment, submit accounting configuration | No; 0 scripts (VERIFIED) |
| `pillars/common/security-console/` (SKILL.md + 7 skills) | Job roles, duties, data security policies, role provisioning, bulk user-role provisioning | No for the main skills |
| `pillars/common/security-console/user-security-common/*.md` (8 cards, ~0.7 KB each) | Task routing cards that point to the owning skill | **Card only**: FROM FSCR `.../import-user-login-history.md:14` "does not introduce an execution route" |
| `core/fusion-api/apps-common/` (router + 8 sub-skills) | Lookups, value sets, profile options, descriptive/extensible/key flexfields, trees, attachments through REST | Thin: value-sets 1.7 KB and profile-options 2.1 KB, no scripts except trees (VERIFIED). Not linked to task codes |
| `shared/common/manual-tasks/` (SKILL.md + 17 cards, ~0.3 KB each) | Manual guidance only for languages, time zones, currencies, help and similar | **Cards only** (one line each); the skill "never automates" (FROM FSCR `SKILL.md:4`) |
| HCM skills reused (for example `pillars/hcm/goal-management/goal-management-common/manage-currencies`, `manage-reference-data-sets`; `global-human-resources/*`) | Currencies, reference data sets, locations, departments, jobs, legislative data groups | No, but they are written for HCM offerings (GUESS for fit to ERP) |
| CX skills reused (`pillars/cx/customer-data-management/enterprise-profile/manage-geographies`, `trading-community-foundation/*` profile options) | Geographies, geocoding, calendar/currency/data-warehouse profile options | No |
| `shared/setup-export/task-level-export` (7 scripts) | Generic FSM CSV export for any task | No: the working reader in every run |
| `shared/setup-import/fsm-csv-import`, `core/data-loader` (16 scripts), `core/runbook` | Generic import, Data Loader with Task Hook gate, Run Book record | No; generic (FROM FSCR `fsm-csv-import/SKILL.md:80` has the call but no task fields, per Run 23) |
| `shared/project-intake/enterprise-structure-intake/SKILL.md` | Enterprise structure intake | **Stub** (2.7 KB, generic headings; VERIFIED in Runs 11, 11b, 14) |
| `shared/best-practices/approval-workflow-guidance/SKILL.md` | Approval guidance | Thin (2.1 KB, one file); not checked further |

## 5. Earlier evidence for Common Features tasks (from run reports only; nothing re-run)

| Run | Task | Really run or paper | What FSCR gave | What GoSaaS (Claude) added | Result |
|---|---|---|---|---|---|
| 01 | Manage Business Unit (create 2 FSCRT BUs) | **Run** (Oracle write) | Route, BU rules, template export, Data Loader, Task Hook, Run Book | 60-line CSV builder `build_bu_package.py`; location look-up through an HCM resource because FSCR's returned 0 rows | 2 created, 0 failed; default set not readable by REST. VERIFIED `_fscr_run_01/RUN_REPORT.md:75,217` |
| 02 | Manage Business Unit (read) | **Run** (read) | Task-level export + LOV GETs | Plain-words explanation and cross-area links | Read fully, including default set. VERIFIED `_fscr_run_02_understand/RUN_REPORT.md:44` |
| 03 | Manage Business Unit (update manager) | **Run**, blocked | Rule registry, Task Hook | Update builder `build_bu_update.py` | **Blocked by FSCR's own rule** (create-only). Nothing reached Oracle. VERIFIED `_fscr_run_03_change/RUN_REPORT.md:35-39` |
| 05 | Legal jurisdictions, inventory organizations, data warehouse profile option | **Run** (export only) | Export route | Grading | Export OK; skills grade 0 (route only; 0–2% of template columns named). VERIFIED `_fscr_run_05_breadth/ledger.csv` |
| 08, 09 | Business units (compare, impact) | **Run** (read) | Export, compare | Impact reading | BU compare ran; FSCR has no impact step. VERIFIED `_fscr_run_09_impact/RUN_REPORT.md:55-77,93` |
| 18 | BUs, reference data sets, currencies, primary ledgers (BU set assignment too) | **Run** (export) | Export | Link counting, Oracle docs, scoring | All exported; currencies export held 9 of 268. VERIFIED `_fscr_run_18_best_subject/RUN_REPORT.md:66-68` |
| 19 | Business units (6-BU workbook) | **Run** (read) | Run 18 exports | Workbook builder and checker | All sheets matched sources. VERIFIED |
| 20 | Accounting calendars, chart-of-accounts value set values, conversion rate types | **Run** (export) | Export | Chain tracing calendar → ledger → BU → Receivables | 24 calendars, 454 periods exported. VERIFIED |
| 21 | Accounting calendars, ledgers, BUs (workbook) | **Run** (read) | Exports | Workbook, period-status reads | 0 mismatches against Run 20. VERIFIED |
| 22 | Accounting calendar change impact | **Analysis on a workbook copy only**; nothing applied to Oracle | Calendar edit and continuity rules, BU checklist, exports | Edit, detection, join, impact map (10 of 15 steps) | Impact traced to 13 ledgers, 37 BUs, 2 Receivables BUs. VERIFIED `_fscr_run_22_calendar_change_impact/RUN_REPORT.md:100-109` |
| 11b, 14, 15 | Enterprise structure intake and planning | **Paper only** (one SOW, no pod) | Org Structures BU design rules; intake skill is a stub | Everything else | Not a generic test; not used for scores. VERIFIED |
| 03 (side note) | Order lookups changed with `core/fusion-api/apps-common/lookups` | **Run** | Common Features lookups skill + REST client | Request bodies | Changed and verified. The task itself (DOO_MANAGE_ORCHESTRATION_LOOKUPS) is SCM, not Common Features. VERIFIED `_fscr_run_03_change/RUN_REPORT.md:76` |

Not tested at all: Initial Users, Workforce Structures, Users and Security, and Application Extensions as Common Features tasks. VERIFIED (no run report names them as tested).

## 6. Files in this folder
- `common_features_tasks.csv`: 144 tasks, one row each, with level, skill paths, CSV and REST flags.
- `area_counts.csv`: the table in section 1.
- `unlinked_mentions.csv`: the 17 no-skill tasks that FSCR files still name.
- `tracker_row.csv`: the proposed row.
- `scripts/build.py`, `scripts/unlinked.py`, `scripts/tracker_row.py`: read-only scripts that made the CSVs.

**REST flag note:** for tasks without a skill, REST support was not scanned (same caveat as Run 23). The column says "not scanned".

**Clean-up:** no server, listener or browser was started in this run. Only Python scripts ran, and each finished. One background `grep` was stopped by me. VERIFIED.
