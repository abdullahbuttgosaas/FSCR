---
skill_id: "gosaas.gap-fills.sourcing.configure-supplier-qualification-controls"
name: "Configure Supplier Qualification Controls (GoSaaS gap fill, test-and-restore)"
description: "Change one value of the single supplier qualification options row (for example SendRFENotifEvalTeamFlag) through FSCR's setup-task CSV export and import, prove it, and put the old value back at once, proven by an export that matches the first one. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing and Supplier Management batch 04, 2026-11-28. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_POQ_CONFIGURE_SUPPLIER_QUALIFICATION_CONTROLS"
task_name: "Configure Supplier Qualification Controls"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Updates the ONE global options row that everyone uses. A test changes one value for about two minutes and then restores the old value; a real change stays."
---

# Configure Supplier Qualification Controls (GoSaaS gap fill, test-and-restore)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-28) · **GUESS** = judgment, not tested.

## What it is and when to use
Supplier qualification controls are global options (one row, `QualificationOptionCode ORA_POQ_QUALIFICATION_OPTION`, VERIFIED):
- `SupplierSourcingEligCode`: sourcing eligibility default for suppliers (seen `NOT_ALLOWED`)
- `OptinSourcingEligCode`: sourcing eligibility for opt-in (seen `ALLOWED`)
- `SendRFENotifEvalTeamFlag`: send request-for-evaluation notifications to the evaluation team (seen `Y`)
There is no "new record" to create: the task only updates this row. So a **test** is test-and-restore: read the old row, change ONE value, prove it, send the old row back at once, prove the export equals the first one. A **real** change is the same Step 2 and 3 with your new value and no restore.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder that holds sourcing\scripts\
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); create it first: mkdir -p "<RUN>"
COLV  = the column to change for the test, best SendRFENotifEvalTeamFlag (only notifications; VERIFIED)
NEWV  = the test value (the opposite of the old value: Y <-> N)
OLDV  = the old value, read in Step 1
```
Every `<...>` below is a placeholder. Git Bash: paths as `E:/...`; start every call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; shell variables do not survive between calls.

## Sign-in
If a call says HTTP 401/403, or hangs with no output, stop and sign in: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1`. **Sign in BEFORE Step 3 if your sign-in is older than about 45 minutes**: the restore must not wait for a sign-in. Never print tokens, the server address or user names; never print the metadata XML, the import log or FSCR's output file names (they hold the environment name).

## Prerequisites
None. The row exists on every environment (GUESS; seen on ours).

## Step 1. Read-only export (the old value)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_POQ_CONFIGURE_SUPPLIER_QUALIFICATION_CONTROLS --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,glob,zipfile; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys; [print(r) for r in csv.DictReader(open(sys.argv[1]+'/ORA_SUPPLIER_QUALIFICATION_OPTIONS.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
One CSV, `ORA_SUPPLIER_QUALIFICATION_OPTIONS.csv`, 1 row with the 4 columns above (no user columns, safe to print). Write down OLDV = the row's value of COLV. VERIFIED

## Step 2. Build BOTH packages first (offline)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; G="<GAPS>/sourcing/scripts"; K="ORA_SUPPLIER_QUALIFICATION_OPTIONS.csv|QualificationOptionCode=ORA_POQ_QUALIFICATION_OPTION"
python -I "$G/build_csv_package.py" --export-dir "<RUN>/export_before/unz" --out "<RUN>/pay_new/new.zip" --prefix GAPFILL_ --edit-row "$K|<COLV>=<NEWV>"
python -I "$G/build_csv_package.py" --export-dir "<RUN>/export_before/unz" --out "<RUN>/pay_old/old.zip" --prefix GAPFILL_ --edit-row "$K|<COLV>=<OLDV>"
```
Each prints `ORA_SUPPLIER_QUALIFICATION_OPTIONS.csv: 1 row(s)` and its ZIP. `--edit-row` copies the one existing row and changes only the named column (`--prefix` is required by the builder but not used for an edit). Both ZIPs exist before anything is changed, so the restore is ready. VERIFIED

## Step 3. Change, prove, restore (one call, no pause)
Approval: the person must approve the environment, the task and the temporary change (column, values) before this step.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; G="<GAPS>/sourcing/scripts"; T=ORA_POQ_CONFIGURE_SUPPLIER_QUALIFICATION_CONTROLS
cd "<FSCR>"; mkdir -p "<RUN>/imp_new" "<RUN>/imp_old"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code $T --task-name "Configure Supplier Qualification Controls" --zip-file "<RUN>/pay_new/new.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp_new" > "<RUN>/imp_new.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp_new.out"; python -I "$G/read_import_log.py" "<RUN>/imp_new"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code $T --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/export_changed" > "<RUN>/export_changed.out" 2>&1
python -I -c "import sys,glob,zipfile,csv; z=glob.glob(sys.argv[1]+'/*.zip'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz'); print('changed row:', [r for r in csv.DictReader(open(sys.argv[1]+'/unz/ORA_SUPPLIER_QUALIFICATION_OPTIONS.csv',encoding='utf-8-sig'))] if z else 'NO ZIP')" "<RUN>/export_changed"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code $T --task-name "Configure Supplier Qualification Controls" --zip-file "<RUN>/pay_old/old.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp_old" > "<RUN>/imp_old.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp_old.out"; python -I "$G/read_import_log.py" "<RUN>/imp_old"
```
Success (VERIFIED): two ProcessIds, each `Business object: Supplier Qualification Options. Status: Completed successfully`, `1 rows were processed. 0 rows of them failed`, `IMPORT: PASS`; the changed row shows `<COLV>` = NEWV and the other columns unchanged.
- **The restore import runs even if the change or the middle export failed.** If the restore import itself fails or drops, do not send the change again: run Step 4; if the row still shows NEWV, run only the restore import again (it sends the old value; that is safe to repeat).

## Step 4. Prove the restore
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_POQ_CONFIGURE_SUPPLIER_QUALIFICATION_CONTROLS --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/export_restored" > "<RUN>/export_restored.out" 2>&1
python -I -c "import sys,glob,zipfile; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_restored"
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_restored/unz" --key ORA_SUPPLIER_QUALIFICATION_OPTIONS.csv=QualificationOptionCode
```
`... before 1, after 1; added 0, removed 0, changed 0` and `RESULT: PASS` = the row is back exactly as before. VERIFIED

## Rules and limits
1. A test changes ONE column and restores it in the same call; never leave the test value. Prefer `SendRFENotifEvalTeamFlag` (notifications only). Changing the sourcing eligibility codes affects which suppliers can be invited to negotiations: do that only as a real, approved change.
2. Never add a second row (the task has one row, key `ORA_POQ_QUALIFICATION_OPTION`).
3. Valid values for the two eligibility codes are lookup codes (seen `ALLOWED`, `NOT_ALLOWED`; full list GUESS: read it on the page or from the lookup before a real change).
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-28)
| Step | Result |
|---|---|
| Before | 1 row: `NOT_ALLOWED`, `ALLOWED`, `SendRFENotifEvalTeamFlag Y` |
| Change | `SendRFENotifEvalTeamFlag N`: ProcessId 100004744440678, 1 row, 0 failed; export shows `N`, other columns same |
| Restore | `Y`: ProcessId 100004744440698, 1 row, 0 failed (about 2 minutes after the change) |
| Proof | restored export = first export: changed 0, RESULT: PASS |
