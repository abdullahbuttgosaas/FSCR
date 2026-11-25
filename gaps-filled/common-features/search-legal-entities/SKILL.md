---
skill_id: "gosaas.gap-fills.common-features.search-legal-entities"
name: "Search Legal Entities (GoSaaS gap fill)"
description: "Find a legal entity and show its setup (identifier, country, registrations, main legal reporting unit, address) without a screen: FSCR's read-only setup-task CSV export of XLE_SEARCH_LEGAL_ENTITIES plus the legalEntitiesLOV REST resource. Read only: creates and changes nothing. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 05, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "XLE_SEARCH_LEGAL_ENTITIES"
task_name: "Search Legal Entities"
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

# Search Legal Entities (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV export flag); it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
"Search Legal Entities" is a **view/search task**: it lists legal entities and opens one to look at it. There is nothing to create. Use this skill when someone asks "which legal entities exist", "show me legal entity X", "what is the identifier / country / registration of X", or wants a read-only check of a legal entity before another setup step.
- Do **not** use it to create or change a legal entity (that is the Manage Legal Entity task, and it changes shared enterprise structure).

## Placeholders
```text
FSCR   = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS   = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H      = <GAPS>/common-features/manage-docseq-categories/scripts   (rest_read.py)
V      = <GAPS>/common-features/search-legal-entities/scripts/view_record.py
RUN    = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
LE     = the legal entity name the person asks about (or a part of it for a search)
```

## Sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Put `timeout 120` in front of REST reads. Never print tokens, headers, the sign-in URL, the server address or user names.
- If a call reports HTTP 401/403, an expired token, or hangs, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page (listener on port 8765); never type credentials. Sign-in time is waiting time.

## Prerequisites
None. The person only needs read access to legal entities (the export and `legalEntitiesLOV`).

## Step 1. Search by REST (fast, a few seconds)
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource legalEntitiesLOV \
  --q "Name LIKE '%<part of LE>%'" --fields Name,LegalEntityIdentifier,EffectiveFrom,EffectiveTo \
  --out "<RUN>/le_search.json"
```
- Shows the matching legal entities with their **LegalEntityIdentifier** (the business key used in every other file). VERIFIED
- For an exact name use `--q "Name='<LE>'" --expect-count 1`. No match shows `legalEntitiesLOV: 0 row(s)` (and, with `--expect-count 1`, `READBACK: FAIL`, exit 1). Exit 2 = sign-in or privilege problem.
- `legalEntitiesLOV` also returns internal ids (LegalEntityId, PartyId). Do not write them down or use them in other skills; use the name and identifier.

## Step 2. Read-only export (the full setup, about 2 minutes)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code XLE_SEARCH_LEGAL_ENTITIES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export"
```
Expect 8 files (VERIFIED, about 1 to 2 minutes): `XLE_ENTITY_PROFILE.csv` (one row per legal entity), `XLE_ETB_PROFILE.csv` (legal reporting units), `XLE_REGISTRATION.csv` (legal entity registrations), `ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION.csv`, `XLE_LE_LEGAL_ADDRESS.csv`, `ORA_XLE_LEGAL_ENTITY_REGISTRATION_FUNCTION.csv`, `ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION_FUNCTION.csv`, and `ASM_SETUP_CSV_METADATA.xml`.
- Success = exit 0 and a ZIP written in `<RUN>/export`; a `StatusCode: (unknown)` line on the way is normal (VERIFIED). The ZIP's file name holds the environment name: never copy it into a report.
- If the export drops (no ZIP), run it again into a **new** folder (one ZIP per folder), one at a time, up to 3 tries.

## Step 3. Show one legal entity
```bash
python -I "<V>" "<RUN>/export/unz" --value "<LEGAL ENTITY IDENTIFIER>" --value "<LE>" \
  --match-cols "LegalEntityIdentifier,XLE_ENTITY_PROFILE.LegalEntityIdentifier,Name,XLE_ETB_PROFILE.Name" \
  --out "<RUN>/le_summary.txt"
```
Prints, per file, the rows whose identifier or name columns hold that value, without audit columns (so no user names). The summary goes to the screen and to `le_summary.txt`. VERIFIED
- Keep `--match-cols`: without it, rows of **other** legal entities also show when their registration number happens to equal your identifier (VERIFIED: one entity's reporting unit registration number was another entity's identifier).
Read it like this:
| File | What you learn |
|---|---|
| `XLE_ENTITY_PROFILE.csv` | country (`TerritoryCode`, `GeographyCode`), `LegalEmployerFlag`, `PsuFlag` (payroll statutory unit), `TransactingEntityFlag`, effective dates |
| `XLE_REGISTRATION.csv` | the identifying registration: `RegisteredName`, `RegistrationNumber`, jurisdiction (`Name`), `IdentifyingFlag=Y`, `FormattedAddress` |
| `XLE_ETB_PROFILE.csv` | its legal reporting units; `MainEstablishmentFlag=Y` marks the main one |
| `ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION.csv` | registrations of those reporting units |
| `XLE_LE_LEGAL_ADDRESS.csv` | address rows; they hold the address, not the legal entity name, so they may show 0 matching rows (VERIFIED). The address is also in `FormattedAddress` of the registration |
- Exit 1 = no row matched: check the spelling with Step 1 (the identifier is the safest key).

## Build rows / import
None. This is a read-only task; never import anything for it.

## Read back
Steps 1 and 3 are the read-back: the REST row and the export rows must agree on name and identifier.

## Rules and limits
1. Read only. Do not use this skill's export as a template for imports (a full re-import would update every legal entity).
2. The export and REST hold internal ids and the export's audit columns hold user names: keep RUN outside git, never copy those into reports.
3. REST `LIKE` is case-sensitive (VERIFIED: an all-lower-case search found 0 rows for a name that exists). If a search finds nothing, try the exact capitalisation, or a shorter part of the name.
4. Tested on one environment (release 11.13.26.10.0), with 67 legal entities in the export.

## Worked example (VERIFIED, 2026-11-25)
| Step | Result |
|---|---|
| REST `legalEntitiesLOV` | 1 row for the named entity, identifier read |
| Export | 8 files, 67 legal entities, about 65 to 120 s |
| View (the counts depend on the entity) | 4 matching rows: profile (country US, legal employer Y, PSU Y, transacting Y), identifying registration (jurisdiction "United States Income Tax"), main legal reporting unit, its registration; address file 0 rows (normal) |
