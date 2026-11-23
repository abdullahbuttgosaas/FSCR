---
skill_id: "gosaas.gap-fills.common-features.manage-tax-lookup-codes"
name: "Manage Tax Lookup Codes (GoSaaS gap fill)"
description: "Create a new Financials generic lookup type with new codes for the tax module through FSCR's setup-task CSV export and import (ORA_FINANCIALS_GENERIC_LOOKUP_TYPE + FUN_APP_GENERIC_LOOKUP package, 4 CSVs), then read it back with FSCR's generic lookups skill (REST) and a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 2, 2026-11-20. Written and tested live on one test environment. NOT official FSCR."
tested_by_fresh_chat: "See gap_index.csv (fresh_claude_pass) and CHANGELOG.md"
layer: "pillar"
pillar: "Common"
offering: "Common Features"
functional_area: "Transaction Tax"
task_code: "ORA_ZX_MANAGE_TAX_LOOKUP_CODES"
task_name: "Manage Tax Lookup Codes"
available_flag: "Y"
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
  - "Starts one setup-task CSV import process that creates one new lookup type and its codes in the tax module. Created lookups may not be deletable; plan as if they stay."
  - "RISK: tax lookup codes can appear in tax screens and lists of values for ALL users of the environment (see Rules 1 and 2)."
required_privileges:
  - "Export Import Functional Setups User plus the task privileges for ORA_ZX_MANAGE_TAX_LOOKUP_CODES, and read access to the setEnabledLookups / standardLookups REST resources"
reused_by:
  - "common-features/manage-le-configurator-lookups (XLE_MANAGE_APPLICATION_LOOKUP)"
---

# Manage Tax Lookup Codes (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has a generic lookups skill (`core/fusion-api/apps-common/lookups`) but no skill for this setup task code. This skill uses FSCR's scripts in place and does not edit any FSCR file.
> This is the **Financials generic lookup** package (4 CSVs). It is **not** the standard lookup package used by `manage-standard-lookups` (2 CSVs); do not mix the two recipes.
> Labels: **VERIFIED** = seen in our live test (2026-11-20) · **FROM FSCR** = FSCR file · **FROM ORACLE DOCS** = link · **GUESS** = judgment, not tested.

## What this setup is
Tax lookup types are named lists of codes used by the tax module, for example input and output tax classifications or tax partner names. Most tax lookups are **set-enabled** (each code belongs to a reference data set, such as `COMMON`); a few are **standard** (no set). The setup task exports both kinds through one package. FROM ORACLE DOCS: https://docs.oracle.com/en/cloud/saas/applications-common/26c/farca/api-set-enabled-lookups.html

## When to use
- Someone asks to create a **new** lookup type with codes in the tax module for task `ORA_ZX_MANAGE_TAX_LOOKUP_CODES` ("Manage Tax Lookup Codes").
- Do **not** use it to change or remove existing lookup types or codes, and do not use it to add codes to seeded tax types in a test (Rule 1). New records only.
- Other tasks that export the same 4 files (`ORA_FINANCIALS_GENERIC_LOOKUP_TYPE*.csv`, `FUN_APP_GENERIC_LOOKUP*.csv`) can reuse this recipe: change the task code and see their card.

## Placeholders used below
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\, pillars\ and core\auth\fusionEnv.properties
          (in a downloaded pack it is often a folder named fscr-main INSIDE another fscr-main). Read only, never edit.
SKILL   = the folder of this SKILL.md
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix (GAPFILL_ in our tests). Every new type and code must start with it.
TYPE    = new lookup type, e.g. GAPFILL_TAX_<something>  (upper case, digits, _ ; max 30 characters)
CODE1.. = new codes, e.g. GAPFILL_TAX_<x> (same rules). Meanings: max 80 characters, unique in the type.
VIEW    = set-enabled (normal for tax lookups) or standard
REFGRP  = reference group of a set-enabled type (read by REST in Step 3)
SET     = reference data set code for the new codes (COMMON unless the person names another set)
```
Pick names that do not exist yet. Do not reuse names from the worked example at the end.

## Step 0. Run FSCR in place (no copy, no edit)
- Run FSCR scripts with their full path and `python -B` (no `__pycache__` inside FSCR).
- Always pass `--output-dir` under `RUN`, or the export writes inside `FSCR\project\...`.
- **Git Bash on Windows, two traps** (both VERIFIED):
  1. Write paths as `E:/folder/...`, not `/e/folder/...` (Python gets `\e\...` and makes a stray folder).
  2. `export MSYS_NO_PATHCONV=1` before calling FSCR's REST client directly with a path like `/fscmRestApi/...`; otherwise Git Bash rewrites it to a Windows folder and the client says `REST URL must have a valid HTTPS authority`. The helper scripts here are not affected.
- Set `PYTHONUTF8=1`. Never print tokens, headers or the sign-in URL.

## Step 1. Sign in (only if needed)
1. Try Step 3's before-read first. If it exits 2 with HTTP 401/403 or "token expired", sign in.
2. FROM FSCR `core/auth/fusion-oauth-authentication`: the values belong in `FSCR/core/auth/fusionEnv.properties` (environment, restBaseUrl, clientId, redirectUrl, scope). Then run in the background:
   ```bash
   cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600
   ```
   A person signs in on the browser tab; the script prints `Login complete`. Never read or type credentials. If the browser cannot reach the 127.0.0.1 callback, stop and ask the person (FSCR's SKILL.md describes the manual `--auth-code` route).
3. Sign-in time is waiting time, not task time.

## Step 2. Read-only export (layout, module values, names in use)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_TAX_LOOKUP_CODES --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "<zip it printed>" "<RUN>/export_before/unz"
```
- The ZIP is named `<ENV>_setup_task_csv_export_ora_zx_manage_tax_lookup_codes_<processId>.zip`; take the path from the `Wrote ...` line. About 30 seconds. VERIFIED
- The export also prints `No matching pillar setup-task metadata found...` and `StatusCode: (unknown)` when it succeeds. Both are normal; success = the `Wrote ...zip` line. VERIFIED
- Some existing codes hold non-ASCII characters (for example a dash) that look garbled in a Windows console. Harmless; read the CSVs as UTF-8.
- Expect 5 files (VERIFIED):

| File | Columns | Holds |
|---|---:|---|
| `ORA_FINANCIALS_GENERIC_LOOKUP_TYPE.csv` | 20 | user-defined types of the module only (seeded types are NOT exported; 0 rows is normal on a fresh environment; every earlier test adds its type, so counts grow) |
| `ORA_FINANCIALS_GENERIC_LOOKUP_TYPE_TRANSLATION.csv` | 14 | one row per type and language |
| `FUN_APP_GENERIC_LOOKUP.csv` | 37 | codes, key = LookupType + LookupCode + ViewApplicationId + SetCode (also codes the customer added to seeded types) |
| `FUN_APP_GENERIC_LOOKUP_TRANSLATION.csv` | 17 | one row per code and language |
| `ASM_SETUP_CSV_METADATA.xml` | | scope: `moduleType` + `moduleKey` (the tax module) and `mode=search` |

- `ViewApplicationId` tells the kind: **2 = set-enabled** (codes carry a `SetCode`), **0 = standard** (SetCode still shows `COMMON`). VERIFIED by REST: a type with 2 is found under `setEnabledLookups`, a type with 0 under `standardLookups`.
- All code rows share one `ModuleId`, `ModuleKey` and `ModuleType`. The helper copies them. VERIFIED
- If the export fails or holds none of the 4 CSVs: **stop**, note it, do not import.
- A missing name in the export does not prove the name is free: Step 3 checks by REST.

## Step 3. Before-read with FSCR's generic lookups skill (REST, read-only)
FROM FSCR `core/fusion-api/apps-common/lookups` (references `set-enabled-lookups.md`, `standard-lookups.md`, `common-lookups.md`). The wrapper uses FSCR's `fusion_rest_client.py` in place; run it **without** `-I` (FSCR sign-in needs `pywin32` from the user site-packages on Windows).

**3a. Reference group** (only for VIEW = set-enabled). Take a seeded set-enabled type from the export (a `LookupType` whose rows have `ViewApplicationId` 2 and that does not start with your test prefix, e.g. an input or output tax classification type) and read it:
```bash
python -B "<SKILL>/scripts/read_generic_lookup.py" --fscr "<FSCR>" --info-of <an existing type from the export>
```
It prints `view=set-enabled ModuleId=... ReferenceGroupName=...`. Use that `ReferenceGroupName` as REFGRP. VERIFIED. (For tax classification types the group is the tax classification codes group.)

**3b. Name is free:**
```bash
python -B "<SKILL>/scripts/read_generic_lookup.py" --fscr "<FSCR>" --type <TYPE> --out "<RUN>/readback_before.json" --expect-absent
```
Want HTTP 404 in all three views and `READBACK: PASS`. Exit 2 = sign-in or privilege problem, not "absent". Checking the type name is enough: codes are unique within their type, so codes of a new type cannot clash.

## Step 4. Build a package that holds only the new rows
```bash
python -I "<SKILL>/scripts/build_generic_lookup_package.py" \
  --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --prefix <PREFIX> \
  --view set-enabled --reference-group <REFGRP> --set-code <SET> \
  --type "<TYPE>|<type meaning>|<type description>" \
  --code "<CODE1>|<meaning 1>|<description 1>" \
  --zip-name tax_lookup_new.zip
```
For a standard type use `--view standard` and no `--reference-group`. If the export has no code rows, also pass `--module-id`, `--module-key`, `--module-type` (see the LE lookups card).

What it writes (VERIFIED, this exact shape imported cleanly):
- Type row: `LookupType`, `ViewApplicationId` (2 or 0), `Meaning`, `Description`, `ModuleId`, `ModuleKey`, `ModuleType`, `CustomizationLevel=U`, `RestAccessSecured=SECURE`, `ReferenceGroupName` (set-enabled only), `ChangeSinceLastRefresh=N`. One type translation row (language from the export, else `US`).
- Code rows: `LookupType`, `LookupCode`, `ViewApplicationId`, `SetCode`, `Meaning`, `Description`, `EnabledFlag=Y`, `DisplaySequence` 1, 2, ..., module columns, `ChangeSinceLastRefresh=N`; dates empty. One translation row per code.
- **`ChangeSinceLastRefresh` is required in all 4 files.** Left empty, the import fails with `JBO-27014: Attribute ChangeSinceLastRefresh ... is required`. VERIFIED (our first attempt).
- Metadata XML copied unchanged; every field quoted, UTF-8, no BOM.
- It stops if: a name lacks the prefix, is not upper case/digits/_, is over 30 characters; a meaning is empty, over 80, or repeated; the type is already in the export (importing it would **update** it); set-enabled without a reference group; more than 3 codes (`--max-codes`).

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact type and codes before the import, knowing Rule 2 (codes may be visible to all users). If their brief already names all of this and says to proceed, that is the approval; say so in your final report (and in the task's CHANGELOG.md if you keep one).
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_TAX_LOOKUP_CODES --task-name "Manage Tax Lookup Codes" \
  --zip-file "<RUN>/payload/tax_lookup_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 30 to 40 seconds. VERIFIED. The script prints `StatusCode: (unknown)` even on success; the real result is only in `<RUN>/import_result/*_process_log.txt` (one long line with literal `\r\n`).

## Step 6. Read the result
```bash
python -I -c "import sys; print(open(sys.argv[1],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<log file>"
```
- Success (VERIFIED): business object `Financials Generic Lookup`, detail objects `LookupTypeGeneric1` and `LookupGeneric1` each `A total of N rows were processed. 0 rows of them failed` (N = 1 for the type; N = number of codes), `Total Objects Failed: 0`, request `Completed successfully`.
- Errors show as `Row Identifier: ... JBO-...`. The type batch runs first; if it fails, the codes fail too. Copy the error, change one thing, retry at most 3 times. If the process is not complete yet, keep the ProcessId and use FSCR's `get_setup_task_csv_import_result.py`; do not import twice.
- Times in the log are the server's time zone, not local time.

## Step 7. Verify two ways
**A. REST read (FSCR generic lookups skill):**
```bash
python -B "<SKILL>/scripts/read_generic_lookup.py" --fscr "<FSCR>" --view set-enabled --type <TYPE> \
  --out "<RUN>/readback_after.json" --expect-meaning "<type meaning>" \
  --expect-code "<CODE1>|<meaning 1>" --expect-set <SET>
```
For several codes repeat `--expect-code`; in Step 7B list them after `--require-codes` separated by spaces. VERIFIED

`READBACK: PASS` = type found in that view, meaning matches, exactly these codes, with these meanings, enabled, in that set. VERIFIED (it also showed level `U` and the reference group).

**B. Second export and compare (offline):** repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip to `<RUN>/export_after/unz`, then
```bash
python -I "<SKILL>/scripts/compare_generic_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --expect-type <TYPE> --require-codes <CODE1>
```
`RESULT: PASS` = only rows of your type were added (type, type translation, codes, code translations), nothing removed, no existing row changed. VERIFIED (the new user-defined type does appear in the after export).

**Evidence (optional):** `python -B "<SKILL>/scripts/render_readback.py" --json <readback json> --title "..." --png <file.png>` draws a read-back as an image with no secrets (needs Pillow; run without `-I`).

## Rules and limits
1. **New type for tests; never add test codes to seeded tax types.** A code added to a seeded type (for example an input or output tax classification type) shows in tax screens, tax rules and transaction lists of values **for all users** at once. That is the real business use of this task, but in a test it pollutes a shared environment. Use a new `GAPFILL_`-style type. Adding codes to a seeded type is **not tested** here (GUESS: same package, the seeded type is not in the type file, code rows only with the seeded type's ViewApplicationId and a SetCode).
2. **Visibility risk even for a new type.** A new set-enabled type in the tax module with a tax reference group can be listed in the Manage Tax Lookup Codes screen and in lookup searches for every user. Name it clearly as a test (`GAPFILL_...`, meaning "GAPFILL ...") and record it. GUESS: a new type is not used by any tax screen's list of values unless a person configures it.
3. **New records only.** Never import a full export; a matching key would update that record. The helper refuses names already in the export, and Step 3 checks REST.
4. **Keep all 5 files** in the package, metadata XML unchanged, `ChangeSinceLastRefresh=N` filled.
5. **Names.** Type and code: upper case letters, digits, `_`, max 30 characters (GUESS from Oracle's lookup screens; 14-character names tried). Meaning max 80. Use your test prefix.
6. **Test records may stay for good.** This skill never deletes. Record every created type and code in your change log.
7. **Language.** One translation row in the export's language (US in our test). Other languages: GUESS, add more translation rows with the same keys.
8. **Set.** Our test used set `COMMON`. Other sets are GUESS (the export shows codes in other sets, so the key accepts them).
9. **Tested on one environment** (release 11.13.26.10.0). Other releases are untested.
10. **Python flags.** `-B` for FSCR scripts, `read_generic_lookup.py` and `render_readback.py` (no `-I`); `-I` for `build_generic_lookup_package.py`, `compare_generic_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-20). Do not reuse these names; they now exist.
| Step | Result |
|---|---|
| Export before | 0 types, 23 codes (22 set-enabled, 1 standard), one module; 28 s (counts are higher now: our test types are in it) |
| Reference group | read from an existing set-enabled tax classification type by REST |
| Before-read | `GAPFILL_TAX_T1`: HTTP 404 in all three views, PASS |
| New records | set-enabled type `GAPFILL_TAX_T1` "GAPFILL TAX T1 Lookup"; code `GAPFILL_TAX_A` "GAPFILL TAX T1 Alpha", set COMMON |
| Import attempt 1 | failed: `ChangeSinceLastRefresh ... is required` (builder fixed) |
| Import attempt 2 | 37 s: type 1 row, codes 1 row, 0 failed |
| REST read-back | found in setEnabledLookups, level U, 1 code, set COMMON: PASS |
| Export after + compare | 1 type, 24 codes; added only GAPFILL_TAX_T1 rows in all 4 files, removed 0, changed 0: PASS |
