---
skill_id: "gosaas.gap-fills.common-features.manage-bu-document-sequences"
name: "Manage Business Unit Document Sequences: new business-unit sequence with one assignment (GoSaaS gap fill)"
description: "Create one new document sequence with determinant BUSINESS UNIT and assign it to one business unit for a TEST document sequence category, through FSCR's setup-task CSV export and FSM CSV import (ORA_FND_APP_DOCSEQ_BU + ORA_FND_APP_DOCSEQ_ASSIGNMENT_BU), then read it back by REST (documentSequences) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 09, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_FND_MANAGE_DOCUMENT_SEQUENCES_BU"
task_name: "Manage Business Unit Document Sequences"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories (a TEST category on a table that takes a business-unit determinant; also its generic helper scripts)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new document sequence and one assignment (business unit + TEST category). Documents are numbered by it only if they use that category, so a test category keeps it unused. It may not be deletable; plan as if it stays."
---

# Manage Business Unit Document Sequences (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file. It is the business-unit twin of the gap skills `manage-ledger-document-sequences` and `manage-legal-document-sequences`.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A business unit document sequence numbers documents per **business unit**: the sequence is defined for an application table, and an **assignment** ties it to a document sequence **category** and a business unit from a start date. Our environment had **no** business unit sequence before the test (VERIFIED, read-only export: 0 rows), so the table could not be copied from an existing row; Oracle accepted a sequence on the manufacturing work-order table `WIE_WORK_ORDERS_B` (application 10108) and shows its determinant as `BU` (VERIFIED). Use this skill to create a **new** sequence and **one** assignment.
**Safety:** assign it only to a **test category** that no real document uses (one you made with the gap skill `manage-docseq-categories`). A real category on a real business unit would change how real documents are numbered: never do that on a shared environment. Never change or end-date an existing sequence or assignment.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
SEQ     = new sequence Name, starting with PREFIX (VERIFIED with 18 characters)
CAT     = a TEST category code (Prerequisite 1), with its ApplicationId APP, ModuleId MODULE and TableName TABLE
BU      = the name of an existing business unit (Prerequisite 2); the CSV column is OrganizationCode
START   = start date, YYYY/MM/DD (if the brief gives none: the first day of the current year)
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
Do Step 2 (the export) first, then come back here: Prerequisites 1 and 3 read that export.

1. **A TEST category CAT on a table that takes a business-unit determinant.** After Step 2 run
   `python -I "<H>/inspect_export.py" "<RUN>/export_before/unz" --file ORA_FND_APP_DOCSEQ_BU.csv --cols TableName,ApplicationId,ModuleId`. If it lists a table, use that table. If the file is empty (as on our environment), use `WIE_WORK_ORDERS_B` (VERIFIED: accepted with determinant BU). Other tables were not tried (GUESS); a ledger table (`GL_JE_HEADERS`, `AP_INVOICES_ALL`) or the legal-entity table (`WSH_NEW_DELIVERIES`) belongs to another determinant, so do not use those.
   Then check you have a test category on that table, from the read-only export of task FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES (the Step 2 command with that task code and `--output-dir "<RUN>/cat_export"`, then unzip it the same way; file `FND_APP_DOCSEQ_CATEGORY.csv`, columns `Code, ApplicationId, ModuleId, TableName`): a row whose `Code` starts with PREFIX and whose `TableName` is that table. If there is none, make one with the gap skill `manage-docseq-categories` (its Step 3: take `ApplicationId`, `ModuleId` and `TableName` from an existing category row of that table) (VERIFIED: `GAPFILL_AB_B9_BC1` on `WIE_WORK_ORDERS_B` imported cleanly). APP, MODULE and TABLE in Step 3 are the category's own three values.
2. **BU exists:** `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource finBusinessUnitsLOV --q "BusinessUnitName='<BU>'" --fields BusinessUnitName --out "<RUN>/bu.json" --expect-count 1` (VERIFIED: the `BusinessUnitName` shown here is the value that `OrganizationCode` takes). If the person names no business unit, take the first one this resource lists without `--q`.
3. **CAT + BU has no open assignment yet** (one category per business unit can have only one assignment for a date range; for ledgers a second one fails with `FND-7020` UNIQUE-DATE OVERLAP, VERIFIED in the ledger skill; GUESS: the same here). After Step 2:
   `python -I -c "import csv,sys; [print(r['ORA_FND_APP_DOCSEQ_BU.Name'],r['StartDate'],r['EndDate']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_FND_APP_DOCSEQ_ASSIGNMENT_BU.csv',encoding='utf-8-sig')) if r['CategoryCode']==sys.argv[2] and r['OrganizationCode']==sys.argv[3]]" "<RUN>/export_before/unz" "<CAT>" "<BU>"` must print nothing. If it prints a row, pick another business unit (or make another test category); never end-date the existing assignment.
4. SEQ is free: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource documentSequences --q "Name='<SEQ>'" --fields Name --out "<RUN>/seq_before.json" --expect-absent` (VERIFIED in the ledger skill).

## Step 2. Read-only export (right before your import)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_FND_MANAGE_DOCUMENT_SEQUENCES_BU --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 2 CSV files + `ASM_SETUP_CSV_METADATA.xml` (VERIFIED, about 1 to 3 minutes; both files may be empty): `ORA_FND_APP_DOCSEQ_BU.csv` (17 columns: `Name, ApplicationId, AuditTableName, ..., InitialValue, ..., MessageFlag, ModuleId, StartDate, TableName, Type, ValidateTransactionDate`) and `ORA_FND_APP_DOCSEQ_ASSIGNMENT_BU.csv` (12 columns: `ORA_FND_APP_DOCSEQ_BU.Name, ApplicationId, CategoryCode, OrganizationCode, MethodCode, StartDate, ...`). If it stops with no ZIP, run it again into a new folder (read-only), up to 3 tries (VERIFIED: one export needed a second try).

## Step 3. Build the package (2 rows)
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name bu_seq_new.zip --prefix <PREFIX> \
  --key "ORA_FND_APP_DOCSEQ_BU.csv=Name" \
  --key "ORA_FND_APP_DOCSEQ_ASSIGNMENT_BU.csv=ORA_FND_APP_DOCSEQ_BU.Name,CategoryCode,OrganizationCode" \
  --prefix-col "ORA_FND_APP_DOCSEQ_BU.csv=Name" \
  --row "ORA_FND_APP_DOCSEQ_BU.csv|Name=<SEQ>|ApplicationId=<APP>|InitialValue=1|MessageFlag=N|ModuleId=<MODULE>|StartDate=<START>|TableName=<TABLE>|Type=A|ValidateTransactionDate=N" \
  --row "ORA_FND_APP_DOCSEQ_ASSIGNMENT_BU.csv|ORA_FND_APP_DOCSEQ_BU.Name=<SEQ>|ApplicationId=<APP>|CategoryCode=<CAT>|OrganizationCode=<BU>|StartDate=<START>"
```
- `Type=A` (automatic) worked (VERIFIED); gapless `G` was not tried here. Leave `AuditTableName` empty (VERIFIED, accepted). `ValidateTransactionDate` must be filled (required for ledger sequences, VERIFIED there; `N` accepted here, VERIFIED).
- `MethodCode` empty (as in every existing assignment, VERIFIED). Leave end dates and audit columns empty.
- Both rows go in the same ZIP: the assignment is a child of the sequence.

## Step 4. Import
**Approval.** The person must approve the environment, the task, SEQ, CAT and BU before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in a file in RUN.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_FND_MANAGE_DOCUMENT_SEQUENCES_BU --task-name "Manage Business Unit Document Sequences" \
  --zip-file "<RUN>/payload/bu_seq_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** (`Started setup task CSV import process: <id>`).
- Short summary of the log (counts and messages only):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Expected (VERIFIED, about 60 to 90 s): `A total of 2 rows were processed. 0 rows of them failed`, `Business Unit Document Sequence. Status: Completed successfully`, `Total Objects Failed: 0`.
- **Dropped connection after the process started:** the import still runs. **Do not import again.** Wait 2 minutes, then Step 5.
- Failed rows: copy the message, change one thing, new SEQ, retry; at most 3 tries. A refused row creates nothing: check with a new export first. `FND-7020`: see Prerequisite 3. `JBO-26041` at the insert: fill `CreatedBy`/`LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it). GUESS

## Step 5. Read back (the proof)
1. REST: `timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource documentSequences --q "Name='<SEQ>'" --fields Name,ApplicationId,Type,DeterminantType,ValidateTransactionDate --out "<RUN>/readback.json" --expect "Name=<SEQ>,DeterminantType=BU"` → `READBACK: PASS`. The business-unit determinant shows as `BU` (VERIFIED). Do not ask for `TableName` (HTTP 400) and always pass `--fields` (full rows hold user names).
2. Export again (Step 2 into `<RUN>/export_after`, unzip) and compare. **First check the after-export made a ZIP** (`ls "<RUN>/export_after"/*.zip`). If not (for example `ProcessCompletedFlag: False`), run the export again into a NEW folder (`export_after_try2`, ...), up to 3 tries, and compare against that folder: a compare against a missing folder prints a false `RESULT: FAIL` with "removed" rows (VERIFIED in a fresh test).
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_FND_APP_DOCSEQ_BU.csv=Name" \
  --key "ORA_FND_APP_DOCSEQ_ASSIGNMENT_BU.csv=ORA_FND_APP_DOCSEQ_BU.Name,CategoryCode,OrganizationCode" \
  --expect "ORA_FND_APP_DOCSEQ_BU.csv=<SEQ>" \
  --expect "ORA_FND_APP_DOCSEQ_ASSIGNMENT_BU.csv=<SEQ>,<CAT>,<BU>"
```
`RESULT: PASS` = only your sequence and assignment added, 0 removed, 0 changed (VERIFIED). The assignment row is the proof of the business-unit link.

## Rules and limits
1. New sequences only, assigned only to a TEST category. Never change, end-date or re-import an existing sequence or assignment.
2. Not tested: gapless (`G`) type, other tables, more than one assignment, `MethodCode` values.
3. Test records may stay for good. This skill never deletes.
4. Tested on one environment (release 11.13.26.10.0). Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for the other helpers and one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | What | Result |
|---|---|---|
| prerequisite | test category `GAPFILL_AB_B9_BC1` on `WIE_WORK_ORDERS_B` (application 10108) by the category skill (ProcessId 100004742441924) | 1 row processed, 0 failed |
| try 1 | `GAPFILL_AB_B9_BSQ1`, type A, assigned to `GAPFILL_AB_B9_BC1` for one existing business unit, from 2026/01/01 (ProcessId 100004742423977) | 2 rows processed, 0 failed; REST: 1 row, DeterminantType BU; export compare (before 0 rows): sequence 1, assignment 1 added, 0 changed: PASS |
