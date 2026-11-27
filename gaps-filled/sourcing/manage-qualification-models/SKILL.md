---
skill_id: "gosaas.gap-fills.sourcing.manage-qualification-models"
name: "Manage Qualification Models (GoSaaS gap fill)"
description: "Create a new DRAFT supplier qualification model with one qualification area and one outcome, owned by a procurement business unit you name, through FSCR's setup-task CSV export and import, read back by REST supplierQualificationModels and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing batch 03, 2026-11-28. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_MODELS"
task_name: "Manage Qualification Models"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gaps-filled sourcing/manage-qualification-areas (the area the model uses)"
side_effects:
  - "Read-only exports and REST reads; one CSV import that creates one new qualification model in DRAFT status with one area and one outcome. There is no delete by CSV: plan as if it stays."
---

# Manage Qualification Models (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-28) · **GUESS** = judgment, not tested.

## What it is and when to use
A qualification model lists the qualification areas (and their outcomes) used to assess a supplier. Each model belongs to a procurement business unit (`ShortCode_QualModel` = that unit's name). VERIFIED. This skill creates a NEW model in **DRAFT** status (not usable until someone activates it) with ONE qualification area and ONE outcome, on a procurement business unit you choose. Use your own test unit and your own test area, so nobody else's records are touched.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties filled in). Read only.
GAPS   = the gaps-filled folder that holds sourcing\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); no folder in its path named exactly "project".
         Create it first: mkdir -p "<RUN>". Check: git -C "<RUN>" rev-parse --show-toplevel 2>/dev/null || echo "RUN not in git: OK"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
MODEL  = new model name: PREFIX + short name, e.g. GAPFILL_AB_QM1
BU     = the owning procurement business unit's name (a unit with the Procurement business function; best your own test unit)
AREA   = an existing qualification area owned by BU, revision 0 (DRAFT is accepted). Best your own test area.
OUTCOME= the model outcome name (free text, no "|"), e.g. GAPFILL AB Model Outcome 1
```
Every `<FSCR>`, `<GAPS>`, `<RUN>`, `<...>` below is a placeholder: put the real value in its place before you run the command.

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. In Git Bash write paths as `E:/...` (never `/e/...`, never `$PWD`). Shell variables do **not** survive from one tool call to the next. VERIFIED
- **Never read the import log with cat, sed or grep** (it holds the environment name and the submitting user). Read it only with `python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"` (prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`). VERIFIED
- **Never print export CSVs whole** (`CreatedBy` / `LastUpdatedBy` hold user names) and never print the metadata XML. FSCR's export and import file names start with the environment name: do not copy them into reports.
- Save each export's output to a file and print only whether a ZIP was written. No ZIP: run the export again into a NEW folder (read only; up to 3 times) and use that folder in every later command.
- The ProcessId is on the line `Started setup task CSV import process: <n>` of `<RUN>/import.out` (`grep -o` is safe; never print `import.out` whole). Do not wrap the import in `timeout`.
- No ProcessId line after an error: **do not import again.** Repeat the Step 4 REST read every minute for 10 minutes; nothing found = nothing created (prove it with the after-export); a second import needs the person's approval again.
- Connection dropped **after** the ProcessId line: the import still runs; **never import again**. Wait 2 minutes and go to Step 4.

## Sign-in
If a call says HTTP 401/403, or hangs with no output (an expired token waits for a browser sign-in), stop it and sign in: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). An unattended run stops here and reports instead. Never print tokens, the server address or user names.

## Prerequisites
1. A procurement business unit BU. On a shared environment use your own test unit: Common Features skill `test-business-unit`, then Procurement skill `configure-procurement-business-function` (function 110 + configuration). Step 2 checks it. VERIFIED (our test used such a unit)
2. A qualification area AREA owned by BU (skill `sourcing/manage-qualification-areas`; a DRAFT area with revision 0 was accepted). Step 2 checks it. VERIFIED

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_MODELS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "
import csv,sys,glob,os
for f in sorted(glob.glob(sys.argv[1]+'/*.csv')): print(os.path.basename(f), sum(1 for _ in csv.DictReader(open(f,encoding='utf-8-sig'))), 'rows')
n=[r['QualModelName'] for r in csv.DictReader(open(sys.argv[1]+'/ORA_POQ_QUAL_MODELS.csv',encoding='utf-8-sig'))]
print('MODEL is new' if sys.argv[2] not in n else 'STOP: MODEL exists')
" "<RUN>/export_before/unz" "<MODEL>"
```
Expect 4 CSV files (VERIFIED): `ORA_POQ_QUAL_MODELS.csv`, `ORA_POQ_QUAL_MODEL_AREAS.csv`, `ORA_POQ_QUAL_MODEL_OUTCOMES.csv`, `ORA_POQ_QUAL_MODEL_BU_ACCESSES.csv`, plus the metadata XML. Our first export had 0 rows in every file even though REST showed one ACTIVE model of another unit, so the export does not list every model (why is GUESS); later exports listed the earlier test models. Whatever the counts, the rows below are written in full and only MODEL may be new.

## Step 2. Check BU, AREA and MODEL live, then build the package
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
python -B "$H" "<FSCR>" "$API/finBusinessUnitsLOV" --query "q=BusinessUnitName='<BU>'" --query onlyData=true --no-open-browser --output "<RUN>/bu.json" > "<RUN>/bu.out" 2>&1; echo "rc=$?"
python -B "$H" "<FSCR>" "$API/supplierQualificationAreas" --query "q=QualArea='<AREA>'" --query onlyData=true --no-open-browser --output "<RUN>/area.json" > "<RUN>/area.out" 2>&1; echo "rc=$?"
python -B "$H" "<FSCR>" "$API/supplierQualificationModels" --query "q=QualModel='<MODEL>'" --query onlyData=true --no-open-browser --output "<RUN>/model_before.json" > "<RUN>/model_before.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys
b=json.load(open(sys.argv[1]))['count']; a=json.load(open(sys.argv[2]))['items']; m=json.load(open(sys.argv[3]))['count']
ok_a=[x for x in a if x['ProcurementBU']==sys.argv[4] and x['Revision']==0]
print('BU found' if b==1 else 'STOP: BU not found', '| AREA found on BU' if ok_a else '| STOP: AREA not found on BU (revision 0)', '| MODEL is new' if m==0 else '| STOP: MODEL exists')
sys.exit(0 if (b==1 and ok_a and m==0) else 1)
" "<RUN>/bu.json" "<RUN>/area.json" "<RUN>/model_before.json" "<BU>" && \
python -I "<GAPS>/sourcing/scripts/build_csv_package.py" --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_POQ_QUAL_MODELS.csv=QualModelName \
  --row "ORA_POQ_QUAL_MODELS.csv|QualModelName=<MODEL>|RevisionNumber=0|ShortCode_QualModel=<BU>|QualModelDescription=GoSaaS gap fill test model|GlobalFlag=N|QualModelStatus=DRAFT|QualModelLevel=SUPPLIER|LatestRevisionFlag=Y|ExpirationReminderPeriod=10|ExpirationReminderType=DAYS|HasAttachments=N|EnableScoringFlag=N|AutoEvalAssessmentFlag=N|ShowAssessmentQualFlag=N|ShowAssessmtToSuppFlag=N|DefaultAssessmtOwnerFlag=N|SourcingEligibleFlag=N|SourcingShareEligFlag=N|ReassessQualificationFlag=N" \
  --row "ORA_POQ_QUAL_MODEL_AREAS.csv|ORA_POQ_QUAL_MODELS.QualModelName=<MODEL>|ORA_POQ_QUAL_MODELS.RevisionNumber=0|ORA_POQ_QUAL_MODELS.ShortCode_QualModel=<BU>|DisplaySequence=10|QualAreaName=<AREA>|RevisionNumber_QualModelArea=0|ShortCode=<BU>" \
  --row "ORA_POQ_QUAL_MODEL_OUTCOMES.csv|ORA_POQ_QUAL_MODELS.QualModelName=<MODEL>|ORA_POQ_QUAL_MODELS.RevisionNumber=0|ORA_POQ_QUAL_MODELS.ShortCode_QualModel=<BU>|DisplaySequence=10|OutcomeName=<OUTCOME>|KnockoutOutcomeFlag=N|NotificationFlag=N"
```
- The REST reads and the build run in one call: the build happens only if BU and AREA are found and MODEL is new. VERIFIED
- Expect `ORA_POQ_QUAL_MODELS.csv: 1 row(s)`, `..._AREAS.csv: 1 row(s)`, `..._OUTCOMES.csv: 1 row(s)`, `..._BU_ACCESSES.csv: 0 row(s)`. VERIFIED
- The child rows name their parent by 3 columns (model name, revision 0, BU): keep them equal to the model row. Leave `ActivationDate`, owners, e-mail and audit columns empty. VERIFIED (accepted)
- The column is `ReassessQualificationFlag` (not `ReassessQualification`); the builder stops on a wrong column name. VERIFIED

## Step 3. Import
Approval: the person must approve the environment, the task and the new record's name before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
mkdir -p "<RUN>/import_result"; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_MODELS --task-name "Manage Qualification Models" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"
```
Keep the ProcessId. Success (VERIFIED): `Business object: Supplier Qualification Model. Status: Completed successfully`, `A total of 1 rows were processed. 0 rows of them failed` (the log counts only the model; area and outcome show in Step 4), `IMPORT: PASS`.

## Step 4. Read back (REST and a second export)
Run this step also when the import failed.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
python -B "$H" "<FSCR>" "$API/supplierQualificationModels" --query "q=QualModel='<MODEL>'" --query "expand=outcomes,areas" --query onlyData=true --no-open-browser --output "<RUN>/model_after.json" > "<RUN>/model_after.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys; i=json.load(open(sys.argv[1],encoding='utf-8'))['items']
[print(x['QualModel'],x['StatusCode'],x['ProcurementBU'],x['Revision'],[a['QualAreaName'] for a in x['areas']],[o['OutcomeName'] for o in x['outcomes']]) for x in i]
ok=len(i)==1 and i[0]['StatusCode']=='DRAFT' and i[0]['ProcurementBU']==sys.argv[2] and [a['QualAreaName'] for a in i[0]['areas']]==[sys.argv[3]] and len(i[0]['outcomes'])==1
print('READBACK:','PASS' if ok else 'FAIL')
" "<RUN>/model_after.json" "<BU>" "<AREA>"
```
`READBACK: PASS` = one model MODEL, DRAFT, owned by BU, with AREA and one outcome. VERIFIED
Second check, a new read-only export and the compare:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_MODELS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_after" > "<RUN>/export_after.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_after"
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_POQ_QUAL_MODELS.csv=QualModelName --key ORA_POQ_QUAL_MODEL_AREAS.csv=ORA_POQ_QUAL_MODELS.QualModelName \
  --key ORA_POQ_QUAL_MODEL_OUTCOMES.csv=ORA_POQ_QUAL_MODELS.QualModelName --key ORA_POQ_QUAL_MODEL_BU_ACCESSES.csv=ORA_POQ_QUAL_MODELS.QualModelName \
  --expect ORA_POQ_QUAL_MODELS.csv=<MODEL> --expect ORA_POQ_QUAL_MODEL_AREAS.csv=<MODEL> --expect ORA_POQ_QUAL_MODEL_OUTCOMES.csv=<MODEL>
```
`RESULT: PASS` = MODEL added to the models, areas and outcomes files, nothing removed or changed. VERIFIED. (Other test models created between your two exports also show as "added"; that is not a failure as long as nothing is removed or changed and yours is there.)

## Rules and limits
1. New models only; never send an existing model name (it would update it). Keep the model DRAFT: activating needs an ACTIVE area and an owner (GUESS) and shows the model to qualification managers.
2. One area and one outcome is the tested shape; more areas, weights and scores: GUESS.
3. Test models stay (no delete by CSV); record them.
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-28). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 4 CSVs, 0 rows each (first run; later runs see earlier test models) |
| BU / AREA | own test unit `GAPFILL_AB_B15_BU1`, own DRAFT area `GAPFILL_AB_S2_QA1` (revision 0) |
| Import | `GAPFILL_AB_S3_QM1`, DRAFT, outcome "GAPFILL AB Model Outcome 1": ProcessId 100004744440460, 1 row, 0 failed |
| REST | 1 model, DRAFT, BU ok, area ok, 1 outcome: PASS |
| Export after | models 0 -> 1, areas 0 -> 1, outcomes 0 -> 1; nothing removed or changed: PASS |
