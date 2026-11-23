---
skill_id: "gosaas.gap-fills.common-features.manage-docseq-categories"
name: "Manage Document Sequence Categories (GoSaaS gap fill)"
description: "Create a new document sequence category on an application table through FSCR's setup-task CSV export and import (FND_APP_DOCSEQ_CATEGORY package), then read it back by REST (documentSequenceCategoriesLOV) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 3, 2026-11-20. Written and tested live on one test environment. NOT official FSCR."
tested_by_fresh_chat: "See gap_index.csv (fresh_claude_pass) and CHANGELOG.md"
layer: "pillar"
pillar: "Common"
offering: "Common Features"
task_code: "FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES"
task_name: "Manage Document Sequence Categories"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
inputs:
  - "fusion_environment_context"
  - "new_category_code_name_table"
outputs:
  - "csv_package_zip"
  - "import_process_log"
  - "rest_readback_json"
  - "export_compare_result"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import process that creates new document sequence categories. They may not be deletable; plan as if they stay."
required_privileges:
  - "Export Import Functional Setups User plus the task privileges for FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES, and read access to the documentSequenceCategoriesLOV REST resource"
reused_by:
  - "common-features/manage-conversion-rate-types (scripts)"
  - "common-features/manage-transaction-calendars (scripts)"
---

# Manage Document Sequence Categories (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's export and import scripts in place and does not edit any FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-20) · **FROM FSCR** = FSCR file · **FROM ORACLE DOCS** = link · **GUESS** = judgment, not tested.

## What this setup is
A document sequence category groups documents of one kind (for example one journal or invoice type) that are stored in one application table, so a document sequence can number them. Each category has a code, a name, an owning application and a table name. Categories are the first link in the chain: category, then document sequence, then sequence assignment (GUESS from the task list order; Oracle's "Document Sequences" help topic describes the chain).

## When to use
- Someone asks to create a **new** document sequence category for task `FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES`.
- Do **not** use it to change or remove existing categories. New records only.
- Note: General Ledger creates a document sequence category for each new journal category by itself (VERIFIED: the export holds one row per test journal category on `GL_JE_HEADERS`). For journal categories use the journal-categories gap skill, not this one.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties
          (in a downloaded pack it is often a folder named fscr-main INSIDE another fscr-main). Read only, never edit.
SKILL   = the folder of this SKILL.md (its scripts\ folder holds the helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix (GAPFILL_ in our tests). Code and name must start with it.
CODE    = new category code, e.g. GAPFILL_DSC_<something>: upper case, digits, _ ; max 30 characters
NAME    = display name; we used NAME = CODE (max 80 characters, GUESS from the screen)
TABLE   = an application table that existing categories already use (Step 3 shows them)
```
Pick a code that does not exist yet. Do not reuse names from the worked example at the end.

## Step 0. Run FSCR in place, safely
- Run FSCR scripts with their full path and `python -B` (no `__pycache__` inside FSCR).
- Always pass `--output-dir` under `RUN`, or the export writes inside `FSCR\project\...`.
- **Git Bash on Windows:** write paths as `E:/folder/...`, not `/e/folder/...` (Python turns `/e/...` into a stray `E:\e\...` folder). Set `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` (without the second one Git Bash rewrites `/fscmRestApi/...` arguments into Windows paths).
- Never print tokens, headers, the sign-in URL or the server address.

## Step 1. Sign in (only if needed)
1. Try Step 4's before-read first. If it says HTTP 401/403 or the token expired, sign in.
2. FROM FSCR `core/auth/fusion-oauth-authentication`: the values belong in `FSCR/core/auth/fusionEnv.properties` (environment, restBaseUrl, clientId, redirectUrl, scope). Then run in the background:
   ```bash
   cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600
   ```
   A person signs in on the browser tab; the script prints `Login complete for standard.` Never read or type credentials. If the browser cannot reach the 127.0.0.1 callback, stop and ask the person.
3. Sign-in time is waiting time, not task time.

## Step 2. Read-only export (layout + codes already in use)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
- Expect 2 files: `ASM_SETUP_CSV_METADATA.xml` and `FND_APP_DOCSEQ_CATEGORY.csv` with 11 columns: `Code, ApplicationId, CreatedBy, CreationDate, Description, LastUpdateDate, LastUpdateLogin, LastUpdatedBy, ModuleId, Name, TableName`. VERIFIED. About 20 to 60 seconds.
- The export holds user-created categories only (not every seeded category); row counts grow with every test. VERIFIED (69 rows on 2026-11-18, 70 before our test).
- If the export fails or has no `FND_APP_DOCSEQ_CATEGORY.csv`: **stop**, note it, do not import.

## Step 3. Pick a valid table (from the export, never guessed)
A category needs a real application table, and `ApplicationId` and `ModuleId` that belong to it. Take all three from an existing row:
```bash
python -I "<SKILL>/scripts/inspect_export.py" "<RUN>/export_before/unz" --file FND_APP_DOCSEQ_CATEGORY.csv --cols TableName,ApplicationId,ModuleId
```
It lists each table with its ApplicationId and ModuleId and how many categories use it. Pick one line and copy its three values. VERIFIED: a General Ledger journal table worked; tables from other applications were listed but not tried (GUESS: they work the same way). Prefer a table whose application you are allowed to touch.
- If the export has no rows, you cannot get a valid ModuleId this way: stop and ask (GUESS: an empty `ModuleId` may fail).

## Step 4. Before-read by REST (read-only)
```bash
python -B "<SKILL>/scripts/rest_read.py" --fscr "<FSCR>" --resource documentSequenceCategoriesLOV \
  --q "Code='<CODE>'" --fields Code,Name,ApplicationShortName,Description \
  --out "<RUN>/readback_before.json" --expect-absent
```
Want `0 row(s)` and `READBACK: PASS`. If a row comes back, pick another code. Exit 2 / HTTP 401/403 = sign-in or privilege problem, not "absent". Run without `-I`. The LOV covers seeded categories too, so this check is wider than the export.

## Step 5. Build a package with only the new category
```bash
python -I "<SKILL>/scripts/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name docseq_cat_new.zip --prefix <PREFIX> \
  --key "FND_APP_DOCSEQ_CATEGORY.csv=Code" --prefix-col "FND_APP_DOCSEQ_CATEGORY.csv=Code,Name" \
  --max-len "Code=30" --max-len "Name=80" \
  --row "FND_APP_DOCSEQ_CATEGORY.csv|Code=<CODE>|Name=<NAME>|Description=<text>|ApplicationId=<app id>|ModuleId=<module id>|TableName=<TABLE>"
```
- Fill only `Code`, `Name`, `Description`, `ApplicationId`, `ModuleId`, `TableName`; leave the audit columns empty. VERIFIED (imported cleanly).
- The helper copies the header and metadata XML from the export, quotes every field, and stops if the code is already in the export (importing it would **update** that row), lacks the prefix or is too long.
- One `--row` per category. We created one; GUESS: several work the same way.

## Step 6. Import
**Approval.** The person must approve the environment, the task and the exact codes before the import. If their brief already names all three and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES --task-name "Manage Document Sequence Categories" \
  --zip-file "<RUN>/payload/docseq_cat_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 40 seconds. VERIFIED. The script may print `StatusCode: (unknown)` even on success; the real result is only in `<RUN>/import_result/*_process_log.txt` (one long line with literal `\r\n`). Read it with:
  `python -I -c "import sys; print(open(sys.argv[1],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<log file>"`
- Success: `Business object: Application Document Sequence Category. Status: Completed successfully.`, `A total of N rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`. VERIFIED
- If it says the process is not complete yet, keep the ProcessId and use FSCR's `get_setup_task_csv_import_result.py`; do not import twice. If rows failed, copy the error, change one thing, retry at most 3 times.

## Step 7. Read back two ways
**A. REST:**
```bash
python -B "<SKILL>/scripts/rest_read.py" --fscr "<FSCR>" --resource documentSequenceCategoriesLOV \
  --q "Code='<CODE>'" --fields Code,Name,ApplicationShortName,Description \
  --out "<RUN>/readback_after.json" --expect "Code=<CODE>,Name=<NAME>" --expect-count 1
```
`READBACK: PASS` = exactly one row with your code and name. The LOV shows the application short name, not the table (the table is checked in B). VERIFIED

**B. Second export and compare (offline):** repeat Step 2 with `--output-dir "<RUN>/export_after"` (unzip the same way), then
```bash
python -I "<SKILL>/scripts/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_DOCSEQ_CATEGORY.csv=Code" --expect "FND_APP_DOCSEQ_CATEGORY.csv=<CODE>" --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your code was added, none removed, no existing row changed. `added_rows.csv` shows the table name Oracle stored. VERIFIED

**Evidence (optional):** `python -B "<SKILL>/scripts/render_readback.py" --json <readback json> --title "..." --png <file.png>` draws a read-back as an image with no secrets (needs Pillow).

## Rules and limits
1. **New records only.** Never import a full export: a matching `Code` would update that category.
2. **Keep both files** in the package, metadata XML unchanged.
3. **Codes:** upper case, digits, `_`, max 30 characters (GUESS from the underlying column; 14 characters tried). Existing user rows also contain spaces and mixed case, so Oracle accepts more, but keep it simple.
4. **Test records may stay for good.** This skill never deletes. Record every created category in your change log.
5. **A category alone numbers nothing.** It only becomes active once a document sequence is assigned to it (task Manage Document Sequences). Our test categories have no sequence.
6. **Tested on one environment** (release 11.13.26.10.0). Other releases are untested.
7. **Python flags.** `-B` and no `-I` for FSCR scripts, `rest_read.py` and `render_readback.py`; `-I` for `inspect_export.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the unzip one-liner.

## Worked example (VERIFIED, 2026-11-20). Do not reuse this code; it now exists.
| Step | Result |
|---|---|
| Export before | 70 rows, 6 tables; 40 s |
| Before-read | `GAPFILL_DSC_T1`: 0 rows, PASS |
| New record | `GAPFILL_DSC_T1` (name = code) on the General Ledger journal header table, ApplicationId and ModuleId copied from an existing row of that table |
| Import | 1 attempt, 38 s: 1 row processed, 0 failed |
| REST read-back | 1 row, code, name and application GL match: PASS |
| Export after + compare | 71 rows; added 1, removed 0, changed 0: PASS |
