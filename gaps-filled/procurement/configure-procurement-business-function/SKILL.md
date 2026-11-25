---
skill_id: "gosaas.gap-fills.procurement.configure-procurement-business-function"
name: "Configure Procurement Business Function (GoSaaS gap fill)"
description: "Change the purchasing and sourcing options of a procurement business unit through FSCR's setup-task CSV export and import (--edit-row of the one existing BU row). Written, not import-tested: every row is a live business unit's setup, so an agent test is unsafe. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 03, 2026-11-25. Export checked live on one test environment; import NOT tested (unsafe). NOT official FSCR."
task_code: "PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION"
task_name: "Configure Procurement Business Function"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Changes a live business unit's setup. Only with the owner's approval; never as an agent test."
---

# Configure Procurement Business Function (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
This task holds the purchasing and sourcing options of a procurement business unit. The export has: `PO_SYSTEM_PARAMETER.csv` (one row per procurement BU, key `ShortCode`, 123 columns: currency, rate type, receipt close, sourcing, approval flags, ...), `PO_DOCUMENT_TYPE.csv` + translation (84 rows: document types per BU), `PON_CONTRACTS.csv` + translation (negotiation contract terms text). VERIFIED
There is no "new record" to create: each row belongs to an existing business unit, and every change changes how that BU works. **An agent must not test this by import** (VERIFIED on 2026-11-25: the agent's permission check blocked a test-and-restore import as an unwanted change to an existing BU). Use this skill when the BU owner has approved a specific change, and let that person run Step 3.

## Placeholders
```text
FSCR  = the FSCR root folder. Read only.
GAPS  = the gaps-filled folder that holds procurement\scripts\
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo
FIELD = the column to change; NEW = the approved new value; OLD = the value in the Step 1 export
```

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` (Git Bash otherwise rewrites values that start with `/`). VERIFIED
- Shell variables do not survive between tool calls: keep values in files under `RUN`.
- Save every FSCR script's output to a file (`> "<RUN>/<step>.out" 2>&1`) and print only the lines you need: error lines can hold the server address.
- Never read the import log with cat, sed or grep (it holds a user name and the environment name). Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/<import folder>"`: it prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. The ProcessId: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/<import>.out"`.
- Never print whole export rows: owner columns (`ListName...`, `EmailAddress...`) and audit columns hold names. FSCR's file names start with the environment name: do not copy them into reports.
- If an export makes no ZIP (`Error: Failed calling ...`; the unzip line then fails with `IndexError`), run it again into a **new** folder (read-only) and use that folder in every later command. VERIFIED (it happens often)
- Do not wrap the import in a shell `timeout`. If its connection drops after the ProcessId line, **never import again**: `mkdir -p` the import folder, fetch the log with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/<import folder>/recovered_process_log.txt"` (repeat until complete), then use the log reader on that folder.
- `compare_exports.py` counts rows from earlier test runs as "before" rows: counts grow with every run.

## Sign-in
If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). Never print tokens, the server address or user names.

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); sys.exit('NO ZIP: run the export again into a new folder') if not z else zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Look only at the columns you need (BU names and owner/audit columns are customer data):
`python -I -c "import csv,sys; [print(r[sys.argv[2]], r[sys.argv[3]]) for r in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'))]" "<RUN>/export_before/unz/<CSV>" <key column> <FIELD>`

## Step 2. Build the change package (one row, one field)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/change.zip" --prefix GAPFILL_ --only \
  --edit-row "PO_SYSTEM_PARAMETER.csv|ShortCode=<BU>|<FIELD>=<NEW>"
```
`--edit-row` copies the one existing row unchanged except FIELD and prints `FIELD 'OLD' -> 'NEW'`. VERIFIED (offline: the package was built; it was **not** imported).

## Step 3. Import (a person, with the BU owner's approval)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION --task-name "Configure Procurement Business Function" \
  --zip-file "<RUN>/payload/change.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_change" > "<RUN>/import_change.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import_change.out"
python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_change"
```
GUESS: success shows `Status: Completed successfully`, 1 row, 0 failed. Not tested.

## Step 4. Read back
Export again into `export_after` and compare with `compare_exports.py` (key = the CSV's key column): expect `RESULT: FAIL` with exactly `changed 1` (your row). GUESS (same pattern as the tested channel-settings and collaboration-messaging skills).

## Rules and limits
1. Never import as an agent test. A real change needs the BU owner's approval and a person to run it.
2. Change only the approved field; `--edit-row` keeps the rest exactly as exported.
3. Export checked on one environment, release 11.13.26.10.0.
