---
skill_id: "gosaas.gap-fills.common-features.manage-conversion-rate-types"
name: "Manage Conversion Rate Types (GoSaaS gap fill)"
description: "Create a new General Ledger conversion rate type through FSCR's setup-task CSV export and import (GL_DAILY_CONVERSION_TYPE + ORA_GL_CONVERSION_RATE_RULE package), then read it back by REST (currencyConversionTypesLOV) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 3, 2026-11-20. Written and tested live on one test environment. NOT official FSCR."
tested_by_fresh_chat: "See gap_index.csv (fresh_claude_pass) and CHANGELOG.md"
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_MANAGE_CONVERSION_RATE_TYPES"
task_name: "Manage Conversion Rate Types"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
inputs:
  - "fusion_environment_context"
  - "new_rate_type_name_and_flags"
outputs:
  - "csv_package_zip"
  - "import_process_log"
  - "rest_readback_json"
  - "export_compare_result"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import process that creates a new conversion rate type. It may not be deletable and shows in every rate type list of values; plan as if it stays."
required_privileges:
  - "Export Import Functional Setups User plus the task privileges for GL_MANAGE_CONVERSION_RATE_TYPES, and read access to the currencyConversionTypesLOV REST resource"
---

# Manage Conversion Rate Types (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's export and import scripts in place and does not edit any FSCR file. It uses the generic helper scripts of the GoSaaS gap skill `manage-docseq-categories` (same recipe as journal categories).
> Labels: **VERIFIED** = seen in our live test (2026-11-20) · **FROM FSCR** = FSCR file · **GUESS** = judgment, not tested.

## What this setup is
A conversion rate type (for example Corporate, Spot or User) names a kind of exchange rate. Daily rates are stored per rate type, and ledgers, journals and subledgers pick a rate type when they convert foreign currency. Optional settings: cross-rate calculation through a pivot currency, with rules per currency pair (the second file). Daily Rates (`GL_MANAGE_DAILY_RATES`) needs a rate type first.

## When to use
- Someone asks to create a **new** conversion rate type for task `GL_MANAGE_CONVERSION_RATE_TYPES`.
- Do **not** use it to change or remove existing rate types or cross-rate rules. New records only.
- This skill was tested **without** cross rates (no pivot currency, no rule rows). Cross-rate rows are described below as GUESS.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties
          (in a downloaded pack it is often a folder named fscr-main INSIDE another fscr-main). Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (the generic helpers this skill uses)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix (GAPFILL_ in our tests)
NAME    = new rate type name (UserConversionType), e.g. GAPFILL_CRT_<something>; max 30 characters
DESC    = description (max 240, GUESS)
```
Pick a name that does not exist yet. Do not reuse the worked-example name at the end.

## Step 0. Run FSCR in place, safely
- Run FSCR scripts with their full path and `python -B`; always pass `--output-dir` under `RUN`.
- **Git Bash on Windows:** paths as `E:/folder/...`, not `/e/folder/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.
- Never print tokens, headers, the sign-in URL or the server address.

## Step 1. Sign in (only if needed)
Run Step 2 (the export) first; it also tells you whether the saved token works. If it says HTTP 401/403 or the token expired, or a REST call hangs with no output (the client is then waiting for a browser sign-in: the token lasts about an hour), sign in as in FSCR `core/auth/fusion-oauth-authentication` (values in `FSCR/core/auth/fusionEnv.properties`), run in the background:
```bash
cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600
```
A person signs in on the browser tab (`Login complete for standard.`). Never read or type credentials. Sign-in time is waiting time.

## Step 2. Read-only export (layout + names in use)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code GL_MANAGE_CONVERSION_RATE_TYPES --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
Expect 3 files (VERIFIED, about 25 seconds):
- `GL_DAILY_CONVERSION_TYPE.csv`, 32 columns: `UserConversionType, LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, LastUpdateLogin, Description, Attribute1..Attribute15, FemEnabledFlag, FemScenario, FemRateTypeCode, FemTimeframe, SecurityFlag, PivotCurrencyCode, EnforceInverseRateFlag, UserOverrideCrossRateFlag, EnableCrossRateFlag, AttributeCategory`
- `ORA_GL_CONVERSION_RATE_RULE.csv`, 9 columns: `GL_DAILY_CONVERSION_TYPE.UserConversionType, FromCurrency, ToCurrency, EnabledFlag, LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, LastUpdateLogin`
- `ASM_SETUP_CSV_METADATA.xml`
- The export holds all rate types, seeded ones too (VERIFIED: the 4 seeded types were in it). There is no internal code column: Oracle makes the internal code itself. If the export fails or lacks these files: **stop**, note it, do not import.

## Step 3. Before-read by REST
```bash
python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource currencyConversionTypesLOV \
  --q "UserConversionType='<NAME>'" --fields UserConversionType,Description \
  --out "<RUN>/readback_before.json" --expect-absent
```
Want `0 row(s)` and `READBACK: PASS`. Exit 2 / HTTP 401/403 = sign-in or privilege problem, not "absent". Run without `-I`.

## Step 4. Build a package with only the new rate type
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name rate_type_new.zip --prefix <PREFIX> \
  --key "GL_DAILY_CONVERSION_TYPE.csv=UserConversionType" \
  --key "ORA_GL_CONVERSION_RATE_RULE.csv=GL_DAILY_CONVERSION_TYPE.UserConversionType,FromCurrency,ToCurrency" \
  --prefix-col "GL_DAILY_CONVERSION_TYPE.csv=UserConversionType" \
  --max-len "UserConversionType=30" --max-len "Description=240" \
  --row "GL_DAILY_CONVERSION_TYPE.csv|UserConversionType=<NAME>|Description=<DESC>|SecurityFlag=N|EnforceInverseRateFlag=Y|UserOverrideCrossRateFlag=N|EnableCrossRateFlag=N"
```
- These 4 flags are what the seeded types carry; with them the row imported cleanly. Leave every other column empty (no pivot currency, no audit columns). VERIFIED
- The rule file goes into the package with only its header. VERIFIED (the log then says the rule object "was already processed").
- **Cross rates (GUESS, not tested):** set `EnableCrossRateFlag=Y` and `PivotCurrencyCode=<an existing currency code>`, and add one `--row "ORA_GL_CONVERSION_RATE_RULE.csv|GL_DAILY_CONVERSION_TYPE.UserConversionType=<NAME>|FromCurrency=<code>|ToCurrency=<code>|EnabledFlag=N"` per rule, copying the pattern of existing rule rows in the export.
- The helper stops if the name is already in the export (importing it would **update** that rate type), lacks the prefix, or is too long.

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact name before the import. If their brief already names all three and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code GL_MANAGE_CONVERSION_RATE_TYPES --task-name "Manage Conversion Rate Types" \
  --zip-file "<RUN>/payload/rate_type_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 40 seconds. VERIFIED. The real result is only in `<RUN>/import_result/*_process_log.txt` (one long line with literal `\r\n`); read it with
  `python -I -c "import sys; print(open(sys.argv[1],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<log file>"`
- Success: `Business object: Conversion Rate Type. Status: Completed successfully.`, `A total of 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`. VERIFIED
- Not complete yet: keep the ProcessId and use FSCR's `get_setup_task_csv_import_result.py`; do not import twice. Rows failed: copy the error, change one thing, retry at most 3 times.

## Step 6. Read back two ways
**A. REST:**
```bash
python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource currencyConversionTypesLOV \
  --q "UserConversionType='<NAME>'" --fields UserConversionType,Description \
  --out "<RUN>/readback_after.json" --expect "UserConversionType=<NAME>,Description=<DESC>" --expect-count 1
```
`READBACK: PASS` = exactly one rate type with your name and description. The LOV shows only name, description and an id; the flags are checked in B. VERIFIED

**B. Second export and compare:** repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "GL_DAILY_CONVERSION_TYPE.csv=UserConversionType" \
  --key "ORA_GL_CONVERSION_RATE_RULE.csv=GL_DAILY_CONVERSION_TYPE.UserConversionType,FromCurrency,ToCurrency" \
  --expect "GL_DAILY_CONVERSION_TYPE.csv=<NAME>" --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your rate type was added (and no rule rows), nothing removed, no existing row changed. `added_rows.csv` shows the flags Oracle stored. VERIFIED. (If you added rule rows, add one `--expect "ORA_GL_CONVERSION_RATE_RULE.csv=<NAME>,<from>,<to>"` each.)

**Evidence (optional):** `python -B "<H>/render_readback.py" --json <readback json> --title "..." --png <file.png>`.

## Rules and limits
1. **New records only.** Never import a full export: a matching `UserConversionType` would update that rate type.
2. **Keep all 3 files** in the package, metadata XML unchanged, the rule file with its header even when empty.
3. **Name:** max 30 characters (GUESS from the screen; 14 tried). Use your test prefix.
4. **Test records may stay for good**, and a new rate type shows in every rate type list (journals, revaluation, daily rates). This skill never deletes. Record every created rate type in your change log.
5. **Tested on one environment** (release 11.13.26.10.0), without cross rates.
6. **Python flags.** `-B`, no `-I`: FSCR scripts, `rest_read.py`, `render_readback.py`. `-I`: `inspect_export.py`, `build_fsm_package.py`, `compare_fsm_exports.py`, the unzip one-liner.

## Worked example (VERIFIED, 2026-11-20). Do not reuse this name; it now exists.
| Step | Result |
|---|---|
| Export before | 13 rate types, 10 rules; 23 s |
| Before-read | `GAPFILL_CRT_T1`: 0 rows, PASS |
| New record | `GAPFILL_CRT_T1`, "GoSaaS gap-fill test rate type", flags N/Y/N/N, no pivot, no rules |
| Import | 1 attempt, 37 s: 1 row processed, 0 failed |
| REST read-back | 1 row, name and description match: PASS |
| Export after + compare | 14 rate types, 10 rules; added 1, removed 0, changed 0: PASS |
