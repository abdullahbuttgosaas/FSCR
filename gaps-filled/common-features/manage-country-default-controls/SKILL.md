---
skill_id: "gosaas.gap-fills.common-features.manage-country-default-controls"
name: "Manage Country Default Controls: create the tax default controls row of one country by setup-task CSV (GoSaaS gap fill)"
description: "Reads, and creates, the tax country default controls of one country (default tax regime and tax flags, product and transaction category controls, registration defaults) through FSCR's setup-task CSV export/import of ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS (ZX_COUNTRY_DEFAULTS), with an export-compare read-back. Tested with a row for a country nobody transacts in, with every default off. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 06 (written), batch 13 (tested), 2026-11-25. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS"
task_name: "Manage Country Default Controls"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.2.0"
status: "tested (batch 13)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
  - "ZX_MANAGE_TAX_REGIMES and ZX_MANAGE_TAXES (only if the row names a default regime and tax)"
side_effects:
  - "Step 2 is read only."
  - "Step 4 creates one country row; with defaults switched on it sets tax defaults for every transaction and registration in that country."
  - "The CSV route has no delete: a created row stays."
---

# Manage Country Default Controls (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-25) · **GUESS** = not run live.
> **Tested:** a new row with every default flag `N` for a country no business unit or legal entity uses (Steps 2 to 5). **Not tested:** rows that name a default regime or tax, and the category, registration and rounding columns.

## What it is and when to use
Country default controls are **one row per country** (key `CountryCode`) that say, for transactions and registrations in that country: the default tax regime and tax (`TaxRegimeCode`, `Tax`, with flags `DefRegimeForInvoiceFlag`, `DefRegimeForLeTrFlag`, `DefTaxForInvoiceFlag`, `DefTaxForLeTrFlag`), the product and transaction fiscal classification controls (`ProductCategCtrlLevelCode`, `ProductCategDefault`, `TransCategCtrlLevelCode`, `IntendedUseDefault`), registration defaults (`RegistrationTypeCode`, `RegistrationStatusCode`, `ValidationType`, `ValidationLevel`, `UniquenessValidationLevel`), the `RoundingRuleCode`, and tax authority party names (`CollectPartyName`, `IssuePartyName`, `ReportPartyName`). Use the skill to read a country's defaults, or to create them for a country that has no row yet.

## Placeholders
```text
FSCR     = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H        = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
RUN      = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
COUNTRY  = the 2-letter country code (ISO), with NO row in the before-export
REGIME, TAX = default regime and tax codes (only if the person names them; they must exist for COUNTRY)
```

## Step 1. Safe run and sign-in
FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. On HTTP 401/403, an expired token or a hang, sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). Never print tokens or the server address; FSCR's output file names, the export's `CreatedBy`/`LastUpdatedBy` columns and the import's `*_process_log.txt` (Submitted By) hold the environment name or user names: never copy them into a report. Run the helper commands from any folder (they use full paths).

## Prerequisites
1. Setup-task export and import rights.
2. **For a real country:** the approval of whoever owns the environment, naming COUNTRY and every value (every transaction in COUNTRY is affected, and the row cannot be deleted by CSV). If the row names a regime and tax, they exist for COUNTRY (skills `manage-tax-regimes`, `manage-taxes`).
3. **For a test on a shared environment:** COUNTRY must be one nobody transacts in (for example an uninhabited territory such as `AQ`, `BV`, `HM`), with no row yet, and every default flag `N` and no regime, tax or other control value. Such a row has no effect on any transaction. Every test uses a NEW country (a second test of the same country would be an update).

## Step 2. Read-only export (VERIFIED)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before" > "<RUN>/export_before.log" 2>&1
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I -c "import csv,sys; print(sorted(r['CountryCode'] for r in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'))))" "<RUN>/export_before/unz/ZX_COUNTRY_DEFAULTS.csv"
```
VERIFIED (about 60 s): the ZIP unzips into `unz/` as 2 files, `ZX_COUNTRY_DEFAULTS.csv` (52 columns, XML path `CountryTaxDefaultControlsVO`) and the metadata. The last line lists the countries that already have a row (ours: none before batch 13; the test countries added since are in the Worked example). COUNTRY must not be in that list. `export_before.log` may end with `StatusCode: (unknown)`: that is normal; success = the ZIP exists and unzips to those 2 files. If the export fails with a network error (`getaddrinfo failed`), run it again into a new folder (for example `export_before2`) and use that folder from then on.

## Step 3. Build the row (VERIFIED)
Test row (Prerequisite 3):
```bash
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" --zip-name country_defaults.zip \
  --prefix "" --key "ZX_COUNTRY_DEFAULTS.csv=CountryCode" --max-rows 1 \
  --row "ZX_COUNTRY_DEFAULTS.csv|CountryCode=<COUNTRY>|DefRegimeForInvoiceFlag=N|DefRegimeForLeTrFlag=N|DefTaxForInvoiceFlag=N|DefTaxForLeTrFlag=N"
```
- `--key` makes the builder stop if COUNTRY already has a row (that would be an update).
- Only `CountryCode` and the four flags are needed (VERIFIED: imported first try). Oracle adds `RegimeTypeFlag` `I` itself.
- For a real row (Prerequisite 2), add `TaxRegimeCode=<REGIME>|Tax=<TAX>` and set the flags the person names (GUESS: not run). Read lookup codes for other control columns live (tax lookups, skill `manage-tax-lookup-codes`), never copy them from another environment. If the import says a column is required (`JBO-27014 ... is required`), add that column only.

## Step 4. Import (VERIFIED)
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS --task-name "Manage Country Default Controls" \
  --zip-file "<RUN>/payload/country_defaults.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/import_result" > "<RUN>/import.log" 2>&1
```
Write down the `ProcessId` (`Started setup task CSV import process: N` in `import.log`). `import.log` may end with `StatusCode: (unknown)`: that is normal. The result is in `<RUN>/import_result/*_process_log.txt` (VERIFIED, about 40 s): `A total of 1 rows were processed. 0 rows of them failed` and `Business object: Country Tax Default. Status: Completed successfully`. An earlier `Status: In progress` line is normal; check the last `Status:` line and the rows line. Read it with `grep -o "A total of [0-9]* rows were processed. [0-9]* rows of them failed\|Status: [A-Za-z ]*" "<RUN>"/import_result/*_process_log.txt`. If the connection drops after the process started, **do not import again**: fetch the log with `shared/setup-import/task-level-import/scripts/get_setup_task_csv_import_result.py --task-code ZX_MANAGE_COUNTRY_DEFAULT_CONTROLS --process-id <N> --output "<RUN>/import_result/log.txt"`, then do Step 5.

## Step 5. Read back (VERIFIED)
Repeat Step 2's export and unzip lines into `<RUN>/export_after` (on a network retry `export_after2`, and use that folder below), then:
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ZX_COUNTRY_DEFAULTS.csv=CountryCode" --expect "ZX_COUNTRY_DEFAULTS.csv=<COUNTRY>"
```
`RESULT: PASS` = only your country row was added (VERIFIED: `before 0 after 1 | added [('AQ',)] | removed 0 | changed 0`). No REST resource for country defaults was found (GUESS), so the export is the read-back.

## Rules and limits
1. Step 2 is safe anywhere. On a shared environment create only the test row of Prerequisite 3; never a row for a country where anyone transacts, never a second row for a country that has one.
2. The CSV route cannot delete a row: choose COUNTRY with care.
3. Not tested: regime and tax defaults, category, registration and rounding columns.
4. Seen on one environment (release 11.13.26.10.0).

## Worked example (2026-11-25)
| Step | Record | Result |
|---|---|---|
| export (batch 06, batch 13) | - | 52 columns, 0 rows |
| import | `AQ`, 4 flags `N`, ProcessId 100004743428300 | PASS first try |
| compare | - | before 0, after 1, added `AQ` |
| fresh test (F) | `BV`, ProcessId 100004743427417 | PASS first try; before 1, after 2, added `BV` |
| re-test (R) after wording fix | `HM`, ProcessId 100004744404860 | PASS first try; before 2, after 3, added `HM` |
