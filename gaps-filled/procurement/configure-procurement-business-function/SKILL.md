---
skill_id: "gosaas.gap-fills.procurement.configure-procurement-business-function"
name: "Configure Procurement Business Function for a NEW test business unit by FSM CSV (GoSaaS gap fill)"
description: "Gives your OWN prefix business unit the Procurement business function (Assign Business Unit Business Function CSV) and then its procurement configuration row (PO_SYSTEM_PARAMETER) through FSCR's setup-task CSV export and import; proves by second exports that only your rows were added. Never changes a real business unit. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 03 (2026-11-25, written unsafe), re-opened and tested in batch 07 (2026-11-27) with an own test business unit. NOT official FSCR."
task_code: "PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION"
task_name: "Configure Procurement Business Function"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.2.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gaps-filled common-features/test-business-unit (makes the prefix business unit)"
side_effects:
  - "Adds one business function row (Procurement) and one procurement configuration row for YOUR prefix business unit. No real business unit is touched. There is no delete by CSV: plan as if they stay."
  - "The configuration row names an existing inventory organization as a value only; that organization is not changed."
---

# Configure Procurement Business Function (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR routes the task (CSV flag Y) but has no skill. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-27) · **GUESS** = not run live.
> Version 0.1.0 (2026-11-25) said a test is unsafe because every row belongs to a live business unit. The safe way is a NEW prefix business unit that nobody uses (VERIFIED here).

## What it is and when to use
Each procurement business unit has one configuration row (`PO_SYSTEM_PARAMETER.csv`, about 120 columns: currency, grouping of requisitions, receipt close tolerances, negotiation style, inventory organization, ...). The task package (VERIFIED) has 5 CSVs: `PO_SYSTEM_PARAMETER`, `PO_DOCUMENT_TYPE` (+ translation, 6 document types per business unit) and `PON_CONTRACTS` (+ translation). A business unit can be configured only after it has the **Procurement** business function (task Assign Business Unit Business Function).
Use this skill to configure a **new** business unit. Never send a row of an existing business unit: an import updates it for real users.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds procurement\ and common-features\)
B     = <GAPS>/procurement/scripts/build_csv_package.py   (offline package builder; refuses a key that already exists or lacks the prefix)
CMP   = <GAPS>/procurement/scripts/compare_exports.py      (before/after compare)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); create it first: mkdir -p "<RUN>"
PREFIX= your test prefix, e.g. GAPFILL_XX_
BU    = your own prefix business unit, e.g. GAPFILL_XX_BU1 (Prerequisite 1)
TPL   = the ShortCode of an existing configured business unit to copy settings from (Step 1 lists them); best one of your own earlier prefix units, so no real unit's settings are used
INV   = an inventory organization code, read from TPL's row (a value only; nothing on it changes)
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Every export below: no ZIP = run again into a NEW folder, up to 3 tries.
Export command, used with `<TASK>` and `<DIR>`:
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code <TASK> --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/<DIR>" > "<RUN>/<DIR>.log" 2>&1
python -I -c "import sys,glob,zipfile; z=glob.glob(sys.argv[1]+'/*.zip'); sys.exit('NO ZIP: run again into a new folder') if not z else zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/<DIR>"
```
Import command, used with `<TASK>`, `"<NAME>"`, `<ZIP>` (absolute) and `<DIR>`:
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code <TASK> --task-name "<NAME>" --zip-file "<ZIP>" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/<DIR>" > "<RUN>/<DIR>.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/<DIR>.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^\]{0,200}|JBO-[0-9]+: [^\]{0,160}" "<RUN>/<DIR>"/*_process_log.txt | sort -u
```
Write down every ProcessId. Print only these grep lines (the log holds the environment name and a user). Dropped connection after a ProcessId: never import again; wait 2 minutes and check with the next export.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; a valid cached sign-in returns at once). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names; never print `ASM_SETUP_CSV_METADATA.xml`.

## Prerequisites
1. **Your own business unit.** Use an existing prefix business unit of yours, or make one with the GoSaaS skill `<GAPS>/common-features/test-business-unit/SKILL.md` (no ledger, no legal entity is fine: VERIFIED). Never use a real business unit.
2. **Give it the Procurement business function** (VERIFIED):
   - Export with `<TASK>`=`FUN_ASSIGN_BUSINESS_UNIT_BUSINESS_FUNCTION`, `<DIR>`=`bfexp1`. Files: `FUN_BUSINESS_UNIT.csv` (units), `FUN_BU_USAGE.csv` (one row per unit and business function: `FUN_BUSINESS_UNIT.Name`, `ModuleId`, `ConfigurationStatus`), `FUN_BU_SERVICE_PROVIDERS.csv`, an `LE_<number>.csv`.
   - Check your unit is there and has no row with `ModuleId` 110 yet:
     ```bash
     cd "<RUN>"; python -I -c "import csv,sys; d=sys.argv[1]; print('unit rows', sum(r['Name']==sys.argv[2] for r in csv.DictReader(open(d+'/FUN_BUSINESS_UNIT.csv',encoding='utf-8-sig')))); print('functions', [r['ModuleId'] for r in csv.DictReader(open(d+'/FUN_BU_USAGE.csv',encoding='utf-8-sig')) if r['FUN_BUSINESS_UNIT.Name']==sys.argv[2]])" bfexp1/unz <BU>
     ```
     Expect `unit rows 1`. `ModuleId 110` = Procurement (VERIFIED: every configured procurement unit has it, and the service-provider pairs 120 Requisitioning → 110 Procurement; GUESS for the name, the export has no names). If 110 is already listed, skip to Step 1.
   - Build and import (the unit's own row goes in unchanged as the parent):
     ```bash
     cd "<RUN>"; python -I "<B>" --export-dir bfexp1/unz --out "<RUN>/pay_bf/bf.zip" --prefix <PREFIX> --copy-row "FUN_BUSINESS_UNIT.csv|Name=<BU>" --row "FUN_BU_USAGE.csv|FUN_BUSINESS_UNIT.Name=<BU>|ModuleId=110|ConfigurationStatus=Y" --only
     ```
     Import with `<TASK>`=`FUN_ASSIGN_BUSINESS_UNIT_BUSINESS_FUNCTION`, `"<NAME>"`=`"Assign Business Unit Business Function"`, `<ZIP>`=`<RUN>/pay_bf/bf.zip`, `<DIR>`=`imp_bf`. Success: `A total of 1 rows were processed. 0 rows of them failed`, `Business object: Business Unit Business Function. Status: Completed successfully`.
   - Read back: export again into `bfexp2`, then
     ```bash
     cd "<RUN>"; python -I "<CMP>" bfexp1/unz bfexp2/unz --key "FUN_BUSINESS_UNIT.csv=Name" --key "FUN_BU_USAGE.csv=FUN_BUSINESS_UNIT.Name+ModuleId" --key "FUN_BU_SERVICE_PROVIDERS.csv=ClientBuName+ProviderBuName+UpstreamFunctionId+DownstreamFunctionId" --key "LE_1214416713655.csv=SetCode+OrganizationCode+ReferenceGroupName" --expect "FUN_BU_USAGE.csv=<BU>+110"
     ```
     (if your `LE_<number>.csv` has another number, use that file name). `RESULT: PASS` = `FUN_BU_USAGE` +1 (`added: <BU>+110`), every other file added 0, removed 0, changed 0.

## Step 1. Read-only export (VERIFIED)
Export with `<TASK>`=`PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION`, `<DIR>`=`exp1`. Then list the configured units and check yours is not among them:
```bash
cd "<RUN>"; python -I -c "import csv; rows=list(csv.DictReader(open('exp1/unz/PO_SYSTEM_PARAMETER.csv',encoding='utf-8-sig'))); [print(r['ShortCode'],'|',r['OrganizationCode'],'|',r['CurrencyCode']) for r in rows]"
```
`ShortCode` is the business unit name. Pick `<TPL>` (any configured unit) and take its `OrganizationCode` (inventory organization) as `<INV>`.

## Step 2. Build your row (offline, VERIFIED)
Copy TPL's settings, but not its unit, inventory organization, currency or audit columns:
```bash
cd "<RUN>"; python -I -c "import csv,sys; r=[x for x in csv.DictReader(open('exp1/unz/PO_SYSTEM_PARAMETER.csv',encoding='utf-8-sig')) if x['ShortCode']==sys.argv[1]][0]; skip={'CreatedBy','LastUpdatedBy','LastUpdateLogin','CreationDate','LastUpdateDate','OrganizationCode','CurrencyCode','ShortCode'}; open('row.txt','w',encoding='utf-8').write('|'.join(['PO_SYSTEM_PARAMETER.csv','ShortCode='+sys.argv[2],'CurrencyCode=USD','OrganizationCode='+sys.argv[3]]+[k+'='+v for k,v in r.items() if v and k not in skip]))" "<TPL>" <BU> <INV>
python -I "<B>" --export-dir exp1/unz --out "<RUN>/pay/pbf.zip" --prefix <PREFIX> --key "PO_SYSTEM_PARAMETER.csv=ShortCode" --row "$(cat row.txt)" --only
```
Success: `PO_SYSTEM_PARAMETER.csv: 1 row(s)` and the ZIP path. `CurrencyCode=USD` is a choice (any enabled currency; GUESS for others). No document type or negotiation terms rows are needed (VERIFIED).

## Step 3. Import ONCE (VERIFIED)
`<TASK>`=`PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION`, `"<NAME>"`=`"Configure Procurement Business Function"`, `<ZIP>`=`<RUN>/pay/pbf.zip`, `<DIR>`=`imp`. Success: `A total of 1 rows were processed. 0 rows of them failed` and `Business object: Procurement Configuration. Status: Completed successfully` (the document type and negotiation terms objects also say completed, with nothing in them).
Known refusal (VERIFIED): `JBO-27014: Attribute InventoryOrganizationId in PurchasingSystemParameterEO is required` = `OrganizationCode` empty. A refused row creates nothing (check with the export in Step 4 before a new try).

## Step 4. Read back (VERIFIED)
Export again into `exp2`, then:
```bash
cd "<RUN>"; python -I "<CMP>" exp1/unz exp2/unz --key "PO_SYSTEM_PARAMETER.csv=ShortCode" --key "PO_DOCUMENT_TYPE.csv=ShortCode+TypeName" --key "PO_DOCUMENT_TYPE_TRANSLATION.csv=PO_DOCUMENT_TYPE.ShortCode+PO_DOCUMENT_TYPE.TypeName+Language" --key "PON_CONTRACTS.csv=ShortCode+VersionNum" --expect "PO_SYSTEM_PARAMETER.csv=<BU>"
```
`RESULT: PASS` = `PO_SYSTEM_PARAMETER` +1 (`added: <BU>`), everything else added 0, removed 0, changed 0.

## Rules and limits
1. Only your own prefix business unit. Never send a row whose `ShortCode` is a real unit (the builder's `--key` check refuses an existing `ShortCode`).
2. No delete by CSV; the unit, its function and its configuration stay.
3. Document types (6 per unit) were not created for the test unit and were not needed by the import (VERIFIED); whether a buyer can create orders in such a unit is GUESS (not tried).
4. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-27, codes and ProcessIds only)
| Step | Result |
|---|---|
| Prerequisite 2 | own unit `GAPFILL_AB_B15_BU1` (made in a Common Features test) + function 110: ProcessId 100004744439440; 1 processed, 0 failed; compare `FUN_BU_USAGE` 1105 → 1106, all else unchanged |
| Try 1 | row without `OrganizationCode`: ProcessId 100004744439507; refused JBO-27014 InventoryOrganizationId required; export: nothing created |
| Try 2 | row with an existing inventory organization code: ProcessId 100004743463568; 1 processed, 0 failed |
| Read back | `PO_SYSTEM_PARAMETER` 14 → 15 (added `GAPFILL_AB_B15_BU1`), document types 84 = 84, negotiation terms 2 = 2, nothing removed or changed: PASS |
