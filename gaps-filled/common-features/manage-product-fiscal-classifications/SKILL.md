---
skill_id: "gosaas.gap-fills.common-features.manage-product-fiscal-classifications"
name: "Manage Product-Based Fiscal Classifications (GoSaaS gap fill, card)"
description: "Card over manage-transaction-fiscal-classifications: create one new product category code (type PRODUCT_CATEGORY) with its translation and denormalized rows through the same tax fiscal classification FSM CSV package, then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 2, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS"
task_name: "Manage Product-Based Fiscal Classifications"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "gosaas common-features/manage-transaction-fiscal-classifications/SKILL.md (the full skill this card changes) and its scripts/fiscal_code_rows.py"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new product category code (4 rows). The seeded type row PRODUCT_CATEGORY is sent unchanged. It may not be deletable; plan as if it stays."
---

# Manage Product-Based Fiscal Classifications (GoSaaS gap fill, card)

> **Added by GoSaaS, not part of official FSCR.** Card over `../manage-transaction-fiscal-classifications/SKILL.md` (the **full skill**). Follow the full skill; this card says only what is different. Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = not tested.

## What this setup is and when to use
Product category fiscal classifications are the codes of the seeded type `PRODUCT_CATEGORY` (in the export: `ORA_ZX_PRODUCT_CLASS_GENERIC.csv` and `ORA_ZX_PRODUCT_CLASS_CODE.csv`). Tax rules and tax exceptions can use them for items or lines. This card adds **one new level-1 code** (no parent). Use it when someone asks for a **new** code for task `ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS`; never to change existing codes. No rule uses the new code until someone sets one up.

## Changes to the full skill
| Full skill step | What to do instead |
|---|---|
| Step 2 export | `--task-code ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS`. Same 73-file package (VERIFIED, about 2.5 min). This card uses `ORA_ZX_PRODUCT_CLASS_GENERIC.csv` (1 row `PRODUCT_CATEGORY`), `ORA_ZX_PRODUCT_CLASS_CODE.csv` (VERIFIED: 10 seeded codes, 6 at level 1, several with a country) + `_TRANSLATION`, `ORA_ZX_PRODUCT_CLASS_DENORM.csv` + `_TRANSLATION`. Do not confuse with `ORA_ZX_PRODUCT_CLASS.csv` (type `USER_ITEM_TYPE`, not used here). |
| Step 3 template | list the codes with `python -I -c "import csv,sys; [print(r['ClassificationCode'],'| parent',r['ParentClassificationCode'] or '-','|',r['RecordTypeCode'],'| country',r['CountryCode'] or '-') for r in csv.DictReader(open(sys.argv[1]+'/ORA_ZX_PRODUCT_CLASS_CODE.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"`. TEMPLATE = the first listed code **without** a parent (prefer `USER_DEFINED` record type if any). No PARENT. VERIFIED (we used the first listed seeded code). CODE must not be in the list. |
| Step 4 build | the helper with `--family product --template-code "<TEMPLATE>"` (no `--template-parent`). Builder keys (**no parent column**: a level-1 code has none and the builder refuses empty key values, VERIFIED): `--key "ORA_ZX_PRODUCT_CLASS_CODE.csv=ClassificationTypeCode,ClassificationCode"`, `--key "ORA_ZX_PRODUCT_CLASS_CODE_TRANSLATION.csv=ORA_ZX_PRODUCT_CLASS_CODE.ClassificationTypeCode,ORA_ZX_PRODUCT_CLASS_CODE.ClassificationCode,Language"`, `--key "ORA_ZX_PRODUCT_CLASS_DENORM.csv=ClassificationTypeCode,ClassificationCode,ConcatClassifCode"`, `--key "ORA_ZX_PRODUCT_CLASS_DENORM_TRANSLATION.csv=ORA_ZX_PRODUCT_CLASS_DENORM.ClassificationTypeCode,ORA_ZX_PRODUCT_CLASS_DENORM.ClassificationCode,ORA_ZX_PRODUCT_CLASS_DENORM.ConcatClassifCode,Language"`, `--prefix-col "ORA_ZX_PRODUCT_CLASS_CODE.csv=ClassificationCode"`, `--max-len "ClassificationCode=30"`, `--zip-name fc_new.zip`. Parent row: `copy_parent_rows.py ... --file ORA_ZX_PRODUCT_CLASS_GENERIC.csv --where ClassificationTypeCode=PRODUCT_CATEGORY` (the helper's `PARENT:` line says the same). Builder must print `1 new rows` for the 4 files. |
| Step 5 import | `--task-code ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS --task-name "Manage Product-Based Fiscal Classifications"`. Success: `Detail Object: ProductGenericFiscalClassificationType ... 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`, about 43 objects. VERIFIED, about 1.5 min. Step 6 is the proof. |
| Step 6 compare | keys: `ORA_ZX_PRODUCT_CLASS_GENERIC.csv=ClassificationTypeCode` and the 4 keys of Step 4 (the denormalized keys end with ConcatClassifCode, which for a level-1 code is the code itself). Expects: `ORA_ZX_PRODUCT_CLASS_CODE.csv=PRODUCT_CATEGORY,<CODE>`, `ORA_ZX_PRODUCT_CLASS_CODE_TRANSLATION.csv=PRODUCT_CATEGORY,<CODE>,US`, `ORA_ZX_PRODUCT_CLASS_DENORM.csv=PRODUCT_CATEGORY,<CODE>,<CODE>`, `ORA_ZX_PRODUCT_CLASS_DENORM_TRANSLATION.csv=PRODUCT_CATEGORY,<CODE>,<CODE>,US`. Want `RESULT: PASS`, type row `changed 0`. VERIFIED |

## Limits
- Not tested: child codes (with a parent), `--keep-country`. The template's country is cleared, so the new code is not limited to that country.
- Tested on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED, 2026-11-24). Do not reuse this name.
| Step | Result |
|---|---|
| Export before | 10 product category codes, 10 denormalized rows; about 2.5 min |
| New record | `GAPFILL_AB_P2_PCC1`, level 1, from 2026/01/01, template = first listed seeded level-1 code, country cleared |
| Builder | first run with the parent column in the key stopped (`missing a key column value`); keys without it worked |
| Import | 1 attempt (ProcessId 100004742413617): ProductGenericFiscalClassificationType 1 row, 0 failed, 43 objects |
| Export after + compare | added 1 + 1 + 1 + 1, type row changed 0: PASS |
