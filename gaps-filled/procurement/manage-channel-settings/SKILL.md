---
skill_id: "gosaas.gap-fills.procurement.manage-channel-settings"
name: "Manage Channel Settings (GoSaaS gap fill)"
description: "Change the enabled flag or value of one channel (claims / customer channel) setting value through FSCR's setup-task CSV export and import, and prove it with exports. Tested as test-and-restore. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 02, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_MANAGE_CHANNEL_SETTINGS"
task_name: "Manage Channel Settings"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Changes ONE existing setting value row (shared). In a test, set the old value back at once (test-and-restore)."
---

# Manage Channel Settings (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
Channel settings control channel revenue management (claims, customer channel programs). The task has:
- `ORA_CJM_SETTING.csv`: the seeded settings (key `SettingCode`, e.g. `CLAIM_OWNER_CODE`), with level (e.g. `BUSINESS_UNIT`). VERIFIED (26 rows on our environment)
- `ORA_CJM_SETTING_VALUE.csv`: values per setting and business unit (key `ORA_CJM_SETTING.SettingCode` + `ValueCode`), with `EnabledFlag` and `SettingValue`. VERIFIED (5 rows)

Use it to change an existing setting value. This is a **shared setting**: on a shared environment, test it only as test-and-restore (Step 6). A real change needs the owner's approval. GUESS: a new value row for another business unit would work the same way with `--row`, but was not tested.

## Placeholders
```text
FSCR    = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS    = the gaps-filled folder that holds procurement\scripts\
RUN     = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
SETTING = the SettingCode; VALUECODE = the ValueCode of the value row to change
FIELD   = EnabledFlag (tested) or SettingValue; NEW = the new value; OLD = the value in the Step 1 export
```

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` (Git Bash otherwise rewrites values that start with `/`). VERIFIED
- Shell variables do not survive between tool calls: keep values in files under `RUN`.
- Never read the import log with cat, sed or grep (it holds a user name and the environment name). Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/<import folder>"`: it prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`.
- The ProcessId: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/<import>.out"`.
- FSCR's file names start with the environment name: do not copy them into reports. Business unit names are customer data: print only the rows you need.
- If an export prints `Error: Failed calling ...` and writes no ZIP, run it again into a **new** folder (read-only) and use that folder from then on.
- Do not wrap the import in a shell `timeout`. If its connection drops after the ProcessId line, **never import again**: fetch the log with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code ORA_MANAGE_CHANNEL_SETTINGS --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/<import folder>/recovered_process_log.txt"` (repeat until complete), then use the log reader on that folder. If even that finds no log, the exports (Step 4) are the proof. VERIFIED (it happened once; the mid export proved the change)

## Sign-in
If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). Never print tokens, the server address or user names.

## Prerequisites
The value row must already exist (this skill changes, it does not create).

## Step 1. Read-only export (before)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_MANAGE_CHANNEL_SETTINGS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys; [print(r['ORA_CJM_SETTING.SettingCode'],r['ValueCode'],r['EnabledFlag'],repr(r['SettingValue'])) for r in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'))]" "<RUN>/export_before/unz/ORA_CJM_SETTING_VALUE.csv"
```
Expect 3 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml`, `ORA_CJM_SETTING.csv`, `ORA_CJM_SETTING_VALUE.csv`. Pick SETTING + VALUECODE from the printed list and write down OLD.

## Step 2. Build the change package (parent row unchanged + changed value row)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/test.zip" --prefix GAPFILL_ --only \
  --copy-row "ORA_CJM_SETTING.csv|SettingCode=<SETTING>" \
  --edit-row "ORA_CJM_SETTING_VALUE.csv|ORA_CJM_SETTING.SettingCode=<SETTING>&ValueCode=<VALUECODE>|<FIELD>=<NEW>"
```
- A value row is processed only with its **parent** setting row in the same ZIP: `--copy-row` adds it unchanged. VERIFIED
- The `&` key form matches both columns (the same ValueCode can appear under several settings). The builder stops unless exactly one row matches, and prints `FIELD 'OLD' -> 'NEW'`: check it.
- `--prefix` is not used here (no new keys); any value works.

## Step 3. Import
Approval: the person must approve the environment, the task, the row and NEW. On a shared environment, approve the restore (Step 6) at the same time.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_MANAGE_CHANNEL_SETTINGS --task-name "Manage Channel Settings" \
  --zip-file "<RUN>/payload/test.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_test" > "<RUN>/import_test.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import_test.out"
python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_test"
```
Success (VERIFIED): `Channel Setting` and `Channel Setting Value` completed successfully, 0 failed, `IMPORT: PASS`.

## Step 4. Read back (export mid + compare)
Repeat Step 1 into `<RUN>/export_mid` (unzip the same way; the last command shows the row), then:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_mid/unz" \
  --key ORA_CJM_SETTING.csv=SettingCode \
  --key ORA_CJM_SETTING_VALUE.csv=ORA_CJM_SETTING.SettingCode+ValueCode
```
Here the expected result is `RESULT: FAIL` with **exactly** `ORA_CJM_SETTING_VALUE.csv ... changed 1` (your row) and nothing else changed or removed: that proves the change, and the parent row is unchanged. VERIFIED

## Step 5. (Real change) stop here
For a real, approved change you are done after Step 4. For a test, go on to Step 6 at once.

## Step 6. Restore (test only: test-and-restore)
Build `<RUN>/payload/restore.zip` as in Step 2 from the **before** export with `<FIELD>=<OLD>` (the builder prints `'OLD' -> 'OLD'`: correct, the before export still holds OLD), import it as in Step 3 into `<RUN>/import_restore`, then export into `<RUN>/export_after` and compare with the **first** export using the Step 4 command (`export_after` instead of `export_mid`). `RESULT: PASS` = everything is back as in Step 1. VERIFIED

## Rules and limits
1. Shared rows. Never leave a test value in place; restore at once and prove it.
2. Always send the parent setting row unchanged (`--copy-row`); never change a seeded setting row.
3. `SettingValue` changes are GUESS (not tested); a value such as a calendar or catalog id must exist.
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Use another row in your own test.
| Step | Result |
|---|---|
| Export before | 3 files; SETTING 26 rows, SETTING_VALUE 5 rows |
| Change | `CLAIM_OWNER_CODE` / `BU2` EnabledFlag Y -> N: ProcessId 100004744393512 (connection dropped, no log found); mid export: changed 1, value N |
| Restore | N -> Y: ProcessId 100004744394843, 2 objects succeeded; compare with first export: PASS |
