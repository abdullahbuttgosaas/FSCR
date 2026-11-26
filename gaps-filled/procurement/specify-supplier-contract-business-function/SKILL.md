---
skill_id: "gosaas.gap-fills.procurement.specify-supplier-contract-business-function"
name: "Specify Supplier Contract Management Business Function Properties for a NEW test business unit by FSM CSV (GoSaaS gap fill)"
description: "Adds the contract management properties row (OKC_BU_IMPL_OPTIONS) for your OWN prefix business unit through FSCR's setup-task CSV export and import, with settings copied from a working row; proves by a second export that only your row was added. Never changes a real business unit. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 03 (2026-11-25, written unsafe), re-opened and tested in batch 07 (2026-11-27) with an own test business unit. NOT official FSCR."
task_code: "OKC_SPECIFY_PROCUREMENT_CONTRACT_MGMT_BUSINESS_FUNC_PROP"
task_name: "Specify Supplier Contract Management Business Function Properties"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.2.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gaps-filled procurement/configure-procurement-business-function (Prerequisite 2: Procurement business function on the unit)"
side_effects:
  - "Adds one contract management properties row for YOUR prefix business unit. No real business unit is touched. No delete by CSV: plan as if it stays."
---

# Specify Supplier Contract Management Business Function Properties (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR routes the task (CSV flag Y) but has no skill. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-27) · **GUESS** = not run live.
> Version 0.1.0 (2026-11-25) said a test is unsafe because every row belongs to a live business unit. The safe way is a NEW prefix business unit that nobody uses (VERIFIED here).

## What it is and when to use
Each business unit that uses contract management has one properties row (`OKC_BU_IMPL_OPTIONS.csv`, the only CSV of the package, VERIFIED): currency, clause numbering, Contract Expert, layout templates, the global business unit flag, invoice numbering. Use this skill to add the row for a **new** business unit. Never send a row of an existing unit: an import updates it.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds procurement\ and common-features\)
B     = <GAPS>/procurement/scripts/build_csv_package.py   (offline package builder)
CMP   = <GAPS>/procurement/scripts/compare_exports.py
W     = <GAPS>/common-features/scripts/rest_call.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); create it first: mkdir -p "<RUN>"
PREFIX= your test prefix, e.g. GAPFILL_XX_
BU    = your own prefix business unit, e.g. GAPFILL_XX_BU1
BUID  = its id, read live in Prerequisite 3
TPL   = OrganizationName of an existing row to copy settings from (Step 1 lists them)
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; a valid cached sign-in returns at once). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names; never print `ASM_SETUP_CSV_METADATA.xml`.

## Prerequisites
1. **Your own business unit** (never a real one): an existing prefix unit of yours, or a new one made with `<GAPS>/common-features/test-business-unit/SKILL.md`.
2. **The Procurement business function on it:** follow Prerequisite 2 of `<GAPS>/procurement/configure-procurement-business-function/SKILL.md` (function `ModuleId` 110). GUESS that it is needed: the test unit had it; a unit without it was not tried.
3. **Read the unit's id live** (read only, VERIFIED):
   ```bash
   cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV --query "q=BusinessUnitName='<BU>'" --query onlyData=true --no-open-browser --output bu.json > bu.log 2>&1
   python -I -c "import json; print([(x['BusinessUnitName'],x['BusinessUnitId'],x['PrimaryLedgerId']) for x in json.load(open('bu.json',encoding='utf-8'))['items']])"
   ```
   One row; its `BusinessUnitId` is `<BUID>`. (Control, VERIFIED: the same call for a real unit gives the `OrgId` that unit has in the export.)

## Step 1. Read-only export (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code OKC_SPECIFY_PROCUREMENT_CONTRACT_MGMT_BUSINESS_FUNC_PROP --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; z=glob.glob(sys.argv[1]+'/*.zip'); sys.exit('NO ZIP: run again into a new folder') if not z else zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
cd "<RUN>"; python -I -c "import csv; [print(r['OrganizationName'],'|',r['GlobalBusUnitYn'],'|',r['LedgerYn'],'|',r['DefaultCurrencyCode']) for r in csv.DictReader(open('exp1/unz/OKC_BU_IMPL_OPTIONS.csv',encoding='utf-8-sig'))]"
```
`<BU>` must not be listed. Pick `<TPL>` from the list. No ZIP: run again into a NEW folder, up to 3 tries.

## Step 2. Build your row (offline, VERIFIED)
Copy TPL's settings, but not its unit, its person (terms library administrator) or audit columns; set `GlobalBusUnitYn=N` (only one global unit is allowed) and `LedgerYn=N` (the unit's currency then comes from `DefaultCurrencyCode`, not from a ledger):
```bash
cd "<RUN>"; python -I -c "import csv,sys; r=[x for x in csv.DictReader(open('exp1/unz/OKC_BU_IMPL_OPTIONS.csv',encoding='utf-8-sig')) if x['OrganizationName']==sys.argv[1]][0]; skip={'CreatedBy','LastUpdatedBy','LastUpdateLogin','CreationDate','LastUpdateDate','OrganizationCode','OrgId','OrganizationName','PcTermsLibAdminName','PcTermsLibAdminNumber','EnterpriseName','ObjectVersionNumber','GlobalBusUnitYn','LedgerYn','DefaultCurrencyCode'}; bu=sys.argv[2]; own=['OrganizationName='+bu,'OrganizationCode='+bu+'\$\$?\$\$FUN_BUSINESS_UNIT','OrgId='+sys.argv[3],'GlobalBusUnitYn=N','LedgerYn=N','DefaultCurrencyCode=USD']; open('row.txt','w',encoding='utf-8').write('|'.join(['OKC_BU_IMPL_OPTIONS.csv']+own+[k+'='+v for k,v in r.items() if v and k not in skip]))" "<TPL>" <BU> <BUID>
python -I "<B>" --export-dir exp1/unz --out "<RUN>/pay/okc.zip" --prefix <PREFIX> --key "OKC_BU_IMPL_OPTIONS.csv=OrganizationName" --row "$(cat row.txt)" --only
```
Success: `OKC_BU_IMPL_OPTIONS.csv: 1 row(s)` and the ZIP path. `OrganizationCode` is the unit's code as the Manage Business Unit export writes it (`<BU>$$?$$FUN_BUSINESS_UNIT` for a unit made with the GoSaaS test-business-unit skill, VERIFIED); check `FUN_BUSINESS_UNIT.csv` of that export if your unit was made another way.

## Step 3. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code OKC_SPECIFY_PROCUREMENT_CONTRACT_MGMT_BUSINESS_FUNC_PROP --task-name "Specify Supplier Contract Management Business Function Properties" --zip-file "<RUN>/pay/okc.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^\]{0,200}|JBO-[0-9]+: [^\]{0,160}" "<RUN>"/imp/*_process_log.txt | sort -u
```
Write down the ProcessId. Success: `A total of 1 rows were processed. 0 rows of them failed` and `Business object: Contract Management Business Function. Status: Completed successfully`. Known refusals (VERIFIED, each created nothing):
- `OKC_BUSET_MIGINVALID_DATA ... Allow related customer accounts` = a hand-made short row; copy the template's settings (Step 2).
- `OKC_BUSET_GLOBALBUEXISTS You can specify only 1 global business unit` = `GlobalBusUnitYn=Y`.
- `JBO-27014: Attribute DefaultCurrencyCode in BuImplOptionEO is required` = `LedgerYn=Y` on a unit with no ledger.
Dropped connection after the ProcessId: never import again; wait 2 minutes and go to Step 4.

## Step 4. Read back (VERIFIED)
Export again (Step 1's first two lines with `exp1` → `exp2`), then:
```bash
cd "<RUN>"; python -I "<CMP>" exp1/unz exp2/unz --key "OKC_BU_IMPL_OPTIONS.csv=OrganizationName" --expect "OKC_BU_IMPL_OPTIONS.csv=<BU>"
```
`RESULT: PASS` = 1 row added (`added: <BU>`), 0 removed, 0 changed.

## Rules and limits
1. Only your own prefix business unit; the builder's `--key` check refuses a unit that already has a row.
2. No delete by CSV.
3. Tested with settings copied from one working row; other values are GUESS. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-27, codes and ProcessIds only)
| Step | Result |
|---|---|
| Prerequisites | own unit `GAPFILL_AB_B15_BU1` with function 110 (see the procurement business function skill); id read by REST |
| Try 1 | short hand-made row: ProcessId 100004744437661, `OKC_BUSET_MIGINVALID_DATA` (related customer accounts) |
| Try 2 | all template settings: ProcessId 100004743463605, `OKC_BUSET_GLOBALBUEXISTS` |
| Try 3 | `GlobalBusUnitYn=N`: ProcessId 100004743465019, JBO-27014 `DefaultCurrencyCode` required; export: still 1 row, nothing created |
| Try 4 | `LedgerYn=N`: ProcessId 100004743463626; 1 processed, 0 failed |
| Read back | rows 1 → 2 (added `GAPFILL_AB_B15_BU1`), nothing removed or changed: PASS |
