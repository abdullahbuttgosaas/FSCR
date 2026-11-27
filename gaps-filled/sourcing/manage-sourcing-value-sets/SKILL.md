---
skill_id: "gosaas.gap-fills.sourcing.manage-sourcing-value-sets"
name: "Manage Sourcing Value Sets (GoSaaS gap fill)"
description: "Create a new independent value set with values in the Sourcing module through FSCR's setup-task CSV export and import, read back by REST and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing batch 02, 2026-11-27. Written and tested live on one test environment. NOT official FSCR."
task_code: "PON_MANAGE_SOURCING_VALUE_SETS"
task_name: "Manage Sourcing Value Sets"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only exports and REST reads; one CSV import that creates one new value set with two values. There is no delete by CSV: plan as if it stays."
---

# Manage Sourcing Value Sets (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-27) · **GUESS** = judgment, not tested.

## What it is and when to use
A value set is a list of allowed values for a flexfield segment (for example a Sourcing descriptive flexfield) or a parameter. The export of this task is scoped to the value sets of one module (metadata scope `moduleKey=PrcPonCommon`); a value set lands in this task only when its `ModuleId` is that module's id. VERIFIED. This skill creates a NEW **independent** character value set (`ValidationType=INDEP`, `VARCHAR2` / `TEXT`) with two values. Use it to add a value set; it never changes an existing value set or value.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties filled in). Read only.
GAPS   = the gaps-filled folder that holds sourcing\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project".
         Check: `git -C "<RUN>" rev-parse --show-toplevel 2>/dev/null || echo "RUN not in git: OK"` must print the OK line.
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
VS     = new value set code: PREFIX + short name (upper case, digits, _), e.g. GAPFILL_AB_VS1
V1, V2 = two new values, upper case (UppercaseOnlyFlag=Y), at most 20 characters, e.g. GAPFILL_A, GAPFILL_B (other value sets may use the same names; that is allowed)
<text> = a short description of your own (no "|"), e.g. GoSaaS gap fill test value set
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
- Connection dropped **after** the ProcessId line: the import still runs; **never import again**. Fetch its log with `cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code PON_MANAGE_SOURCING_VALUE_SETS --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/import_result/recovered_process_log.txt"`, then read it with `read_import_log.py`.

## Sign-in
- If a call says HTTP 401/403, or hangs with no output (an expired token waits for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). An unattended run stops here and reports instead.
- Never print tokens, the server address or user names.

## Prerequisites
None to create. The module id is read live in Step 2 from a seeded lookup type of the same module (`PON_LINE_ATTRIBUTE_GROUPS`). VERIFIED: its `ModuleId` is the module of this task's value sets.

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PON_MANAGE_SOURCING_VALUE_SETS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "
import csv,sys,glob,os
for f in sorted(glob.glob(sys.argv[1]+'/*.csv')): print(os.path.basename(f), sum(1 for _ in csv.DictReader(open(f,encoding='utf-8-sig'))), 'rows')
" "<RUN>/export_before/unz"
```
Expect 7 files (VERIFIED): the metadata XML, `FND_APP_FLEX_VALUE_SET.csv`, `ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv` and 4 files for table, view-object and related value sets. The CSVs can be empty (ours on our first run: 0 value sets, 0 values; later runs also see earlier test value sets); an empty export is fine, the files still give the layout. The builder in Step 2 sends only the rows you give it.

## Step 2. Module id, before-read and package
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
python -B "$H" "<FSCR>" "$API/standardLookups/PON_LINE_ATTRIBUTE_GROUPS?onlyData=true&fields=LookupType,ModuleId" --no-open-browser --output "<RUN>/module.json" > "<RUN>/module.out" 2>&1; echo "rc=$?"
MOD=$(python -I -c "import json,sys; m=json.load(open(sys.argv[1]))['ModuleId']; print(m) if len(m)==32 else sys.exit('STOP: no module id')" "<RUN>/module.json") && echo "module id read (32 characters)"
python -B "$H" "<FSCR>" "$API/valueSets?q=ValueSetCode='<VS>'&onlyData=true&fields=ValueSetCode" --no-open-browser --output "<RUN>/before.json" > "<RUN>/before.out" 2>&1; echo "rc=$?"
python -I -c "import json,sys; c=json.load(open(sys.argv[1]))['count']; print('VS is new' if c==0 else sys.exit('STOP: VS already exists'))" "<RUN>/before.json" && \
python -I "<GAPS>/sourcing/scripts/build_csv_package.py" --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key FND_APP_FLEX_VALUE_SET.csv=ValueSetCode --key ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=FND_APP_FLEX_VALUE_SET.ValueSetCode \
  --row "FND_APP_FLEX_VALUE_SET.csv|ValueSetCode=<VS>|ModuleId=$MOD|Description=<text>|ValidationType=INDEP|ValueDataType=VARCHAR2|ValueSubtype=TEXT|MaximumLength=20|UppercaseOnlyFlag=Y|ZeroFillFlag=N|SecurityEnabledFlag=N" \
  --row "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv|FND_APP_FLEX_VALUE_SET.ValueSetCode=<VS>|Value=<V1>|Description=<text>|EnabledFlag=Y|SummaryFlag=N|SortOrder=1" \
  --row "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv|FND_APP_FLEX_VALUE_SET.ValueSetCode=<VS>|Value=<V2>|Description=<text>|EnabledFlag=Y|SummaryFlag=N|SortOrder=2"
```
- Run the module read and the build **in the same Bash call** (`MOD` does not survive to the next call).
- `rc=0` = the read worked; to see an error safely: `sed -E 's#https?://[^ "]+#<URL>#g' "<RUN>/module.out" | tail -3`.
- An empty `ModuleId` fails the import (`ORA-01400: cannot insert NULL`, seen in the Common Features value set test): the command stops before that. VERIFIED
- Expect `FND_APP_FLEX_VALUE_SET.csv: 1 row(s)`, `ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv: 2 row(s)`, the 4 other files 0 rows. VERIFIED
- Use `ValidationType=INDEP` exactly (`INDEPENDENT` is refused: seen in an earlier FSCR run on this task). VERIFIED

## Step 3. Import
Approval: the person must approve the environment, the task and the new record's name before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code PON_MANAGE_SOURCING_VALUE_SETS --task-name "Manage Sourcing Value Sets" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"
```
Keep the ProcessId. Success (VERIFIED): `Business object: Application Flexfield Value Set. Status: Completed successfully`, `A total of 3 rows were processed. 0 rows of them failed`, `IMPORT: PASS`.

## Step 4. Read back (REST and a second export)
Run this step also when the import failed: it proves whether anything was created.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; API=/fscmRestApi/resources/11.13.18.05
python -B "$H" "<FSCR>" "$API/standardLookups/PON_LINE_ATTRIBUTE_GROUPS?onlyData=true&fields=LookupType,ModuleId" --no-open-browser --output "<RUN>/module.json" > /dev/null 2>&1
python -B "$H" "<FSCR>" "$API/valueSets/<VS>?onlyData=true" --no-open-browser --output "<RUN>/vs_after.json" > "<RUN>/a1.out" 2>&1; echo "rc=$?"
python -B "$H" "<FSCR>" "$API/valueSets/<VS>/child/values?onlyData=true&fields=Value,EnabledFlag,SortOrder" --no-open-browser --output "<RUN>/values_after.json" > "<RUN>/a2.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys
v=json.load(open(sys.argv[1])); vals=json.load(open(sys.argv[2]))['items']; mod=json.load(open(sys.argv[3]))['ModuleId']
got=sorted((x['Value'],x['EnabledFlag']) for x in vals); want=sorted([(sys.argv[4],'Y'),(sys.argv[5],'Y')])
print(v['ValueSetCode'],v['ValidationType'],v['ValueDataType'],v['MaximumLength'],'module ok' if v['ModuleId']==mod else 'module DIFFERENT',[x['Value'] for x in vals])
print('READBACK:','PASS' if v['ValidationType']=='INDEP' and v['ModuleId']==mod and got==want else 'FAIL')
" "<RUN>/vs_after.json" "<RUN>/values_after.json" "<RUN>/module.json" <V1> <V2>
```
The REST key of a value set is its **code** (`valueSets/<VS>`). `READBACK: PASS` = the value set is INDEP, in the task's module, with exactly your two values enabled. VERIFIED
Second check, a new read-only export and the compare:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PON_MANAGE_SOURCING_VALUE_SETS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_after" > "<RUN>/export_after.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_after"
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz"   --key FND_APP_FLEX_VALUE_SET.csv=ValueSetCode --key "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=FND_APP_FLEX_VALUE_SET.ValueSetCode+Value"   --expect FND_APP_FLEX_VALUE_SET.csv=<VS> --expect "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=<VS>+<V1>" --expect "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=<VS>+<V2>"
```
`RESULT: PASS` = nothing removed or changed, and VS and its two values (`<VS>+<V1>`, `<VS>+<V2>`) are among the added rows. Values are matched by value set **and** value: a value name is unique only inside its value set, and other test value sets may use the same value names (a key on `Value` alone shows them as "changed" and gives a false FAIL). VERIFIED. The new value set being in this task's export proves it landed in the module. VERIFIED

## Rules and limits
1. New value sets only; never send an existing value set or value (it would update it).
2. Tested: independent, character, 2 values. Not tested: table-validated, dependent, number or date value sets, security, translations.
3. A new value set is used by nothing until a flexfield segment points to it.
4. Test records stay; record every value set and value.
5. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-27). Do not reuse these names.
Counts are from our run; later runs see more rows (every test adds records). That is expected.
| Step | Result |
|---|---|
| Export before | 7 files; 0 value sets, 0 values |
| Module id | from `PON_LINE_ATTRIBUTE_GROUPS`, 32 characters |
| Import | `GAPFILL_AB_S2_SVS1` with `GAPFILL_A`, `GAPFILL_B`: ProcessId 100004743465550, 3 rows, 0 failed |
| REST | INDEP / VARCHAR2 / 20, module ok, 2 values: PASS |
| Export after | value set + 2 values added, 0 removed, 0 changed: PASS |
