---
skill_id: "gosaas.gap-fills.common-features.manage-resource-note-type-mapping"
name: "Manage Resource Note Type Mapping (GoSaaS gap fill)"
description: "Create one new note type mapping (an existing note type mapped to an existing object) through FSCR's setup-task CSV export and FSM CSV import (ORA_OBJECT_LOOKUP / ZMM_OBJECT_LOOKUP_MAPPING package), with the note type checked live by REST, then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 2, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "HZ_MANAGE_RESOURCE_NOTE_TYPE_MAPPING"
task_name: "Manage Resource Note Type Mapping"
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
  - "gosaas common-features/manage-profile-options/scripts/copy_parent_rows.py"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one mapping row. The object row is sent unchanged as the parent. The mapping limits which note types users see for notes on that object, so a test uses a TEST object only. It may not be deletable; plan as if it stays."
---

# Manage Resource Note Type Mapping (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has guidance cards for other note type mapping tasks but nothing that builds the rows. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A note type mapping says which note types (codes of the lookup `ZMM_NOTE_TYPE`) are offered when someone adds a note to a given **object** (here: the objects in the task's export, custom objects such as `..._C`). This skill maps **one existing note type to one existing object**.
- **Test rule:** map only to an object that is clearly a test object (code or name contains `TEST`) and that has **no mapping yet**. Mapping a real object changes the note types every user sees on it: that needs the person's explicit approval.
- **Record name:** a mapping has no name or code of its own; it is identified by object + note type. So it cannot carry the test prefix. Record the pair in your log. Use a seeded note type (for example `GENERAL`); adding a new code to the seeded `ZMM_NOTE_TYPE` lookup is a different, untested change.

## When to use
- Someone asks to create a **new** note type mapping for task `HZ_MANAGE_RESOURCE_NOTE_TYPE_MAPPING`.
- Do **not** use it to change, end-date or remove mappings. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
SK      = <GAPS>/common-features/manage-profile-options/scripts     (copy_parent_rows.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, no folder in its path named exactly "project"
OBJECT  = the ObjectCode to map to (Step 3)
NOTE    = the note type code (LookupCode of ZMM_NOTE_TYPE), e.g. GENERAL (Step 3)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code HZ_MANAGE_RESOURCE_NOTE_TYPE_MAPPING --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 3 files (VERIFIED, about 40 s): `ORA_OBJECT_LOOKUP.csv` (objects: `ObjectCode, ObjectName, ObjectDesc, DeletedFlag, ModuleId` + audit), `ZMM_OBJECT_LOOKUP_MAPPING.csv` (mappings: `ORA_OBJECT_LOOKUP.ObjectCode, MappingTypeCode, MappedLookupCode, SourceObjectCode, MappingEndDate, DefaultFlag, EndDateActive, EnabledFlag` + audit) and `ASM_SETUP_CSV_METADATA.xml` (scope `ZmmObjectMapTypeCode=ZMM_NOTE_TYPE`). The mapping file may be empty. If the export drops, retry into a new folder, up to 3 tries; then **stop**.

## Step 3. Choose OBJECT and NOTE
```bash
python -I -c "import csv,sys; d=sys.argv[1]; m={r['ORA_OBJECT_LOOKUP.ObjectCode'] for r in csv.DictReader(open(d+'/ZMM_OBJECT_LOOKUP_MAPPING.csv',encoding='utf-8-sig'))}; [print(r['ObjectCode'],'|',r['ObjectName'],'| deleted',r['DeletedFlag'],'| mapped' if r['ObjectCode'] in m else '| no mapping') for r in csv.DictReader(open(d+'/ORA_OBJECT_LOOKUP.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource standardLookups/ZMM_NOTE_TYPE/child/lookupCodes \
  --fields LookupCode,Meaning,EnabledFlag --out "<RUN>/note_types.json" | head -15
```
1. **OBJECT**: the person names it, or the **first listed** object whose code or name contains `TEST`, with `deleted N` and `no mapping`. If there is none, **stop** and ask.
2. **NOTE**: the person names it, or `GENERAL`. It must be in the REST list with `EnabledFlag=Y`. VERIFIED
3. The pair OBJECT + NOTE must not be in the mapping file (Step 3 lists mapped objects; you chose an unmapped one).

## Step 4. Build: the mapping row, then the object row unchanged
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name ntm_new.zip \
  --key "ORA_OBJECT_LOOKUP.csv=ObjectCode" --key "ZMM_OBJECT_LOOKUP_MAPPING.csv=ORA_OBJECT_LOOKUP.ObjectCode,MappingTypeCode,MappedLookupCode" \
  --row "ZMM_OBJECT_LOOKUP_MAPPING.csv|ORA_OBJECT_LOOKUP.ObjectCode=<OBJECT>|MappingTypeCode=ZMM_NOTE_TYPE|MappedLookupCode=<NOTE>|DefaultFlag=N|EnabledFlag=Y"
python -I "<SK>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
  --zip-name ntm_new.zip --file ORA_OBJECT_LOOKUP.csv --where ObjectCode=<OBJECT>
```
- The builder must print `ZMM_OBJECT_LOOKUP_MAPPING.csv: 1 new rows` and `ORA_OBJECT_LOOKUP.csv: 0 new rows`; then `copy_parent_rows.py` adds the object row **unchanged** (the package is hierarchical: a child without its parent row is not processed). Import the re-zipped ZIP.
- `MappingTypeCode=ZMM_NOTE_TYPE` is the export's scope value. Leave `SourceObjectCode`, `MappingEndDate`, `EndDateActive` and the audit columns empty: Oracle fills `SourceObjectCode` with OBJECT itself. VERIFIED. `DefaultFlag=N` (not the default note type).

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact OBJECT + NOTE before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code HZ_MANAGE_RESOURCE_NOTE_TYPE_MAPPING --task-name "Manage Resource Note Type Mapping" \
  --zip-file "<RUN>/payload/ntm_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`).
- About 1.5 minutes. Short summary of the process log (no user names):
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: [^.]+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Parent row is missing[^.]{0,120}|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: Object ... A total of 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`. The line counts the **object** row; the mapping has no line of its own, so Step 6 is the proof.
- **If the script loses the connection after the process started**, do **not** import again. Wait 2 minutes and do Step 6.
- Rows failed: copy the error, change one thing, retry at most 3 times. A generic database error at the insert (`JBO-26041`): first fill `CreatedBy` and `LastUpdatedBy` from the export metadata's `SubmittedBy` (read at run time, never printed). GUESS (not needed here).

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_OBJECT_LOOKUP.csv=ObjectCode" --key "ZMM_OBJECT_LOOKUP_MAPPING.csv=ORA_OBJECT_LOOKUP.ObjectCode,MappingTypeCode,MappedLookupCode" \
  --expect "ZMM_OBJECT_LOOKUP_MAPPING.csv=<OBJECT>,ZMM_NOTE_TYPE,<NOTE>" --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your mapping was added and the object row is unchanged (`changed 0`). VERIFIED

## Rules and limits
1. New records only; only TEST objects in a test (see the test rule).
2. The package holds your mapping and the object row unchanged; nothing else.
3. Test records may stay for good. This skill never deletes. Record every OBJECT + NOTE pair.
4. Not tested: `DefaultFlag=Y`, end dates, new note type codes in `ZMM_NOTE_TYPE`, objects that already have mappings.
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags: `-B` without `-I` for FSCR scripts and `rest_read.py`; `-I` for the helpers and the one-liners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this pair.
| Step | Result |
|---|---|
| Export before | 18 objects (custom objects), 0 mappings; about 40 s |
| Choice | object `TESTOBJECT1_C` ("Test Object 1", no mapping), note type `GENERAL` (enabled) |
| Import | 1 attempt (ProcessId 100004741419676), about 1.5 min: Object 1 row, 0 failed |
| Export after + compare | 1 mapping added (`SourceObjectCode` filled by Oracle = the object), object row changed 0: PASS |
