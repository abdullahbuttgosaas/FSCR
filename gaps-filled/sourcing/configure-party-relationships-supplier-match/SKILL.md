---
skill_id: "gosaas.gap-fills.sourcing.configure-party-relationships-supplier-match"
name: "Configure Party Relationships for Supplier Match (GoSaaS gap fill)"
description: "Adds ONE relationship type of your own to the list of party relationship types used for supplier match, through FSCR's setup-task CSV export and import. Because the list is shared, the test first creates a NEW organization-to-organization relationship type of your own (task Manage Relationship Types, CSV) that no party uses, then adds that type. Read back by REST relationshipTypes and two export compares. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing and Supplier Management batch 03, 2026-11-28. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_POZ_CONFIGURE_PARTY_RELATIONSHIPS_FOR_SUPPLIER_MATCH"
task_name: "Configure Party Relationships for Supplier Match"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "task HZ_MANAGE_RELATIONSHIP_TYPES (Manage Relationship Types), used here for the prerequisite type"
side_effects:
  - "Creates one new relationship type (and its role lookup rows) and adds it to the supplier match list. The list is shared: add only a type of your own that no party uses, so supplier matching does not change. There is no delete by CSV: plan as if both stay."
---

# Configure Party Relationships for Supplier Match (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-28) · **GUESS** = judgment, not tested.

## What it is and when to use
This task lists the party relationship types that supplier match takes into account (the CSV holds one column, `RelationshipType`). VERIFIED. Adding a type that real parties use would change how suppliers are matched for everyone, and the CSV cannot remove it again. So this skill **first creates a NEW relationship type of your own** (organization to organization, symmetric, no party has it) and adds only that type. Our environment's list was empty before the test (0 rows).

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties filled in). Read only.
GAPS   = the gaps-filled folder that holds sourcing\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path); no folder in its path named exactly "project".
         Create it first: mkdir -p "<RUN>". Check: git -C "<RUN>" rev-parse --show-toplevel 2>/dev/null || echo "RUN not in git: OK"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
RT     = new relationship type code: PREFIX + short name, e.g. GAPFILL_AB_RT1
SUBJ   = subject role plural, text that is NEW on the environment, e.g. "GAPFILL AB RT1 subjects" (singular: same without the final s)
OBJ    = object role plural, DIFFERENT from SUBJ and new, e.g. "GAPFILL AB RT1 objects"
```
Every `<FSCR>`, `<GAPS>`, `<RUN>`, `<...>` below is a placeholder: put the real value in its place before you run the command.

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. In Git Bash write paths as `E:/...` (never `/e/...`, never `$PWD`). Shell variables do **not** survive from one tool call to the next. VERIFIED
- **Never read an import log with cat, sed or grep** (it holds the environment name and the submitting user). Read it only with `python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<folder>"`. VERIFIED
- **Never print export CSVs whole** and never print the metadata XML. FSCR's output file names start with the environment name: do not copy them into reports.
- Save each export's output to a file and print only whether a ZIP was written. No ZIP: run the export again into a NEW folder (read only; up to 3 times) and use that folder in every later command.
- The ProcessId is on the line `Started setup task CSV import process: <n>` (`grep -o` is safe). No ProcessId line after an error: **do not import again**; check with REST / the after-export first. Connection dropped **after** the ProcessId line: the import still runs; **never import again**; wait 2 minutes and read back.

## Sign-in
If a call says HTTP 401/403, or hangs with no output, stop it and sign in: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). An unattended run stops here and reports instead. Never print tokens, the server address or user names.

## Prerequisites (numbered steps; P1 to P3 create your own relationship type)
REST `relationshipTypes` (CRM) reads types but has no create (describe shows `get` only, VERIFIED). The type is created by CSV through the task **Manage Relationship Types** (`HZ_MANAGE_RELATIONSHIP_TYPES`). Its export lists only types created this way (no seeded types): our first export had 0 type rows, and an export right after our create still showed 0, while the next tester's export showed our type (1 row) and then its own (2 rows). So the type row is written in full and read back by REST (the export can lag). VERIFIED

### P1. Check RT is new and read-only export of Manage Relationship Types
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/crmRestApi/resources/11.13.18.05/relationshipTypes" --query "q=RelationshipType='<RT>'" --query onlyData=true --no-open-browser --output "<RUN>/rt_before.json" > "<RUN>/rt_before.out" 2>&1; echo "rc=$?"
python -I -c "import json,sys; c=json.load(open(sys.argv[1]))['count']; print('RT is new' if c==0 else 'STOP: RT exists')" "<RUN>/rt_before.json"
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code HZ_MANAGE_RELATIONSHIP_TYPES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/rt_export_before" > "<RUN>/rt_export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/rt_export_before"
python -I -c "
import csv,sys
m=[r['Meaning'] for r in csv.DictReader(open(sys.argv[1]+'/ORA_FND_LOOKUP_VALUES_B.csv',encoding='utf-8-sig'))]
print('role texts are new' if sys.argv[2] not in m and sys.argv[3] not in m else 'STOP: pick new SUBJ/OBJ texts')
" "<RUN>/rt_export_before/unz" "<SUBJ>" "<OBJ>"
```
Expect 3 files: `HZ_RELATIONSHIP_TYPES.csv` (types made by this route, often 0 or earlier test types), `ORA_FND_LOOKUP_VALUES_B.csv` (role lookups), `ORA_HZ_CODE_ASSIGNMENTS.csv`. VERIFIED

### P2. Build and import the relationship type
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/sourcing/scripts/build_csv_package.py" --export-dir "<RUN>/rt_export_before/unz" --out "<RUN>/rt_payload/new.zip" --prefix <PREFIX> \
  --key HZ_RELATIONSHIP_TYPES.csv=RelationshipType \
  --row "HZ_RELATIONSHIP_TYPES.csv|RelationshipType=<RT>|SubjectType=ORGANIZATION|ObjectType=ORGANIZATION|ForwardRelationshipCode=PARTNER_OF|BackwardRelationshipCode=PARTNER_OF|DirectionCode=N|Status=A|AllowRelateToSelfFlag=N|AllowCircularRelationships=Y|CreatedByModule=HZ_RM_UI|SubjectRoleSingular=<SUBJ without final s>|SubjectRolePlural=<SUBJ>|ObjectRoleSingular=<OBJ without final s>|ObjectRolePlural=<OBJ>|SubjectRoleMeaning=<SUBJ>|SubjectRoleDescription=GoSaaS gap fill test role"
mkdir -p "<RUN>/rt_import"; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code HZ_MANAGE_RELATIONSHIP_TYPES --task-name "Manage Relationship Types" \
  --zip-file "<RUN>/rt_payload/new.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/rt_import" > "<RUN>/rt_import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/rt_import.out"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/rt_import"
```
Success (VERIFIED): `Business object: Trading Community Relationship Type. Status: Completed successfully`, `A total of 1 rows were processed. 0 rows of them failed`, `IMPORT: PASS`. What each column needs (VERIFIED by refused tries):
- `PARTNER_OF` / `PARTNER_OF` with `DirectionCode N` copies the pattern of the seeded symmetric type `PARTNER` (forward = backward code). Codes are read live in P1b below if you want another pair.
- No role texts: `JBO-27035: Attribute Name is required`. No `CreatedByModule`: `HZ_CBM_REQD_ERROR`. `HZ_RM_UI` is a code of lookup `HZ_CREATED_BY_MODULES` and was accepted.
- **SUBJ and OBJ must differ** and be new: the same plural for both gives `FND_CMN_RCRD_VAL: A record with the value <text> already exists`.
- **A refused row can still leave one role lookup** (code `RM_USER_ROLE<number>`, meaning = SUBJ) behind. Before any new try, run P1's export again and pick NEW SUBJ and OBJ texts, or the next try fails on the same duplicate.

P1b (optional, read only): seeded symmetric organization types and their codes:
`python -B "$H" "<FSCR>" "/crmRestApi/resources/11.13.18.05/relationshipTypes" --query "q=DirectionCode='N';SubjectType='ORGANIZATION';ObjectType='ORGANIZATION'" --query onlyData=true --no-open-browser --output "<RUN>/rt_sym.json"` (use `;` between conditions; VERIFIED 4 types: COMPETITOR, ORA_SHIP_TO_CUSTOMER, PARTNER, REFERENCE).

### P3. Read the new type back
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/crmRestApi/resources/11.13.18.05/relationshipTypes" --query "q=RelationshipType='<RT>'" --query onlyData=true --no-open-browser --output "<RUN>/rt_after.json" > "<RUN>/rt_after.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys; i=json.load(open(sys.argv[1],encoding='utf-8'))['items']
[print(x['RelationshipType'],x['ForwardRelationshipCode'],x['BackwardRelationshipCode'],x['DirectionCode'],x['SubjectType'],x['ObjectType'],x['Status'],x['CreatedByModule']) for x in i]
print('TYPE:','PASS' if len(i)==1 and i[0]['Status']=='A' else 'FAIL')
" "<RUN>/rt_after.json"
```
`TYPE: PASS` = one active type RT. VERIFIED

## Step 1. Read-only export of the task
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_POZ_CONFIGURE_PARTY_RELATIONSHIPS_FOR_SUPPLIER_MATCH --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys; r=[x['RelationshipType'] for x in csv.DictReader(open(sys.argv[1]+'/ORA_SUPPLIER_MATCH_PARTY_RELATIONSHIP.csv',encoding='utf-8-sig'))]; print(len(r),'types in the list:',r); print('RT not yet in the list' if sys.argv[2] not in r else 'STOP: RT already in the list')" "<RUN>/export_before/unz" "<RT>"
```
One CSV, `ORA_SUPPLIER_MATCH_PARTY_RELATIONSHIP.csv`, one column `RelationshipType`. It held 0 rows before our first test; earlier test types may be in it now. VERIFIED

## Step 2. Build the package (offline)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
python -I "<GAPS>/sourcing/scripts/build_csv_package.py" --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_SUPPLIER_MATCH_PARTY_RELATIONSHIP.csv=RelationshipType \
  --row "ORA_SUPPLIER_MATCH_PARTY_RELATIONSHIP.csv|RelationshipType=<RT>"
```
Expect `ORA_SUPPLIER_MATCH_PARTY_RELATIONSHIP.csv: 1 row(s)`. The builder refuses a type without the prefix or one already in the list. VERIFIED

## Step 3. Import
Approval: the person must approve the environment, the tasks and the new codes before P2 and this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
mkdir -p "<RUN>/import_result"; cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_POZ_CONFIGURE_PARTY_RELATIONSHIPS_FOR_SUPPLIER_MATCH --task-name "Configure Party Relationships for Supplier Match" \
  --zip-file "<RUN>/payload/new.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"
```
Success (VERIFIED): `Business object: Supplier Match Party Relationship. Status: Completed successfully`, `A total of 1 rows were processed. 0 rows of them failed`, `IMPORT: PASS`.

## Step 4. Read back (second exports)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_POZ_CONFIGURE_PARTY_RELATIONSHIPS_FOR_SUPPLIER_MATCH --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/export_after" > "<RUN>/export_after.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_after"
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_SUPPLIER_MATCH_PARTY_RELATIONSHIP.csv=RelationshipType --expect ORA_SUPPLIER_MATCH_PARTY_RELATIONSHIP.csv=<RT>
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code HZ_MANAGE_RELATIONSHIP_TYPES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/rt_export_after" > "<RUN>/rt_export_after.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/rt_export_after"
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/rt_export_before/unz" "<RUN>/rt_export_after/unz" \
  --key HZ_RELATIONSHIP_TYPES.csv=RelationshipType --key ORA_FND_LOOKUP_VALUES_B.csv=LookupCode --key ORA_HZ_CODE_ASSIGNMENTS.csv=HZ_RELATIONSHIP_TYPES.RelationshipType --expect ORA_FND_LOOKUP_VALUES_B.csv=<RT>
```
Both print `RESULT: PASS` (VERIFIED): the supplier match list gained only RT; the relationship type export gained only your rows: lookup rows (one with code RT, and the new role lookup `RM_USER_ROLE<number>`) and, once the export catches up, the type row RT in `HZ_RELATIONSHIP_TYPES.csv`; nothing removed or changed. Other people's new lookup rows between your two exports would also show as added.

## Rules and limits
1. Add only a relationship type of your own that no party uses. Adding a seeded or used type (for example PARTNER) changes supplier matching for everyone and cannot be undone by CSV: that is a decision for the supplier data owner, not a test.
2. New rows only; the list has no other columns.
3. Test types and list rows stay (no delete by CSV); record them, including any `RM_USER_ROLE` lookup left by a refused try.
4. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-28). Do not reuse these names or texts.
| Step | Result |
|---|---|
| Type try 1 | no role texts: `JBO-27035 Attribute Name is required` (ProcessId 100004743466577), nothing created |
| Type try 2 | + role texts, no `CreatedByModule`: `HZ_CBM_REQD_ERROR` (100004743464742); left role lookup "GAPFILL AB test partners" |
| Type try 3 | + `CreatedByModule HZ_RM_UI`, same texts: `FND_CMN_RCRD_VAL` duplicate (100004743464751), caused by try 2's leftover lookup (proved by export) |
| Type try 4 | new texts, but SUBJ = OBJ: `FND_CMN_RCRD_VAL` (100004743466610); left role lookup "GAPFILL AB S3 RT1 partners" |
| Type try 5 | SUBJ "GAPFILL AB RT1 subjects", OBJ "GAPFILL AB RT1 objects": `GAPFILL_AB_S3_RT1` created, ProcessId 100004744441598; REST 1 type, active, `HZ_RM_UI` |
| Task import | `GAPFILL_AB_S3_RT1` added to the supplier match list: ProcessId 100004743464762, 1 row, 0 failed |
| Exports after | supplier match list 0 -> 1 (only RT): PASS; relationship type export: only lookup rows added (RT, 3 role lookups incl. the 2 leftovers): PASS |
