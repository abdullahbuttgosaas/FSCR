---
skill_id: "gosaas.gap-fills.procurement.manage-contract-clause-types"
name: "Manage Contract Clause Types (GoSaaS gap fill)"
description: "Add a new clause type (a new code on the extensible lookup type OKC_SUBJECT) through FSCR's setup-task CSV export and import, carrying the existing type row unchanged, then read it back by REST. New codes only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 01, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_LOOKUPS"
task_name: "Manage Contract Clause Types"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "0.3.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only export and REST reads; one CSV import that adds one new code to the clause type list. The new code shows to every Contract Terms Library user. Plan as if it stays."
reused_by:
  - "procurement PO_MANAGE_FOB_LOOKUP (type FOB) and PO_MANAGE_FREIGHT_TERM_LOOKUP (type FREIGHT TERMS): same package and steps with the task code and type changed (not tested here)"
---

# Manage Contract Clause Types (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
Clause types classify clauses in the Contract Terms Library (for example Administration, Payment, Law). They are the codes of the standard lookup type `OKC_SUBJECT` ("Clause Types"), which Oracle ships as **extensible** (`CustomizationLevel` = `E`): you may add codes, not change the type. VERIFIED
Use it to **add a new clause type code**. Do not use it to rename, disable or end-date an existing code (a row with an existing code would update it).

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE   = new clause type code, PREFIX + short name (upper case, digits, _; max 30), e.g. GAPFILL_AB_CT1
MEANING= its display name (max 80, not used by another code of the type)
DESC   = a short description (optional; any text, max 240 GUESS)
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
None (the type `OKC_SUBJECT` is seeded). Step 2 checks it allows new codes.

## Step 1. Read-only export (shows the scope)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_LOOKUPS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 3 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml`, `FND_APP_STANDARD_LOOKUP.csv`, `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv`. The metadata scope is `lookupType` = `OKC_SUBJECT`, mode `edit`. On an environment where nobody has added a code to this type yet, both CSV files are empty. **After a code was added by import, the export holds the type row and all its codes** (VERIFIED: 18 codes in a later test). Either way the builder sends only the rows you give it and refuses a code already in the export.

## Step 2. Read the type by REST (read only) and build the package
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/standardLookups/OKC_SUBJECT?expand=lookupCodes&onlyData=true" \
  --no-open-browser --output "<RUN>/type_before.json"
TYPEROW=$(python -I "<GAPS>/procurement/scripts/lookup_type_row.py" "<RUN>/type_before.json" --new-code <CODE>)
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_FND_APP_STANDARD_LOOKUP_CODE.csv=LookupCode \
  --row "$TYPEROW" \
  --row "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv|FND_APP_STANDARD_LOOKUP.LookupType=OKC_SUBJECT|LookupCode=<CODE>|Meaning=<MEANING>|Description=<DESC>|EnabledFlag=Y"
```
- Run `rest_call.py` **without** `-I` (FSCR sign-in needs packages from the user site on Windows). It wraps FSCR's own `fusion_rest_client.py` unchanged and shows Oracle's real error text.
- `lookup_type_row.py` copies the type row **unchanged** from the REST read (type, meaning, description, ModuleId, customization level, REST access) and stops if the type is not extensible (`E`/`U`) or CODE already exists. The type row must be in the ZIP: a code row is processed only with its parent row in the same package (lesson from the profile and lookup gap fills).
- Leave dates, `DisplaySequence` and audit columns empty. VERIFIED. Check MEANING is not the meaning of another code in `type_before.json`.

## Step 3. Import
Approval: the person must approve the environment, the task and CODE before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code OKC_MANAGE_CLAUSE_AND_TEMPLATE_MANAGEMENT_LOOKUPS --task-name "Manage Contract Clause Types" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
- Keep the ProcessId. `StatusCode: (unknown)` is normal; read the result only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"` (never cat/grep the log: it holds a user name). Success (VERIFIED): `Business object: Application Standard Lookup. Status: Completed successfully`, `A total of 2 rows were processed. 0 rows of them failed` (type row + code row).
- A dropped connection after the ProcessId: never import again; fetch and read the log as the shell section says (recovered_process_log.txt).

## Step 4. Read back (REST, before vs after)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/standardLookups/OKC_SUBJECT?expand=lookupCodes&onlyData=true" \
  --no-open-browser --output "<RUN>/type_after.json"
python -I -c "
import json,sys
a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]));code=sys.argv[3]
k=lambda d:{c['LookupCode']:{x:y for x,y in c.items() if 'LastUpdate' not in x} for c in d['lookupCodes']}
ca,cb=k(a),k(b)
t=[x for x in a if x not in ('lookupCodes','LastUpdateDate','LastUpdatedBy','LastUpdateLogin') and a[x]!=b.get(x)]
added=[c for c in cb if c not in ca]; gone=[c for c in ca if c not in cb]; ch=[c for c in ca if c in cb and ca[c]!=cb[c]]
print('type changed',t,'added',added,'removed',gone,'changed',ch)
print('READBACK:', 'PASS' if added==[code] and not (t or gone or ch) and cb[code]['EnabledFlag']=='Y' else 'FAIL')
" "<RUN>/type_before.json" "<RUN>/type_after.json" <CODE>
```
`READBACK: PASS` = only your code was added, enabled; the type row and every existing code are unchanged. VERIFIED (in our test even the type's LastUpdateDate stayed the same). Optional second check: repeat Step 1 into `<RUN>/export_after` and run `python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" --key ORA_FND_APP_STANDARD_LOOKUP_CODE.csv=LookupCode --expect ORA_FND_APP_STANDARD_LOOKUP_CODE.csv=<CODE>` (works once the export holds rows).

## Rules and limits
1. New codes only. Never send an existing code; never change the type row (copy it as read).
2. Codes: upper case, digits, `_`, max 30 (GUESS from the lookup screens); meaning max 80 and unique in the type.
3. A new clause type shows to every user of the Contract Terms Library. Test codes stay (no delete); record them.
4. The same steps work for other extensible procurement lookups with their own task codes (FOB, FREIGHT TERMS): GUESS, not tested here.
5. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 3 files, both CSVs empty (first run), scope OKC_SUBJECT |
| REST before | OKC_SUBJECT, level E, 16 codes |
| New code | `GAPFILL_AB_B1_CT1` "GAPFILL AB B1 Clause Type 1" |
| Import | ProcessId 100004744392840: 2 rows processed, 0 failed |
| REST after | 17 codes; added 1, removed 0, changed 0; type unchanged: PASS |
