# Output 2: Enterprise Structure (Project Intake, high-level)

**Project:** Twelve: Oracle Cloud SCM Implementation (SOW dated Jan 24, 2025, Doc 50513scm)
**Produced by:** FSCR + Claude.
- **FSCR** supplied the Business Unit design principles and required design evidence (`pillars/erp/financials/organization-structures/SKILL.md` §"Business Unit Design Principles" and §"Required Design Evidence"), the design advisory (`ora-resource/ora_design_advisory.md`), and the catalog task names for cost and inventory orgs (Manage Cost Organizations, Manage Cost Books, Cost Organization Relationships, Manage Inventory Organizations, Manage Plant Profiles).
- **Claude** read the SOW, applied that guidance and wrote the structure. Suggestions for inventory, cost and item-master orgs are standard Oracle practice from Claude's general knowledge; they are not in FSCR's SCM skills, which hold no design guidance.
- FSCR `shared/project-intake/enterprise-structure-intake` is an empty stub and contributed nothing.

**Important:** The SOW does **not** name any ledger, legal entity, business unit, inventory organization, cost organization or plant. Every named object below is a placeholder. Labels: **[SOW]** verified from the SOW text; **[FSCR]** verified from repo guidance; **SUGGESTED (checklist / FSCR guidance / Claude)** not verified, with a matching open question; **not stated**.

---

## 1. Facts stated in the SOW (all verified)

| # | Fact | SOW ref |
|---|---|---|
| E1 | Countries: 1 (US) | C.7 |
| E2 | Plant locations: 2 | C.7 |
| E3 | "Configuration of the current Plant locations as Inventory Organizations, allowing location specific configurations to be added in the future" | B 2.2 |
| E4 | "Definition of the Costing Organization Structure and Cost Books" | B 2.3 |
| E5 | Costing processes for manufactured inventory, maintenance equipment and inventoried material | B 2.4–2.6 |
| E6 | An **existing** Business Unit structure exists in production Financials | B Fin 3.1 |
| E7 | "Configure updates for the Requisitioning and Purchasing Business Units into the existing Business Unit Structure" | B Fin 3.1 |
| E8 | "Include considerations for Centralized / Decentralized and Shared Service processes" | B Fin 3.2 |
| E9 | Production Financials in use: GL, AR, Project Management, Grants Management, AP, Cash Management, Fixed Assets. This implies at least one existing ledger, legal entity and BU. Their names, counts and currency are not stated. | B Fin intro |
| E10 | Project and non-project accounting for POs, receipts and expenses implies project organizations exist in production. | B 3.4, Fin 1, Fin 5.4 |
| E11 | Common design for all modules, positioning future location-specific phase roll-outs | C.3 |
| E12 | Manufacturing is process-based only; maintenance is in scope. Which plant does which is not stated. | B 6.2, B 7 |

## 2. Proposed high-level structure

```
Enterprise: Twelve Benefit Corporation  [SOW: name of contracting party; Oracle enterprise name not stated]
└─ Country: United States  [SOW]
   ├─ Primary Ledger: <EXISTING US LEDGER>         SUGGESTED (FSCR guidance + Claude): reuse existing; 1 ledger, USD
   │   └─ Legal Entity: <EXISTING US LE>           SUGGESTED (Claude): reuse existing production LE(s)
   ├─ Business Units
   │   ├─ <EXISTING FINANCE BU>                    [SOW: an existing BU structure exists; name not stated]
   │   │     current functions: Payables, Receivables, Projects, Grants, Assets-related (implied by E9; not verified)
   │   │     ADD: Requisitioning + Procurement + Receiving functions   SUGGESTED (FSCR guidance: smallest practical number of BUs)
   │   └─ (option) <PROCUREMENT BU> as shared-service provider       SUGGESTED alternative only if centralized procurement is chosen (E8)
   ├─ Item Master Organization: <ITEM MASTER>      SUGGESTED (Claude; Oracle practice: separate master org)
   ├─ Inventory Organizations (2)                  [SOW: 2 plants → inventory orgs]
   │   ├─ <PLANT 1>  manufacturing-enabled? maintenance-enabled?   not stated
   │   └─ <PLANT 2>  manufacturing-enabled? maintenance-enabled?   not stated
   └─ Cost Organization(s)                         [SOW: structure to be defined]
       └─ <COST ORG> covering both plants          SUGGESTED (Claude): 1 cost org (single LE / ledger)
           └─ Cost Book(s): <PRIMARY COST BOOK>    SUGGESTED (Claude): 1 primary book tied to the ledger
```

## 3. Component by component

### 3.1 Ledgers
- **Stated:** a production GL exists (E9). Count, name, currency, calendar and chart of accounts: **not stated**.
- **SUGGESTED (FSCR guidance + Claude):** reuse the existing US primary ledger for all SCM subledgers. One country gives no evident need for another primary ledger. FSCR advisory: a BU uses **one primary ledger**; secondary ledgers or reporting currencies are not primary ledgers.
- **Checklist recommendation:** none (the checklist does not cover ledgers).
- **FSCR impact:** new subledger accounting for Receipt Accounting, Cost Accounting (incl. manufacturing and maintenance work-order costing) and Expenses lands in that ledger. COA segment impacts (new inventory, WIP and variance accounts) are **not stated** → Q-E3.

### 3.2 Legal entities
- **Stated:** none named. One country implies at least one US legal entity.
- **SUGGESTED (Claude):** reuse the existing production LE(s). No new LE is implied by the SOW.
- FSCR guidance: "Do not normally split one legal entity across multiple BUs; document and test any exception."
- Inventory orgs need an LE and a primary ledger: if there is more than one LE, each plant must be mapped → Q-E2.

### 3.3 Business units (FSCR design principles applied)
- **Stated:** an existing BU structure; requisitioning and purchasing BUs are to be added "into" it; centralized, decentralized and shared-service options to be considered (E6–E8).
- **SUGGESTED, Option A (FSCR guidance "prefer the smallest practical number of BUs"):** assign the Requisitioning, Procurement and Receiving business functions to the existing finance BU. That BU is then the requisitioning, procurement and payables-invoicing BU. Simplest, with no service-provider relationship needed.
- **SUGGESTED, Option B (only if Twelve wants centralized procurement for future sites, per E8 and E11):** a dedicated procurement BU acting as service provider to the existing finance/requisitioning BU (FSCR task `FUN_MANAGE_SERVICE_PROVIDER_RELATIONSHIPS`). FSCR guidance: "a procurement BU … must be associated with the finance BU in which purchase orders are created and matched to payables invoices."
- **Employee-assignment BU:** FSCR guidance says to design it with Expenses, Projects and Requisitioning effects in mind and prefer alignment with Payables invoicing. SUGGESTED: the same existing BU → Q-E5.
- **Reference data sets:** FSCR says the task must be saved even if defaults are unchanged. Which set holds procurement and inventory reference data (payment terms, UOM, carriers, etc.) is **not stated** → Q-E6.
- **Design evidence to record per BU (FSCR "Required Design Evidence"):** purpose and owner; why a hierarchy is insufficient; ledger/LE relationship; business functions; service-provider relationships; security/data-role scope; reference-data-set assignment; testing impact. All are **not recorded** for Twelve; they need the existing-BU facts.

### 3.4 Inventory organizations
- **Stated:** 2 plants become inventory orgs, with room for future location-specific configuration (E2, E3).
- **SUGGESTED (Claude, Oracle practice):** an Item Master Organization separate from the plants, plus the 2 plant inventory orgs under the same BU, LE and ledger.
- Per plant, **not stated** (→ Q-E7): plant names and addresses; manufacturing plant enabled (process manufacturing); maintenance enabled; which items and processes each holds (spare parts, bulk material, VMI, manufactured product); subinventories and locators (putaway is in scope per B 2.1); lot or serial control; receiving parameters.
- FSCR catalog tasks to run later (no configuration now): Manage Inventory Organizations, Manage Plant Profiles, Manage Inventory Organization Data Access for Users, Associate Fixed Asset Books with Inventory Organizations (relevant to maintenance assets). [FSCR] verified task names.

### 3.5 Cost organizations and cost books
- **Stated:** structure and cost books to be defined; costing for manufactured inventory, maintenance equipment and inventoried material (E4, E5).
- **SUGGESTED (Claude):** 1 cost org covering both plant inventory orgs, since there is one LE/ledger, and 1 primary cost book linked to the primary ledger. A second cost book only if a parallel valuation is needed (for example grants or project reporting): **not stated**.
- **Not stated** (→ Q-E8): cost method per org/item (standard, average, actual); valuation structure (by cost org vs by inventory org); whether the two plants must be valued separately; how maintenance work-order cost flows (expense vs capitalize to Fixed Assets or projects).
- FSCR catalog tasks: Manage Cost Organizations, Cost Organization Relationships, Manage Cost Books, Manage Cost Organization Data Access for Users. [FSCR] verified task names.

### 3.6 Other organizations touched (stated or implied)
| Org | Status |
|---|---|
| Project organizations (Project Financial Management) | Implied by project accounting in POs and expenses (E10). Names not stated. |
| Grants organizations | Grants in production (E9). Names not stated. |
| Asset books (Fixed Assets) | Implied by FA in production and maintainable assets. Book names not stated. |
| Approval hierarchy for delegation of authority (POs, requisitions, expenses) | Basis (position, supervisor, job level, approval groups) not stated → Q-E9 |
| Sustainability | No org structure stated. Data sourced from AP invoices and file uploads. |

## 4. Checklist mapping (GoSaaS Scoping Checklist / Pre-sales)
| Checklist question | Answer |
|---|---|
| Number of locations | 2 plants, US only [SOW] verified |
| Number of divisions (Overview) | not stated → Q-E1 |
| PIM "child orgs" | 2 plant inventory orgs as children of an item master: SUGGESTED (checklist asks; Claude answers) → Q-E7 |
| PIM "operational attributes" | not stated |
| Security: restricted viewing / data access | not stated. Inventory and cost org data access tasks exist in FSCR → Q-E10 |

## 5. Open questions (each needs a person to confirm)
| ID | Question | Suggested answer |
|---|---|---|
| Q-E1 | What are the names and count of existing ledgers, legal entities and BUs in production? (Required before any design decision.) | none |
| Q-E2 | Which legal entity owns each plant? | SUGGESTED (Claude): same existing US LE for both |
| Q-E3 | Do COA changes need new inventory, WIP, cost-variance or receipt-accrual accounts? | SUGGESTED (Claude): yes, likely new natural accounts, no new segments |
| Q-E4 | Procurement model: decentralized (Option A) or centralized shared service (Option B)? | SUGGESTED (FSCR guidance): Option A, the smallest number of BUs |
| Q-E5 | Which BU is the employee-assignment BU for requisitioners and expense submitters? | SUGGESTED (FSCR guidance): the existing finance BU |
| Q-E6 | Reference data set strategy for procurement and inventory objects? | SUGGESTED (Claude): the existing BU's default set |
| Q-E7 | Plant names; manufacturing and/or maintenance enabled per plant; item master org? | SUGGESTED (Claude): separate item master org |
| Q-E8 | Cost org count, cost books, cost method; how maintenance work-order cost is handled? | SUGGESTED (Claude): 1 cost org, 1 primary cost book |
| Q-E9 | Approval hierarchy basis for POs, requisitions and expenses? | none (Coupa values may be reused: SOW B 3.5) |
| Q-E10 | Data access needed by plant or cost org? | none |
| Q-E11 | Future sites (C.3): expected count and country, to size the BU and cost-org design for growth? | none |
