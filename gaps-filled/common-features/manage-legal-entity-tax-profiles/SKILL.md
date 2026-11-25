---
skill_id: "gosaas.gap-fills.common-features.manage-legal-entity-tax-profiles"
name: "Manage Legal Entity Tax Profiles: change the tax profile of a legal entity (GoSaaS gap fill, written, not load-tested)"
description: "Read, and (only on an environment you own) change, the tax profile of an existing legal entity through FSCR's setup-task CSV export and FSM CSV import (ZX_LEGAL_ENTITY_TAX_PROFILE). The export steps are verified; the change and import steps are not tested, because every row is an existing profile that drives tax on real transactions. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 08, 2026-11-25. Written from a live read-only export and Oracle's docs. Import NOT tested (unsafe on a shared environment). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES"
task_name: "Manage Legal Entity Tax Profiles"
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
  - "An import (Steps 4 to 6) UPDATES an existing legal entity tax profile: it changes tax calculation, rounding and withholding for every transaction of that legal entity."
---

# Manage Legal Entity Tax Profiles (GoSaaS gap fill, written, not load-tested)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live read-only export (2026-11-25) · **GUESS** = from Oracle's docs or judgment, not tested.
> **Status: written, not tested.** On a shared environment, do Steps 1 to 3 only (read). Steps 4 to 6 are for an environment you own, with written approval.

## What it is and when to use
A legal entity tax profile holds the tax settings of a first-party legal entity: rounding level and rule, tax-inclusive handling, whether it uses its own subscription (`UseLeAsSubscriberFlag`), self-assessment, offset taxes, withholding settings, and the default tax classification. Oracle **creates one profile with each legal entity** (VERIFIED: 67 legal entities, 67 profile rows; there is no profile row without a legal entity). So the task never creates a stand-alone record: every load **changes** an existing profile.
Use Steps 1 to 3 to read a legal entity's tax settings. Use Steps 4 to 6 only to change a profile on an environment you own.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
LE      = the LegalEntityIdentifier of the legal entity (the key column of the profile file)
```

## Step 1. Safe run and sign-in
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL, the server address or user names. FSCR's export and import print file names that hold the environment name: never copy those lines into a report.
- On HTTP 401/403, an expired token or a hang, sign in as in FSCR `core/auth/fusion-oauth-authentication`: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page; port 8765). Sign-in time is waiting time.

## Prerequisites
1. The legal entity exists (gap skill `search-legal-entities` reads it). Its tax profile exists with it (VERIFIED: one row per legal entity).
2. For Steps 4 to 6 only: an environment you own, and the person's written approval naming LE and the exact columns to change.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
VERIFIED (about 50 s): 2 files, `ZX_LEGAL_ENTITY_TAX_PROFILE.csv` (60 columns, one row per legal entity; key `LegalEntityIdentifier`; also `PartyTypeCode`, `RoundingLevelCode`, `RoundingRuleCode`, `InclusiveTaxFlag`, `UseLeAsSubscriberFlag`, `EffectiveFromUseLe`, `SelfAssessFlag`, `AllowOffsetTaxFlag`, `TaxClassificationCode`, the `Wht*` withholding columns, `CountryCode`, `Attribute1..15`, audit columns) and `ASM_SETUP_CSV_METADATA.xml`. If no ZIP: run it again into a new folder (read-only), up to 3 tries.

## Step 3. Read one profile
```bash
python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/export_before/unz" --value "<LE>" --match-cols LegalEntityIdentifier
```
It shows the profile row without audit or person columns. This is the read-only use of the task (VERIFIED: the viewer works on this export the same way as on the legal entity export).

## Step 4. Build a change file (GUESS, environment you own only)
1. Copy the LE row from the export **unchanged** into a payload folder with the same headers (all files of the export; other files header only), for example with `<GAPS>/common-features/manage-profile-options/scripts/copy_parent_rows.py --file ZX_LEGAL_ENTITY_TAX_PROFILE.csv --where LegalEntityIdentifier=<LE>` after `build_fsm_package.py` wrote empty files. GUESS
2. Change only the approved columns in that one row (for example `RoundingRuleCode`). Keep the audit columns as exported or empty. GUESS
3. Round-trip first (proof that the CSV path works for this object): import the row **unchanged**; the after-export must show `changed 0`. GUESS

## Step 5. Import (GUESS, environment you own only)
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_LEGAL_ENTITY_TAX_PROFILES --task-name "Manage Legal Entity Tax Profiles" \
  --zip-file "<RUN>/payload/<zip>" --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
Write down the ProcessId. Never import the full export (it would rewrite all 67 profiles). A dropped connection after the process started: do not import again; wait 2 minutes and read back.

## Step 6. Read back (GUESS)
Export again and compare with `<H>/compare_fsm_exports.py --key "ZX_LEGAL_ENTITY_TAX_PROFILE.csv=LegalEntityIdentifier"`: only the LE row may show `changed`, in only the approved columns. (No `--expect`: nothing is added.) A REST resource for legal entity tax profiles was not checked (GUESS: the export is the proof).

## Rules and limits
1. Shared environment: read only (Steps 1 to 3). A change alters tax on real transactions of that legal entity.
2. Never import the whole export; one row, approved columns only.
3. Not tested: any import of this object.
4. Tested (read only) on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED read only, 2026-11-25)
| Step | Result |
|---|---|
| Export | 2 files, 67 profile rows (one per legal entity), about 50 s |
| Decision | not loaded: every row is an existing profile; a load is an update of a shared tax setting |
