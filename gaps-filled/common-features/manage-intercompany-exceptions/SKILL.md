---
skill_id: "gosaas.gap-fills.common-features.manage-intercompany-exceptions"
name: "Manage Intercompany Exceptions (GoSaaS gap fill, written, not load-tested)"
description: "Read the legal entity package behind the Manage Intercompany Exceptions task through FSCR's setup-task CSV export (XLE_ENTITY_PROFILE, XLE_ETB_PROFILE, XLE_REGISTRATION, XLE_LE_LEGAL_ADDRESS and reporting-unit registrations), and describe how a change would be loaded on an environment you own. The export is verified; no import was run, because every row belongs to an existing legal entity used by every financial transaction. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 08, 2026-11-25. Written from a live read-only export and Oracle's docs. Import NOT tested (unsafe on a shared environment). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "XLE_MANAGE_INTERCOMPANY_EXCEPTIONS"
task_name: "Manage Intercompany Exceptions"
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
  - "gosaas common-features/search-legal-entities (read-only viewer)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "An import (Steps 4 to 6) changes legal entity records (profile, establishment, registration, address) that every ledger, business unit and intercompany transaction of that legal entity uses."
---

# Manage Intercompany Exceptions (GoSaaS gap fill, written, not load-tested)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live read-only export (2026-11-25) · **GUESS** = from Oracle's docs or judgment, not tested.
> **Status: written, not tested.** On a shared environment do Steps 1 to 3 only.

## What it is and when to use
The task's CSV package is the **legal entity package** (VERIFIED: the same 7 CSV files as the legal entity tasks): legal entity profiles (`XLE_ENTITY_PROFILE.csv`), establishments / legal reporting units (`XLE_ETB_PROFILE.csv`), registrations (`XLE_REGISTRATION.csv`, `ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION.csv`), legal addresses (`XLE_LE_LEGAL_ADDRESS.csv`) and registration functions (2 files, empty here). There is **no separate "exception" file** in the package (VERIFIED): the intercompany behaviour it refers to (GUESS from Oracle's docs: which legal entities are treated as one for intercompany, the legal entity's intercompany settings) is held on the legal entity records themselves. So a load always changes an existing legal entity or creates a whole new legal entity with its party, address and registrations.
Use Steps 1 to 3 to read a legal entity's records. Use Steps 4 to 6 only on an environment you own.

## Placeholders
```text
FSCR, GAPS, H, RUN  = as in the other gap skills (FSCR root; gaps-filled folder; <GAPS>/common-features/manage-docseq-categories/scripts; a new run folder outside any repo)
LE      = the legal entity's name or LegalEntityIdentifier
```

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`, `--output-dir` under RUN, `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` in Git Bash, paths as `E:/...`. Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name). Addresses and registration numbers in this export are company data: do not paste them into reports. On 401/403 sign in with FSCR `core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the page).

## Prerequisites
1. For reading: none.
2. For Steps 4 to 6: an environment you own, written approval naming LE and each column to change. A new legal entity also needs a legislative category, a country, a legal address (geography) and a registration with a jurisdiction (GUESS from the columns and Oracle's docs).

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code XLE_MANAGE_INTERCOMPANY_EXCEPTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
VERIFIED (about 45 s): 8 files: `XLE_ENTITY_PROFILE.csv` (79 columns, 67 rows), `XLE_ETB_PROFILE.csv` (89, 67), `XLE_REGISTRATION.csv` (55, 68), `XLE_LE_LEGAL_ADDRESS.csv` (115, 57), `ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION.csv` (56, 67), the two registration-function files (0 rows) and `ASM_SETUP_CSV_METADATA.xml`.

## Step 3. Read one legal entity
```bash
python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/export_before/unz" --value "<LE>" --match-cols Name,LegalEntityIdentifier
```
(The gap skill `search-legal-entities` is the tested read-only guide for this package, including REST `legalEntitiesLOV`.)

## Step 4. Build a change (GUESS, environment you own only)
Copy the LE's rows unchanged (parent profile row first: a child row is processed only with its parent in the same ZIP), change only approved columns, round-trip the unchanged rows first and check the after-export shows `changed 0`. A brand new legal entity would be written in full; read required columns from `JBO-27014` messages. GUESS

## Step 5. Import (GUESS, environment you own only)
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code XLE_MANAGE_INTERCOMPANY_EXCEPTIONS --task-name "Manage Intercompany Exceptions" \
  --zip-file "<RUN>/payload/<zip>" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
Keep the ProcessId. Never import the full export.

## Step 6. Read back (GUESS)
Export again and compare with `<H>/compare_fsm_exports.py` (keys: the identifier column of each file): only the approved changes.

## Rules and limits
1. Shared environment: read only. Legal entity records are used by every ledger, business unit and intercompany transaction of the entity.
2. Never import the full export.
3. Not tested: any import of this package. Tested (read only) on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED read only, 2026-11-25)
| Step | Result |
|---|---|
| Export | 8 files, 67 legal entities, about 45 s |
| Decision | not loaded: no stand-alone "exception" record exists in the package; any load changes or creates a legal entity |
