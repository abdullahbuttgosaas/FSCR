---
skill_id: "gosaas.gap-fills.common-features.manage-configuration-owner-tax-options"
name: "Manage Configuration Owner Tax Options: add tax options for one owner and event class by FSM CSV (GoSaaS gap fill)"
description: "Reads configuration owner tax options (ZX_CONFIGURATION_OWNER_TAX_OPTIONS) by FSCR's setup-task CSV export and adds ONE new option row (owner + application + event class + tax type) by FSM CSV import, with an export compare as proof. Tested with a test legal entity as the owner (prefix name, nobody uses it). Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 08 (written) and batch 14 (tested), 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS"
task_name: "Manage Configuration Owner Tax Options"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/test-legal-entity (owner for a test)"
  - "ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS (only if you name your own factor set; the seeded TAXREGIME needs nothing)"
side_effects:
  - "Step 1 is read only."
  - "Step 3 adds tax options for the owner: tax handling of that owner's transactions of that event class changes from the defaults."
---

# Manage Configuration Owner Tax Options (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25 read, 2026-11-26 load) · **GUESS** = not run live.

## What it is and when to use
A configuration owner tax option row sets, for one **owner** (a business unit `OU` or a legal entity `FIRST_PARTY`), one application event class (for example Payables `AP_INVOICES` / `STANDARD INVOICES`) and one tax type (`IndirectTaxOrWhtFlag` `I` = indirect tax, `W` = withholding), how tax is handled: allow overrides and manual lines, exemptions, rounding level, enforce tax from account or reference document, determining factor set (`DetFactorTemplCode`), and more. Without a row, Oracle's defaults apply.
Use it when a business unit or legal entity needs tax handling different from the defaults. **For a test**, use your own test legal entity as the owner: a new row for a real owner changes that owner's real transactions.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py   (offline builder, new rows only)
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo
OWNER = owner name: a legal entity name (PartyTypeCode FIRST_PARTY) or a business unit name (PartyTypeCode OU)
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names.

## Prerequisites
1. The owner exists. **For a test:** your own legal entity from `<GAPS>/common-features/test-legal-entity/SKILL.md` (GET first: REST `legalEntitiesLOV`, `q=LegalEntityIdentifier='<LE>'`; create only if count 0). The owner name is the legal entity **name**.
   Check command (read only; run from `<RUN>`; a timeout on a GET is safe to repeat):
   ```bash
   cd "<RUN>"; python -B "<GAPS>/common-features/scripts/rest_call.py" "<FSCR>" /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV --query onlyData=true --query "q=LegalEntityIdentifier='<LE>'" --no-open-browser --output le.json > le.log 2>&1; python -I -c "import json; d=json.load(open('le.json',encoding='utf-8')); print(d['count'], [i['Name'] for i in d['items']])"
   ```
   `1` and your name = it exists, use it. `0` = create it with the test-legal-entity skill. (`<LE>` is the identifier; for a test legal entity the name is the same.)
2. A determining factor set: the seeded `TAXREGIME` (VERIFIED, used by existing rows) needs nothing; your own set needs `manage-tax-factor-sets` first.

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
```
1 CSV `ZX_CONFIGURATION_OWNER_TAX_OPTIONS.csv` + metadata. Key: `PartyName`, `ApplicationId`, `EntityCode`, `EventClassCode`, `IndirectTaxOrWhtFlag` (plus `EffectiveFrom`). Check that your owner has no row for that event class and tax type yet: `grep -c "<OWNER>" "<RUN>/exp1/unz/ZX_CONFIGURATION_OWNER_TAX_OPTIONS.csv"` → 0 for a new test owner. If your owner already has a row with the same application, entity, event class and tax type, **stop**: a new import with that key would update it (pick another event class, or ask the owner). No ZIP: run again into a NEW folder, up to 3 tries.

## Step 2. Build the row (offline, VERIFIED)
Give only business columns; **leave every who column empty** (`CreatedBy`, `CreationDate`, `LastUpdatedBy`, `LastUpdateDate`, `LastUpdateLogin`) and `ObjectVersionNumber` if present. Tested row (Payables standard invoices, indirect tax, legal entity owner):
```bash
cd "<RUN>"; O=<OWNER>
python -I "<B>" --export-dir exp1/unz --out-dir pay --zip-name coto.zip --prefix <PREFIX> \
 --key "ZX_CONFIGURATION_OWNER_TAX_OPTIONS.csv=PartyName,ApplicationId,EntityCode,EventClassCode,IndirectTaxOrWhtFlag" \
 --prefix-col "ZX_CONFIGURATION_OWNER_TAX_OPTIONS.csv=PartyName" \
 --row "ZX_CONFIGURATION_OWNER_TAX_OPTIONS.csv|ApplicationId=200|ApplicationId1=200|ApplicationShortName=AP|EntityCode=AP_INVOICES|EventClassCode=STANDARD INVOICES|EffectiveFrom=<today yyyy/mm/dd>|EnabledFlag=Y|IndirectTaxOrWhtFlag=I|PartyTypeCode=FIRST_PARTY|PartyName=$O|AllowExemptionsFlag=N|AllowManualLinRecalcFlag=Y|AllowManualLinesFlag=Y|AllowOffsetTaxCalcFlag=Y|AllowOverrideFlag=Y|CtrlEffOvrdCalcLinesFlag=Y|DefaultRoundingLevelCode=HEADER|DetFactorTemplCode=TAXREGIME|EnforceTaxFromAcctFlag=Y|EnforceTaxFromRefDocFlag=N|EnterOvrdInclTaxLinesFlag=N|PerfAddnlApplForImprtFlag=Y|ProcessForApplicabilityFlag=N|RecordTypeCode=USER_DEFINED|TaxVarianceCalcFlag=Y"
```
For a real (non-prefix) owner, drop `--prefix-col` and get written approval first. `PartyTypeCode`: `FIRST_PARTY` for a legal entity (VERIFIED), `OU` for a business unit (VERIFIED in existing rows). Payables `ApplicationId` is 200 (VERIFIED); other applications: copy the ids from an existing row of that application (GUESS).

## Step 3. Import (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS --task-name "Manage Configuration Owner Tax Options" --zip-file "<RUN>/pay/coto.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
```
Write down the ProcessId. Result in `<RUN>/imp/*_process_log.txt`: `A total of 1 rows were processed. 0 rows of them failed`, `Configuration Owner Tax Option. Status: Completed successfully`. Dropped connection: never import again; wait 2 minutes and read back.

**Read the log safely:** the process log and the file names in `<RUN>/imp` hold the environment name and the submitting user; never print the whole log, never list that folder into a report. Print only the result lines:
```bash
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```


## Step 4. Read back (VERIFIED)
Export again: run Step 1 again with `exp2` in place of `exp1` (both the export line and the unzip line), then:
```bash
python -I "<CMP>" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --key "ZX_CONFIGURATION_OWNER_TAX_OPTIONS.csv=PartyName,ApplicationId,EntityCode,EventClassCode,IndirectTaxOrWhtFlag" --expect "ZX_CONFIGURATION_OWNER_TAX_OPTIONS.csv=<OWNER>,200,AP_INVOICES,STANDARD INVOICES,I"
```
PASS = exactly your row added, none removed or changed. Your row shows `PartyTypeCode FIRST_PARTY`, `EnabledFlag Y`.

## Rules and limits
1. New rows only; never re-import an existing owner's row (that updates it).
2. A test uses only your own test owner. The CSV route cannot delete a row (set `EnabledFlag N` by a later import of your own row to stop it; GUESS, not tested).
3. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Owner | own legal entity `GAPFILL_AB_B14_LE1` |
| Import | AP / STANDARD INVOICES / I; ProcessId 100004743430482; 1 processed, 0 failed |
| Compare | 4 → 5 rows, only own row added: PASS. (The test row also carried the export's creation date by mistake; Oracle ignored it and set its own. The skill now leaves who columns empty.) |
