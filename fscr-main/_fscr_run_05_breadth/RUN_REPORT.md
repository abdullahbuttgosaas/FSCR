# FSCR Test 2 (Run 05): breadth: what do FSCR's other skills give a consultant?

Pod ETIA-TEST (release 26.10), read-only. Start 2026-11-03 09:40:15 · finish 10:08:20 +05:00 · **28 min**.
**Limits:** 40 of about 1,100 skill files (about 900 working skills), one pod, one release. **Grading is my judgment**, made mechanical by `scripts/analyze40.py`, whose rules are fixed in its docstring. Labels: verified / not verified / unclear.

---

## 1. One page for practice leads

**What a sampled skill really gives:** mostly a **pointer**. It names the setup task, its import mode and the FSCR route (export, then validate, then Data Loader), plus rule tables in `ora-resource`.
- **28 of 40 are grade 0** (route only, or no route).
- **7 are grade 1** (route plus a field list).
- **0 are grade 2.**
- **5 are grade 3** (own runnable script). None of those 5 are setup-import skills with an adapter: they are REST helpers, a workbook builder, a security script and the UCM client.

**How often the skills match the pod:**
- **Exports:** all 20 sampled tasks with CSV export support exported from the pod. That is 40 export processes; one data download failed on DNS.
- **Field names:** the skills **rarely name the pod's real template columns**. Median coverage is 0%. Only 4 of 20 name more than 5%: Fixed-assets value sets 20%, Contact lookups 56%, and receipt-accounting profile options and profile options at 8% each.
- **Wrong names:** some skills list names that are not template columns. Asset categories lists 17, such as `BookName` and `AssetCategoryBook`.
- **Verified:** the comparison of names against template columns (`evidence/field_compare.json`).

| Area | Sample | Grades (0/1/2/3) | Exports | Field coverage of template columns | Verdict | What a consultant still has to do | Fill-in build |
|---|---:|---|---|---|---|---|---|
| **ERP** | 10 | 4 / 3 / 0 / 3 | 5 of 5 exportable tasks OK | 0–20% | **Not yet** for setup import (route only); **use as is** for the 3 scripted helpers after testing | map every field from the template, write the CSV, write the rule results | **medium** per task: one adapter of the size seen in Run 04 (about 1,800 lines each), but generable from the template |
| **SCM** | 10 | 9 / 1 / 0 / 0 | 7 of 7 OK (1 data download failed) | 0–8% | **Not yet** | same as ERP; many SCM tasks route to REST with no body recipe | **medium** |
| **HCM** | 12 | 10 / 2 / 0 / 0 | 6 of 6 OK (FSM CSV tasks) | 0–8% | **Not yet** | for HDL tasks, a different loader and file format (none sampled had a script); dependency graph unusable for these tasks | **medium–large**: HDL tasks need an HDL builder FSCR does not ship |
| **CX** | 4 | 2 / 1 / 0 / 1 | 2 of 2 OK | 0% and 56% | **Not yet** (lookups closest) | as ERP | **small–medium** for lookups (REST client exists) |
| **Shared/core** | 4 | 3 / 0 / 0 / 1 | n/a | n/a | **Use as is**, as guidance; the UCM client is a real script | – | – |

Size basis: Run 04 shows a working FSCR adapter is about 1,800 lines per task, plus a descriptor, plus a rule set. None of the 40 sampled tasks has one. FSCR's generator (`fscr-deliverable-builder`) suggests the adapters are generated rather than hand-written, hence "medium" per task rather than "large".

## 2. Sampling method and seed
- **Script:** `scripts/sample40.py`, **seed 20261103**.
- **Population:** every `.md` with a skill front matter `type:` under `pillars/`, `shared/`, `core/`: 1,123 files.
- **Excluded:** 32 files tested in Runs 01–04: the 16 create skills, BU, price lists, receivables payment terms, order lookups, apps-common lookups, customers, export, compare, validator, Data Loader, auth, Run Book, initializer and router.
- **Strata:** ERP 10, SCM 10, HCM 12, CX 4, shared/core 4. Types are proportional to each area's mix, with largest-remainder rounding.
- **No cherry-picking and no replacements.**
- **Type labels:** wider than the four in the brief. Shared skills also use validation, assessment, export, support and verification. The quotas used the labels as found.
- **Population counts:** `evidence/population_counts.json`.

## 3. Scorecard per skill
Full table: `ledger.csv` (skill, area, type, grade, route, scripts, field match, export result, process IDs, task code, mode). Summary:

| # | Area | Skill (folder) | Type | Route | Grade | Template field coverage |
|---|---|---|---|---|---|---|
| 1 | ERP | manage-legal-jurisdictions | orch | FSM | 0 | 2% |
| 2 | ERP | fusion-accounting-hub | orch | none | 0 | – |
| 3 | ERP | manage-asset-categories | plan | FSM | 1 | 5% (17 listed names not columns) |
| 4 | ERP | add-other-data-sources | plan | REST | 3 | – (no CSV) |
| 5 | ERP | manage-fixed-assets-flexfield-value-sets | plan | FSM | 1 | 20% |
| 6 | ERP | fixed-assets (area) | plan | REST | 1 | – |
| 7 | ERP | manage-expense-report-templates | plan | none | 3 | – |
| 8 | ERP | complete-primary-to-secondary-ledger-mapping | plan | REST | 0 | 0% |
| 9 | ERP | manage-ledger-sets | plan | FSM | 0 | 0% |
| 10 | ERP | project-financial-management (area) | plan | REST | 3 | – |
| 11 | SCM | import-items | import | none | 0 | – (no CSV flag) |
| 12–20 | SCM | change attribute groups, procurement foundation, inventory orgs, document output, orders, item relationship DFFs, inventory zones, receipt accounting profiles, supplier category hierarchy | plan | FSM/REST | 0 (orders 1) | 0–8% |
| 21–32 | HCM | classrooms, communicate lookups, workforce DFFs, payroll value sets, HCM security common, time and labor foundation, costing of payment sources, HCM extract, administrator profile values, check-in template, profile options, key flexfields | import/orch/plan | REST/FSM/none | 0 (time and labor 1, HCM extract 1) | 0–8% |
| 33–36 | CX | reporting hierarchy generation, data warehouse profile, contact lookups, field-service users and security | orch/plan | REST/FSM/none | 0, 0, 1, 3 | 0%, 56% |
| 37–40 | Shared/core | integration-strategy-advisor, ucm-rest-client, extensible-flexfields, readiness-checklist-generator | adv/import/orch/plan | none | 0, 3, 0, 0 | – |

Every feature flag (fields, rules, example, dependencies, verification) per skill is in `evidence/analysis40.json`.

## 4. Routing and modes (8 questions; **I followed the router text**, FSCR ran nothing)

| Area | Question | Router outcome | Skill reached | Mode |
|---|---|---|---|---|
| ERP | set up asset categories | 1 offering, resolves | manage-asset-categories (exact task code) | assisted |
| ERP | set up ledger sets | 2 offerings, **asks the user** | manage-ledger-sets | assisted |
| SCM | set up inventory organizations | 5 offerings, **asks** | manage-inventory-organizations | assisted |
| SCM | set up inventory zones | 1 offering, resolves | inventory-zones | assisted |
| HCM | set up communicate lookups | 1 offering, resolves | manage-communicate-lookups | hybrid |
| HCM | set up costing of payment sources | 1 offering, resolves | costing-of-payment-sources | assisted |
| CX | set up data warehouse profile option | 4 offerings, **asks** | manage-data-warehouse-profile-option | assisted |
| CX | set up contact lookups | 6 offerings, **asks** | manage-contact-lookups | assisted |

- **Result:** 8 of 8 reach the right skill by exact task code; 4 of 8 need an offering choice first.
- **The router answers which skill, not what to set up.** None of the reached skills gives a complete field recipe (grades above).

## 5. HCM findings
- **Routes across all HCM task files:** FSM 190, REST 75, **HDL 22**, ESS 1.
  - FSM-mode HCM tasks use the same FSCR export → Data Loader route as Finance. 6 sampled HCM tasks exported fine.
  - HDL tasks need HCM Data Loader files (`.dat`, business-object hierarchies). FSCR's FSM adapters don't cover them, and no sampled HCM skill ships an HDL builder.
  - The pod's Data Loader lists business objects (Run 01: 353 objects, 0 FBDI), but nothing was tested here.
- **Dependency graph:** `hcm-dependency-graph.json` has 86 nodes and 281 edges. It contains **2 of the 8** sampled HCM task codes, both with **0 edges**, so it is **not usable** to order the sampled tasks.
- **What can run on this pod:** read-only exports of the 6 CSV-capable HCM tasks (verified). No sampled HCM skill has its own script, so nothing else can run without building one.

## 6. Where FSCR's docs were wrong or silent
1. **Field lists rarely match the pod's columns** (median 0%). Some skills name entity names or concepts as if they were columns (asset categories: 17 names not in the template).
2. **"Import" skills without an import route:** `import-items` has no Data Loader mode or CSV flag in its skill text.
3. **Type labels:** the repo uses about 9 type labels, not the 4 the brief lists. Execution modes in the sample: assisted 31, hybrid 9, none automated or advisory.
4. **The HCM dependency graph** covers few tasks and gives no edges for the sampled ones it contains.
5. **Many functional-area skills** (`fixed-assets`, `orders`, `procurement-foundation`) route to REST with no body recipe.

## 7. Stats and token proxy
- **Oracle:** 40 export processes (template + data for 20 tasks); IDs in `evidence/export_process_ids.txt` and per task in `ledger.csv`. **No import, create, update, delete or approval.**
- **Tool calls:** about 30 (approximate).
- **Local:** the export step wrote **no existing file** in the copy (`diff -rq fscr-work5` vs the original repo: no differences outside `__pycache__`).

| When | Source | Context size | 5-hour window | Weekly |
|---|---|---|---|---|
| Start 09:40 | `get_usage` | 836,944 | 81% | 40% |
| Midway 09:45 | `get_usage` | 865,913 | 86% | 41% |
| End 10:08 | `get_usage` | 868,988 | 87% | 41% |

Context size is not billed tokens; plan windows may include other use.

## 8. Capability matrix

| Capability | Tested | Result | Evidence | Limits |
|---|---|---|---|---|
| Create | not exercised (Run 04) | – | – | – |
| Change | not exercised (Run 03) | – | – | – |
| Verify | not exercised here | – | – | – |
| **Understand** | 20 exports | FSCR's export reads every sampled CSV-capable task (20/20 templates), but the skills explain few of the columns they export | `evidence/field_compare.json` | field names only, not semantics |
| **Plan and advise** | 8 routing questions | right skill 8/8; offering question 4/8; HCM dependency graph unusable for the sample | `evidence/routing8.txt` | router followed by me |
| **Breadth** | 40 skills, 5 areas | grades 0: 28, 1: 7, 2: 0, 3: 5; no setup-import skill in the sample has an adapter | `evidence/analysis40.json` | 40 of about 900 |

## 9. Honest assessment and comparison with the earlier audit
- **Agrees with the earlier route audit.** That audit found a route named almost always, a real write recipe in 2 of 10 REST skills, and field detail often missing. This sample agrees:
  - Every task skill names its route, either an import mode or REST.
  - No sampled task skill gives a complete recipe (grade 2: 0 of 40).
  - Field lists are partial and often not template columns.
- **Where FSCR helps:** task identity, the routing to FSCR's export / Data Loader chain, and rule tables that describe validations a consultant should check. The export route works on the pod for every sampled CSV-capable task.
- **Where it has holes:**
  - For about 900 skills outside the 16 adapters, a consultant still has to build each import file by hand from the template.
  - HDL tasks have no builder.
  - The HCM dependency graph does not order the sampled tasks.
- **No time-saving claim:** nothing was created, and there is no manual baseline.
