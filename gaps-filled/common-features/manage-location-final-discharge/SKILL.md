---
skill_id: "gosaas.gap-fills.common-features.manage-location-final-discharge"
name: "Manage Location of Final Discharge (GoSaaS gap fill)"
description: "Create one new location of final discharge (an HZ location plus its tax final discharge row) through FSCR's setup-task CSV export and FSM CSV import, rows written in full (the export is often empty), then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 4 part 3, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_MANAGE_LOCATION_FINAL_DISCHARGE"
task_name: "Manage Location of Final Discharge"
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
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new HZ location and one final discharge row for it. Tax determination can use enabled final discharge locations; a test location at a test street changes no transaction. It may not be deletable; plan as if it stays."
---

# Manage Location of Final Discharge (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill that builds these rows. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A location of final discharge is the final destination of goods bought by a customer (used by some tax rules). In Oracle it is an **HZ location** (file `ORA_LOCATION_OF_FINAL_DISCHARGE.csv`, key `ClliCode` = the location code) with a **child row** in `ORA_ZX_LOCATION_OF_FINAL_DISCHARGE.csv` (Oracle table ZX_FINAL_DISCHARGE_LOCATIONS: country, enabled flag, entity code). This skill creates **one new location** with both rows written in full: no ids, only codes and an address.

## When to use
- Someone asks to create a **new** location of final discharge for task `ORA_ZX_MANAGE_LOCATION_FINAL_DISCHARGE`.
- Do **not** use it to change or disable existing locations. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
CODE    = new location code (ClliCode), upper case, starting with PREFIX, max 30 (GUESS; 18 characters worked)
COUNTRY = 2-letter country code, e.g. US
ADDRESS = a real, valid address in COUNTRY (street of your choice, but city, state, county and postal code must exist in Oracle geography), e.g. US: "1 <PREFIX> test street" / Redwood City / CA / San Mateo / 94065
CBM     = a created-by-module code (Step 3), e.g. HZ_WS
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR puts the environment name in its output file names: never copy those names into evidence.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_LOCATION_FINAL_DISCHARGE --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.log" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 3 files (VERIFIED, about 30 s): `ORA_LOCATION_OF_FINAL_DISCHARGE.csv` (113 columns), `ORA_ZX_LOCATION_OF_FINAL_DISCHARGE.csv` (5 columns), `ASM_SETUP_CSV_METADATA.xml`. Both CSVs may have **0 rows** (VERIFIED); this skill does not need a template row.
- List existing codes: `python -I -c "import csv,sys; [print(r['ClliCode']) for r in csv.DictReader(open(sys.argv[1]+'/ORA_LOCATION_OF_FINAL_DISCHARGE.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"`. CODE must not be listed.
- If the export drops (no ZIP), run it again into a new folder, one at a time, up to 3 tries. If it still fails: **stop**.

## Step 3. Choose CBM (read live)
`CreatedByModule` is required (VERIFIED: without it `HZ_CBM_REQD_ERROR`). It must be a code of the lookup `HZ_CREATED_BY_MODULES`. Check that `HZ_WS` exists:
```bash
cd "<FSCR>"; timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" \
  --resource "standardLookups/HZ_CREATED_BY_MODULES/child/lookupCodes" --q "LookupCode='HZ_WS'" \
  --fields LookupCode,Meaning --out "<RUN>/cbm.json" --expect-count 1
```
`READBACK: PASS` = use `CBM=HZ_WS` (VERIFIED). If it fails, list the lookup without `--q` and pick a general HZ code (for example `HZ_CPUI`, GUESS).

## Step 4. Build a package with only the new location
Write both rows in full (one line each, no "|" inside values):
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name lfd_new.zip \
  --prefix <PREFIX> --key "ORA_LOCATION_OF_FINAL_DISCHARGE.csv=ClliCode" \
  --key "ORA_ZX_LOCATION_OF_FINAL_DISCHARGE.csv=ORA_LOCATION_OF_FINAL_DISCHARGE.ClliCode" \
  --prefix-col "ORA_LOCATION_OF_FINAL_DISCHARGE.csv=ClliCode" --max-len "ClliCode=30" \
  --row "ORA_LOCATION_OF_FINAL_DISCHARGE.csv|ClliCode=<CODE>|Country=<COUNTRY>|Address1=<street>|City=<city>|State=<state>|County=<county>|PostalCode=<postal code>|Description=<free text>|CreatedByModule=<CBM>|OrigSystemReference=<CODE>|StatusFlag=A" \
  --row "ORA_ZX_LOCATION_OF_FINAL_DISCHARGE.csv|ORA_LOCATION_OF_FINAL_DISCHARGE.ClliCode=<CODE>|CountryCode=<COUNTRY>|EnabledFlag=Y|EntityCode=HZ_LOCATIONS"
```
Why each value (all VERIFIED by Oracle errors in our test): `CreatedByModule` (HZ_CBM_REQD_ERROR), `OrigSystemReference` and `StatusFlag` (`JBO-27014 ... is required` in LocationEO; `A` = active), `EntityCode` (`JBO-27014 ... EntityCode in FinalDischargeLocationEO is required`; `HZ_LOCATIONS` = an external location, Oracle's documented value for this table). The builder must print `1 new rows` for both files.

## Step 5. Import
**Approval.** The person must approve the environment, the task and the exact CODE and address before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_LOCATION_FINAL_DISCHARGE --task-name "Manage Location of Final Discharge" \
  --zip-file "<RUN>/payload/lfd_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result" > "<RUN>/import.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/import.log"
python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: [^.]+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Total Objects \w+: [0-9]+|Message Code: [A-Z_]+|JBO-[0-9]+: [^.]{0,160}',t)))))" "<RUN>/import_result"
```
- **Write down the `ProcessId`** (the grep line). The one-liner prints only counts and error codes (no user names).
- Success (VERIFIED, about 25 s): `Detail Object: HzLocation. Status: Completed successfully ... 1 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0` (2 objects: Tax Location and Final Discharge Location).
- **If the script loses the connection after the process started**, the import still runs. **Do not import again.** Wait 2 minutes and do Step 6.
- Rows failed: read the message, change one thing, retry at most 3 times. A failed row creates nothing (VERIFIED: tries 1 and 2 created nothing; try 3 created the code).

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_LOCATION_OF_FINAL_DISCHARGE.csv=ClliCode" \
  --key "ORA_ZX_LOCATION_OF_FINAL_DISCHARGE.csv=ORA_LOCATION_OF_FINAL_DISCHARGE.ClliCode" \
  --expect "ORA_LOCATION_OF_FINAL_DISCHARGE.csv=<CODE>" --expect "ORA_ZX_LOCATION_OF_FINAL_DISCHARGE.csv=<CODE>" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your 2 rows were added. Oracle fills `LeFormattedAddress` (for example `<street>/REDWOOD CITY, CA 94065`) on both rows (VERIFIED). Do not print whole rows: they hold user names in the audit columns.

## Rules and limits
1. New records only; never import a full export.
2. Keep every file and the metadata XML unchanged in layout; only the 2 new rows go in.
3. Test records may stay for good. This skill never deletes. Record every created code.
4. Not tested: countries other than US, addresses without county, `EnabledFlag=N`, internal (HR) locations.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this code.
| Step | Result |
|---|---|
| Export before | 3 files, 0 rows; about 30 s |
| Try 1 (ProcessId 100004741423731) | no CreatedByModule: `HZ_CBM_REQD_ERROR`, nothing created |
| Try 2 (100004741423798) | `JBO-27014` EntityCode, OrigSystemReference, StatusFlag required; nothing created |
| Try 3 (100004741426100) | `GAPFILL_AB_P3_LFD1`, US, Redwood City CA 94065: HzLocation 1 row, 0 failed; 2 objects succeeded |
| Export after + compare | 0 -> 1 in both files, removed 0, changed 0: PASS |
