# Twelve: manual planning baseline (Oracle Cloud SCM, SOW dated Jan 24, 2025)

- **Run:** 13. Read-only review of the customers Google Drive (`Customers / Twelve Projects`).
- **Date:** 2026-11-05.
- **Method:** browser crawl of every sub-folder of *Cloud SCM Expansion 2024* (1,246 items in 200 folders; 8 more folders re-checked, 7 empty). File contents were read through the browser document viewer and the Google Drive connector, using read-only calls only.
- **Read-only:** nothing in Drive was created, edited, moved, renamed, shared, commented on or deleted.
- **Legend:** **V** = verified (I opened and read the content). **NV** = not verified (name only, or not opened). "SCM/…" = `Twelve Projects/Cloud SCM Expansion 2024/…`.
- **Dates:** created and modified times come from Drive metadata where I fetched them; otherwise I use the date shown in the Drive list. A date with no year (e.g. "Aug 24") is 2026.
- **Before/after SOW** is judged against Jan 24, 2025. Every file below was made by hand by the GoSaaS or Twelve team, so all of them predate FSCR/Claude. The only Claude-era item seen is a PDF created 2026-11-04 outside the Customers folder, and it was not used.

## 1. Verdicts

| # | Output | Verdict | Main manual source(s) | Before SOW? |
|---|---|---|---|---|
| 1 | Scope | **PRESENT** | SOW v4 (signed) [V]; Kick Off deck [V]; Change Requests #01 and #02 [V]; Updated Plan [V]; pre-SOW *Oracle (& Plex) Implementation Proposal* [V] | Proposal: before. SOW, kickoff and CRs: on or after. |
| 2 | Enterprise structure | **PRESENT** (after SOW only) | Enterprise Structures Best Start (Apr 2025, CRP1 May 2025) [V]; Cost Management Best Start [V]; Inventory Best Start CRP1 [V]; Enterprise Structure decks (diagrams are images) [V text / NV diagrams] | After. The pre-SOW Procurement design doc has an empty org-structure section. |
| 3 | Integration landscape | **PARTLY** | SOW ("no extensions and integrations") [V]; CR #01 (Rippling → Oracle HR via OIC) [V]; Rippling HR Integration deck [V]; Cutover Strategy [V]; CR #02 (international bank wire) [V] | After. Pre-SOW only mentions systems (Coupa, Plex, Kiwi, Aveva PI/PLC) [V]. |
| 4 | Offering task map | **PRESENT** (after SOW) | Configuration Master Checklist (381 tasks, 7 module tabs) [V]; Best Start task indexes [V]; Project Plan config task list [V]; Requirements MASTER RTM (134 requirement IDs) [V] | After. Pre-SOW: Requirements Gathering Tracker (8 modules, no tasks) [V]. |
| 5 | Wave plan / instance plan | **PARTLY** | *Twelve Instance Plan 2025.xlsx* [V text; cell shading NV]; *Twelve SCM Project Schedule.xlsx* (7 re-plan versions) [V]; Updated Plan [V]; CR #02 dates [V] | After (created 2025-03-05). |
| 6 | Task dependencies | **PARTLY** (mostly implied) | Twelve Project Plan: predecessors on 5 of ~277 tasks [V]; Config Master Checklist "Predecessor/Owner" holds the owning module [V]; CRP entry criteria [V] | After. |
| 7 | Readiness checklist | **PRESENT** (go-live and cutover, after SOW) | Twelve Cutover Plan.xlsx (24 items) [V]; Twelve Cutover Strategy (Go/No-Go business and application checklists) [V]; CRP1 entry criteria [V] | After (Aug 2025). The "00 Preimplementation Checklist" folder holds no checklist. |

**Bottom line:**
- No complete manual baseline existed **before** the SOW date. Before Jan 24, 2025 there were only:
  - the phased-scope proposal (Jun 2024)
  - discovery Q&A (Dec 2024)
  - a module-owner tracker (Nov–Dec 2024)
  - a generic procurement design draft (Nov 2024)
  - a project-plan template copied from another customer
- Every output except the integration landscape has a manual version made **after** the SOW, between Feb and Aug 2025. Dependencies and the instance plan are only partly captured.

## 2. Detail per output

### 2.1 Scope: PRESENT

**Twelve - Oracle Cloud SCM Implementation SOW v4 (signed)**
- **File:** Google Doc, SCM/08 Project Management/SOW. Created and modified 2025-02-05; document dated Jan 24, 2025. [V] Capture: `captures/SOW_v4_signed_scope_capture.txt`
- **SCM modules, with sub-items:**
  - PIM (3)
  - Inventory & Cost Mgmt (6: plants as inventory orgs, costing org structure and cost books, costing for manufactured, maintenance and inventoried items)
  - Self-Service Procurement (5, reusing Coupa values)
  - Purchasing (2)
  - Supplier Portal (5)
  - Manufacturing (4: process mfg "ready to use")
  - Maintenance (7: equipment, structures, work definitions, WOs, meters, programs, Installed Base)
- **Financials and reporting:**
  - Remediation of GL, AR, Projects, Grants, AP, Cash Mgmt and FA
  - New Sustainability; Expenses subject to a design session
  - Confirm BU structure (add Requisitioning and Purchasing BUs)
  - Reporting approach (OTBI/BIP/FDI/EPM)
  - GL support
- **RICE:** 1 report (printable PO), 1 conversion (Suppliers); no integrations, no extensions.
- **Configuration scope:** 12 areas (PIM, SSP, Purchasing, Supplier Portal, Payables, Inventory & Cost, GL/SLA, Projects, Sustainability, Maintenance, Manufacturing, Security & Roles).
- **Change management:** training materials; Train-the-Trainer.
- **Exclusions:**
  - discrete manufacturing
  - MES integration
  - configuration or migration of structures, work definitions and assets
  - EPM sustainability reporting
  - integrations and extensions
  - travel
- **Assumptions (11):** 1 country (US), 2 plant locations, 12 weeks, minimal data migration, common design, Twelve migrates configurations to PROD, Twelve owns change management.
- **Costs:** rate, hour and total tables present (masked).

**Scope changes after the SOW (manual)**
- **CR #01** (.docx, SCM/08 Project Management/Change Requests, list date May 5, 2025) [V]:
  - removes Expenses (Twelve chose Rippling Expense)
  - adds Oracle Tax (indirect and use tax, jurisdictions; no third-party tax engine)
  - adds the inbound Rippling → Oracle HR integration via OIC
  - expands Projects (types and templates, structures, expenditure categories, manual budgets, assets to FA; excludes burdening, intercompany and resource management)
- **CR #02** (two versions, May 10, 2025 and Aug 27, 2025 "_final") [V]:
  - go-live moved to Aug 1, 2025, then Sep 1, 2025
  - hypercare through Sep and Oct 2025
  - adds AirPlant One BU financials (GL, AR, FA, CM, AP, Purchasing, SSP) for LEs Twelve Benefit Corporation (001) and Twelve Rainier, LLC (003)
  - adds a Coupa supplier onboarding strategy, Coupa open-PO conversion and Alameda on-hand conversion, and the international bank wire remediation
- **Twelve Updated Plan.pptx** (SCM/08 Project Management, May 15, 2025) [V]:
  - adds AirPlant Financials and close-out
  - out of scope: Coupa close-out conversions, international wire
  - future items: AirPlant FA and project migrations, hypercare, Stacks/Alameda full Inventory and Manufacturing, Maintenance, Configure-to-Order, OTBI/FRS, EPM, Joint Venture Management
- **Twelve Cloud SCM 2024 Kick Off.pptx** (SCM/08 Project Management; created 2024-11-14, modified 2025-02-14) [V]:
  - new or changed modules: SSP, Purchasing, Supplier Portal, Inventory, Cost, Expenses, Sustainability, Product Data Mgmt, Maintenance, Manufacturing
  - phases: PIT → Design Workshops → Build → CRP 1 & 2 / UAT / EUT → Deployment
  - tentative KDD list

**Pre-SOW scope**
- **Oracle (& Plex) Implementation Proposal 6-5-24.pptx** (SCM/98 Files from Twelve; created 2024-06-25, modified 2024-12-05, **before SOW**) [V]. Twelve's own 5-phase plan:
  1. R1 Moses Lake Procurement, Inventory, Maintenance, Order Mgmt, plus Stacks PLM
  2. C1/R1 capital procurement
  3. MEA and Stacks Procurement, Inventory, Sourcing, MEA PLM
  4. MEA and Stacks Manufacturing and Maintenance (Plex, limited)
  5. Indirect purchasing, ending Coupa
- Timeline Jul '24 → Mar '25. Finance was already live.

### 2.2 Enterprise structure: PRESENT (after SOW)

Sources [V]:
- *Twelve - Oracle Fusion - Enterprise Structures Best Start .xlsx* (SCM/03 Design Documents/Best Starts, list date Apr 8, 2025)
- *… (1).xlsx* in Best Starts/CRP 1 (May 23, 2025)
- *Twelve - Oracle Fusion - Cost Management Best Start* (Google Sheet, May 6, 2025)
- *Twelve - Oracle Fusion - Inventory Best Start.xlsx* in Best Starts/CRP 1 (May 23, 2025)
- The Google Sheet *Inventory Best Start* (Nov 4, 2025) has headers only, with no org rows.

| Object | Values in the manual Best Starts |
|---|---|
| Ledgers | **Twelve US** (USD, COA "Twelve", calendar "Twelve", Twelve Standard Accrual); **Twelve NL** (EUR, Standard Accrual) |
| Legal entities | **Twelve Benefit Corporation** (001, US, ledger Twelve US); **Twelve Rainier, LLC** (003, US, ledger Twelve US); **Opus B.V.** (002, Netherlands, ledger Twelve NL); company value 100 "Twelve Corp" also in COA |
| COA | 8 segments: Company, Account, Cost Center, Location, LoB, IC, Future1, Future2 |
| Business units | Apr 2025: **Twelve Operations** (Berkeley 710, set COMMON). CRP1 May 2025: Twelve Operations (now Alameda 1135) + **AirPlant 1** (Moses Lake, LE "Rainer LLC"). CR #02 calls it "AirPlantOne". |
| Inventory organizations | CRP1 Inventory Best Start: **Alameda (ALA1)**, **Berkeley (BRK1)**, **AirPlant™ One (AirP1)**, **Blender (BLE1)**, all BU Twelve Operations / LE Twelve Benefit Corp; **AirPlant™ Two (AirP2)** with BU AirPlant 1 / Rainier LE; item master org **Twelve**. Addresses present, masked. |
| Cost organizations | **Stacks Cost Org** (Twelve_Cost_Org_01) → Alameda, Berkeley. **Fuels Cost Org** (Twelve_Cost_Org_02) → AirPlant One. Both under LE Twelve Benefit Corp, effective 3/1/25. |
| Cost books | **Twelve Benefit Cost Book** ("Primary Stacks CB"); **Twelve AirPlant One Cost Book** ("Primary Fuel CB"); both on the US Ledger; Perpetual Average cost profiles |

**Decks:**
- *Twelve Enterprise Structure.pptx* (Mar 19, 2025) and *… CRP 0.pptx* (Jul 3, 2025), SCM/01 Trainings and Workshops/Design Workshops/Enterprise Structure.
- Text read [V]. The current, to-be, CRP0 and CRP1 structure diagrams are images (NV).
- Also NV in the same folder: *To-Be Enterprise Structure.jpg*, *Current Enterprise Structure_rev01.jpg*, *Enterprise Structure.drawio*, *Cost Organization Structure.drawio*; and in Design Workshops/Accounting, *Twelve Ledger Design.drawio* ×2.

**Before SOW:**
- *Twelve Procurement Design Document V1.docx* (Nov 2024) [V] has an "Organization Structure" section with no Twelve entities.
- The SOW states 2 plant locations and 1 country.

### 2.3 Integration landscape: PARTLY

No consolidated integration landscape document was found. What exists [V]:
- **SOW (Jan 24, 2025):** "No extensions and integrations are part of the target scope". MES integration is explicitly out of scope. The only RICE items are the PO report and the supplier conversion.
- **CR #01:** inbound **Rippling → Oracle HR (HCM)** via **Oracle Integration Cloud (OIC)**. Twelve runs the extract and transformation; GoSaaS builds the OIC side.
- **Rippling - HR Integration.pptx** (May 13, 2025):
  - system of truth: Rippling
  - flow: employee data file → OIC (get file, map, transform) → create/update employee in Oracle HCM, with a success/failure response
  - needs OIC and HCM service accounts and an optional connectivity agent
  - deliverables listed
- Supporting files in *SCM/03 Design Documents/Rippling - Oracle HR Integration* (NV): mapping sheets, HR extract and a recording.
- **CR #02:** international Payables bank wire transfer integration (discovery and remediation), plus Coupa → Oracle open-PO and on-hand **conversions**.
- **Cutover Strategy and Cutover Plan:** HRIS/OIC integration is the only integration in cutover; "Failure in core integration (Rippling HR)" is a No-Go trigger.
- **Before SOW** (systems mentioned, no landscape):
  - the proposal names Coupa and Plex
  - discovery answers name the Kiwi app (M-BOM), Aveva PI dashboards and PLC devices ("nice to have" integration)
- **NV:** *B2B XML Invoices import Production Setups* (Google Doc, SCM/09 OCM/Training Materials, Jan 8, 2026), not opened.
- **Verdict:** PARTLY. It comes down to one integration (Rippling → HCM via OIC, inbound) plus conversions and a bank-wire item, all after the SOW, with no landscape document.

### 2.4 Offering task map: PRESENT (after SOW)

- **Configuration Master Checklist** (Google Sheet, SCM/02 Testing, list date Aug 18, 2025) [V]. Columns: Task List/Task, Description, Required, Predecessor/Owner, BU Specific/Cross BU, Configured. Capture: `captures/Configuration_Master_Checklist.txt`

  | Tab | Tasks | Group headers | Configured status |
  |---|---|---|---|
  | Financials | 252 | 45 | all FALSE |
  | Procurement | 51 | 16 | 22 TRUE / 29 FALSE |
  | Inventory | 29 | 1 | Not Started |
  | Costing | 14 | 4 | Not Started |
  | Manufacturing | 11 | – | Not Started |
  | Maintenance | 21 | 3 | Not Started |
  | PIM | 3 | – | FALSE (offering "Product Management") |
  | **Total** | **381** | | |

- **Best Start task indexes** [V]:
  - Enterprise Structures: 28 GL setup steps (GL-01…), Mandatory/Optional, Y/N status
  - Inventory (CRP1): 24 steps Inv-01…Inv-24, all "Ready for Verification"
  - Other Best Starts exist per module (NV, beyond names): Procurement, Purchasing, Supplier Portal, PIM, Manufacturing, Maintenance, Expenses, AP, AR, Accounting, Cash Mgmt, Tax, Projects, Sustainability, SCFO, Procurement Approval (PROD)
- **Twelve Project Plan** (Google Sheet, SCM/03 Design Documents/Archive, Aug 14, 2025) [V]. Its "Configure test environment" step lists setup tasks per module: Enterprise Structures 18, Procurement 15, Product Data Hub 4, Sustainability 7, Inventory 28, Maintenance 5 pre-config + 24 config, Manufacturing 12, Costing 14, Payables 23, Supplier Portal 6.
- **Requirements matrices** [V]:
  - *Twelve ERP SCM Requirements MASTER.xlsx* (SCM/03 Design Documents/Archive/Old versions; created 2025-02-03, modified 2025-02-25): Consolidated RTM with 134 requirement IDs (PO 77, INV 57), 111 marked in scope (PO 65, INV 46). Source rows are dated May 2023, so they were carried over from Twelve's earlier RTM.
  - *Twelve Procurement Requirements Traceability Matrix (1).xlsx* (SCM/98 Files from Twelve, Jan 18, 2025, **before SOW**): 79 rows PO01–PO79; several marked "Phase 2" or "remain in Coupa"; PO79 is Coupa open-PO conversion.
- **Before SOW:** *Twelve - Requirements Gathering Tracker* (created 2024-11-06, modified 2024-12-11) [V] lists 8 modules with owners, design docs, Best Start names and target dates, but no tasks.
- **NV:** *Functional Setup Manager Package.pptx*; *Twelve ERP SCM Business Scenarios.xlsx*; Inventory and Order Management RTMs; *Design Workshop List/Schedule*.

### 2.5 Wave plan / instance plan: PARTLY

- **Twelve Instance Plan 2025.xlsx** (SCM/08 Project Management; created 2025-03-05, modified 2025-04-24) [V text]:
  - Sheet "2024 All": weekly columns from 30-Dec (2024) to 24-Nov (2025).
  - Environment rows: **Production, Test, Development (Dev 2)**; activity rows: **Patch, Refresh, Data Extract, Cutover**.
  - Oracle update row: **24D** (wk 30-Dec), **25A** (27-Jan), **25B** (28-Apr), **25C** (28-Jul), **25D** (27-Oct).
  - Sheet "Key": cohort months A = Feb/May/Aug/Nov, B = Mar/Jun/Sep/Dec, C = Apr/Jul/Oct/Jan; **LS = A (Dev) + B (Test & Prod)**; **Non-Prod = 1st Friday, Prod = 3rd Friday**.
  - **NV:** which weeks each environment, patch, refresh or cutover occupies is coded in cell shading and does not come through as text.
- **Twelve SCM Project Schedule.xlsx** (SCM/08 Project Management, Jul 10, 2025) [V]. Re-plan versions:
  1. "SOW Timeline": 16 weeks, Feb-17 → Jun-02 Go-Live; CRP1, CRP2, UAT, TTT, EUT
  2. "SCM SOW": 15 weeks; Mock 1/2; Ready to Use
  3. "SCM Current" as of May 14, 2025: CRP0 (wk Apr 7), CRP1 (wk May 12)
  4. "CR to AUG": CRP2 + 3-week UAT, Go-Live Ready and Hypercare around Aug 2025
  5. Variant without CRP2 (2-week UAT)
  6. Variant to Jul-28 (extended CRP1, TTT, UAT)
  7. "SCM Old": 12 weeks, Jan-13 → Mar-31
- **Other dated sources** [V]:
  - Updated Plan (May 15, 2025): accelerated timeline, CRP1 deferred 1 week for AirPlant Financials
  - CRP Approach: CRP1 May 19–30, 2025
  - UAT Approach: TTT Aug 4–8, 2025
  - CR #02: go-live Aug 1 then Sep 1, 2025
  - Cutover Strategy: go-live 09/02/2025
- **NV:** *Twelve SCM PIT Schedule.xlsx*, *Twelve CRP 1 Schedule_DRAFT (1).xlsx*, *UAT Schedule.xlsx*, *Twelve Redwood Roadmap.xlsx*, *Twelve Project Management* (Google Sheet).
- **Verdict:** PARTLY. The instance plan exists with environments and update windows, but its environment-by-week grid is not readable, and the test cycles and go-live sit in separate schedule files. All of it is after the SOW.

### 2.6 Task dependencies: PARTLY (mostly implied)

- **Twelve Project Plan** (Google Sheet) [V] has Predecessors and Successors columns, but only **5 of ~277** task rows carry predecessors, all in onboarding:
  - 2 (Kickoff meeting) ← 1
  - 3 (Project Team Spreadsheet) ← 2
  - 4 (Onboarding) ← 3
  - 5 (SharePoint access) ← 4
  - 6 (Oracle access) ← 4
  - Design, CRP, UAT, Training and Ready to Use rows have no predecessors; many show "Missing Dates".
- **Configuration Master Checklist** [V]:
  - The "Predecessor/Owner" column holds the **owning module**, not a task predecessor. Examples:
    - Procurement "Manage Inventory Organization" → Inventory
    - Maintenance "Manage Plant Parameters" → Manufacturing
    - "Manage Inventory Organization Data Access" → Financials
    - Costing tasks → Cost Management
  - Values appear on 45 of 381 rows: Procurement 10, Costing 14, Maintenance 21.
  - The Financials tab has a colour key "Prerequisite Tasks / Configuration Tasks", but the colours are not readable as text (NV).
- **Implied ordering** [V]: kickoff phase order (PIT → Design → Build → CRP → Deployment); CRP1 entry criteria (Best Starts documented → configs loaded in DEV2 → smoke test → scripts reviewed → RAID log → user access); the Maintenance "Pre-Configurations" block in the Project Plan (GL, Enterprise Structure, Inventory, Suppliers, Plant Parameters before maintenance configs); cutover sequence (Aug-19 prep → Aug-20 integration → Aug-20..27 applications → Aug-28/29 people → Sep-2 go-live).
- **Before SOW:** *Twelve SCM Expansion 2024 Plan.xlsx* (SCM/03 Design Documents/Archive; created 2024-11-26, modified 2024-12-18) [V] has numeric predecessors (e.g. "122, 123", "162"). Its own Comments tab says it is "a copy from a PLM project. To be updated to reflect for Twelve scope", and the tasks are another customer's PLM project. It is **not** Twelve dependency content.

### 2.7 Readiness checklist: PRESENT (go-live and cutover, after SOW)

- **Twelve Cutover Plan.xlsx** (SCM/08 Project Management, Aug 18, 2025) [V]. 24 items, all "Not Started":
  - Design configuration sign-off (PROD Best Starts)
  - Define processes
  - Define policies & procedures
  - Go/NoGo decision
  - Cutover communication email
  - PROD provisioning & admin access
  - **Production instance readiness check**
  - Freeze configs in DEV2
  - Enable modules in PROD
  - HR configs in PROD
  - HRIS/OIC integration to PROD
  - Integration validation
  - PROD configuration of Financials, Procurement, Projects and SCM
  - Security configuration in PROD
  - Cross-module transaction test in PROD
  - End-user role assignment confirmation
  - Responsibility & org structure verification
  - End-user training completion
  - Freeze Coupa
  - Go-Live (Sep-2)
- **Twelve Cutover Strategy** (Google Slides, 08/22/2025) [V]:
  - **Go criteria:** no open high defects; 100% UAT success for key processes; critical configs successful in PROD; training repository built.
  - **No-Go triggers:** high-severity UAT issues; Rippling HR integration failure; Finance/SCM reconciliation gaps.
  - **Business Readiness Checklist:** Business Processes, Infrastructure, Data, People.
  - **Application Checklist:** 12 lines, from GL/AR/CM/FA through HRIS/OIC, each checked for UAT, EUT material and PROD configuration.
- **CRP1 entry criteria** in *Twelve SCM CRP Approach.pptx* (May 30, 2025) [V]: business scenarios, roles and responsibilities, application configurations, master data, seed data, RICE migrated and validated.
- **Pre-implementation checklist:** none found. *SCM/00 Preimplementation Checklist* contains only the sub-folder *Pre-Implementation Slides PIM* with one shortcut, "Product Data" (Google Slides). Its content was not opened (NV).
- **Before SOW:** none found.

## 3. Files relied on

| File | Drive path | Created | Last modified | vs SOW | Read |
|---|---|---|---|---|---|
| Twelve - Oracle Cloud SCM Implementation SOW v4 (signed) (GDoc) | SCM/08 Project Management/SOW | 2025-02-05 | 2025-02-05 | doc dated SOW date; file after | V |
| Twelve Cloud SCM 2024 Kick Off.pptx | SCM/08 Project Management | 2024-11-14 | 2025-02-14 | created before, final after | V |
| Oracle (& Plex) Implementation Proposal 6-5-24.pptx | SCM/98 Files from Twelve | 2024-06-25 | 2024-12-05 | **before** | V |
| Twelve - SCM Implementation Change Request #01.docx | SCM/08 Project Management/Change Requests | not recorded | May 5, 2025 | after | V |
| Twelve - SCM Implementation Change Request #02.docx | same | not recorded | May 10, 2025 | after | V |
| Twelve - Change Request 02 Extension and Hypercare_final.docx | same | not recorded | Aug 27, 2025 | after | V |
| Twelve - SCM Implementation Addendum.docx (blank template) | same | not recorded | Mar 20, 2025 | after | V |
| Twelve Updated Plan.pptx | SCM/08 Project Management | not recorded | May 15, 2025 | after | V |
| Twelve - Oracle Fusion - Enterprise Structures Best Start .xlsx | SCM/03 Design Documents/Best Starts | not recorded | Apr 8, 2025 | after | V |
| Twelve - Oracle Fusion - Enterprise Structures Best Start (1).xlsx | SCM/03 Design Documents/Best Starts/CRP 1 | not recorded | May 23, 2025 | after | V |
| Twelve - Oracle Fusion - Inventory Best Start.xlsx | SCM/03 Design Documents/Best Starts/CRP 1 | not recorded | May 23, 2025 | after | V |
| Twelve - Oracle Fusion - Cost Management Best Start (GSheet) | SCM/03 Design Documents/Best Starts | not recorded | May 6, 2025 | after | V |
| Twelve Enterprise Structure.pptx / … CRP 0.pptx | SCM/01 …/Design Workshops/Enterprise Structure | not recorded | Mar 19 / Jul 3, 2025 | after | V (text) |
| Cost Management CRP1 - TWELVE (GSlides) | SCM/03 Design Documents/Cost Management | not recorded | Apr 16, 2026 | after | V |
| Twelve CRP1 Manfuacturing Structure.pptx | SCM/03 Design Documents | not recorded | May 6, 2025 | after | V |
| Rippling - HR Integration.pptx | SCM/03 Design Documents/Rippling - Oracle HR Integration | not recorded | May 13, 2025 | after | V |
| Configuration Master Checklist (GSheet) | SCM/02 Testing | not recorded | Aug 18, 2025 | after | V |
| Twelve Project Plan (GSheet) | SCM/03 Design Documents/Archive | not recorded | Aug 14, 2025 | after | V |
| Twelve ERP SCM Requirements MASTER.xlsx | SCM/03 Design Documents/Archive/Old versions | 2025-02-03 | 2025-02-25 | after | V |
| Twelve Procurement Requirements Traceability Matrix (1).xlsx | SCM/98 Files from Twelve | not recorded | Jan 18, 2025 | **before** | V |
| Twelve - Requirements Gathering Tracker (GSheet) | SCM/03 Design Documents/Archive | 2024-11-06 | 2024-12-11 | **before** | V |
| Updated Discovery Questions for Twelve 12-Dec - Answers.xlsx | SCM/98 Files from Twelve | 2024-12-13 | 2024-12-16 | **before** | V |
| Twelve Procurement Design Document V1.docx | SCM/03 Design Documents | not recorded | Nov 20, 2024 | **before** | V |
| Twelve SCM Expansion 2024 Plan.xlsx (copy of another customer's plan) | SCM/03 Design Documents/Archive | 2024-11-26 | 2024-12-18 | **before** | V |
| Twelve Instance Plan 2025.xlsx | SCM/08 Project Management | 2025-03-05 | 2025-04-24 | after | V (text) / NV (shading) |
| Twelve SCM Project Schedule.xlsx | SCM/08 Project Management | not recorded | Jul 10, 2025 | after | V |
| Twelve Cutover Plan.xlsx | SCM/08 Project Management | not recorded | Aug 18, 2025 | after | V |
| Twelve Cutover Strategy (GSlides) | SCM/08 Project Management | not recorded | Aug 22, 2025 | after | V |
| Twelve SCM CRP Approach.pptx | SCM/02 Testing | not recorded | May 30, 2025 | after | V |
| Twelve SCM UAT Approach.pptx | SCM/02 Testing/3 UAT | not recorded | Jul 31, 2025 | after | V |

"Not recorded" = I did not fetch the created time; the last-modified date is the one shown in the Drive list.

## 4. Could not open, or not opened

**Could not open**
- *Twelve Post Prod Deployment Projects.pptx* (shortcut, SCM root): "You need permission to open this item".
- *Twelve Roadmap* (Google Slides shortcut, SCM/98 Files from Twelve): the target returned "Page Not Found".
- Image or diagram content with no text:
  - *To-Be Enterprise Structure.jpg*, *Current Enterprise Structure_rev01.jpg*, *Twelve Cost Breakdown Structure Example.png*
  - diagram slides inside the Enterprise Structure decks
  - colour-coded cells in *Twelve Instance Plan 2025.xlsx* and in the Configuration Master Checklist key
- draw.io files: *Enterprise Structure.drawio*, *Cost Organization Structure.drawio*, *Twelve Ledger Design.drawio* ×2, *Generate Accounting.drawio*, *Procure to Invoice Approvals.drawio*, *Twelve R1 WO process flow.drawio*. Not opened; no text reader was used for this file type.

**Not opened (named only, NV)**
- **PDFs:** SOW v4 (signed).pdf, Kick Off.pdf, the two PO PDFs, the E-Jet PDFs.
- **Schedules:** PIT Schedule, CRP 1 Schedule DRAFT, UAT Schedule, Redwood Roadmap, *Twelve Project Management* (GSheet), *Twelve Project Plan.xlsx*.
- **Workshops and setup:** Design Workshop List and Schedule, *Design Workshops* (GSheet), *SCM Pre Implementation Training List*, *Functional Setup Manager Package.pptx*.
- **Requirements:** Business Scenarios workbooks, Inventory and Order Management RTMs, Change Request Tracker.
- **SOW-folder workbooks:** Roadmap/ROM workbooks in SOW and Change Requests (these contain estimates).
- **Design and training:** *B2B XML Invoices import Production Setups*, Reporting Strategy files, Enterprise Configuration PIT slides, *Ledger and Accounting Flexfield Design.pptx*, Project Status decks (2/28–4/18/2025), Security Mini-Project and security matrices, design workshop decks per module, training materials, test scripts, IDR invoice samples, PIDX files, FBDI templates.
- A first browser read of several of these was started but lost when the browser session dropped; it was not re-run.

**Other folders checked only by title search, not crawled in full**
- **Other Twelve project folders** (*ERP*, *CTO Demo*, *Cloud PLM 2023*, *Cloud EPM 2024*, *2026 Projects*): a Drive title search for Twelve SCM, Inventory, Procurement, Instance, Cutover and Readiness files found nothing SCM-specific in them.
- **Twelve SCM files elsewhere in the same shared drive:**
  - a "Configuration Workbooks" folder (created 2026-07-06) with three Best Starts
  - training materials (Dec 2025)
  - all post-implementation, not used
- **Copies in a different shared drive** (outside the Customers folder, not reviewed): Best Starts, Design Documents (Requirements MASTER, Business Scenarios, Procurement Design Doc) and Pre-implementation slides, dated Feb 2025.
- **A Claude-era item:** a signed SOW PDF created 2026-11-04 in another drive. Not used.
- **000 Reference Project Setup:** top level listed only (generic folders: 2 Training and Workshops, 6 UAT, 8 Integration Documents, 20. Reference Large Project Setup, *Oracle Cloud Implementation Process* doc). No Twelve files found by title search; contents not opened.

**Empty folders (verified):** SCM/07 Post Go Live, SCM/04 Extensions, SCM/08 Project Management/Meeting Records, SCM/03 Design Documents/Best Starts/CRP 0, SCM/01 …/Design Workshops/Procurement, two training sub-folders.

## 5. Captures

All captures are in `captures/` and are masked: emails, phones, $ amounts, rates and street addresses are replaced with "[… masked]".
- `_drive_inventory_scm_folder.tsv`: full list of the SCM folder (1,246 rows: name, path, list date, type, id)
- `SOW_v4_signed_scope_capture.txt`
- `_condensed_extracts_of_files_read_inline.md`: Enterprise Structure decks, Cost Best Start, Cost CRP1, Manufacturing structure, Rippling, Project Plan, Project Schedule, Cutover Plan and Strategy, CRP and UAT approach, Requirements tracker, Discovery Q&A, Procurement design doc
- Full-text captures:
  - Kick Off deck
  - Proposal
  - Updated Plan
  - Instance Plan
  - SCM Expansion 2024 Plan
  - CR #01, CR #02, CR #02 final, Addendum
  - Enterprise Structures Best Start (Apr and CRP1)
  - Inventory Best Start CRP1
  - Requirements MASTER
  - Procurement RTM
  - Configuration Master Checklist
