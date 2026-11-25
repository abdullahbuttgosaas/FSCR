---
skill_id: "gosaas.gap-fills.common-features.manage-country-default-controls"
name: "Manage Country Default Controls (GoSaaS gap fill, written, not load-tested)"
description: "Read, and when a person approves it, create the tax country default controls of one country (default tax regime and tax, product and transaction category controls, registration defaults) through FSCR's setup-task CSV export/import of ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS (ZX_COUNTRY_DEFAULTS). WRITTEN ONLY: the import was not run, because a country default row changes tax defaulting for every transaction in that country. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 06, 2026-11-25. Export seen live on one test environment; the import was NOT run (unsafe on a shared environment). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS"
task_name: "Manage Country Default Controls"
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
  - "ZX_MANAGE_TAX_REGIMES and ZX_MANAGE_TAXES (a regime and tax for the country, if defaults name them)"
side_effects:
  - "Step 2 is read only."
  - "Step 4 (import, not run here) sets tax defaults for every transaction and registration in that country, for all business units."
---

# Manage Country Default Controls (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> **Status: written, not load-tested.** The export was run live (VERIFIED). The import was **not** run on our shared test environment: a country row changes tax defaults for every transaction in that country, and countries are shared by everyone. Steps 3 to 5 are **GUESS**, built from the export's columns, Oracle's tax setup guide and the tested tax recipes of batches 3 and 4.

## What it is and when to use
Country default controls are **one row per country** (key `CountryCode`) that say, for transactions and registrations in that country: the default tax regime and tax (`TaxRegimeCode`, `Tax`, with flags `DefRegimeForInvoiceFlag`, `DefRegimeForLeTrFlag`, `DefTaxForInvoiceFlag`, `DefTaxForLeTrFlag`), the product and transaction fiscal classification controls (`ProductCategCtrlLevelCode`, `ProductCategDefault`, `TransCategCtrlLevelCode`, `IntendedUseDefault`), registration defaults (`RegistrationTypeCode`, `RegistrationStatusCode`, `ValidationType`, `ValidationLevel`, `UniquenessValidationLevel`), the `RoundingRuleCode`, and tax authority party names (`CollectPartyName`, `IssuePartyName`, `ReportPartyName`). Use the skill to read a country's defaults (safe), or to create them on an environment you own, with approval.

## Placeholders
```text
FSCR     = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H        = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN      = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
COUNTRY  = the 2-letter country code (e.g. US)
REGIME, TAX = the default regime and tax codes (they must exist for COUNTRY; GUESS)
```

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; `timeout 120` before REST reads. On HTTP 401/403, an expired token or a hang, sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). Never print tokens, headers, the server address or user names; FSCR's output file names hold the environment name, never copy them into a report.

## Prerequisites
1. If the row names a default regime and tax: REGIME and TAX exist for COUNTRY (skills `manage-tax-regimes` and `manage-taxes`; on a shared environment only your own not-live test regime, and never make a test tax live).
2. For Step 4 only: written approval from whoever owns the environment, naming COUNTRY and every value, because every transaction in COUNTRY is affected.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz"
```
VERIFIED (about 65 s): 2 files, `ZX_COUNTRY_DEFAULTS.csv` (52 columns, one object, XML path `CountryTaxDefaultControlsVO`) and the metadata. Our export had **0 rows**: no country had default controls. If COUNTRY has a row, read it with `python -I "<GAPS>/common-features/search-legal-entities/scripts/view_record.py" "<RUN>/export_before/unz" --value <COUNTRY> --match-cols CountryCode` (no audit columns). A country that already has a row must **not** be imported again (that is an update).

## Step 3. Build the row (GUESS: not run)
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name country_defaults.zip \
  --prefix "" --key "ZX_COUNTRY_DEFAULTS.csv=CountryCode" --max-rows 1 \
  --row "ZX_COUNTRY_DEFAULTS.csv|CountryCode=<COUNTRY>|TaxRegimeCode=<REGIME>|Tax=<TAX>|DefRegimeForInvoiceFlag=Y|DefTaxForInvoiceFlag=Y|DefRegimeForLeTrFlag=N|DefTaxForLeTrFlag=N"
```
- The builder's `--key` refuses a country that already has a row (no update). VERIFIED for the builder; the rest GUESS.
- Fill the other control columns only with values the person names; their lookup codes (`ProductCategCtrlLevelCode`, `TransCategCtrlLevelCode`, `RoundingRuleCode`, `RegistrationStatusCode`, ...) should be read live from the tax lookups by REST (`standardLookups` or the tax lookups of `manage-tax-lookup-codes`), never copied from another environment (GUESS which lookup types).
- If the import says a column is required (`JBO-27014 ... is required`), add that column only (lesson from batch 4).

## Step 4. Import (GUESS: not run; only with the approval of Prerequisite 2)
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS --task-name "Manage Country Default Controls" \
  --zip-file "<RUN>/payload/country_defaults.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result"
```
Write down the `ProcessId`. `0 rows were processed` is a failure. If the connection drops after the process started, do not import again: wait 2 minutes and do Step 5. A generic database error at the insert (`JBO-26041`): fill `CreatedBy`/`LastUpdatedBy` with the export metadata's `SubmittedBy` (read at run time, never print it).

## Step 5. Read back
Repeat Step 2 into `export_after`, then:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_COUNTRY_DEFAULTS.csv=CountryCode" --expect "ZX_COUNTRY_DEFAULTS.csv=<COUNTRY>"
```
`RESULT: PASS` = only your country row was added. No REST resource for country defaults was found (GUESS).

## Rules and limits
1. Step 2 is safe anywhere. Steps 3 to 5 change tax defaulting for a whole country: only on an environment you own, with written approval.
2. Never load a test row on a shared test environment (why this skill was not load-tested); there is no "test country".
3. Not tested: the import, any column value, a default tax that is live.
4. Export seen on one environment (release 11.13.26.10.0).

## Worked example (read part only, VERIFIED 2026-11-25)
| Step | Result |
|---|---|
| Export | 2 files, `ZX_COUNTRY_DEFAULTS.csv` 52 columns, 0 rows; about 65 s |
| Import | not run (unsafe: changes tax defaults for every transaction in the country) |
