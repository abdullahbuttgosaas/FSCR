---
skill_id: "gosaas.gap-fills.common-features.manage-tax-zone-types"
name: "Manage Tax Zone Types (GoSaaS gap fill)"
description: "Create a new tax zone type (Trading Community geography type with use TAX) through FSCR's setup-task CSV export and import, then read it back with a second export. The who columns (CreatedBy, LastUpdatedBy) must be filled with the importing user, or the database insert fails with JBO-26041. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 2, 2026-11-23 (failed); cause found and fixed in batch taxfix2, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_TAX_ZONE_TYPES"
task_name: "Manage Tax Zone Types"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers: build_fsm_package.py, compare_fsm_exports.py, inspect_export.py)"
  - "gosaas common-features/manage-tax-zone-types/scripts/zone_type_rows.py"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new zone type (geography type, use TAX). A zone type with no zones changes no tax result. It may not be deletable; plan as if it stays."
---

# Manage Tax Zone Types (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file. It uses the generic helpers of the gap skill `manage-docseq-categories` and its own `scripts/zone_type_rows.py`.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A tax zone type is a Trading Community geography type with geography use `TAX` (for example "EU member states" or a county group). Tax zones of that type then list geographies or postal code ranges, and tax regimes or jurisdictions can use a zone. This skill creates the **zone type only** (no zones). Prerequisites: none in Oracle (no regime or tax is needed); only the FSCR sign-in.

## When to use
- Someone asks to create a **new** tax zone type for task `ZX_MANAGE_TAX_ZONE_TYPES`.
- Do **not** use it to change existing zone types or to add zones. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
Z       = <GAPS>/common-features/manage-tax-zone-types/scripts      (zone_type_rows.py)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE    = new zone type code (GeographyType), upper case letters, digits and _, starting with PREFIX
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (not `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL, the server address or user names.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.
- **Use the same sign-in for the export (Step 2) and the import (Step 5)**: the helper takes the importing user's name from the export.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_ZONE_TYPES --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz" --file ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv --cols GeographyType,GeographyUse,PostalCodeRangeFlag,CreatedByModule,GeographyTypeName
```
Expect 9 files (VERIFIED, about 40 to 165 s): `ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv` (23 columns: `GeographyType, GeographyUse, PostalCodeRangeFlag, LimitedByGeographyId, CreatedByModule, LastUpdatedBy, CreatedBy, RequestId, GeographyTypeName, GeographyName, BoundaryGeographyType, StartDate, EndDate, GeographyElement1..10`), `ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE_TRANSLATION.csv` (7), six zone/geography files (`HZ_GEOGRAPHIES_ZONE`, `ORA_HZ_GEO_ZONE_IDENTIFIER`, `ORA_HZ_GEOGRAPHY_RANGE`, `ORA_HZ_GEO_HIERARCHY_NODE`, `ORA_HZ_GEO_RELATIONSHIP`, `ORA_HZ_GEO_RELATIONSHIP_TYPE`) and `ASM_SETUP_CSV_METADATA.xml`. Zero existing zone types is fine. A good run ends with `Wrote ...zip`; that also proves the sign-in works. If the export fails or lacks these files: **stop**. If the connection drops, re-run the export into a new folder (e.g. `<RUN>/export_before2`) and use that folder wherever later steps say `export_before`.

## Step 3. Write the row
```bash
python -I "<Z>/zone_type_rows.py" --export-dir "<RUN>/export_before/unz" --code <CODE> --out "<RUN>/rows.txt"
```
- Writes one zone type row (`GeographyUse=TAX`, `PostalCodeRangeFlag=N`, `CreatedByModule=HZ_GEO_HIERARCHY`, name = code with `_` as spaces and Python title case, e.g. `GAPFILL_X_ZT1` → `Gapfill X Zt1`, `ZT4F` → `Zt4F` (accepted as is); `--name "..."` to choose) and one translation row (`--language`, default `US`). This is the shape of a zone type made on the screen. VERIFIED
- **It fills `CreatedBy` and `LastUpdatedBy`** in both rows with the export's `SubmittedBy` (the signed-in user). **This is required:** with those two columns empty the import says `GeographyType: 1 rows processed, 0 failed` and then fails with `JBO-26041: Failed to post data to database during "Insert"` on `HZ_GEOGRAPHY_TYPES_B`, and nothing is created (VERIFIED, 6 failed tries). Never type a user name in by hand and never print it.
- It stops if CODE is already in the export (importing it would **update** that zone type).
- Country limit (optional): `--limit-like "<existing zone type code>"` copies the country limit of an existing zone type in the export. **GUESS**: not tested with the who-column fix. Without it the zone type has no country limit, like a screen-made one where none was picked.

## Step 4. Build a package with only the new zone type
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name zone_type_new.zip --prefix <PREFIX> \
  --key "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv=GeographyType" \
  --prefix-col "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv=GeographyType" @"<RUN>/rows.txt"
```
Expect `1 new rows` for each of the two files; the 7 other files go in with their header only. VERIFIED

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact CODE before the import. If their brief names all three and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_TAX_ZONE_TYPES --task-name "Manage Tax Zone Types" \
  --zip-file "<RUN>/payload/zone_type_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 40 s. Keep the ProcessId it prints. `StatusCode: (unknown)` is normal; the result is only in `<RUN>/import_result/*_process_log.txt` (one line with literal `\r\n`). The log has a `Submitted By: <user>` line, so print only the result lines:
  `python -I -c "import sys,glob; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)); print(chr(10).join(l for l in t.split(chr(10)) if any(k in l for k in ('Business object','Detail Object: GeographyType','Total Objects','JBO','rror'))))" "<RUN>/import_result"`
- Success (VERIFIED): `Business object: Trading Community Geography Zone. Status: Completed successfully`, `Detail Object: GeographyType ... A total of 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0`. (The GeographyType line repeats several times; that is normal.)
- **`0 rows were processed` is a failure.** `JBO-26041` = the who columns were empty: redo Step 3 from an export made with the same sign-in. Other errors: copy the error, change one thing, retry at most 3 times.
- If the connection drops during the import: **do not import again**. First run Step 6 (new export); import again only if CODE is not there.

## Step 6. Read back (second export and compare)
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv=GeographyType" \
  --key "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE_TRANSLATION.csv=GeographyType,Language" \
  --expect "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv=<CODE>" \
  --expect "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE_TRANSLATION.csv=<CODE>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = exactly your zone type and its translation row added, nothing else changed. Check the added row has `GeographyUse=TAX`, `PostalCodeRangeFlag=N`, `CreatedByModule=HZ_GEO_HIERARCHY`. There is no REST resource for zone types (`geographyTypes`, `taxZoneTypes`, `zoneTypes`: HTTP 404, VERIFIED 2026-11-23), so the export is the read-back. On the screen: Manage Tax Zone Types, search by code.

## Rules and limits
1. New records only; never import a full export (it would update every zone type in it).
2. This skill never deletes.
3. No zones, zone identifiers or ranges are created; their files stay header only (not tested with rows).
4. Tested on one environment (release 11.13.26.10.0).

## History (short)
- 2026-11-23/24: 6 tries refused with `JBO-26041` (rows built with `CreatedBy`/`LastUpdatedBy` empty). 2026-11-24: a round trip of a screen-made zone type's own export imported fine; the only difference from our row was the two who columns. With them filled (from the export's `SubmittedBy`) the skill's row imported first try. Details in CHANGELOG.md.
