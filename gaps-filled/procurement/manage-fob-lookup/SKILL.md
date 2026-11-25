---
skill_id: "gosaas.gap-fills.procurement.manage-fob-lookup"
name: "Manage FOB Lookup (GoSaaS gap fill)"
description: "Add a new FOB (free on board) code, a new code on the extensible lookup type FOB, through FSCR's setup-task CSV export and import, carrying the existing type row unchanged, then read it back by REST. New codes only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Procurement batch 05, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
task_code: "PO_MANAGE_FOB_LOOKUP"
task_name: "Manage FOB Lookup"
offering: "Procurement"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only export and REST reads; one CSV import that adds one new code to the FOB list. The new code shows in the FOB list of every purchasing document and supplier site. Plan as if it stays."
---

# Manage FOB Lookup (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
FOB codes say where the responsibility for shipped goods passes from the seller to the buyer (for example "Origin", "Destination"). They are the codes of the standard lookup type `FOB` ("Valid FOB Codes"), which Oracle ships as **extensible** (`CustomizationLevel` = `E`): you may add codes, not change the type. VERIFIED
They show in the **FOB** list on a purchase order's terms and on supplier sites. GUESS (from Oracle's docs; not opened in our test)
Use this skill to **add a new FOB code**. Do not use it to rename, disable or end-date an existing code (a row with an existing code would update it).

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties). Read only.
GAPS   = the gaps-filled folder that holds procurement\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project"
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE   = new FOB code, PREFIX + short name (upper case, digits, _; max 30), e.g. GAPFILL_AB_FOB1
MEANING= its display name (max 80, not used by another code of the type)
DESC   = a short description (optional; max 240 GUESS)
```

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. In Git Bash write paths as `E:/...` (never `/e/...`).
- Shell variables do **not** survive from one tool call to the next. Save values you need later in a file under `RUN`, or set them again in the same call.
- **Never read the import log with cat, sed or grep**: it is one long line holding the environment name and the submitting user name. Read it only with `python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"`. It prints only the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. VERIFIED
- **Never print the export CSVs whole**: their `CreatedBy` / `LastUpdatedBy` columns hold user names. Print only the columns you need (Step 4 shows how).
- FSCR's export and import file names start with the environment name; do not copy them into reports.
- Save each export's output to a file and print only whether a ZIP was written (the network error line holds the server address). If no ZIP was written, run the export again into a new folder (it is read-only; up to 3 times). VERIFIED
- Do **not** wrap the import in a shell `timeout`: once the ProcessId is printed the import runs on in Oracle. The script's own `--wait-seconds` is enough. Save the import output to a file so the ProcessId is not lost.
- The ProcessId is on the line `Started setup task CSV import process: <n>`. Print only that line: `grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"`.
- If an export had to be re-run into a new folder, use **that** folder (the one holding the ZIP) in every later command.
- If the import prints `Error: ...` (for example `Remote end closed connection without response`) and there is **no** ProcessId line, you cannot tell at once whether Oracle got the file. **Do not import again yet.** Run the Step 4 REST read every minute for 10 minutes. If CODE shows up, the import worked: go on with Step 4. If it never shows up, nothing was created (also prove it with the after-export of Step 4); a second import is a new try and needs the person's approval again (a brief that allows "one retry after a drop with no ProcessId" counts). VERIFIED (a drop with no ProcessId created nothing in our test)
- If an import's connection drops after the ProcessId line, the import still runs in Oracle: **never import again**. Fetch its log with FSCR's `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code PO_MANAGE_FOB_LOOKUP --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/import_result/recovered_process_log.txt"` (run it again if it says not complete), then read it with `read_import_log.py "<RUN>/import_result"`. VERIFIED (same package, other tasks)

## Sign-in
- Run FSCR scripts with their full path and `python -B`; set `PYTHONUTF8=1` and `MSYS_NO_PATHCONV=1`.
- If a call says HTTP 401/403, or hangs with no output (an expired token makes the client wait for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
  `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). VERIFIED
- Never print tokens, the server address or user names.

## Prerequisites
None: the type `FOB` is seeded. Step 2 checks that it allows new codes and that CODE is not there yet.

## Step 1. Read-only export (shows the scope)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code PO_MANAGE_FOB_LOOKUP --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 3 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml`, `FND_APP_STANDARD_LOOKUP.csv`, `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv`. The export scope is the one lookup type `FOB`. Where nobody has added a code by import yet, both CSV files hold the header only (VERIFIED: 0 rows, although the type has a seeded code). After a code was added by import, the export holds the type row and its codes (VERIFIED: type + 2 codes). Either way the builder sends only the rows you give it and refuses a code already in the export. The worked example below is from the first run; later runs see more codes.

## Step 2. Read the type by REST (read only) and build the package
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/standardLookups/FOB?expand=lookupCodes&onlyData=true" \
  --no-open-browser --output "<RUN>/type_before.json" > "<RUN>/rest_before.out" 2>&1; echo "rc=$?"
TYPEROW=$(python -I "<GAPS>/procurement/scripts/lookup_type_row.py" "<RUN>/type_before.json" --new-code <CODE>) && \
python -I "<GAPS>/procurement/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_FND_APP_STANDARD_LOOKUP_CODE.csv=LookupCode \
  --row "$TYPEROW" \
  --row "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv|FND_APP_STANDARD_LOOKUP.LookupType=FOB|LookupCode=<CODE>|Meaning=<MEANING>|Description=<DESC>|EnabledFlag=Y"
```
- `rc=0` = the read worked. If not, read `<RUN>/rest_before.out` only after hiding addresses: `sed -E 's#https?://[^ "]+#<URL>#g' "<RUN>/rest_before.out" | tail -3`.
- Run `rest_call.py` **without** `-I` (FSCR sign-in needs packages from the user site on Windows). It wraps FSCR's own `fusion_rest_client.py` unchanged and shows Oracle's real error text.
- `lookup_type_row.py` copies the type row **unchanged** from the REST read (type, meaning, description, ModuleId, customization level, REST access) and stops if the type is not extensible (`E`/`U`) or CODE already exists. The type row must be in the ZIP: a code row is processed only with its parent row in the same package. VERIFIED
- Expect the builder to print `FND_APP_STANDARD_LOOKUP.csv: 1 row(s)` and `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv: 1 row(s)`. VERIFIED
- Leave dates, `DisplaySequence` and audit columns empty. VERIFIED. Check MEANING is not the meaning of another code in `type_before.json`.

## Step 3. Import
Approval: the person must approve the environment, the task and CODE before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code PO_MANAGE_FOB_LOOKUP --task-name "Manage FOB Lookup" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"
python -I "<GAPS>/procurement/scripts/read_import_log.py" "<RUN>/import_result"
```
- If the `grep` prints nothing, there is no ProcessId: see the "no ProcessId" rule in the shell section. To look at `import.out` safely, hide addresses first: `sed -E 's#https?://[^ "]+#<URL>#g' "<RUN>/import.out" | tail -3`.
- Keep the ProcessId. Success (VERIFIED): `Business object: Application Standard Lookup. Status: Completed successfully`, `A total of 2 rows were processed. 0 rows of them failed` (type row + code row), `IMPORT: PASS`.

## Step 4. Read back (REST before vs after, and a second export)
Run this step also when the import failed: it proves whether anything changed.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/standardLookups/FOB?expand=lookupCodes&onlyData=true" \
  --no-open-browser --output "<RUN>/type_after.json" > "<RUN>/rest_after.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys
a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]));code=sys.argv[3]
k=lambda d:{c['LookupCode']:{x:y for x,y in c.items() if 'LastUpdate' not in x} for c in d['lookupCodes']}
ca,cb=k(a),k(b)
t=[x for x in a if x not in ('lookupCodes','LastUpdateDate','LastUpdatedBy','LastUpdateLogin') and a[x]!=b.get(x)]
added=[c for c in cb if c not in ca]; gone=[c for c in ca if c not in cb]; ch=[c for c in ca if c in cb and ca[c]!=cb[c]]
print('codes before',len(ca),'after',len(cb)); print('type changed',t,'added',added,'removed',gone,'changed',ch)
print('READBACK:', 'PASS' if added==[code] and not (t or gone or ch) and cb[code]['EnabledFlag']=='Y' else 'FAIL')
" "<RUN>/type_before.json" "<RUN>/type_after.json" <CODE>
```
`READBACK: PASS` = only your code was added, enabled; the type row and every existing code are unchanged. VERIFIED (the type's LastUpdateDate also stayed the same).
Second check: repeat Step 1 into `<RUN>/export_after`, then print only safe columns:
```bash
python -I -c "
import csv,sys
for r in csv.DictReader(open(sys.argv[1]+'/ORA_FND_APP_STANDARD_LOOKUP_CODE.csv',encoding='utf-8-sig')): print(r['LookupCode'],'|',r['Meaning'],'|',r['EnabledFlag'])
" "<RUN>/export_after/unz"
```
Your CODE must be in the list. If the before-export already held rows, also run `python -I "<GAPS>/procurement/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" --key ORA_FND_APP_STANDARD_LOOKUP_CODE.csv=LookupCode --expect ORA_FND_APP_STANDARD_LOOKUP_CODE.csv=<CODE>`. (With an empty before-export the compare would list the type row as "added" too: that is the first export of a type, not a change.)

## Where to see it in Fusion
Setup and Maintenance > Procurement offering > functional area Procurement Foundation > task **Manage FOB Lookup**: the lookup type `FOB` shows, and CODE is in its list of codes. GUESS (screen path from the task catalog; not opened by the agent)

## Rules and limits
1. New codes only. Never send an existing code; never change the type row (copy it as read).
2. Codes: upper case, digits, `_`, max 30 (GUESS from the lookup screens); meaning max 80 and unique in the type.
3. A new FOB code shows to every buyer. Test codes stay (no delete); record them.
4. The same steps work for Manage Freight Terms Lookup (`PO_MANAGE_FREIGHT_TERM_LOOKUP`, type `FREIGHT TERMS`) with the task code and type changed: GUESS, not tested here.
5. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-25). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 3 files, both CSVs empty, scope FOB |
| REST before | FOB "Valid FOB Codes", level E, 1 code |
| New code | `GAPFILL_AB_B5_FOB1` "GAPFILL AB Demo FOB Point 1" |
| Import | ProcessId 100004744393796: 2 rows processed, 0 failed |
| REST after | 2 codes; added 1, removed 0, changed 0; type unchanged: PASS |
| Export after | type row + 2 codes, the new code enabled |
