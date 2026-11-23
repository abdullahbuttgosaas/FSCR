---
skill_id: "gosaas.gap-fills.common-features.manage-profile-options"
name: "Manage Applications Core Profile Options (GoSaaS gap fill)"
description: "Create a new profile option definition (with its levels) through FSCR's setup-task CSV export and import (FND_APP_PROFILE_OPTION package), then read it back by REST (profileOptions) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 1, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS"
task_name: "Manage Applications Core Profile Options"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.apps-common.profile-options (read-back resource)"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
reused_by:
  - "common-features/manage-admin-profile-values (FND_MANAGE_APPLICATIONS_CORE_ADMINISTRATOR_PROFILE_VALUES)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new profile option definition and its level rows. It may not be deletable; plan as if it stays."
required_privileges:
  - "Export Import Functional Setups User plus the task privileges for FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS, and read access to the profileOptions REST resource"
---

# Manage Applications Core Profile Options (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's `core/fusion-api/apps-common/profile-options` skill reads and sets profile **values** by REST, but nothing in FSCR creates a profile option **definition** or names this task code. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **FROM FSCR** = FSCR file · **GUESS** = judgment, not tested.

## What this setup is
A profile option is a named setting (for example a date format or a feature switch). Its **definition** says which application owns it, its display name, and at which **levels** (SITE, PRODUCT, USER) a value may be set. Values are set in a separate task (Manage Administrator Profile Values). A new, user-defined option is not read by any Oracle code until someone writes an extension that reads it, so creating one changes nothing for other users.

## When to use
- Someone asks to create a **new** profile option definition for task `FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS`.
- Do **not** use it to change seeded options or existing values. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties
          (in a downloaded pack it is often a folder named fscr-main INSIDE another fscr-main). Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment
          share the saved sign-in (VERIFIED: two different copies both worked with one sign-in).
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
NAME    = new ProfileOptionName, upper case letters, digits and _, starting with PREFIX (max 80, GUESS)
DISPLAY = UserProfileOptionName (the name people see), e.g. "GAPFILL <INITIALS> test option"
```
Pick a NAME that does not exist yet. Do not reuse the worked-example names at the end.

## Step 0. Run FSCR in place, safely
- Run FSCR scripts with their full path and `python -B`; always pass `--output-dir` under `RUN`.
- **Git Bash on Windows:** paths as `E:/folder/...`, not `/e/folder/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.
- Put `timeout 120` in front of REST reads: an expired token makes them hang silently.
- Never print tokens, headers, the sign-in URL or the server address.

## Step 1. Sign in (only if needed)
Run Step 2 first; it shows whether the saved token works. If it says HTTP 401/403 or the token expired, or a REST read hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication` (run in the background; the listener waits on the redirect port, 8765 by default):
```bash
cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600
```
A person signs in on the browser tab (`Login complete for standard`). Never read or type credentials. Sign-in time is waiting time.

## Step 2. Read-only export (layout + names in use)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
`inspect_export.py` prints file names with column and row counts. To see one file's column names:
`python -I -c "import csv,sys;print(next(csv.reader(open(sys.argv[1],encoding='utf-8'))))" "<RUN>/export_before/unz/<file>.csv"`.
Expect 4 files (VERIFIED, about 25 seconds; row counts grow with every earlier test, so yours will differ from the worked example):
- `FND_APP_PROFILE_OPTION.csv` (13 columns): `ProfileOptionName, ApplicationId, ModuleId, Description, SqlValidation, StartDateActive, EndDateActive, UserProfileOptionName` + 5 audit columns
- `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv` (10): `FND_APP_PROFILE_OPTION.ProfileOptionName, FND_APP_PROFILE_OPTION.ApplicationId, LevelName, UpdateableFlag, EnabledFlag` + audit. Every option has 3 rows: PRODUCT, SITE, USER.
- `FND_APP_PROFILE_VALUE.csv` (10): option keys + `LevelName, LevelValue, ProfileOptionValue` + audit
- `ASM_SETUP_CSV_METADATA.xml`: scope `moduleType=APPLICATION`, `moduleKey=FND`, `mode=search`
- The export is scoped (Applications Core options and options customers added), not every option. If it fails or lacks these files: **stop**, do not import.

## Step 3. Module id and before-read (REST)
The new option needs the Applications Core `ModuleId` (32 characters) so it lands in the task's scope. Read it from the seeded `YES_NO` lookup, which every environment has:
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource standardLookups --q "LookupType='YES_NO'" \
  --fields LookupType,ModuleId --out "<RUN>/fnd_module.json" --expect-count 1
python -I -c "import json,sys;print(json.load(open(sys.argv[1]))['items'][0]['ModuleId'])" "<RUN>/fnd_module.json"
```
Keep it as MODULE; check it is not empty. Then check NAME is free:
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions \
  --q "ProfileOptionName='<NAME>'" --out "<RUN>/readback_before.json" --expect-absent
```
Want `0 row(s)` and `READBACK: PASS`. Exit 2 = sign-in or privilege problem, not "absent". (The REST item form `profileOptions/<NAME>` gives HTTP 400 through this helper; use the `--q` form. VERIFIED)

## Step 4. Build a package with only the new option
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name profile_option_new.zip --prefix <PREFIX> \
  --key "FND_APP_PROFILE_OPTION.csv=ProfileOptionName,ApplicationId" \
  --key "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv=FND_APP_PROFILE_OPTION.ProfileOptionName,FND_APP_PROFILE_OPTION.ApplicationId,LevelName" \
  --key "FND_APP_PROFILE_VALUE.csv=FND_APP_PROFILE_OPTION.ProfileOptionName,FND_APP_PROFILE_OPTION.ApplicationId,LevelName,LevelValue" \
  --prefix-col "FND_APP_PROFILE_OPTION.csv=ProfileOptionName" --max-len "ProfileOptionName=80" \
  --row "FND_APP_PROFILE_OPTION.csv|ProfileOptionName=<NAME>|ApplicationId=0|ModuleId=<MODULE>|Description=<text>|StartDateActive=<yyyy/mm/dd>|UserProfileOptionName=<DISPLAY>" \
  --row "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=0|LevelName=PRODUCT|UpdateableFlag=N|EnabledFlag=N" \
  --row "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=0|LevelName=SITE|UpdateableFlag=Y|EnabledFlag=Y" \
  --row "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<NAME>|FND_APP_PROFILE_OPTION.ApplicationId=0|LevelName=USER|UpdateableFlag=N|EnabledFlag=N"
```
- Dates are `yyyy/mm/dd` (the export's format). VERIFIED
- `ApplicationId=0` = Applications Core (FND), the application of the task's scope. VERIFIED (REST then shows `ApplicationShortName=FND`).
- Give all 3 level rows; the pattern above (site only) is the one tested. To allow user-level values, set USER to `Y`/`Y` (GUESS: same shape as seeded options that allow it).
- Leave `SqlValidation`, `EndDateActive`, audit columns and the value file empty (values are the next task). VERIFIED
- The helper stops if NAME is already in the export (importing it would **update** that option), lacks the prefix, or is too long.

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact NAME before the import. If their brief already names all three and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS --task-name "Manage Applications Core Profile Options" \
  --zip-file "<RUN>/payload/profile_option_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 40 seconds. VERIFIED. The script may print `StatusCode: (unknown)`; the real result is only in `<RUN>/import_result/*_process_log.txt` (one long line with literal `\r\n`). Read it with
  `python -I -c "import sys,glob; print(open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<RUN>/import_result"`
- Success: `Business object: Application Profile Value`, `Detail Object: ProfileOptionSD.xml ... A total of 4 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`. VERIFIED (1 option + 3 levels = 4)
- **`0 rows were processed` is a failure**, even though the status says "Completed successfully". Not complete yet: keep the ProcessId and use FSCR's `get_setup_task_csv_import_result.py`; do not import twice. Rows failed: copy the error, change one thing, retry at most 3 times.

## Step 6. Read back two ways
**A. REST** (FROM FSCR `core/fusion-api/apps-common/profile-options/references/profile-options.md`, resource `profileOptions`):
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions --q "ProfileOptionName='<NAME>'" \
  --fields ProfileOptionName,ApplicationShortName,UserProfileOptionName,Description,StartDateActive \
  --out "<RUN>/readback_after.json" --expect "ProfileOptionName=<NAME>,UserProfileOptionName=<DISPLAY>" --expect-count 1
```
`READBACK: PASS` = exactly one option with your name and display name. VERIFIED. Always pass `--fields`: without it the row also holds user names.

**B. Second export and compare:** repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_PROFILE_OPTION.csv=ProfileOptionName,ApplicationId" \
  --key "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv=FND_APP_PROFILE_OPTION.ProfileOptionName,FND_APP_PROFILE_OPTION.ApplicationId,LevelName" \
  --key "FND_APP_PROFILE_VALUE.csv=FND_APP_PROFILE_OPTION.ProfileOptionName,FND_APP_PROFILE_OPTION.ApplicationId,LevelName,LevelValue" \
  --expect "FND_APP_PROFILE_OPTION.csv=<NAME>,0" \
  --expect "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv=<NAME>,0,PRODUCT" \
  --expect "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv=<NAME>,0,SITE" \
  --expect "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv=<NAME>,0,USER" --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your option and its 3 levels were added, nothing removed or changed. Give **every** added row as `--expect` (the 3 levels too), or the compare reports a PROBLEM. VERIFIED

**Evidence (optional):** `python -B "<H>/render_readback.py" --json <readback json> --title "..." --png <file.png>`.

## Rules and limits
1. **New records only.** Never import a full export: a matching `ProfileOptionName` + `ApplicationId` would update that option.
2. **Keep all 4 files** in the package, metadata XML unchanged.
3. **Test records may stay for good.** This skill never deletes. Record every created option in your change log.
4. **Not tested:** SQL validation (list of values), end dates, options owned by an application other than 0, translations.
5. **Tested on one environment** (release 11.13.26.10.0).
6. **Python flags.** `-B`, no `-I`: FSCR scripts, `rest_read.py`, `render_readback.py`. `-I`: `inspect_export.py`, `build_fsm_package.py`, `compare_fsm_exports.py`, the one-liners.

## Worked example (VERIFIED, 2026-11-23). Do not reuse these names; they now exist.
| Step | Result |
|---|---|
| Export before | 91 options, 273 level rows, 45 values; 24 s |
| Module id + before-read | ModuleId from `YES_NO`; `GAPFILL_AB_PO1`: 0 rows, PASS |
| New record | `GAPFILL_AB_PO1`, application 0, site level enabled, product and user disabled |
| Import | 1 attempt, 41 s: 4 rows processed, 0 failed |
| REST read-back | 1 row, `ApplicationShortName=FND`, names match: PASS |
| Export after + compare | 92 options, 276 level rows; added 1 + 3, removed 0, changed 0: PASS |
