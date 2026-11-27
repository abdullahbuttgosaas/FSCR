---
skill_id: "gosaas.gap-fills.sourcing.manage-qualification-areas"
name: "Manage Qualification Areas (GoSaaS gap fill)"
description: "Create a new DRAFT supplier qualification area with one outcome, owned by a procurement business unit you name, through FSCR's setup-task CSV export and import, read back by REST supplierQualificationAreas and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing batch 02, 2026-11-27. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_AREAS"
task_name: "Manage Qualification Areas"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only exports and REST reads; one CSV import that creates one new qualification area in DRAFT status with one outcome. There is no delete by CSV: plan as if it stays."
---

# Manage Qualification Areas (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-27) · **GUESS** = judgment, not tested.

## What it is and when to use
A qualification area groups the questions used to qualify suppliers for one topic (for example environmental compliance) and lists the possible outcomes. Each area belongs to a procurement business unit (`ShortCode_QualArea` = that unit's name). VERIFIED. This skill creates a NEW area in **DRAFT** status (not usable in qualifications until someone activates it) with one outcome and no questions, on a procurement business unit you choose. Use your own test procurement business unit when you can, so nobody else's unit gets a new area. REST `supplierQualificationAreas` reads areas (VERIFIED); the CSV creates them.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties filled in). Read only.
GAPS   = the gaps-filled folder that holds sourcing\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project".
         Check: `git -C "<RUN>" rev-parse --show-toplevel 2>/dev/null || echo "RUN not in git: OK"` must print the OK line.
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
AREA   = new area name: PREFIX + short name, e.g. GAPFILL_AB_QA1 (also used as SectionName)
BU     = the owning procurement business unit's name (a unit with the Procurement business function; best your own test unit)
OUTCOME= the outcome name, e.g. a meaning of the lookup type ORA_POQ_QUALIFICATION_OUTCOME (no "|")
```
Every `<FSCR>`, `<GAPS>`, `<RUN>`, `<...>` in the commands below is a placeholder: put the real value in its place before you run the command.

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. In Git Bash write paths as `E:/...` (never `/e/...`, and never pass `$PWD`: FSCR's REST client then fails with `No module named 'rest_client_common'`). VERIFIED
- Shell variables do **not** survive from one tool call to the next: set them again in every call.
- **Never read the import log with cat, sed or grep** (it holds the environment name and the submitting user). Read it only with `python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"`: it prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. VERIFIED
- **Never print the export CSVs whole** (`CreatedBy` / `LastUpdatedBy` hold user names) and never print the metadata XML. Print only the columns shown below. Existing records may carry people's names: do not copy them into reports.
- FSCR's export and import file names start with the environment name; do not copy them into reports.
- Save each export's output to a file and print only whether a ZIP was written. If no ZIP was written, run the export again into a new folder (read-only; up to 3 times) and use **that** folder in every later command.
- Save the import's screen output to `<RUN>/import.out`; the ProcessId is on the line `Started setup task CSV import process: <n>`. `grep -o` on `import.out` is safe; never print `import.out` whole. Do not wrap the import in a shell `timeout`.
- No ProcessId line after an error: **do not import again.** Repeat the Step 4 read-back every minute for 10 minutes; if the record shows up, go on; if not, nothing was created (prove it with the after-export); a second import needs the person's approval again.
- Connection dropped **after** the ProcessId line: the import still runs; **never import again**. Fetch its log with `cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_AREAS --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/import_result/recovered_process_log.txt"`, then read it with `read_import_log.py`.

## Sign-in
- If a call says HTTP 401/403, or hangs with no output (an expired token waits for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). An unattended run stops here and reports instead.
- Never print tokens, the server address or user names.

## Prerequisites
1. A procurement business unit BU (a business unit with the Procurement business function and its procurement configuration). On a shared environment use your own test unit: make one with the Common Features skill `test-business-unit`, then the Procurement skills `configure-procurement-business-function` (function 110 + configuration). Step 2 checks BU exists. VERIFIED (our test used such an own unit)
2. Optional: a qualification outcome code of your own (skill `manage-qualification-outcome-lookup`) to use as OUTCOME. The outcome name was accepted as text; whether it must match a lookup meaning is GUESS.

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_AREAS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "
import csv,sys,glob,os
for f in sorted(glob.glob(sys.argv[1]+'/*.csv')): print(os.path.basename(f), sum(1 for _ in csv.DictReader(open(f,encoding='utf-8-sig'))), 'rows')
" "<RUN>/export_before/unz"
```
Expect 5 files (VERIFIED): the metadata XML, `ORA_POQ_QUAL_AREAS.csv`, `ORA_POQ_QUAL_AREA_OUTCOMES.csv`, `ORA_POQ_QUAL_AREA_QUESTIONS.csv`, `ORA_POQ_QUAL_AREA_BU_ACCESSES.csv`. Ours held 19 areas, 48 outcomes, 17 question links, 1 access row. Check AREA is not there yet:
```bash
python -I -c "
import csv,sys
n=[r['QualAreaName'] for r in csv.DictReader(open(sys.argv[1]+'/ORA_POQ_QUAL_AREAS.csv',encoding='utf-8-sig'))]
print(len(n),'areas;', 'AREA is new' if sys.argv[2] not in n else 'STOP: AREA exists')
" "<RUN>/export_before/unz" <AREA>
```

## Step 2. Check BU and AREA live, then build the package
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
python -B "$H" "<FSCR>" "$API/finBusinessUnitsLOV?q=BusinessUnitName='<BU>'&onlyData=true" --no-open-browser --output "<RUN>/bu.json" > "<RUN>/bu.out" 2>&1; echo "rc=$?"
python -B "$H" "<FSCR>" "$API/supplierQualificationAreas?q=QualArea='<AREA>'&onlyData=true" --no-open-browser --output "<RUN>/area_before.json" > "<RUN>/area_before.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys
b=json.load(open(sys.argv[1]))['count']; a=json.load(open(sys.argv[2]))['count']
print('BU found' if b==1 else 'STOP: BU not found', '| AREA is new' if a==0 else '| STOP: AREA exists'); sys.exit(0 if (b==1 and a==0) else 1)
" "<RUN>/bu.json" "<RUN>/area_before.json" && \
python -I "<GAPS>/sourcing/scripts/build_csv_package.py" --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_POQ_QUAL_AREAS.csv=QualAreaName \
  --row "ORA_POQ_QUAL_AREAS.csv|QualAreaName=<AREA>|RevisionNumber_QualArea=0|ShortCode_QualArea=<BU>|QualAreaDescription=<text>|GlobalFlag=N|QualAreaStatus=DRAFT|InformationOnlyFlag=N|QualAreaLevel=SUPPLIER|LatestRevisionFlag=Y|ExpirationReminderPeriod=10|ExpirationReminderType=DAYS|HasAttachments=N|EnableScoringFlag=N|AutoAcceptResponsesFlag=N|AutoEvaluateQualFlag=N|QualificationDurationType=MONTHS|AutoPopulateResponsesFlag=Y|ShowQualInterRespFlag=N|ShowQualToSupplierFlag=N|RequalifyExpirationFlag=N|QualAreaSurveyFlag=N|SectionName=<AREA>|QualAreaUsageCode=ORA_QUALIFICATION" \
  --row "ORA_POQ_QUAL_AREA_OUTCOMES.csv|ORA_POQ_QUAL_AREAS.QualAreaName=<AREA>|ORA_POQ_QUAL_AREAS.RevisionNumber_QualArea=0|ORA_POQ_QUAL_AREAS.ShortCode_QualArea=<BU>|DisplaySequence=10|OutcomeName=<OUTCOME>|ActiveFlag=Y|KnockoutOutcomeFlag=N|NotificationFlag=N"
```
- The REST reads and the build run in one call: the build happens only if BU is found and AREA is new. VERIFIED
- Leave `ActivationDate`, owner, e-mail and audit columns empty: a DRAFT area needs no activation date or owner. VERIFIED (accepted)
- Expect `ORA_POQ_QUAL_AREAS.csv: 1 row(s)`, `ORA_POQ_QUAL_AREA_OUTCOMES.csv: 1 row(s)`, the other 2 files 0 rows. VERIFIED
- The child rows name their parent by 3 columns (area name, revision 0, BU): keep them equal to the area row. VERIFIED

## Step 3. Import
Approval: the person must approve the environment, the task and the new record's name before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_AREAS --task-name "Manage Qualification Areas" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"
```
Keep the ProcessId. Success (VERIFIED): `Business object: Supplier Qualification Area. Status: Completed successfully`, `A total of 1 rows were processed. 0 rows of them failed` (the log counts only the area; the outcome shows in the export), `IMPORT: PASS`.

## Step 4. Read back (REST and a second export)
Run this step also when the import failed.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
python -B "$H" "<FSCR>" "$API/supplierQualificationAreas?q=QualArea='<AREA>'&onlyData=true" --no-open-browser --output "<RUN>/area_after.json" > "<RUN>/area_after.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys; d=json.load(open(sys.argv[1])); i=d['items']
[print({k:x[k] for k in ('QualArea','QualAreaStatusCode','ProcurementBU','Revision','QualAreaLevelCode')}) for x in i]
ok=len(i)==1 and i[0]['QualAreaStatusCode']=='DRAFT' and i[0]['ProcurementBU']==sys.argv[2] and i[0]['Revision']==0
print('READBACK:','PASS' if ok else 'FAIL')
" "<RUN>/area_after.json" "<BU>"
```
`READBACK: PASS` = one area AREA, DRAFT, revision 0, owned by BU. VERIFIED
Second check, a new read-only export and the compare:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_AREAS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_after" > "<RUN>/export_after.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_after"
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_POQ_QUAL_AREAS.csv=QualAreaName --key ORA_POQ_QUAL_AREA_OUTCOMES.csv=ORA_POQ_QUAL_AREAS.QualAreaName \
  --key ORA_POQ_QUAL_AREA_QUESTIONS.csv=ORA_POQ_QUAL_AREAS.QualAreaName --key ORA_POQ_QUAL_AREA_BU_ACCESSES.csv=ORA_POQ_QUAL_AREAS.QualAreaName \
  --expect ORA_POQ_QUAL_AREAS.csv=<AREA> --expect ORA_POQ_QUAL_AREA_OUTCOMES.csv=<AREA>
```
`RESULT: PASS` = AREA added to the areas and the outcomes file, nothing removed or changed. VERIFIED

## Rules and limits
1. New areas only; never send an existing area name (it would update it). Keep the area DRAFT: an ACTIVE area needs questions and an activation date (GUESS) and shows to qualification managers.
2. Questions are not added here (they come from the task Manage Questions; a question link row needs an existing question: GUESS).
3. Test areas stay (no delete by CSV); record them.
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-27). Do not reuse these names.
Counts are from our run; later runs see more rows (every test adds records). That is expected.
| Step | Result |
|---|---|
| Export before | 5 files; 19 areas, 48 outcomes |
| BU | own test unit `GAPFILL_AB_B15_BU1` (Procurement function), found by REST |
| Import | `GAPFILL_AB_S2_QA1`, DRAFT, outcome "GAPFILL AB Qualification Outcome 1": ProcessId 100004744440374, 1 row, 0 failed |
| REST | 1 area, DRAFT, revision 0, BU ok: PASS |
| Export after | 20 areas, 49 outcomes; added only the new area and its outcome: PASS |
