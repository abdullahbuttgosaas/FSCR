# FSCR slide-claim verification — 2026-10-29

Read-only check of `E:\GoSaaS\fscr-main\fscr-main`. No Oracle calls, no repo edits. Counting scripts were run from a scratch folder outside the repo.

## Repository version

- No `.git` folder (`git rev-parse HEAD` → "not a git repository"). There is no commit id.
- All 6,082 non-project, non-`.pyc` files carry date **2026-10-28**, the date this copy was unpacked.
- Three files were changed **by our own sessions** on 2026-10-28 and are not original:
  - `core/auth/fusionEnv.properties` (filled in, 15:40)
  - `core/data-loader/config/env.properties` (`runID` set by Run Book creation, 15:53)
  - `pillars/erp/financials/customer-billing/manage-receivables-payment-terms/scripts/payment_terms_fsm_package.py` (order-check patch, 15:59)
- Newest original file time: 2026-10-28 15:24 (e.g. `shared/validation/setup-data-validator/SKILL.md`).

## Counting definitions (repeatable)

- **SKILL.md files:** every `SKILL.md` under the repo, excluding `project/`.
- **Leaf skill:** a SKILL.md whose folder contains no other SKILL.md folder below it. **Guide skill:** one that does. (An earlier session reported 932 leaves using a looser file-count rule; 934 is the strict definition.)
- **Type / mode:** the `type:` and `execution_mode:` frontmatter values.
- **Skill has a task:** `task_code:` in a SKILL.md frontmatter (definition A), or in any pillar `.md` frontmatter, which includes task guide files such as `manage-business-unit.md` (definition B).
- **Own scripts:** a `.py`, `.js`, `.cjs`, `.sh` or `.ps1` file inside the skill's own `scripts/` folder.
- **Create marker:** the text `fscr-supported-operations:` in SKILL.md.
- **Tests:** files in the skill folder whose relative path contains test/tests/fixture(s)/golden/test-catalog as a path or name token.
- **Registry ready:** every node in every task of `ora_rule_registry.json` has `readiness.status == "ready"`.

## A. README

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | "separately released sample and reference material", not a product feature, not covered by support | VERIFIED | `README.md:3-5`: "FSCR is separately released sample and reference material for planning and configuring Oracle Fusion Cloud implementations. It is not an Oracle Fusion Cloud product feature and is not covered by Fusion Cloud product support." |
| 2a | Calls itself a scaffold repository | VERIFIED | `README.md:168`: "This is a scaffold repository." |
| 2b | Requires 26D + 16 Oct 2026 Weekly Maintenance Pack or higher | VERIFIED | `README.md:61-63`: "FSCR skills require Oracle Fusion Applications Release 26D with the 16 October 2026 Weekly Maintenance Pack for Fusion Applications Update 26D, or a higher release or maintenance pack." |
| 2c | Licence UPL 1.0 | VERIFIED | `README.md:17`: "FSCR is released under the Universal Permissive License (UPL), Version 1.0." |
| 2d | Tested with a named model | VERIFIED | `README.md:87`: "FSCR has been tested with the GPT 5.6 Terra Medium model." |
| 3a | Four execution modes | VERIFIED | `README.md:157-160`: `advisory` "Produces guidance for implementors to execute offline."; `assisted` "Generates artifacts or recommendations that require human review."; `automated` "Performs approved actions directly through APIs, loaders, or jobs."; `hybrid` "Combines automated discovery or preparation with human approval." |
| 3b | Review generated plans before running | VERIFIED | `README.md:10-11`: "Review generated plans, requests, and changes before running them in your environment." |

## B. Size and shape

| # | Claim | Verdict | Evidence (script result) |
|---|---|---|---|
| 4a | Total SKILL.md | VERIFIED: **1,126** | Count of SKILL.md excluding `project/` |
| 4b | Leaf vs guide | VERIFIED: **934 leaf, 192 guide** | Strict leaf rule above |
| 4c | By top folder (all / leaf) | VERIFIED | core 33/31, shared 82/81, router 3/3, pillars/erp 103/84, pillars/scm 243/202, pillars/hcm 457/359, pillars/cx 196/166, pillars/common 9/8 |
| 4d | By type (all / leaf) | VERIFIED | planning 851/701, orchestration 141/102, import 63/60, advisory 32/32, assessment 14/14, verification 14/14, validation 5/5, export 5/5, support 1/1 |
| 4e | By execution_mode (all / leaf) | VERIFIED | assisted 899/718, hybrid 192/181, advisory 28/28, automated 7/7 |
| 5a | Catalog file and total tasks | VERIFIED: **2,616** | `knowledge/setup-task-catalog/effective/setupTasksAll.json` → `items` (2,616 distinct TaskCode; file says "release - pre_release.removals + pre_release.items + custom.items") |
| 5b | Tasks supporting FSM CSV export/import | VERIFIED: **2,076** (CSVExportImportSupportedFlag = Y); 2,121 have ExportImportSupportedFlag = Y | Same file |
| 5c | Tasks with a skill | Two definitions | A (SKILL.md `task_code`): **701** distinct codes, all in the catalog. B (any pillar `.md` `task_code`): **848** |
| 5d | Catalog tasks with no skill | Two definitions | A: **1,915**. B: **1,768** |
| 6a | Number of `ora_rule_registry.json` | VERIFIED: **592** repo-wide (excl. project); **588** under `pillars/` | File count |
| 6b | Registries marked ready | VERIFIED: **578 of 592** have every node ready; 654 of 676 registry tasks ready | Node `readiness.status` |

## C. "Can create" counts

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| C(i)-a | Skills whose metadata DECLARES a route (`dataloader_import_mode` ∈ FSM, FBDI, HDL, CXIMPORT, REST, ESS) | **720** (FSM 424, REST 222, HDL 41, FBDI 16, ESS 12, CXIMPORT 5) | Frontmatter count. Declaring a route ≠ having code for it |
| C(i)-b | Skills with a non-empty `side_effects` list | **310** | Frontmatter count |
| C(i)-a∪b | Either | **834** | Union |
| C(ii) | Own script + create marker + `e2e-adapter.json` + `ora_rule_registry.json` | **16** | 17 skills have the marker; the 17th, `expenses/manage-auto-submission-and-matching-options`, has no e2e adapter |
| C(iii) | Of (ii), with any tests | **1** | `expenses/manage-conversion-rates-and-policies` (`e2e-test-catalog.json` with 24 cases, plus `references/create-test-lifecycle.md`) |
| 8 | All (ii) skills are in ERP Financials | VERIFIED: **16 of 16** | Paths all under `pillars/erp/financials/` |

### 7. The 16 skills in (ii)

All 16 declare `dataloader_import_mode: "FSM"` (FSM CSV import through `core.data-loader`). "Header pin" means the adapter fails when a CSV's header list differs from `e2e-adapter.json` (`"header order differs from e2e-adapter.json"`). "Order pin" means a fixed entity-order list in the scripts.

| Skill (pillars/erp/financials/…) | Task code | Creates | Built on | e2e readiness | Header pin | Order pin |
|---|---|---|---|---|---|---|
| customer-billing/manage-autoaccounting-rules | AR_MANAGE_AUTOACCOUNTING_RULES | AutoAccounting rules | 11.13.27.01.0 | 8 ready | Yes | No |
| customer-billing/manage-autoinvoice-grouping-rules | AR_MANAGE_AUTOINVOICE_GROUPING_RULES | AutoInvoice grouping rules | 11.13.26.10.0 | 8 ready | Yes | No |
| customer-billing/manage-receivables-payment-terms | AR_MANAGE_RECEIVABLES_PAYMENT_TERMS | Receivables payment terms | 11.13.26.10.0 | 8 ready | Yes | **Yes in the original file**; removed by our local patch |
| customer-billing/manage-remit-to-addresses | AR_MANAGE_REMIT_TO_ADDRESSES | Remit-to addresses | 11.13.26.10.0 | 8 ready | Yes | No |
| customer-billing/manage-transaction-sources | AR_MANAGE_TRANSACTION_SOURCES | Transaction sources | 11.13.26.10.0 | 8 ready | Yes | No |
| customer-billing/manage-transaction-types | AR_MANAGE_TRANSACTION_TYPES | Transaction types | 11.13.26.10.0 | 8 ready | Yes | No |
| customer-payments/manage-receipt-classes-and-methods | AR_MANAGE_RECEIPT_CLASSES_AND_METHODS | Receipt classes and methods | 11.13.26.07.0 | 8 ready | Yes | No |
| customer-payments/manage-receipt-sources | AR_MANAGE_RECEIPT_SOURCES | Receipt sources | 11.13.26.07.0 | 8 ready | Yes | No |
| expenses/manage-conversion-rates-and-policies | EXM_MANAGE_CONVERSION_RATES_AND_POLICIES | Conversion-rate options and tolerances | 11.13.27.01.0 | 10 ready | Yes | No |
| payables/manage-bank-charges | ORA_AP_MANAGE_BANK_CHARGES | Bank charges | 11.13.26.10.0 | **6 blocked**, 1 ready, 1 n/a | Yes | No |
| payables/manage-common-options-for-payables-and-procurement | AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT | Common options row | 11.13.26.10.0 | 8 ready | Yes | No |
| payables/manage-invoice-options | AP_MANAGE_INVOICE_OPTIONS | Invoice options row | 11.13.27.01.0 | 8 ready | Yes | No |
| payables/manage-payables-calendars | AP_MANAGE_PAYABLES_CALENDARS | Period types and periods | 11.13.26.10.0 | 8 ready | Yes | No |
| payables/manage-payment-options | AP_MANAGE_PAYMENT_OPTIONS | Payment options row | 11.13.26.04.0 | 8 ready | Yes | No |
| payables/manage-payment-terms | AP_MANAGE_PAYMENT_TERMS | Payables payment terms | 11.13.26.10.0 | 8 ready | Yes | No |
| receivables/manage-receivables-system-options | AR_MANAGE_RECEIVABLES_SYSTEM_OPTIONS | System options row | 11.13.26.10.0 | 8 ready | Yes | No |

**About the skills you previously excluded:**
- **All six belong to (ii)** by the definition: Bank Charges, Receivables System Options, Invoice Options, Payment Options, Common Options and AutoAccounting.
- **Bank Charges:** its own e2e adapter marks 6 capabilities blocked.
- **AutoAccounting:** built on 27.01.
- **The four options skills:** my earlier "update-only" label is **CORRECTED**. All four carry `fscr-supported-operations: create, update`.
  - Receivables System Options says "Every create requires an explicit nonblank `RuleSetName`" (SKILL.md:156).
  - Payment Options says "For every Payment Options create or update, validate the complete resulting row" (SKILL.md:205).
  - Invoice Options and Common Options: CANNOT VERIFY from the repo whether create is meaningful beyond the marker.

## D. Order Management (DOO_ORCHESTRATION)

Source: `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json` → `offerings.DOO_ORCHESTRATION`. Route = the first matching skill's `dataloader_import_mode`.

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 9a | Task count | VERIFIED: **166** distinct tasks | By area: Orders 42, Channel Revenue Management 35, Items 25, Pricing 17, Customers 13, Enterprise Profile 12, Users and Security 7, Initial Users 6, Organization Structures 4, Catalogs 3, Application Extensions 2 |
| 9b | Tasks with a skill | VERIFIED: **53 with, 113 without** | SKILL.md `task_code` match (definition A) |
| 9c | Route totals | VERIFIED | FSM 27, REST 17, ESS (job) 3, FBDI 2, CX Import 2, no route declared 2, **no skill 113** |
| 9d | Scripts among the 53 | VERIFIED: **0 with a create marker**; 1 with its own script | The only script is `cx/customer-data-management/enterprise-profile/run-maintain-geography-name-referencing` (type verification). Full per-task list in the appendix |
| 10 | OM "can create" skills | VERIFIED: **guidance only** | None has its own `scripts/` folder or a create marker. Each lists `core.data-loader` (and some `core.fusion-api.rest-api-client`) as dependencies |
| 11 | Order Types | VERIFIED | Folder `pillars/scm/order-management/orders/manage-order-lookups` contains **only SKILL.md**: `type: "planning"`, `execution_mode: "assisted"`, `side_effects: []`. SKILL.md:130-133: "Route each Manage Order Lookups request to `core.fusion-api.apps-common` … Do not select a direct REST endpoint from this task skill." The generic call is in `core/fusion-api/apps-common/lookups/references/standard-lookups.md:18`: "Lookup code \| List, create \| `GET`, `POST` \| `/fscmRestApi/resources/11.13.18.05/standardLookups/{LookupType}/child/lookupCodes`". No `.py` file anywhere in the repo contains `ORA_DOO_ORDER_TYPES` or `order_type`, so **no ready script creates an order type** |
| 12 | Business Units | VERIFIED | No dedicated skill folder. `FUN_MANAGE_BUSINESS_UNIT` is covered by the functional-area skill `pillars/erp/financials/organization-structures/SKILL.md` (planning/assisted) and its task file `manage-business-unit.md:2` (`task_code: "FUN_MANAGE_BUSINESS_UNIT"`). REST block, `ora-resource/ora_rest_execution.md:3`: "Direct REST writes remain unavailable." Allowed CSV route, SKILL.md:154: "Create the BU through template preparation, Data Loader preflight, Task Hook and the immutable approved FSM archive." |
| 13 | Price Lists | VERIFIED | Folder has only `SKILL.md` and `ora-resource/`: **no scripts, no `tests/` folder**, although SKILL.md:394 cites `tests/golden-scenarios.md`. Route: `dataloader_import_mode: "FBDI"`, `type: "import"`, `execution_mode: "hybrid"`. Needs a populated `PriceListsImportBatchTemplate.xlsm` (SKILL.md:171, 195). Read-back: only an **optional** verification through `customerPricingDefinitions` (SKILL.md:100, 341-358); there is no price-list read-back |
| 14a | manage-customer-uploads | VERIFIED | `type: "planning"`, `execution_mode: "assisted"`, `dataloader_import_mode: "FBDI"`, business object `customers` (SKILL.md:154). Self-blocks: SKILL.md:302 "never uploads, submits ESS, queries Fusion, rolls back or retries."; SKILL.md:351 "The current helper continues to return nonzero from review because hard live gates remain open even when the record matches."; `scripts/customers_package.py:4` "It has no authentication, upload, ESS, or import capability." Contacts: SKILL.md:187 "Contacts, Reference Accounts and Customer Bank Accounts are deferred." Rollback: SKILL.md:374 "no inverse-import rollback is promised." Person customers: no explicit statement; the asset contracts contain no `PERSON_` fields, so whether persons are supported is NOT VERIFIABLE from the repo |
| 14b | import-trading-community-data | VERIFIED | `type: "import"`, `execution_mode: "hybrid"`, `dataloader_import_mode: "CXIMPORT"`. SKILL.md:114: "Uses the core CX adapter to upload an explicitly approved immutable CSV group and create or activate one Import Management activity." Limit, SKILL.md:287: "`ZCA_CUSTOMER` results in sales `SALES_ACCOUNT` usage and does not establish financial `CUSTOMER` usage." SKILL.md:285: "route creation of the financial customer account through its owning workflow" |
| 14c | Skill for AR_MANAGE_CUSTOMERS | VERIFIED: **none** | The code appears only in the four catalog JSON files; no `.md` under `pillars/` mentions it |

## E. Other SCM (leaf skills; scripts = own `scripts/` folder; marker = create marker)

| # | Area | Verdict | Leaf skills / with scripts / with create marker |
|---|---|---|---|
| 15 | Inventory Management | VERIFIED | 26 / 0 / 0 |
| 15 | Procurement | VERIFIED | 48 / 1 / 0 (configure-new-supplier-notification, REST) |
| 15 | Product Management | VERIFIED | 41 / 1 / 0 (manage-product-management-indexes, REST) |
| 15 | Manufacturing (master data) | VERIFIED | 9 / 0 / 0 |
| 15 | Cost Accounting | VERIFIED | 17 / 2 / 0 (cost-organizations, cost-profiles; `side_effects` empty) |
| 15 | Shipping | VERIFIED | 8 / 0 / 0 |
| 15 | Receiving | VERIFIED | 2 / 0 / 0 |
| 15 | Logistics | VERIFIED: no folder named logistics; the closest is Carriers & Transit Times | 2 / 0 / 0 |
| 15 | Supply Chain Planning | VERIFIED | 4 / 1 / 0 (load-planning-data-from-files, FBDI) |
| 15 | Also | VERIFIED | Facilities 6/0/0, Supply Chain Financial Flows 10/0/0, Maintenance 3/0/0, Advanced Inventory 2/0/0, Landed Cost 4/0/0 |

## F. Quality and portability

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 16 | Tests in the repo | VERIFIED: **10 test/fixture files across 5 skills** | (1) `expenses/manage-conversion-rates-and-policies/e2e-test-catalog.json`: 24 cases, 93 variants (offline 65, static 17, live-readonly 8, live-mutation 3), plus `references/create-test-lifecycle.md`. (2) `erp/risk-and-security/activate-algorithms/.../fixtures/mock-active-modules.json` (mock data). (3) `hcm/hcm-tool/profile-management-content-library-configuration`: test-batch schemas, a test-batch runner script and a test-only batch reference. (4) `hcm/hcm-tool/profile-management-data-load-migration-and-maintenance/references/skill-wiki-test-prompts.md`. (5) `hcm/performance-management/.../performance-templates`: `related_fixture_routes.json` and `related_fixture_rest.py`. **No unit-test framework (pytest/unittest) folders were found** |
| 17 | Adapter release pinning | VERIFIED: **6 of 16 differ from 11.13.26.10.0** | 27.01.0: AutoAccounting, Conversion Rates, Invoice Options. 26.07.0: Receipt Classes & Methods, Receipt Sources. 26.04.0: Payment Options. The other 10 were built on 26.10.0 |
| 18 | Generator in repo | VERIFIED: **not in the repo** | Referenced 32 times, e.g. `customer-billing/manage-autoaccounting-rules/e2e-adapter.json:101`: `"generator": "fscr-deliverable-builder/scripts/generate_fsm_task_adapter.py"`. No file or folder with that name exists |
| 19a | Windows requirements | VERIFIED (code only) | `pywin32` is required only in code: `core/auth/fusion-oauth-authentication/scripts/windows_private_storage.py:4` "pywin32 is required." No README or SKILL.md lists pywin32. Docs mention Windows only for secret storage (`fusion-oauth-authentication/SKILL.md:220, 231`) and private-storage controls (`onboarding/references/pkce-login-flow.md:86`) |
| 19b | Console encoding / Git Bash path problems documented | VERIFIED: **not documented** | No `cp1252`, `PYTHONIOENCODING`, Git Bash, MSYS or path-conversion text in any `.md` (one unrelated `UnicodeEncodeError` handler in a customer script) |
| 20 | Prerequisites and gates | VERIFIED | OAuth public client, `README.md:41`: "Creating a public OAuth client (**Mobile Application**)". Properties, `README.md:43`: "Populating `core/auth/fusionEnv.properties`". Trust, `fusion-oauth-authentication/SKILL.md:162`: "Login requires a trust policy enrolled separately from caller-selectable properties." Run Book, `router/implementation-router/SKILL.md:81`: "Do not route to Data Loader or another Fusion-submission workflow until `runbook_control.status` is `active`." Design confirmation, `manage-receivables-payment-terms/SKILL.md:227`: "Bind the confirmation to the preview's design SHA-256 and both source-package hashes." Standalone approval, `core/data-loader/SKILL.md:66`: "An explicit user request to upload, initiate, submit, load, or create data authorizes validation, not submission by itself." and "Submit only after a later standalone approval of the exact validated source…" |
| 21 | Configuration packages rejected | VERIFIED, **but in one skill only** | Only `hcm/global-payroll/payroll-balances/balance-groups`: `ora_input_validation.md:21` "Reject an XML configuration package containing ASM_MIG_PROCESS_INFO.xml … as FSM_CONFIGURATION_PACKAGE_UNSUPPORTED"; `ora_error_handling.md:7` "a limitation of the current FSCR task CSV adapter". No repo-wide rule |

## G. Reusable parts

| # | Part | Verdict | Where / size / contents |
|---|---|---|---|
| 22 | Setup task catalog | Exists | `knowledge/setup-task-catalog/` (15 MB, 26 files): release, pre_release, custom and effective layers; 2,616 tasks with flags; offering → functional area → task hierarchy; a local HTML hierarchy browser |
| 22 | Dependency graphs | Exists, **HCM only** | `knowledge/dependency-graphs/hcm-dependency-graph.json` (856 KB, 86 nodes, 281 edges) |
| 22 | Rule files per task | Exists | `pillars/**/ora-resource/` (588 registries under pillars): input validation, dependencies, lookups, defaults, design rules, error handling |
| 22 | Reference lookups | Exists | 515 `ora_reference_lookups.md` files under pillars |
| 22 | FSM REST client | Exists | `core/fusion-api/fsm-rest-client` (176 KB, 26 files; BOSS/FSM read scripts) and `core/fusion-api/rest-api-client` (92 KB, 16 files) |
| 22 | Setup export/import | Exists | `shared/setup-export` (169 KB, 18 files) and `shared/setup-import` (133 KB, 17 files): task, functional-area, offering and generic FSM CSV levels |
| 22 | Data-loader scripts | Exists | `core/data-loader/scripts` (473 KB, 13 files: upload/initiate, status, validation, sample generation) plus `task-hook` and `task-validator` (56 KB) |
| 22 | Validators | Exists, **thin** | `shared/validation` (28 KB, 5 files, 4 validator skills; one script: `setup_data_validation_context.py`) |
| 22 | Project workspace template | Exists, **small** | `project/_template` (13 KB, 4 files) plus the initializer scripts in `core/project-mgmt` |

## H. Receivables Payment Terms live test (saved records only)

| # | Claim | Verdict | Evidence (`project/draft-impl-project-20261028/`) |
|---|---|---|---|
| 23a | Task code | VERIFIED | `state/runs/20261028-payment-term-create-verified.json`: `"task_code": "AR_MANAGE_RECEIVABLES_PAYMENT_TERMS"` |
| 23b | What was created | VERIFIED | `"term": {"name": "ZZFSCR N45 4203", "set_code": "COMMON"}`. Reconcile persisted rows: 1 header, 2 lines, 1 translation, 0 discounts |
| 23c | Import times | VERIFIED | `"initiated": "2026-10-28T11:02:29Z"`, `"succeeded_observed": "2026-10-28T11:04:26Z"` (about 2 min). Process result: Succeeded, 3 objects, 3 loaded, 0 failed, 0 warnings. IDs: UCMFA04512183 / 4418138 / FSM 4418141 |
| 23d | Reconcile result | VERIFIED | `artifacts/.../reconcile-result.json`: `"status": "verified"`, `"mismatches": []`. The run record also says `"other_terms_unchanged": true` |
| 23e | The one local patch | VERIFIED | `"local_patch": "payment_terms_fsm_package.py: fixed PAYMENT_TERM_OBJECT_ORDER replaced by template/baseline order equality"`. That is, the per-package check of a fixed entity order was removed and a template-vs-baseline order-equality check was added. File modified 2026-10-28 15:59 |
| 23f | Term still exists | **CANNOT VERIFY FROM THE REPO** | The records prove presence only at the verification export (process 100004731498215, file written 2026-10-28 16:05 local). Showing it still exists needs a fresh read-only export or GET from Oracle |

## Do NOT put on a slide

- **"FSCR creates Order Management setup"**: no Order Management skill has its own script or create marker; all 53 are guidance pointing to generic services.
- **"FSCR is tested"**: 1 of the 16 create-capable skills has a test catalog; there is no unit-test suite.
- **"The e2e adapters are live-proven / ready"**: "ready" is a self-label. AR Payment Terms was "ready" yet failed on ETIA-TEST until patched. No repo file records a live run for the others.
- **"FSCR works on any 26D pod out of the box"**: all 16 adapters pin exact CSV headers to a snapshot, 6 snapshots are not 26.10.0, and the generator to rebuild them is missing.
- **"AR Payment Terms works unmodified"**: it needed one local code patch.
- **"FSCR rejects configuration packages"**: true for one HCM skill only.
- **"FSCR supports Windows"** (as a documented feature): pywin32 is required only in code; encoding and Git Bash issues are undocumented.
- **"The test term still exists"**: not verifiable from saved records.
- **Single unlabelled numbers for "skills that create"**: say which definition. 720 declare a route, 310 declare side effects, 16 have the full adapter set.
- **"Customers: organization only"**: the repo has no explicit statement; it can only be inferred from missing person fields.
- **932 leaf skills** (an earlier figure): use 934 with the strict definition.
- **Any git commit id**: none exists.

## Appendix: Order Management tasks with a skill (53)

| Functional area | Task code | Skill path (pillars/�) | Type | Mode | Route | Own scripts | Create marker |
|---|---|---|---|---|---|---|---|
| Initial Users | PER_USER_AND_ROLES_SYNCHRONIZE_DETAILS | cx/field-service/users-and-security/run-user-and-roles-synchronization-process | planning | assisted | ESS | 0 | no |
| Initial Users | ORA_ASE_IMPORT_USERS_AND_ROLES | cx/field-service/users-and-security/import-users-and-roles-into-application-security | planning | assisted | ESS | 0 | no |
| Initial Users | ORA_ASE_IMPORT_USER_LOGIN_HISTORY | cx/field-service/users-and-security/import-user-login-history | planning | hybrid | ESS | 0 | no |
| Enterprise Profile | FND_MANAGE_REFERENCE_DATA_SETS | hcm/goal-management/goal-management-common/manage-reference-data-sets | planning | assisted | FSM | 0 | no |
| Enterprise Profile | HZ_MANAGE_GEOGRAPHIES | cx/customer-data-management/enterprise-profile/manage-geographies | import | hybrid | CXIMPORT | 0 | no |
| Enterprise Profile | HZ_RUN_MAINTAIN_GEOGRAPHY_NAME_REFERENCING | cx/customer-data-management/enterprise-profile/run-maintain-geography-name-referencing | verification | hybrid | (none) | 1 | no |
| Enterprise Profile | ORA_HZ_RUN_GEOCODE_LOADER | cx/customer-data-management/enterprise-profile/run-geocode-generation | import | hybrid | (none) | 0 | no |
| Enterprise Profile | PER_MANAGE_ENTERPRISE_HCM_INFORMATION | hcm/global-human-resources/enterprise/manage-enterprise-hcm-information | planning | assisted | REST | 0 | no |
| Enterprise Profile | PER_MANAGE_LOCATIONS | hcm/global-human-resources/locations/manage-locations | planning | assisted | REST | 0 | no |
| Organization Structures | EGP_MANAGE_ITEM_ORGANIZATIONS | scm/manufacturing-and-supply-chain-materials-management/facilities/manage-item-organizations | planning | assisted | REST | 0 | no |
| Users and Security | ASXS_MANAGE_JOB_ROLES | common/security-console/manage-job-roles | orchestration | hybrid | FSM | 0 | no |
| Users and Security | ASXS_MANAGE_DUTIES | common/security-console/manage-duties | orchestration | hybrid | FSM | 0 | no |
| Users and Security | ASXS_MANAGE_DATA_SECURITY_POLICIES | common/security-console/manage-data-security-policies | orchestration | hybrid | FSM | 0 | no |
| Users and Security | PER_MANAGE_HCM_ROLE_PROVISIONING_RULES | common/security-console/manage-hcm-role-provisioning-rules | orchestration | hybrid | FSM | 0 | no |
| Users and Security | PER_MANAGE_USERS | cx/service/users-and-security/manage-users | planning | assisted | CXIMPORT | 0 | no |
| Items | INV_MANAGE_UNITS_OF_MEASURE | scm/product-management/items/manage-units-of-measure | planning | assisted | REST | 0 | no |
| Items | EGP_MANAGE_PRODUCT_VALUE_SETS | scm/product-management/items/manage-product-and-child-value-sets | planning | assisted | FSM | 0 | no |
| Items | ORA_EGP_MANAGE_ATTACH_CAT_FOR_PIM | scm/product-management/items/manage-attachment-categories-for-product-management | planning | assisted | FSM | 0 | no |
| Items | EGP_MANAGE_OPERATIONAL_ATTRIBUTES_GROUPS | scm/product-management/items/manage-operational-attributes-groups | planning | assisted | REST | 0 | no |
| Items | EGP_MANAGE_ITEM_STATUSES | scm/product-management/items/manage-item-statuses | planning | assisted | REST | 0 | no |
| Items | EGP_MANAGE_CROSS_REFERENCE_TYPES | scm/product-management/items/manage-cross-reference-types | planning | assisted | FSM | 0 | no |
| Items | EGP_MANAGE_ITEM_DESCRIPTIVE_FLEXFIELDS | scm/product-management/items/manage-item-descriptive-flexfields | planning | assisted | FSM | 0 | no |
| Items | EGP_IMPORT_ITEMS | scm/product-management/items/import-items | import | hybrid | FBDI | 0 | no |
| Items | EGP_MANAGE_RELATED_ITEM_SUBTYPES | scm/product-management/items/manage-related-item-subtypes | planning | assisted | FSM | 0 | no |
| Items | EGP_ITEM_RELATIONSHIP_DFFS | scm/product-management/items/manage-item-relationship-descriptive-flexfields | planning | assisted | FSM | 0 | no |
| Items | EGP_TRADING_PARTNER_ITEMS_DFFS | scm/product-management/items/manage-trading-partner-item-descriptive-flexfields | planning | assisted | FSM | 0 | no |
| Items | RCS_MANAGE_UOM_INTER_CLASS_CONV | scm/product-management/items/manage-units-of-measure-for-interclass-conversion | planning | assisted | REST | 0 | no |
| Items | RCS_MANAGE_UOM_INTRA_CLASS_CONV | scm/product-management/items/manage-units-of-measure-for-intraclass-conversion | planning | assisted | REST | 0 | no |
| Catalogs | EGP_MANAGE_DEFAULT_CATALOGS | scm/product-management/catalogs/manage-functional-area-catalogs | planning | assisted | FSM | 0 | no |
| Catalogs | EGP_MANAGE_CATALOG_ATTRIBUTES | scm/product-management/catalogs/manage-catalog-descriptive-flexfields | planning | assisted | FSM | 0 | no |
| Catalogs | EGP_MANAGE_CATEGORY_ATTRIBUTES | scm/product-management/catalogs/manage-category-descriptive-flexfields | planning | assisted | FSM | 0 | no |
| Customers | HZ_MANAGE_TRADING_COMMUNITY_SOURCE_SYSTEMS | cx/customer-data-management/trading-community-foundation/manage-trading-community-source-systems | orchestration | hybrid | FSM | 0 | no |
| Customers | HZ_MANAGE_SOURCE_SYSTEM_ENTITIES | cx/customer-data-management/trading-community-foundation/manage-source-system-entities | orchestration | hybrid | FSM | 0 | no |
| Customers | HZ_MANAGE_SOURCE_SYSTEM_LOOKUPS | cx/customer-data-management/trading-community-foundation/manage-source-system-lookups | planning | assisted | FSM | 0 | no |
| Customers | HZ_MANAGE_SOURCE_SYSTEM_DESCRIPTIVE_FLEXFIELDS | cx/customer-data-management/trading-community-foundation/manage-source-system-descriptive-flexfields | planning | assisted | FSM | 0 | no |
| Customers | HZ_MANAGE_IMPORT_LOOKUPS | cx/customer-data-management/trading-community-foundation/manage-import-lookups | planning | assisted | FSM | 0 | no |
| Customers | ORA_CMK_COLLAB_MESG_SERVICE_PROVIDER | scm/procurement/suppliers/manage-collaboration-messaging-service-providers | planning | assisted | FSM | 0 | no |
| Customers | ORA_CMK_MNGE_SIMPLIFIED_COLLAB_MSG_CONFIG | scm/procurement/suppliers/manage-simplified-collaboration-messaging-configuration | planning | assisted | FSM | 0 | no |
| Orders | DOO_MANAGE_ORCHESTRATION_LOOKUPS | scm/order-management/orders/manage-order-lookups | planning | assisted | FSM | 0 | no |
| Orders | DOO_MANAGE_ORCHESTRATION_PROFILES | scm/order-management/orders/manage-order-profiles | planning | assisted | FSM | 0 | no |
| Orders | DOO_MANAGE_ORCHESTRATION_EXTENSIBLE_FLEXFIELDS | scm/order-management/orders/manage-order-extensible-flexfields | planning | assisted | FSM | 0 | no |
| Orders | ORA_FOM_MANAGE_ORDER_MANAGEMENT_SYSTEM_PARAMETERS | scm/order-management/orders/manage-order-management-parameters | planning | assisted | REST | 0 | no |
| Orders | DOO_MANAGE_EXTERNAL_INTERFACE_WEB_SERVICE_DETAILS | scm/order-management/orders/manage-external-interface-web-service-details | planning | assisted | REST | 0 | no |
| Orders | ORA_DOO_MANAGE_BUSINESS_EVENT_TRIGGER_POINTS | scm/order-management/orders/manage-business-event-trigger-points | planning | assisted | REST | 0 | no |
| Orders | DOO_MANAGE_HOLD_CODE | scm/order-management/orders/manage-hold-codes | planning | assisted | REST | 0 | no |
| Orders | ORA_FOS_MANAGE_DROP_SHIP_AGREEMENTS | scm/manufacturing-and-supply-chain-materials-management/supply-chain-financial-flows/manage-drop-ship-financial-flows | planning | assisted | REST | 0 | no |
| Orders | ORA_RESERVATION_PRIORITY_FOR_SALES_ORDERS | scm/order-management/orders/reservation-priority-for-sales-orders | planning | assisted | FSM | 0 | no |
| Orders | ORA_FOM_REVISION_PREFERENCES_FOR_SALES_ORDERS | scm/order-management/orders/revision-preferences-for-sales-orders | planning | hybrid | REST | 0 | no |
| Pricing | ORA_QP_MANAGE_PRICING_LOOKUPS | scm/order-management/pricing/manage-pricing-lookups | planning | assisted | FSM | 0 | no |
| Pricing | CUSTOM_IMPORT_PRICE_LISTS | scm/order-management/pricing/import-price-lists | import | hybrid | FBDI | 0 | no |
| Channel Revenue Management | ORA_CJM_MANAGE_CLAIM_TYPES | scm/order-management/channel-revenue-management/manage-channel-claim-types | planning | assisted | REST | 0 | no |
| Channel Revenue Management | ORA_CJM_MANAGE_CLAIM_REASONS | scm/order-management/channel-revenue-management/manage-channel-claim-reasons | planning | assisted | REST | 0 | no |
| Channel Revenue Management | ORA_CJM_MANAGE_CLAIM_SOURCES | scm/order-management/channel-revenue-management/manage-channel-claim-sources | planning | assisted | REST | 0 | no |

## Appendix: Order Management tasks with no skill (113)

| Functional area | Task code | CSV flag |
|---|---|---|
| Initial Users | ORA_ASE_MANAGE_SECURITY_PREFERENCES | True |
| Initial Users | FND_CREATE_IMPLEMENTATION_USERS | False |
| Initial Users | FND_CREATE_DATA_ROLE_FOR_IMPLEMENTATION_USERS | False |
| Enterprise Profile | HRW_ESTABLISH_ENTERPRISE_STRUCTURES | True |
| Enterprise Profile | FND_MANAGE_REFERENCE_DATA_SET_ASSIGNMENTS | True |
| Enterprise Profile | ORA_FUN_MANAGE_REFERENCE_DATA_SET_DATA_ACCESS_FOR_USERS | False |
| Enterprise Profile | HZ_LOAD_GEOGRAPHY_INTERFACE_DATA | False |
| Enterprise Profile | HZ_RUN_GEOGRAPHY_LOADER | False |
| Enterprise Profile | HZ_MANAGE_GEOGRAPHY_LOOKUPS | True |
| Organization Structures | FUN_MANAGE_BUSINESS_UNIT | True |
| Organization Structures | ORA_FUN_MANAGE_BUSINESS_UNIT_DATA_ACCESS_FOR_USERS | False |
| Organization Structures | FUN_MANAGE_BUSINESS_UNIT_SET_ASSIGNMENT | True |
| Users and Security | HRC_IMPORT_WORKER_USERS | False |
| Users and Security | ORA_FUN_MANAGE_DATA_ACCESS_FOR_USERS | True |
| Items | EGP_MANAGE_ITEM_PROFILE_OPTIONS | True |
| Items | ORA_RCS_MANAGE_UOM_PROFILE | True |
| Items | ORA_RCS_MANAGE_SCMCOM_VALUE_SETS | True |
| Items | ORA_RCS_MANAGE_UOM_DESCRIPTIVE_FLEXFIELDS | True |
| Items | EGP_MANAGE_LIFECYCLE_PHASES | True |
| Items | EGP_MANAGE_DEFAULT_ITEM_CLASS | True |
| Items | EGP_MANAGE_ITEM_TYPES | True |
| Items | ORA_EGP_DOWNLOAD_IMPORT_TEMPLATE_OER | False |
| Items | ORA_EGP_UPLOAD_ITEM_DATA | False |
| Items | ORA_EGP_LOAD_FILE_SCHEDULED_PROCESSS | False |
| Items | EGP_MANAGE_ITEM_REV_DFFS | True |
| Items | ORA_EGP_MANAGE_ITEM_KEYWORD_SEARCH | True |
| Customers | HZ_IMPORT_PARTNERS | False |
| Customers | ORA_CMK_MANAGE_COLLAB_MESG_CONFIG | True |
| Customers | ORA_CMK_MANAGE_COLLAB_MESG_DVM | False |
| Customers | INV_MANAGE_TASK_CONFIGURATIONS | True |
| Customers | ORA_MANAGE_APPROVAL_GROUPS | False |
| Customers | ORA_CMK_MANAGE_B2B_CONFIG | False |
| Orders | DOO_MANAGE_ORCHESTRATION_DESCRIPTIVE_FLEXFIELDS | True |
| Orders | ORA_DOO_PUBLISH_EFF_ATTRIBUTES | False |
| Orders | DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES | True |
| Orders | DOO_ORCHESTRATION_MANAGE_SOURCE_SYSTEMS | True |
| Orders | ORA_FOM_COLLECT_ORDER_REFERENCE_DATA | False |
| Orders | DOO_REVIEW_ORCHESTRATION_COLLECTED_DATA | False |
| Orders | ORA_FOM_LOAD_ORDER_REFERENCE_DATA_FROM_FLAT_FILES | False |
| Orders | DOO_MANAGE_EXTERNAL_INTERFACE_TRANSFORMATION_STYLESHEETS | False |
| Orders | DOO_MANAGE_EXTERNAL_INTERFACE_MEDIATORS | False |
| Orders | DOO_MANAGE_EXTERNAL_INTERFACE_ROUTING_RULES | True |
| Orders | DOO_MANAGE_TASK_TYPES | True |
| Orders | DOO_MANAGE_ORDER_ATTRIBUTES_IDENTIFYING_CHANGE | True |
| Orders | DOO_MANAGE_STATUS_VALUES | True |
| Orders | DOO_MANAGE_TASK_STATUS_CONDITIONS | True |
| Orders | DOO_MANAGE_ORCHESTRATION_PROCESS_DEFINITIONS | True |
| Orders | DOO_MANAGE_ORCHESTRATION_PROCESS_ASSIGNMENT_RULES | True |
| Orders | DOO_MANAGE_JEOPARDY_PRIORITIES | True |
| Orders | DOO_MANAGE_JEOPARDY_THRESHOLDS | True |
| Orders | DOO_MANAGE_CONSTRAINT_OBJECTS | True |
| Orders | DOO_MANAGE_PROCESS_CONSTRAINTS | True |
| Orders | DOO_MANAGE_TRANSFORMATION_RULE_SETS | True |
| Orders | DOO_MANAGE_TRANSFORMATION_RULES | True |
| Orders | DOO_MANAGE_EXTERNAL_INTERFACE_DATA_VALUE_MAPS | True |
| Orders | DOO_GENERATE_BUCKET_SETS_FOR_BUSINESS_RULES | False |
| Orders | ORA_FOS_MANAGE_TRADE_QUALIFIER | True |
| Orders | ORA_FOS_MANAGE_SYSTEM_OPTIONS | True |
| Orders | ORA_DOO_MANAGE_EXTERNAL_INTEGRATION_VIB_ROUTING_RULES | True |
| Orders | ORA_DOO_MANAGE_PROCESS_VIB_ASSIGNMENT_RULES | True |
| Orders | ORA_DOO_MANAGE_PRETRANSFORMATION_VIB_RULE_SETS | True |
| Orders | ORA_FOM_MANAGE_ORDER_APPROVAL_RULES | True |
| Orders | ORA_FOM_MANAGE_ORDER_MANAGEMENT_EXTENSIONS | True |
| Orders | ORA_OKC_MANAGE_TIME_UNIT_MAPPINGS | True |
| Pricing | ORA_QP_MANAGE_PRICE_ELEMENTS | True |
| Pricing | ORA_QP_MANAGE_PRICING_CHARGE_DEFINITIONS | True |
| Pricing | ORA_QP_MANAGE_PRICING_BASES | True |
| Pricing | ORA_QP_MANAGE_PRICING_MESSAGE_TOKEN_ATTRIBUTE_DEFINITIONS | True |
| Pricing | ORA_QP_MANAGE_PRICING_MESSAGES | True |
| Pricing | ORA_QP_MANAGE_PRICING_TOTALS_DEFINITIONS | True |
| Pricing | ORA_QP_MANAGE_PRICING_MATRIX_TYPES | True |
| Pricing | ORA_QP_MANAGE_PRICING_PARAMETERS | True |
| Pricing | ORA_QP_MANAGE_PRICING_PROCESS_ASSIGNMENTS | True |
| Pricing | ORA_QP_MANAGE_ROUNDING_RULES | True |
| Pricing | ORA_QP_MANAGE_ROUNDING_RULE_ASSIGNMENTS | True |
| Pricing | ORA_QP_MANAGE_PRICING_RESULTS_PRESENTATIONS | True |
| Pricing | ORA_QP_MANAGE_PRICING_DESCRIPTIVE_FLEXFIELDS | True |
| Pricing | ORA_QP_MANAGE_EXT_SERVICES_FOR_ALGORITHMS | True |
| Pricing | CUSTOM_CUSTOMER_PRICING_DEFINITIONS | False |
| Channel Revenue Management | ORA_CJM_MANAGE_CHANNEL_PROFILE_OPTIONS | True |
| Channel Revenue Management | ORA_CJM_MANAGE_CHANNEL_LOOKUPS | True |
| Channel Revenue Management | ORA_CJM_MANAGE_CHANNEL_VALUE_SETS | True |
| Channel Revenue Management | ORA_CJM_MANAGE_CHANNEL_DESCRIPTIVE_FLEXFIELDS | True |
| Channel Revenue Management | ORA_CJM_MANAGE_CHANNEL_MESSAGES | False |
| Channel Revenue Management | ORA_CJM_MANAGE_CHANNEL_USER_STATUSES | True |
| Channel Revenue Management | ORA_CJM_MANAGE_PROGRAM_TYPES | True |
| Channel Revenue Management | ORA_CJM_MANAGE_ADJ_TYPES | True |
| Channel Revenue Management | IEX_MANAGE_AGING_METHODS | True |
| Channel Revenue Management | ORA_MANAGE_CHANNEL_SETTINGS | True |
| Channel Revenue Management | ORA_CJM_RUN_MIGRATE_PENDING_APPROVALS_TO_BPM_WORKFLOW_PROCESS | False |
| Channel Revenue Management | XLA_MANAGE_SUBLEDGER_APPLICATION | True |
| Channel Revenue Management | XLA_UPDATE_SUBLEDGER_APPLICATION_OPTIONS | False |
| Channel Revenue Management | XLA_MANAGE_SUBLEDGER_APPLICATION_TRANSACTION_OBJECTS | True |
| Channel Revenue Management | XLA_CREATE_AND_ASSIGN_SOURCES | False |
| Channel Revenue Management | XLA_MANAGE_SOURCES | True |
| Channel Revenue Management | ORA_XLA_MANAGE_FORMULA | True |
| Channel Revenue Management | XLA_MANAGE_ACCOUNTING_ATTRIBUTES | True |
| Channel Revenue Management | XLA_MANAGE_JOURNAL_LINE_RULE | True |
| Channel Revenue Management | XLA_MANAGE_DESCRIPTION_RULE | True |
| Channel Revenue Management | XLA_MANAGE_MAPPING_SET | True |
| Channel Revenue Management | XLA_MANAGE_ACCOUNT_RULE | True |
| Channel Revenue Management | XLA_MANAGE_SUPPORTING_REFERENCE | True |
| Channel Revenue Management | XLA_MANAGE_SUBLEDGER_JOURNAL_ENTRY_RULE_SET | True |
| Channel Revenue Management | XLA_MANAGE_ACCOUNTING_METHOD | True |
| Channel Revenue Management | XLA_ACTIVATE_SUBLEDGER_JOURNAL_ENTRY_RULE_SET_ASSIGNMENTS | False |
| Channel Revenue Management | XLA_IMPORT_SUPPORTING_REFERENCE_INITIAL_BALANCES | False |
| Channel Revenue Management | XLA_MANAGE_SUBLEDGER_ACCOUNTING_OPTIONS | True |
| Channel Revenue Management | XLA_MANAGE_ACCOUNTING_CLASS_USAGES | True |
| Channel Revenue Management | XLA_MANAGE_SUBLEDGER_ACCOUNTING_LOOKUPS | True |
| Channel Revenue Management | XLA_MANAGE_SUBLEDGER_ACCOUNTING_PROFILE_OPTIONS | True |
| Channel Revenue Management | XLA_MANAGE_SUBLEDGER_ACCOUNTING_DESCRIPTIVE_FLEXFIELD | True |
| Application Extensions | ORA_ATK_CUSTOM_ESS_FSCM | True |
| Application Extensions | ORA_RCS_GUIDED_JOURNEY | False |
