# RUN 11 — FSCR project intake test (Twelve Oracle Cloud SCM SOW)

Run folder: `E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_11_project_intake`
Date: 2026-11-05. Paper only: no Oracle pod, no sign-in, no Fusion or REST calls, no tokens, no browser. [V]
Tags: **[V]** verified (checked in a file or the SOW); **[NV]** not verified / interpretation.

## 1. Setup
| Item | Result | Tag |
|---|---|---|
| Repo copy | `fscr-main\fscr-main` → `_fscr_run_11_project_intake\fscr-main` with robocopy; 6,120 files, same count as the original. Original and earlier run folders not modified | V |
| Input | Attached SOW PDF copied to `sow\`; text extracted with `pdftotext` to `sow\sow_text.txt` (313 lines). Signed by both parties 28 Jan 2025, document number 50513scm | V |
| Pre-existing project in the copy | `project\draft-impl-project-20261028` came with the copy; left untouched | V |
| Project workspace created | `fscr-main\project\twelve-scm-intake-20261105\` (copied from `project/_template`; see stop R5) | V |
| Portal code folder | not used | V |

## 2. FSCR skills and templates used (exact)
| # | Skill / file | Role in this run | Content it gave | Tag |
|---|---|---|---|---|
| 1 | `AGENTS.md` | Entry rules: start at the router; create `project/{id}` from `_template`; token log | Process rules | V |
| 2 | `router/implementation-router/SKILL.md` (router.implementation-router) | Entry point; depends on classifier + next-action-planner | Output names only; no intake questions | V |
| 3 | `router/project-objective-classifier/SKILL.md` (router.project-objective-classifier) | Offering / functional-area resolution rules (exact match, fail closed) | Real rules + catalog procedure | V |
| 4 | `router/next-action-planner/SKILL.md` | Read; generic | Output names only | V |
| 5 | `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json` + `pillars-offerings-mapping.json` | Resolved SOW modules to offering and functional-area codes | Real data (54 offerings) | V |
| 6 | `shared/project-intake/implementation-scope-intake/SKILL.md` | Scope intake | **Generic stub** (2,721 bytes; identical to the enterprise-structure and country-localization intake skills apart from the name) | V |
| 7 | `shared/project-intake/scope-definition/SKILL.md` | Defines the confirmed-scope artifact (scope, assumptions, exclusions) | Output structure only | V |
| 8 | `shared/project-intake/enterprise-structure-intake/SKILL.md` | Enterprise-structure intake | **Generic stub** | V |
| 9 | `shared/project-intake/integration-landscape-intake/SKILL.md` | Integration intake | **Generic stub** | V |
| 10 | `shared/integrations/{integration-strategy-advisor, oic-design-advisor, api-led…, event-driven…, legacy-system…}` | Checked for integration content | All 5 are ~2.1 KB generic stubs | V |
| 11 | `pillars/erp/financials/legal-structures`, `financial-reporting-structures`, `organization-structures` (SKILL.md task lists) | Object list for enterprise structure | Setup-task names/codes (LE, LRU, CoA, calendar, BU, BU function, set assignment, service provider) | V |
| 12 | `pillars/scm/manufacturing-and-supply-chain-materials-management/{facilities, cost-accounting, maintenance-management}` (folder names) | Object list for SCM structure (inventory orgs, item orgs, cost orgs, cost books, valuation structures, maintenance org relationships) | Folder/task names only (SKILL bodies not read) | V names / NV contents |
| 13 | `core/project-mgmt/project-workspace-initializer/SKILL.md` | Workspace creation rules | Read; script **not run** (see R4/R5) | V |
| 14 | `project/_template` + `schemas/implementation-objective.schema.json` | Workspace layout; objective fields | Used for `objective.json` | V |
| 15 | `knowledge/product-guidance/pillars/{scm/manufacturing…, erp/financials}/reference.md` | Product guidance (AGENTS says use first) | Only a link to Oracle's 26C implementation guide; no intake content. Oracle docs were not opened (paper-only run) | V |

Not used: `shared/project-intake/business-requirements-intake`, `country-localization-intake` (stubs, not needed — country stated as US) [V names; contents not read beyond size: NV]; `shared/implementation-planning/*` (planning, not intake) [V].

## 3. Every place FSCR's routed workflow stops to ask (recorded, not answered)
| # | Where | Rule (quoted / paraphrased) | Why it stopped here | Tag |
|---|---|---|---|---|
| R1 | AGENTS.md → project creation | "if no implementation project exists, create one … `draft_impl_project_<date>`, **inform the user, and offer to rename**" | No project existed for this objective. I named it `twelve-scm-intake-20261105` and record the offer here instead of asking | V |
| R2 | project-objective-classifier, Offering-Scope Resolution step 5 | "If there are no candidates or multiple candidates … set `offering_scope` to pending, and **ask for an offering short code** or sufficient business context" | The SOW uses module names ("Product Information Management", "Inventory and Cost Management", "Purchasing", "Manufacturing", "Maintenance") that are not exact offering display names; rule 4 forbids partial / keyword matches | V |
| R3 | project-objective-classifier, fail-closed rule | "Fail closed on ambiguous offering, functional-area … resolution" | Supplier Portal (2 offerings), Sustainability (3), Items (6), Structures (2), GL (2), Payables (3), Cash Mgmt (3), Project Costing (2), Receiving/Receipt Accounting (2) | V |
| R4 | project-workspace-initializer | "`--identified-task-mapping` is mandatory … If more than one offering remains plausible, **ask the user** to provide the current offering for that task" | A setup-task mapping cannot be derived from a SOW without picking configuration tasks (out of scope for paper intake) and offerings are unresolved (R2) | V |
| R5 | project-workspace-initializer completion gate | "A copied `project/_template` directory is not an initialized project" | I copied the template and wrote the intake artifacts. **Formally the project is not initialized**; `state/project-state.json` status = `blocked_offering_scope_pending` | V |
| R6 | initializer / router Run Book gate | New projects get `runbook_control: pending`, then `core.runbook` creates the Oracle Run Book | Would require an Oracle call; forbidden in this run. Not reached | V |
| R7 | implementation-router / next-action-planner | Output "human_review_points" | No concrete question text; generic | V |
| — | Intake skills (scope, enterprise structure, integration) | — | **Never ask anything**: they hold no questions | V |

## 4. The three outputs and who produced them
| Output | File | Producer | Basis | Tag |
|---|---|---|---|---|
| 1. Scope | `outputs/01_scope_intake.md` (copy in `project/…/artifacts/shared/project-intake/implementation-scope-intake/current/`) + `objective.json`, `scope.json` | **FSCR + Claude** — the classifier rules and catalog gave the offering/FA codes and the ambiguity finding; I wrote the scope content, exclusions, assumptions and 17 open questions | SOW only | V |
| 2. Enterprise structure | `outputs/02_enterprise_structure_intake.md` | **FSCR + Claude** — FSCR's setup skills gave the list of 18 structure objects; I filled each from the SOW and wrote the questions | SOW only | V |
| 3. Integration landscape | `outputs/03_integration_landscape_intake.md` | **Claude alone** — every FSCR integration skill is an empty stub; no integrations created (SOW: none) | SOW only | V |

Nothing from the SOW was invented: environments, users, ledgers, legal entities, BUs, cost orgs and the item master org are all listed as open questions. [V]

**Blind step:** all three outputs, plus the workspace copies, were written before any run 10 file was opened in this run. [V] Limitation: I created the run 10 files earlier in this same conversation, so their content was already in my context. True blindness was not possible. [V] After the blind step I opened DRIVE_REFERENCE.md, 01, 04 and 07 as instructed. I also grepped one line from `downloads/02_instance_plans_all_capture.txt` to confirm Twelve's environments; that file was not on your list. [V]

## 5. Our Scoping Checklist vs FSCR intake
Our checklist (`0 Pre Implementation Checklist/01. Scoping Checklist`) is written for **PLM**. Its Scope sheet has PD / PIM / Quality / EG&C / IM columns; there is no SCM, Procurement or Financials section. [V]

| Scoping Checklist question | FSCR intake skill covers? | My SOW-based output covers? | Tag |
|---|---|---|---|
| Annual revenue | No | No (not in SOW; not asked) | V |
| Legacy system / systems replaced | No | Partly — Coupa named; I1/I2/S10 ask about it | V |
| Industry | No | Asked (S15) | V |
| Number of locations | No (only via setup tasks) | Yes — 2 plants, 1 country (stated) | V |
| ERP | No | Yes — Oracle Fusion Financials already in production (inferred) | NV |
| Employees / number of users, approvers, viewers | No | Asked (S4) | V |
| ITAR / citizenship restrictions | No | **Missed** | V |
| Regulation (FDA) | No | Partly (S15 regulatory) | V |
| Business objectives | No | Yes (SOW objective) | V |
| Modules being implemented | Partly — classifier resolves modules to catalog codes | Yes | V |
| Number of divisions | No | Partly (BUs, E6) | V |
| Module-specific questions (PD/PIM/Quality/EG&C/IM) | No | Not applicable to SCM; SCM equivalents only partly (cost orgs, maintenance orgs) | V |
| GoSaaS tools | No | **Missed** | V |
| Customizations & custom reports | No | Yes — 1 report, 0 extensions (stated) | V |
| Security | Partly — Users and Security as a functional area | Asked (S12) | V |
| Integrations: endpoints, middleware, direction, objects | No (stub) | None in scope; I1–I7 asked | V |
| **Number of environments** | No | Asked (S2) | V |
| Data migration (sources, objects, volumes, history, delta) | No | Partly (Supplier conversion; S9, I3) | V |
| Post go-live / in-house IT / hypercare | No | **Missed** | V |
| Test environments (2 recommended) | No | Partly (S2) | V |
| Workshop durations (1 wk per module …) | No | **Missed** (planning, not intake) | V |
| Timeline extenders (regions, decision owner, decision process, time zones) | No | Partly (S17 decision owner); regions/time zones missed | V |
| Test cycles CRP1/CRP2/CRP3/UAT | No | Asked (S7) | V |
| Cutover window, delta migration | No | Partly (S8) | V |
| Quarter-end freeze | No | Yes (S8) | V |
| PM deliverables (high-level plan, instance plan, status, budget) | No | **Missed** | V |

**Covered by FSCR but not by our checklist** [V]:
1. Exact catalog resolution of each module to an Oracle offering and functional-area code, with ambiguity detection (e.g. Supplier Portal sits under both Procurement and Product Management).
2. A full enterprise-structure object list (legal entities, LRUs, CoA, calendars, ledgers, BUs, BU functions, reference sets, service-provider relationships, inventory/item orgs, cost orgs/books, maintenance org relationships). Our checklist asks only "Number of Locations" and "ERP".
3. Durable workspace discipline: objective/scope artifacts, versioning policy, project state, token-usage log.

**Summary:** FSCR's three intake skills hold **zero** intake questions. Every question in my outputs came from me (Claude), framed by FSCR's catalog and setup-task lists. [V]

## 6. Comparison with the real Twelve project (answer key)
| Topic | Intake (SOW only) | Real project (run 10 captures) | Match | Tag |
|---|---|---|---|---|
| Modules | PIM, Inv & Cost, SSP, Purchasing, Supplier Portal, process Mfg, Maintenance, Sustainability; incremental Fin/PPM; Expenses TBD | Same list (07 capture) | Yes | V |
| Existing Financials in production | Inferred (NV) | Schedule has "As-Is Cloud Finance Knowledge Capture" and design workshops include "overview of Cloud Financials, Prod Dev, Prod Data Hub & Coupa" | Confirmed | V |
| Coupa | Open question: config source or coexistence | Coupa is a design-workshop topic; "SCM Old" sheet also names Expensify | Partly confirmed; Expensify never mentioned in the SOW | V |
| Environments | Open question (S2) | Instance plan: Production, Test, Development (Dev 2) = 3 | Correctly left open; answer = 3 | V |
| Duration | 12 weeks (SOW) | Schedule 15–16 weeks; re-plan "CR to AUG" 27–32 weeks with HyperCare | SOW figure was optimistic; the intake flagged only "aggressive plan" | V |
| Test cycles | Open question (S7) | SOW timeline: CRP1, CRP2, UAT + Mock 1/2 loads; actual: CRP0, CRP1, (CRP2), UAT 2–3 weeks | Correctly left open | V |
| Integrations | None (SOW) | Key files list none. During run 10 (not in the key files) the Twelve folder had a design folder "Rippling - Oracle HR Integration" | Possible later integration outside SOW scope | NV |
| Enterprise structure | 2 plants → inv orgs; Req/Purch BUs; cost orgs/books; LE/ledger count open | Key files do not record the final structure | not recorded | V |
| Hours | **3,820** (sum of the cost table) | Run 10 `07_C2_scm_sow_capture.txt` and DRIVE_REFERENCE §4 say "4,800 hours" | **Run 10 was wrong**; 3,820 is correct (140+640+80+560+320+280+280+560+560+400). Run 10 files left unchanged per your rule | V |

## 7. Bottom line
- **Scope:** FSCR + Claude. FSCR's useful part is the catalog check, which shows the SOW's product names don't map one-to-one to Fusion offerings, so FSCR stops and asks (R2/R3). [V]
- **Enterprise structure:** FSCR + Claude. FSCR knows what objects exist but has no intake layer; its skills go straight to configuration (Data Loader / Run Book). [V]
- **Integration landscape:** Claude alone. FSCR's integration skills are empty. [V]
- FSCR cannot formally finish project initialization from a SOW. The initializer requires a setup-task mapping and then an Oracle Run Book creation (R4–R6). [V]

## 8. Run stats and cleanup
- Time: 09:45:01 → 09:52 local, about 7 minutes of wall clock between the first and last timestamped command. [V]
- Tool calls: about 33 in this run. Output tokens: roughly 20–25k (estimate; exact accounting is not available to me). [NV]
- Processes: none started in this run (no servers, no browser). The run 10 browser and helper were already stopped. [V]
