# RUN_REPORT — run 11b: FSCR project intake from the Twelve SOW (paper only)

Run folder: `E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_11b_project_intake`
Date: 2026-11-05. Start 09:57:29, outputs frozen 10:03:55 (before the blind step), report written about 10:05 local time (UTC+5) **[V, shell clock]**.
Input: `sow/SOW.pdf`, a copy of `50513 - Twelve - Oracle Cloud SCM Implementation SOW v4_Twelve-signed_GS signed.pdf`. Text extracted with pdftotext to `sow/SOW.txt` (313 lines) **[V]**.

Tags: **[V]** = verified. **[NV]** = not verified. "not recorded" = no source states it.

## 0. Rules compliance

| Rule | Result |
|---|---|
| Paper only: no pod, no sign-in, no Fusion calls, no tokens | Kept. No network calls. The only script run was the FSCR initializer with `--dry-run --no-create-runbook`; it rejected its input before writing anything. **[V]** |
| Own copy of the repo; original never modified | `repo/` copied from `fscr-main\fscr-main`. `diff -rq` showed the copy identical before work (6,120 files). After the run, the original still has 6,120 files, nothing newer than the run start, and its `project/` folder is unchanged. **[V]** |
| Earlier run folders not modified | `_fscr_run_11_project_intake` was not opened. `_fscr_run_10_drive_reference` was only read, and only in the blind step. **[V]** |
| Portal code folder not used | Not touched. **[V]** |
| Blind step | Outputs were frozen at 10:03:55 (`work/blind_step_timestamp.txt`). `_fscr_run_10_drive_reference` was first listed after that. The outputs were not edited after the blind step. **[V]** |
| No invented integrations | 0 integrations recorded. **[V]** |
| Hours | Uses the SOW's **3,820 h** (role-table sum, rechecked). DRIVE_REFERENCE.md §4 and `07_C2_scm_sow_capture.txt` both say "4,800 hours", which does not match the SOW. **[V]** |

## 1. Deliverables

| File | Content |
|---|---|
| `outputs/01_scope.md` | Scope, RICE, configurations, exclusions, assumptions, FSCR offering resolution, 15 open questions |
| `outputs/02_enterprise_structure.md` | Enterprise structure layer by layer, FSCR BU design principles, design-evidence grid, 12 open questions |
| `outputs/03_integration_landscape.md` | 0 integrations; systems named in the SOW (context only); 6 open questions |
| `work/classifier_offering_resolution.json` | Machine output of the classifier rules applied to 25 SOW module terms |
| `repo/project/twelve-scm-project-intake-20261105/` | FSCR workspace: `state/project-state.json`, `artifacts/artifact-index.json`, copies of the three outputs under `artifacts/shared/project-intake/...`, classifier diagnostics, `artifacts/shared/token-usage/current/token-usage-log.md` |

## 2. FSCR route followed and skills used

The route was AGENTS.md → `router/implementation-router/SKILL.md` → `router/project-objective-classifier/SKILL.md` → project workflow (`project/_template`, `core.project-mgmt.project-workspace-initializer`) → shared intake skills → `router.next-action-planner` (read only).

| # | Skill / template (path in repo) | What it gave | Substance |
|---|---|---|---|
| 1 | `AGENTS.md` | Entry rule, project-workspace rule, token-log rule | Real rules **[V]** |
| 2 | `router/implementation-router/SKILL.md` | Routing to classifier and planner; Run Book gate | Short; no intake questions **[V]** |
| 3 | `router/project-objective-classifier/SKILL.md` | Exact-match offering resolution rules; classification dimensions (pillar, offering, functional area, scope, geography, phase) | **Real logic**, applied in section 9 of Output 1 **[V]** |
| 4 | `router/next-action-planner/SKILL.md` | Outputs list only | Stub **[V]** |
| 5 | `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json` + `pillars-offerings-mapping.json` | 54 offerings with functional areas | **Real data** **[V]** |
| 6 | `project/_template/` (state + artifact-index templates, token-usage README) | Workspace skeleton | Real skeleton **[V]** |
| 7 | `core/project-mgmt/project-workspace-initializer/SKILL.md` + `scripts/initialize_project_workspace.py` | Required initializer | Blocked (see stop R3) **[V]** |
| 8 | `shared/project-intake/implementation-scope-intake/SKILL.md` | Headings: recommendations, work_products, review_points | **Stub** (2.7 KB, no questions) **[V]** |
| 9 | `shared/project-intake/scope-definition/SKILL.md` | Headings: confirmed_scope, assumptions, exclusions; persistence path | Stub plus a persistence location **[V]** |
| 10 | `shared/project-intake/enterprise-structure-intake/SKILL.md` | Generic headings | **Stub** **[V]** |
| 11 | `shared/project-intake/integration-landscape-intake/SKILL.md` | Generic headings | **Stub** **[V]** |
| 12 | `shared/integrations/integration-strategy-advisor/SKILL.md` | Generic headings | **Stub** **[V]** |
| 13 | `pillars/erp/financials/organization-structures/SKILL.md` ("Business Unit Design Principles", "Required Design Evidence") | BU design rules and per-BU evidence columns | **Real content**, used in Output 2 **[V]** |
| 14 | `pillars/erp/financials/organization-structures/ora-resource/ora_design_advisory.md` (and `ora_input_intake.md`, read only) | BU, ledger and service-provider terminology; task-level field intake | Real, but task-level (configuration), so used only for terminology **[V]** |
| 15 | `knowledge/product-guidance/pillars/scm/*/reference.md` | Oracle implementation-guide links only | Thin; nothing used in the outputs **[V]** |

Searched but **not used**, because they are generic stubs of about 2.1–3.0 KB with no content: `shared/project-intake/business-requirements-intake`, `country-localization-intake`; `shared/integrations/*` (api-led, event-driven, legacy, oic-design-advisor); `shared/instance-strategy/*` (no environment-count intake); `shared/implementation-planning/{implementation-wave-planner, readiness-checklist-generator, guided-setup-roadmap}`; `shared/reporting/reporting-strategy-advisor`; `shared/data-conversion/conversion-strategy-advisor`; `shared/best-practices/*`. `pillars/erp/financials/legal-structures` and `financial-reporting-structures` exist but are setup-task skills, not intake. **[V by file size and content check]**

## 3. Every place the FSCR route stopped to ask a question

None of these questions were put to you, as instructed. Each is recorded here and as an open question in the outputs.

| # | Where | What FSCR requires | What happened in this run |
|---|---|---|---|
| R1 | AGENTS.md "Project and Change Discipline" | No project exists, so create one from `project/_template`, **inform the user and offer to rename** it | Created `twelve-scm-project-intake-20261105` (named after the objective). The rename offer was not asked. **[V]** |
| R2 | Workspace initializer: automatic Run Book creation | By default, new-project initialization goes on to `core.runbook` and **creates an Oracle Run Book** (a Fusion call) unless `--no-create-runbook` is given | `--no-create-runbook` was used. No Fusion call. **[V]** |
| R3 | Workspace initializer: `--identified-task-mapping` | A **non-empty setup-task mapping** is mandatory. The dry run failed with: `Identified task mapping must contain a non-empty tasks array.` | **Hard stop.** A SOW gives no setup tasks, and building that mapping is configuration-level work outside scope. The workspace was copied from `_template` and populated by hand. Per the initializer's own gate, it is **not a formally initialized project**. **[V]** |
| R4 | Initializer task mapping | "If more than one offering remains plausible, ask the user" for each task | Not reached (no task mapping). **[V]** |
| R5 | Classifier offering resolution, step 5 | No exact match, so set offering_scope to pending and "**ask for an offering short code** or sufficient business context" | Triggered for 13 SOW terms (PIM, Inventory & Cost, Self-Service Procurement, Purchasing, Manufacturing, Maintenance, AR, Project Management, AP, Project Cost Mgmt, Asset Mgmt, SLA, Security). **[V]** |
| R6 | Classifier: multiple candidates | Same stop for terms that match functional areas in several offerings | Triggered for Supplier Portal, General Ledger, Cash Management, Payables, Sustainability. **[V]** |
| R7 | `scope-definition` (`execution_mode: assisted`) | The confirmed scope needs **human confirmation** | Scope left as DRAFT, not confirmed. **[V]** |
| R8 | `router.next-action-planner` | Produces `human_review_points` | No review points defined beyond the stub. Recorded R5–R7 as the review points. **[V]** |
| R9 | Implementation router Run Book gate | Blocks any Fusion mutation until `runbook_control.status = active` | Not applicable (no mutation). `runbook_control` absent. **[V]** |

The intake skills themselves never stop to ask anything: they contain no questions. **[V]**

## 4. Score: who produced each output

| Output | Producer | Why |
|---|---|---|
| 1. Scope | **FSCR + Claude** | FSCR gave the classifier rules, the catalog (offering codes, pending and ambiguous diagnostics) and the scope-definition headings. All scope content (modules, RICE, exclusions, assumptions, costs, open questions) was extracted by Claude. **[V]** |
| 2. Enterprise structure | **FSCR + Claude** | The intake skill is a stub. The ERP Organization Structures skill gave real BU design principles and the per-BU evidence columns. The layer table (LE, ledger, inventory org, cost org, item master), its values and the open questions came from Claude. FSCR has nothing for SCM inventory or cost organization intake. **[V]** |
| 3. Integration landscape | **Claude alone** | `integration-landscape-intake` and `integration-strategy-advisor` are stubs with generic headings only. **[V]** |

## 5. Scoping Checklist versus FSCR intake

Source: `downloads/01_checklists_capture.txt` (Scoping Checklist, with the Methodology and PM Check List as context).
"FSCR covers" means an FSCR skill, input or catalog actually captures the item. "Nominal" means only a stub skill with the right name exists.

### 5.1 Checklist questions FSCR covers

| Checklist item | FSCR mechanism | Level |
|---|---|---|
| Business objectives for the project | `implementation_objective` input (router, classifier, initializer) | Covered **[V]** |
| Modules being implemented | Classifier offering and functional-area scope plus the effective catalog | Covered, strongest area **[V]** |
| Industry | Initializer `--industry` | Field only **[V]** |
| Country / geography (and partly Number of Locations) | Classifier "geography"; initializer `--country`; country-localization-intake (stub) | Partial; locations not covered **[V]** |
| Delivery phase | Classifier phase; initializer `--implementation-phase` (discovery…operate) | Partial: phase label only, no test-cycle plan **[V]** |
| Integration (endpoints, middleware, direction) | integration-landscape-intake, integration-strategy-advisor, oic-design-advisor | **Nominal (stubs)** **[V]** |
| Data migration (sources, objects, volumes) | data-conversion skills (stubs) | Nominal **[V]** |
| Security | security-role-guidance (3.9 KB), security-console skills (task-level) | Nominal for intake **[V]** |
| Number of environments | instance-strategy skills (stubs); topology-manager needs live Fusion | Nominal **[V]** |

### 5.2 Checklist questions FSCR misses

Customer Information: annual revenue, legacy system, ERP, employees, ITAR or citizenship restrictions, FDA or other regulations, systems or functions being replaced. Scope overview: number of users, approvers or changers, view-only users, number of divisions. All module-specific PD, PIM, Quality, IM and EG&C questions (the checklist is PLM-centric). GoSaaS tools (Power Tools, Portal, Archiver). Customization and custom-report limits ("typically 5"). Integration object types and item classes. Data history (latest revision vs full history), attachment counts, when source files arrive. Post go-live: in-house IT, extended hypercare. Planning: number of test environments ("2 recommended"), workshop durations by type, timeline extenders (regions, decision owner, time zone), test cycles CRP1/CRP2/CRP3/UAT with data scope, between-cycle activities (about 7 weeks), quarter-end freeze. Project Management: GoSaaS vs client split for plan, instance plan, status reports and budget. Methodology: Oracle upgrade-plan inquiry. PM checklist: "open SRs to get update schedule and create instance plan". **[V: none of these appear in any FSCR intake, router or project-template file read]**

### 5.3 What FSCR covers that the checklist does not

1. Exact Oracle offering and functional-area codes from the catalog, with fail-closed handling of ambiguous matches (the checklist has free text only). **[V]**
2. **Enterprise structure design:** BU principles and per-BU design evidence (ledger and legal entity, business functions, service-provider relationships, reference data sets, security scope). The checklist only asks for "number of divisions" and "number of locations". **[V]**
3. SCM and ERP offerings in general. The checklist has no Procurement, Inventory, Cost, Manufacturing or Maintenance questions. **[V]**
4. Setup-task mapping, dependency graphs and task sequencing (initializer, task-dependency-resolver). This is beyond intake. **[V]**
5. Durable project state, artifact index, versioning, token-usage logging and approval gates. **[V]**

## 6. Comparison with what the real Twelve project used

Sources: `07_C2_scm_sow_capture.txt`, `04_C2_scm_project_schedule_capture.txt`, DRIVE_REFERENCE.md §4 and §6.

| Topic | My outputs (SOW only) | Real Twelve project | Match |
|---|---|---|---|
| Modules and scope | Full module list, Financials remediation, conditional Expenses, Sustainability | Same list (07 capture) | **Match** **[V]** |
| BU structure | Requisitioning/Purchasing BUs into the existing structure; centralized, decentralized or shared service as an open decision | Same SOW wording. The captures show no enterprise-structure design document. | Match on SOW. Real design: **not recorded** **[V]** |
| Plants / inventory orgs | 2 plants, inventory orgs = plants (count of 2 inferred) | Same SOW wording | Match **[V]**; real inventory-org count not recorded |
| Integrations | 0; Coupa and MES as context only | 0 per SOW. Design workshops include "Cloud Financials, Prod Dev, Prod Data Hub & Coupa". The "SCM Old" kickoff mentions **Expensify**. | Match on 0. **Missed:** Expensify (not in the SOW, so not findable from it) and Product Development / Product Data Hub as existing PLM context. **[V]** |
| RICE | 1 report (printable PO), 1 conversion (Suppliers) | Same | Match **[V]** |
| Environments | Open question S2 (SOW silent) | Instance plan: Production, Test, Development (Dev 2) = 3 | Correctly left open. Answer is 3. **[V]** |
| Duration | 12 weeks (SOW) | SOW timeline 15–16 weeks (Feb 17 → Jun 2, 2025); "SCM Old" 12 weeks; re-planned ("CR to AUG") to about 24–32 weeks including hypercare | SOW figure is correct as stated. The real plan exceeded it. **[V]** |
| Test cycles | Open question S6 | CRP1 (wk5–6), CRP2 (wk9–10), UAT (wk13), Mock 1/2; re-plan CRP0/CRP1/CRP2, UAT 2–3 weeks | Correctly left open. FSCR has no test-cycle intake. **[V]** |
| Cutover / hypercare | Open question S7 | Go-Live Ready, HyperCare 4–8 weeks in re-plans; config migration; production data-load coordination | Correctly left open **[V]** |
| As-is Financials capture | Recommended an early enterprise-structure workshop (NV) | "As-Is Cloud Finance Knowledge Capture" wk2–4 | Consistent **[V]** |
| Hours | 3,820 (SOW table) | Captures say 4,800 | **Discrepancy.** The SOW governs; the 4,800 in the captures is not supported by the SOW cost table. **[V]** |

## 7. Conclusions

1. FSCR can run project intake from a SOW only **partly**. Its working parts are the classifier's catalog-based offering resolution and the ERP Business Unit design guidance. The six `shared/project-intake` skills and all integration skills are placeholder stubs with no questions, templates or examples. **[V]**
2. FSCR's project workflow is built for configuration, not planning. Project initialization needs a setup-task mapping and defaults to creating an Oracle Run Book, so a paper-only intake cannot pass its initialization gate (stop R3). **[V]**
3. Strict exact-match offering rules leave 18 of 25 SOW module terms pending. SOW wording (for example "Inventory and Cost Management", "Self-Service Procurement") does not match Oracle offering names. **[V]**
4. GoSaaS's Scoping Checklist and FSCR barely overlap. The checklist covers people, timeline, environments and test cycles. FSCR covers Oracle catalog identity and enterprise-structure design. Merging them would cover both. **[NV, recommendation]**

## 8. Run metrics

| Metric | Value |
|---|---|
| Time taken | about 8 minutes of wall clock, 09:57:29 → about 10:05 (end time recorded in the chat summary) **[V]** |
| Tool calls | About 50 (counted by hand; exact count not recorded by the harness here) **[NV]** |
| Output tokens | Not recorded exactly (no API accounting available in session). Deliverable text is about 23.4 KB of outputs plus about 15 KB in this report, roughly 10k tokens at chars/4 (FSCR's prescribed method). Total model output including reasoning: not recorded. **[NV]** |
| Processes started | 1 background copy (`cp`, finished, exit 0) and short shell commands; no servers, no browser **[V]** |
