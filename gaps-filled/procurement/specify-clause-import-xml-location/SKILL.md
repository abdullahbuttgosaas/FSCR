---
skill_id: "gosaas.gap-fills.procurement.specify-clause-import-xml-location"
name: "Specify Contract Clause Import XML File Location (GoSaaS gap fill)"
description: "Set the site value of the profile option OKC_CLAUSE_IMP_FILE_LOCATION (directory used by the Import Clauses from XML File process) through FSCR's setup-task CSV import, and read it back by REST. Tested as test-and-restore. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 02, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_PROFILES"
task_name: "Specify Contract Clause Import XML File Location"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Changes ONE shared site-level setting: the directory the Import Clauses from XML File process uses. In a test, set the old value back at once (test-and-restore)."
---

# Specify Contract Clause Import XML File Location (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
The task sets one profile option: `OKC_CLAUSE_IMP_FILE_LOCATION`, "Location of XML File for Import Clauses" (application OKC, id 510). It holds the Enterprise Scheduler server directory where the **Import Clauses from XML File** process picks up files. Only the SITE level is enabled and updatable. VERIFIED
Use it to set that directory. This is a **shared setting**: on a shared environment, test it only as test-and-restore (Step 6). A real change needs the owner's approval.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
NEWDIR = the directory to set (a test value such as /usr/tmp/gapfill_<initials>/ in a test)
OLD    = the value read in Step 2 (to put back in a test)
```

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. **Without it Git Bash rewrites a value that starts with `/`** (for example `/usr/tmp/`) into a Windows path, and that wrong value is what Oracle stores. VERIFIED (it happened in our test).
- Shell variables do not survive between tool calls: keep values in files under `RUN`.
- Never read the import log with cat, sed or grep (it holds a user name and the environment name). Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/<import folder>"`, which prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. To show the ProcessId: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/<import>.out"`.
- FSCR's output file names start with the environment name: do not copy them into reports. Never print whole REST JSON (it holds user names in the audit fields); print only the fields you need.
- If an export prints `Error: Failed calling ...` and writes no ZIP, run it again into a new folder (read-only) and use that folder from then on.
- Do not wrap the import in a shell `timeout`. Save its output to a file. If its connection drops after `Started setup task CSV import process: <n>` was printed, **never import again**: fetch the log with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_PROFILES --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/<import folder>/recovered_process_log.txt"` (repeat until it is complete), then use the log reader on that folder.

## Sign-in
If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). Never print tokens, the server address or user names.

## Prerequisites
None.

## Step 1. Read-only export (package template)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_PROFILES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 4 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml`, `FND_APP_PROFILE_OPTION.csv`, `ORA_FND_APP_PROFILE_OPTION_LEVEL.csv`, `FND_APP_PROFILE_VALUE.csv`. The scope is the one option, mode `edit`. The CSVs may be **empty even when the option has a site value** (VERIFIED: 0 rows while REST showed the value). So REST (Step 2) is the source of the current value.

## Step 2. Read the option and its current value (REST, read only)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/profileOptions?q=ProfileOptionName='OKC_CLAUSE_IMP_FILE_LOCATION'&expand=all&onlyData=true" \
  --no-open-browser --output "<RUN>/before.json"
python -I "<GAPS>/procurement/scripts/profile_option_row.py" "<RUN>/before.json" --show
```
`profile_option_row.py --show` prints only: option name, ApplicationId, levels (enabled/updatable) and the SITE value. Write the SITE value down as OLD (for example `/usr/tmp/`, VERIFIED on our environment). Run `rest_call.py` without `-I`.

## Step 3. Build the package (option row unchanged + SITE value)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
OPT=$(python -I "<GAPS>/procurement/scripts/profile_option_row.py" "<RUN>/before.json")
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/set.zip" --prefix GAPFILL_ \
  --row "$OPT" \
  --row "FND_APP_PROFILE_VALUE.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=OKC_CLAUSE_IMP_FILE_LOCATION|FND_APP_PROFILE_OPTION.ApplicationId=510|LevelName=SITE|LevelValue=SITE|ProfileOptionValue=<NEWDIR>"
python -I -c "import zipfile,sys; print(zipfile.ZipFile(sys.argv[1]).read('FND_APP_PROFILE_VALUE.csv').decode())" "<RUN>/payload/set.zip"
```
- `profile_option_row.py` (no `--show`) prints the option row copied **unchanged** from REST (name, ApplicationId, ModuleId, description, start date, display name). A value row is processed only with its parent option row in the same ZIP.
- **Check the printed value row**: `ProfileOptionValue` must be exactly NEWDIR (no `E:/...` or `C:/...` in front). VERIFIED trap.
- `--prefix` is not used here (no new keys); any value works.
- `ApplicationId` 510 is OKC on our environment (VERIFIED). GUESS: the same on every environment; the helper reads it live anyway.

## Step 4. Import
Approval: the person must approve the environment, the task and NEWDIR. On a shared environment, approve the restore (Step 6) at the same time.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_PROFILES --task-name "Specify Contract Clause Import XML File Location" \
  --zip-file "<RUN>/payload/set.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_set" > "<RUN>/import_set.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import_set.out"
python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_set"
```
Success (VERIFIED): `Business object: Application Profile Value. Status: Completed successfully`, `A total of 2 rows were processed. 0 rows of them failed`, `IMPORT: PASS`.

## Step 5. Read back (REST)
Repeat Step 2 with `--output "<RUN>/after_set.json"` and `--show`: the SITE value must be NEWDIR. VERIFIED

## Step 6. Restore (test only: test-and-restore)
Do this **straight after Step 5**. Build `restore.zip` exactly as in Step 3 with `ProfileOptionValue=<OLD>` (check the printed row again), import it as in Step 4 into `<RUN>/import_restore`, then prove the option is back as it was:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/profileOptions?q=ProfileOptionName='OKC_CLAUSE_IMP_FILE_LOCATION'&expand=all&onlyData=true" \
  --no-open-browser --output "<RUN>/after_restore.json"
python -I "<GAPS>/procurement/scripts/profile_option_row.py" "<RUN>/after_restore.json" --same-as "<RUN>/before.json"
```
`SAME: PASS` = option fields, levels and every level value are equal to Step 2 (audit fields ignored). VERIFIED

## Rules and limits
1. One shared site setting. Never leave a test value in place; restore at once and prove it.
2. Only the SITE level is enabled (PRODUCT and USER are disabled), so a test cannot be kept to one user. VERIFIED
3. The value is a server directory path; Oracle does not check that it exists (GUESS: our test value was accepted).
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25)
| Step | Result |
|---|---|
| Export before | 4 files, 0 rows (scope: the one option) |
| REST before | SITE value `/usr/tmp/`; levels PRODUCT N/N, SITE Y/Y, USER N/N |
| Set | ProcessId 100004744391334: 2 rows, 0 failed. Stored value had a Windows prefix (Git Bash path rewrite, before the `MSYS_NO_PATHCONV=1` rule): the trap above |
| Restore | ProcessId 100004744391355: 2 rows, 0 failed; REST: SITE `/usr/tmp/`, option and levels unchanged: PASS |
