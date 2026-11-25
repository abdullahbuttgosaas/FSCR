---
skill_id: "gosaas.gap-fills.procurement.manage-purchasing-profile-options"
name: "Manage Purchasing Profile Options (GoSaaS gap fill)"
description: "Create a new Purchasing (application 201) profile option with its 3 levels and a site value through FSCR's setup-task CSV export and import, then read it back by REST. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 02, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "PO_MANAGE_PURCHASING_PROFILE_OPTIONS"
task_name: "Manage Purchasing Profile Options"
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
  - "Read-only export and REST reads; one CSV import that creates one new profile option (3 level rows + 1 site value). Nothing reads a new option, so no behaviour changes. Plan as if it stays."
---

# Manage Purchasing Profile Options (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. Same 3-file profile package as the Common Features task "Manage Applications Core Profile Options" (folder `common-features/manage-profile-options`), here for application 201 (Purchasing). This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
Purchasing profile options switch purchasing features (Redwood pages, supplier communication, default procurement business unit, ...). The task's export scope is a fixed list of about 50 seeded Purchasing options (mode `edit`). VERIFIED
- **Tested use (this skill):** create a **new** profile option in Purchasing with its levels and a site value. VERIFIED: Oracle accepted an option that is not in the scope list.
- **Not tested:** changing the value of a seeded option (for example `PO_DEFAULT_PRC_BU` at USER level). That changes a setting other people use; do it only on an environment you own, or as test-and-restore with the old value exported first (GUESS: same package, the seeded option and level rows copied unchanged from the export, plus the value row).

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
NAME   = new option name, PREFIX + short name (upper case, digits, _), e.g. GAPFILL_AB_PO1. GUESS: max 30 characters (the export shows longer seeded names cut at 40; keep it short)
DISPLAY= its display name; START = today as yyyy/mm/dd
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
1. The Purchasing module id (`ModuleId`), taken from the export (Step 1): every `FND_APP_PROFILE_OPTION.csv` row of application 201 except the Redwood "manage agreements" one shows the same ModuleId. VERIFIED. If the export has no rows, read it by REST from a seeded Purchasing lookup: `standardLookups/FOB` returns the same ModuleId (VERIFIED).

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PO_MANAGE_PURCHASING_PROFILE_OPTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys,collections; r=list(csv.DictReader(open(sys.argv[1],encoding='utf-8'))); print(collections.Counter((x['ApplicationId'],x['ModuleId']) for x in r))" "<RUN>/export_before/unz/FND_APP_PROFILE_OPTION.csv"
```
Expect 4 files (VERIFIED): the metadata XML, `FND_APP_PROFILE_OPTION.csv`, `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv`, `FND_APP_PROFILE_VALUE.csv`. Only scoped options that have a value are exported (8 in our test). The last command prints the (ApplicationId, ModuleId) pairs: use the most common ModuleId with ApplicationId `201` as MODULE (a second ModuleId with 1 row is expected: the Redwood manage-agreements option). Write it to `<RUN>/module.txt`.

## Step 2. Check the name is free (REST, read only)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/profileOptions?q=ProfileOptionName='<NAME>'&onlyData=true&fields=ProfileOptionName" \
  --no-open-browser --output "<RUN>/before.json"
python -I -c "import json,sys;print('count',json.load(open(sys.argv[1]))['count'])" "<RUN>/before.json"
```
Want `count 0`. Run `rest_call.py` without `-I`. (The `profileValues` resource did not find our option even after the load; use `profileOptions`. VERIFIED)

## Step 3. Build rows (new option, 3 levels, 1 site value)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key FND_APP_PROFILE_OPTION.csv=ProfileOptionName \
  --row "FND_APP_PROFILE_OPTION.csv|ProfileOptionName=<NAME>|ApplicationId=201|ModuleId=<MODULE>|Description=<text>|StartDateActive=<START>|UserProfileOptionName=<DISPLAY>" \
  --row "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=201|LevelName=PRODUCT|UpdateableFlag=N|EnabledFlag=N" \
  --row "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=201|LevelName=SITE|UpdateableFlag=Y|EnabledFlag=Y" \
  --row "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=201|LevelName=USER|UpdateableFlag=N|EnabledFlag=N" \
  --row "FND_APP_PROFILE_VALUE.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=201|LevelName=SITE|LevelValue=SITE|ProfileOptionValue=Y"
```
The option row is the parent of the level and value rows; all are in one ZIP (a child row is processed only with its parent in the same package). Leave `SqlValidation`, `EndDateActive` and audit columns empty. VERIFIED

## Step 4. Import
Approval: the person must approve the environment, the task and NAME before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code PO_MANAGE_PURCHASING_PROFILE_OPTIONS --task-name "Manage Purchasing Profile Options" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
Keep the ProcessId. `StatusCode: (unknown)` is normal; read the result only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"` (never cat/grep the log: it holds a user name). Success (VERIFIED): `Business object: Application Profile Value. Status: Completed successfully`, `A total of 5 rows were processed. 0 rows of them failed`. A dropped connection after the ProcessId: never import again; fetch the log with FSCR's `get_setup_task_csv_import_result.py`.

## Step 5. Read back (REST)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/profileOptions?q=ProfileOptionName='<NAME>'&expand=all&onlyData=true" \
  --no-open-browser --output "<RUN>/after.json"
python -I -c "
import json,sys; d=json.load(open(sys.argv[1])); x=d['items'][0] if d['count']==1 else {}
lv={l['LevelName']:(l['EnabledFlag'],l['UpdateableFlag']) for l in x.get('profileOptionLevels',[])}
site=[v['ProfileOptionValue'] for v in x.get('siteProfileOptionValues',[])]
ok=x.get('ApplicationShortName')=='PO' and lv=={'PRODUCT':('N','N'),'SITE':('Y','Y'),'USER':('N','N')} and site==['Y']
print(x.get('ProfileOptionName'), x.get('ApplicationShortName'), lv, site); print('READBACK:', 'PASS' if ok else 'FAIL')" "<RUN>/after.json"
```
`READBACK: PASS` = the option is in Purchasing (`PO`) with the 3 levels and site value Y. VERIFIED. A second export does not help: the new option is outside the export's fixed scope list (GUESS, not re-exported).

## Rules and limits
1. New options only. Never send a seeded option row changed; never import the full export.
2. A site value on a new option changes nothing for other users (no code reads it).
3. Test options stay (no delete). Record every name.
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 8 options, 8 site values, 24 level rows (all seeded options with values) |
| New option | `GAPFILL_AB_B2_PO1`, application 201, levels PRODUCT N/N, SITE Y/Y, USER N/N, site value Y |
| Import | ProcessId 100004743407091: 5 rows processed, 0 failed |
| REST read-back | found, ApplicationShortName PO, 3 levels as sent, site value Y: PASS |
