---
skill_id: "gosaas.gap-fills.common-features.manage-legal-entity-tax-profiles"
name: "Manage Legal Entity Tax Profiles: read and change the tax profile of a legal entity by FSM CSV (GoSaaS gap fill)"
description: "Reads the legal entity tax profiles (ZX_LEGAL_ENTITY_TAX_PROFILE) by FSCR's setup-task CSV export and changes ONE profile by FSM CSV import (one row, approved columns only), with an export compare as proof. Tested on a test legal entity made for the test (prefix name, nobody uses it). Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 08 (written) and batch 14 (tested), 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES"
task_name: "Manage Legal Entity Tax Profiles"
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
  - "Steps 2 and 3 are read only."
  - "Step 5 UPDATES one existing legal entity tax profile: rounding, inclusive tax, withholding and other tax settings of every transaction of that legal entity."
---

# Manage Legal Entity Tax Profiles (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25 read, 2026-11-26 change) · **GUESS** = not run live.

## What it is and when to use
A legal entity tax profile holds the tax settings of a first-party legal entity: rounding level and rule, tax-inclusive handling, its own subscription (`UseLeAsSubscriberFlag`), self-assessment, offset taxes, withholding settings, default tax classification. Oracle **creates one profile with each legal entity** (VERIFIED: a new legal entity got its profile at once, `PartyTypeCode FIRST_PARTY`). So the task never creates a record: a load **changes** an existing profile.
- To read a profile: Steps 1 to 3.
- To change one: Steps 4 to 6, on the legal entity the owner names (real use) or on **your own test legal entity** (a test on a shared environment). Never change another person's or a real legal entity's profile in a test.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
S     = <GAPS>/common-features/scripts   (own_row_package.py, compare_own_update.py)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (exports hold user names)
LE    = LegalEntityIdentifier of the legal entity whose profile you change (for a test: your own, starting with PREFIX)
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...` (never `$PWD` or `/e/...`); `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name).

## Prerequisites
1. The legal entity exists. **For a test:** your own legal entity made with `<GAPS>/common-features/test-legal-entity/SKILL.md` (check first that it exists: REST `legalEntitiesLOV` with `q=LegalEntityIdentifier='<LE>'`; create it only if count is 0). Its profile is made by Oracle with it.
   Check command (read only; run from `<RUN>`; a timeout on a GET is safe to repeat):
   ```bash
   cd "<RUN>"; python -B "<GAPS>/common-features/scripts/rest_call.py" "<FSCR>" /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV --query onlyData=true --query "q=LegalEntityIdentifier='<LE>'" --no-open-browser --output le.json > le.log 2>&1; python -I -c "import json; d=json.load(open('le.json',encoding='utf-8')); print(d['count'], [i['Name'] for i in d['items']])"
   ```
   `1` and your name = it exists, use it. `0` = create it with the test-legal-entity skill. (`<LE>` is the identifier; for a test legal entity the name is the same.)
2. For a real change: the owner's approval naming LE and the columns.

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
```
2 files: `ZX_LEGAL_ENTITY_TAX_PROFILE.csv` (60 columns, one row per legal entity; key `LegalEntityIdentifier` + `PartyTypeCode`) and `ASM_SETUP_CSV_METADATA.xml`. No ZIP: run again into a NEW folder, up to 3 tries.

## Step 2. Find the profile (read only, VERIFIED)
`grep -c "<LE>" <RUN>/exp1/unz/ZX_LEGAL_ENTITY_TAX_PROFILE.csv` → 1. A new legal entity's profile has only `PartyTypeCode FIRST_PARTY` and `RecordTypeCode USER_DEFINED` filled.

## Step 3. Read it (read only)
`python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/exp1/unz" --value "<LE>" --match-cols LegalEntityIdentifier` shows the row without audit or person columns.

## Step 4. Build the change (offline, VERIFIED)
One row only, taken from **this** export (never from an older export: it would undo later changes), with only the approved columns changed. Example (tested): rounding rule `NEAREST`, rounding level `LINE` (codes of lookups `ZX_ROUNDING_RULE` / `ZX_ROUNDING_LEVEL`; GUESS for the lookup names, the codes are VERIFIED).
```bash
cd "<RUN>"; python -I "<S>/own_row_package.py" --export-dir exp1/unz --file ZX_LEGAL_ENTITY_TAX_PROFILE.csv --match LegalEntityIdentifier=<LE> --prefix <PREFIX> --set RoundingRuleCode=NEAREST --set RoundingLevelCode=LINE --out-dir pay --zip-name letp.zip
```
The helper refuses a match value without your prefix and any match that is not exactly 1 row. (Real use on a named legal entity without a prefix: build the one row the same way by hand; GUESS.)

## Step 5. Import (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES --task-name "Manage Legal Entity Tax Profiles" --zip-file "<RUN>/pay/letp.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
```
Write down the ProcessId. Result in `<RUN>/imp/*_process_log.txt`: success = `A total of 1 rows were processed. 0 rows of them failed`, `Legal Entity Tax Profile. Status: Completed successfully` (FSCR's own log may end `StatusCode: (unknown)`: normal). Never import the whole export. Dropped connection after the process started: do not import again; wait 2 minutes and read back.

**Read the log safely:** the process log and the file names in `<RUN>/imp` hold the environment name and the submitting user; never print the whole log, never list that folder into a report. Print only the result lines:
```bash
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```


## Step 6. Read back (VERIFIED)
Export again: run Step 1 again with `exp2` in place of `exp1` (both the export line and the unzip line; if that export had to be run again into a new folder, use that folder instead of `exp2` below), then:
```bash
python -I "<S>/compare_own_update.py" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --file ZX_LEGAL_ENTITY_TAX_PROFILE.csv --key LegalEntityIdentifier,PartyTypeCode --own <LE> --expect RoundingRuleCode=NEAREST --expect RoundingLevelCode=LINE
```
The compare prints `RESULT: PASS` or `RESULT: FAIL` itself. PASS = same row count, other rows changed 0, your row shows the new values. No REST resource was used (the export is the proof).

## Rules and limits
1. One row, approved columns only; never another legal entity's profile in a test.
2. The CSV route cannot delete a profile.
3. Tested on one environment (release 11.13.26.10.0), US legal entity.

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Prerequisite | own legal entity `GAPFILL_AB_B14_LE1` (test-legal-entity skill) |
| Change | `RoundingRuleCode` '' → `NEAREST`, `RoundingLevelCode` '' → `LINE`; ProcessId 100004743430357, 1 processed, 0 failed |
| Compare | 68 → 68 rows, other rows changed 0, own row changed only the 2 columns: PASS |
