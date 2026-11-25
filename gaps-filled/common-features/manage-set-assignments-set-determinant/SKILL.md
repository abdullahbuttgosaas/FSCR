---
skill_id: "gosaas.gap-fills.common-features.manage-set-assignments-set-determinant"
name: "Manage Set Assignments for Set Determinant Type: assign a reference data set to a reference group for a SET determinant by FSM CSV (GoSaaS gap fill)"
description: "Adds one reference data set assignment whose determinant type is SET (FND_APP_REFERENCE_DATA_SET_ASSIGNMENT: determinant set + reference group → set) by FSM CSV import, with an export compare as proof. Tested with a reference data set made for the test as the determinant. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 15, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_REFERENCE_DATA_SET_ASSIGNMENTS"
task_name: "Manage Set Assignments for Set Determinant Type"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "FND_MANAGE_REFERENCE_DATA_SETS (the determinant set; Step 2 makes a test one)"
side_effects:
  - "Step 2 (test) creates a reference data set. Step 4 adds an assignment: data of that reference group is shared for the determinant set from the assigned set."
---

# Manage Set Assignments for Set Determinant Type (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
Reference data sharing decides, per **determinant** and **reference group** (for example `PJF_RATES`), which **reference data set** supplies the data. Determinant types (lookup `DETERMINANT_TYPE`, VERIFIED): `BU` business unit, `CST` cost organization, `PU` project unit, `AB` asset book, `SET` reference data set. **This task's package only handles determinant type `SET`** (VERIFIED: its object is `SetIdAssignmentsSetVO`, and `DeterminantValueSetCode` must be a **set code**; with `BU` and a business unit name or organization code Oracle answers `JBO-27014: Attribute DeterminantValue in SetIdAssignmentsEO is required`). Business-unit set assignments are part of the business unit package instead (GUESS: the Manage Business Unit export holds a set-assignment file).
Use it to assign a set to a reference group for a set determinant. **For a test**, use your own new set as the determinant.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo
DSET  = the determinant set code (for a test: your own new set, PREFIX + short name)
GROUP = reference group name, e.g. PJF_RATES (VERIFIED)
TSET  = the set to assign, e.g. COMMON (VERIFIED; seeded in every environment)
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Export command (used in Steps 1, 2, 5; TASK and folder change):
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code <TASK> --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/<dir>" > "<RUN>/<dir>.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/<dir>"
```
No ZIP: run again into a NEW folder, up to 3 tries. Import command (TASK, name, zip, folder change), then read only the result lines (the log holds the environment name and user):
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code <TASK> --task-name "<TASK NAME>" --zip-file "<RUN>/<zip>" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/<imp>" > "<RUN>/<imp>.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/<imp>.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/<imp>/*_process_log.txt | sort -u
```
**If the ProcessId printed but the status poll fails** (network error, no process log): never import again. Fetch the result by ProcessId (VERIFIED):
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code <TASK> --process-id <ProcessId> --token-cache auto --no-open-browser --output "<RUN>/<imp>_result.json" > "<RUN>/<imp>_result.log" 2>&1
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+" "<RUN>/<imp>_result.log" "<RUN>/<imp>_result.json" | sort -u
```

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names.

## Prerequisites
1. The determinant set DSET exists (Step 2 makes a test one; check first).
2. TSET exists (`COMMON` always does) and GROUP is a valid reference group name (VERIFIED for `PJF_RATES`).

## Step 1. Read-only export of this task (VERIFIED)
Export command with TASK = `FND_MANAGE_REFERENCE_DATA_SET_ASSIGNMENTS`, dir `exp1`. 1 CSV `FND_APP_REFERENCE_DATA_SET_ASSIGNMENT.csv` (columns `DeterminantType`, `DeterminantValueSetCode`, `ReferenceGroupName`, `SetCode`; it may be header only or already hold earlier assignments; the builder sends only your new row) + metadata. Success = a ZIP in `exp1`. The CSV who columns (`CreatedBy`, `LastUpdatedBy`) hold user names: never copy them.

## Step 2. The determinant set (test: create it; VERIFIED)
Export command with TASK = `FND_MANAGE_REFERENCE_DATA_SETS`, dir `sets1` (1 CSV `FND_APP_REFERENCE_DATA_SET.csv`: `SetCode`, `SetName`, `Description`). `grep -c "\"<DSET>\"" "<RUN>/sets1/unz/FND_APP_REFERENCE_DATA_SET.csv"` → 0 means create it; 1 means reuse it and go on to Step 3 (Step 1 is still needed).
```bash
cd "<RUN>"; python -I "<B>" --export-dir sets1/unz --out-dir setpay --zip-name set.zip --prefix <PREFIX> --key "FND_APP_REFERENCE_DATA_SET.csv=SetCode" --prefix-col "FND_APP_REFERENCE_DATA_SET.csv=SetCode" --row "FND_APP_REFERENCE_DATA_SET.csv|SetCode=<DSET>|SetName=<DSET>|Description=Test set, not used"
```
Import command with TASK = `FND_MANAGE_REFERENCE_DATA_SETS`, name "Manage Reference Data Sets", zip `setpay/set.zip`, folder `setimp`. Success: `A total of 1 rows were processed. 0 rows of them failed`, `Application Reference Data Set. Status: Completed successfully`.

## Step 3. Build the assignment (offline, VERIFIED)
```bash
cd "<RUN>"; python -I "<B>" --export-dir exp1/unz --out-dir pay --zip-name rdsa.zip --prefix <PREFIX> --key "FND_APP_REFERENCE_DATA_SET_ASSIGNMENT.csv=DeterminantType,DeterminantValueSetCode,ReferenceGroupName" --prefix-col "FND_APP_REFERENCE_DATA_SET_ASSIGNMENT.csv=DeterminantValueSetCode" --row "FND_APP_REFERENCE_DATA_SET_ASSIGNMENT.csv|DeterminantType=SET|DeterminantValueSetCode=<DSET>|ReferenceGroupName=<GROUP>|SetCode=<TSET>"
```
Success: the builder prints `1 new rows` for the file and `wrote pay/rdsa.zip` (the same check applies to the Step 2 build).

## Step 4. Import (VERIFIED)
Import command with TASK = `FND_MANAGE_REFERENCE_DATA_SET_ASSIGNMENTS`, name "Manage Set Assignments for Set Determinant Type", zip `pay/rdsa.zip`, folder `imp`. Success: `A total of 1 rows were processed. 0 rows of them failed`, `Application Reference Data Set Assignment. Status: Completed successfully`. Write down the ProcessId.

## Step 5. Read back (VERIFIED)
Export command with this task, dir `exp2`, then:
```bash
python -I "<CMP>" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --key "FND_APP_REFERENCE_DATA_SET_ASSIGNMENT.csv=DeterminantType,DeterminantValueSetCode,ReferenceGroupName" --expect "FND_APP_REFERENCE_DATA_SET_ASSIGNMENT.csv=SET,<DSET>,<GROUP>"
```
`RESULT: PASS` = only your assignment added.

## Rules and limits
1. New assignments only; a test uses only your own determinant set. Never re-import an existing assignment row (that changes which data a real determinant sees).
2. Tested on one environment (release 11.13.26.10.0) with `PJF_RATES` → `COMMON`.

## Worked example (2026-11-26, codes and ProcessIds only)
| Try | Result |
|---|---|
| 1 | `BU`, determinant = business unit name: ProcessId 100004743432285, `JBO-27014 DeterminantValue ... is required`, nothing created |
| 2 | `BU`, determinant = business unit organization code: ProcessId 100004743434516, same error |
| set | own set `GAPFILL_AB_B15_SET1`: ProcessId 100004743432297, created |
| 3 | `SET`, `GAPFILL_AB_B15_SET1`, `PJF_RATES` → `COMMON`: ProcessId 100004744413542; status poll dropped, result fetched by ProcessId: 1 processed, 0 failed; compare 0 → 1, PASS |
| fresh | own set `GAPFILL_AB_B15_SET2F` (100004744414204), assignment (100004744415045): 1 → 2, PASS |
| re-test | own set `GAPFILL_AB_B15_SET3R` (100004743432588), assignment (100004744415284): 2 → 3, PASS |
