# Output 1 — Project scope intake (from the SOW only)

Source: `sow/50513 - Twelve - Oracle Cloud SCM Implementation SOW v4_Twelve-signed_GS signed.pdf`, extracted to `sow/sow_text.txt`. The SOW is dated 24 Jan 2025, signed 28 Jan 2025 by both parties, document number 50513scm.
FSCR skills: `router.project-objective-classifier` (offering resolution against `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`), `shared.project-intake.implementation-scope-intake`, `shared.project-intake.scope-definition`.
Who produced it: **FSCR + Claude**. The classifier and catalog gave the offering and functional-area codes and the artifact locations. The intake skill gave only output names (`recommendations`, `work_products`, `review_points`). I wrote all the content.
Tags: [V] = stated in the SOW or checked against the catalog file. [NV] = my interpretation.

## 1. Objective [V]
Implement Oracle Cloud SCM modules to support key financial and supply chain processes, focusing on core functionality, future readiness and **a common design across modules**. Give input into updates of the **production** Financials modules that integrate natively with the new SCM modules. Create a **Reporting Strategy**. GoSaaS also documents configurations for the modules.

Implication [NV]: Financials is already live in a production pod (the SOW says "production Financials modules" and "existing Business Unit Structure"). This is an SCM expansion on an existing Fusion tenancy, not a greenfield.

## 2. Classification (classifier format)

| Field | Value | Tag |
|---|---|---|
| Customer | Twelve Benefit Corporation | V |
| Pillars | SCM (primary), ERP (Financials and Projects remediation) | V for the pillars named; NV for primary vs secondary |
| Geography | 1 country (US) | V (Assumption 7) |
| Sites | 2 plant locations | V (Assumption 7) |
| Industry | not recorded (the SOW does not say) | — |
| Phase | discovery / design (SOW signed, project not started) | NV |
| Delivery approach | Common design for all modules, so future location-specific phase rollouts can follow | V (Assumption 3) |
| Duration | 12 weeks | V (Assumption 8) |
| Effort | 3,820 hours across 10 roles (Finance 140, SCM 640, Reporting 80, Inventory 560, PMO 320, DEV 280, Finance consultant 280, Mfg/Maintenance 560, Procurement 560, PIM 400). Total value split in the SOW: Finance $83,700 / Supply Chain $276,600; T&M, billed monthly | V (summed from the cost table) |

### 2.1 Offering and functional-area resolution (classifier rule: exact names or codes only)

| SOW wording | Candidate offering (code) | Candidate functional area (code) | Resolved? |
|---|---|---|---|
| Product Information Management Module | Product Management (`PIM_PROD_MNG`)? | Items `ORA_EGP_FA_ITEMS` (in 6 offerings), Structures `EGO_ADVANCED_PRODUCT_STRUCT` (2) | **No.** "Product Information Management" is not an exact offering name, so the classifier stops (rule 4/5) [V] |
| Inventory and Cost Management Module | Manufacturing and Supply Chain Materials Management (`ORA_MANUFACTURING_AND_SUPPLY_C`) | Inventory Management `ORA_WSH_INVENTORY_MGMT` (1 offering), Cost Accounting `CST_DEFINE_COST_MANAGEMENT` (1), Receiving `WSH_ENABLE_RECEIVING` (2), Receipt Accounting `CMR_RECEIPT_ACCOUNTING` (2), Facilities `ORA_RCS_FACILITIES` (1) | Functional areas with one owner resolve; the offering is not named exactly [V] |
| Self-Service Procurement | Procurement (`PO_PROCUREMENT`) | Self Service Procurement `PO_SSP_DEPLOYED` (1) | Unique functional area; offering inferred [V for uniqueness] |
| Purchasing | Procurement (`PO_PROCUREMENT`) | Purchasing Foundation `ORA_PO_PURCHASING_FOUNDATION` (1), Approval Management `ORA_PO_APPROVAL_MANAGEMENT_FA` (1), Procurement Transaction Account Rules `ORA_PO_PRC_TRX_ACC_RULES_FA` (1) | Unique functional areas [V] |
| Supplier Portal | Procurement or Product Management | Supplier Portal `PO_SUP_PORTAL_DEPLOYED` (2 offerings) | **Ambiguous** — the classifier fails closed [V] |
| Manufacturing (process only) | `ORA_MANUFACTURING_AND_SUPPLY_C` | Manufacturing Master Data `ORA_WIS_COMMON_MFG_WORK_SETUP` (1) | Unique functional area [V]. No separate process-manufacturing functional area in the catalog [V] |
| Maintenance | `ORA_MANUFACTURING_AND_SUPPLY_C` | Maintenance Management `ORA_MNT_MGMT` (1) | Unique functional area [V] |
| Sustainability | 3 candidate offerings | Sustainability `ORA_SUS_SUSTAINABILITY` (MSCMM, Product Mgmt, Procurement) | **Ambiguous** [V] |
| Expenses (TBD) | Financials (`XLE_FINANCIALS_JUR`) | Expenses `FIN_EXPENSES_DEPLOYED` (1) | Unique; scope conditional [V] |
| GL / SLA (incremental) | Financials | General Ledger `ORA_FIN_GENERAL_LEDGER` (Financials, Accounting Hub) | Ambiguous between 2 [V] |
| Payables, Cash Mgmt (incremental) | Financials or Procurement | `FIN_PAYABLES_DEPLOYED` (3), `ORA_CE_CASH_MGMT_BANK` (3) | Ambiguous [V] |
| Receivables, Fixed Assets | Financials | `FIN_RECEIVABLES_DEPLOYED` (2), `FIN_FIXED_ASSETS_DEPLOYED` (1) | FA resolves; AR ambiguous [V] |
| Project Management / Project Cost | Project Financial Management (`PJF_PROJ_MNG`) | Project Costing Base `ORA_PJC_PROJ_COSTING_BASE_FA` (2) | Ambiguous with Grants [V] |
| Grants Management | Grants Management (`ORA_GMS_GRANTS_MANAGEMENT`) | Grants Management Foundation `ORA_GMS_GRANTS_BASE_FA` (1) | Resolves [V] |
| Reporting approach (OTBI, BIP, FDI, EPM) | no offering | no functional area | Not catalogued [V] |
| Security and Roles | many | Users and Security `ORA_ASK_USERS_AND_SECURITY` (21 offerings) | Ambiguous [V] |

**Result:** following the classifier's own rules, `offering_scope` = **pending**. FSCR would stop and ask for offering short codes (see RUN_REPORT §3). [V]

## 3. In scope [V unless marked]

**SCM — new configuration** ("Configurations Scope" list):
1. Product Information Management: items for maintainable equipment, assets and spare parts; items for manufactured product; enable manufacturing and maintenance structures.
2. Inventory & Cost Management: inventoriable items (spares, bulk, VMI, manufactured); receiving against PO, return to vendor, putaway; **current plant locations as Inventory Organizations**; **Costing Organization structure and Cost Books**; costing for manufactured inventory, maintenance equipment and inventoried material.
3. Self-Service Procurement: non-catalog requisitions; requisitions for inventory materials (maintenance, manufacturing); PO approval delegation of authority; project and non-project accounting rules for POs and receipts; reuse Coupa configuration values and concepts where applicable.
4. Purchasing: project and non-project requisitions and POs; delegation of authority.
5. Supplier Portal: supplier registration; procure-to-pay inquiry; supplier invoice creation; supplier self-maintenance. Supplier onboarding is done by Twelve.
6. Manufacturing: "ready to use" — create structures, work definitions, work centers, work areas, operations; create, release and complete **process** work orders; issue and receive materials.
7. Maintenance: "ready to use" — maintainable assets and equipment, equipment structures, work definitions, work centers, work areas, operations; maintenance work orders; meters; maintenance programs (preventive); Installed Base trackable.
8. Sustainability (new): data from Payables supplier invoices and manual file upload; native seeded reporting.
9. Security and Roles.

**Financials / Projects — remediation (incremental, "to be determined during the project"):** GL/SLA, AR, Project Management, Grants Management, AP, Cash Management, Fixed Assets.
- Project Cost Management: project commitments for requisitions and POs; PO receipts and AP invoices for project transactions.
- Asset Management: updates to AP and Projects caused by the new SCM and Expenses modules.
- **Confirm the Enterprise (BU) Structure:** add Requisitioning and Purchasing BUs to the existing BU structure; consider centralized/decentralized and shared-service processes.
- GL: support with accounting and journal flow from Inventory, Costing, Manufacturing, Maintenance, Purchasing and Expenses.
- Expenses: conditional on a design session; if in scope, T&E, approvals, and project/non-project accounting rules.
- Reporting Approach: future use of OTBI / BIP / FDI / EPM; financial reporting for EPM Planning & Budgeting, month-end close, GL reporting.

**RICE:**
- Reports: 1 — printable Purchase Order (FDD, TDD, build, unit test).
- Conversions: 1 object — Suppliers (FDD, TDD).
- Extensions: none. Integrations: none ("No extensions and integrations are part of the target scope").

**Deliverables per module** (stated): business scenarios, requirements, process flows, key design decisions (KDDs), configuration templates.

**Change management:** training material for new modules; Train-the-Trainer.

## 4. Explicitly out of scope [V]
- Discrete manufacturing.
- MES integration (a longer-term vision only).
- Configuring or migrating manufacturing structures and work definitions; configuring or migrating maintenance assets and equipment.
- EPM-enabled sustainability reporting.
- Extensions and integrations.
- Organizational change management (Twelve manages it, unless noted).
- Moving configuration to Production (Twelve does this).
- Travel (excluded from cost).

## 5. Assumptions and constraints [V]
- GoSaaS estimate excludes Twelve's own effort.
- "Ready to Use" positioning; go-live and ready-to-use criteria to be refined during the project.
- Minimal data migration; required employees already in Production or onboarded post go-live.
- "Aggressive plan": fast decisions and sign-offs needed; out-of-scope items become addendums.
- Client responsibilities: timely decisions, testing, data in agreed format, access to dev and production platforms, a project lead with decision authority, reference calls and case studies.

## 6. Open questions (the SOW does not state these — not invented)
| # | Question | Why it matters |
|---|---|---|
| S1 | Which Fusion offerings and short codes are to be enabled? (product names in the SOW do not match catalog names exactly) | Classifier gate; FSCR stops here |
| S2 | Number of environments (pods) and their roles (Dev / Test / Prod); is Production already live for Financials? | Not stated; needed for an instance plan |
| S3 | Oracle quarterly update cohort and current release | Not stated |
| S4 | Number of users by role (requesters, buyers, receivers, planners, technicians, approvers) | Not stated |
| S5 | Is Expenses in or out? (design-session decision) | Conditional scope |
| S6 | Which Financials changes are needed? ("to be determined during the project") | Open-ended remediation scope |
| S7 | Number of CRP, SIT and UAT cycles and test approach | Not stated |
| S8 | Go-live date, cutover window and freeze periods (quarter end) | Only "12 weeks" is stated |
| S9 | Data volumes for the Supplier conversion; other data needs ("minimal") | Not stated |
| S10 | Coupa: which configuration values to reuse? Does Coupa stay live (coexistence)? | Coupa named but its role is unclear |
| S11 | Approval hierarchy source (supervisor / position / job) and DOA limits | Delegation of authority named, rules not given |
| S12 | Security: role list, segregation of duties, data access by BU or org | "Security and Roles" named only |
| S13 | Reporting approach: are FDI and EPM licensed? | Listed as options only |
| S14 | Maintenance: number of assets and meters (none are migrated) | Sizing |
| S15 | Industry / regulatory needs (e.g. lot or serial control for process manufacturing) | Not stated |
| S16 | Go-live and "Ready to Use" acceptance criteria | SOW says they will be refined |
| S17 | Twelve project lead and decision owners per area | Named as a responsibility only |
