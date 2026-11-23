# Output 1: Offering Task Map (Project Planning, high-level)

**Project:** Twelve Benefit Corporation: Oracle Cloud SCM Implementation (SOW dated Jan 24, 2025, Doc 50513scm)
**Produced by:** FSCR + Claude.
- **FSCR** supplied the task membership and order (effective catalog `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`, 54 offerings / 609 FAs / 7,282 tasks), the skill match for each task (FSCR's own matcher `core/runbook/scripts/task_context._skill_path`), the initializer mapping schema, and the project workspace initializer dry-run.
- **Claude** chose the offering / functional-area pairs from the SOW and the Run 14 intake (01_SCOPE.md §2), classified each as NEW / INCR / COND / TBD, ran the resolver's catalog steps offline (no FSM/BOSS task discovery, which needs a Fusion call), and wrote this summary.
- FSCR's `offering-task-map-builder` has a method and a helper (`task_to_skill_mapping.py`) but no CLI; FSCR's `task-dependency-resolver` is a method only (no script). Both were followed by Claude's script `work/build_task_map.py`.

**Status:** Planning only. Nothing configured, no Fusion calls. Full task list: `01_OFFERING_TASK_MAP_tasks.csv`; initializer-format mapping: `01_identified-task-mapping.json`.

**Scope classes:** NEW = new module, all catalog tasks listed for review; INCR = incremental change to live production Financials, tasks listed but only some will change; COND = conditional (Expenses design session); TBD = remediation scope 'determined during the project', FA listed, tasks not expanded.

**Sequence:** `Resolver Sequence` = offering/FA order below × catalog `displaySequence`, numbered 1…N. It follows resolver steps 1, 2 and 6 using catalog data only. FSM-backed sequence: **not available** (paper run). This is a deviation from the builder's gate, which expects a resolver-persisted `setup_task_sequence`; recorded as such. verified (script).

## 1. Offering / functional-area map

| # | Offering (code) | Functional area (code) | SOW ref | Class | Catalog tasks | In map | With FSCR skill | Catalog-mandatory | FSM export/import | Repeated task codes | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Financials (`XLE_FINANCIALS_JUR`) | Organization Structures (`ORA_ASK_ORGANIZATION_STRUCTURE`) | Fin 3.1-3.2 | INCR | 18 | 18 | 10 | 10 | 10 | 0 | pending in Run 14 classifier; SUGGESTED owner Financials (Run 14 Q-S4) |
| 2 | Financials (`XLE_FINANCIALS_JUR`) | Users and Security (`ORA_ASK_USERS_AND_SECURITY`) | Cfg 12 | NEW | 9 | 9 | 5 | 7 | 7 | 0 | pending in Run 14 classifier (21 offerings); SUGGESTED owner Financials (Run 14 Q-S4) |
| 3 | Product Management (`PIM_PROD_MNG`) | Item Organizations (`ORA_EGP_FA_ITEM_ORGANIZATIONS`) | B 1.1-1.3 | NEW | 26 | 26 | 22 | 1 | 24 | 7 | resolved |
| 4 | Product Management (`PIM_PROD_MNG`) | Items (`ORA_EGP_FA_ITEMS`) | B 1.1-1.2 | NEW | 35 | 35 | 27 | 4 | 30 | 0 | resolved |
| 5 | Product Management (`PIM_PROD_MNG`) | Structures (`EGO_ADVANCED_PRODUCT_STRUCT`) | B 1.3 | NEW | 7 | 7 | 6 | 2 | 6 | 0 | resolved |
| 6 | Manufacturing and Supply Chain Materials Management (`ORA_MANUFACTURING_AND_SUPPLY_C`) | Facilities (`ORA_RCS_FACILITIES`) | B 2.2 | NEW | 29 | 29 | 11 | 6 | 27 | 10 | resolved |
| 7 | Manufacturing and Supply Chain Materials Management (`ORA_MANUFACTURING_AND_SUPPLY_C`) | Inventory Management (`ORA_WSH_INVENTORY_MGMT`) | B 2.1-2.2 | NEW | 63 | 63 | 27 | 0 | 62 | 3 | resolved |
| 8 | Manufacturing and Supply Chain Materials Management (`ORA_MANUFACTURING_AND_SUPPLY_C`) | Receiving (`WSH_ENABLE_RECEIVING`) | B 2.1 | NEW | 6 | 6 | 2 | 0 | 6 | 0 | resolved |
| 9 | Manufacturing and Supply Chain Materials Management (`ORA_MANUFACTURING_AND_SUPPLY_C`) | Receipt Accounting (`CMR_RECEIPT_ACCOUNTING`) | B 2.1, 3.4 | NEW | 44 | 44 | 2 | 0 | 36 | 21 | resolved |
| 10 | Manufacturing and Supply Chain Materials Management (`ORA_MANUFACTURING_AND_SUPPLY_C`) | Cost Accounting (`CST_DEFINE_COST_MANAGEMENT`) | B 2.3-2.6 | NEW | 63 | 63 | 18 | 20 | 56 | 30 | resolved |
| 11 | Manufacturing and Supply Chain Materials Management (`ORA_MANUFACTURING_AND_SUPPLY_C`) | Manufacturing Master Data (`ORA_WIS_COMMON_MFG_WORK_SETUP`) | B 6.1-6.4 | NEW | 26 | 26 | 18 | 5 | 21 | 6 | resolved; process vs discrete not separated in catalog |
| 12 | Manufacturing and Supply Chain Materials Management (`ORA_MANUFACTURING_AND_SUPPLY_C`) | Maintenance Management (`ORA_MNT_MGMT`) | B 7.1-7.7 | NEW | 23 | 23 | 7 | 7 | 16 | 8 | resolved |
| 13 | Manufacturing and Supply Chain Materials Management (`ORA_MANUFACTURING_AND_SUPPLY_C`) | Sustainability (`ORA_SUS_SUSTAINABILITY`) | Fin 4.1-4.3 | NEW | 7 | 7 | 0 | 5 | 7 | 0 | pending in Run 14 (3 offerings); SUGGESTED owner MSCMM (Run 14 Q-S4) |
| 14 | Procurement (`PO_PROCUREMENT`) | Procurement Foundation (`ORA_PO_PROC_FOUNDATION_FA`) | B 4.1 | NEW | 16 | 16 | 11 | 6 | 16 | 2 | resolved |
| 15 | Procurement (`PO_PROCUREMENT`) | Suppliers (`ORA_EGP_SUPPLIERS`) | B 5.4, RICE 2 | NEW | 35 | 35 | 26 | 1 | 26 | 2 | resolved |
| 16 | Procurement (`PO_PROCUREMENT`) | Approval Management (`ORA_PO_APPROVAL_MANAGEMENT_FA`) | B 3.3, 4.2 | NEW | 14 | 14 | 5 | 2 | 0 | 1 | resolved |
| 17 | Procurement (`PO_PROCUREMENT`) | Purchasing Foundation (`ORA_PO_PURCHASING_FOUNDATION`) | B 4.1-4.2 | NEW | 11 | 11 | 2 | 0 | 11 | 0 | resolved |
| 18 | Procurement (`PO_PROCUREMENT`) | Procurement Transaction Account Rules (`ORA_PO_PRC_TRX_ACC_RULES_FA`) | B 3.4 | NEW | 9 | 9 | 0 | 0 | 8 | 9 | resolved |
| 19 | Procurement (`PO_PROCUREMENT`) | Self Service Procurement (`PO_SSP_DEPLOYED`) | B 3.1-3.5 | NEW | 11 | 11 | 6 | 4 | 9 | 3 | resolved |
| 20 | Procurement (`PO_PROCUREMENT`) | Supplier Portal (`PO_SUP_PORTAL_DEPLOYED`) | B 5.1-5.5 | NEW | 7 | 7 | 6 | 1 | 5 | 1 | resolved |
| 21 | Financials (`XLE_FINANCIALS_JUR`) | General Ledger (`ORA_FIN_GENERAL_LEDGER`) | Fin 7, Cfg 7 | INCR | 42 | 42 | 15 | 11 | 38 | 14 | resolved |
| 22 | Financials (`XLE_FINANCIALS_JUR`) | Payables (`FIN_PAYABLES_DEPLOYED`) | Cfg 5 | INCR | 50 | 50 | 7 | 5 | 44 | 26 | pending in Run 14 (Financials or Procurement); SUGGESTED owner Financials |
| 23 | Project Financial Management (`PJF_PROJ_MNG`) | Project Costing Base (`ORA_PJC_PROJ_COSTING_BASE_FA`) | Fin 1, Cfg 8 | INCR | 33 | 33 | 1 | 1 | 33 | 3 | resolved |
| 24 | Financials (`XLE_FINANCIALS_JUR`) | Fixed Assets (`FIN_FIXED_ASSETS_DEPLOYED`) | Fin 2 | INCR | 47 | 47 | 10 | 10 | 42 | 23 | resolved |
| 25 | Financials (`XLE_FINANCIALS_JUR`) | Expenses (`FIN_EXPENSES_DEPLOYED`) | Fin 5.1-5.4 | COND | 40 | 40 | 6 | 6 | 34 | 4 | resolved; in/out decided by Expenses design session |
| 26 | Financials (`XLE_FINANCIALS_JUR`) | Receivables (`FIN_RECEIVABLES_DEPLOYED`) | Fin intro | TBD | 51 | 0 | 0 | 0 | 0 | 0 | remediation; extent 'determined during the project' |
| 27 | Financials (`XLE_FINANCIALS_JUR`) | Cash Management (`ORA_CE_CASH_MGMT_BANK`) | Fin intro | TBD | 39 | 0 | 0 | 0 | 0 | 0 | remediation; pending owner in Run 14; SUGGESTED Financials |
| 28 | Grants Management (`ORA_GMS_GRANTS_MANAGEMENT`) | Grants Management Foundation (`ORA_GMS_GRANTS_BASE_FA`) | Fin intro | TBD | 27 | 0 | 0 | 0 | 0 | 0 | remediation; extent TBD |
| 29 | Financials (`XLE_FINANCIALS_JUR`) | Financial Reporting Center (`ORA_FIN_REPORT_CENTER`) | Fin 6 | TBD | 16 | 0 | 0 | 0 | 0 | 0 | reporting approach is a strategy deliverable, not configuration |

## 2. Totals (verified by script)

- Offering/FA pairs selected: **29** (25 expanded, 4 TBD not expanded).
- Offerings: **6** (Grants Management only as a TBD row).
- Task rows in the map: **671**; unique task codes: **498**; rows repeating a code already listed under another FA: **173** (kept, per resolver rule 'retain every catalog task occurrence').
- By class: COND 40, INCR 190, NEW 441.
- By offering: Manufacturing and Supply Chain Materials Management 261, Financials 206, Procurement 103, Product Management 68, Project Financial Management 33.
- Rows with an FSCR pillar skill or flat task guidance: **250** (37%); the rest route to FSCR's shared Manual Tasks skill.
- Resolver Sequence unique and positive 1…671: yes. `sequence_unresolved` tasks: 0 (no pre-release/custom candidates were selected).

## 3. Planning view: build waves by functional area (Claude, SUGGESTED)

The catalog order is task order inside an offering. For the wave plan, the FAs are grouped into build waves. Each wave is built in Dev for CRP1 unless marked.

| Build wave | Functional areas | Why first/later | Target |
|---|---|---|---|
| B1 Foundation | Organization Structures (BU functions), Facilities (plants), Item Organizations (item master), Inventory org setup in Inventory Management, Cost Accounting org/books, Procurement Foundation | FSCR D1–D7, D13: org, LE, ledger links come first | W2–W3 (CRP1) |
| B2 Core flows | Items, Purchasing Foundation, Self Service Procurement, Suppliers, Receiving, Inventory Management, Receipt Accounting, Procurement Transaction Account Rules, Project Costing Base (commitments) | Requisition → PO → receipt → putaway → accounting end to end | W2–W3 (CRP1) |
| B3 Manufacturing and maintenance | Manufacturing Master Data, Maintenance Management, Structures | Needs plants, items, work areas (FSCR D8–D11) | W3 (CRP1, ready-to-use only) |
| B4 Controls, extensions | Users and Security, Approval Management, Supplier Portal, Printable PO report | CRP2 rule: full security + customizations | W6 (CRP2) |
| B5 Finance updates | General Ledger/SLA, Payables, Fixed Assets, Expenses (if in), Sustainability | Depend on B2 accounting and AP invoices (D27, D28) | W6 (CRP2) |
| TBD | Receivables, Cash Management, Grants, Financial Reporting Center | Scope determined during the project; reporting approach is a strategy deliverable | decide by G1 |

## 4. Project workspace initializer (FSCR) dry-run

Command (repo copy, run from `fscr-main/`):
`python core/project-mgmt/project-workspace-initializer/scripts/initialize_project_workspace.py --project-name "Twelve SCM Planning Run15" --customer "Twelve Benefit Corporation" --implementation-objective "Implement Oracle Cloud SCM for Twelve (planning only)" --pillar SCM --pillar ERP --offering "Product Management" --offering "Manufacturing and Supply Chain Materials Management" --offering "Procurement" --offering "Financials" --offering "Project Financial Management" --country US --implementation-phase design --identified-task-mapping ../work/taskmap/identified-task-mapping.json --no-create-runbook --dry-run`

- Result: exit 0, printed `Would create project workspace: project\twelve-scm-planning-run15`. No folder was created (`project/` listing unchanged: `README.md`, `_template`, `draft-impl-project-20261028`). verified.
- The dry-run runs the initializer's mapping validation (`validate_identified_task_mapping`, exact-name match against `knowledge/setup-task-catalog/effective/setupTasksAll.json`) but does not print its counts. Calling the same FSCR function directly gave: **matched 671, unmatched 0, ambiguous 0, total 671**. verified (`work/initializer_dryrun.txt`).
- Not run: `create_project_runbook.py` (it writes into a workspace, which a dry-run does not create) and `core.runbook` (Oracle Run Book creation needs Fusion). `runbook_control` therefore was never written. verified.


## 5. Gaps and notes

- 5 FA owners were 'pending' (fail-closed) in Run 14 and use Run 14's SUGGESTED owner: Organization Structures, Users and Security, Payables, Cash Management → Financials; Sustainability → MSCMM. A person must confirm (Run 14 Q-S4). not verified.
- The catalog has no separate FA for process vs discrete manufacturing, meters or Installed Base (Run 14 note). Discrete tasks inside Manufacturing Master Data must be skipped by hand. not verified.
- Task counts for INCR FAs overstate the work: only changed tasks will be touched in live Production Financials. not verified.
- 'Inventory Organizations' FA under Product Management (`ORA_EGP_FA_INVENTORY_ORGANIZAT`) was not selected; inventory orgs are covered through Facilities / Inventory Management as in Run 14. Open question for the reviewer.
