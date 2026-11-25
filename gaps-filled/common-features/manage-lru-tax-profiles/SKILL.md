---
skill_id: "gosaas.gap-fills.common-features.manage-lru-tax-profiles"
name: "Manage Legal Reporting Unit Tax Profiles (GoSaaS gap fill, written, not load-tested)"
description: "Read, and (only on an environment you own) change, the tax profile of an existing legal reporting unit (establishment) through FSCR's setup-task CSV export and FSM CSV import (ZX_ESTABLISHMENT_TAX_PROFILE and its classification files). The export steps are verified; the import is not tested, because every profile row is an existing reporting unit's profile that drives tax and tax reporting. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 08, 2026-11-25. Written from a live read-only export and Oracle's docs. Import NOT tested (unsafe on a shared environment). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES"
task_name: "Manage Legal Reporting Unit Tax Profiles"
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
  - "An import (Steps 4 to 6) UPDATES an existing reporting unit tax profile (rounding, tax registration defaults, classifications): it changes tax on that unit's transactions and its tax reports."
---

# Manage Legal Reporting Unit Tax Profiles (GoSaaS gap fill, written, not load-tested)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live read-only export (2026-11-25) · **GUESS** = from Oracle's docs or judgment, not tested.
> **Status: written, not tested.** On a shared environment do Steps 1 to 3 only.

## What it is and when to use
A legal reporting unit (establishment) tax profile holds the tax settings of one reporting unit: rounding, inclusive tax, self-assessment, registrations defaults and party fiscal classifications. Oracle **creates one profile with each reporting unit** (VERIFIED: `ZX_ESTABLISHMENT_TAX_PROFILE.csv` has 67 rows, the same count as the reporting units). The package also carries the whole fiscal classification set-up (about 70 CSV files: classification types and codes, their denormalized rows, product, transaction and user-defined classifications), because a profile can point to classification codes. A load therefore always **changes** an existing profile, or (for the classification files) is the work of other gap skills (`manage-party-fiscal-classifications`, `manage-transaction-fiscal-classifications`, `manage-product-fiscal-classifications`, all tested).

## Placeholders
```text
FSCR, GAPS, H, RUN  = as in the other gap skills (FSCR root; gaps-filled folder; <GAPS>/common-features/manage-docseq-categories/scripts; a new run folder outside any repo)
LRU     = the reporting unit's name or identifier as shown in ZX_ESTABLISHMENT_TAX_PROFILE.csv
```

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`, `--output-dir` under RUN, `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` in Git Bash, paths as `E:/...`. Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name). On 401/403 sign in with FSCR `core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the page).

## Prerequisites
1. The reporting unit exists (gap skill `search-legal-reporting-units` reads it). Its profile exists with it (VERIFIED: 67 profile rows).
2. For Steps 4 to 6: an environment you own and written approval naming LRU and the columns to change. Classification codes the profile points to must exist first (the fiscal classification gap skills).

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
VERIFIED (about 1 minute): about 70 CSV files plus `ASM_SETUP_CSV_METADATA.xml`; the profile file is `ZX_ESTABLISHMENT_TAX_PROFILE.csv` (62 columns, 67 rows); reporting-unit classification links are in `ZX_ESTABLISHMENT_CLASSIF_ASSOC.csv` (1 row) and `ORA_ZX_ESTABLISHMENT_CLASSIF_CODE.csv` (67 rows).

## Step 3. Read one profile
```bash
python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/export_before/unz" --value "<LRU>"
```
Shows every row that holds LRU, without audit or person columns.

## Step 4 to 6. Change, import, read back (GUESS, environment you own only)
Same pattern as the gap skill `manage-legal-entity-tax-profiles` Steps 4 to 6, with file `ZX_ESTABLISHMENT_TAX_PROFILE.csv` and task code `ZX_MANAGE_LEGAL_REPORTING_UNIT_TAX_PROFILES` / name "Manage Legal Reporting Unit Tax Profiles": copy the one row unchanged, round-trip it first (`changed 0`), then change only approved columns; never import the full export (it would rewrite all profiles and the whole classification set-up); compare before/after exports: only that row `changed`.

## Rules and limits
1. Shared environment: read only.
2. Never import the full export.
3. Not tested: any import of this object. Tested (read only) on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED read only, 2026-11-25)
| Step | Result |
|---|---|
| Export | about 70 files, 67 reporting unit profiles, about 1 minute |
| Decision | not loaded: every profile row is an existing reporting unit's profile |
