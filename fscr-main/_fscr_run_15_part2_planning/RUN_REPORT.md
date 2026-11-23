# FSCR Run 15: Part 2, Project Planning (Twelve, Oracle Cloud SCM SOW dated Jan 24, 2025)

- **Run folder:** `E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_15_part2_planning`
- **Repo:** own copy at `fscr-main/`, copied from `…\fscr-main\fscr-main` at 19:42. After the run, `diff -rq -x __pycache__` against the original showed no differences. verified
- **Mode:** paper work only. No Oracle pod, sign-in, Fusion call or token. FSCR scripts were run read-only. The workspace initializer ran with `--dry-run --no-create-runbook` and wrote nothing. verified
- **Timing:** start 19:41:25, freeze 19:56:37, report 19:59–20:05 local (UTC+5). Total ≈ 24 min. verified, from shell clock
- **Note on the clock:** the shell printed the zone as "PST". Python reports Pakistan Standard Time (UTC+5). The times above are UTC+5.

## 0. Inputs and rule compliance

| Item | What was used | Status |
|---|---|---|
| SOW | The SOW was attached to the chat (`C:\Users\PC\Downloads\…SOW v4….pdf`). It was copied to `input/`, and its text was extracted with `pdftotext` to `work/sow_text.txt`. MD5 77241006ca0165557315ca946f4b6c56 is identical to the Run 14 input copy. | verified |
| Intake outputs | `01_SCOPE.md`, `02_ENTERPRISE_STRUCTURE.md` and `03_INTEGRATION_LANDSCAPE.md`, found at the top level of `_fscr_run_14_part2_intake`. There is no `outputs` subfolder. | verified |
| Team method | `_fscr_run_10_drive_reference/downloads/01_checklists_capture.txt` (all) and the TEMPLATES section (lines 1–9) of `02_instance_plans_all_capture.txt` | verified |
| **Rule deviation (exposure)** | Before the freeze, an early `grep` on the 02 file printed matching lines from its CUSTOMER PLANS section. That included line 25, the Twelve instance plan summary: rows Production/Test/Development (Dev 2), Patch, Refresh, Data Extract, Cutover; cohort bars 24D–25D; key A/B/C/LS. **I did not use it.** The environment rows had already been prescribed by the task. The cohort analysis uses only the A/B/C key given in the task. The LS key entry was not used, which is why it shows as missed in §2.2. | verified (the exposure happened; non-use is my statement and **not verifiable**) |
| Forbidden folders before the freeze | No other files in `_fscr_run_10`, `_fscr_run_11*`, `_fscr_run_12*` or `_fscr_run_13` were opened before 19:56:37. | verified (from my tool log) |
| Portal code folder | not used | verified |

## 1. Outputs and who produced them

| # | Output | File(s) | Produced by |
|---|---|---|---|
| 1 | Offering task map | `01_OFFERING_TASK_MAP.md`, `01_OFFERING_TASK_MAP_tasks.csv` (671 rows), `01_identified-task-mapping.json` (initializer format) | **FSCR + Claude** |
| 2 | Wave plan | `02_WAVE_PLAN.xlsx` (sheets: README, 12-week plan, Activities, 16-week alternative, Fit arithmetic, Update conflicts, Assumptions & Open Qs, Legend) | **Claude alone**. FSCR's wave planner and instance-strategy skills are empty placeholders. |
| 3 | Task dependencies | `03_TASK_DEPENDENCIES.md` (32 dependencies) | **FSCR + Claude** |
| 4 | Readiness checklist | `04_READINESS_CHECKLIST.md` (7 gates, 66 checks) | **Claude alone**. FSCR's readiness generator is an empty placeholder. 4 checks cite FSCR dependencies. |

All four outputs were finished; none is "not produced". verified

### What FSCR actually contributed (verified)

- **Effective catalog:** `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`, with 54 offerings, 609 FAs and 7,282 tasks. It supplied task membership and `displaySequence` for 25 expanded FA pairs, which gave 671 rows and 498 unique task codes.
- **Skill matcher:** FSCR's own `core/runbook/scripts/task_context._skill_path` assigned a skill to each task. 250 of 671 rows (37%) have a pillar skill or flat guidance; the rest route to the Manual Tasks skill. It took 10 min 38 s, because it scans 1,006 skill manifests per task.
- **Offering-task-map-builder:** used for its method only. It has no CLI; its helper needs a run-book plan. Its sequence gate expects a resolver-persisted, FSM-backed `setup_task_sequence`, which is impossible offline. I used the catalog order instead and labelled the deviation.
- **Task-dependency-resolver:** a method only, with no script. The only dependency graph is `knowledge/dependency-graphs/hcm-dependency-graph.json`, so it added nothing for SCM or ERP.
- **Pillar dependency files:** `ora_dependency_readiness.md` in 161 in-scope pillar skills; 136 have a "Required Dependency Order" section (`work/fscr_dependency_extract.txt`). 16 dependencies were taken from them (D1–D16).
- **Project workspace initializer dry-run:** exit 0, "Would create project workspace: project\twelve-scm-planning-run15", no folder created. Its mapping validation (`validate_identified_task_mapping`), called directly, gave matched 671, unmatched 0, ambiguous 0. `create_project_runbook.py` and `core.runbook` were not run: they need a real workspace and Fusion, respectively.

### Freeze

`work/freeze_record.txt`, frozen 2026-11-05 19:56:37 UTC+5. After the freeze the files were set read-only and not edited. verified

| MD5 | File |
|---|---|
| 3e1f1e36b5cfa5928ffe946ad8e7683d | 01_OFFERING_TASK_MAP.md |
| aeeaae6447eecf81abe67ccfd4b83e2e | 01_OFFERING_TASK_MAP_tasks.csv |
| 07ff52c10758c3f0ca55d37aa3e35b87 | 01_identified-task-mapping.json |
| e281323fb4ffb3c30df312186598308d | 02_WAVE_PLAN.xlsx |
| 7e3c3714cf23cb806ae3650eeaaac0ca | 03_TASK_DEPENDENCIES.md |
| c981c87e1662222a46b5667f498d5cae | 04_READINESS_CHECKLIST.md |

### Key results (before the comparison)

**12-week fit.**
- The checklist-faithful model needs 33 weeks: 3 + 2 + 2 + 7 + 2 + 7 + 2 + 7 + 1, which is 21 weeks too long.
- The test cycles alone take 7 of the 12 weeks.
- 12 weeks fits only by cutting each between-cycle gap to 1 week (the checklist says 7): design 3, CRP1 2, gap 1, CRP2 2, gap 1, UAT 2, go-live 1 = 12.
- SCM Architect hours (640 ÷ 12 = 53 h/week) also point to about 16 weeks at 40 h/week.
- A 16-week alternative is included.
- verified arithmetic; the plan itself is SUGGESTED.

**Oracle update conflicts in the 12-week plan.** These are verified date arithmetic. The cohort itself is unknown.

| Cohort | Conflicts | Notes |
|---|---|---|
| A | 4 | Non-prod update 02-May falls in UAT. Prod update 16-May is the week after go-live. |
| B | 3 | Non-prod update 07-Mar is next to CRP1. Lowest risk of the three. |
| C | 5 | Non-prod update 04-Apr falls in CRP2. Prod update 18-Apr falls in the Prod config migration. |

Recommended shifts for each cohort are in the workbook.

## 2. Comparison with the manual baseline (after the freeze)

**Sources read after the freeze:**
- `_fscr_run_13_twelve_manual_baseline/TWELVE_MANUAL_BASELINE.md`
- From its captures: `Configuration_Master_Checklist.txt`, `Twelve_Instance_Plan_2025.xlsx.txt`, `_condensed_extracts_of_files_read_inline.md`
- `_fscr_run_10…/downloads/02` (Twelve row) and `04_C2_scm_project_schedule_capture.txt`
- Other capture files were listed but not read; they are not needed for the four outputs.

**Labels:**
- **covered**, **partly** and **missed** describe how my output handles each manual item.
- **contradicted** means my output says the opposite.
- **not findable from the SOW** means the item came from later re-planning or change requests (CR #01 May 2025, CR #02 May/Aug 2025). These are excluded from the misses.
- Each count is verified by script or hand count as noted. Judgements of coverage are mine and **not verified** by a second person.

### 2.1 Offering task map

Manual = **Configuration Master Checklist** (Aug 18, 2025; 7 module tabs). The baseline states 381 tasks; my parser found **386 rows** (difference not resolved; probably header rows with trailing cells). Matching was by normalized task name: punctuation, spacing and a trailing " Task" ignored (`work/compare_task_map.py`; per-row result in `work/compare_task_map.csv`).

| Result | Rows | What |
|---|---|---|
| **Covered** | **264** | 258 exact or spelling-variant name matches, plus 6 Manufacturing/Maintenance tasks renamed in the catalog (e.g. "Manage Work Areas" = "Manufacturing Work Areas"). |
| **Partly** | **49** | 42 Receivables / Cash Management tasks in FAs I listed as TBD but did not expand; 7 "Define …" task-list headers (e.g. Define Cost Accounting Policies) whose child tasks are in my map. |
| **Missed** | **26** | 20 Financials foundation tasks: legal jurisdictions, authorities, addresses and registrations; LE configurator; geography loader; currencies and rates; reference data sets; COA configurations; banking configurations. I selected Organization Structures but not Legal Structures, Financial Reporting Structures, Enterprise Profile or Banking. Also missed: Procurement "Manage Locations", "Manage Inventory Organization", "Manage Inventory Organization Locations", "Manage Functional Area Catalogs", "Manage Supplier News Content", and Inventory "Manage Inventory Document Output Preferences". My own open question flagged the Inventory Organizations FA. |
| **Contradicted** | **0** | – |
| **Not findable from the SOW** | **43** | Oracle Tax tasks. Tax was added by CR #01; the SOW has no tax. |
| Not a task | 4 | PIM tab header text ("Offering", "Product Management"). |

Sum: 264 + 49 + 26 + 0 + 43 + 4 = 386. Per tab:

| Tab | Covered (exact) | Partly | Missed (raw, before reclassification) |
|---|---|---|---|
| Financials | 146 | 42 | 64 |
| Procurement | 46 | 0 | 5 |
| Inventory | 28 | 0 | 1 |
| Costing | 14 | 0 | 4 |
| Manufacturing | 4 | 0 | 7 |
| Maintenance | 20 | 0 | 1 |
| PIM | 0 | 0 | 4 |

**Mine but not in the manual list (not findable / mine only):**
- 316 unique task names (349 rows).
- Largest groups: Expenses 40 (not findable: CR #01 removed Expenses), Inventory Management 37, General Ledger 35, Items 34, Project Costing Base 31, Suppliers 25, Facilities 20, Cost Accounting 19, Manufacturing Master Data 18.
- My map lists every catalog task in each FA. The manual list is a curated subset. Its PIM tab has only 3 rows, against my 68 Product Management rows.
- My map also has things the manual list lacks: scope class per FA, SOW reference, FSCR skill path, the catalog mandatory flag, and FSM export/import support.

### 2.2 Wave plan

Manual sources:
- *Twelve Instance Plan 2025.xlsx*: the text only. Its cell shading, which carries the environment-by-week blocks and the marked update weeks, was **not readable** (baseline NV).
- *Twelve SCM Project Schedule.xlsx*: 7 versions. Its "SOW Timeline" sheet (16 weeks, Feb-17 → Jun-02) is the closest to the SOW; later sheets are re-plans.

| # | Manual item | Mine | Result |
|---|---|---|---|
| 1 | Environments Production, Test, Development (Dev 2) | Production, Test (SUGGESTED), Development (SUGGESTED) | covered |
| 2 | Patch row | Oracle update rows for cohorts A, B and C | covered |
| 3 | Refresh row | Refresh (SUGGESTED) row, P2T in W5 | covered |
| 4 | Data Extract row | data load blocks; no extract row (checklist: extract 0 weeks) | partly |
| 5 | Cutover row | Go-Live / cutover week block; no separate row | partly |
| 6 | Weekly columns 30-Dec-24 → 24-Nov-25 (48) | 17-Feb → 28-Jul-25 (24) | partly |
| 7 | Release bars 24D / 25A / 25B / 25C / 25D | release labels on each cohort's update weeks (24D … 25C) | partly |
| 8 | Key: A/B/C months; non-prod 1st Friday, prod 3rd Friday | same (given) | covered |
| 9 | Key: **LS = A (Dev) + B (Test & Prod)** | not used | missed |
| 10 | Kick-off / Pre-Implementation Training, week 1 | kickoff inside the W1 design block; no pre-implementation training | partly |
| 11 | Design weeks 2–4 (3 weeks) | design 3 weeks (W1–W3, including kickoff) | covered |
| 12 | As-Is Cloud Finance knowledge capture, weeks 2–4 | – | missed |
| 13 | CRP1 2 weeks (weeks 5–6) | CRP1 2 weeks (W4–W5; W6–W7 in the 16-week alternative) | covered |
| 14 | CRP2 prep 2 weeks | 1-week gap (12-week plan); 2 weeks (16-week alternative) | partly |
| 15 | CRP2 2 weeks (weeks 9–10) | CRP2 2 weeks | covered |
| 16 | UAT prep 2 weeks | as row 14 | partly |
| 17 | **UAT 1 week** (week 13) | UAT 2 weeks (given rule) | contradicted |
| 18 | Train-the-Trainer weeks 13–14 | TTT during UAT (WP-16, assumption only, not drawn) | partly |
| 19 | End-user training weeks 13–15 | readiness check G5.10 only; not drawn | partly |
| 20 | Data migrations weeks 14–15, just before go-live | Prod load + delta W11–W12, just before go-live | covered |
| 21 | Go-live week 16 (16-week SOW timeline) | main plan W12; the **16-week alternative has go-live in W16** | partly |
| 22 | Mock 1 / Mock 2 ("SCM SOW" sheet) | no mock/CRP3 (WP-7) | contradicted |
| 23 | "Ready to Use" milestone | in the readiness gate (SOW C.2.1), not in the plan | partly |
| 24 | "SCM Old" 12-week plan fits 12 weeks with 1-week CRP2 and UAT | I fit 12 weeks by keeping 2-week cycles and cutting the gaps | contradicted (different compression) |
| 25 | Fix weeks after each cycle (CRP0 / CRP1 / UAT Fix) | Fix config blocks | covered |
| 26 | Config migration + production data load coordination | Twelve migrates config to Prod W9–W11; Prod load W11–W12 | covered |
| 27 | "F&A resources available" in 4-week blocks | – | missed |
| 28 | CRP0 added; CRP1 May 19–30; TTT Aug 4–8; go-live Sep 2, 2025 | – | not findable from the SOW (re-plan, CRs) |
| 29 | Hypercare 8 weeks (CR to AUG) | Hypercare 2 weeks (SUGGESTED) | not findable from the SOW (CR #02) |

**Counts:** covered 10, partly 11, missed 3, contradicted 3, not findable 2 (29 items). Hand count, verified against the table.

**Environments:** both use 3 (Prod, Test, Dev).
- Real CRP1 ran in **DEV2** (CRP Approach), which matches my "CRP1 in Dev".
- Where real CRP2 and UAT ran: not recorded.

**Cycle order:**
- Manual SOW timeline: CRP1 → CRP2 → UAT → go-live. Mine is the same.
- Real project: CRP0 → CRP1 → (CRP2 dropped in one variant) → UAT/TTT → go-live (not findable).

**Cycle length:**
- Agreement: CRP1 2 weeks and CRP2 2 weeks in both.
- Difference: UAT is 1 week in the manual plan and 2 in mine. The gaps are 2 weeks in the manual plan and 1 in mine (12-week plan) or 2 in mine (16-week plan).
- The manual "SOW Timeline" is **16 weeks**. That matches my 16-week alternative in length and go-live week, not my 12-week main plan.

**Oracle update weeks:**
- The weeks marked on the real instance plan are **not recorded**: the shading is unreadable.
- Readable text: release bars start in the weeks of 30-Dec (24D), 27-Jan (25A), 28-Apr (25B), 28-Jul (25C) and 27-Oct (25D), plus the A/B/C/LS key.
- Bars starting in the weeks just before Feb, May, Aug and Nov are consistent with **cohort A**. Not verified: this may be template layout, not Twelve's cohort.
- The key also defines LS (Dev on A, Test and Prod on B), which I did not model.
- Best-matching cohort: **A (not verified)**. My cohort-A weeks:

| Date | Plan week | Update |
|---|---|---|
| 21-Feb-2025 | W1 | prod 25A |
| 02-May-2025 | W11 | non-prod 25B |
| 16-May-2025 | W13 | prod 25B |
| 01-Aug-2025 | W24 | non-prod 25C |
| 15-Aug-2025 | W26 | prod 25C |

- Agreement with the real marked weeks: **not recorded**.
- Against the real dates (go-live Sep 2, 2025), cohort A's 25C prod update (15-Aug) falls during the real cutover preparation (Aug 19–29). Not findable from the SOW; noted only.

**Mine only:**
- per-cohort conflict list with recommended shifts
- 12-week fit arithmetic and hours check
- calendar notes: the start date is Presidents' Day; April month-end close falls in the go-live week
- the P2T refresh before the Test build
- which environment each cycle runs in
- timing of Twelve's own Prod migration (SOW C.10)

### 2.3 Task dependencies

Manual sources:
- Twelve Project Plan: 5 predecessor links.
- Configuration Master Checklist "Predecessor/Owner" column: 45 rows giving the owning module.
- Implied orders: phases, CRP1 entry, Maintenance pre-configurations, cutover sequence.

| # | Manual item | Mine | Result |
|---|---|---|---|
| M1 | Kickoff → team spreadsheet → onboarding → SharePoint / Oracle access | access in readiness G0.6; no chain in dependencies | partly |
| M2 | Inventory organization (Inventory) before its use in Procurement | D4, D8; build wave B1 | covered |
| M3 | Plant parameters (Manufacturing) before Maintenance | D11 (maintenance-enabled org), D8; plant parameters not named | partly |
| M4 | Inventory org data access (Financials/security) before use | D10 (organization access before resources) | covered |
| M5 | Costing tasks owned by Cost Management (cost org → books → profiles) | D1–D6, D16 | covered |
| M6 | Financials "Prerequisite vs Configuration" colour key | not readable (NV) | not compared |
| M7 | Phase order PIT → Design → Build → CRP → Deployment | D19, wave plan | covered |
| M8 | CRP1 entry: Best Starts → configs in DEV2 → smoke test → scripts → RAID → user access | D19 + G2 gate | covered |
| M9 | Maintenance pre-configurations: GL, ES, Inventory, Suppliers, Plant Parameters | D11, D17, D18; suppliers not linked to maintenance | partly |
| M10 | Cutover: prep → integration → applications → people → go-live | D29 (UAT → Prod config → load → go-live); no people step | partly |
| M11 | Rippling HR integration cut over before applications | – | not findable (CR #01) |
| M12 | AirPlantOne inventory and cost orgs re-entered into the AirPlantOne BU before CRP1 | – | not findable (CR #02) |

**Counts:** covered 5, partly 4, missed 0, contradicted 0, not findable 2, not compared 1 (12 items). verified hand count.

**Mine only:** 32 dependencies, against the manual plan's 5 explicit predecessors. They include:
- 16 setup-object dependencies from FSCR files (LE → cost org → cost books/ledger; BU functions; work area → work center; …)
- project dependencies: Coupa values, approval basis, supplier FDD, Expenses decision, Test environment, COA accounts, Oracle update SR, month-end close

### 2.4 Readiness checklist

Manual sources:
- Twelve Cutover Plan: 20 named items, out of the 24 the baseline counts.
- Cutover Strategy: Go criteria, No-Go triggers, Business and Application checklists.
- CRP1 entry criteria from the CRP Approach.
- There is no manual pre-implementation checklist.

| # | Manual item | Mine | Result |
|---|---|---|---|
| C1 | Design configuration sign-off (PROD Best Starts) | G1.1, G5.3 | covered |
| C2 | Define processes | G1.1 process flows | partly |
| C3 | Define policies & procedures | – | missed |
| C4 | Go/No-Go decision | G5 gate | covered |
| C5 | Cutover communication email | – | missed |
| C6 | PROD provisioning & admin access | G0.6, G5.5 | covered |
| C7 | Production instance readiness check | G5.3 | partly |
| C8 | Freeze configs in DEV2 | – | missed |
| C9 | Enable modules in PROD | G5.3 / D13 opt-in | partly |
| C10 | HR configurations in PROD | – | not findable (CR #01) |
| C11 | HRIS/OIC integration to PROD | – | not findable |
| C12 | Integration validation | – | not findable |
| C13 | PROD configuration of Financials, Procurement, Projects, SCM | G4.8, G5.3 | covered |
| C14 | Security configuration in PROD | G5.5 | covered |
| C15 | Cross-module transaction test in PROD (before go-live) | G6.2 (after go-live) | partly |
| C16 | End-user role assignment confirmation | G5.5 | covered |
| C17 | Responsibility & org structure verification | – | missed |
| C18 | End-user training completion | G5.10 | covered |
| C19 | Freeze Coupa | G5.9 (Coupa transition decision) | partly |
| C20 | Go-live Sep-2 | go-live gate; date not findable | not findable |
| S1 | Go: no open high defects | G4.1 / G5.1 | partly |
| S2 | Go: 100% UAT success for key processes | G5.1 | partly |
| S3 | Go: critical configs successful in PROD | G5.3 | covered |
| S4 | Go: training material repository built | G4.7 | covered |
| S5 | No-Go: high-severity UAT issues open | G5.1 | partly |
| S6 | No-Go: Rippling integration failure | – | not findable |
| S7 | No-Go: Finance/SCM reconciliation gaps | G3.9, G6.4 | partly |
| S8 | Business readiness: processes, infrastructure, data, people | spread over G5 | partly |
| S9 | Application checklist per module (UAT / EUT material / PROD config) | not per module | partly |
| S10 | Contingency: stay on Coupa if No-Go | – | missed |
| E1 | CRP1 entry: business scenarios | G1.1, G2.4 | covered |
| E2 | CRP1 entry: roles and responsibilities | G2.4 (attendees) | partly |
| E3 | CRP1 entry: configurations loaded in DEV2 | G2.1 | covered |
| E4 | CRP1 entry: master data | G2.3 | covered |
| E5 | CRP1 entry: seed data | G2.3 | partly |
| E6 | CRP1 entry: **RICE migrated and validated** | G2.6: no customizations in CRP1 (given rule) | contradicted |
| E7 | CRP1 entry: smoke tested | G2.8 | covered |
| E8 | CRP1 entry: scripts reviewed, RAID log | G2.4, G2.5; no RAID | partly |
| E9 | CRP1 entry: user access | G2.6 | partly |
| E10 | CRP1 entry: AirPlant financial modules in Best Starts; orgs re-entered into the AirPlantOne BU | – | not findable (CR #02) |

**Counts:** covered 13, partly 15, missed 5, contradicted 1, not findable 6 (40 items). verified hand count.

**Mine only:**
- start gate G0 (no manual pre-implementation checklist exists; the baseline found none)
- design gate G1
- CRP2 and UAT entry gates G3 and G4
- Oracle update checks per cycle
- month-end-close check
- hypercare exit gate G6

### 2.5 Summary of counts

| Output | Covered | Partly | Missed | Contradicted | Not findable from SOW | Other |
|---|---|---|---|---|---|---|
| 1 Offering task map (386 manual rows) | 264 | 49 | 26 | 0 | 43 | 4 not tasks |
| 2 Wave plan (29 items) | 10 | 11 | 3 | 3 | 2 | – |
| 3 Task dependencies (12 items) | 5 | 4 | 0 | 0 | 2 | 1 not compared |
| 4 Readiness checklist (40 items) | 13 | 15 | 5 | 1 | 6 | – |

## 3. Findings (each marked)

1. **FSCR helps most with the task map.** 68% of the manual checklist rows (264 of 386) match FSCR catalog tasks in my map. Most misses come from FA selection: Financials foundation FAs not chosen. They do not come from catalog gaps. verified (script)
2. **The FSCR catalog over-lists.** 316 task names in my map are not in the team's curated list. The team picks a subset per FA; FSCR has no way to mark "typical for this offering". verified count; interpretation not verified
3. **FSCR's planning skills are empty.** The wave planner, readiness generator and instance-strategy skills contributed nothing. The dependency resolver has no script and no SCM/ERP graph. The useful dependency content sits in the per-task pillar files. verified
4. **The team's own SOW-era schedule was 16 weeks, not 12.** That matches my fit arithmetic and my 16-week alternative. verified (capture 04)
5. **The given cycle rules differ from the team's SOW-era schedule.** The rules say UAT is 2 weeks, while the team's schedule had 1 week. The rules say no customizations in CRP1, while the team's CRP1 entry required RICE migrated. verified
6. **Twelve's Oracle cohort is not determinable from the text captures.** The instance plan's shading is unreadable. A person must confirm it against Oracle's schedule. verified (baseline NV)
7. **Data-quality notes on the comparison:** the parsed manual task count is 386 against the 381 the baseline states, and the 20-of-24 cutover items were taken as named. not verified

## 4. Run statistics

- **Elapsed:** about 24 minutes (19:41:25 → about 20:05 local). verified, shell clock
- **Tool calls:** about 80 (counted from my own log: 75 by 19:59, about 5 for the report and wrap-up). not verified
- **Output tokens:** **not recorded.** I have no token counter. Rough estimate by chars/4: the files I authored (scripts plus the 3 markdown outputs, 78,002 chars) come to about 19.5k tokens. With this report and my messages, the total is about 30k. not verified
- **Processes:**
  - Started: one Python build job (finished, exit 0), one background wait and one monitor (both ended).
  - No servers were started.
  - At the end, no Python process was running. The only `node.exe` (PID 9608) was not started by this run and was left running.
  - verified via `tasklist`
- **Repo copy changes:** `__pycache__` folders under `fscr-main/core/runbook/scripts/` and the initializer `scripts/` (created by importing FSCR modules). The original repo was untouched. verified
