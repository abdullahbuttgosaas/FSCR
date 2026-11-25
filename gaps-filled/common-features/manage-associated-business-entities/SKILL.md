---
skill_id: "gosaas.gap-fills.common-features.manage-associated-business-entities"
name: "Manage Associated Business Entities: associate a legal reporting unit with a business unit by FSM CSV (GoSaaS gap fill)"
description: "Adds one legal association (XLE_ASSOCIATION) between a legal reporting unit and a business entity (here a business unit, context TAX_CALCULATION) by FSM CSV import, with an export compare as proof. Tested with a test legal entity's reporting unit and a test business unit, both made for the test. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 15, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "XLE_MANAGE_ASSOCIATED_BUSINESS_ENTITIES"
task_name: "Manage Associated Business Entities"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/test-legal-entity and test-business-unit (for a test)"
side_effects:
  - "Step 3 adds a legal association: for tax, transactions of that business unit may use that reporting unit (context TAX_CALCULATION)."
---

# Manage Associated Business Entities (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
A legal association links a **legal reporting unit** (establishment) of a legal entity to a **business entity**: a business unit (`OPERATING_UNIT`), an inventory organization, or a ship-to, bill-to or inventory location (lookup `XLE_ASSOC_BUS_ENTITY_TYPE`, VERIFIED). With context `TAX_CALCULATION` it tells tax which reporting unit to use for that entity's transactions (GUESS from Oracle's docs).
Use it to link a reporting unit to a business unit. **For a test**, link only your own test reporting unit to your own test business unit: an association on a real business unit or location changes tax on its real transactions.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py   (offline builder; it trims spaces, see Step 2)
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (use a separate one, e.g. <RUN>/../bu, for the prerequisite skills: their folders exp1, pay, imp would clash)
W     = <GAPS>/common-features/scripts/rest_call.py
LE    = the legal entity identifier (for a test: your own)
LRU   = the reporting unit name (a test legal entity's main unit has the legal entity's name)
BU    = the business unit name (for a test: your own, made WITH a location)
LOCN  = the business unit's location name as the export shows it in BusinessEntityLocation (for a location code like "X Location" the name was the same, VERIFIED)
ADDR  = the location's formatted address as the association expects it: for a location with no address lines it is exactly three spaces "   " (VERIFIED)
PREFIX= your test prefix, e.g. GAPFILL_XX_
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names.

## Prerequisites
Order: check 1, then Step 1 (to read LOC), then make the business unit (2), then Steps 2 to 4.
1. A legal entity with its reporting unit. **For a test:** `<GAPS>/common-features/test-legal-entity/SKILL.md` (check first, read only, from `<RUN>`: `python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV --query onlyData=true --query "q=LegalEntityIdentifier='<LE>'" --query fields=LegalEntityIdentifier,Name --no-open-browser --output le.json > le.log 2>&1` then `python -I -c "import json; print(json.load(open('le.json',encoding='utf-8'))['count'])"`; create only if 0). The main reporting unit LRU has the legal entity's name.
2. A business unit **with a location** (`InternalLocationCode`). **For a test:** `<GAPS>/common-features/test-business-unit/SKILL.md` with LOC = the location of a business unit that already has an association (after Step 1: the `BusinessEntityLocation` of an `OPERATING_UNIT` row in `XLE_ASSOCIATION.csv`; VERIFIED with `GoSaaS Location` style codes where code = name). Without a location the association is refused with `XLE_ASSOC_OBJECT_ID_REQUIRED` (VERIFIED twice).
3. LOCN and ADDR: copy them from an existing association row for a business unit with the same location (after Step 1: `grep "<LOCN>" "<RUN>/exp1/unz/XLE_ASSOCIATION.csv"`), or use the rule above.

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code XLE_MANAGE_ASSOCIATED_BUSINESS_ENTITIES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
```
1 CSV `XLE_ASSOCIATION.csv` + metadata. Columns used: `AssociationTypeId` (10000 in every row, VERIFIED), `EffectiveFrom`, `LeIdentifierSubjectParent` (legal entity), `EstablishmentName` (reporting unit), `BusinessEntityType`, `BusinessEntityOrgName`, `BusinessEntityLocation`, `BusinessEntityAddress`, `Context`. Check your pair is not there yet (`grep -c "<BU>"` → 0). No ZIP: run again into a NEW folder, up to 3 tries.

## Step 2. Build (offline, VERIFIED)
Replace `<today yyyy/mm/dd>` in the command. The builder trims values, so it drops ADDR's spaces: build, then set ADDR in the file and zip again.
```bash
cd "<RUN>"; python -I "<B>" --export-dir exp1/unz --out-dir pay --zip-name abe.zip --prefix <PREFIX> \
 --key "XLE_ASSOCIATION.csv=LeIdentifierSubjectParent,EstablishmentName,BusinessEntityOrgName,Context" \
 --prefix-col "XLE_ASSOCIATION.csv=EstablishmentName" --prefix-col "XLE_ASSOCIATION.csv=BusinessEntityOrgName" \
 --row "XLE_ASSOCIATION.csv|AssociationTypeId=10000|EffectiveFrom=<today yyyy/mm/dd>|LeIdentifierSubjectParent=<LE>|BusinessEntityType=OPERATING_UNIT|BusinessEntityOrgName=<BU>|BusinessEntityLocation=<LOCN>|Context=TAX_CALCULATION|EstablishmentName=<LRU>"
cd "<RUN>/pay"; python -I - "<ADDR>" <<'EOF'
import csv, glob, os, sys, zipfile
f = "XLE_ASSOCIATION.csv"
with open(f, encoding="utf-8", newline="") as fh: rows = list(csv.reader(fh))
assert len(rows) == 2, "expected exactly 1 data row"
rows[1][rows[0].index("BusinessEntityAddress")] = sys.argv[1]
with open(f, "w", encoding="utf-8", newline="") as fh: csv.writer(fh, quoting=csv.QUOTE_ALL, lineterminator="\n").writerows(rows)
os.remove("abe.zip")
with zipfile.ZipFile("abe.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(glob.glob("*.csv")) + ["ASM_SETUP_CSV_METADATA.xml"]: z.write(p)
print(zipfile.ZipFile("abe.zip").namelist())
EOF
```
(Close the file before zipping, as above: a zip written while the CSV is still open holds an empty file.) For a real (non-test) pair drop the two `--prefix-col` and get written approval first.

## Step 3. Import (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code XLE_MANAGE_ASSOCIATED_BUSINESS_ENTITIES --task-name "Manage Associated Business Entities" --zip-file "<RUN>/pay/abe.zip" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^.\]{0,200}|JBO-[0-9]+: [^.\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
Write down the ProcessId. Success: `A total of 1 rows were processed. 0 rows of them failed`, `Legal Association. Status: Completed successfully`. `XLE_ASSOC_OBJECT_ID_REQUIRED` = Oracle could not find the business unit by name + location + address (no location, or LOCN/ADDR not as expected); nothing is created. Print only the grep lines (the log holds the environment name and user). Dropped connection: never import again; wait 2 minutes and read back.

## Step 4. Read back (VERIFIED)
Export again (Step 1 with `exp2`, both lines), then:
```bash
python -I "<CMP>" "<RUN>/exp1/unz" "<RUN>/exp2/unz" --key "XLE_ASSOCIATION.csv=LeIdentifierSubjectParent,EstablishmentName,BusinessEntityOrgName,Context" --expect "XLE_ASSOCIATION.csv=<LE>,<LRU>,<BU>,TAX_CALCULATION"
```
`RESULT: PASS` = only your association added, none removed or changed.

## Rules and limits
1. New associations only; a test links only your own reporting unit and business unit. No delete through CSV.
2. Tested on one environment (release 11.13.26.10.0), type `OPERATING_UNIT`, context `TAX_CALCULATION`. Other types: GUESS.

## Worked example (2026-11-26, codes and ProcessIds only)
| Try | Result |
|---|---|
| 1 | unit `GAPFILL_AB_B14_LE1` → `GAPFILL_AB_B15_BU1` (no location): ProcessId 100004743430787, `XLE_ASSOC_OBJECT_ID_REQUIRED` |
| 2 | → `GAPFILL_AB_B15_BU3` (new business unit with a location), location given, address empty: ProcessId 100004743434305, same error |
| 3 | as 2 plus address "   " (as in the working rows): ProcessId 100004743433629, 1 processed, 0 failed; compare 3 → 4 rows, PASS |
| fresh | `GAPFILL_AB_B14_LE2F` → new `GAPFILL_AB_B15_BU4F` (with location, 100004743435021): ProcessId 100004743435423, 4 → 5 rows, PASS |
| re-test | `GAPFILL_AB_B14_LE3R` → new `GAPFILL_AB_B15_BU5R` (100004744417195): ProcessId 100004743432818, 5 → 6 rows, PASS |
