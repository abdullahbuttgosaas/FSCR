---
skill_id: "gosaas.gap-fills.procurement.manage-contract-line-types"
name: "Manage Contract Line Types (GoSaaS gap fill)"
description: "Create a new enterprise contract line type based on an existing line type source, through FSCR's setup-task CSV export and import, then prove it with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 01, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "OKC_MANAGE_CONTRACT_LINE_TYPES"
task_name: "Manage Contract Line Types"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.3.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only CSV exports; one CSV import that creates one new contract line type. Plan as if it stays (this skill never deletes)."
---

# Manage Contract Line Types (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A contract line type is a kind of line users can add to an enterprise contract (for example "Free-form" or "Item" on a purchase contract). Every line type is based on a **line type source** (`SourceCode`, for example `USER_FREE_FORM_BUY`) and a source class (`SourceCodeClass`, for example `BUY`, `PROJECT`, `SERVICE`).
Use it to create a **new** line type. Do not use it to change an existing line type.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\ (build_csv_package.py, compare_exports.py)
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
NAME   = new line type name, PREFIX + short name (e.g. GAPFILL_AB_LT1)
LTC    = new LineTypeCode: 32 upper-case letters/digits, made fresh (Step 2)
SRC    = an existing SourceCode and its SourceCodeClass, taken from the export (Step 1)
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
1. A valid line type source. It must be one of the `SourceCode` values already in the export (the seeded line types each show one). VERIFIED: a new, made-up SourceCode is refused with `OKC_SETUP_INVALID_LINE_SOURCE: You must enter a valid line type source` (nothing created). Use the `SourceCodeClass` shown on the same export row.

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code OKC_MANAGE_CONTRACT_LINE_TYPES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys; [print(r[2], r[3], '|', r[5]) for r in list(csv.reader(open(sys.argv[1],encoding='utf-8')))[1:]]" "<RUN>/export_before/unz/OKC_LINE_TYPE.csv"
```
Expect 2 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml` and `OKC_LINE_TYPE.csv` with columns `LineTypeCode, ParentLineTypeId, SourceCode, SourceCodeClass, RecursiveYn, Name, Description, CleType`. It lists all line types (13 seeded ones in our test plus every earlier test type, so your count is higher). The last command prints SourceCode, SourceCodeClass and Name of each. Pick SRC (we used `USER_FREE_FORM_BUY` / `BUY`, the purchasing "Free-form" source). If NAME is already in the list, pick another name.

## Step 2. Build the row (new line type only)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
[ -f "<RUN>/ltc.txt" ] || python -I -c "import uuid; print(uuid.uuid4().hex.upper())" > "<RUN>/ltc.txt"
LTC=$(cat "<RUN>/ltc.txt")
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key OKC_LINE_TYPE.csv=Name --new OKC_LINE_TYPE.csv=LineTypeCode \
  --row "OKC_LINE_TYPE.csv|LineTypeCode=$LTC|SourceCode=<SRC code>|SourceCodeClass=<SRC class>|RecursiveYn=N|Name=<NAME>|Description=<text>"
```
- `LineTypeCode` is the key of a line type: it must be **new** (a code already in the export would update that line type). The seeded codes are 32-character hex strings; a fresh random one of the same shape is safe. VERIFIED (we used a 32-character upper-case code; Oracle kept it as given).
- Leave `ParentLineTypeId` and `CleType` empty; `RecursiveYn=N`. VERIFIED
- The builder copies the metadata XML unchanged and stops if NAME lacks the prefix or NAME / LTC is already in the export.

## Step 3. Import
Approval: the person must approve the environment, the task and NAME before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code OKC_MANAGE_CONTRACT_LINE_TYPES --task-name "Manage Contract Line Types" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
- Keep the ProcessId. `StatusCode: (unknown)` is normal; read the result only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"` (never cat/grep the log: it holds a user name). Success (VERIFIED): `Business object: Contract Line Type. Status: Completed successfully`, `1 rows were processed. 0 rows of them failed`.
- A dropped connection after the ProcessId: never import again; fetch and read the log as the shell section says (recovered_process_log.txt).

## Step 4. Read back (second export + compare)
Repeat Step 1 into `<RUN>/export_after`, then:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key OKC_LINE_TYPE.csv=Name --expect OKC_LINE_TYPE.csv=<NAME>
```
`RESULT: PASS` = only your line type was added, nothing removed or changed. VERIFIED. If it says a folder has no export, the after-export made no ZIP: export again.

## Rules and limits
1. New records only; a row with an existing LineTypeCode would update that line type.
2. Only existing line type sources are accepted (Prerequisite 1).
3. Name: we used 17 characters. GUESS: maximum 80 (translatable name).
4. Test line types stay (no delete). They appear in the line type list of contracts whose class matches (GUESS).
5. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 13 seeded line types |
| Try 1 | `GAPFILL_AB_B1_LT1` with a made-up SourceCode: ProcessId 100004744392804, refused `OKC_SETUP_INVALID_LINE_SOURCE`, nothing created |
| Try 2 | `GAPFILL_AB_B1_LT2`, source `USER_FREE_FORM_BUY` / `BUY`: ProcessId 100004744392822, 1 processed, 0 failed |
| Export after + compare | 14 line types; added 1, removed 0, changed 0: PASS |
