---
skill_id: "gosaas.gap-fills.common-features.search-legal-reporting-units"
name: "Search Legal Reporting Units (GoSaaS gap fill)"
description: "Find a legal reporting unit and show its setup (its legal entity, main flag, country, registrations) without a screen: the legalReportingUnitsLOV REST resource plus FSCR's read-only setup-task CSV export of XLE_SEARCH_LEGAL_REPORTING_UNITS. Read only: creates and changes nothing. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 05, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "XLE_SEARCH_LEGAL_REPORTING_UNITS"
task_name: "Search Legal Reporting Units"
dataloader_import_mode: "FSM"
type: "export"
execution_mode: "read-only"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "gosaas common-features/manage-docseq-categories/scripts/rest_read.py (generic REST read)"
  - "gosaas common-features/search-legal-entities/scripts/view_record.py (export viewer)"
side_effects:
  - "Starts one setup-task CSV export process (read-only for Fusion data). Nothing is created or changed."
---

# Search Legal Reporting Units (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
"Search Legal Reporting Units" is a **view/search task**: it lists legal reporting units (LRUs, also called establishments) and opens one. There is nothing to create. Use it when someone asks "which reporting units does legal entity X have", "show me reporting unit Y", "which one is the main unit", or wants a read-only check before a tax or registration step.
- Do **not** use it to create or change a reporting unit (that changes shared enterprise structure).

## Placeholders
```text
FSCR   = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS   = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H      = <GAPS>/common-features/manage-docseq-categories/scripts   (rest_read.py)
V      = <GAPS>/common-features/search-legal-entities/scripts/view_record.py
RUN    = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
LRU    = the reporting unit name the person asks about (or a part of it for a search)
```

## Sign-in
Same as `search-legal-entities` (this folder's sibling): FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...`, `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; `timeout 120` before REST reads; on HTTP 401/403, an expired token or a hang, sign in with `core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). Never print tokens, the server address or user names.

## Prerequisites
None (read access to legal entities and reporting units).

## Step 1. Search by REST
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource legalReportingUnitsLOV \
  --q "LegalReportingUnitName LIKE '%<part of LRU>%'" \
  --fields LegalReportingUnitName,MainLegalReportingUnitFlag,StartDate,EndDate \
  --out "<RUN>/lru_search.json"
```
- Shows matching units and whether each is the **main** unit of its legal entity. VERIFIED
- To list all units of one legal entity: first find the entity with `legalEntitiesLOV` (`--q "Name='<LE>'"`, field `LegalEntityId`), then `--q "LegalEntityId=<that id>"` here. Use the id only inside this run; never write it into a report or another skill. VERIFIED (both resources return the id)

## Step 2. Read-only export (about 2 minutes)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code XLE_SEARCH_LEGAL_REPORTING_UNITS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export"
```
Same 8 files as Search Legal Entities (VERIFIED: the two tasks export the same legal entity package). The reporting units are in `XLE_ETB_PROFILE.csv` (`Name`, parent `XLE_ENTITY_PROFILE.LegalEntityIdentifier`, `MainEstablishmentFlag`, geography columns) and their registrations in `ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION.csv` (`XLE_ETB_PROFILE.Name`, `RegisteredName`, `RegistrationNumber`, jurisdiction `Name`, `FormattedAddress`). If the export drops, retry into a new folder, one at a time, up to 3 tries.

## Step 3. Show one reporting unit
```bash
python -I "<V>" "<RUN>/export/unz" --value "<LRU>" \
  --file XLE_ETB_PROFILE.csv --file ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION.csv --out "<RUN>/lru_summary.txt"
```
- Prints the unit and its registrations, with no audit columns (no user names). VERIFIED
- The main reporting unit often has the **same name** as its legal entity; then also `XLE_ENTITY_PROFILE.csv` matches. Add `--file XLE_ENTITY_PROFILE.csv` to see the parent too.
- Exit 1 = nothing matched: check the exact name with Step 1.

## Build rows / import
None. Read-only task; never import anything for it.

## Read back
Steps 1 and 3 are the read-back: REST and export must agree on the unit name and its main flag.

## Rules and limits
1. Read only. Never re-import this export (it would update every legal entity and reporting unit).
2. Keep RUN outside git (internal ids in REST, user names in audit columns).
3. Tested on one environment (release 11.13.26.10.0): 67 reporting units, each with one registration.

## Worked example (VERIFIED, 2026-11-25)
| Step | Result |
|---|---|
| REST `legalReportingUnitsLOV` | named unit found, `MainLegalReportingUnitFlag=True` |
| Export | 8 files, 67 units, about 2 minutes |
| View (2 files) | 1 unit row (`MainEstablishmentFlag=Y`, country US) and 1 registration row (jurisdiction "United States Income Tax") |
