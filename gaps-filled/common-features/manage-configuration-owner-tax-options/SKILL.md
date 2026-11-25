---
skill_id: "gosaas.gap-fills.common-features.manage-configuration-owner-tax-options"
name: "Manage Configuration Owner Tax Options (GoSaaS gap fill, written, not load-tested)"
description: "Read, and (only on an environment you own) add, configuration owner tax options: the per business unit or legal entity, per application event class tax options (ZX_CONFIGURATION_OWNER_TAX_OPTIONS) through FSCR's setup-task CSV export and FSM CSV import. The export steps are verified; the import is not tested, because every row changes tax handling of real transactions. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 08, 2026-11-25. Written from a live read-only export and Oracle's docs. Import NOT tested (unsafe on a shared environment). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS"
task_name: "Manage Configuration Owner Tax Options"
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
  - "An import (Steps 4 to 6) adds or changes the tax options of a business unit or legal entity for one application event class: it changes how tax is calculated, defaulted and overridden on every such transaction of that owner."
---

# Manage Configuration Owner Tax Options (GoSaaS gap fill, written, not load-tested)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live read-only export (2026-11-25) · **GUESS** = from Oracle's docs or judgment, not tested.
> **Status: written, not tested.** On a shared environment do Steps 1 to 3 only.

## What it is and when to use
Configuration owner tax options override the tax defaults of one **configuration owner** (a business unit, `PartyTypeCode=OU`, or a legal entity) for one **application event class** (for example payables standard invoices), from a date: allow manual tax lines, allow override, allow exemptions, rounding level, tax-point basis, withholding calculation point, determining factor set (`DetFactorTemplCode`) and more. They act on real transactions as soon as they exist. The owner must be a real business unit or legal entity: there is no "test owner".
Note: the **global configuration owner option row** that tax content needs (see the gap skill `manage-tax-regimes` Step 7) is a different file (`ORA_ZX_BU_GCO_TAX_SUB.csv` in the regimes package), not this task.

## Placeholders
```text
FSCR, GAPS, H, RUN  = as in the other gap skills (FSCR root; gaps-filled folder; <GAPS>/common-features/manage-docseq-categories/scripts; a new run folder outside any repo)
OWNER   = PartyName of the business unit (PartyTypeCode OU) or legal entity
APP     = ApplicationShortName (e.g. AP), ENTITY = EntityCode (e.g. AP_INVOICES), CLASS = EventClassCode (e.g. STANDARD INVOICES)
FROM    = EffectiveFrom date YYYY/MM/DD
```

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`, `--output-dir` under RUN, `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1` in Git Bash, paths as `E:/...`. Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name). On 401/403 sign in with FSCR `core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the page). Sign-in time is waiting time.

## Prerequisites
1. OWNER exists (business unit or legal entity) and uses tax for that application. GUESS
2. For Steps 4 to 6: an environment you own and written approval naming OWNER, APP/ENTITY/CLASS and each option value.
3. `DetFactorTemplCode`, if set, must be an existing determining factor set (gap skill `manage-tax-factor-sets`). VERIFIED that existing rows use such codes.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
VERIFIED (about 45 s): 2 files, `ZX_CONFIGURATION_OWNER_TAX_OPTIONS.csv` (56 columns; 4 rows on our environment, all `PartyTypeCode=OU`, `ApplicationShortName=AP`, `RecordTypeCode=USER_DEFINED`, indirect tax `I` or withholding `W` in `IndirectTaxOrWhtFlag`) and `ASM_SETUP_CSV_METADATA.xml`. The row key is (GUESS from the columns) `ApplicationId, EntityCode, EventClassCode, PartyTypeCode, PartyName, IndirectTaxOrWhtFlag, EffectiveFrom`.

## Step 3. Read the options of one owner
```bash
python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/export_before/unz" --value "<OWNER>" --match-cols PartyName
```
Shows each event class row of OWNER without audit columns (VERIFIED viewer behaviour on this kind of file).

## Step 4. Build a new row (GUESS, environment you own only)
Copy one existing row of the same APP/ENTITY/CLASS as a template (all 56 columns), change `PartyName` to OWNER, `EffectiveFrom` to FROM and only the approved options; leave audit columns empty; `RecordTypeCode=USER_DEFINED`. Build with `<H>/build_fsm_package.py --key "ZX_CONFIGURATION_OWNER_TAX_OPTIONS.csv=ApplicationId,EntityCode,EventClassCode,PartyTypeCode,PartyName,IndirectTaxOrWhtFlag,EffectiveFrom"` so an existing key is refused (an existing key would be an update). GUESS

## Step 5. Import (GUESS, environment you own only)
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS --task-name "Manage Configuration Owner Tax Options" \
  --zip-file "<RUN>/payload/<zip>" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
Keep the ProcessId. `JBO-27014 ... is required` names a missing column; `JBO-26041` at the insert: fill `CreatedBy`/`LastUpdatedBy` from the export metadata's `SubmittedBy` (never print it). GUESS

## Step 6. Read back (GUESS)
Export again; `<H>/compare_fsm_exports.py` with the key above and `--expect` your new key: only your row added.

## Rules and limits
1. Shared environment: read only. Any row changes tax on real transactions of a real owner.
2. Never import the full export. Never change an existing row.
3. Not tested: any import of this object. Tested (read only) on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED read only, 2026-11-25)
| Step | Result |
|---|---|
| Export | 2 files, 4 option rows (2 business units, payables event classes), about 45 s |
| Decision | not loaded: every possible row belongs to a real business unit or legal entity and changes its tax handling |
