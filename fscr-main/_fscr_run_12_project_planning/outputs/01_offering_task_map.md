# Output 1: Offering Task Map (Twelve, SOW 50513scm)

**Who produced it: FSCR + Claude.** Claude chose the offerings and functional areas from the SOW (`work/scripts/selection.json`, each with its SOW clause). FSCR's effective catalog `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json` supplied every task, its code and its display sequence. FSCR's offering-task-map-builder code (`shared/implementation-planning/offering-task-map-builder/scripts/task_to_skill_mapping.py`, which calls `core/runbook/scripts/task_context.py`) resolved each task to an FSCR skill path. Full row-level list: `outputs/01_offering_task_map.csv`; initializer input: `work/identified-task-mapping.json`.

Legend: V = read from an FSCR file or the SOW in this run. NV = Claude's judgment, needs confirmation.

## 1. Offerings to enable

| Offering code | Offering | Status | SOW basis | FAs selected | Tasks | Status of mapping |
|---|---|---|---|---|---|---|
| `ORA_MANUFACTURING_AND_SUPPLY_C` | Manufacturing and Supply Chain Materials Management | new | SCM 2, 6, 7; Fin 4 | 17 | 346 | NV (Claude selection; codes V from catalog) |
| `PO_PROCUREMENT` | Procurement | new | SCM 3, 4, 5; RICE 2 suppliers | 11 | 170 | NV (Claude selection; codes V from catalog) |
| `PIM_PROD_MNG` | Product Management | new | SCM 1 | 2 | 50 | NV (Claude selection; codes V from catalog) |
| `PJF_PROJ_MNG` | Project Financial Management | incremental | Fin 1.1-1.2; Config scope 8 | 1 | 33 | NV (Claude selection; codes V from catalog) |
| `XLE_FINANCIALS_JUR` | Financials | incremental | Fin intro, 2, 5, 7 | 3 | 129 | NV (Claude selection; codes V from catalog) |
| `ORA_GMS_GRANTS_MANAGEMENT` | (no FA mapped) | incremental | Fin intro | 0 | 0 | NV (Claude selection; codes V from catalog) |

`new` = to be opted in for this project. `incremental` = already in Twelve's production (SOW Fin intro); only changes, which the SOW leaves to be decided (intake S5). `ORA_GMS_GRANTS_MANAGEMENT` has no task mapping because its changes are not defined.

## 2. Functional areas and task counts

| Offering | Functional area (code) | Tasks | SOW basis |
|---|---|---|---|
| ORA_MANUFACTURING_AND_SUPPLY_C | Initial Users (`ORA_ASK_INITIAL_USER`) | 6 | Common foundation (all new SCM offerings) |
| ORA_MANUFACTURING_AND_SUPPLY_C | Enterprise Profile (`ORA_ASK_ENTERPRISE_PROFILE`) | 12 | Common foundation |
| ORA_MANUFACTURING_AND_SUPPLY_C | Legal Structures (`ORA_ASK_LEGAL_STRUCTURES`) | 8 | Existing LE reused; verify only (Fin 3) |
| ORA_MANUFACTURING_AND_SUPPLY_C | Financial Reporting Structures (`ORA_ASK_FIN_REPORTING_STRUCT`) | 12 | Existing ledger/COA reused; verify only |
| ORA_MANUFACTURING_AND_SUPPLY_C | Organization Structures (`ORA_ASK_ORGANIZATION_STRUCTURE`) | 4 | Fin 3.1 BU updates |
| ORA_MANUFACTURING_AND_SUPPLY_C | Facilities (`ORA_RCS_FACILITIES`) | 29 | SCM 2.2 plants as inventory orgs; 6.1 plants |
| ORA_MANUFACTURING_AND_SUPPLY_C | Users and Security (`ORA_ASK_USERS_AND_SECURITY`) | 7 | Config scope 12 Security and Roles |
| ORA_MANUFACTURING_AND_SUPPLY_C | Items (`ORA_EGP_FA_ITEMS`) | 28 | SCM 1.1-1.2, 2.1 |
| ORA_MANUFACTURING_AND_SUPPLY_C | Catalogs (`ORA_EGP_FA_CATALOGS`) | 3 | SCM 2.1 item categories (Claude inference) |
| ORA_MANUFACTURING_AND_SUPPLY_C | Inventory Management (`ORA_WSH_INVENTORY_MGMT`) | 63 | SCM 2.1 |
| ORA_MANUFACTURING_AND_SUPPLY_C | Receiving (`WSH_ENABLE_RECEIVING`) | 6 | SCM 2.1 receiving, RTV, putaway |
| ORA_MANUFACTURING_AND_SUPPLY_C | Receipt Accounting (`CMR_RECEIPT_ACCOUNTING`) | 44 | SCM 3.4 PO receipt accounting; Fin 1.2 |
| ORA_MANUFACTURING_AND_SUPPLY_C | Cost Accounting (`CST_DEFINE_COST_MANAGEMENT`) | 63 | SCM 2.3-2.6 |
| ORA_MANUFACTURING_AND_SUPPLY_C | Manufacturing Master Data (`ORA_WIS_COMMON_MFG_WORK_SETUP`) | 26 | SCM 6.1-6.4 (process mfg); 7.3 maintenance work definitions |
| ORA_MANUFACTURING_AND_SUPPLY_C | Structures (`EGO_ADVANCED_PRODUCT_STRUCT`) | 5 | SCM 1.3 manufacturing and maintenance structures |
| ORA_MANUFACTURING_AND_SUPPLY_C | Maintenance Management (`ORA_MNT_MGMT`) | 23 | SCM 7.1-7.7 |
| ORA_MANUFACTURING_AND_SUPPLY_C | Sustainability (`ORA_SUS_SUSTAINABILITY`) | 7 | Fin 4.1-4.2 (FA is in 3 offerings; placed here, NV) |
| PO_PROCUREMENT | Workforce Structures (`ORA_ASK_WORKFORCE_STRUCTURE`) | 4 | Approvals/DOA need jobs/positions (C.5.1 employees exist) |
| PO_PROCUREMENT | Users and Security (`ORA_ASK_USERS_AND_SECURITY`) | 10 | Security and Roles |
| PO_PROCUREMENT | Purchasing Categories (`ORA_PO_PURCHASING_CAT_FA`) | 3 | Purchasing categories (Coupa reuse 3.5) |
| PO_PROCUREMENT | Suppliers (`ORA_EGP_SUPPLIERS`) | 35 | RICE 2 supplier conversion; 5.4 |
| PO_PROCUREMENT | Approval Management (`ORA_PO_APPROVAL_MANAGEMENT_FA`) | 14 | 3.3, 4.2 DOA |
| PO_PROCUREMENT | Procurement Foundation (`ORA_PO_PROC_FOUNDATION_FA`) | 16 | Procurement BU, agents, line types |
| PO_PROCUREMENT | Purchasing Foundation (`ORA_PO_PURCHASING_FOUNDATION`) | 11 | 4.1 |
| PO_PROCUREMENT | Procurement Transaction Account Rules (`ORA_PO_PRC_TRX_ACC_RULES_FA`) | 9 | 3.4 project and non-project accounting rules |
| PO_PROCUREMENT | Self Service Procurement (`PO_SSP_DEPLOYED`) | 11 | 3.1-3.2 |
| PO_PROCUREMENT | Supplier Portal (`PO_SUP_PORTAL_DEPLOYED`) | 7 | 5.1-5.4 |
| PO_PROCUREMENT | Payables (`FIN_PAYABLES_DEPLOYED`) | 50 | Payables incremental (Config scope 5) |
| PIM_PROD_MNG | Inventory Organizations (`ORA_EGP_FA_INVENTORY_ORGANIZAT`) | 24 | SCM 2.2 (inventory orgs) |
| PIM_PROD_MNG | Item Organizations (`ORA_EGP_FA_ITEM_ORGANIZATIONS`) | 26 | Item master org (E7 open) |
| PJF_PROJ_MNG | Project Costing Base (`ORA_PJC_PROJ_COSTING_BASE_FA`) | 33 | Project commitments, PO receipts and AP invoices on projects |
| XLE_FINANCIALS_JUR | General Ledger (`ORA_FIN_GENERAL_LEDGER`) | 42 | Fin 7 GL/SLA incremental |
| XLE_FINANCIALS_JUR | Fixed Assets (`FIN_FIXED_ASSETS_DEPLOYED`) | 47 | Fin 2.1 Asset Management incremental |
| XLE_FINANCIALS_JUR | Expenses (`FIN_EXPENSES_DEPLOYED`) | 40 | CONDITIONAL: Fin 5.1 design session decides |

Excluded functional areas and the reason for each are listed in `work/scripts/selection.json` (`excluded`).

## 3. Totals

| Measure | Value | Status |
|---|---|---|
| Task rows (task occurrences per offering/FA) | 728 | V (counted) |
| Unique task codes | 514 | V (counted) |
| Rows with an FSCR pillar skill | 297 | V (FSCR code) |
| Rows routed to manual (no FSCR task skill) | 431 | V (FSCR code) |
| Sequence source: catalog display sequence | 727 | V |
| Sequence source: functional-area tail (no catalog sequence) | 1 | V |
| Source layer release / pre_release-custom | 727 / 1 | V |
| Task names with exactly 1 / 0 / >1 matches in effective setupTasksAll.json | 728 / 0 / 0 | V |

`Resolver Sequence` was assigned **by Claude** following the resolver's written method (catalog order within offering/FA, then functional-area tail). It is **not** output from FSCR's `task-dependency-resolver`, which has no script and needs FSM/BOSS (see Output 3, section 2).

## 4. SOW items with no clear catalog task (NV)

| SOW item | Note |
|---|---|
| 7.5 Meters, 7.6 Maintenance Programs, 7.7 Installed Base | No task named meter, maintenance program or installed base was found in the selected offerings' FAs by a name search. These are probably transactional/master data, not setup tasks. NV |
| Reporting approach (Fin 6) | Advisory deliverable; no setup task |
| RICE 1 printable PO | BI Publisher build; no setup task |
| Training (Change Mgmt) | Not a setup task |

## 5. Project workspace initializer dry run

```text
$ python core/project-mgmt/project-workspace-initializer/scripts/initialize_project_workspace.py --customer "Twelve Benefit Corporation" --implementation-objective "Implement Oracle Cloud SCM for Twelve (SOW 50513scm)" --pillar SCM --pillar ERP --offering ... (6) --country US --identified-task-mapping ../work/identified-task-mapping.json --no-create-runbook --dry-run
Would create project workspace: project\twelve-sow-50513scm-oracle-cloud-scm
exit code: 0
```

Initializer catalog validation (exact-name, `knowledge/setup-task-catalog/effective/setupTasksAll.json`): matched 728, unmatched 0, ambiguous 0, total 728. V (run in this session)

### Initializer findings

| Finding | Status |
|---|---|
| **The dry run now passes** (exit code 0). Run 11b stopped at `Identified task mapping must contain a non-empty tasks array.`; this run supplied 728 rows. | V |
| `--dry-run` writes nothing. `project/` still holds only `README.md`, `_template` and `draft-impl-project-20261028`. It would create `project/twelve-sow-50513scm-oracle-cloud-scm`. | V |
| The initializer validates task **names only** (exact name against `effective/setupTasksAll.json`): 728/728 matched. It does **not** check offering, functional area or `Resolver Sequence`. | V (code read: `validate_identified_task_mapping`) |
| `Resolver Sequence` is checked only later, by `create_project_runbook.py` (unique positive integers). That step was not run: dry-run stops before it, and the SKILL.md says it runs after initialization. | V (code read) |
| SKILL.md gate: "before writing the mapping, read the persisted `setup_task_sequence`". The resolver could not produce one (no script, needs FSM/BOSS), so under the skill's own written gate this mapping **should not be used for a Run Book plan**. The script does not enforce that gate. | V (SKILL.md text) |
| Rows with no FSCR task skill (431) would route to `shared/common/manual-tasks` (FSCR task-context policy). | V (FSCR code output) |
| Runtime: FSCR's skill-path resolution took 11 min 4 s for 728 tasks (it re-reads the catalog and globs `pillars/**` for every task). | V (timed) |
