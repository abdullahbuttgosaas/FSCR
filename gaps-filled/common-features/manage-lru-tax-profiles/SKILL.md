---
skill_id: "gosaas.gap-fills.common-features.manage-lru-tax-profiles"
name: "Manage Legal Reporting Unit Tax Profiles: read and change the tax profile of a legal reporting unit by FSM CSV (GoSaaS gap fill)"
description: "Reads the legal reporting unit (establishment) tax profiles by FSCR's setup-task CSV export (a 73-file package) and changes ONE profile (ZX_ESTABLISHMENT_TAX_PROFILE) by FSM CSV import, every other file header only, with an export compare as proof. Tested on the main reporting unit of a test legal entity made for the test. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 08 (written) and batch 14 (tested), 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES"
task_name: "Manage Legal Reporting Unit Tax Profiles"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/test-legal-entity (for a test)"
  - "gosaas common-features/scripts/own_row_package.py, compare_own_update.py"
side_effects:
  - "Steps 1 and 2 are read only."
  - "Step 4 UPDATES one existing reporting unit tax profile: tax and tax reporting of transactions of that reporting unit."
---

# Manage Legal Reporting Unit Tax Profiles (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25 read, 2026-11-26 change) · **GUESS** = not run live.

## What it is and when to use
Each legal reporting unit (establishment) has one tax profile: rounding, inclusive tax, self-assessment, registrations, fiscal classifications. Oracle **creates it with the reporting unit** (VERIFIED: the main reporting unit of a new legal entity got its profile at once, `PartyTypeCode LEGAL_ESTABLISHMENT`, `LegalEstablishmentName` = the unit name). A load therefore **changes** an existing profile.
- Read: Steps 1 to 2. Change one profile: Steps 3 to 5, on the unit the owner names or, for a test, on **your own test legal entity's** main reporting unit only.
- Fiscal classification codes on the profile (the other 72 files) are a separate change: use the fiscal classification gap skills for codes (GUESS for the link rows; not tested here).

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
S     = <GAPS>/common-features/scripts   (own_row_package.py, compare_own_update.py)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo
LE    = the legal entity identifier (for the check in Prerequisite 1)
LRU   = LegalEstablishmentName of the reporting unit (a new legal entity's main unit has the legal entity's name)
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names.

## Prerequisites
1. The reporting unit exists. **For a test:** your own legal entity from `<GAPS>/common-features/test-legal-entity/SKILL.md` (GET first with REST `legalEntitiesLOV`, `q=LegalEntityIdentifier='<LE>'`; create only if count 0). Its main reporting unit and that unit's tax profile come with it.
   Check command (read only; run from `<RUN>`; a timeout on a GET is safe to repeat):
   ```bash
   cd "<RUN>"; python -B "<GAPS>/common-features/scripts/rest_call.py" "<FSCR>" /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV --query onlyData=true --query "q=LegalEntityIdentifier='<LE>'" --no-open-browser --output le.json > le.log 2>&1; python -I -c "import json; d=json.load(open('le.json',encoding='utf-8')); print(d['count'], [i['Name'] for i in d['items']])"
   ```
   `1` and your name = it exists, use it. `0` = create it with the test-legal-entity skill. (`<LE>` is the identifier; for a test legal entity the name is the same.)

## Step 1. Read-only export (VERIFIED, 2 to 5 minutes; allow 7 minutes per export or import command, or run it in the background)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
```
73 CSVs + metadata. The profile file is `ZX_ESTABLISHMENT_TAX_PROFILE.csv` (one row per reporting unit; columns `PartyTypeCode`, `PartyNumber`, `LegalEntityIdentifier`, `LegalEstablishmentName`, `RoundingRuleCode`, `RoundingLevelCode`, ...). The other files are fiscal classification rows. No ZIP: run again into a NEW folder, up to 3 tries.

## Step 2. Find the profile (read only, VERIFIED)
`grep -c "<LRU>" <RUN>/exp1/unz/ZX_ESTABLISHMENT_TAX_PROFILE.csv` → 1. Read it: `python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/exp1/unz" --value "<LRU>" --match-cols LegalEstablishmentName --file ZX_ESTABLISHMENT_TAX_PROFILE.csv` (only that file; the viewer hides who and person columns and empty columns, so empty rounding columns do not show; Step 3 prints the old value as `'' -> ...`).

## Step 3. Build the change (offline, VERIFIED)
One row from **this** export, approved columns only. Tested example: `RoundingRuleCode NEAREST`, `RoundingLevelCode LINE`.
```bash
cd "<RUN>"; python -I "<S>/own_row_package.py" --export-dir exp1/unz --file ZX_ESTABLISHMENT_TAX_PROFILE.csv --match LegalEstablishmentName=<LRU> --prefix <PREFIX> --set RoundingRuleCode=NEAREST --set RoundingLevelCode=LINE --out-dir pay --zip-name lrutp.zip
```
The other 72 files go in header only (the helper does this).

## Step 4. Import (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES --task-name "Manage Legal Reporting Unit Tax Profiles" --zip-file "<RUN>/pay/lrutp.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
```
Write down the ProcessId. Result in `<RUN>/imp/*_process_log.txt`: `A total of 1 rows were processed. 0 rows of them failed`, 42 business objects listed, all `Completed successfully` (most of them had no rows: normal). Never import the whole export. Dropped connection: never import again; wait 2 minutes and read back.

**Read the log safely:** the process log and the file names in `<RUN>/imp` hold the environment name and the submitting user; never print the whole log, never list that folder into a report. Print only the result lines:
```bash
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```


## Step 5. Read back (VERIFIED)
Export again: run Step 1 again with `exp2` in place of `exp1` (both the export line and the unzip line; if that export had to be run again into a new folder, use that folder instead of `exp2` below), then:
```bash
python -I "<S>/compare_own_update.py" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --file ZX_ESTABLISHMENT_TAX_PROFILE.csv --key LegalEstablishmentName,PartyNumber --own <LRU> --expect RoundingRuleCode=NEAREST --expect RoundingLevelCode=LINE
```
PASS = same count, other rows changed 0, your row has the new values. Also check that no other file changed its row count, with a CSV reader (a field can span lines, so `wc -l` can miscount):
```bash
python -I -c "import csv,sys,glob,os; [print(os.path.basename(f), sum(1 for _ in csv.reader(open(f,encoding='utf-8-sig')))-1, sum(1 for _ in csv.reader(open(f.replace(sys.argv[1],sys.argv[2]),encoding='utf-8-sig')))-1) for f in sorted(glob.glob(sys.argv[1]+'/*.csv'))]" "<RUN>/exp1/unz" "<RUN>/exp2/unz"
```
Every line must show two equal numbers. (Row counts differ between environments and grow as testers add legal entities.)

## Rules and limits
1. One profile row, approved columns only; a test changes only your own test unit.
2. Tested on one environment (release 11.13.26.10.0), US unit.

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Prerequisite | own legal entity `GAPFILL_AB_B14_LE1`; its unit `GAPFILL_AB_B14_LE1` |
| Change | rounding `NEAREST` / `LINE`; ProcessId 100004744411602; 42 objects, 0 failed |
| Compare | 68 → 68 profile rows, other rows changed 0, own row changed only the 2 columns; all 73 file counts unchanged: PASS |
