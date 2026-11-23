---
skill_id: "gosaas.gap-fills.common-features.manage-standard-lookups"
name: "Manage Applications Core Standard Lookups (GoSaaS gap fill)"
description: "Create a new standard lookup type with new codes through FSCR's setup-task CSV export and import (FND_APP_STANDARD_LOOKUP package), then read it back with FSCR's generic lookups skill (REST) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 1, 2026-11-20. Written and tested live on one test environment. NOT official FSCR."
tested_by_fresh_chat: "See gap_index.csv (fresh_claude_pass) and CHANGELOG.md"
layer: "pillar"
pillar: "Common"
offering: "Common Features"
functional_area: "Application Extensions"
task_code: "FND_MANAGE_APPLCORE_STANDARD_LOOKUPS"
task_name: "Manage Applications Core Standard Lookups"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
inputs:
  - "fusion_environment_context"
  - "new_lookup_type_and_codes"
outputs:
  - "csv_package_zip"
  - "import_process_log"
  - "rest_readback_json"
  - "export_compare_result"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.apps-common.lookups"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import process that creates one new lookup type and its codes. Created lookups may not be deletable; plan as if they stay."
required_privileges:
  - "Export Import Functional Setups User plus the task privileges for FND_MANAGE_APPLCORE_STANDARD_LOOKUPS, and read access to the standardLookups REST resource"
reused_by:
  - "common-features/manage-geography-lookups (HZ_MANAGE_GEOGRAPHY_LOOKUPS)"
  - "common-features/manage-resource-note-type (HZ_MANAGE_RESOURCE_NOTE_TYPE)"
---

# Manage Applications Core Standard Lookups (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a generic lookups skill (`core/fusion-api/apps-common/lookups`) but no skill for this setup task code. This skill uses FSCR's scripts in place and does not edit any FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-20) · **FROM FSCR** = FSCR file · **FROM ORACLE DOCS** = link · **GUESS** = judgment, not tested.

## What this setup is
A standard lookup type is a named list of codes (for example a list of sample types) that screens and flexfields use as a list of values. Each code has a meaning (display text), an enabled flag and an order. FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/applications-common/26c/farca/api-standard-lookups.html

## When to use
- Someone asks to create a **new** standard lookup type with codes for task `FND_MANAGE_APPLCORE_STANDARD_LOOKUPS` ("Manage Applications Core Standard Lookups").
- Do **not** use it to change or remove existing lookup types or codes. New records only.
- Other tasks that export the same two files (`FND_APP_STANDARD_LOOKUP.csv`, `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv`) can reuse this recipe: change the task code and see their card.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\, pillars\ and core\auth\fusionEnv.properties
          (in a downloaded pack it is often a folder named fscr-main INSIDE another fscr-main). Read only, never edit.
SKILL   = the folder of this SKILL.md
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix (GAPFILL_ in our tests). Every new type and code must start with it.
TYPE    = new lookup type, e.g. GAPFILL_SL_<something>  (upper case, digits, _ ; max 30 characters)
CODE1.. = new codes, e.g. GAPFILL_A (same rules). Meanings: max 80 characters, unique in the type.
```
Pick names that do not exist yet. Do not reuse names from the worked example at the end.

## Step 0. Run FSCR in place, safely
- Run FSCR scripts with their full path and `python -B` (no `__pycache__` inside FSCR).
- Always pass `--output-dir` under `RUN`, or the export writes inside `FSCR\project\...`.
- **Git Bash on Windows:** write paths as `E:/folder/...` (drive letter form), not `/e/folder/...`. Python receives `/e/...` as `\e\...` and creates a stray folder `E:\e\...`. VERIFIED (it happened once in our test). Set `PYTHONUTF8=1`.
- Never print tokens, headers or the sign-in URL.

## Step 1. Sign in (only if needed)
1. Try Step 3's before-read first. If it says HTTP 401/403 or the token expired, sign in.
2. FROM FSCR `core/auth/fusion-oauth-authentication`: the values belong in `FSCR/core/auth/fusionEnv.properties` (environment, restBaseUrl, clientId, redirectUrl, scope). Then:
   ```bash
   cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600
   ```
   Run it in the background. The person signs in on the browser tab; the script prints `Login complete for standard.` VERIFIED. A person must do the sign-in; never read or type credentials. If the browser cannot reach the 127.0.0.1 callback, stop and ask the person; FSCR's manual route (`--auth-code`, which also needs `--code-verifier` with PKCE) is described in FSCR `core/auth/fusion-oauth-authentication/SKILL.md` and was not tried here (GUESS).
3. Sign-in time is waiting time, not task time.

## Step 2. Read-only export (layout + names already in use)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code FND_MANAGE_APPLCORE_STANDARD_LOOKUPS --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "<zip it printed>" "<RUN>/export_before/unz"
```
- The ZIP is named `<ENV>_setup_task_csv_export_<task code lower case>_<processId>.zip`; take the exact path from the `Wrote ...` line.
- Expect 3 files: `ASM_SETUP_CSV_METADATA.xml`, `FND_APP_STANDARD_LOOKUP.csv` (15 columns), `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv` (14 columns). VERIFIED. About 1 to 1.5 minutes. VERIFIED
- If the export fails or has no lookup files: **stop**, note it, do not import.
- **The export is scoped, not every lookup.** Its metadata XML has scope `moduleType=APPLICATION`, `moduleKey=FND`, and the rows are user-defined types (`CustomizationLevel=U`) of that one module. Seeded types are not in it. VERIFIED. So a missing name in the export does not prove the name is free: Step 3 checks by REST too.
- Every row of one task's export shares one `ModuleId` (the module the task manages). VERIFIED. The helper copies it.

- Row counts grow with every run (each test adds its type), and the export may hold other teams' test types. That is normal.

## Step 3. Before-read with FSCR's generic lookups skill (REST, read-only)
Steps 2 and 3 can run in either order. Running Step 3 first also tells you whether sign-in is needed. `read_lookup.py` can run from any folder; it finds FSCR from `--fscr`.
FROM FSCR `core/fusion-api/apps-common/lookups/references/standard-lookups.md`: `GET /fscmRestApi/resources/11.13.18.05/standardLookups/{LookupType}?expand=lookupCodes` through `core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`. Our wrapper calls exactly that and checks the result:
```bash
python -B "<SKILL>/scripts/read_lookup.py" --fscr "<FSCR>" --type <TYPE> --out "<RUN>/readback_before.json" --expect-absent
```
- Run it **without** `-I` (FSCR sign-in needs `pywin32` from the user site-packages on Windows).
- Want `NOT FOUND (HTTP 404)` and `READBACK: PASS`. If the type exists, pick another name. HTTP 401/403 = sign-in or privilege problem, not "absent".

## Step 4. Build a package with only the new type and codes
```bash
python -I "<SKILL>/scripts/build_lookup_package.py" \
  --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --prefix <PREFIX> \
  --type "<TYPE>|<type meaning>|<type description>" \
  --code "<CODE1>|<meaning 1>|<description 1>" --code "<CODE2>|<meaning 2>|<description 2>" \
  --zip-name std_lookup_new.zip
```
What it writes (VERIFIED, this exact shape imported cleanly):
- Type row: `LookupType`, `Meaning`, `Description`, `ModuleId` (from the export), `CustomizationLevel=U`, `RestAccessSecured=SECURE`; all other columns empty (no audit columns, no dates).
- Code rows: `FND_APP_STANDARD_LOOKUP.LookupType` = TYPE, `LookupCode`, `Meaning`, `Description`, `EnabledFlag=Y`, `DisplaySequence` 1, 2, ...; dates empty (no start/end date worked).
- The metadata XML copied unchanged; every field quoted, UTF-8, no BOM.
- It stops if: a name lacks the prefix, is not upper case/digits/_, is over 30 characters; a meaning is empty, over 80, or repeated; the type is already in the export (importing it would **update** it); more than 3 codes (`--max-codes`); or the export has no rows and you gave no `--module-id` (see the geography and note-type cards for that case).

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact type and codes before the import. If their brief already names all three and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code FND_MANAGE_APPLCORE_STANDARD_LOOKUPS --task-name "Manage Applications Core Standard Lookups" \
  --zip-file "<RUN>/payload/std_lookup_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 20 to 30 seconds. VERIFIED. The script prints `StatusCode: (unknown)` even on success; the real result is only in `<RUN>/import_result/*_process_log.txt` (one long line with literal `\r\n`).
- To read the log: `python -I -c "import sys; print(open(sys.argv[1],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<log file>"`. Times in the log are in the server's time zone (UTC in our test), not local time.
- Success looks like: `Business object: Application Standard Lookup. Status: Completed successfully.` and `A total of N rows were processed. 0 rows of them failed` where N = 1 type + number of codes, and `Total Objects Failed: 0`. VERIFIED
- If it says the process is not complete yet, keep the ProcessId and use FSCR's `get_setup_task_csv_import_result.py`; do not import twice. If rows failed, copy the error, change one thing, retry at most 3 times.

## Step 6. Read back two ways
**A. REST read (FSCR generic lookups skill):**
```bash
python -B "<SKILL>/scripts/read_lookup.py" --fscr "<FSCR>" --type <TYPE> --out "<RUN>/readback_after.json" \
  --expect-meaning "<type meaning>" --expect-code "<CODE1>|<meaning 1>" --expect-code "<CODE2>|<meaning 2>"
```
`READBACK: PASS` = type found, meaning matches, exactly these codes with these meanings. VERIFIED (the new type also came back with the export's ModuleId and level U).

**B. Second export and compare (offline):** repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip to `<RUN>/export_after/unz`, then
```bash
python -I "<SKILL>/scripts/compare_lookup_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --expect-type <TYPE> --expect-code <CODE1> --expect-code <CODE2>
```
`RESULT: PASS` = only your type and codes were added, nothing removed, no existing row changed. VERIFIED

**Evidence (optional):** `python -B "<SKILL>/scripts/render_readback.py" --json <readback json> --title "..." --png <file.png>` draws the read-back as an image with no secrets (needs Pillow; run without `-I`).

## Rules and limits
1. **New records only.** Never import a full export; a matching LookupType or code would update that record. The helper refuses names already in the export, and Step 3 checks REST.
2. **Keep all 3 files** in the package, metadata XML unchanged.
3. **Names.** Type and code: upper case letters, digits, `_`, max 30 characters (GUESS from Oracle's lookup screens; names up to 17 characters were tried). A code must be unique within its type (the key is type + code); starting codes with your type's short name avoids any doubt. Meaning max 80. Use your test prefix.
4. **Test records may stay for good.** This skill never deletes. Record every created type and code in your change log.
5. **Language.** Only the session language was used; the package has no translation file. GUESS: other languages need the UI or REST translations.
6. **Tested on one environment** (release 11.13.26.10.0). Other releases are untested.
7. **Python flags.** `-B` for FSCR scripts and `read_lookup.py` / `render_readback.py` (no `-I`); `-I` for `build_lookup_package.py`, `compare_lookup_exports.py` and the unzip one-liner.

## Worked example (VERIFIED, 2026-11-20). Do not reuse these names; they now exist.
| Step | Result |
|---|---|
| Export before | 16 types, 36 codes, one ModuleId; 78 s |
| Before-read | `GAPFILL_SL_T1`: HTTP 404, PASS |
| New records | type `GAPFILL_SL_T1` "GAPFILL SL T1 Lookup"; codes `GAPFILL_A` "GAPFILL SL T1 Alpha", `GAPFILL_B` "GAPFILL SL T1 Beta" |
| Import | 1 attempt, 22 s: 3 rows processed, 0 failed |
| REST read-back | found, 2 codes, meanings match: PASS |
| Export after + compare | 17 types, 38 codes; added 1 type + 2 codes, removed 0, changed 0: PASS |
