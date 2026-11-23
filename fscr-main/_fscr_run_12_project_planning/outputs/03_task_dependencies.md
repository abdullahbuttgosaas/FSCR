# Output 3: Task Dependencies (Twelve, SOW 50513scm)

High-level only. These are "what must exist before what" statements for planning. Nothing is configured.

**Who produced it: FSCR + Claude.** Claude picked the relevant pairs. FSCR files supplied the dependency statements for rows marked "FSCR". FSCR's `task-dependency-resolver` has **no script**. It is a method written in SKILL.md and needs FSM/BOSS task discovery (`uses_core: core.fusion-api.fsm-rest-client`), which this paper-only run may not call. So no `setup-task-sequence.json` was produced by FSCR. The only dependency graph in the repo is `knowledge/dependency-graphs/hcm-dependency-graph.json` (86 nodes, 281 edges, HCM only). FSCR has **no SCM, Procurement or Financials dependency graph**.

Legend: **V** = verified by reading the cited file in this run. **NV** = not verified (Claude's reasoning or Oracle knowledge, not checked against a source in this run).

## 1. Dependencies

| # | Must exist first | Before | Why / rule | Source | Status |
|---|---|---|---|---|---|
| D1 | Legal entity | Cost organization | "Define the legal entity before creating the cost organization." (dependency CCO-LEGAL-ENTITY, mandatory) | FSCR `pillars/scm/manufacturing-and-supply-chain-materials-management/cost-accounting/cost-organizations/ora-resource/ora_dependency_readiness.md` | V |
| D2 | Cost organization | Cost organization relationships (inventory orgs, cost books) | Required order step 1: define the cost org before associating inventory orgs or cost books | FSCR `.../cost-accounting/cost-organization-relationships/ora-resource/ora_dependency_readiness.md` (seq 1) | V |
| D3 | Item master (item validation) organization in the same legal entity | Cost organization relationship | Required order step 2 | same file (seq 2–3) | V |
| D4 | Ledger + accounting calendar; cost book | Cost book association to cost org | At least one cost book must be on the primary ledger of the cost org's legal entity | same file (seq 5–7, 10) | V |
| D5 | Inventory org with a Profit Center BU, same LE and same item master | Assignment of the inventory org to a cost org | Required order step 9 | same file (seq 9) | V |
| D6 | Location | Inventory organization | The inventory org create is blocked when no LocationId/Code/Name is supplied | FSCR `.../facilities/manage-inventory-organizations/ora-resource/ora_input_validation.md` (row "Location") | V |
| D7 | Location | Business unit | **Conditional only.** FSCR resolves a BU location "only when manager or location is supplied". The location is not mandatory for a BU. | FSCR `pillars/erp/financials/organization-structures/ora-resource/ora_design_enforcement.md` (FUN_MANAGE_BUSINESS_UNIT step 3) | V |
| D8 | Person/worker records (users) | BU manager reference, and any setup that names a person | Manager is resolved to an exact active PersonId; the request stops if the person is missing or inactive | same file (step 3) and `.../ora_error_handling.md` | V |
| D9 | Business unit + inventory organization | Inventory business-event configurations | "Ensure the business unit and the inventory organization ... already exist" | FSCR `.../inventory-management/inventory-business-event-configurations/ora-resource/ora_dependency_readiness.md` (seq 1) | V |
| D10 | Inventory organization | Manufacturing work area | Confirm the target organization exists before creating a work area | FSCR `.../manufacturing-master-data/manufacturing-work-areas/ora-resource/ora_dependency_readiness.md` (seq 1) | V |
| D11 | Work area | Work center | A work center create resolves an active Work Area first | FSCR `.../manufacturing-master-data/manufacturing-work-centers/ora-resource/ora_dependency_readiness.md` (seq 1) | V |
| D12 | Plant org access, resource type, UOM; primary work center | Manufacturing resource and resource instances | Org access and the resource prerequisites come first; a primary work center must be assigned to the parent resource | FSCR `.../manufacturing-master-data/manufacturing-resources/ora-resource/ora_dependency_readiness.md` (seq 1–4) | V |
| D13 | Inventory org access + asset source item enabled in that org | Maintenance work orders in a related org | Required order step 2 | FSCR `.../maintenance-management/manage-maintenance-organization-relationships/ora-resource/ora_dependency_readiness.md` | V |
| D14 | Work definitions duplicated across orgs with a common code | Cross-org maintenance programs (preventive, SOW 7.6) | Required order step 3 | same file | V |
| D15 | Cost analysis group and analysis code | Cost element that references them | seq 5 | FSCR `.../cost-accounting/cost-elements/ora-resource/ora_dependency_readiness.md` | V |
| D16 | Cost organization (→ cost book → category) | Default cost profiles | seq 1–4 | FSCR `.../cost-accounting/default-cost-profiles/ora-resource/ora_dependency_readiness.md` | V |
| D17 | Procurement offering opted in; implementation role assigned | Any Procurement setup (e.g. purchasing line types) | seq 1–2 | FSCR `pillars/scm/procurement/procurement-foundation/manage-purchasing-line-types/ora-resource/ora_dependency_readiness.md` | V |
| D18 | Locations ↔ legal and legislative organizations (HCM) | Departments, jobs, positions (used by approval hierarchies) | The graph has `locations → legal-and-legislative-organizations` **and** `legal-and-legislative-organizations → locations`, which is a **cycle**. Under FSCR's own resolver rules a cycle is skipped and diagnosed (`dependency-graph-enrichment.md`, "Skip and diagnose edges with ... cycle"). | FSCR `knowledge/dependency-graphs/hcm-dependency-graph.json` | V (edges read); impact on Twelve NV |
| D19 | Functional-area order in the catalog: Legal Structures → Financial Reporting Structures → Organization Structures → Facilities → Users and Security → Items → Inventory → Receiving → Receipt Accounting → Cost Accounting → Manufacturing Master Data → Structures → Maintenance | Setup order inside Manufacturing and Supply Chain Materials Management | `functionalAreaOrder` is the catalog's own order. The resolver treats catalog order as the primary sequence source. | FSCR `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json` (ORA_MANUFACTURING_AND_SUPPLY_C) | V (order); that the order is a true prerequisite: NV |
| D20 | Users/workers with supervisor or position hierarchy | Purchasing DOA approval rules (SOW 3.3, 4.2) and expense approvals (5.3) | Approval rules route to people or hierarchies that must already exist | Claude (Oracle BPM approval knowledge) | NV |
| D21 | Users (procurement agents) | Procurement agent assignments to the procurement BU | An agent is an existing person/user | Claude. FSCR's `manage-procurement-agents` folder has no statement about this. | NV |
| D22 | Requisitioning and Procurement BU functions (Fin 3.1) + service-provider relationship | Requisitions and POs (SOW 3, 4) | A procurement BU must serve the requisitioning/finance BU | Intake output 2 quoting FSCR `organization-structures` skill; FSCR `assign-business-unit-business-function.md` line 60 | V (FSCR text) |
| D23 | Supplier conversion (RICE 2) loaded | CRP2 PO/receipt/invoice scenarios; Supplier Portal registration and self-service (SOW 5) | Full-data CRP2 needs real suppliers | Claude + our practice (CRP2 = full data) | NV |
| D24 | Purchasing categories (Coupa values, 3.5) | Requisition lines, item categories, cost profiles by category (D16) | Categories are referenced downstream | Claude; D16 is FSCR | NV |
| D25 | Payables supplier invoices in the system | Sustainability data (SOW Fin 4.1) | Sustainability is sourced from AP invoices | SOW Fin 4.1 + Claude | V (SOW) / NV (sequence) |
| D26 | Inventory orgs, items, work definitions | CRP1 manufacturing/maintenance work-order scenarios (6.1, 7.1) | You cannot create, release and complete a work order without them | Claude | NV |

Count: 26 dependencies (≥10 requested). FSCR-sourced: 20 (D1–D19, D22). Claude-only: 5 (D20, D21, D23, D24, D26). SOW + Claude: 1 (D25).

## 2. What FSCR could and could not do

| Item | Result | Status |
|---|---|---|
| Ordered `setup_task_sequence` from `task-dependency-resolver` | **Not produced by FSCR.** No script exists. The method needs FSM/BOSS discovery, which a paper-only run may not call. Claude applied steps 2, 5 and 6 by hand (catalog `displaySequence`, functional-area tail for tasks with no sequence) to produce the `Resolver Sequence` column in Output 1. That column is not an FSCR resolver result. | V |
| SCM dependency graph | None in the repo | V |
| Cross-offering edges (e.g. Procurement BU → Inventory) | None in FSCR | V |
| Per-task dependency statements | Present in many pillar `ora_dependency_readiness.md` files; these are the source of D1–D17. They are written for task execution (Data Loader preflight), not for project planning. | V |

## 3. Open questions

| # | Question |
|---|---|
| T1 | Will Twelve keep the existing LE/ledger as the cost org LE (D1, D4)? Intake E1/E2 are still open. |
| T2 | Is a new item master org needed (D3)? Intake E7. |
| T3 | Which approval hierarchy is used for DOA: supervisor, position or approval groups (D20)? |
| T4 | Should the HCM location ↔ legal-entity cycle (D18) be fixed in FSCR's graph? |
