# Output 1 — Project Scope (Twelve, Oracle Cloud SCM Implementation)

Source: SOW "Twelve - Oracle Cloud SCM Implementation SOW", dated January 24, 2025, signed January 28, 2025, Document Number 50513scm (copy at `sow/SOW.pdf`, text at `sow/SOW.txt`).
Built under FSCR skills: `router.project-objective-classifier` (offering resolution), `shared.project-intake.implementation-scope-intake` and `shared.project-intake.scope-definition` (section headings: confirmed scope, assumptions, exclusions). Those two intake skills are generic stubs with no questions or template, so Claude filled every row from the SOW.

Legend: **V** = verified against the SOW text (section given). **NV** = not verified (Claude's reading or inference; must be confirmed). "not recorded" = the SOW does not say.

Status: **DRAFT, not confirmed.** `scope-definition` runs in `assisted` mode and expects the customer to confirm the scope. That confirmation has not happened.

## 1. Project header

| Item | Value | Status |
|---|---|---|
| Customer | Twelve Benefit Corporation ("Twelve") | V (preamble) |
| Implementer | GoSaaS, Inc. | V (preamble) |
| Signatories | Maisie Luce, Head of IT (Twelve); Meghan Dey, Partner, Head of Revenue (GoSaaS) | V (signature block) |
| Objective | Implement Oracle Cloud SCM modules for core functionality, future readiness and a common design across modules. Provide input on updates to the production Financials modules natively integrated with SCM. Create a Reporting Strategy. | V (A) |
| Duration | 12 weeks | V (C.8) |
| Start date / go-live date | not recorded. Work starts when GoSaaS receives the client-signed SOW. | V (preamble) |
| Countries | 1 (US) | V (C.7) |
| Plant locations | 2 | V (C.7) |
| Delivery approach | Common Design for all modules. Future location-specific phases. | V (C.3) |
| Commercials | Time and materials, billed monthly. Total $360,300; Finance $83,700; Supply Chain $276,600. | V (D) |
| Estimated hours | **3,820** (sum of the role table: 140+640+80+560+320+280+280+560+560+400) | V (D, arithmetic checked) |
| Implementation phase (FSCR) | discovery | NV (FSCR template default) |

### Effort by role (SOW D)

| Role | Rate | Hours | Subtotal |
|---|---|---|---|
| Finance Architect | $225 | 140 | $31,500 |
| SCM Architect | $225 | 640 | $144,000 |
| Reporting Architect | $225 | 80 | $18,000 |
| Inventory Consultant | $45 | 560 | $25,200 |
| PMO Analyst | $150 | 320 | $48,000 |
| DEV Consultant | $45 | 280 | $12,600 |
| Finance Consultant | $45 | 280 | $12,600 |
| Manufacturing / Maintenance Consultant | $45 | 560 | $25,200 |
| Procurement Consultant | $45 | 560 | $25,200 |
| Product Information Management | $45 | 400 | $18,000 |
| **Total** | | **3,820** | **$360,300** |
All rows V (D).

## 2. In-scope modules: new SCM implementation

| # | SOW module | Scope items (SOW numbering) | Status |
|---|---|---|---|
| 1 | Product Information Management | 1.1 items for maintainable equipment, assets and spare parts; 1.2 items for manufactured product; 1.3 ability to create manufacturing and maintenance structures | V (B, SCM 1) |
| 2 | Inventory and Cost Management | 2.1 inventoriable items (spare parts, bulk material, vendor managed inventory, manufactured product), receiving against POs, return to vendor, putaway; 2.2 current plant locations as Inventory Organizations; 2.3 costing organization structure and cost books; 2.4–2.6 costing for manufactured inventory, maintenance equipment, inventoried material | V (B, SCM 2) |
| 3 | Self-Service Procurement | 3.1 non-catalog requisitioning; 3.2 requisitioning for inventory materials for maintenance and manufacturing; 3.3 PO delegation of authority (approvals); 3.4 project and non-project accounting rules for POs and receipts; 3.5 reuse configuration values and concepts from Coupa where applicable | V (B, SCM 3) |
| 4 | Purchasing | 4.1 project and non-project requisitions and POs; 4.2 delegation of authority for requisitions and POs | V (B, SCM 4) |
| 5 | Supplier Portal | 5.1 supplier registration; 5.2 procure-to-pay inquiry; 5.3 supplier invoice creation; 5.4 supplier self-maintenance; 5.5 Twelve manages supplier onboarding | V (B, SCM 5) |
| 6 | Manufacturing (process only) | 6.1 "ready to use": create structures, work definitions, work centers, work areas, operations; validate create, release and complete of process work orders; 6.2 process manufacturing only; 6.3 enable work definitions etc.; 6.4 manual release and complete, material issue and receipt | V (B, SCM 6) |
| 7 | Maintenance | 7.1 "ready to use": assets, equipment, equipment structures, work definitions, work centers, work areas, operations; validate maintenance work orders; 7.2–7.7 equipment and structures, maintenance work definitions, repair and replace work orders, meters, maintenance programs (preventive), Installed Base trackable | V (B, SCM 7) |
| 8 | Supply Chain Sustainability | Financials 4.1 data from Payables supplier invoices and manual file upload; 4.2 native seeded Sustainability reporting | V (B, Financials 4) |

## 3. In-scope modules: Financials remediation and other items

| # | Area | Scope items | Status |
|---|---|---|---|
| 9 | Financials remediation: GL, AR, Project Management, Grants Management, AP, Cash Management, Fixed Assets | Remediation needed because of the new SCM and Expenses modules. **What changes in production Financials is to be decided during the project.** | V (B, Financials intro) |
| 10 | Project Cost Management | 1.1 project commitments for requisitions and POs; 1.2 PO receipts and AP invoices for project transactions | V (B, Fin 1) |
| 11 | Asset Management | 2.1 changes to AP and Project Management caused by the new SCM and Expenses modules | V (B, Fin 2) |
| 12 | Enterprise (Business Unit) structure | 3.1 add Requisitioning and Purchasing BUs to the existing BU structure; 3.2 consider centralized, decentralized and shared-service processes | V (B, Fin 3). See Output 2 |
| 13 | Expenses (**conditional**) | 5.1 a design session decides in or out of scope. If in: 5.2 employee travel and entertainment; 5.3 expense report approvals; 5.4 project and non-project accounting rules | V (B, Fin 5) |
| 14 | Reporting Approach | 6.1 future use of OTBI, BIP, Fusion Data Intelligence, EPM; 6.2 financial reporting for EPM Planning & Budgeting, month-end close, GL reporting | V (B, Fin 6) |
| 15 | General Ledger support | 7.1 support on accounting and journal entries from Inventory, Costing, Manufacturing, Maintenance, Purchasing, Expenses | V (B, Fin 7) |

## 4. RICE scope

| Type | Objects | Deliverables | Status |
|---|---|---|---|
| Reports | 1: Printable Purchase Order | Functional Design, Technical Design (plus code and unit test) | V (B, RICE 1) |
| Conversions | 1: Suppliers | Functional Design, Technical Design | V (B, RICE 2) |
| Integrations | **0** | none | V (B, RICE 3) |
| Extensions | **0** | none | V (B, RICE 3) |

## 5. Configuration documentation scope (SOW "Configurations Scope")

New: Product Information Management; Self-Service Purchasing; Purchasing; Supplier Portal; Inventory & Cost Management; Sustainability; Maintenance; Manufacturing.
Incremental changes as needed: Payables; General Ledger / Subledger Accounting; Project Management.
Also listed: Security and Roles. — all V (B, Configurations Scope)

Documentation deliverables for each module: Business Scenarios, Requirements, Process Flows, Key Design Decisions, Configuration Templates. — V (B, both scope intros)

## 6. Change management and training

- GoSaaS creates training material for the new modules and uses Train-the-Trainer. — V (B, Change Management; C.6)
- Twelve owns all other change management unless stated otherwise. — V (C.4)

## 7. Exclusions (stated out of scope)

| Exclusion | Status |
|---|---|
| Discrete manufacturing | V (6.2) |
| Configuring or migrating manufacturing structures or work definitions | V (6.1) |
| Integration with an MES (only a long-term vision is in scope) | V (6.4) |
| Configuring or migrating maintenance assets or equipment | V (7.1) |
| EPM-enabled sustainability reporting | V (Fin 4.3) |
| Extensions and integrations | V (RICE 3) |
| Travel (if needed, billed outside project costs) | V (C.11) |
| Migrating approved configurations to Production (Twelve does this) | V (C.10) |
| Productive effort from Twelve resources (not in the estimate) | V (C.1) |
| Supplier onboarding (Twelve manages it) | V (5.5) |

## 8. Assumptions (SOW C, restated)

Minimal data migration; required employees are already in Production or can be onboarded after go-live (C.5, 5.1). Go-live and ready-to-use criteria are refined during the project (C.2.1). Changes in complexity or duration can change cost (C.9). — V

## 9. FSCR classifier result (offering scope)

Rule applied: the classifier matches offering names exactly against `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json` and leaves an offering pending when there is no match or more than one candidate. It does not allow partial-name matching. The script output is in `work/classifier_offering_resolution.json`.

| SOW term | FSCR result | Candidate codes | Status |
|---|---|---|---|
| Product Management | resolved: `PIM_PROD_MNG` | — | V (catalog) |
| Procurement | resolved: `PO_PROCUREMENT` | — | V (catalog) |
| Grants Management | resolved: `ORA_GMS_GRANTS_MANAGEMENT` | — | V (catalog) |
| Fixed Assets | functional area `FIN_FIXED_ASSETS_DEPLOYED`, only one offering (`XLE_FINANCIALS_JUR`) | — | V (catalog) |
| Expenses | functional area `FIN_EXPENSES_DEPLOYED`, only one offering (`XLE_FINANCIALS_JUR`) | — | V (catalog) |
| Supplier Portal | **pending**: functional area in two offerings | PIM_PROD_MNG, PO_PROCUREMENT | V (catalog) |
| General Ledger | **pending** | XLE_FINANCIALS_JUR, XLE_FIN_CONTROL_JUR | V (catalog) |
| Cash Management | **pending** | ORA_STUDENT_MANAGEMENT, XLE_FINANCIALS_JUR, PO_PROCUREMENT | V (catalog) |
| Payables | **pending** | ORA_STUDENT_MANAGEMENT, XLE_FINANCIALS_JUR, PO_PROCUREMENT | V (catalog) |
| Sustainability | **pending** | ORA_MANUFACTURING_AND_SUPPLY_C, PIM_PROD_MNG, PO_PROCUREMENT | V (catalog) |
| Product Information Management, Inventory and Cost Management, Self-Service Procurement, Purchasing, Manufacturing, Maintenance, Accounts Receivable, Project Management, Accounts Payable, Project Cost Management, Asset Management, Subledger Accounting, Security and Roles | **pending: no exact match** | — | V (catalog) |

Claude's reading (NV; exact-match rules prevent FSCR from choosing these): Inventory, Cost, Manufacturing and Maintenance most likely map to `ORA_MANUFACTURING_AND_SUPPLY_C` (functional areas include ORA_WSH_INVENTORY_MGMT, CST_DEFINE_COST_MANAGEMENT, ORA_WIS_COMMON_MFG_WORK_SETUP, ORA_MNT_MGMT). Self-Service Procurement and Purchasing most likely map to `PO_PROCUREMENT` (PO_SSP_DEPLOYED, ORA_PO_PURCHASING_FOUNDATION). Project Management and Project Cost Management most likely map to `PJF_PROJ_MNG`. All of these need human confirmation.

## 10. Open questions (the SOW does not state these)

| # | Question |
|---|---|
| S1 | Start date, go-live date and milestone or phase dates. Only the 12-week duration is stated. |
| S2 | Number and type of Oracle environments or pods. The SOW mentions only "development and production platforms" (E.6). |
| S3 | Number of users and named-user licence counts by module |
| S4 | Is Expenses in or out of scope? The SOW leaves this to the design session (Fin 5.1). |
| S5 | Which specific changes are needed in production Financials (GL, AR, PM, Grants, AP, CM, FA)? The SOW says "to be determined" during the project. |
| S6 | Test phases (SIT, UAT), test cycles and who executes them. The SOW names only "testing functionality" as a Twelve responsibility (E.1). |
| S7 | Cutover and hypercare or post-go-live support duration |
| S8 | Oracle release or update cadence the project targets |
| S9 | Twelve project lead's name. E.9 requires one but does not name them. |
| S10 | Detailed go-live and "ready to use" criteria. The SOW says these are refined during the project (C.2.1). |
| S11 | Exact FSCR offering codes for each SOW module (see section 9, pending rows) |
| S12 | Supplier conversion: source system, record volume and number of load cycles |
| S13 | Number of training sessions and trainers (Train-the-Trainer is stated; quantities are not) |
| S14 | Security: number of roles, custom roles and approval hierarchies |
| S15 | Coupa (3.5): which configuration values are reused, and is Coupa being retired? |
