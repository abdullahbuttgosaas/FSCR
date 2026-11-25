---
skill_id: "gosaas.gap-fills.common-features.manage-ledger-document-sequences"
name: "Manage Ledger Document Sequences: new ledger-level sequence with one assignment (GoSaaS gap fill)"
description: "Create one new document sequence with determinant LEDGER and assign it to one ledger for a TEST document sequence category, through FSCR's setup-task CSV export and FSM CSV import (FND_APP_DOCSEQ_LEDGER + ORA_FND_APP_DOCSEQ_ASSIGNMENT_LEDGER), then read it back by REST (documentSequences) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 08, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_FND_MANAGE_DOCUMENT_SEQUENCES_LEDGER"
task_name: "Manage Ledger Document Sequences"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories (a TEST category; also its generic helper scripts)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new document sequence and one assignment (ledger + TEST category). Documents are numbered by it only if they use that category, so a test category keeps it unused. It may not be deletable; plan as if it stays."
---

# Manage Ledger Document Sequences (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A ledger document sequence numbers documents (for example journals or payables invoices) per **ledger**: the sequence is defined for an application table, and an **assignment** ties it to a document sequence **category** and a ledger from a start date. Use this skill to create a **new** sequence and **one** assignment. 
**Safety:** assign it only to a **test category** that no real document uses (a category you made with the gap skill `manage-docseq-categories`, which is not a journal category or a document type). An assignment for a real category on a real ledger would change how real documents are numbered: do not do that on a shared environment. Never change or end-date an existing assignment.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
SEQ     = new sequence Name, starting with PREFIX (VERIFIED with 18 characters)
CAT     = a TEST document sequence category code (Prerequisite 1), with its ApplicationId APP, ModuleId MODULE and TableName TABLE
LEDGER  = the name of an existing ledger (Prerequisite 2)
AUDIT   = the audit table of TABLE's application (General Ledger: GL_DOC_SEQUENCE_AUDIT, VERIFIED)
START   = start date, YYYY/MM/DD (if the brief gives none: the first day of the current year, as in the worked example)
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
1. **A TEST category CAT** on a table whose sequences use the LEDGER determinant (VERIFIED: the General Ledger journal header table `GL_JE_HEADERS`, application 101). Check it exists, and read APP, MODULE and TABLE, from the category export of the gap skill `manage-docseq-categories` (task FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES, read-only export, file `FND_APP_DOCSEQ_CATEGORY.csv`, columns `Code, ApplicationId, ModuleId, TableName`). If you have no test category, make one with that skill first (once). Never use a category that real documents use (for General Ledger: a journal category creates a category of the same code; do not use those).
2. **LEDGER** exists: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource ledgersLOV --q "Name='<LEDGER>'" --fields Name,LedgerCategoryCode --out "<RUN>/ledger.json" --expect-count 1` (VERIFIED).
3. **CAT + LEDGER has no open assignment yet.** One category on one ledger can have only one assignment for a date range: a second one fails with `FND-7020` "UNIQUE-DATE OVERLAP", 0 rows processed, nothing created (VERIFIED in our fresh test). After Step 2, check the before-export: `python -I -c "import csv,sys; [print(r['FND_APP_DOCSEQ_LEDGER.Name'],r['StartDate'],r['EndDate']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_FND_APP_DOCSEQ_ASSIGNMENT_LEDGER.csv',encoding='utf-8-sig')) if r['CategoryCode']==sys.argv[2] and r['DeterminantValueLedgerName']==sys.argv[3]]" "<RUN>/export_before/unz" "<CAT>" "<LEDGER>"` must print nothing. If it prints a row, pick another ledger (or make another test category); never end-date the existing assignment.
4. SEQ is free: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource documentSequences --q "Name='<SEQ>'" --fields Name --out "<RUN>/seq_before.json" --expect-absent` (VERIFIED).

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_FND_MANAGE_DOCUMENT_SEQUENCES_LEDGER --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 3 files (VERIFIED, about 50 s): `FND_APP_DOCSEQ_LEDGER.csv` (17 columns: `Name, ApplicationId, AuditTableName, ..., ModuleId, StartDate, TableName, Type, ValidateTransactionDate`), `ORA_FND_APP_DOCSEQ_ASSIGNMENT_LEDGER.csv` (12 columns: `FND_APP_DOCSEQ_LEDGER.Name, ApplicationId, CategoryCode, DeterminantValueLedgerName, MethodCode, StartDate, ...`) and `ASM_SETUP_CSV_METADATA.xml`. If it stops with no ZIP (for example a read time-out), run it again into a new folder (read-only), up to 3 tries.

## Step 3. Build the package (2 rows)
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name ledger_seq_new.zip --prefix <PREFIX> \
  --key "FND_APP_DOCSEQ_LEDGER.csv=Name" \
  --key "ORA_FND_APP_DOCSEQ_ASSIGNMENT_LEDGER.csv=FND_APP_DOCSEQ_LEDGER.Name,CategoryCode,DeterminantValueLedgerName" \
  --prefix-col "FND_APP_DOCSEQ_LEDGER.csv=Name" \
  --row "FND_APP_DOCSEQ_LEDGER.csv|Name=<SEQ>|ApplicationId=<APP>|AuditTableName=<AUDIT>|InitialValue=1|MessageFlag=N|ModuleId=<MODULE>|StartDate=<START>|TableName=<TABLE>|Type=A|ValidateTransactionDate=N" \
  --row "ORA_FND_APP_DOCSEQ_ASSIGNMENT_LEDGER.csv|FND_APP_DOCSEQ_LEDGER.Name=<SEQ>|ApplicationId=<APP>|CategoryCode=<CAT>|DeterminantValueLedgerName=<LEDGER>|StartDate=<START>"
```
- **`ValidateTransactionDate` is required** for a new sequence (VERIFIED: without it, try 1 failed with `JBO-27014: Attribute ValidateTransactionDate in DocumentSequencesEO is required`, nothing created). `N` worked.
- `Type=A` = automatic numbering (VERIFIED). `G` (gapless) is what the existing payables rows use; not tried.
- APP, MODULE and TABLE come from CAT's own category row (they must belong together). AUDIT for General Ledger is `GL_DOC_SEQUENCE_AUDIT` (VERIFIED: accepted, and REST shows it); for payables rows the export shows `AP_DOC_SEQUENCE_AUDIT`.
- `MethodCode` empty: every existing assignment has it empty (VERIFIED). Leave the end date and audit columns empty.
- The assignment row is a child of the sequence row: both go in the same ZIP (they do, from this one build).

## Step 4. Import
**Approval.** The person must approve the environment, the task, SEQ, CAT and LEDGER before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_FND_MANAGE_DOCUMENT_SEQUENCES_LEDGER --task-name "Manage Ledger Document Sequences" \
  --zip-file "<RUN>/payload/ledger_seq_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`).
- Short summary of the log (counts and messages only):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Expected (VERIFIED, about 25 s): `A total of 2 rows were processed. 0 rows of them failed`, `Ledger Document Sequence ... Completed successfully`, `Total Objects Failed: 0`.
- **Dropped connection after the process started:** the import still runs. **Do not import again.** Wait 2 minutes, then Step 5.
- `FND-7020` "UNIQUE-DATE OVERLAP": CAT + LEDGER already has an open assignment (Prerequisite 3). A new SEQ does not help: change the ledger or the test category.
- Other failed rows: copy the message, change one thing, new SEQ, retry; at most 3 tries. A refused row creates nothing: check with a new export first. `JBO-26041` at the insert: fill `CreatedBy`/`LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it). GUESS

## Step 5. Read back (the proof)
1. REST: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource documentSequences --q "Name='<SEQ>'" --fields Name,ApplicationId,Type,DeterminantType,ValidateTransactionDate --out "<RUN>/readback.json" --expect "Name=<SEQ>,DeterminantType=LEDGER"` → `READBACK: PASS` (VERIFIED). Do not ask for `TableName` in `--fields`: the resource rejects it (HTTP 400, VERIFIED). Without `--fields` the output holds user names: always pass `--fields`.
2. Export again (Step 2 into `<RUN>/export_after`, unzip) and compare:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_DOCSEQ_LEDGER.csv=Name" \
  --key "ORA_FND_APP_DOCSEQ_ASSIGNMENT_LEDGER.csv=FND_APP_DOCSEQ_LEDGER.Name,CategoryCode,DeterminantValueLedgerName" \
  --expect "FND_APP_DOCSEQ_LEDGER.csv=<SEQ>" \
  --expect "ORA_FND_APP_DOCSEQ_ASSIGNMENT_LEDGER.csv=<SEQ>,<CAT>,<LEDGER>"
```
`RESULT: PASS` = only your sequence and assignment added (VERIFIED). The assignment is the proof that the ledger link was made (REST `documentSequences` shows only the sequence).

## Rules and limits
1. New sequences only, assigned only to a TEST category. Never change, end-date or re-import an existing sequence or assignment.
2. Not tested: gapless type, other applications' tables, more than one assignment, `MethodCode` values.
3. Test records may stay for good. This skill never deletes.
4. Tested on one environment (release 11.13.26.10.0). Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for the other helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | What | Result |
|---|---|---|
| 1 | `GAPFILL_AB_B8_LSQ1` without `ValidateTransactionDate` (ProcessId 100004742423686) | refused: `JBO-27014 ... ValidateTransactionDate ... is required`; new export: 0 GAPFILL rows, nothing created |
| 2 | `GAPFILL_AB_B8_LSQ2`, `ValidateTransactionDate=N`, General Ledger journal header table, assigned to test category `GAPFILL_DSC_T1` on one existing primary ledger (ProcessId 100004743403613) | 2 rows processed, 0 failed; REST: 1 row, DeterminantType LEDGER; export compare: sequence 1, assignment 1 added: PASS |
| fresh test | `GAPFILL_AB_B8_LSQ3F`, same category and same ledger (ProcessId 100004742423742) | refused: `FND-7020` UNIQUE-DATE OVERLAP (the pair already had LSQ2's open assignment); 0 rows, nothing created. Led to Prerequisite 3 |
| re-test | `GAPFILL_AB_B8_LSQ4R`, same category, another primary ledger with no assignment for it (ProcessId 100004742423771) | 2 rows processed, 0 failed; REST read-back PASS; export compare: sequence 1, assignment 1 added: PASS |
