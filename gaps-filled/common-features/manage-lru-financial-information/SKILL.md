---
skill_id: "gosaas.gap-fills.common-features.manage-lru-financial-information"
name: "Manage Legal Reporting Unit Financial Information: set the activity code (and context segments) of a legal reporting unit by FSM CSV (GoSaaS gap fill)"
description: "Reads a legal reporting unit's financial information (activity code, EtbInformation context segments) from the legal entity package exported under this task code, and changes it for ONE reporting unit by FSM CSV import (its XLE_ETB_PROFILE row plus its legal entity row unchanged), with an export compare as proof. Tested on the main reporting unit of a test legal entity made for the test. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 14, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "XLE_MANAGE_LEGAL_REPORTING_UNIT_FINANCIAL_INFORMATION"
task_name: "Manage Legal Reporting Unit Financial Information"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/test-legal-entity (for a test)"
  - "gosaas common-features/scripts/own_row_package.py (--copy), compare_own_update.py"
side_effects:
  - "Step 1 is read only."
  - "Step 3 UPDATES one existing legal reporting unit (its financial information fields); its legal entity row goes in unchanged."
---

# Manage Legal Reporting Unit Financial Information (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
The reporting unit version of legal entity financial information: the unit's **activity code** (`ActivityCode` on `XLE_ETB_PROFILE`, a **NAICS 1997** code: the same check as on the legal entity, GUESS that the list is the same; `541511` was accepted, VERIFIED) and its context segments `EtbInformation1..20` under `EtbInformationContext` (GUESS, not tested). The task has **no package of its own**: its export is the full legal entity package (7 CSVs) with this task's name in the metadata (VERIFIED).
Use it to set those fields on an existing unit. A test changes only **your own** test legal entity's main unit.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
S     = <GAPS>/common-features/scripts   (own_row_package.py, compare_own_update.py)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (the prerequisite check writes le.json / le.log into it first: fine)
LE    = the unit's LegalEntityIdentifier (for a test: your own, starting with PREFIX)
LRU   = the unit Name in XLE_ETB_PROFILE (a new legal entity's main unit has the legal entity's name)
CODE  = a NAICS 1997 code, e.g. 541511
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names.

## Prerequisites
1. The unit exists. **For a test:** your own legal entity from `<GAPS>/common-features/test-legal-entity/SKILL.md` (GET first: REST `legalEntitiesLOV`, `q=LegalEntityIdentifier='<LE>'`; create only if count 0); its main unit comes with it.
   Check command (read only; run from `<RUN>`; a timeout on a GET is safe to repeat):
   ```bash
   cd "<RUN>"; python -B "<GAPS>/common-features/scripts/rest_call.py" "<FSCR>" /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV --query onlyData=true --query "q=LegalEntityIdentifier='<LE>'" --no-open-browser --output le.json > le.log 2>&1; python -I -c "import json; d=json.load(open('le.json',encoding='utf-8')); print(d['count'], [i['Name'] for i in d['items']])"
   ```
   `1` and your name = it exists, use it. `0` = create it with the test-legal-entity skill. (`<LE>` is the identifier; for a test legal entity the name is the same.)

## Step 1. Read-only export under THIS task code (VERIFIED, about 1 to 5 minutes)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code XLE_MANAGE_LEGAL_REPORTING_UNIT_FINANCIAL_INFORMATION --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
grep -o "<ObjectShortName>[^<]*" "<RUN>/exp1/unz/ASM_SETUP_CSV_METADATA.xml"
```
Must print `XLE_MANAGE_LEGAL_REPORTING_UNIT_FINANCIAL_INFORMATION` (a package built from another task's export is refused with HTTP 400; VERIFIED for the legal entity task). Take this export **after** any other change to the same legal entity: the legal entity row goes into the package unchanged, so an older export would undo later changes. Read the unit: `python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/exp1/unz" --value "<LRU>" --match-cols Name --file XLE_ETB_PROFILE.csv`. The viewer hides empty columns: no `ActivityCode` in its output means it is empty.

## Step 2. Build the change (offline, VERIFIED)
The unit row is a child of the legal entity row: the parent must be in the package **unchanged** (`--copy`).
```bash
cd "<RUN>"; python -I "<S>/own_row_package.py" --export-dir exp1/unz --file XLE_ETB_PROFILE.csv --match Name=<LRU> --prefix <PREFIX> --set ActivityCode=<CODE> --copy "XLE_ENTITY_PROFILE.csv|LegalEntityIdentifier=<LE>" --out-dir pay --zip-name lrufi.zip
```

## Step 3. Import (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code XLE_MANAGE_LEGAL_REPORTING_UNIT_FINANCIAL_INFORMATION --task-name "Manage Legal Reporting Unit Financial Information" --zip-file "<RUN>/pay/lrufi.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
```
Write down the ProcessId. Result in `<RUN>/imp/*_process_log.txt`: `A total of 1 rows were processed. 0 rows of them failed` (plus a line `A total of 0 rows were processed. 0 rows of them failed` for the unchanged legal entity batch: normal), `Legal Reporting Unit. Status: Completed successfully` (an extra line `Status: In progress` for the same object is normal). Dropped connection: never import again; wait 2 minutes and read back.

**Read the log safely:** the process log and the file names in `<RUN>/imp` hold the environment name and the submitting user; never print the whole log, never list that folder into a report. Print only the result lines:
```bash
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```


## Step 4. Read back (VERIFIED)
Export again: run Step 1 again with `exp2` in place of `exp1` (both the export line and the unzip line), then both checks:
```bash
python -I "<S>/compare_own_update.py" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --file XLE_ETB_PROFILE.csv --key Name --own <LRU> --expect ActivityCode=<CODE>
python -I "<S>/compare_own_update.py" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --file XLE_ENTITY_PROFILE.csv --key LegalEntityIdentifier --own <LE>
```
PASS twice: the unit changed only `ActivityCode`; the legal entity row changed nothing (`changed columns: []`); 0 other rows changed.

## Rules and limits
1. One unit row plus its parent unchanged, from a fresh export.
2. Tested on one environment (release 11.13.26.10.0), US unit.

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Unit | main unit `GAPFILL_AB_B14_LE1` of own legal entity `GAPFILL_AB_B14_LE1` |
| Import | `ActivityCode 541511`; ProcessId 100004743429712; 1 processed, 0 failed |
| Compare | unit: 68 rows (counts vary by environment), other rows changed 0, changed only ActivityCode: PASS; legal entity row unchanged: PASS |
