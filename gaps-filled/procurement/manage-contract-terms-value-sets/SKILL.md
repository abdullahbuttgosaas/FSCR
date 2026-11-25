---
skill_id: "gosaas.gap-fills.procurement.manage-contract-terms-value-sets"
name: "Manage Contract Terms Value Sets (GoSaaS gap fill)"
description: "Create a new independent value set with values in the Contract Terms (OKC) module through FSCR's setup-task CSV export and import, then read it back by REST and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 01, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "OKC_MANAGE_CONTRACT_TERMS_VALUE_SETS"
task_name: "Manage Contract Terms Value Sets"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.3.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only exports and REST reads; one CSV import that creates one new value set and its values. Plan as if it stays."
---

# Manage Contract Terms Value Sets (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. Same value set package as the Common Features task "Manage Applications Core Value Sets", scoped to the Contract Terms module (`OKC`). This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
Contract terms value sets give the list of values for contract terms flexfields and Contract Expert variables. Use this skill to create a **new independent value set** (a fixed list of text values) in module `OKC`. Do not use it to change an existing value set or its values.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
VS     = new value set code, PREFIX + short name (upper case, digits, _), e.g. GAPFILL_AB_VS1
V1, V2 = new values (text, upper case because UppercaseOnlyFlag=Y, max MaximumLength characters)
```

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Without it Git Bash rewrites values that start with `/` (for example `/usr/tmp/`) into Windows paths. VERIFIED (it happened once).
- Shell variables do **not** survive from one tool call to the next. Save any value you need later (module id, codes) in a file under `RUN` and read it back, or set it again in the same call.
- **Never read the import log with cat, sed or grep**: it is one long line holding the environment name and the submitting user name. Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"`. It prints only the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. VERIFIED
- FSCR's export and import file names start with the environment name; do not copy them into reports.
- If an export prints `Error: Failed calling ...` (network) and writes no ZIP, run it again into a new folder (it is read-only; up to 3 times). VERIFIED
- Do **not** wrap the import in a shell `timeout`: once the ProcessId is printed the import runs on in Oracle. The script's own `--wait-seconds` is enough. Save the import output to a file so the ProcessId is not lost.
- Row counts in exports grow with every test run (rows from earlier test runs are normal). The worked example counts are from our first run.

- The ProcessId is on the line `Started setup task CSV import process: <n>` of the import output. Save the output to a file and print only that line: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"`.
- If the before- or after-export had to be re-run into a new folder, use **that** folder (the one holding the ZIP) in every later command instead of `export_before` / `export_after`.
- If an import's connection drops after the ProcessId line (`Error: Failed calling ...` printed **with** a ProcessId), the import still runs in Oracle: **never import again**. Fetch its log into the import folder with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code <TASK CODE> --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/import_result/recovered_process_log.txt"`; if it says the process is not complete, run it again. Then read it with `read_import_log.py "<RUN>/import_result"`. VERIFIED

## Sign-in
- Run FSCR scripts with their full path and `python -B`; set `PYTHONUTF8=1`. In Git Bash write paths as `E:/...` (never `/e/...`) and set `MSYS_NO_PATHCONV=1`.
- If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
  `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). VERIFIED
- Never print tokens, the server address or user names.

## Prerequisites
1. The Contract Terms module id (`ModuleId`), read live (Step 2). Never copy it from an example.

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code OKC_MANAGE_CONTRACT_TERMS_VALUE_SETS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 7 files (VERIFIED): the metadata XML and `FND_APP_FLEX_VALUE_SET.csv`, `ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv`, `ORA_APPLICATION_FLEXFIELD_RELATED_VALUE_SET.csv`, `ORA_APPLICATION_FLEXFIELD_RELATED_VALUE_SET_VALUE.csv`, `ORA_APPLICATION_FLEXFIELD_VALUE_SET_VALIDATION_VIEW_OBJECT.csv`, `ORA_FND_APP_FLEX_VALUE_SET_VALIDATION_TABLE.csv`. Scope: `moduleType` APPLICATION, `moduleKey` OKC, mode `search`. Only user-made value sets of that module are exported (0 rows on a fresh environment, test sets from earlier runs otherwise; seeded OKC value sets are not in it). VERIFIED

## Step 2. Read the module id and check the name is free (REST, read only)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/standardLookups/OKC_SUBJECT?onlyData=true&fields=LookupType,ModuleId" \
  --no-open-browser --output "<RUN>/okc_module.json"
python -I -c "import json,sys;print(json.load(open(sys.argv[1]))['ModuleId'])" "<RUN>/okc_module.json" > "<RUN>/module.txt"; MODULE=$(cat "<RUN>/module.txt")
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/valueSets?q=ValueSetCode='<VS>'&onlyData=true&fields=ValueSetCode" \
  --no-open-browser --output "<RUN>/vs_before.json"
python -I -c "import json,sys;print('count',json.load(open(sys.argv[1]))['count'])" "<RUN>/vs_before.json"
```
- `OKC_SUBJECT` (the seeded clause type lookup) belongs to the Contract Terms module; its ModuleId is the one the existing `OKC_XPRT_...` value sets use. VERIFIED. Run `rest_call.py` without `-I`.
- Want `count 0`. If not 0, pick another VS.

## Step 3. Build rows (new value set + values only)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; MODULE=$(cat "<RUN>/module.txt")
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key FND_APP_FLEX_VALUE_SET.csv=ValueSetCode \
  --row "FND_APP_FLEX_VALUE_SET.csv|ValueSetCode=<VS>|ModuleId=$MODULE|Description=<text>|ValidationType=INDEP|ValueDataType=VARCHAR2|ValueSubtype=TEXT|MaximumLength=20|UppercaseOnlyFlag=Y|ZeroFillFlag=N|SecurityEnabledFlag=N" \
  --row "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv|FND_APP_FLEX_VALUE_SET.ValueSetCode=<VS>|Value=<V1>|Description=<text>|EnabledFlag=Y|SummaryFlag=N|SortOrder=1" \
  --row "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv|FND_APP_FLEX_VALUE_SET.ValueSetCode=<VS>|Value=<V2>|Description=<text>|EnabledFlag=Y|SummaryFlag=N|SortOrder=2"
```
All 7 files go in the ZIP (the 4 others with headers only); metadata XML unchanged; ids, dates and audit columns empty. VERIFIED

## Step 4. Import
Approval: the person must approve the environment, the task, VS and its values before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code OKC_MANAGE_CONTRACT_TERMS_VALUE_SETS --task-name "Manage Contract Terms Value Sets" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
- Keep the ProcessId. `StatusCode: (unknown)` is normal; read the result only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"` (never cat/grep the log: it holds a user name). Success (VERIFIED): `Business object: Application Flexfield Value Set. Status: Completed successfully`, `A total of 3 rows were processed. 0 rows of them failed` (1 set + 2 values).
- A dropped connection after the ProcessId: never import again; fetch and read the log as the shell section says (recovered_process_log.txt).

## Step 5. Read back (REST + second export)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"; MODULE=$(cat "<RUN>/module.txt")
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/valueSets/<VS>?expand=values&onlyData=true" \
  --no-open-browser --output "<RUN>/vs_after.json"
python -I -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['ValueSetCode'],d['ModuleId']==sys.argv[2],d['ValidationType'],[(v['Value'],v['EnabledFlag']) for v in d['values']])" "<RUN>/vs_after.json" "$MODULE"
```
Want the VS, `True`, `INDEP` and both values with `Y`. VERIFIED. Then repeat Step 1 into `<RUN>/export_after` and:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key FND_APP_FLEX_VALUE_SET.csv=ValueSetCode --key ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=FND_APP_FLEX_VALUE_SET.ValueSetCode+Value \
  --expect FND_APP_FLEX_VALUE_SET.csv=<VS>
```
`RESULT: PASS` = only your set and its values were added, nothing removed or changed. VERIFIED. If a folder has no export, export again.

## Rules and limits
1. New records only; a row with an existing ValueSetCode or value would update it.
2. Keep every export file in the package.
3. Values are stored upper case only when `UppercaseOnlyFlag=Y`; send them upper case. Value length must fit `MaximumLength`.
4. Test value sets stay (no delete). Using the set in a flexfield or Contract Expert variable is a separate task.
5. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 7 files, 0 rows |
| New set | `GAPFILL_AB_B1_VS1` INDEP, VARCHAR2 20; values `GAPFILL_V1`, `GAPFILL_V2` |
| Import | ProcessId 100004744391249: 3 rows processed, 0 failed |
| REST after | set found in the OKC module, 2 values enabled |
| Export after + compare | added 1 set + 2 values, removed 0, changed 0: PASS |
