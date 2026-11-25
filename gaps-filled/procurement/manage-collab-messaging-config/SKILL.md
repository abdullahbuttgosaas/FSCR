---
skill_id: "gosaas.gap-fills.procurement.manage-collab-messaging-config"
name: "Manage Collaboration Messaging Configuration (GoSaaS gap fill)"
description: "Change one field of the collaboration messaging parameters (for example the auto-reprocess time period) through FSCR's setup-task CSV export and import, and prove it with exports. Tested as test-and-restore. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 02, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_CMK_MANAGE_COLLAB_MESG_CONFIG"
task_name: "Manage Collaboration Messaging Configuration"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Changes ONE shared row (the collaboration messaging parameters, one row per environment). In a test, set the old value back at once (test-and-restore)."
---

# Manage Collaboration Messaging Configuration (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
Collaboration messaging sends and receives B2B purchasing messages. This task holds:
- `ORA_CMK_COLLAB_MSG_PARAM.csv`: **one** row of parameters (key `MsgParamId`), for example `AutoRepTimePeriod`, `EssOutRepInterval`, `MaxMsgPayloadSize`. VERIFIED
- `ORA_CMK_COLLAB_MSG_BUS_PROCESS.csv`: business processes and their `EnableFlag`. VERIFIED (7 rows on our environment)
- `ORA_CMK_COLLAB_MSG_PARAM_DATA.csv`: default and maximum numbers by `ParamDataId` only; it has **no parameter name**, so you cannot tell which row belongs to which field. Read only here. VERIFIED (21 rows)

There is nothing to create: you change an existing row. This is a **shared setting**: on a shared environment, test it only as test-and-restore (Step 6). A real change needs the owner's approval.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder that holds procurement\scripts\
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
FIELD = the column of ORA_CMK_COLLAB_MSG_PARAM.csv to change (e.g. AutoRepTimePeriod)
NEW   = the new value; OLD = the value in the Step 1 export (to put back in a test)
```

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` (Git Bash otherwise rewrites values that start with `/`). VERIFIED
- Shell variables do not survive between tool calls: keep values in files under `RUN`.
- Never read the import log with cat, sed or grep (it holds a user name and the environment name). Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/<import folder>"`: it prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`.
- The ProcessId: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/<import>.out"`.
- FSCR's file names start with the environment name: do not copy them into reports.
- If an export prints `Error: Failed calling ...` and writes no ZIP, run it again into a **new** folder (read-only) and use that folder from then on. VERIFIED (it happened once)
- Do not wrap the import in a shell `timeout`. If its connection drops after the ProcessId line, **never import again**: fetch the log with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code ORA_CMK_MANAGE_COLLAB_MESG_CONFIG --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/<import folder>/recovered_process_log.txt"` (repeat until complete), then use the log reader on that folder.

## Sign-in
If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). Never print tokens, the server address or user names.

## Prerequisites
None.

## Step 1. Read-only export (before)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_CMK_MANAGE_COLLAB_MESG_CONFIG --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys; r=list(csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'))); print(len(r),'row(s)'); [print(k,'=',v) for k,v in r[0].items()]" "<RUN>/export_before/unz/ORA_CMK_COLLAB_MSG_PARAM.csv"
```
Expect 4 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml` and the 3 CSVs above. The last command prints the one parameter row. Write down `MsgParamId` and OLD (the FIELD value). These files hold no audit columns. VERIFIED

## Step 2. Build the change package
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/test.zip" --prefix GAPFILL_ \
  --edit-row "ORA_CMK_COLLAB_MSG_PARAM.csv|MsgParamId=<MsgParamId>|<FIELD>=<NEW>"
```
- `--edit-row` copies the one existing row and changes only FIELD. It prints `FIELD 'OLD' -> 'NEW'`: check it. The other 2 CSVs go in with the header only (no change). VERIFIED
- `--prefix` is not used here (no new keys); any value works.
- The export does not show the allowed range of a field (see above). Keep a test change small (OLD + 1 was accepted for `AutoRepTimePeriod` and `EssOutRepInterval`: VERIFIED). For a real change, check the range on the screen first.

## Step 3. Import
Approval: the person must approve the environment, the task, FIELD and NEW. On a shared environment, approve the restore (Step 6) at the same time.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_CMK_MANAGE_COLLAB_MESG_CONFIG --task-name "Manage Collaboration Messaging Configuration" \
  --zip-file "<RUN>/payload/test.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_test" > "<RUN>/import_test.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import_test.out"
python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_test"
```
Success (VERIFIED): `IMPORT: PASS`, 1 row processed, 0 failed.

## Step 4. Read back (export mid + compare)
Repeat Step 1 into `<RUN>/export_mid` (unzip the same way; if it made no ZIP, re-run into `<RUN>/export_mid2` and use that), then:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_mid/unz" \
  --key ORA_CMK_COLLAB_MSG_PARAM.csv=MsgParamId \
  --key ORA_CMK_COLLAB_MSG_BUS_PROCESS.csv=BusinessProcessId \
  --key ORA_CMK_COLLAB_MSG_PARAM_DATA.csv=ParamDataId
```
Here the expected result is `RESULT: FAIL` with **exactly** `ORA_CMK_COLLAB_MSG_PARAM.csv ... changed 1` and nothing else changed or removed: that proves the change. Print FIELD from the mid export (last command of Step 1 on `export_mid`): it must be NEW. VERIFIED

## Step 5. (Real change) stop here
For a real, approved change you are done after Step 4. For a test, go on to Step 6 at once.

## Step 6. Restore (test only: test-and-restore)
Build `restore.zip` as in Step 2 from the **before** export and `--out "<RUN>/payload/restore.zip"`, with `<FIELD>=<OLD>` (the builder prints `'OLD' -> 'OLD'`: correct, the before export still holds OLD), import it as in Step 3 into `<RUN>/import_restore`, then export into `<RUN>/export_after` and compare with the **first** export (if that export made no ZIP, re-run it into `<RUN>/export_after2` and put that folder in the command below):
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_CMK_COLLAB_MSG_PARAM.csv=MsgParamId \
  --key ORA_CMK_COLLAB_MSG_BUS_PROCESS.csv=BusinessProcessId \
  --key ORA_CMK_COLLAB_MSG_PARAM_DATA.csv=ParamDataId
```
`RESULT: PASS` = everything is back as in Step 1. VERIFIED

## Rules and limits
1. One shared row. Never leave a test value in place; restore at once and prove it.
2. Change only the columns you name; `--edit-row` keeps the rest exactly as exported.
3. Business process `EnableFlag` changes work the same way (`--edit-row "ORA_CMK_COLLAB_MSG_BUS_PROCESS.csv|BusinessProcessId=<id>|EnableFlag=<Y/N>"`). GUESS: not tested.
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Use another value in your own test.
| Step | Result |
|---|---|
| Export before | 4 files; PARAM 1 row (MsgParamId 30010), BUS_PROCESS 7, PARAM_DATA 21 |
| Change | AutoRepTimePeriod 50 -> 51: ProcessId 100004744393468, IMPORT PASS |
| Mid export | changed 1 (PARAM), nothing else; value 51 |
| Restore | 51 -> 50: ProcessId 100004744394251, IMPORT PASS; compare with first export: PASS |
