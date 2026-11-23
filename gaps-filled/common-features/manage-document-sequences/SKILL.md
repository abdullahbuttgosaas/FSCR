---
skill_id: "gosaas.gap-fills.common-features.manage-document-sequences"
name: "Manage Document Sequences (GoSaaS gap fill)"
description: "Create a new document sequence (without an assignment) through FSCR's setup-task CSV export and import (FND_APP_DOCSEQ package), then read it back by REST (documentSequences) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 2, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_DOCUMENT_SEQUENCES"
task_name: "Manage Document Sequences"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
  - "FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES only if you add an assignment (not tested)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new document sequence. Without an assignment it numbers no document. It may not be deletable; plan as if it stays."
---

# Manage Document Sequences (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file. It uses the generic helpers of the gap skill `manage-docseq-categories`.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
A document sequence gives documents (journals, invoices, customer accounts...) a unique number. A sequence has a name, an application, the table of the documents it numbers, a type (`A` automatic, `G` gapless, `M` manual), an initial value and a start date. It does nothing until an **assignment** links it to a document sequence category (and, for some categories, a ledger, legal entity or business unit). This skill creates the **sequence only**. An assignment changes how real documents are numbered, so it is not part of the test.

## When to use
- Someone asks to create a **new** document sequence for task `FND_MANAGE_DOCUMENT_SEQUENCES`.
- Do **not** use it to change existing sequences or assignments. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
NAME    = new sequence Name, upper case letters, digits and _, starting with PREFIX (max 30, GUESS)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (not `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads (an expired token makes them hang silently). Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_DOCUMENT_SEQUENCES --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz" --file FND_APP_DOCSEQ.csv --cols Name,ApplicationId,ModuleId,TableName,Type
```
Expect 3 files (VERIFIED, about 60 s; counts differ per environment):
- `FND_APP_DOCSEQ.csv` (16 columns): `Name, ApplicationId, AuditTableName, CreatedBy, CreationDate, EndDate, InitialValue, LastUpdateDate, LastUpdateLogin, LastUpdatedBy, MessageFlag, ModuleId, StartDate, TableName, Type, ValidateTransactionDate`
- `ORA_FND_APP_DOCSEQ_ASSIGNMENT.csv` (12): `FND_APP_DOCSEQ.Name, ApplicationId, CategoryCode, DeterminantValue, MethodCode, StartDate, ...`
- `ASM_SETUP_CSV_METADATA.xml` (scope `mode=search`). The export holds the sequences of all applications. If it fails or lacks these files: **stop**.

## Step 3. Choose the application and check the name
1. **Application, module and table.** A sequence belongs to the application whose documents it numbers. Take `ApplicationId`, `ModuleId` and `TableName` **together from one existing sequence row of that application** in the export (printed in Step 2). Never guess them. For a test that assigns nothing, any existing automatic (`Type A`) row with a `TableName` will do (VERIFIED); prefer a row that is **not** an earlier test row (its name does not start with a test prefix). If the person names a document sequence category instead, the category's table and application are in the categories export (see `manage-docseq-categories`).
2. **Name is free** (REST):
   ```bash
   timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource documentSequences --q "Name='<NAME>'" \
     --fields Name --out "<RUN>/readback_before.json" --expect-absent
   ```
   Want `0 row(s)`, `READBACK: PASS`. Exit 2 = sign-in or privilege problem, not "absent".

## Step 4. Build a package with only the new sequence
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name docseq_new.zip --prefix <PREFIX> \
  --key "FND_APP_DOCSEQ.csv=Name" \
  --key "ORA_FND_APP_DOCSEQ_ASSIGNMENT.csv=FND_APP_DOCSEQ.Name,ApplicationId,CategoryCode,DeterminantValue,MethodCode,StartDate" \
  --prefix-col "FND_APP_DOCSEQ.csv=Name" --max-len "Name=30" \
  --row "FND_APP_DOCSEQ.csv|Name=<NAME>|ApplicationId=<APP>|ModuleId=<MODULE>|TableName=<TABLE>|Type=A|InitialValue=1|StartDate=<yyyy/mm/dd>|MessageFlag=N|ValidateTransactionDate=N"
```
- The assignment file goes in with its header only (no assignment). VERIFIED
- Dates `yyyy/mm/dd`. Leave `EndDate`, `AuditTableName` and the audit columns empty. VERIFIED
- The helper stops if NAME is already in the export (importing it would **update** that sequence), lacks the prefix, or is too long.

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact NAME before the import. If their brief names all three and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_DOCUMENT_SEQUENCES --task-name "Manage Document Sequences" \
  --zip-file "<RUN>/payload/docseq_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 25 s. `StatusCode: (unknown)` is normal; the result is only in `<RUN>/import_result/*_process_log.txt` (one line with literal `\r\n`). Read it with
  `python -I -c "import sys,glob; print(open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<RUN>/import_result"`
- Success (VERIFIED): `Business object: Application Document Sequence. Status: Completed successfully`, `DocumentSequencesLoaderSD.xml ... A total of 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`.
- **`0 rows were processed` is a failure** even when the status says "Completed successfully". Rows failed: copy the error, change one thing, retry at most 3 times; never import twice while one is running.

## Step 6. Read back two ways
**A. REST:**
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource documentSequences --q "Name='<NAME>'" \
  --fields Name,ApplicationShortName,Type,InitialValue,StartDate,MessageFlag \
  --out "<RUN>/readback_after.json" --expect "Name=<NAME>,Type=A" --expect-count 1
```
`READBACK: PASS` = exactly one sequence with your name and type. Always pass `--fields` (the full row holds user names). VERIFIED

**B. Second export and compare:** repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_DOCSEQ.csv=Name" \
  --key "ORA_FND_APP_DOCSEQ_ASSIGNMENT.csv=FND_APP_DOCSEQ.Name,ApplicationId,CategoryCode,DeterminantValue,MethodCode,StartDate" \
  --expect "FND_APP_DOCSEQ.csv=<NAME>" --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your sequence was added, no assignment, nothing removed or changed. If someone else imported sequences between your two exports, extra added rows appear: then judge your own row (added) plus `removed 0` and `changed 0`, and report the extra rows.

## Rules and limits
1. New records only; never import a full export.
2. Keep all 3 files, metadata XML unchanged; the assignment file stays header-only.
3. **No assignment in a test.** An assignment starts numbering real documents of that category. Adding one (`ORA_FND_APP_DOCSEQ_ASSIGNMENT.csv` row: sequence name, ApplicationId, CategoryCode, DeterminantValue, MethodCode, StartDate) is **not tested** and needs the person's explicit approval.
4. Test records may stay for good. This skill never deletes. Record every created sequence.
5. Not tested: gapless (`G`) and manual types, audit tables, end dates.
6. Tested on one environment (release 11.13.26.10.0).
7. Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for `inspect_export.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-23). Do not reuse this name; it now exists.
| Step | Result |
|---|---|
| Export before | 35 sequences, 36 assignments; 64 s (counts grow with every test) |
| Application | copied from an existing automatic sequence row that has a table |
| New record | `GAPFILL_AB_DS1`, type A, initial value 1, no assignment |
| Import | 1 attempt, 24 s: 1 row processed, 0 failed |
| REST read-back | 1 row, name and type match: PASS |
| Export after + compare | 36 sequences, 36 assignments; added 1, removed 0, changed 0: PASS |
