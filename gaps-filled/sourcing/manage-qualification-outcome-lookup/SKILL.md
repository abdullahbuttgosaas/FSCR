---
skill_id: "gosaas.gap-fills.sourcing.manage-qualification-outcome-lookup"
name: "Manage Qualification Outcome Lookup (GoSaaS gap fill)"
description: "Add a new code to the lookup type of the task Manage Qualification Outcome Lookup through FSCR's setup-task CSV export and import, carrying the existing type row unchanged, then read it back by REST and a second export. New codes only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, Sourcing batch 01, 2026-11-27. Written and tested live on one test environment. NOT official FSCR."
task_code: "ORA_POQ_MANAGE_QUALIFICATION_OUTCOME_LOOKUP"
task_name: "Manage Qualification Outcome Lookup"
offering: "Procurement (Sourcing and Supplier Management)"
dataloader_import_mode: "FSM"
owner_team: "GoSaaS"
version: "1.0.2"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.rest-api-client"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Read-only export and REST reads; one CSV import that adds one new enabled code to one lookup type. The code shows in that list for every user. There is no delete by CSV: plan as if it stays."
---

# Manage Qualification Outcome Lookup (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a CSV route for this task but no skill. This skill runs FSCR's scripts in place and never edits an FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-27) · **GUESS** = judgment, not tested.

## What it is and when to use
Qualification outcomes are the results a supplier qualification can end with (for example approved, conditional). They are the codes of the standard lookup type `ORA_POQ_QUALIFICATION_OUTCOME` ("Qualification Outcome"; note the `ORA_` at the start, unlike the other POQ types: a REST read of `POQ_QUALIFICATION_OUTCOME` gives HTTP 404), user-extensible (`CustomizationLevel` = `U`). VERIFIED. Its description says the outcomes are defaulted to a qualification area when one is created. VERIFIED (type description). On our test environment the type had 0 codes before our first test (later runs see the test codes). VERIFIED
Use this skill to **add a new code**. Do not use it to rename, disable or end-date an existing code: a row with an existing code would update it.

## Placeholders
```text
FSCR   = the FSCR root folder (holds core\, shared\ and core\auth\fusionEnv.properties filled in). Read only.
GAPS   = the gaps-filled folder that holds sourcing\scripts\ and common-features\scripts\rest_call.py
RUN    = a NEW empty work folder OUTSIDE FSCR and outside any git repo; no folder in its path named exactly "project".
         Check: `git -C "<RUN>" rev-parse --show-toplevel 2>/dev/null || echo "RUN not in git: OK"` must print the OK line.
PREFIX = your test prefix, e.g. GAPFILL_<INITIALS>_
TYPE   = the lookup type you add to (Step 1 shows which types this task holds)
CODE   = the new code: PREFIX + short name (upper case, digits, _; max 30 GUESS), e.g. GAPFILL_AB_X1
MEANING= its display name (max 80 GUESS; must not be the meaning of another code of TYPE; no "|")
DESC   = a short description (optional; no "|")
```

## Shell, logs and counts (read first)
- Start **every** Bash call with `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. In Git Bash write paths as `E:/...` (never `/e/...`, and never pass `$PWD`: it is a `/e/...` path and FSCR's REST client then fails with `No module named 'rest_client_common'`). VERIFIED
- Shell variables do **not** survive from one tool call to the next. Set them again in every call, or save values in a file under `RUN`. Every `<FSCR>`, `<GAPS>`, `<RUN>`, `<TYPE>`, `<CODE>` ... in the commands below is a placeholder: put the real value in its place before you run the command.
- **Never read the import log with cat, sed or grep**: it holds the environment name and the submitting user name. Read it only with `python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"`, which prints the result lines and `IMPORT: PASS` / `IMPORT: FAIL`. VERIFIED
- **Never print the export CSVs whole** (`CreatedBy` / `LastUpdatedBy` hold user names) and never print the metadata XML (it holds the submitting user). Print only the columns shown below. Existing codes may carry people's names: do not copy them into reports.
- FSCR's export and import file names start with the environment name; do not copy them into reports.
- Save each export's output to a file and print only whether a ZIP was written (the error lines hold the server address). If no ZIP was written, run the export again into a new folder (read-only; up to 3 times) and use **that** folder in every later command.
- Do **not** wrap the import in a shell `timeout`; the script's `--wait-seconds` is enough. Save its output to `<RUN>/import.out` so the ProcessId is not lost. The ProcessId is on the line `Started setup task CSV import process: <n>`. `import.out` is the script's screen output, not the process log: `grep -o` on it prints only the matched line and is safe; never print `import.out` whole (it may hold the server address).
- If the import prints an error and there is **no** ProcessId line, you cannot tell whether Oracle got the file. **Do not import again.** Run the Step 4 REST read every minute for 10 minutes. If CODE shows up, go on with Step 4. If not, nothing was created (prove it with the after-export of Step 4); a second import needs the person's approval again.
- If the connection drops **after** the ProcessId line, the import still runs: **never import again**. Fetch its log with `cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code ORA_POQ_MANAGE_QUALIFICATION_OUTCOME_LOOKUP --process-id <n> --token-cache auto --no-open-browser --output "<RUN>/import_result/recovered_process_log.txt"` (again if it says not complete), then read it with `read_import_log.py`.

## Sign-in
- Run FSCR scripts with their full path and `python -B`.
- If a call says HTTP 401/403, or hangs with no output (an expired token waits for a browser sign-in), stop it and sign in with FSCR `core/auth/fusion-oauth-authentication`:
  `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600 > "<RUN>/login.log" 2>&1` (a person signs in on the browser tab; do not print the log). An unattended run stops here and reports instead.
- Never print tokens, the server address or user names.

## Prerequisites
None: the lookup type of this task is seeded. Step 2 checks that TYPE allows new codes and that CODE is not there yet.

## Step 1. Read-only export (shows the scope)
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_QUALIFICATION_OUTCOME_LOOKUP --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<GAPS>/sourcing/scripts/scope_lookup_types.py" "<RUN>/export_before/unz"
python -I -c "
import csv,sys
for f in ['FND_APP_STANDARD_LOOKUP.csv','ORA_FND_APP_STANDARD_LOOKUP_CODE.csv']:
    print(f, sum(1 for _ in csv.DictReader(open(sys.argv[1]+'/'+f,encoding='utf-8-sig'))), 'rows')
" "<RUN>/export_before/unz"
```
Expect 3 files (VERIFIED): `ASM_SETUP_CSV_METADATA.xml`, `FND_APP_STANDARD_LOOKUP.csv`, `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv`. `scope_lookup_types.py` prints the lookup type(s) of the task; ours: `ORA_POQ_QUALIFICATION_OUTCOME`. VERIFIED. So TYPE = `ORA_POQ_QUALIFICATION_OUTCOME`.
The CSV files hold the type row(s) and codes that were ever changed or added; they can be empty (header only) even when the type exists. Either way the builder sends only the rows you give it and refuses a CODE already in the export.

## Step 2. Read TYPE by REST (read only) and build the package
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/standardLookups/<TYPE>?expand=lookupCodes&onlyData=true" \
  --no-open-browser --output "<RUN>/type_before.json" > "<RUN>/rest_before.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys; d=json.load(open(sys.argv[1])); m=[c['Meaning'] for c in d['lookupCodes']]
print('TYPE',d['LookupType'],'level',d['CustomizationLevel'],'codes',len(m))
sys.exit('MEANING TAKEN: pick another MEANING' if sys.argv[2] in m else print('MEANING FREE'))
" "<RUN>/type_before.json" "<MEANING>" && \
TYPEROW=$(python -I "<GAPS>/sourcing/scripts/lookup_type_row.py" "<RUN>/type_before.json" --new-code <CODE>) && \
python -I "<GAPS>/sourcing/scripts/build_csv_package.py" \
  --export-dir "<RUN>/export_before/unz" --out "<RUN>/payload/new.zip" --prefix <PREFIX> \
  --key ORA_FND_APP_STANDARD_LOOKUP_CODE.csv=LookupCode \
  --row "$TYPEROW" \
  --row "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv|FND_APP_STANDARD_LOOKUP.LookupType=<TYPE>|LookupCode=<CODE>|Meaning=<MEANING>|Description=<DESC>|EnabledFlag=Y"
```
- `rc=0` = the read worked. HTTP 404 = TYPE is spelled wrong (copy it from Step 1). To look at an error safely: `sed -E 's#https?://[^ "]+#<URL>#g' "<RUN>/rest_before.out" | tail -3`. VERIFIED
- Run `rest_call.py` **without** `-I` (FSCR sign-in needs packages from the user site on Windows), and pass the FSCR folder as `E:/...`. It wraps FSCR's own `fusion_rest_client.py` unchanged and shows Oracle's real error text.
- `lookup_type_row.py` copies the type row **unchanged** from the REST read and stops if the type does not allow new codes (`S`) or CODE already exists. The type row must be in the ZIP: a code row is processed only with its parent row in the same package. VERIFIED
- The second command prints the type's `CustomizationLevel` and code count and checks MEANING. If it prints `MEANING TAKEN`, nothing is built (the `&&` stops the block): pick another MEANING and run the block again. VERIFIED
- Expect `FND_APP_STANDARD_LOOKUP.csv: 1 row(s)` and `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv: 1 row(s)`; if the builder prints `STOP` or other counts, do not import. Leave dates, `DisplaySequence` and audit columns empty. VERIFIED

## Step 3. Import
Approval: the person must approve the environment, the task and CODE before this step (a brief that names them and says proceed is the approval).
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_QUALIFICATION_OUTCOME_LOOKUP --task-name "Manage Qualification Outcome Lookup" \
  --zip-file "<RUN>/payload/new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.out" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.out"
python -I "<GAPS>/sourcing/scripts/read_import_log.py" "<RUN>/import_result"
```
Keep the ProcessId. Success (VERIFIED): `Business object: Application Standard Lookup. Status: Completed successfully`, `A total of 2 rows were processed. 0 rows of them failed` (type row + code row), `IMPORT: PASS`.

## Step 4. Read back (REST before vs after, and a second export)
Run this step also when the import failed: it proves whether anything changed.
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1; H="<GAPS>/common-features/scripts/rest_call.py"
python -B "$H" "<FSCR>" "/fscmRestApi/resources/11.13.18.05/standardLookups/<TYPE>?expand=lookupCodes&onlyData=true" \
  --no-open-browser --output "<RUN>/type_after.json" > "<RUN>/rest_after.out" 2>&1; echo "rc=$?"
python -I -c "
import json,sys
a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]));code=sys.argv[3]
k=lambda d:{c['LookupCode']:{x:y for x,y in c.items() if 'LastUpdate' not in x} for c in d['lookupCodes']}
ca,cb=k(a),k(b)
t=[x for x in a if x not in ('lookupCodes','LastUpdateDate','LastUpdatedBy','LastUpdateLogin') and a[x]!=b.get(x)]
added=[c for c in cb if c not in ca]; gone=[c for c in ca if c not in cb]; ch=[c for c in ca if c in cb and ca[c]!=cb[c]]
print('codes before',len(ca),'after',len(cb)); print('type changed',t,'added',added,'removed',len(gone),'changed',len(ch))
print('READBACK:', 'PASS' if added==[code] and not (t or gone or ch) and cb.get(code,{}).get('EnabledFlag')=='Y' else 'FAIL')
" "<RUN>/type_before.json" "<RUN>/type_after.json" <CODE>
```
`READBACK: PASS` = only your code was added, enabled; the type row and every existing code are unchanged. VERIFIED. (If someone else adds a code to TYPE at the same moment, `added` lists theirs too and this prints FAIL: look at the `added` list before you judge.)
Second check: a new read-only export into `export_after`, then the compare:
```bash
export PYTHONUTF8=1 MSYS_NO_PATHCONV=1
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_POQ_MANAGE_QUALIFICATION_OUTCOME_LOOKUP --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_after" > "<RUN>/export_after.out" 2>&1
python -I -c "import sys,zipfile,glob; z=glob.glob(sys.argv[1]+'/*.zip'); print('ZIP written' if z else 'NO ZIP: run again into a new folder'); z and zipfile.ZipFile(z[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_after"
python -I "<GAPS>/sourcing/scripts/compare_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key ORA_FND_APP_STANDARD_LOOKUP_CODE.csv=LookupCode --expect ORA_FND_APP_STANDARD_LOOKUP_CODE.csv=<CODE>
```
`RESULT: PASS` = nothing removed or changed and CODE is among the added rows. VERIFIED. When the before-export was empty, the type row also shows as "added": that is the first export of the type, not a change (the REST check proves the type did not change). VERIFIED

## Where to see it in Fusion
Setup and Maintenance > Procurement offering > functional area Supplier Qualification > task **Manage Qualification Outcome Lookup**: CODE is in the list of codes of TYPE. GUESS (screen path from the task catalog; not opened by the agent)

## Rules and limits
1. New codes only. Never send an existing code; never change the type row (copy it as read).
2. Codes: upper case, digits, `_`, max 30 (GUESS); meaning max 80 and unique in the type (GUESS).
3. A new code shows to every user of the list. Test codes stay (no delete by CSV); record them.
4. Tasks that share this package (the other Sourcing and Supplier Qualification lookup tasks) and overlap in scope must run one after the other, not at the same time.
5. Tested on one environment, release 11.13.26.10.0.

## Worked example (VERIFIED, 2026-11-27). Do not reuse these names.
Counts are from our first run; every test adds codes, so later runs see more codes before. That is expected.
| Step | Result |
|---|---|
| Export before | 3 files; scope ORA_POQ_QUALIFICATION_OUTCOME; type before: 0 codes (export empty) |
| New code | `GAPFILL_AB_S1_QO1` "GAPFILL AB Qualification Outcome 1" |
| Import | ProcessId 100004744437773: 2 rows processed, 0 failed |
| REST after | 1 codes; added 1, removed 0, changed 0; type unchanged: PASS |
| Export after | compare PASS (only the new code added) |
