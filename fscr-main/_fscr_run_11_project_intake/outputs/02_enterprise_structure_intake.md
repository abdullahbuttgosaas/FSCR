# Output 2 — Enterprise structure intake (from the SOW only)

FSCR skills: `shared.project-intake.enterprise-structure-intake` (generic stub — no questions or fields). The object list below comes from FSCR's setup-level skills and catalog: `pillars/erp/financials/legal-structures` (5 tasks), `pillars/erp/financials/financial-reporting-structures` (7 tasks), `pillars/erp/financials/organization-structures` (4 tasks: Business Unit, BU Business Function, BU Set Assignment, Service Provider Relationships), `pillars/scm/manufacturing-and-supply-chain-materials-management/facilities` (incl. manage-inventory-organizations, manage-item-organizations), `.../cost-accounting` (cost-organizations, cost-books, cost-organization-relationships, valuation-structures, valuation-units), `.../maintenance-management/manage-maintenance-organization-relationships`, `pillars/erp/project-financial-management/project-organizations`, and the catalog functional areas Legal Structures, Financial Reporting Structures, General Ledger, Organization Structures, Workforce Structures, Inventory Organizations, Item Organizations.
Who produced it: **FSCR + Claude**. FSCR gave the object types (as setup tasks); I wrote the intake, the SOW facts and the questions. None of the FSCR skills used here holds intake questions; they are configuration workflows.
Tags: [V] = stated in the SOW. [NV] = my interpretation. No values below are invented. Anything the SOW does not state is an open question.

| # | Structure object (FSCR source) | What the SOW says | Tag | Status / open question |
|---|---|---|---|---|
| E1 | Enterprise (Enterprise Profile) | Twelve Benefit Corporation | V | Existing tenancy implied by "production Financials" [NV] |
| E2 | Legal entities (Legal Structures: Manage Legal Entity, Registrations, Addresses) | Not stated. Only "1 country (US)" | V (country only) | **Q:** How many legal entities exist or are needed? Any new LE for SCM? |
| E3 | Legal reporting units / jurisdictions | Not stated | — | **Q:** LRUs and registrations (US federal/state) — existing, no change? |
| E4 | Ledgers (General Ledger) — primary, secondary, reporting currencies | Not stated. The SOW says GL updates are "incremental changes as needed" | V | **Q:** Number of ledgers; currency; whether costing needs a separate secondary ledger. Assumed existing [NV] |
| E5 | Chart of accounts, value sets, calendar (Financial Reporting Structures) | Not stated. Accounting rules for POs/receipts/expenses are in scope | V | **Q:** Does the CoA need new segment values (inventory, WIP, cost variance, accrual, maintenance expense)? |
| E6 | Business units (Organization Structures: Manage Business Unit) | "Configure updates for the **Requisitioning and Purchasing Business Units** into the **existing** Business Unit Structure" | V | **Q:** Number of existing BUs; are requisitioning and procurement BUs new or functions added to existing BUs? |
| E7 | BU business functions (Assign BU Business Function) | Requisitioning and Purchasing functions implied | V | **Q:** Which BU gets Requisitioning, Procurement, Payables Invoicing, Receiving? |
| E8 | Service provider relationships (Manage Service Provider Relationships) | "considerations for Centralized / Decentralized and **Shared Service** processes" | V | **Q:** Will a central procurement BU serve the requisitioning BUs? Decision is open |
| E9 | Reference data sets (BU Set Assignment) | Not stated | — | **Q:** Common vs BU-specific sets for suppliers, payment terms, catalogs |
| E10 | Inventory organizations (Facilities: manage-inventory-organizations) | "Configuration of the **current Plant locations** as Inventory Organizations"; "Number of Plant Locations — **2**" | V | **Q:** Plant names/codes; one inventory org per plant (= 2) [NV]; manufacturing-enabled and/or maintenance-enabled per org; subinventories and locators |
| E11 | Item master organization (Item Organizations / Inventory Organizations in Product Management) | Not stated (PIM items in scope) | V (PIM in scope) | **Q:** Does an item master org already exist (for Financials/AP items)? New or reuse? |
| E12 | Cost organizations, cost books, valuation structures (Cost Accounting) | "Definition of the **Costing Organization Structure and Cost Books**" | V | **Q:** Number of cost orgs (one for both plants vs one per plant); primary/secondary cost books; cost method per item type |
| E13 | Maintenance organization relationships (Maintenance Management) | Maintenance in scope; maintainable assets; Installed Base trackable | V | **Q:** Which inventory org(s) are maintenance orgs, and their relationship to the plant orgs |
| E14 | Manufacturing plants (Manufacturing Master Data: plant parameters) | Process manufacturing; work centers/areas | V | **Q:** Which of the 2 plants manufacture? Work areas and work centers per plant |
| E15 | Project organizations (Project Organizations) | Project and non-project POs, commitments, receipts | V | **Q:** Project-owning orgs and expenditure orgs unchanged? |
| E16 | Workforce structures / locations | Not stated; "Required employees are in Production" | V | **Q:** Are locations for ship-to/bill-to/plants already defined? |
| E17 | Intercompany / supply chain financial flows | Not stated | — | **Q:** Any intercompany transfers between plants or legal entities? |
| E18 | Future rollouts | "Common Design … positioning future location specific Phase rollouts" | V | **Q:** Expected future sites/countries (affects naming and set strategy) |

## Summary
- Stated by the SOW: **1 country (US), 2 plants → inventory organizations, an existing BU structure to be extended with Requisitioning and Purchasing BUs, a costing org structure and cost books to define, and a decision on centralized/decentralized/shared service.** [V]
- Not stated (must not be assumed): number of legal entities, ledgers, currencies, BUs, cost organizations, the item master org, environments, users. [V that the SOW is silent]
- FSCR reached this structure only through setup-task skills. Those skills assume configuration inputs (BU name, set, ledger, LE) and route to Data Loader / Run Book. They hold no "intake question" layer. [V]
