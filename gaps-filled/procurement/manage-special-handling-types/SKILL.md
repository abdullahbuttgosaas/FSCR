---
skill_id: "gosaas.gap-fills.procurement.manage-special-handling-types"
name: "Manage Special Handling Types (GoSaaS gap fill)"
description: "Create a new purchasing special handling type (with its US translation row) through FSCR's setup-task CSV export and import, then prove it with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 01, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_PO_MANAGE_SPECIAL_HANDLING_TYPES"
task_name: "Manage Special Handling Types"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.3.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only CSV exports; one CSV import that creates one new special handling type. Plan as if it stays (this skill never deletes)."
---

# Manage Special Handling Types (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A special handling type marks purchasing documents that follow a special flow (the seeded one is "Bill Only"). Each type has a code, a name, a description, an enabled flag, four Y/N behaviour flags and, optionally, a header and a line descriptive flexfield context.
Use it to create a **new** special handling type. Do not use it to change or disable an existing one (a row with an existing code would update it).

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\ (build_csv_package.py, compare_exports.py)
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE   = new type code, PREFIX + short name, upper case, digits, _ (e.g. GAPFILL_AB_SH1)
NAME   = display name (we used the code with spaces; GUESS max 80); DESC = a description (GUESS max 240)
```
Pick a CODE that does not exist yet. Do not reuse names from the worked example.

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
  `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). A sign-in lasts about an hour. VERIFIED
- Never print tokens, the server address or user names.

## Prerequisites
None. VERIFIED: a type with both flexfield context codes empty was accepted. (If you want contexts, they must already exist in the purchasing special handling flexfields: GUESS, not tested.)

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_PO_MANAGE_SPECIAL_HANDLING_TYPES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 3 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml`, `ORA_PO_SPECIAL_HANDLING.csv` (16 columns), `ORA_PO_SPECIAL_HANDLING_TRANSLATION.csv` (11 columns). The export holds every type (seeded `ORA_PO_BILL_ONLY` + any test types). If CODE is in it, pick another code. If the export makes no ZIP, run it again into a new folder (up to 3 times); do not import without it.

## Step 2. Build rows (new type only)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_PO_SPECIAL_HANDLING.csv=SpecialHandlingTypeCode \
  --key ORA_PO_SPECIAL_HANDLING_TRANSLATION.csv=ORA_PO_SPECIAL_HANDLING.SpecialHandlingTypeCode \
  --row "ORA_PO_SPECIAL_HANDLING.csv|SpecialHandlingTypeCode=<CODE>|SpecialHandlingType=<NAME>|Description=<DESC>|EnabledFlag=Y|AutoCreateReceiptFlag=N|NegotiatedFlag=N|RequiresSingleSupplierFlag=N|PreventAutoSubmitFlag=N" \
  --row "ORA_PO_SPECIAL_HANDLING_TRANSLATION.csv|ORA_PO_SPECIAL_HANDLING.SpecialHandlingTypeCode=<CODE>|SpecialHandlingType=<NAME>|Description=<DESC>|Language=US|SourceLang=US"
```
- Leave `SpecialHandlingTypeId`, both context codes and all audit columns empty. VERIFIED (Oracle makes the id).
- The builder copies the metadata XML unchanged and stops if CODE lacks the prefix or is already in the export.
- `Language`/`SourceLang` = `US` is the session language of our test. GUESS: use your installed base language if it is not US.

## Step 3. Import
Approval: the person must approve the environment, the task and CODE before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_PO_MANAGE_SPECIAL_HANDLING_TYPES --task-name "Manage Special Handling Types" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
- Write down the ProcessId (`Started setup task CSV import process: <n>`); it is the only key to the full log.
- The script prints `StatusCode: (unknown)` even on success. read the result only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"` (never cat/grep the log: it holds a user name). Success (VERIFIED): `Business object: Special Handling Type. Status: Completed successfully` and `A total of 1 rows were processed. 0 rows of them failed` (the log counts only the top object; the translation row is proven by Step 4).
- A dropped connection after the ProcessId: never import again; fetch and read the log as the shell section says (recovered_process_log.txt).

## Step 4. Read back (second export + compare)
Repeat Step 1 with `--output-dir "<RUN>/export_after"` (unzip it the same way), then:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_PO_SPECIAL_HANDLING.csv=SpecialHandlingTypeCode \
  --key ORA_PO_SPECIAL_HANDLING_TRANSLATION.csv=ORA_PO_SPECIAL_HANDLING.SpecialHandlingTypeCode+Language \
  --expect ORA_PO_SPECIAL_HANDLING.csv=<CODE>
```
`RESULT: PASS` = your type and its translation row were added, nothing removed, no existing row changed (audit columns ignored). VERIFIED. If it says there is no export in a folder, the after-export made no ZIP: run it again; do not treat that as a failure of the import.
GUESS: no public REST resource for special handling types was found; the export is the read-back.

## Rules and limits
1. New records only; never import a full export.
2. Keep all 3 files in the package; metadata XML unchanged.
3. Code: upper case letters, digits, `_`; we used 17 characters. GUESS: maximum 30.
4. Test types stay (no delete). Record every code you create.
5. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 1 type (`ORA_PO_BILL_ONLY`), 1 translation |
| New type | `GAPFILL_AB_B1_SH1`, flags N, enabled Y, no contexts |
| Import | ProcessId 100004743406576: 1 row processed, 0 failed |
| Export after + compare | 2 types, 2 translations; added 1 + 1, removed 0, changed 0: PASS. Oracle gave it a new SpecialHandlingTypeId. |
