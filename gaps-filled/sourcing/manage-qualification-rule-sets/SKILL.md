---
skill_id: "gosaas.gap-fills.sourcing.manage-qualification-rule-sets"
name: "Manage Supplier Qualification Rule Sets (GoSaaS gap fill)"
description: "Create a new INACTIVE supplier qualification (registration) rule set with one always-display area rule, assigned to a procurement business unit you name, through FSCR's setup-task CSV export and import, read back by a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing and Supplier Management batch 03, 2026-11-28. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_POQ_MANAGE_SUPPLIER_REG_RULE_SETS"
task_name: "Manage Supplier Qualification Rule Sets"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gaps-filled sourcing/manage-qualification-areas (the area the rule shows)"
side_effects:
  - "Read-only exports and REST reads; one CSV import that creates one new INACTIVE rule set with one rule, its translation row and one business unit assignment. There is no delete by CSV: plan as if it stays."
---

# Manage Supplier Qualification Rule Sets (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-28) · **GUESS** = judgment, not tested.

## What it is and when to use
A supplier qualification rule set decides which qualification areas (questionnaires) a supplier must answer during registration or profile change, per procurement business unit. This skill creates a NEW rule set in status **INACTIVE** (it is not used by any registration) with ONE rule ("always display" one qualification area at registration) and assigns it to a business unit you choose. Use your own test unit and test area so nobody else's registration flow changes. There is **no REST resource** for rule sets (3 names tried, HTTP 404, VERIFIED): the export compare is the read-back.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties filled in). Read only.
GAPS   = the gaps-filled folder that holds sourcing\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); no folder in its path named exactly "project".
         Create it first: mkdir -p "<RUN>". Check: git -C "<RUN>" rev-parse --show-toplevel 2>/dev/null || echo "RUN not in git: OK"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
RS     = new rule set name: PREFIX + short name, e.g. GAPFILL_AB_RS1
BU     = a procurement business unit's name (best your own test unit)
AREA   = an existing qualification area owned by BU (a DRAFT area was accepted). Best your own test area.
```
Every `<FSCR>`, `<GAPS>`, `<RUN>`, `<...>` below is a placeholder: put the real value in its place before you run the command.

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. In Git Bash write paths as `E:/...` (never `/e/...`, never `$PWD`). Shell variables do **not** survive from one tool call to the next. VERIFIED
- **Never read the import log with cat, sed or grep** (it holds the environment name and the submitting user). Read it only with `python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"`. VERIFIED
- **Never print export CSVs whole** (`CreatedBy`, `LastUpdatedBy`, owner and e-mail columns hold people's names) and never print the metadata XML. Existing rule sets may carry people's names in their own names: do not copy them into reports. FSCR's output file names start with the environment name: do not copy them.
- Save each export's output to a file and print only whether a ZIP was written. No ZIP: run the export again into a NEW folder (read only; up to 3 times) and use that folder in every later command.
- The ProcessId is on the line `Started setup task CSV import process: <n>` of `<RUN>/import.out` (`grep -o` is safe; never print `import.out` whole).
- No ProcessId line after an error: **do not import again**; prove with the after-export that nothing was created; a second import needs the person's approval again. Connection dropped **after** the ProcessId line: the import still runs; **never import again**; wait 2 minutes and go to Step 4.

## Sign-in
If a call says HTTP 401/403, or hangs with no output, stop it and sign in: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). An unattended run stops here and reports instead. Never print tokens, the server address or user names.

## Prerequisites
1. A procurement business unit BU (own test unit: Common Features `test-business-unit` + Procurement `configure-procurement-business-function`). VERIFIED (our test used such a unit)
2. A qualification area AREA owned by BU (skill `sourcing/manage-qualification-areas`). A DRAFT area was accepted for an INACTIVE rule set. VERIFIED
3. Valid rule set statuses come from the standard lookup `POQ_RULE_SET_STATUS` (REST `standardLookups`, not `commonLookups`): `ACTIVE`, `INACTIVE`. `DRAFT` is refused (`FND_CMN_INVALID_ATTRB_API_SERV: The value of the attribute Status isn't valid`). VERIFIED. Read it live (Step 2).

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_SUPPLIER_REG_RULE_SETS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "
import csv,sys,glob,os
for f in sorted(glob.glob(sys.argv[1]+'/*.csv')): print(os.path.basename(f), sum(1 for _ in csv.DictReader(open(f,encoding='utf-8-sig'))), 'rows')
n=[r['RuleSetName'] for r in csv.DictReader(open(sys.argv[1]+'/ORA_POQ_RULE_SETS.csv',encoding='utf-8-sig'))]
print('RS is new' if sys.argv[2] not in n else 'STOP: RS exists')
" "<RUN>/export_before/unz" "<RS>"
```
Expect 6 CSV files (VERIFIED): `ORA_POQ_RULE_SETS.csv`, `ORA_POQ_TRANS_RULE_SETS.csv`, `ORA_POQ_RULE_SET_BU_ASSIGNMENTS.csv`, `ORA_POQ_RULE_SET_BU_EVENT_RULES.csv`, `ORA_POQ_RULES.csv`, `ORA_POQ_RULE_AREA_QUESTIONS.csv`. Ours held 3 rule sets.

## Step 2. Check BU, AREA and the status lookup live, then build the package
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
python -B "$H" "<FSCR>" "$API/finBusinessUnitsLOV" --query "q=BusinessUnitName='<BU>'" --query onlyData=true --no-open-browser --output "<RUN>/bu.json" > "<RUN>/bu.out" 2>&1; echo "rc=$?"
python -B "$H" "<FSCR>" "$API/supplierQualificationAreas" --query "q=QualArea='<AREA>'" --query onlyData=true --no-open-browser --output "<RUN>/area.json" > "<RUN>/area.out" 2>&1; echo "rc=$?"
python -B "$H" "<FSCR>" "$API/standardLookups/POQ_RULE_SET_STATUS" --query expand=lookupCodes --query onlyData=true --no-open-browser --output "<RUN>/status.json" > "<RUN>/status.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys
b=json.load(open(sys.argv[1]))['count']; a=[x for x in json.load(open(sys.argv[2]))['items'] if x['ProcurementBU']==sys.argv[4]]
st=[c['LookupCode'] for c in json.load(open(sys.argv[3]))['lookupCodes']]
print('BU found' if b==1 else 'STOP: BU not found', '| AREA found on BU' if a else '| STOP: AREA not on BU', '| statuses', st)
sys.exit(0 if (b==1 and a and 'INACTIVE' in st) else 1)
" "<RUN>/bu.json" "<RUN>/area.json" "<RUN>/status.json" "<BU>" && \
python -I "<GAPS>/sourcing/scripts/build_csv_package.py" --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_POQ_RULE_SETS.csv=RuleSetName \
  --row "ORA_POQ_RULE_SETS.csv|RuleSetName=<RS>|RuleSetDescription=GoSaaS gap fill test rule set|RuleSetStatus=INACTIVE|UseQuestionBranchFlag=N|AutoCreateQualFlag=N" \
  --row "ORA_POQ_TRANS_RULE_SETS.csv|ORA_POQ_RULE_SETS.RuleSetName=<RS>|Language=US|SourceLang=US" \
  --row "ORA_POQ_RULE_SET_BU_ASSIGNMENTS.csv|ORA_POQ_RULE_SETS.RuleSetName=<RS>|ShortCode=<BU>" \
  --row "ORA_POQ_RULES.csv|ORA_POQ_RULE_SETS.RuleSetName=<RS>|RuleType=AREA|DisplaySequence=10|Event=REGISTRATION|ConditionType=ALWAYS_DISPLAY|EventRuleCode=BUS_REL_BOTH|RegSourceCode=EXTERNAL" \
  --row "ORA_POQ_RULE_AREA_QUESTIONS.csv|ORA_POQ_RULE_SETS.RuleSetName=<RS>|ORA_POQ_RULES.RuleType=AREA|ORA_POQ_RULES.DisplaySequence=10|ORA_POQ_RULES.Event=REGISTRATION|ShortCode=<BU>|QualAreaName=<AREA>|DisplaySequence_RuleAreasQuestion=10"
```
- The build happens only if BU and AREA are found and `INACTIVE` is a valid status. VERIFIED
- Expect 1 row in 5 files and 0 rows in `ORA_POQ_RULE_SET_BU_EVENT_RULES.csv` (that file names owners and responders, which are people: left out). VERIFIED (accepted)
- `Language=US` / `SourceLang=US` as in the existing rows. Leave `ActivationDate` and audit columns empty. VERIFIED

## Step 3. Import
Approval: the person must approve the environment, the task and the new record's name before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
mkdir -p "<RUN>/import_result"; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_SUPPLIER_REG_RULE_SETS --task-name "Manage Supplier Qualification Rule Sets" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"
```
Keep the ProcessId. Success (VERIFIED): `Business object: Supplier Qualification Rule Set. Status: Completed successfully`, `A total of 1 rows were processed. 0 rows of them failed` (the log counts only the rule set), `IMPORT: PASS`.

## Step 4. Read back (second export)
Run this step also when the import failed.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_SUPPLIER_REG_RULE_SETS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_after" > "<RUN>/export_after.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_after"
P=ORA_POQ_RULE_SETS.RuleSetName
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_POQ_RULE_SETS.csv=RuleSetName --key ORA_POQ_TRANS_RULE_SETS.csv=$P --key ORA_POQ_RULE_SET_BU_ASSIGNMENTS.csv=$P \
  --key ORA_POQ_RULE_SET_BU_EVENT_RULES.csv=$P --key "ORA_POQ_RULES.csv=$P+DisplaySequence" --key "ORA_POQ_RULE_AREA_QUESTIONS.csv=$P+ORA_POQ_RULES.DisplaySequence" \
  --expect ORA_POQ_RULE_SETS.csv=<RS> --expect ORA_POQ_TRANS_RULE_SETS.csv=<RS> --expect ORA_POQ_RULE_SET_BU_ASSIGNMENTS.csv=<RS> \
  --expect "ORA_POQ_RULES.csv=<RS>+10" --expect "ORA_POQ_RULE_AREA_QUESTIONS.csv=<RS>+10"
python -I -c "import csv,sys; print([(r['RuleSetName'],r['RuleSetStatus'],r['ActivationDate']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_POQ_RULE_SETS.csv',encoding='utf-8-sig')) if r['RuleSetName']==sys.argv[2]])" "<RUN>/export_after/unz" "<RS>"
```
`RESULT: PASS` = RS added to the 5 files, nothing removed or changed (other people's new rule sets between your two exports would also show as added). The last line must show `('<RS>', 'INACTIVE', '')`. VERIFIED

## Rules and limits
1. New rule sets only; never send an existing rule set name (it would update it). Keep it INACTIVE: an ACTIVE rule set on a business unit changes the supplier registration questionnaire for that unit.
2. Only one rule (always display one area at registration) was tested; response-dependent rules (`ConditionType RESPONSE_DEPENDENT`, `SupplierAttributeCode`, `ConditionValue`) and event rules: GUESS.
3. Test rule sets stay (no delete by CSV); record them.
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-28). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 6 CSVs; 3 rule sets, 6 rules |
| Try 1 | status `DRAFT`: refused, `FND_CMN_INVALID_ATTRB_API_SERV` (ProcessId 100004744441515); export proved nothing created |
| Try 2 | `GAPFILL_AB_S3_RS1`, INACTIVE, on own unit `GAPFILL_AB_B15_BU1`, rule shows own area `GAPFILL_AB_S2_QA1`: ProcessId 100004743464733, 1 row, 0 failed |
| Export after | rule sets 3 -> 4, translations 3 -> 4, BU assignments 3 -> 4, rules 6 -> 7, area rows 6 -> 7, event rules unchanged: PASS |
