---
skill_id: "gosaas.gap-fills.common-features.manage-value-sets"
name: "Manage Applications Core Value Sets (GoSaaS gap fill, short card)"
description: "Short card over FSCR's value-sets skill: create a new independent value set with values through the setup-task CSV export and FSM CSV import (FND_APP_FLEX_VALUE_SET package; REST cannot create a value set), then read it back with FSCR's value-sets REST resources and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 3, 2026-11-20. Written and tested live on one test environment. NOT official FSCR."
tested_by_fresh_chat: "See gap_index.csv (fresh_claude_pass) and CHANGELOG.md"
layer: "pillar"
pillar: "Common"
offering: "Common Features"
task_code: "FND_MANAGE_APPLCORE_VALUE_SETS"
task_name: "Manage Applications Core Value Sets"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.fusion-api.apps-common.value-sets (FSCR; references/value-sets.md, read-back only)"
  - "core.fusion-api.apps-common.lookups (FSCR; one read to get the module id)"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import process that creates a new value set and its values. They may not be deletable; plan as if they stay."
required_privileges:
  - "Export Import Functional Setups User plus the task privileges for FND_MANAGE_APPLCORE_VALUE_SETS, and read access to the valueSets and standardLookups REST resources"
---

# Manage Applications Core Value Sets (GoSaaS gap fill, short card)

> **Added by GoSaaS, not part of official FSCR.** FSCR's value-sets skill (`core/fusion-api/apps-common/value-sets`, `references/value-sets.md`) reads value sets by REST and says REST has **no create** for a value set definition. This card creates the value set and its values through the task's FSM CSV package, and uses FSCR's REST resources to read them back. It does not edit any FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-20) · **FROM FSCR** = FSCR file · **GUESS** = judgment, not tested.

## What this setup is
A value set is a list of allowed values for a flexfield segment or a parameter. An **independent** value set (`ValidationType=INDEP`) holds its own list of values. Value sets are usually made before the descriptive flexfield tasks that use them. This card covers independent, character (`VARCHAR2` / `TEXT`) value sets only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers; this card needs that folder in place)
RUN     = a NEW empty work folder OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix (GAPFILL_ in our tests)
VS      = new value set code, e.g. GAPFILL_VS_<something>: upper case, digits, _ (13 characters tried; GUESS max 60)
V1, V2  = new values, e.g. GAPFILL_A (each at most the value set's MaximumLength)
```

## Step 0. Safe running
FSCR scripts with full path and `python -B`; always `--output-dir` under `RUN`. Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.

## Step 1. Export first (also the sign-in check)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_APPLCORE_VALUE_SETS --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
- **Sign-in:** if this says HTTP 401/403 or token expired, or any later REST call hangs with no output (the client is then waiting for a browser sign-in; a token lasts about an hour, VERIFIED), stop that call and sign in: `python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` from `<FSCR>`, in the background; a person completes the browser page (`Login complete for standard.`); never type credentials. Sign-in is waiting time. Tip: put `timeout 120` in front of REST calls so a hang cannot block you.
- Expect 7 files (VERIFIED, about 40 to 55 s): the metadata XML, `FND_APP_FLEX_VALUE_SET.csv` (28 columns), `ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv` (28 columns), and 4 files for table, view-object and related value sets.
- **The export is scoped** to the Applications Core module (metadata scope `moduleKey=FND`) and can be **empty** although the environment has many value sets (VERIFIED: 0 rows before our test). An empty export is fine here; the files still give the layout. If the export fails or lacks these files: **stop**, note it, do not import.

## Step 2. Module id and before-read (REST, read-only)
The value set needs the Applications Core `ModuleId`, so it lands in the task's scope. Read it from a seeded Applications Core lookup that every environment has (`YES_NO`), with FSCR's lookups resource:
```bash
python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource standardLookups --q "LookupType='YES_NO'" \
  --fields LookupType,ModuleId --out "<RUN>/fnd_module.json" --expect-count 1
python -I -c "import json,sys;print(json.load(open(sys.argv[1]))['items'][0]['ModuleId'])" "<RUN>/fnd_module.json"
```
Keep the printed 32-character id as MODULE. **Check it is not empty before you build** (VERIFIED: an empty ModuleId fails the import with `ORA-01400: cannot insert NULL`). Then the before-read (FROM FSCR `references/value-sets.md`, `GET valueSets`):
```bash
python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource valueSets --q "ValueSetCode='<VS>'" \
  --fields ValueSetId,ValueSetCode --out "<RUN>/readback_before.json" --expect-absent
```
Want `0 row(s)` and `READBACK: PASS`. Exit 2 = sign-in, privilege or HTTP problem, not "absent".

## Step 3. Build a package with only the new value set and values
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name value_set_new.zip --prefix <PREFIX> \
  --key "FND_APP_FLEX_VALUE_SET.csv=ValueSetCode" \
  --key "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=FND_APP_FLEX_VALUE_SET.ValueSetCode,Value" \
  --prefix-col "FND_APP_FLEX_VALUE_SET.csv=ValueSetCode" --max-len "ValueSetCode=60" \
  --row "FND_APP_FLEX_VALUE_SET.csv|ValueSetCode=<VS>|ModuleId=<MODULE>|Description=<text>|ValidationType=INDEP|ValueDataType=VARCHAR2|ValueSubtype=TEXT|MaximumLength=20|UppercaseOnlyFlag=Y|ZeroFillFlag=N|SecurityEnabledFlag=N" \
  --row "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv|FND_APP_FLEX_VALUE_SET.ValueSetCode=<VS>|Value=<V1>|Description=<text>|EnabledFlag=Y|SummaryFlag=N|SortOrder=1" \
  --row "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv|FND_APP_FLEX_VALUE_SET.ValueSetCode=<VS>|Value=<V2>|Description=<text>|EnabledFlag=Y|SummaryFlag=N|SortOrder=2"
```
- VERIFIED: exactly these columns imported cleanly; all others empty (no `ValueSetIdentifier`, no dates, no audit columns). The other 4 files keep only their headers.
- `UppercaseOnlyFlag=Y` means values must be upper case: keep the values upper case, or set it to `N`.
- The helper stops if the code is already in the export (only a partial check, because the export is scoped: Step 2's REST check is the real one).

## Step 4. Import
**Approval:** the person must approve the environment, the task and the exact value set and values; a brief that names them and says proceed is the approval (note it in your work folder).
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_APPLCORE_VALUE_SETS --task-name "Manage Applications Core Value Sets" \
  --zip-file "<RUN>/payload/value_set_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 25 to 45 s. `StatusCode: (unknown)` is normal; the real result is only in `<RUN>/import_result/*_process_log.txt`. Read it with
  `python -I -c "import sys; print(open(sys.argv[1],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<log file>"`
- Success (VERIFIED): `Business object: Application Flexfield Value Set. Status: Completed successfully.` and `ValueSetSD.xml ... A total of 3 rows were processed. 0 rows of them failed` (1 value set + 2 values), `Total Objects Failed: 0`.
- Failure seen (VERIFIED): `Status: Completed with errors` and `ORA-01400: cannot insert NULL` when ModuleId was empty. Note that the detail line can still say `Completed successfully ... 0 rows were processed`: always check `Total Objects Failed`. Fix one thing, retry at most 3 times; never import twice while one is still running.

## Step 5. Read back two ways
**A. REST (FSCR value-sets resources).** The REST key of a value set is its **code**, not the numeric `ValueSetId` (VERIFIED: the numeric id gives HTTP 404).
```bash
python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource valueSets --q "ValueSetCode='<VS>'" \
  --fields ValueSetId,ValueSetCode,ValidationType,ValueDataType,ValueSubtype,MaximumLength,UppercaseOnlyFlag,Description \
  --out "<RUN>/readback_vs.json" --expect "ValueSetCode=<VS>,ValidationType=INDEP,ValueDataType=VARCHAR2,MaximumLength=20" --expect-count 1
python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource "valueSets/<VS>/child/values" \
  --fields Value,Description,EnabledFlag,SortOrder --out "<RUN>/readback_after.json" \
  --expect "Value=<V1>,EnabledFlag=Y" --expect "Value=<V2>,EnabledFlag=Y" --expect-count 2
```
Both must print `READBACK: PASS`. VERIFIED

**B. Second export and compare:** repeat Step 1 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "FND_APP_FLEX_VALUE_SET.csv=ValueSetCode" --key "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=FND_APP_FLEX_VALUE_SET.ValueSetCode,Value" \
  --expect "FND_APP_FLEX_VALUE_SET.csv=<VS>" --expect "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=<VS>,<V1>" --expect "ORA_FND_APP_FLEX_VALUE_SET_VALUE.csv=<VS>,<V2>"
```
VERIFIED: with the Applications Core ModuleId the new value set **does** appear in the scoped export, so `RESULT: PASS` (0 -> 1 value set, 0 -> 2 values). Other test value sets created the same way will also be in the export, so counts grow.

Evidence (optional): `python -B "<H>/render_readback.py" --json <readback json> --title "..." --png <file.png>`.

## Rules and limits
1. New records only; never import a full export (matching codes would update a value set or value).
2. Keep all 7 files, metadata XML unchanged.
3. Values in an existing value set: FSCR's REST `POST valueSets/{code}/child/values` exists (FROM FSCR `references/value-sets.md`) but was not used here. This card does not add values to existing value sets.
4. Tested: independent, character, 2 values. Not tested: table-validated, dependent, number or date value sets, security, translations.
5. Test records may stay for good; this card never deletes. Record every value set and value you create.
6. Tested on one environment (release 11.13.26.10.0).
7. Python flags: `-B` without `-I` for FSCR scripts, `rest_read.py`, `render_readback.py`; `-I` for the file-only helpers.

## Worked example (VERIFIED, 2026-11-20). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 7 files, 0 rows (scoped) |
| Module id + before-read | ModuleId from `YES_NO`; `GAPFILL_VS_T1`: 0 rows, PASS |
| Import | attempt 1 failed (ModuleId empty, ORA-01400); attempt 2 with ModuleId: 3 rows, 0 failed |
| REST read-back | value set INDEP / VARCHAR2 / TEXT / 20 / upper case: PASS; values `GAPFILL_A`, `GAPFILL_B` enabled: PASS |
| Export after + compare | 1 value set, 2 values added; removed 0, changed 0: PASS |
