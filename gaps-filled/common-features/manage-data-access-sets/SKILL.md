---
skill_id: "gosaas.gap-fills.common-features.manage-data-access-sets"
name: "Manage Data Access Sets (GoSaaS gap fill)"
description: "Create a new General Ledger data access set (full ledger access to one ledger) through FSCR's setup-task CSV export and FSM CSV import (GL_ACCESS_SET_DEF + ORA_GL_ACCESS_SET_ASSIGNMENT_DEF), with the ledger's chart of accounts, calendar and period type read live by REST, then read it back with a second export. New records only; the set is not given to any user. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 05, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_MANAGE_DATA_ACCESS_SETS"
task_name: "Manage Data Access Sets"
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
  - "an existing ledger (read by REST; not created here)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new data access set with one ledger assignment. No user or role gets it (that is the separate task Manage Data Access for Users), so nobody's access changes. It may not be deletable; plan as if it stays."
---

# Manage Data Access Sets (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag); it has no skill or guide and gives no row content. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
A **data access set** says which ledgers (or which primary balancing segment values of them) a person may see or post to. It does nothing on its own: it only takes effect when it is given to a user with a role (task "Manage Data Access for Users"). This skill creates **one data access set with full-ledger access to one existing ledger**.
- Use it when someone asks to create a new data access set for task `GL_MANAGE_DATA_ACCESS_SETS`.
- Do **not** use it to change an existing set, to give a set to a user, or for balancing-segment or management-segment sets (not tested). New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
DAS     = new data access set name, starting with PREFIX, at most 30 characters (GUESS: GL_ACCESS_SETS.NAME is 30)
LEDGER  = the name of an existing ledger the set gives access to (the person names it; else any PRIMARY ledger from Step 3)
COA, PS, PT, SIC = the ledger's chart of accounts number, calendar (period set), period type and chart of accounts instance code, all read live in Step 3
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`: the helpers then cannot find FSCR), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
1. An existing ledger (LEDGER). This skill does not create ledgers. Step 3 checks it exists and reads its values.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code GL_MANAGE_DATA_ACCESS_SETS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 3 files (VERIFIED, about 30 to 65 s): `GL_ACCESS_SET_DEF.csv` (the sets, 46 columns), `ORA_GL_ACCESS_SET_ASSIGNMENT_DEF.csv` (ledger assignments, 37 columns, parent column `GL_ACCESS_SET_DEF.Name`) and `ASM_SETUP_CSV_METADATA.xml`. The export holds only manually made sets (VERIFIED: 4 sets; the sets Oracle creates automatically for each ledger are not in it). DAS must not be in `GL_ACCESS_SET_DEF.csv` (the builder checks again). If the export drops (no ZIP), run it again into a new folder, one at a time, up to 3 tries; then stop.

## Step 3. Ledger values (live, REST; never from an export)
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource ledgersLOV --q "Name='<LEDGER>'" \
  --fields Name,ChartOfAccountsId,PeriodSetName,AccountedPeriodType,LedgerCategoryCode --out "<RUN>/ledger.json" --expect-count 1
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource chartOfAccountsLOV --q "StructureInstanceNumber=<COA>" \
  --fields StructureInstanceNumber,StructureInstanceCode,Name --out "<RUN>/coa.json" --expect-count 1
```
Keep: COA = `ChartOfAccountsId`, PS = `PeriodSetName`, PT = `AccountedPeriodType` (from `ledgersLOV`), SIC = `StructureInstanceCode` (from `chartOfAccountsLOV`, using COA in the filter). VERIFIED. Exit 2 = sign-in or privilege problem; `--expect-count 1` failing = wrong ledger name (exact, case-sensitive).

## Step 4. Build a package with only the new set
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name das_new.zip --prefix <PREFIX> \
  --key "GL_ACCESS_SET_DEF.csv=Name" --key "ORA_GL_ACCESS_SET_ASSIGNMENT_DEF.csv=GL_ACCESS_SET_DEF.Name,Name" \
  --prefix-col "GL_ACCESS_SET_DEF.csv=Name" --max-len "Name=30" \
  --row "GL_ACCESS_SET_DEF.csv|Name=<DAS>|Description=<short text>|SecuritySegmentCode=F|EnabledFlag=Y|PeriodSetName=<PS>|UserPeriodSetName=<PS>|AutomaticallyCreatedFlag=N|DefaultLedgerName=<LEDGER>|Name1=<LEDGER>|StructureInstanceNumber=<COA>|StructureInstanceCode=<SIC>|KeyFlexfieldCode=GL#|ApplicationShortName=GL" \
  --row "ORA_GL_ACCESS_SET_ASSIGNMENT_DEF.csv|GL_ACCESS_SET_DEF.Name=<DAS>|Name=<LEDGER>|AllSegmentValueFlag=Y|AccessPrivilegeCode=B|SegmentValueTypeCode=S|ChartOfAccountStructIdTrans=<COA>|PeriodSetNameTrans=<PS>|AccountedPeriodTypeTrans=<PT>|BooleanAllSegmentValueTrans=true"
```
- `SecuritySegmentCode=F` = full ledger access; `AccessPrivilegeCode=B` = read and write; `SegmentValueTypeCode=S` = a single ledger; `AllSegmentValueFlag=Y` with `BooleanAllSegmentValueTrans=true` = all values. These are the values of every working set in our export (VERIFIED). `UserPeriodSetName` = PS worked (VERIFIED; GUESS that it can differ from PS in other environments: if the import says the calendar is invalid, use the calendar's user name).
- **`StructureInstanceCode` is required in practice** (VERIFIED: without it the import refused the row with `GL_INVALID_LEDGER: You must enter a valid ledger value`, 1 row processed, 1 failed, nothing created).
- Leave the descriptive flexfield columns (`Attribute*`), `Description1`, `SecuredSegValueSetCode`, `TreeCode*`, dates and the audit columns empty. VERIFIED
- Builder must print `GL_ACCESS_SET_DEF.csv: 1 new rows` and `ORA_GL_ACCESS_SET_ASSIGNMENT_DEF.csv: 1 new rows`.

## Step 5. Import
**Approval.** The person must approve the environment, the task, DAS and LEDGER before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code GL_MANAGE_DATA_ACCESS_SETS --task-name "Manage Data Access Sets" \
  --zip-file "<RUN>/payload/das_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`). It is the only key to the full process log later.
- About 30 to 90 s. Short summary of the process log (prints only counts and error texts, no user names):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_]+\. Message Text: [^.]{0,160}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Total Objects Succeeded: 2`, `Total Objects Failed: 0`. Any `Total Objects Failed` above 0, or a `Message Code`, is a failure: nothing was created (check with Step 6's export before any retry).
- **If the script loses the connection after the process started**, the import still runs. **Do not import again.** Wait 2 minutes and do Step 6.
- Rows failed: copy the message, change one thing, retry at most 3 times with a new DAS name. A generic database error at the insert (for example `JBO-26041`): fill `CreatedBy` and `LastUpdatedBy` with the export metadata's `SubmittedBy` (read it at run time, never print it). GUESS (not needed here).

## Step 6. Read back: second export and compare (the proof)
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "GL_ACCESS_SET_DEF.csv=Name" --key "ORA_GL_ACCESS_SET_ASSIGNMENT_DEF.csv=GL_ACCESS_SET_DEF.Name,Name" \
  --expect "GL_ACCESS_SET_DEF.csv=<DAS>" --expect "ORA_GL_ACCESS_SET_ASSIGNMENT_DEF.csv=<DAS>,<LEDGER>" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your set and its one ledger row were added, nothing removed or changed (VERIFIED). To look at the row without audit columns: `python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/export_after/unz" --value <DAS>`.
- There is no REST resource that lists data access sets by name (VERIFIED: `dataAccessSetLedgersLOV` lists ledgers of the sets the signed-in user has, not set names). The export compare is the proof.

## Rules and limits
1. New records only; never import a full export (it would update every set).
2. Never give the test set to a user or role (that changes someone's access; a separate task).
3. Test records may stay for good. This skill never deletes. Record every created set.
4. Not tested: primary balancing segment sets (`SecuritySegmentCode=B`), management segment sets, ledger sets, read-only privilege, several ledgers in one set (each needs the same chart of accounts and calendar, GUESS).
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for `inspect_export.py`, `build_fsm_package.py`, `compare_fsm_exports.py`, `view_record.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 4 sets, 5 assignments; about 30 s |
| Ledger values | `ledgersLOV` + `chartOfAccountsLOV` for one PRIMARY ledger |
| Try 1 | `GAPFILL_AB_B5_DAS1` without `StructureInstanceCode`: `GL_INVALID_LEDGER`, 1 row processed 1 failed, **not created** (ProcessId 100004743395885; export check: 0 GAPFILL sets) |
| Try 2 | `GAPFILL_AB_B5_DAS2` with `StructureInstanceCode` (ProcessId 100004743395906), about 90 s: Total Objects Succeeded 2, Failed 0 |
| Export after + compare | sets added 1, assignments added 1, removed 0, changed 0: PASS |
