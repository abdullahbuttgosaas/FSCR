# FSCR route audit (read-only, 2026-11-02)

Start 2026-11-02 21:23:33 +0500 · finish 2026-11-02 21:52:38 +0500 · 29 minutes (29 min 5 s).
Nothing in the FSCR repo or the project was changed; Oracle was not called. Every number below comes from the scripts
in this folder over the repo at `E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main`.

## Direct answer

FSCR does state a route for almost every task it covers, but as **a field plus a pointer to its own engine**, not as an
Oracle recipe. Each task file carries `dataloader_import_mode` (FSM, REST, HDL, FBDI, ESS or CXIMPORT) and a section
that sends the import to FSCR's `core.data-loader`. Only a minority name an actual Oracle endpoint, file layout or
required fields. **No task declares browser/UI automation**: 47 forbid it outright, and 12 say "do it by hand in the
UI". FSM CSV is the main route, and it mostly follows the catalog flag, because the route section is generated from
that flag.

## How a task is linked to its skill (from the files)

- **Link:** a file's YAML frontmatter has `task_code: "<TaskCode>"`. 931 such files exist, and every task code is in
  the catalog.
  - `SKILL.md`: 769 files covering **701 tasks**. 1,126 SKILL.md files exist in total; two are named `skill.md` in
    lower case.
  - **Task guide files:** 162 `.md` files inside a functional-area skill folder, e.g.
    `pillars/erp/financials/organization-structures/manage-business-unit.md`.
  - **SKILL.md or task guide: 848 tasks.** 147 tasks have only a task guide; 14 have both.
- **Wider definition, for information:** a task code appears anywhere in a skill folder: 873 tasks.
- **Repeats:** some tasks have several skills. For example, FND_MANAGE_COMMON_LOOKUPS has 10 and
  FND_MANAGE_PROFILE_OPTIONS has 9.
- **Pillars:** shared/ and core/ skills carry no `task_code`, so they are not in the set.

## Where a route is stated

| Place | Field / signal | Files using it |
|---|---|---|
| Frontmatter | `dataloader_import_mode` | 720 SKILL.md (FSM 424, REST 222, HDL 41, FBDI 16, ESS 12, CXIMPORT 5) |
| Frontmatter | `businessObject` / `businessObjects` | 693 / 20 |
| Frontmatter | `csv_export_import_supported_flag`, `export_import_supported_flag` (copied from the catalog) | 766 each |
| Frontmatter | `depends_on` / `uses_core` naming a route skill (`core.data-loader` 718, `core.fusion-api.rest-api-client` 255, `apps-common` 118, `ess-job-submitter` 37) | see 01 output |
| Frontmatter | `side_effects` (text; 812 are empty `[]`) | 1,122 |
| Body | section "CSV Export, Import, and Validation Workflow" (generated from the catalog flag) | 617 SKILL.md |
| Body | section "Download Fusion Data Loader Sample" (Data Loader business object) | 175 |
| Body | "Execution Route" / "Automation Boundary" / manual-tasks routing | few; see 05 output |
| HTML comments | `fscr-supported-operations` 18, `fscr-create-fields` 16, `fscr-update-fields` 16 | |
| Files | `ora-resource/ora_rest_execution.md` 28, `ora_fbdi_processing.md` 4, `e2e-adapter.json` 16 (`task.importMode`), `scripts/fsm_task_adapter.py` 16 | |

Note: the body sometimes overrules the frontmatter. In 14 files the body calls `dataloader_import_mode` "non-operative
compatibility metadata" or "catalog metadata only".

## Counts by declared route (931 task files; one file can have several routes)

Definitions are in the docstring of `02_route_audit.py`. In short:

- **FSM CSV:** a route section in its positive form, a `core.data-loader … FSM` line, or an adapter with `importMode` FSM.
- **REST:** any one of these:
  - `ora_rest_execution.md`;
  - REST mode with a business object;
  - the Data Loader sample section;
  - `task-rest`;
  - REST mode that the body doesn't disclaim;
  - a `depends_on` to a REST core service.
- The frontmatter mode counts only when the body doesn't disclaim it.

| Route | All | ERP | HCM | SCM | CX | Common |
|---|---|---|---|---|---|---|
| Task files | 931 | 80 | 365 | 251 | 223 | 12 |
| FSM CSV import | 739 | 64 | 285 | 219 | 165 | 6 |
| REST (any kind, see below) | 473 | 45 | 153 | 194 | 81 | 0 |
| HDL (HCM Data Loader) | 43 | 2 | 41 | 0 | 0 | 0 |
| ESS job | 27 | 2 | 8 | 1 | 16 | 0 |
| FBDI | 9 | 3 | 0 | 6 | 0 | 0 |
| CX import | 5 | 0 | 0 | 0 | 5 | 0 |
| Browser / UI automation | **0** | 0 | 0 | 0 | 0 | 0 |
| Manual only (user does it in the UI) | 12 | 0 | 1 | 10 | 1 | 0 |
| None declared | 17 | 0 | 3 | 3 | 5 | 6 |
| Unclear | 1 | 0 | 1 | 0 | 0 | 0 |
| More than one route | 384 | 36 | 120 | 182 | 46 | 0 |

**What "REST" means here.** A file can have several kinds of evidence, so these don't add up to 473:

| Kind of REST evidence | Files |
|---|---|
| Fusion **Data Loader** import of a named business object (e.g. `advancedInventoryParameters`), not a direct POST to the resource | 227 |
| REST mode in the frontmatter only | 220 |
| Only a `depends_on` to a REST client, which may be used just for reads | 201 |
| An `ora_rest_execution.md` file | 24 |
| `task-rest` | 5 |

**Browser / UI automation:** no file declares it. 47 files forbid it explicitly, for example
`manage-trading-community-messages/SKILL.md:156`: "browser automation or direct UI control" in its "Do not route" list.

## Catalog flag (CSV import allowed) against the skill

| Result | Files |
|---|---|
| Agree: flag Y, skill declares FSM CSV | 736 |
| Agree: flag N, skill declares another route or manual | 125 |
| **Contradiction:** flag N but the skill declares FSM CSV | **2** |
| **Reverse:** flag Y but the skill declares only another route or manual | **37** |
| Flag UNKNOWN in the catalog | 14 |
| No route to compare (flag N / flag Y) | 11 / 6 |

- **Agreement is partly built in.** The FSM section is generated from the flag ("`CSVExportImportSupportedFlag` is `Y`
  for this task, so route …").
- **Flag copies differ.** In 16 files the frontmatter's copy of the flag differs from the catalog (UNKNOWN, missing,
  or N where the catalog says Y).
- **Flag N, FSM declared (both):** CUSTOM_MANAGE_SALES_FUNCTIONAL_AREA_CATALOG (`…/manage-sales-functional-area-catalog/SKILL.md:16`
  `dataloader_import_mode: "FSM"`) and QSC_MANAGE_PRODUCT_GROUPS (`pillars/cx/service/service-catalog/manage-product-groups.md:12`).
- **Reverse, first 10** (the full list is in `05_tables.out.txt`):

  | Task | Declared route |
  |---|---|
  | ORA_CPQ_SETUP_ASSISTANT | REST |
  | GL_MANAGE_ACCOUNTING_CALENDARS | REST |
  | GL_MANAGE_CHART_OF_ACCOUNTS_MAPPING | REST |
  | GL_MANAGE_CHART_OF_ACCOUNTS_VALUE_SET_VALUES | FBDI |
  | GL_REVIEW_AND_SUBMIT_ACCOUNTING_CONFIGURATION | ESS + REST |
  | PJF_MANAGE_PROJECT_ORGANIZATION_CLASSIFICATIONS | HDL + REST |
  | PJF_MANAGE_PROJECT_UNIT_ORGANIZATIONS | HDL + REST |
  | ORA_PER_MANAGE_HCM_POSITION_HIERARCHY | HDL + REST |
  | ORA_PER_MANAGE_BARGAINING_UNIT_LOOKUP | Data Loader REST |
  | ORA_PER_MANAGE_WORKFORCE_STRUCTURES_DESCRIPTIVE_FLEXFIELDS | Data Loader REST |

  Most of these look like a deliberate choice of another loader, not an error.

## Our areas (quoted lines in `03_our_areas.out.txt`)

| Area | FSCR task (catalog CSV flag) | Declared route, quoted |
|---|---|---|
| Order Types | DOO_MANAGE_ORCHESTRATION_LOOKUPS (Y) | `pillars/scm/order-management/orders/manage-order-lookups/SKILL.md:16` `dataloader_import_mode: "FSM"`; `:281` "4. Import setup task data with `core.data-loader`." |
| Business Units | FUN_MANAGE_BUSINESS_UNIT (Y), **task guide only** | `pillars/erp/financials/organization-structures/manage-business-unit.md:32` "3. Import reviewed task setup data with `core.data-loader`."; its folder's `ora-resource/ora_rest_execution.md:18` says a direct REST write is "Stop. Do not invent an endpoint or package format." |
| Price Lists | only CUSTOM_IMPORT_PRICE_LISTS (N) | `pillars/scm/order-management/pricing/import-price-lists/SKILL.md:16` `dataloader_import_mode: "FBDI"`; `:155` "`dataloader_import_mode` is `FBDI`. Route Price Lists FBDI package validation …". No "Manage Price Lists" task is in the catalog. |
| Payment Terms (Payables) | AP_MANAGE_PAYMENT_TERMS (Y) | `pillars/erp/financials/payables/manage-payment-terms/SKILL.md:16` `"FSM"`; `:196` "4. Import setup task data with `core.data-loader`."; `e2e-adapter.json` `importMode: FSM` |
| Customers | AR_MANAGE_CUSTOMERS (N), AR_CREATE_CUSTOMER (N), ORA_FOS_IMPORT_CUSTOMER (N) | **no skill and no task guide**; only customer-account flexfield and lookup tasks have skills (FSM) |
| Receivables Payment Terms | AR_MANAGE_RECEIVABLES_PAYMENT_TERMS (Y) | `pillars/erp/financials/customer-billing/manage-receivables-payment-terms/SKILL.md:16` `"FSM"`; `e2e-adapter.json` `importMode: FSM` |
| AutoInvoice Grouping Rules | AR_MANAGE_AUTOINVOICE_GROUPING_RULES (Y) | `…/manage-autoinvoice-grouping-rules/SKILL.md:16` `"FSM"`; `:139` "4. Import setup task data with `core.data-loader`." |
| Transaction Sources | AR_MANAGE_TRANSACTION_SOURCES (Y) | `…/manage-transaction-sources/SKILL.md:16` `"FSM"`; `:137` same line |
| Transaction Types | AR_MANAGE_TRANSACTION_TYPES (Y) | `…/manage-transaction-types/SKILL.md:16` `"FSM"`; `:167` "Route every import through `core.data-loader` in `FSM` mode with an empty `businessObject` …" |

**The 16 create skills** are the files with `fscr-create-fields`. All 16 declare FSM CSV and are ERP Receivables or
Payables tasks. Two of them also list `core.fusion-api.rest-api-client` in `depends_on`:
ORA_AP_MANAGE_BANK_CHARGES and AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT.

## Files with no route: what they give

There are 30 such files: 12 manual-only, 17 with none declared and 1 unclear.

- **Manual-only (12):** they give UI steps to do by hand, e.g. "## Manual steps" and "## Manual validation" in the
  supplier approval guides.
- **No ora-resource or references folder (24 of the 30):** only the generated metadata sections. 6 security-console
  task guides have no body sections at all.
- **With ora-resource files (5):** input validation, dependency, reference-lookup files with fields and rules.

By contrast, a typical routed file such as Transaction Types gives instructions **plus** a route. It has the route
section, `dataloader_import_mode`, `core.data-loader`, and for the 16 create skills the exact create fields.

## Accuracy sample (files only; `04_accuracy_sample.out.txt`)

**10 REST files**, one per pillar in turn, where the REST evidence is in the file's own text:

| Result | Tasks |
|---|---|
| Name a POST for the setup object itself | 2 of 10: HZ_MANAGE_GEOGRAPHIES (`/crmRestApi/…/importMappings`, with Oracle docs links) and BEN_MANAGE_BENEFIT_PROGRAMS_DETAILS (`POST /hcmRestApi/resources/latest/benefitPlanCopyParameters`) |
| Give only an ESS job submission | 1: ORA_HZ_RUN_GEOCODE_LOADER |
| Name an evaluation action, not a create path | 1: BEN_MANAGE_ELIGIBILITY_PROFILES (`formulaEvaluations`) |
| The "REST" is the FSM CSV import call | 1: GL_MANAGE_CHART_OF_ACCOUNTS_MAPPING (`POST … setupTaskCSVImports`) |
| Give a Data Loader business object and FSCR's sample script, with fields from live metadata | 2: ORA_ADVANCED_INVENTORY_PARAMETERS, ORA_INVENTORY_TASK_CONFIGURATIONS. Usable only through FSCR's Data Loader engine. |
| Give no write contract | 3: GL_MANAGE_ACCOUNTING_CALENDARS and GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES say "do not invent an endpoint" / "Direct REST write contract unavailable … TBD"; HZ_MANAGE_RESOURCE_ROLES names `resourceRoles` with no write method |

All 10 have an `ora_input_validation.md`.

**10 FSM CSV files without REST:**

- **Present in all 10:** the task code and the template/export step, so the file layout comes from Oracle's own
  template at run time.
- **Import step to `core.data-loader`:** 8 of 10. The 2 security-console files route through their own security
  skills.
- **Often missing:** entity or CSV file names (3 of 10), the metadata file named (4 of 10), a required-fields file
  (5 of 10) and the create fields listed (2 of 10, both Receivables).

So the route is complete for FSM, but field-level requirements are often absent.

## What could not be classified

- **One file:** `pillars/hcm/goal-management/goal-management-common/manage-reference-data-sets/SKILL.md`.
  - Its body says (line 129) the flag "is catalog metadata only in this Goal Management facade" and sends work to
    another provider.
  - It names no route of its own.
- **Limits of the method:**
  - Task guide files are classified from their own text only; they may inherit their parent skill's route. This may
    undercount routes for the 162 guides.
  - The REST count includes 201 files where the only evidence is a `depends_on` to a REST client. These are counted
    as REST but may be reads only.
  - Negations are detected by wording ("do not", "never", "must not", list headers, "UNSUPPORTED" table rows). All
    6 hits found before that test was widened were read by hand and were negations.

## Scripts and outputs (all in this folder)

| Step | Script | Output |
|---|---|---|
| Field survey | `01_survey_fields.py` | `01_survey_fields.out.json` |
| Main classification | `02_route_audit.py` | `02_route_audit.out.json` (every file, with evidence lines), `02_route_audit.out.txt` (summary) |
| Our areas, quoted | `03_our_areas.py` | `03_our_areas.out.txt` |
| Accuracy sample | `04_accuracy_sample.py` | `04_accuracy_sample.out.json` / `.txt` |
| Tables and contradiction lists | `05_tables.py` | `05_tables.out.txt` |

Run order: 01, 02 (about 3.5 minutes), 03, 04, 05. Python 3.12 with PyYAML.
