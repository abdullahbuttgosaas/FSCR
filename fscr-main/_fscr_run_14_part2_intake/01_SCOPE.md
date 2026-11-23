# Output 1: Project Scope (Project Intake)

**Project:** Twelve Benefit Corporation ("Twelve"): Oracle Cloud SCM Implementation
**Source:** SOW "Twelve - Oracle Cloud SCM Implementation SOW", dated January 24, 2025, signed Jan 28, 2025, Document Number 50513scm (`input/…SOW v4_Twelve-signed_GS signed.pdf`, MD5 77241006ca0165557315ca946f4b6c56)
**Produced by:** FSCR + Claude. FSCR supplied the classifier rules, the effective offering/functional-area catalog and the workspace (`fscr-main/project/twelve-scm-intake-20261105/artifacts/router/project-objective-classifier/current/scope.json`). Claude read the SOW, mapped it to catalog codes, and wrote this document in the shape of the GoSaaS Scoping Checklist. FSCR's `shared/project-intake/implementation-scope-intake` and `scope-definition` skills are empty stubs and contributed nothing.
**Status:** Planning only. Nothing configured, no Fusion calls.

**Labels used**
- **[SOW §x]** is stated in the SOW. Verified against the extracted SOW text (`work/sow_text.txt`).
- **[FSCR]** comes from the FSCR effective catalog in the repo copy. Verified by script output.
- **SUGGESTED (checklist)** is a recommendation taken from the GoSaaS checklist capture (`01_checklists_capture.txt`). It is not verified for this project and is also listed as an open question.
- **SUGGESTED (Claude)** is a recommendation with no checklist source. It is not verified and is also listed as an open question.
- **not stated** means the SOW is silent and there is no suggestion.

---

## 1. Customer Information (Scoping Checklist › Customer Information)

| Checklist question | Answer | Basis |
|---|---|---|
| Customer | Twelve Benefit Corporation; signatory Maisie Luce, Head of IT | [SOW cover] verified |
| Industry | not stated | – |
| Annual revenue | not stated | – |
| Employees / number of users | not stated | – |
| Number of locations | 1 country (US), 2 plant locations | [SOW C.7] verified |
| Current ERP | Oracle Cloud Financials already in production: GL, AR, Project Management, Grants Management, AP, Cash Management, Fixed Assets | [SOW B, "Financials and Reporting Scope"] verified |
| Legacy procurement system | Coupa. The SOW says to reuse "configuration values and concepts from Coupa". | [SOW B 3.5] verified |
| Legacy PLM / MES | No PLM named. An external MES is a "longer term vision" and out of scope. | [SOW B 6.4] verified |
| Restrictions (ITAR / citizenship) | not stated | – |
| Regulations (FDA, etc.) | not stated | – |
| Business objectives | Implement Oracle Cloud SCM for core functionality, future readiness and a common design across modules. Feed updates into the production Financials modules. Create a Reporting Strategy. | [SOW A] verified |
| Systems / functions replaced | Coupa is implied as the requisitioning/procurement source; whether it is retired is not stated. | [SOW B 3.5] partly verified (replacement not stated) |

## 2. Implementation Overview: modules in scope

FSCR catalog resolution used the classifier's exact-code rules. Pending items failed closed on purpose because the functional area belongs to more than one offering.

| # | SOW module / scope line | New or incremental | FSCR offering (pillar) | FSCR functional areas | Resolution | Basis |
|---|---|---|---|---|---|---|
| S1 | Product Information Management: items for maintainable equipment, assets, spare parts and manufactured product; manufacturing and maintenance structures | New | Product Management `PIM_PROD_MNG` (SCM) | Items `ORA_EGP_FA_ITEMS`, Structures `EGO_ADVANCED_PRODUCT_STRUCT`, Item Organizations `ORA_EGP_FA_ITEM_ORGANIZATIONS` | resolved | [SOW B 1.1–1.3], [FSCR] verified |
| S2 | Inventory & Cost Management: spare parts, bulk material, VMI and manufactured product; PO receiving, return to vendor, putaway; 2 plants as inventory orgs; cost org structure and cost books; costing for manufactured inventory, maintenance equipment and inventoried material | New | Manufacturing and Supply Chain Materials Management `ORA_MANUFACTURING_AND_SUPPLY_C` (SCM) | Facilities `ORA_RCS_FACILITIES`, Inventory Management `ORA_WSH_INVENTORY_MGMT`, Receiving `WSH_ENABLE_RECEIVING`, Cost Accounting `CST_DEFINE_COST_MANAGEMENT`, Receipt Accounting `CMR_RECEIPT_ACCOUNTING` | resolved | [SOW B 2.1–2.6], [FSCR] verified |
| S3 | Self-Service Procurement: non-catalog requisitions, inventory requisitions for maintenance and manufacturing, PO approvals (delegation of authority), project and non-project accounting rules for POs and receipts, reuse of Coupa values | New | Procurement `PO_PROCUREMENT` (SCM) | Self Service Procurement `PO_SSP_DEPLOYED`, Approval Management `ORA_PO_APPROVAL_MANAGEMENT_FA`, Procurement Transaction Account Rules `ORA_PO_PRC_TRX_ACC_RULES_FA` | resolved | [SOW B 3.1–3.5], [FSCR] verified |
| S4 | Purchasing: project and non-project requisitions and POs; delegation of authority | New | Procurement `PO_PROCUREMENT` (SCM) | Procurement Foundation `ORA_PO_PROC_FOUNDATION_FA`, Purchasing Foundation `ORA_PO_PURCHASING_FOUNDATION` | resolved | [SOW B 4.1–4.2], [FSCR] verified |
| S5 | Supplier Portal: supplier registration, P2P inquiry, supplier invoice creation, supplier self-maintenance. Twelve manages supplier onboarding. | New | Procurement `PO_PROCUREMENT` (SCM) | Supplier Portal `PO_SUP_PORTAL_DEPLOYED`, Suppliers `ORA_EGP_SUPPLIERS` | resolved | [SOW B 5.1–5.5], [FSCR] verified |
| S6 | Manufacturing, process-based only and "ready to use": structures, work definitions, work centers, work areas, operations; create, release and complete process work orders; issue materials and receive into inventory. No structures or work definitions configured or migrated. | New | Manufacturing and Supply Chain Materials Management (SCM) | Manufacturing Master Data `ORA_WIS_COMMON_MFG_WORK_SETUP` | resolved. Process vs discrete has no separate FA (catalog gap). | [SOW B 6.1–6.4], [FSCR] verified |
| S7 | Maintenance, "ready to use": maintainable assets and equipment, equipment structures, work definitions, work centers and areas, operations; maintenance work orders; meters; maintenance programs (preventive); Installed Base trackable. No assets or equipment configured or migrated. | New | Manufacturing and Supply Chain Materials Management (SCM) | Maintenance Management `ORA_MNT_MGMT` | resolved. No separate FA for meters or Installed Base (not verified). | [SOW B 7.1–7.7], [FSCR] verified |
| F1 | Project Cost Management: project commitments for requisitions and POs; receipts and AP invoices for project transactions | Incremental | Project Financial Management `PJF_PROJ_MNG` (ERP) | Project Costing Base `ORA_PJC_PROJ_COSTING_BASE_FA` | resolved | [SOW B Fin 1], [FSCR] verified |
| F2 | Asset Management: updates from AP and Project Management changes | Incremental | Financials `XLE_FINANCIALS_JUR` (ERP) | Fixed Assets `FIN_FIXED_ASSETS_DEPLOYED` | resolved | [SOW B Fin 2], [FSCR] verified |
| F3 | Confirm Enterprise (BU) Structure: requisitioning and purchasing BUs; centralized, decentralized and shared service | Incremental | ambiguous: in 9–10 offerings | Legal Structures, Financial Reporting Structures, Organization Structures | **pending** (fail-closed, needs human review) | [SOW B Fin 3], [FSCR] verified. See Output 2. |
| F4 | Sustainability: data from AP supplier invoices and manual file upload; seeded reports only; EPM-enabled reporting out of scope | New | ambiguous: MSCMM, PIM, Procurement | Sustainability `ORA_SUS_SUSTAINABILITY` | **pending** (fail-closed) | [SOW B Fin 4], [FSCR] verified |
| F5 | Expenses: T&E, approvals, project and non-project accounting rules. **Conditional**: a design session decides in or out. | Conditional new | Financials `XLE_FINANCIALS_JUR` (ERP) | Expenses `FIN_EXPENSES_DEPLOYED` | resolved (scope conditional) | [SOW B Fin 5.1–5.4], [FSCR] verified |
| F6 | Reporting approach: OTBI vs BIP vs Fusion Data Intelligence vs EPM; financial reporting for EPM Planning & Budgeting, month-end close, GL | New (strategy only) | Financials (partial: Financial Reporting Center `ORA_FIN_REPORT_CENTER`) | – | partial. No FSCR content for FDI or EPM. | [SOW B Fin 6], [FSCR] verified |
| F7 | General Ledger / SLA: support for accounting and journals from Inventory, Costing, Manufacturing, Maintenance, Purchasing, Expenses | Incremental | Financials `XLE_FINANCIALS_JUR` (ERP) | General Ledger `ORA_FIN_GENERAL_LEDGER` (+ Receipt Accounting, Cost Accounting above) | resolved | [SOW B Fin 7, Cfg 7], [FSCR] verified |
| F8 | Payables (incremental changes as needed) | Incremental | ambiguous: Financials or Procurement | Payables `FIN_PAYABLES_DEPLOYED` | **pending** (fail-closed) | [SOW Cfg 5], [FSCR] verified |
| F9 | Receivables, Cash Management, Grants Management: "in-scope for remediation"; extent "determined during the project" | Remediation, TBD | Financials / Grants Management | `FIN_RECEIVABLES_DEPLOYED` (resolved), `ORA_CE_CASH_MGMT_BANK` (**pending**), `ORA_GMS_GRANTS_BASE_FA` (resolved) | mixed | [SOW B Fin intro], [FSCR] verified |
| C12 | Security and Roles | New | ambiguous: 21 offerings | Users and Security `ORA_ASK_USERS_AND_SECURITY` | **pending** (fail-closed) | [SOW Cfg 12], [FSCR] verified |

**Resolved FSCR offerings (6):** Product Management, Manufacturing and Supply Chain Materials Management, Procurement (all SCM); Financials, Project Financial Management, Grants Management (all ERP). [FSCR] verified.
**Classifier totals:** 31 SOW-to-functional-area rows, 24 resolved, 7 pending with diagnostics. [FSCR] verified.

### Wording inconsistency in the SOW (verified)
- The Configurations Scope list (12 items) **does not include** Receivables, Cash Management, Fixed Assets, Grants or Expenses. The Financials section names AR, CE, FA and Grants as "in-scope … for remediation". Expenses appears only as conditional. → open question Q-S3.
- The Project Objective says "Product Management, Materials Management and Procurement Modules". Section B also adds Manufacturing, Maintenance and Sustainability.

## 3. Explicit exclusions (verified, SOW)
- Discrete Manufacturing [B 6.2]
- Integration with an MES [B 6.4]
- Configuring or migrating manufacturing structures and work definitions [B 6.1]
- Configuring or migrating maintenance assets and equipment [B 7.1]
- EPM-enabled sustainability reporting [B Fin 4.3]
- Extensions and integrations: "No extensions and integrations are part of the target scope" [B RICE 3]
- Supplier onboarding is done by Twelve [B 5.5]
- Change management, unless otherwise noted, is Twelve's [C.4]
- Migration of configurations to Production is done by Twelve [C.10]
- Travel [C.11]

## 4. Reports, Conversions, Extensions, Customizations (Scoping Checklist › Customizations & Custom Reports; Data Migration)

| Item | Answer | Basis |
|---|---|---|
| Custom reports | 1: Printable Purchase Order. Deliverables: FDD, TDD; code and unit test. | [SOW B RICE 1] verified |
| Checklist norm "GoSaaS typically includes 5" | SOW has 1. Noted as a difference, not a gap. | checklist, verified |
| Conversions | 1 object: Suppliers. Deliverables: FDD, TDD. | [SOW B RICE 2] verified |
| Data migration effort | "minimal". Required employees are in Production or onboarded after go-live. | [SOW C.5] verified |
| Supplier source system | not stated (Coupa is likely, not verified) | open Q-D1 |
| Supplier volume, history vs latest, delta | not stated | open Q-D2 |
| Extensions / customizations | none | [SOW B RICE 3] verified |
| Integrations | none. See Output 3. | [SOW B RICE 3] verified |

## 5. Configuration deliverables (verified, SOW "Configurations Scope")
Document configurations for: 1 PIM (new), 2 Self-Service Purchasing (new), 3 Purchasing (new), 4 Supplier Portal (new), 5 Payables (incremental), 6 Inventory & Cost Management (new), 7 GL/SLA (incremental), 8 Project Management (incremental), 9 Sustainability (new), 10 Maintenance (new), 11 Manufacturing (new), 12 Security and Roles.
Per module, also: Business Scenarios, Requirements, Process Flows, Key Design Decisions, Configuration Templates [SOW B]. Training material for new modules; Train-the-Trainer [SOW B Change Mgmt, C.6].

## 6. Commercials and resourcing (verified, SOW §D)
- Duration: 12 weeks [C.8]. Time and materials, billed monthly. Total **$360,300** (Finance $83,700 / Supply Chain $276,600).
- Roles and hours: Finance Architect 140, SCM Architect 640, Reporting Architect 80, Inventory Consultant 560, PMO Analyst 320, DEV Consultant 280, Finance Consultant 280, Mfg/Maintenance Consultant 560, Procurement Consultant 560, PIM 400. Total 3,820 hours (computed by Claude from the table; arithmetic verified: 140+640+80+560+320+280+280+560+560+400 = 3,820).
- Estimate does not include productive Twelve effort [C.1]. Twelve appoints a project lead with decision authority [E.9].

## 7. Planning (Scoping Checklist › Planning; Methodology; Pre-sales Timeline)

| Checklist item | Answer | Basis |
|---|---|---|
| Number of environments | **SUGGESTED (checklist):** 3 (Dev / Test / Production), "recommended". The SOW mentions only "development and production platforms" [E.6]. | not verified → Q-P1 |
| Test environments | **SUGGESTED (checklist):** 2 test environments "unless the implementation is small". With only 1, add 1–2 weeks between test cycles. | not verified → Q-P2 |
| Configuration design workshops | **SUGGESTED (checklist):** 1 week per module, 8am–noon PST. Applied to the 11 configured modules plus security, that is about 12 workshop-weeks, run in parallel streams. | not verified → Q-P3 |
| Other workshops | **SUGGESTED (checklist):** Data Migration 1 week (supplier conversion), Reports 1 week (PO print), Security 1 week, Sign-off 1 week. Integrations 0, since there are none. | not verified → Q-P3 |
| Test cycles | **SUGGESTED (checklist):** CRP1 (partial data, 2 wks), CRP2 (full data, 2 wks), CRP3 (mock migration), UAT (2 wks), Go-Live cutover (1 wk), with about 7 weeks of work between cycles. | not verified → Q-P4 |
| **Timeline risk** | The checklist cycle model alone (~9 weeks of test and cutover plus ~7 weeks between cycles) exceeds the SOW's 12 weeks. The SOW calls the plan "aggressive". A reduced cycle plan is needed, for example CRP1 + CRP2 + UAT with minimal data, since only suppliers are converted. | Claude analysis, not verified → Q-P4 |
| Go-live criteria | "Go-Live & Ready to Use criteria will be refined during the project" | [SOW C.2.1] verified |
| Roll-out approach | Common design for all modules, positioned for future location-specific phase roll-outs | [SOW C.3] verified |
| Quarter-end or freeze periods | not stated. Checklist asks: "What are the quarter end months? Is there a quarter end freeze". | open Q-P5 |
| Oracle update schedule | **SUGGESTED (checklist):** open SRs to get the update schedule and build an instance plan so updates do not hit milestones. | not verified → Q-P6 |
| Decision owner / process | Twelve project lead has decision authority. | [SOW E.9] verified |
| Other Oracle Cloud projects running | not stated. Production Financials exists. | open Q-P7 |
| Post go-live / hypercare | not stated | open Q-P8 |

## 8. Project Management (PM Checklist, Pre-implementation Checklist)
**SUGGESTED (checklist), none verified:** high-level plan in MS Project from the SOW; kickoff deck and meeting; client contact list; weekly client and internal meetings; workshop and training plan with names; offshore access to the Oracle environment and SRs; meeting-minutes template; budget tracker and Harvest; Oracle Support identifier and admin access with a backup; environment list. Integration access requirements document: **not applicable**, since there are no integrations.
Verified from the SOW: Twelve provides remote access to development and production [E.6, E.7] and reference information [E.2]. Twelve also migrates approved configurations to Production [C.10].

## 9. Open questions (each needs a person to confirm)

| ID | Question | Suggested answer (label) |
|---|---|---|
| Q-S1 | Is Expenses in or out of scope after the design session? | none. Decided by the SOW design session. |
| Q-S2 | Which production Financials modules need actual configuration changes? The SOW says "determined during the project". | none |
| Q-S3 | Are AR, Cash Management, Fixed Assets and Grants in the configuration-documentation deliverable even though Configurations Scope omits them? | SUGGESTED (Claude): document only if changed |
| Q-S4 | Which FSCR offering owns Sustainability, Payables, Cash Management, Security and the Enterprise Structure FAs (classifier pending)? | SUGGESTED (Claude): Sustainability → MSCMM; Payables and CE → Financials; ES and Security → Financials |
| Q-S5 | Industry, revenue, user counts, ITAR or FDA restrictions? | none |
| Q-S6 | Will Coupa be retired at go-live? | none |
| Q-D1 | What is the source of the supplier conversion (Coupa or Oracle Payables suppliers already in production)? | none |
| Q-D2 | Supplier volume; active only or all; delta load at cutover? | SUGGESTED (checklist): plan a delta migration if cutover is not frozen |
| Q-P1 | How many environments? | SUGGESTED (checklist): 3 (Dev/Test/Prod) |
| Q-P2 | How many test environments? | SUGGESTED (checklist): 2 |
| Q-P3 | Workshop plan and durations? | SUGGESTED (checklist): 1 wk/module plus DM, Reports, Security, Sign-off 1 wk each |
| Q-P4 | Which test cycles fit in 12 weeks? | SUGGESTED (checklist), compressed: CRP1, CRP2, UAT |
| Q-P5 | Quarter-end months and freeze periods? | none |
| Q-P6 | Oracle quarterly update dates vs milestones? | SUGGESTED (checklist): open SR and build an instance plan |
| Q-P7 | Any other Oracle Cloud projects running in parallel on the same pod? | none |
| Q-P8 | Hypercare length and support model? | none |
| Q-P9 | Who is GoSaaS's PM contact? Who is Twelve's project lead? | none (Twelve signatory is Maisie Luce, Head of IT; project lead not named) |
