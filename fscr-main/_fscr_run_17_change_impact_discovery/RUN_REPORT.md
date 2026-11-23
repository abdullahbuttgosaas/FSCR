# FSCR Run 17: change-impact discovery (read only)

Pod **ETIA-TEST**, 2026-11-09. Nothing was created, changed or deleted in Oracle. The 12 FSM exports each left one export-process record in Oracle. That is how FSM export works, and it is a read route (same as Run 09).

## Answer

**Use order types for the change-impact test.** FSCR can export them with its own FSM route (`DOO_MANAGE_ORCHESTRATION_LOOKUPS`, CSV), and REST gives the same 62 rows. ETIA-TEST also has a live, active rule that uses one of them: process assignment rule **`ordertype`** sends orders of type **AMNA_STANDARD_ORDERS** to process **DOO_OrderFulfillmentGenericProcess**. So a change to that code has a real, visible effect. Oracle's documentation also names five other places that use order type.

Price lists are the weaker choice:
- FSCR has no export for them, only an FBDI import skill.
- In this pod, 0 pricing strategies and 0 customer pricing definitions are visible, so no "what uses this price list" link can be shown.

FSCR still has **no step that finds what uses a record** (no downstream reader). Only one dependency graph exists, and it is HCM only. Claude has to do the impact part.

## Step 1: Order types

| Check | Result | Source |
|---|---|---|
| a) Skill or guide | Order types are not their own task. They are lookup codes in **ORA_DOO_ORDER_TYPES**, handled by `fscr-main/pillars/scm/order-management/orders/manage-order-lookups/SKILL.md` (task `DOO_MANAGE_ORCHESTRATION_LOOKUPS`, lines 147 and 238–245). No separate "order transaction types" task is in the catalog. | FSCR file |
| b) Export route | **FSM CSV export**: `shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code DOO_MANAGE_ORCHESTRATION_LOOKUPS --data`. Catalog flags: export Y, CSV Y. **REST**: `GET /fscmRestApi/resources/11.13.18.05/standardLookups/ORA_DOO_ORDER_TYPES/child/lookupCodes`. | `knowledge/setup-task-catalog/effective/setupTasksAll.json` |
| c) Export done | `order_types_ETIA-TEST.xlsx`: **62 rows, 14 columns**: LookupType, LookupCode, Meaning, Description, EnabledFlag, StartDateActive, EndDateActive, DisplaySequence, CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate, LastUpdateLogin, Tag. 61 enabled, 1 disabled, 18 with an end date. REST gave the same 62. | `evidence/exports/DOO_MANAGE_ORCHESTRATION_LOOKUPS/`, `evidence/rest/ot_lookup_codes.json` |

## Step 2: Price lists

| Check | Result | Source |
|---|---|---|
| a) Skill or guide | `fscr-main/pillars/scm/order-management/pricing/import-price-lists/SKILL.md` (FBDI import, task `CUSTOM_IMPORT_PRICE_LISTS`). There is also a pricing parent skill, `pricing/SKILL.md`. | FSCR file |
| b) Export route | **No FSM export**: catalog flags are N and N (SKILL.md lines 141–151 say not to use the CSV export route). **REST**: `GET /fscmRestApi/resources/11.13.18.05/priceLists`. FBDI is import only. | FSCR file, catalog |
| c) Export done | `price_lists_ETIA-TEST.xlsx`: **55 rows, 28 columns** (name, ID, type, BU, currency, status, dates, approval status, charge definition, line type, calculation method, audit fields, change type). 54 approved, 1 in progress. 48 SEGMENT, 5 FLOOR, 1 CEILING, 1 GSA. | `evidence/rest/pl_all.json` |

## Step 3: What exists in ETIA-TEST around order types

| Area | Found | Source |
|---|---|---|
| Order types | 62 codes (see step 1) | FSM export + REST |
| Process assignment rules | 1 rule dictionary (AssignLaunch), rule set AssignOrchProcess, **2 rules**: `AssignProcessNameinPackingInstructions10AK` and **`ordertype`** (active; if order type = AMNA_STANDARD_ORDERS then process DOO_OrderFulfillmentGenericProcess) | `evidence/rule_blob_findings.txt` |
| Orchestration processes | 2: CustomDOO_OUStandardOrderProcess_10AK, CustomDOO_ShipOrderGenericProcess (21 steps, 25 step links) | process definitions export |
| Pretransformation, routing and approval rules | Exported. These are the same shared rule file as above; no other rule names order type | 3 exports |
| Processing constraints | 12 constraints, 26 conditions. **None names order type** | constraints export |
| Source systems | 8: OPS, ORA_BM_CPQ, ORA_ELECTRONIC_DOCUMENTS, 123, N_123, LEG1, GPR, ORA_FA_CPQ (4 enabled). 134 organizations, all under OPS | source systems export |
| Web service / connector details | **0 rows** (no external fulfillment endpoint set up) | web service details export |
| Shipping | 10 shipping parameter rows, 11 carriers, 27 pick wave release rules (**0** use an order type) | 3 WSH exports |
| Sales orders | **0 visible** to this user | REST salesOrdersForOrderHub |
| OM system parameters | **Could not read**: the FSM export failed on Oracle's side | `evidence/export_run.log` |
| EBS | **Not found** as a connection. "EBS" appears only in 10 organization descriptions under OPS (for example "Vision Spain-EBS"); these are names, not links | source systems export |
| Oracle Integration (OIC) or other outside systems | **Not found.** Fusion setup exports do not show OIC; no endpoint exists in web service details | as above |

## Step 4: Dependency map: order types

**What order types depend on**

| Item | Tag | Source |
|---|---|---|
| Lookup type ORA_DOO_ORDER_TYPES (user-extensible, level U) | VERIFIED IN ENVIRONMENT | `evidence/rest/ot_lookup_type.json` |
| Apps Common lookups route (no direct REST from the task skill) | FROM FSCR | `manage-order-lookups/SKILL.md:40-43` |
| Oracle ships no order-type values; you must add them | FROM ORACLE DOCUMENTATION | [Use Groups to Manage and Control Sales Orders (26c)](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faiom/use-groups-to-manage-and-control-sales-orders.html) |

**What depends on order types**

| Item | Tag | Source |
|---|---|---|
| Process assignment rule `ordertype` uses AMNA_STANDARD_ORDERS and sends those orders to DOO_OrderFulfillmentGenericProcess | VERIFIED IN ENVIRONMENT | `evidence/rule_blob_findings.txt` |
| Pick wave release rules have a SourceOrderTypeCode column (0 in use) | VERIFIED IN ENVIRONMENT (column); FROM FSCR | `pick-wave-release-rules/ora-resource/ora_dependency_readiness.md:22` |
| Processing constraints (0 use order type here) | VERIFIED IN ENVIRONMENT (0 uses) | constraints export |
| Sales orders store the order type (TransactionTypeCode); 0 visible | VERIFIED IN ENVIRONMENT (0 orders) | `evidence/rest/so_total.json` |
| Reservation priority rules can use order type | FROM FSCR | `orders/reservation-priority-for-sales-orders/SKILL.md:273` |
| Supply chain financial flows: financial qualifier ORDER_TYPE | FROM FSCR | `supply-chain-financial-flows/financial-qualifiers/ora-resource/ora_reference_lookups.md:42` |
| Source order import rejects an order type that is not in the lookup | FROM ORACLE DOCUMENTATION | [26c, Use Groups](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faiom/use-groups-to-manage-and-control-sales-orders.html) |
| Routing rules can choose the fulfillment system by order type | FROM ORACLE DOCUMENTATION | same page |
| Processing constraints can use order type | FROM ORACLE DOCUMENTATION | same page |
| Order search filter | FROM ORACLE DOCUMENTATION | same page |
| Pricing strategy assignment by Order Type Code (needs a service mapping and a matrix class change) | FROM ORACLE DOCUMENTATION | [Assign Pricing Strategy According to Order Type (25d)](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/25d/faupr/assign-pricing-strategy-according-to-order-type.html) |
| Upstream systems such as EBS or CPQ that send orders with an order type would fail import | GUESS (based on the import check above; no such link found in the pod) | — |
| Order reports and analytics grouped by order type | GUESS | — |
| "Subscription" appears in the orchestration process rule file | GUESS (text match only; not confirmed as an order-type use) | `evidence/ref_scan.json` |

**Price lists (short)**

| Item | Direction | Tag | Source |
|---|---|---|---|
| Business unit, currency, charge definition, line type | depends on | VERIFIED IN ENVIRONMENT (columns filled) | `evidence/rest/pl_all.json` |
| Run 09: 1 price list tied to BU FSCRT_Brindle Harbor | depends on | VERIFIED IN ENVIRONMENT (Run 09) | `_fscr_run_09_impact/RUN_REPORT.md` |
| Pricing strategies reference price lists (0 strategies visible) | used by | VERIFIED IN ENVIRONMENT (0); FROM FSCR | `import-price-lists/SKILL.md:355-356` |
| Customer pricing definitions (0 visible) | used by | VERIFIED IN ENVIRONMENT (0) | `evidence/rest/cpd_definitions.json` |
| Strategy assignment by segment, channel and transaction type; OM pricing at run time | used by | FROM ORACLE DOCUMENTATION | [Overview of Oracle Pricing (26a)](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26a/faupr/overview-of-oracle-fusion-pricing.html) |
| CPQ and Subscriptions pricing | used by | GUESS | — |

## Step 5: Recommendation

| Item | Order types (winner) |
|---|---|
| Why | FSCR route exists and works (FSM CSV, with REST as a cross-check). One live, active rule uses a code. Oracle names 5 consumers. Price lists have no FSCR export and no visible consumers. |
| Export route | FSCR task-level FSM CSV export of `DOO_MANAGE_ORCHESTRATION_LOOKUPS`, file `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv`, filtered to ORA_DOO_ORDER_TYPES |
| Sheet columns | The 14 columns in step 1c (the useful ones: LookupCode, Meaning, EnabledFlag, StartDateActive, EndDateActive) |
| Value to change in the sheet | **EnabledFlag Y → N (or set EndDateActive) on AMNA_STANDARD_ORDERS.** It is the only code a live rule uses. Disabling it hits: the process assignment rule (orders stop reaching that process), source order import (orders with that type are rejected), and any routing, constraint or pricing rule that uses it. The lookup is global, so every BU is affected. |
| Compare the edited sheet against | (1) the original sheet, to find what changed; (2) the rule file in the assignment, transformation, routing and approval exports; (3) the pick wave rules and processing constraints exports; (4) sales orders by TransactionTypeCode (REST); (5) the source systems and web service details exports, for outside systems |
| FSCR can do by itself | The exports (FSM CSV), the lookup guidance, a REST client, and sign-in |
| Claude has to do | Find the changed row; search the rule files (108 KB XML) and the other exports for the code; add Oracle's documented consumers; tag each line; write the impact list. FSCR has no downstream impact step. |

## Time and tool calls

| Item | Value |
|---|---|
| Start → finish of the work | 16:45 → about 17:41 (+05:00), about 56 min |
| Of which waiting for sign-in | 16:50 → 17:23, about 33 min. Tries 1–4 failed: a 15-minute timeout, then an old browser tab sent a stale answer. Try 5 worked in the app's browser. |
| Work without the sign-in wait | about 23 min |
| Tool calls | about 72 (counted by hand) |
| FSM exports | 12 started, 11 returned data (OM parameters failed) |

## Checks
- **Read only:** no writes were sent to Oracle (GET reads and FSM exports only).
- **No tokens printed or saved** in the run folder.
- **Original repo not touched:** the run used a copy, `fscr-work17`.
- **Processes:** the sign-in listeners exited by themselves. The browser pane and any leftover processes were closed at the end (see the chat reply).
