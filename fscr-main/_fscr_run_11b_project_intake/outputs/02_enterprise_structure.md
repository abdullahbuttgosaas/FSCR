# Output 2 — Enterprise Structure Intake (Twelve)

Source: SOW 50513scm only.
FSCR skills used:
- `shared.project-intake.enterprise-structure-intake` is a generic stub with no questions and no template. It provided only the output headings (recommendations, work products, review points).
- `pillars/erp/financials/organization-structures/SKILL.md` was used for its "Business Unit Design Principles" and its per-BU "Required Design Evidence" list (the column structure of table 3).
- `ora-resource/ora_design_advisory.md` was used for BU, ledger and service-provider terminology.
- FSCR offering catalog functional areas were used for the structure layers in table 1: `ORA_ASK_LEGAL_STRUCTURES`, `ORA_ASK_FIN_REPORTING_STRUCT`, `ORA_ASK_ORGANIZATION_STRUCTURE`, `ORA_RCS_FACILITIES`, `CST_DEFINE_COST_MANAGEMENT`.

FSCR has no enterprise-structure questionnaire and no SCM inventory or cost organization intake. Claude filled all content from the SOW.

Legend: **V** = verified against the SOW text. **NV** = not verified (inference). "not recorded" = the SOW does not say.

## 1. Enterprise structure, layer by layer

| Layer | What the SOW says | Count | Status |
|---|---|---|---|
| Enterprise / company | Twelve Benefit Corporation | 1 enterprise | V (preamble) |
| Countries / jurisdictions | US only | 1 | V (C.7) |
| Legal entities | not recorded | **not recorded** | — |
| Ledgers (primary, secondary, reporting currency) | Production Financials already exist (GL named, Fin intro). Ledger names and counts are not given. | **not recorded** | V that an existing production GL exists; count not recorded |
| Chart of accounts / calendar | not recorded | not recorded | — |
| Business units, existing | An "existing Business Unit Structure" exists (Fin 3.1). How many and which functions: not recorded. | not recorded | V (exists) |
| Business units, new or updated | Requisitioning and Purchasing BU functions or BUs to be configured into the existing structure (Fin 3.1). Whether these are new BUs or new functions on existing BUs is not stated. | not recorded | V (requirement); NV (new BU vs function) |
| Shared services / service provider | Centralized, decentralized and shared-service processes are to be considered (Fin 3.2). The design is not decided. | not recorded | V |
| Plant locations | 2 | 2 | V (C.7) |
| Inventory organizations | The current plant locations become Inventory Organizations, so location-specific setup can be added later (SCM 2.2) | 2 implied (one per plant) | V (rule); NV (count of 2 is inferred from C.7 + 2.2) |
| Item master organization | not recorded | not recorded | — |
| Costing organization(s) and cost books | Costing org structure and cost books are to be defined (SCM 2.3) | not recorded | V (requirement) |
| Manufacturing plants / work centers / work areas | The ability to create them is in scope. No structures or work definitions are migrated (6.1). | not recorded | V |
| Maintenance organizations | Maintenance is enabled for equipment and assets (7.x). The maintenance org model is not stated. | not recorded | V (requirement) |
| Project organizations / Grants | Production Project Management and Grants already exist and are being remediated (Fin intro) | not recorded | V (exist) |
| Fixed Assets books | FA exists in production and is being remediated | not recorded | V (exists) |
| Future rollout | Common design; future location-specific phase rollouts (C.3) | — | V |

## 2. FSCR Business Unit design principles applied to the SOW (organization-structures skill)

| FSCR principle | What it means for Twelve | Status |
|---|---|---|
| Prefer the smallest practical number of BUs; do not copy the org chart | The new Requisitioning and Purchasing functions should first be considered as **functions assigned to an existing BU** before creating new BUs | NV (recommendation) |
| "A procurement BU ... must be associated with the finance BU in which purchase orders are created and matched to payables invoices" | If a separate procurement BU is chosen (Fin 3.2 shared service), a service-provider relationship to the AP or finance BU is needed | NV (recommendation) |
| Cross-country BUs are an exception | Not applicable: 1 country (US) | V (C.7) |
| Design employee-assignment BUs with Expenses, Projects and Requisitioning in mind | Relevant because Expenses (conditional), Projects and Requisitioning are all in scope | V (scope); NV (design impact) |
| BU changes affect access, approvals, defaults and history; reassess through change control | Changing an existing production BU structure is a high-impact change for production Financials | NV (risk) |

## 3. Required design evidence for each BU (FSCR template columns, values from the SOW)

| BU | Purpose / owner | Ledger + legal entity | Business functions | Service-provider relationships | Security / data scope | Reference data set | Test impact |
|---|---|---|---|---|---|---|---|
| Existing BU(s) (names not recorded) | not recorded | not recorded | Existing functions not recorded; add Requisitioning and Purchasing (Fin 3.1, V) | To be decided (Fin 3.2, V) | not recorded | not recorded | Regression of production Financials (NV) |
| Any new procurement BU (only if decided) | not recorded | not recorded | Procurement / Requisitioning (NV) | Required to the finance BU (FSCR rule) | not recorded | not recorded | not recorded |

## 4. Recommendations (NV, Claude using the FSCR principles)

1. Hold an enterprise-structure confirmation workshop in the first weeks, because every SCM organization depends on the existing LE, ledger and BU foundation.
2. Default position: assign Requisitioning and Purchasing to the existing BU(s); create a separate procurement BU only if Fin 3.2 results in a shared-service model.
3. One inventory organization per plant (2), plus a separate item master organization if Twelve has none. This needs confirmation.
4. Define cost organizations and cost books together with the inventory orgs (2.3) and record them as Key Design Decisions.

## 5. Open questions

| # | Question |
|---|---|
| E1 | How many legal entities are there, what are their names, and how are they registered in the US jurisdiction? |
| E2 | How many primary ledgers are there? Are there secondary ledgers or reporting currencies? What chart of accounts and calendar are used? |
| E3 | What business units exist today and which business functions are assigned to each? |
| E4 | Should Requisitioning and Purchasing be new BUs or functions added to existing BU(s)? |
| E5 | Centralized, decentralized or shared-service procurement and payables? Which BU is the provider and which is the client? |
| E6 | Names and addresses of the 2 plants. Confirm one inventory organization per plant. |
| E7 | Is there an item master organization? Is it new or existing? |
| E8 | Cost organization structure, how many cost books, and the costing method for manufactured and maintenance items |
| E9 | Maintenance organization model: are maintenance orgs the same as the plant inventory orgs? |
| E10 | Reference data set strategy for the new SCM reference objects |
| E11 | Are any new legal entities, plants or locations expected for the future "location specific phase rollouts" (C.3), and when? |
| E12 | Project organizations and Grants: does the existing structure need changes for project-based POs and receipts? |
