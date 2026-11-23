# RUN_REPORT — run 12: Can FSCR do project planning for Twelve?

Question: from the Twelve SOW (50513scm) and the run 11b intake outputs only, can FSCR produce (1) an offering task map, (2) a wave plan, (3) task dependencies and (4) a readiness checklist?

Legend: **[V]** = verified (read, run or counted in this run). **[NV]** = not verified (Claude's judgment or inference). "not recorded" = no source gives it.

## 0. Short answer

| # | Output | File | Who produced it | Status |
|---|---|---|---|---|
| 1 | Offering task map | `outputs/01_offering_task_map.md` + `.csv` (728 rows) | **FSCR + Claude**. Claude chose offerings and functional areas from the SOW. The FSCR catalog supplied the tasks. FSCR code resolved skill paths. | [V] |
| 1b | Workspace initializer `--dry-run --no-create-runbook` | `work/initializer_dryrun.txt` | **FSCR**: **it now passes** (exit 0; 728/728 names matched). Run 11b stopped at "non-empty tasks array". | [V] |
| 2 | Wave plan (.xlsx) | `outputs/02_wave_plan.xlsx` | **Claude alone**. FSCR's `implementation-wave-planner` and all five `instance-strategy` skills are generic stubs with no rules. The cycle rules came from our practice (the run prompt). | [V] |
| 3 | Task dependencies | `outputs/03_task_dependencies.md` (26 rows) | **FSCR + Claude**. 20 rows come from FSCR pillar `ora_dependency_readiness.md` / `ora_input_validation.md` files and the HCM graph; 5 rows are Claude-only; 1 row is SOW + Claude. The FSCR resolver produced no sequence (no script; it needs FSM/BOSS). | [V] |
| 4 | Readiness checklist | `outputs/04_readiness_checklist.md` (5 gates, 41 checks) | **Claude alone**. `readiness-checklist-generator` is a stub. 4 checks cite FSCR task-level readiness files. | [V] |

Does the SOW's 12 weeks fit? **No.** [V, arithmetic] The practice cycles alone add up to 2 (CRP1) + 7 (fix/load/validate) + 2 (CRP2) + 7 + 2 (UAT) + 1 (go-live) = **21 weeks**, which is 9 weeks over the SOW before any design or configuration. With an assumed 4 weeks of design/configure the total is **25 weeks** (13 over). The 4-week figure is a Claude assumption [NV]. The SOW's 3,820 hours over 12 weeks is 318 h/week (≈8 FTE). Over 25 weeks it is 153 h/week (≈3.8 FTE). The formulas are on the `Arithmetic` sheet.

Oracle update calendar: **the repo holds none.** [V] FSCR's plan does **not** flag the risk of test cycles falling in update windows. There is no FSCR plan logic to flag it. [V]

## 1. Rules followed

| Rule | How it was kept | Status |
|---|---|---|
| Paper only: no pod, sign-in, Fusion calls or tokens | No network calls. The scripts run were local Python only: FSCR `task_to_skill_mapping.py` → `task_context.py`; FSCR `initialize_project_workspace.py --dry-run --no-create-runbook`; FSCR `validate_identified_task_mapping()`; Claude's builders in `work/scripts/`. | [V] |
| New folder with its own repo copy | `_fscr_run_12_project_planning/repo` copied from `fscr-main/fscr-main` (6,120 files in both). The original and earlier run folders were not modified. Run 11b outputs were **copied** into `inputs/`. | [V] |
| Portal code folder not used | Not touched | [V] |
| SOW | Your attached PDF has the same MD5 as the run 11b copy (`77241006…`). It is saved as `sow/SOW_attached.pdf`. Text is from `sow/SOW.txt`. Before you attached it I used the run 11b copy; since the two files are identical, nothing changed. | [V] |
| Hours | SOW role table = **3,820** h (140+640+80+560+320+280+280+560+560+400). DRIVE_REFERENCE says ~4,800; not used. | [V] |
| Blind step | All four outputs were finished and hashed **before** anything in `_fscr_run_10_drive_reference` was opened. **Frozen at 2026-11-05 10:24:53 PST** (`work/freeze_record.txt`, MD5 of every output). The first read of DRIVE_REFERENCE.md was at 10:24:59. | [V] |
| No invented dates/environments | Relative weeks only. The only environments are the two the SOW names ("development and production platforms", E.6). The missing ones are open questions W1–W8 in the workbook. | [V] |
| AGENTS.md | Read. The router entry point was reviewed. The initializer was run in dry-run mode only, so no `project/{id}` workspace was created and no token-usage log was written (the dry run writes nothing). | [V] |
| Persistent processes | None started. The only background job was the task-map build, and it has exited. LibreOffice recalc could not start (Windows `AF_UNIX` error), so nothing is left running. | [V] |

## 2. Files used (exact)

FSCR repo (`_fscr_run_12_project_planning/repo/…`):

| File | Used for | Result |
|---|---|---|
| `AGENTS.md` | Rules, workflow | Read [V] |
| `router/implementation-router/SKILL.md` | Entry point | Read; no planning content [V] |
| `shared/implementation-planning/implementation-wave-planner/SKILL.md` | Wave plan | **Stub**: generic inputs/outputs, no rules [V] |
| `shared/implementation-planning/readiness-checklist-generator/SKILL.md` | Checklist | **Stub** [V] |
| `shared/implementation-planning/guided-setup-roadmap/SKILL.md` | Roadmap | **Stub** [V] |
| `shared/implementation-planning/offering-task-map-builder/SKILL.md` + `scripts/task_to_skill_mapping.py` | Task map | Has a real sequence gate (text) and working skill-path code [V] |
| `shared/implementation-planning/task-dependency-resolver/SKILL.md` + `references/dependency-graph-enrichment.md` | Dependencies, sequence | Real method, **no script**; needs `core.fusion-api.fsm-rest-client` [V] |
| `shared/instance-strategy/{fusion-instance-strategy, pod-strategy-advisor, environment-refresh-guidance, migration-path-planner, release-update-readiness}/SKILL.md` | Environments, updates | **All 5 are stubs** [V] |
| `core/project-mgmt/project-workspace-initializer/SKILL.md`, `scripts/initialize_project_workspace.py`, `scripts/create_project_runbook.py` (read, not run) | Initializer | Dry run passed [V] |
| `core/runbook/scripts/task_context.py` | Skill path resolution (imported) | Ran [V] |
| `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json` | Offerings, FAs, tasks | 54 offerings / 609 FAs / 7,282 tasks [V] |
| `knowledge/setup-task-catalog/effective/setupTasksAll.json` | Name validation | [V] |
| `knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json` | Source layer check | [V] |
| `knowledge/dependency-graphs/hcm-dependency-graph.json` | Only graph in repo (HCM) | 86 nodes / 281 edges; location↔legal-entity cycle [V] |
| `knowledge/product-guidance/pillars/scm/*/reference.md` | Product guidance | One Oracle doc link each, no planning content [V] |
| `pillars/scm/manufacturing-and-supply-chain-materials-management/SKILL.md` | Offering skill | Routing only [V] |
| Dependency files: `.../cost-accounting/{cost-organizations, cost-organization-relationships, cost-elements, default-cost-profiles}/ora-resource/ora_dependency_readiness.md`; `.../facilities/manage-inventory-organizations/ora-resource/ora_input_validation.md`; `.../inventory-management/inventory-business-event-configurations/…/ora_dependency_readiness.md`; `.../manufacturing-master-data/{manufacturing-work-areas, manufacturing-work-centers, manufacturing-resources}/…/ora_dependency_readiness.md`; `.../maintenance-management/manage-maintenance-organization-relationships/…/ora_dependency_readiness.md`; `pillars/scm/procurement/procurement-foundation/manage-purchasing-line-types/…/ora_dependency_readiness.md`; `pillars/erp/financials/organization-structures/ora-resource/{ora_design_enforcement.md, ora_error_handling.md}`, `assign-business-unit-business-function.md`, `manage-business-unit.md` | Output 3 | [V] |
| `pillars/hcm/goal-management/.../oracle_hcm_goal_management_best_practices.md` §20.3 | Only "quarterly update" hit (HCM regression list) | [V] |

Run inputs: `sow/SOW.txt`, `sow/SOW.pdf`; `inputs/01_scope.md`, `02_enterprise_structure.md`, `03_integration_landscape.md` (copied from run 11b). After the freeze: `_fscr_run_10_drive_reference/DRIVE_REFERENCE.md`, `downloads/01_checklists_capture.txt`, `02_instance_plans_all_capture.txt`, `03_C1_instance_plan_capture.txt`, `04_C2_scm_project_schedule_capture.txt`, `07_C2_scm_sow_capture.txt`; `notes/*.txt` (grep only).

Claude scripts: `work/scripts/selection.json` (offering/FA choice with SOW clause), `build_task_map.py`, `render_task_map_md.py`, `build_wave_plan.py`.

## 3. Output details

### 3.1 Offering task map [V counts; NV selection]
- Offerings: **new**: `ORA_MANUFACTURING_AND_SUPPLY_C` (17 FAs, 346 tasks), `PO_PROCUREMENT` (11, 170), `PIM_PROD_MNG` (2, 50). **Incremental**: `PJF_PROJ_MNG` (1, 33), `XLE_FINANCIALS_JUR` (3, 129, with Expenses conditional), `ORA_GMS_GRANTS_MANAGEMENT` (0: changes TBD).
- 728 task rows, 514 unique task codes. 297 rows have an FSCR pillar skill and 431 route to manual tasks. 727 rows take the catalog sequence; 1 is a functional-area tail (`Configure Subinventories`).
- The `Resolver Sequence` column is numbered by **Claude** following the resolver's written method. It is not FSCR resolver output. Under the offering-task-map-builder's own gate, the mapping should not feed a Run Book plan without a persisted `setup_task_sequence`. The initializer script does not check this.
- FSCR's skill-path code took 11 min 4 s for 728 tasks, because it re-parses a 650 KB catalog and globs `pillars/**` for every task.
- SOW items with no setup task found: meters, maintenance programs, installed base (7.5–7.7) [NV].

### 3.2 Wave plan [V file; rules sourced as below]
Sheets: `Wave Plan (rules)` (25 weeks), `SOW 12 weeks (does not fit)`, `Arithmetic` (formulas), `Open questions`.

| Rule | Source | Status |
|---|---|---|
| CRP1 2 wk partial data, no security, no customizations | Our practice (run prompt). After the freeze: matches the Scoping Checklist "Planning" sheet | [V] |
| CRP2 2 wk full data, full security, customizations | Our practice | [V] |
| UAT 2 wk full + delta; go-live 1 wk | Our practice | [V] |
| ~7 weeks fix/load/validate between cycles | Our practice. Post-freeze: the checklist breaks it down as fix config 3, cleanse 3, configure env 1, validate 1, load 2, smoke 1, "total 7" | [V] |
| Design + configure 4 weeks before CRP1 | **Claude assumption** | [NV] |
| Environments DEV + PROD | SOW E.6 | [V] |
| Separate TEST pod, update weeks, dates | Not given: open questions W1–W3 | [V] |

The workbook formulas could not be recalculated with LibreOffice (Windows socket error). They were checked by reading them back: `=SUM(B2:B8)`=25, `=SUM(B3:B8)`=21, `=B10-B12`=13, `=B11-B12`=9, `=B15/B12`=318.3. Excel calculates them on open. [V for references; cached values not stored]

### 3.3 Dependencies: 26 rows (≥10). Examples: legal entity → cost org; location → inventory org (mandatory); location → BU (**optional** in FSCR); inventory org → work area → work center; persons → BU manager. [V]
### 3.4 Readiness checklist: gates 0 (start), 1 (CRP1), 2 (CRP2), 3 (UAT), 4 (go-live). [V]

## 4. Oracle update calendar

| Check | Result | Status |
|---|---|---|
| Search for quarterly update / cohort / update window / release calendar / CRP / UAT in `shared`, `knowledge`, `router`, `core`, `governance`, `project/_template` | **No hits.** The only "quarterly update" text is an HCM Goal Management regression list and HCM "quarterly release metadata" fields. There is no calendar, no cohort list and no update dates. | [V] |
| Does FSCR's plan flag cycles in update windows? | **No.** `release-update-readiness` is a stub and there is no wave-planning logic. | [V] |
| Our real practice (post-freeze) | Instance plans carry a 13-week cohort bar (24D, 25A–25D for Twelve), yellow update weeks, and the key "A = Feb/May/Aug/Nov; B = Mar/Jun/Sep/Dec; C = Apr/Jul/Oct/Jan; Non-Prod = 1st Friday, Prod = 3rd Friday". The PM checklist says "Open SRs to get the update schedule and create instance plan". | [V] (capture) |

## 5. Scoring against the answer key (read after the freeze)

### 5.1 Who produced what

| Output | Producer | Comment |
|---|---|---|
| Offering task map | FSCR + Claude | FSCR's strongest area: catalog and skill paths are real. Claude chose the scope. |
| Wave plan | Claude alone | FSCR contributes nothing |
| Task dependencies | FSCR + Claude | FSCR has object-level prerequisites inside task skills, but no SCM graph and no resolver output |
| Readiness checklist | Claude alone | FSCR stub |

### 5.2 What our real Twelve plans have that FSCR's output lacks [V from captures]
1. **Three pods**: Production, Test, Development (Dev 2), from `Twelve Instance Plan 2025.xlsx`. The SOW names only two, so I left TEST as an open question.
2. **Oracle cohort bar** (24D → 25D), Patch / Refresh / Data Extract / Cutover rows, and the A/B/C key with first-Friday and third-Friday rules.
3. **Real calendar dates** (start Feb 17, 2025) and dated re-plan versions (SOW Timeline, SCM SOW, SCM Current "as of May 14, 2025", CR to AUG with 3 scenarios).
4. Activities my plan does not have: kick-off and pre-implementation training, design workshops (wk 2–4, actual 2–9), **CRP0**, CRP prep and CRP fix weeks, **Mock 1 / Mock 2** loads, **Train-the-Trainer and end-user training**, Production data-load coordination, config migration, "Go-Live Ready", **HyperCare (4–8 weeks)**, F&A resource availability.
5. GoSaaS sizing method (Scoping Checklist): 1 workshop week per module plus 1 each for data migration, reports, security and sign-off; optional **CRP3** (mock, full + delta); "highly recommended to have 2 test environments"; "if only 1, … an extra 1 to 2 weeks in between test cycle"; quarter-end freeze.
6. Checklist items: get the update schedule via SR, request concurrent patching or a cohort, right-size environments, Oracle support identifier, admin plus backup access.

### 5.3 What FSCR's output has that the real plans lack [V]
1. Task-level scope: 728 catalog tasks mapped to offerings/FAs with SOW clauses and FSCR skill paths. The real schedule has no task list.
2. Object-level dependencies with file citations (LE → cost org, location → inventory org, work area → work center, etc.).
3. Explicit arithmetic and assumption cells (hours/week, FTE, gap to SOW).
4. Gate-by-gate readiness with sources, plus a V/NV marking on every line.
5. Practice rules applied literally: 7-week gaps. **The real Twelve plans did not use 7-week gaps.** The gaps there were 1–3 weeks (e.g. CRP1 fix wk16 → CRP2 wk17).

### 5.4 How the duration is derived

| Plan | Duration | How it was derived | Status |
|---|---|---|---|
| SOW | 12 weeks | Stated as an assumption (C.8). No derivation, no phase list. 3,820 h. | [V] |
| My rules plan | 25 weeks (21 without design) | Bottom-up sum of practice cycle blocks plus a 4-week design assumption. Fixed rules, no actuals. | [V] |
| Twelve "SOW Timeline" sheet | 16 weeks | Weekly bars squeezed to fit the SOW: design 3 wk, CRP1 wk5–6, CRP2 wk9–10, UAT wk13 (1 week), go-live wk16. Gaps of 2 weeks (prep), not 7. | [V] |
| Twelve "SCM Old" | 12 weeks | CRP2 1 wk, UAT 1 wk, gaps of 1 week | [V] |
| Twelve "CR to AUG" (change request) | Go-Live Ready wk23–28, hypercare to wk27–32 | **Re-plan from actuals**: design ran wk2–9, CRP0 was inserted, and 3 scenarios (with or without CRP2, UAT 2–3 wk) were costed for a CR | [V] |
| GoSaaS Scoping Checklist method | not computed for Twelve | Workshop weeks per module + cycle lengths + 7-week between-cycle work | [V method]; Twelve number not recorded |

Conclusion: my 25-week figure is close to the re-planned Twelve go-live (wk23–28), but **the derivation is different**. Mine is a rule sum before the project starts; theirs is a squeeze to the SOW followed by re-planning from actual progress. Neither the SOW nor FSCR derives duration from scope. Applying the Scoping Checklist literally to the 8 new modules (8 + 1 + 1 + 1 + 1 = 12 workshop-weeks if run one after another) would give more than 25 weeks. Whether Twelve's workshops ran in parallel is not recorded. [NV]

### 5.5 Answer-key notes
- DRIVE_REFERENCE lists the Twelve SOW at ~4,800 h; the SOW table says 3,820 h. **3,820 used.** [V]
- My readiness checklist overlaps the real checklists on environment access, update schedule, sign-offs, training and config migration. It lacks concurrent patching, right-sizing and the quarter-end freeze. The real "Go Live Readiness Review.docx" was not captured in run 10, so go-live gate content cannot be compared (not recorded).

## 6. Gaps found in FSCR (for the backlog)

| # | Gap | Status |
|---|---|---|
| G1 | `implementation-wave-planner`, `readiness-checklist-generator`, `guided-setup-roadmap` and all five `instance-strategy` skills are stubs | [V] |
| G2 | No Oracle update / cohort calendar, and no rule tying test cycles to update windows | [V] |
| G3 | `task-dependency-resolver` has no script and cannot run without FSM/BOSS, so no offline sequence is possible | [V] |
| G4 | No SCM/Procurement/Financials dependency graph; the HCM graph has a location↔legal-entity cycle | [V] |
| G5 | The initializer validates task names only. It does not check offering/FA context or `Resolver Sequence`, and does not enforce the map-builder's sequence gate. | [V] |
| G6 | Skill-path resolution is slow (11 min for 728 tasks; per-task catalog re-read and glob) | [V] |
| G7 | 431 of 728 mapped tasks (59%) have no FSCR task skill | [V] |

## 7. Run statistics

| Item | Value | Status |
|---|---|---|
| Start | 2026-11-05 10:08:26 PST (first command) | [V] |
| Outputs frozen | 10:24:53 PST | [V] |
| Report written | about 10:27 PST (system clock) | [V] |
| Elapsed (system clock) | about 19 min. The 11-minute task-map job ran in the background inside this window. | [V] |
| Tool calls | about 60 (counted from the transcript; approximate) | [NV] |
| Output tokens | **not recorded**: the app exposes no output-token counter to me. Context window used at the end: 280,545 tokens (session usage tool). | [V for context figure] |
| Processes left running | none (checked with `ps` at 10:27:04; no python/soffice). Files newer than the run start in `fscr-main/`, `_fscr_run_11b_project_intake/`, `_fscr_run_10_drive_reference/`: none. | [V] |
