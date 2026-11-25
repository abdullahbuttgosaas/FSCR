---
skill_id: "gosaas.gap-fills.procurement.manage-compliance-checklist-questions"
name: "Manage Compliance Checklist Questions (GoSaaS gap fill)"
description: "Create a new compliance checklist question (text entry, with its US translation) through FSCR's setup-task CSV export and import, then prove it with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 03, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_PO_COMPLIANCE_CHECKLIST_QUESTIONS"
task_name: "Manage Compliance Checklist Questions"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only CSV exports; one CSV import that creates one new checklist question. Plan as if it stays (this skill never deletes)."
---

# Manage Compliance Checklist Questions (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A compliance checklist question is asked inside a checklist section (task `ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS`). Use this skill to create a **new** question with a text answer. Do not use it to change an existing one.
Oracle stores it as a supplier qualification question with usage `ORA_CHECKLIST`. VERIFIED

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
NAME   = the new question's internal name, PREFIX + short name (e.g. GAPFILL_AB_Q1)
TEXT   = the question text
```
Pick names that do not exist yet. Do not reuse names from the worked example.

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` (Git Bash otherwise rewrites values that start with `/`). VERIFIED
- Shell variables do not survive between tool calls: keep values in files under `RUN`.
- Save every FSCR script's output to a file (`> "<RUN>/<step>.out" 2>&1`) and print only the lines you need: error lines can hold the server address.
- Never read the import log with cat, sed or grep (it holds a user name and the environment name). Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/<import folder>"`: it prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. The ProcessId: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/<import>.out"`.
- Never print whole export rows: owner columns (`ListName...`, `EmailAddress...`) and audit columns hold names. FSCR's file names start with the environment name: do not copy them into reports.
- If an export makes no ZIP (`Error: Failed calling ...`; the unzip line then fails with `IndexError`), run it again into a **new** folder (read-only) and use that folder in every later command. VERIFIED (it happens often)
- Do not wrap the import in a shell `timeout`. If its connection drops after the ProcessId line, **never import again**: `mkdir -p` the import folder, fetch the log with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code ORA_PO_COMPLIANCE_CHECKLIST_QUESTIONS --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/<import folder>/recovered_process_log.txt"` (repeat until complete), then use the log reader on that folder.
- `compare_exports.py` counts rows from earlier test runs as "before" rows: counts grow with every run.

## Sign-in
If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person signs in on the browser tab). Never print tokens, the server address or user names.

## Prerequisites
None. The owner is set by Oracle when the owner columns (`ListName`, `PrimaryEmailId`, `EmailAddress`) are empty. VERIFIED. Never type a person's name or email.

## Step 1. Read-only export
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_PO_COMPLIANCE_CHECKLIST_QUESTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); sys.exit('NO ZIP: run the export again into a new folder') if not z else zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 6 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml`, `ORA_POQ_CHECKLIST_QUESTION.csv`, `..._ACC_RESPONSES.csv`, `..._BRANCHES.csv`, `ORA_POQ_TRANS_CHECKLIST_QUESTION.csv`, `ORA_POQ_TRANS_CHECKLIST_QUESTION_ACC_RESPONSES.csv`. Our environment started with 0 rows.

## Step 2. Build the package (new question only)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_POQ_CHECKLIST_QUESTION.csv=QuestionName \
  --row "ORA_POQ_CHECKLIST_QUESTION.csv|QuestionName=<NAME>|RevisionNumber=0|AllowRespCommentFlag=N|LatestRevisionFlag=Y|QuestionLevel=SUPPLIER|QuestionStatus=ACTIVE|QuestionText=<TEXT>|QuestionType=INPUT_BOX|ResponseRequiredFlag=N|ResponseType=SINGLE_LINE_TEXT|QuestionUsage=ORA_CHECKLIST|ResponderType=INTERNAL" \
  --row "ORA_POQ_TRANS_CHECKLIST_QUESTION.csv|ORA_POQ_CHECKLIST_QUESTION.QuestionName=<NAME>|ORA_POQ_CHECKLIST_QUESTION.RevisionNumber=0|Language=US|SourceLang=US|QuestionText=<TEXT>"
```
- Codes (VERIFIED, from the lookups): `QuestionStatus` `DRAFT` or `ACTIVE` (`POQ_QUESTION_STATUS`); `QuestionType` `INPUT_BOX` (`POQ_QUESTION_TYPE`; `MCSS` / `MCMS` need acceptable-response rows, not tested); `ResponseType` `SINGLE_LINE_TEXT` (`POQ_RESPONSE_TYPE`); `ResponderType` `INTERNAL` (`POQ_RESPONDER_TYPE`); `QuestionLevel` `SUPPLIER` (`POQ_QUESTION_LEVEL`); usage `ORA_CHECKLIST`.
- Use `ACTIVE` if the question will go into an active section (a section can be activated only with active questions). VERIFIED
- Leave owner and audit columns empty. `Language`/`SourceLang` = `US`: GUESS, use your base language.

## Step 3. Import
Approval: the person must approve the environment, the task and NAME before this step.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_PO_COMPLIANCE_CHECKLIST_QUESTIONS --task-name "Manage Compliance Checklist Questions" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result" > "<RUN>/import_result.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import_result.out"
python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"
```
Success (VERIFIED): `Compliance Checklist Question. Status: Completed successfully`, `1 rows were processed. 0 rows of them failed`, `IMPORT: PASS`.

## Step 4. Read back (second export + compare)
Repeat Step 1 with `export_after` (a new folder if it makes no ZIP), then:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_POQ_CHECKLIST_QUESTION.csv=QuestionName \
  --key ORA_POQ_TRANS_CHECKLIST_QUESTION.csv=ORA_POQ_CHECKLIST_QUESTION.QuestionName+Language \
  --expect ORA_POQ_CHECKLIST_QUESTION.csv=<NAME>
```
`RESULT: PASS` = question and translation added, nothing removed or changed. VERIFIED

## Rules and limits
1. New records only. Questions stay (this skill never deletes).
2. Keep all 6 files in the package; metadata XML unchanged.
3. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Try | Result |
|---|---|
| Draft question `GAPFILL_AB_B3_CQ1` | ProcessId 100004744395732: 1 row, 0 failed |
| Active question `GAPFILL_AB_B3_CQ2` | ProcessId 100004744395761: 1 row, 0 failed; compare: 2 questions + 2 translations added: PASS; used in active section `GAPFILL_AB_B3_CS3` |
