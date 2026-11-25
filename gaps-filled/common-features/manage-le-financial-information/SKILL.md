---
skill_id: "gosaas.gap-fills.common-features.manage-le-financial-information"
name: "Manage Legal Entity Financial Information: set the activity code (and context segments) of a legal entity by FSM CSV (GoSaaS gap fill)"
description: "Reads a legal entity's financial information (activity code, Legal Entity Context flexfield segments LeInformation1-20) from the legal entity package exported under this task code, and changes it for ONE legal entity by FSM CSV import (one XLE_ENTITY_PROFILE row), with an export compare as proof. Tested on a test legal entity made for the test. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 14, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "XLE_MANAGE_LEGAL_ENTITY_FINANCIAL_INFORMATION"
task_name: "Manage Legal Entity Financial Information"
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
  - "gosaas common-features/scripts/own_row_package.py, compare_own_update.py"
side_effects:
  - "Step 1 is read only."
  - "Step 3 UPDATES one existing legal entity (its financial information fields)."
---

# Manage Legal Entity Financial Information (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
The task opens the legal entity's **financial information**: the **activity code** (`ActivityCode`, the main activity; validated against the **NAICS 1997** classification, VERIFIED by Oracle's error) and the **Legal Entity Context** flexfield segments `LeInformation1` to `LeInformation20` under context `LeInformationContext` (country, e.g. `US`) (Oracle docs; the segments in use depend on the context: GUESS, none filled on our environment). The task has **no package of its own**: its export is the full legal entity package (VERIFIED: the same 7 CSVs as Manage Legal Entity), but the metadata names this task.
Use it to set or correct those fields on an existing legal entity. A test changes only **your own** test legal entity.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
S     = <GAPS>/common-features/scripts   (own_row_package.py, compare_own_update.py)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo
LE    = LegalEntityIdentifier (for a test: your own, starting with PREFIX)
CODE  = a NAICS 1997 code, 2 to 6 digits, e.g. 541511 (custom computer programming services)
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names.

## Prerequisites
1. The legal entity exists. **For a test:** your own from `<GAPS>/common-features/test-legal-entity/SKILL.md` (GET first: REST `legalEntitiesLOV`, `q=LegalEntityIdentifier='<LE>'`; create only if count 0).
   Check command (read only; run from `<RUN>`; a timeout on a GET is safe to repeat):
   ```bash
   cd "<RUN>"; python -B "<GAPS>/common-features/scripts/rest_call.py" "<FSCR>" /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV --query onlyData=true --query "q=LegalEntityIdentifier='<LE>'" --no-open-browser --output le.json > le.log 2>&1; python -I -c "import json; d=json.load(open('le.json',encoding='utf-8')); print(d['count'], [i['Name'] for i in d['items']])"
   ```
   `1` and your name = it exists, use it. `0` = create it with the test-legal-entity skill. (`<LE>` is the identifier; for a test legal entity the name is the same.)

## Step 1. Read-only export under THIS task code (VERIFIED, about 1 to 5 minutes)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code XLE_MANAGE_LEGAL_ENTITY_FINANCIAL_INFORMATION --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
grep -o "<ObjectShortName>[^<]*" "<RUN>/exp1/unz/ASM_SETUP_CSV_METADATA.xml"
```
The last line must print `XLE_MANAGE_LEGAL_ENTITY_FINANCIAL_INFORMATION`. **A package built from a Manage Legal Entity export is refused at submit with HTTP 400** (VERIFIED): always export under this task code. Read the current values: `python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/exp1/unz" --value "<LE>" --match-cols LegalEntityIdentifier --file XLE_ENTITY_PROFILE.csv`. The viewer hides empty columns: no `ActivityCode` in its output means it is empty (Step 2 prints the old value as `'' -> ...`).

## Step 2. Build the change (offline, VERIFIED)
One `XLE_ENTITY_PROFILE` row from **this** export with the approved column(s) changed; all other files header only.
```bash
cd "<RUN>"; python -I "<S>/own_row_package.py" --export-dir exp1/unz --file XLE_ENTITY_PROFILE.csv --match LegalEntityIdentifier=<LE> --prefix <PREFIX> --set ActivityCode=<CODE> --out-dir pay --zip-name lefi.zip
```
Context segments: `--set LeInformation<N>=<value>` (keep `LeInformationContext` as exported; GUESS, not tested).

## Step 3. Import (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code XLE_MANAGE_LEGAL_ENTITY_FINANCIAL_INFORMATION --task-name "Manage Legal Entity Financial Information" --zip-file "<RUN>/pay/lefi.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
```
Write down the ProcessId. Result in `<RUN>/imp/*_process_log.txt`: `A total of 1 rows were processed. 0 rows of them failed`, `Legal Entity. Status: Completed successfully` (a line `Status: In progress` for the same object and a first line `0 rows were processed` for another batch is normal). A wrong code gives `FND_VS_VAL_NOT_IN_LIST ... NAICS 1997 <value> is not in the list of values` and changes nothing. Dropped connection: never import again; wait 2 minutes and read back.

**Read the log safely:** the process log and the file names in `<RUN>/imp` hold the environment name and the submitting user; never print the whole log, never list that folder into a report. Print only the result lines:
```bash
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```


## Step 4. Read back (VERIFIED)
Export again: run Step 1 again with `exp2` in place of `exp1` (both the export line and the unzip line), then:
```bash
python -I "<S>/compare_own_update.py" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --file XLE_ENTITY_PROFILE.csv --key LegalEntityIdentifier --own <LE> --expect ActivityCode=<CODE>
```
PASS = 0 other rows changed, your row changed only `ActivityCode`.

## Rules and limits
1. One legal entity row from a fresh export (an older export would undo later changes to the same legal entity).
2. The reporting unit's own activity code is the separate task Manage Legal Reporting Unit Financial Information.
3. Tested on one environment (release 11.13.26.10.0), US legal entity.

## Worked example (2026-11-26, codes and ProcessIds only)
| Try | Result |
|---|---|
| 1 | package built from a Manage Legal Entity export: HTTP 400 at submit, no process |
| 2 | own export, `ActivityCode GAPFILL_PROBE`: ProcessId 100004743429588, refused `NAICS 1997 ... is not in the list of values`, nothing changed |
| 3 | `ActivityCode 541511` on `GAPFILL_AB_B14_LE1`: ProcessId 100004743429645, 1 processed, 0 failed; compare PASS (68 rows, other rows changed 0) |
