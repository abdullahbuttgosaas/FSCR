# Output 3: Task Dependencies (Project Planning, high-level)

**Project:** Twelve Benefit Corporation: Oracle Cloud SCM Implementation (SOW dated Jan 24, 2025, Doc 50513scm)
**Produced by:** FSCR + Claude.
- **FSCR** supplied (a) setup-object dependencies from the pillar task skills' `ora-resource/ora_dependency_readiness.md` files (161 in-scope files scanned by `work/extract_deps.py`, extract in `work/fscr_dependency_extract.txt`), and (b) the within-offering task order of the effective catalog (functional-area order × `displaySequence`), used as the Resolver Sequence in Output 1.
- **Claude** added project-level dependencies (design, data, environments, decisions, SOW responsibilities) that FSCR does not model. FSCR's `task-dependency-resolver` is a method description (no script); its dependency-graph enrichment has only `knowledge/dependency-graphs/hcm-dependency-graph.json`, so it adds nothing for SCM/ERP (verified: only that one file exists).
**Status:** Planning only. Nothing configured, no Fusion calls.

**Labels:** **verified** = checked against the cited file or SOW text in this run. **not verified** = Claude judgement, needs a person. Paths below are relative to `fscr-main/` (repo copy in this run folder).

---

## A. Setup-object dependencies from FSCR pillar dependency files (FSCR)

Each row quotes the dependency as written in the FSCR file (shortened). All are **verified** as present in the file; whether they apply to Twelve's design is **not verified**.

| # | Predecessor → Successor | What FSCR says | Twelve relevance | Source (FSCR file, `…/ora-resource/ora_dependency_readiness.md`) |
|---|---|---|---|---|
| D1 | Legal entity → Cost organization | "Define the legal entity before creating the cost organization." | Cost org for the 2 plants (SOW B 2.3) needs the existing US LE (Output 2, Q-E2). | `pillars/scm/manufacturing-and-supply-chain-materials-management/cost-accounting/cost-organizations` |
| D2 | Cost organization → Cost organization relationships (inventory orgs, cost books) | "Define the Cost Organization before associating inventory organizations or cost books." Item validation org must be "in the same legal entity as the Cost Organization". | Both plant inventory orgs and the item master must share the cost org's LE. | `…/cost-accounting/cost-organization-relationships` |
| D3 | Primary ledger → Cost book association | "Associate at least one Cost Book with the primary ledger of the Cost Organization legal entity." | Uses the existing production ledger (live Financials). | `…/cost-accounting/cost-organization-relationships` |
| D4 | Profit Center Business Unit → Inventory organization in cost org | "Confirm each inventory organization has a Profit Center Business Unit, shares the Cost Organization legal entity and item master organization." | BU decision (Output 2 Option A/B, Q-E4) must precede inventory org setup. | `…/cost-accounting/cost-organization-relationships` |
| D5 | Cost organization → Cost book → Default cost profiles | "Resolve the specified cost organization before resolving a cost book or a type-specific cost profile." | Costing for manufactured, maintenance and inventoried material (SOW B 2.4–2.6). | `…/cost-accounting/default-cost-profiles` |
| D6 | Cost organization + cost book + costing-enabled item → Item cost profiles | "Validate one exact Cost Organization … before validating the Cost Book, Item, and Cost Profiles." | Items (PIM) must exist and be costing-enabled first. | `…/cost-accounting/item-cost-profiles` |
| D7 | Reference data set → Business unit → BU business functions → Service provider relationships | Manage Business Unit needs the reference data set; Assign BU Business Function needs the BU and, for financial functions, its primary ledger and legal entity; Service Provider Relationships need both BUs. | Adding Requisitioning/Procurement functions to the existing BU (SOW Fin 3.1); service provider only if centralized (Fin 3.2). | `pillars/erp/financials/organization-structures` |
| D8 | Inventory organization → Manufacturing work areas | "Confirm that the target organization exists … before creating or updating a work area." | Plant inventory orgs (SOW B 2.2) before Mfg/Maint work areas (B 6.3, 7.3). | `…/manufacturing-master-data/manufacturing-work-areas` |
| D9 | Work area → Work center | Work center create resolves "the active Work Areas row from OrganizationCode and … WorkAreaCode". | SOW B 6.3 / 7.3 "Work Centers, Work Areas". | `…/manufacturing-master-data/manufacturing-work-centers` |
| D10 | Organization access + work center → Manufacturing resources | "The authenticated user must have access to the resource organization"; "A primary work center must be assigned to the parent resource". | Data access setup (security) before resources. | `…/manufacturing-master-data/manufacturing-resources` |
| D11 | Maintenance-enabled org + asset item → Maintenance work orders / programs | "The contextual organization must be maintenance-enabled"; work orders need "inventory organization access and the asset source item enabled"; cross-org programs need work definitions duplicated. | SOW B 7.1–7.6: validate create/release/complete maintenance work orders and maintenance programs. | `…/maintenance-management/manage-maintenance-organization-relationships` |
| D12 | Business unit + inventory org → Inventory business events | "Ensure the business unit and the inventory organization … already exist." | Only if inventory business events are used (not stated). | `…/inventory-management/inventory-business-event-configurations` |
| D13 | Procurement offering opt-in + implementation role + DFF deployment → Purchasing line types | "Opt in to Procurement … before implementing Procurement setup"; "Deploy the required descriptive-flexfield context … before supplying DFF values." | Offering opt-in is the first Procurement build step. | `pillars/scm/procurement/procurement-foundation/manage-purchasing-line-types` |
| D14 | Ledger + COA + account combinations → Asset categories | "Resolve the selected book ledger, COA, Natural Account … before populating an account role." | FA updates from AP/Projects (SOW Fin 2) and maintainable assets. | `pillars/erp/financials/fixed-assets/manage-asset-categories` |
| D15 | Ledger, LE, currency, calendar → Project accounting business function | "Ledger, legal entity, currency, and accounting calendar ready …" | Project-based POs/receipts (SOW B 3.4, Fin 1). Already live in Prod; check only. | `pillars/erp/project-financial-management/project-organizations/configure-project-accounting-business-function` |
| D16 | Cost element set → Cost elements | "Resolve one existing Cost Element Set name to SetId." | Cost elements for the cost books. | `…/cost-accounting/cost-elements` |

## B. Task order from the FSCR effective catalog (FSCR alone)

| # | Dependency | Source | Status |
|---|---|---|---|
| D17 | Within each offering, functional areas follow the catalog `functionalAreaOrder`; e.g. Manufacturing and Supply Chain Materials Management: Facilities → Inventory Management → Receiving → Receipt Accounting → Cost Accounting → Manufacturing Master Data → Maintenance Management → Sustainability. Within each FA, tasks follow `displaySequence`. This order is the Resolver Sequence in Output 1. | `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json` | verified (script). FSM/BOSS task discovery not run (paper run), so the order is catalog-only. |

## C. Project-level dependencies (Claude)

All **not verified** unless a SOW/checklist reference is marked verified.

| # | Predecessor → Successor | Why | Source |
|---|---|---|---|
| D18 | Existing enterprise-structure facts (ledger, LE, BU names; Run 14 Q-E1) → BU, inventory-org and cost-org design | Twelve's production Financials already has these; the SOW names none. Nothing in D1–D7 can be designed without them. | Claude; SOW Fin 3.1 (existing BU structure, verified) |
| D19 | Design sign-off (per module) → configuration build for CRP1 | Methodology: requirements documented and approved before CRP preparation. | GoSaaS methodology steps 5 → 7 (checklist capture, verified) |
| D20 | Coupa configuration values extract → Self-Service Procurement, approvals and account rules | SOW asks to reuse Coupa values "where applicable". | SOW B 3.5 (verified); Claude |
| D21 | Approval hierarchy basis decision (position, supervisor, job level, approval groups; Run 14 Q-E9) → Approval Management for requisitions, POs (and expenses) | Delegation of Authority is in scope (B 3.3, 4.2, Fin 5.3). | Claude |
| D22 | Supplier source decision + Supplier conversion FDD/TDD → partial supplier load (CRP1) → full load (CRP2) → delta (UAT, go-live) | Only conversion object in scope. | SOW RICE 2 (verified); cycle rules (given) |
| D23 | Item master org + item classes → items for equipment, spares, manufactured product → manufacturing and maintenance structures | Items before structures (B 1.1–1.3), and before maintainable assets (B 7.1). | Claude |
| D24 | Expenses design session decision → Expenses configuration and test | Expenses is conditional. | SOW Fin 5.1 (verified) |
| D25 | Security and roles design + Printable PO report built and unit-tested → CRP2 entry | CRP2 rule: full security and customizations. | Cycle rules (given); SOW RICE 1, Cfg 12 (verified) |
| D26 | Test environment available (Run 14 Q-P1) + P2T refresh → CRP2 build | SOW names only development and production. | SOW E.6 (verified); checklist (verified); Claude |
| D27 | New COA natural accounts (inventory, WIP, variance, receipt accrual; Run 14 Q-E3) → Receipt Accounting / Cost Accounting / SLA rules → GL review (Fin 7) | Live ledger; new subledgers post into it. | Claude |
| D28 | Procurement + Payables flows working (supplier invoices) → Sustainability test | Sustainability data comes from AP supplier invoices and file uploads. | SOW Fin 4.1 (verified); Claude |
| D29 | UAT sign-off → Twelve migrates approved configuration to Production → Prod supplier load + delta → go-live | Twelve owns the Prod migration. | SOW C.10 (verified); Claude sequence |
| D30 | Oracle update cohort/dates confirmed (SR) → wave plan frozen | Updates must not hit test cycles or go-live. | PM checklist "Open SRs to get the update schedule" (verified); Claude |
| D31 | Training material (Train-the-Trainer) → Twelve trainers trained → end-user training before go-live | GoSaaS builds material, Twelve runs change management. | SOW B Change Mgmt, C.4, C.6 (verified); Claude timing |
| D32 | April month-end close in live Financials → go-live cutover window | Go-live W12 (5–9 May 2025) overlaps the close. | Claude (date arithmetic verified; close calendar not stated) |

## D. Counts
- FSCR file-based dependencies: 16 (D1–D16), plus 1 catalog-order dependency (D17): **17 FSCR**. Verified present in the files.
- Claude project-level dependencies: **15** (D18–D32). Not verified.
- Total: **32** (requirement: at least 10).

## E. Gaps noted
- FSCR has no cross-functional-area dependency graph for SCM/ERP (only HCM). Cross-module links (e.g. D2–D4 cost ↔ inventory ↔ BU) come from individual task skills, not a graph. verified.
- Several in-scope FAs have no pillar dependency file with a "Required Dependency Order" section: Approval Management and Sustainability have none; Self Service Procurement has 1 (catalog category hierarchy) and Supplier Portal 2. verified by the extract (136 sections from 161 files).
- Several dependency files describe execution prerequisites (Data Loader, FSM template, approval) rather than business dependencies; those were left out as not relevant to planning. verified (see extract).
