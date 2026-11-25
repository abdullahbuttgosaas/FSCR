---
skill_id: "gosaas.gap-fills.common-features.view-accounting-configuration-summary"
name: "View Accounting Configuration Summary (GoSaaS gap fill)"
description: "Show the accounting configuration of a ledger (category, currency, calendar, chart of accounts, secondary ledgers, legal entities and their balancing segment values) without a screen: the ledgersLOV REST resource plus FSCR's read-only setup-task CSV export of GL_VIEW_ACCOUNTING_CONFIGURATION_SUMMARY. Read only: creates and changes nothing. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 05, 2026-11-25. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_VIEW_ACCOUNTING_CONFIGURATION_SUMMARY"
task_name: "View Accounting Configuration Summary"
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

# View Accounting Configuration Summary (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task; it has no skill or guide. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-25) · **GUESS** = judgment, not tested.

## What it is and when to use
The accounting configuration of a primary ledger is: the ledger itself (currency, calendar, chart of accounts, period type), its secondary or reporting-currency ledgers, the legal entities assigned to it, and the balancing segment values of each legal entity. "View Accounting Configuration Summary" only **shows** this. There is nothing to create. Use the skill when someone asks "how is ledger X set up", "which legal entities and balancing segment values does ledger X have", "does it have a secondary ledger", or before any GL setup step that needs these facts.
- Do **not** use it to change a ledger (Manage Primary Ledger / Complete Primary Ledger Configuration change shared accounting setup).

## Placeholders
```text
FSCR   = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
GAPS   = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H      = <GAPS>/common-features/manage-docseq-categories/scripts   (rest_read.py)
V      = <GAPS>/common-features/search-legal-entities/scripts/view_record.py
RUN    = a NEW empty work folder, OUTSIDE FSCR and outside any git repo, with no folder in its path named exactly "project"
LEDGER = the ledger name the person asks about (usually the primary ledger)
```

## Sign-in
FSCR scripts with full path and `python -B`; Git Bash paths as `E:/...` (never `$PWD` or `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`; `timeout 120` before REST reads. On HTTP 401/403, an expired token or a hang, sign in with `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; never type credentials). Never print tokens, headers, the server address or user names.

## Prerequisites
None (read access to ledgers).

## Step 1. The ledger by REST (seconds)
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource ledgersLOV \
  --q "Name='<LEDGER>'" --fields Name,LedgerCategoryCode,CurrencyCode,PeriodSetName,AccountedPeriodType,ChartOfAccountsId,SequencingModeCode \
  --out "<RUN>/ledger.json" --expect-count 1
```
`READBACK: PASS` = exact name. Gives category (PRIMARY / SECONDARY / ALC), currency, calendar (`PeriodSetName`), period type (a coded value such as `MONTH` plus digits) and the chart of accounts number. VERIFIED. For the chart of accounts **name and code**:
```bash
timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource chartOfAccountsLOV \
  --q "StructureInstanceNumber=<ChartOfAccountsId>" --fields StructureInstanceNumber,StructureInstanceCode,Name \
  --out "<RUN>/coa.json" --expect-count 1
```
(VERIFIED)

## Step 2. Read-only export (about 2 minutes)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code GL_VIEW_ACCOUNTING_CONFIGURATION_SUMMARY --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export"
```
- Success = exit 0 and a ZIP written in `<RUN>/export`; a `StatusCode: (unknown)` line on the way is normal (VERIFIED). The ZIP's file name holds the environment name: never copy it into a report.

Expect 11 files, 10 CSVs plus `ASM_SETUP_CSV_METADATA.xml` (VERIFIED, about 45 to 125 s), among them `GL_LEDGER.csv`, `GL_PRIMARY_LEDGER.csv` (the full ledger options), `ORA_GL_LEDGER_RELATIONSHIP.csv` (secondary and reporting-currency ledgers), `ORA_GL_JOURNAL_CONFIG_DETAIL.csv` (legal entities assigned, with `StatusCode`), `ORA_LEGAL_ENTITY_BAL_SEG_VAL_DEF.csv` (balancing segment values per legal entity). If the export drops, retry into a new folder, one at a time, up to 3 tries.

## Step 3. Show the configuration of one ledger
```bash
python -I "<V>" "<RUN>/export/unz" --value "<LEDGER>" --out "<RUN>/ledger_summary.txt" > /dev/null
```
The rows are long: read them in `ledger_summary.txt` (the same text the viewer would print). Read it like this (VERIFIED):
| File | What you learn |
|---|---|
| `GL_PRIMARY_LEDGER.csv` | one row for the ledger and one per secondary **and** reporting-currency (ALC) ledger under it: `LedgerCategoryCode`, `CurrencyCode`, `PeriodSetName`, `FirstLedgerPeriodName`, `StructureInstanceCode`, suspense/rounding/retained earnings accounts (segment values joined with `.`), sequencing flags |
| `ORA_GL_LEDGER_RELATIONSHIP.csv` | each secondary or reporting-currency ledger: `TargetLedgerName`, `TargetLedgerCategoryCode` (SECONDARY or ALC), `RelationshipTypeCode` (the conversion level, e.g. SUBLEDGER or JOURNAL), `TargetCurrencyCode`, and `RelationshipEnabledFlag` (N = that relationship is turned off) |
| `ORA_GL_JOURNAL_CONFIG_DETAIL.csv` | assigned legal entities (`ObjectTypeCode=LEGAL_ENTITY`, `ObjectName`, `LegalEntityIdentifier`) and the configuration `StatusCode` (CONFIRMED = completed) |
| `ORA_LEGAL_ENTITY_BAL_SEG_VAL_DEF.csv` | balancing segment values per legal entity (`LegalEntityIdentifier`, `FlexSegmentValue`, value set) |
- `GL_PRIMARY_LEDGER.csv` and `GL_SECONDARY_LEDGER.csv` show the same rows (VERIFIED); read one of them.
- Exit 1 = nothing matched: check the exact name with Step 1.

## Build rows / import
None. Read-only task; never import anything for it.

## Read back
Step 1 and Step 3 must agree on category, currency and calendar.

## Rules and limits
1. Read only. Never re-import this export (it would update ledgers).
2. Keep RUN outside git (internal numbers, audit user names).
3. Tested on one environment (release 11.13.26.10.0): 49 ledgers in the export.

## Worked example (VERIFIED, 2026-11-25; one ledger, the counts depend on the ledger)
| Step | Result |
|---|---|
| REST `ledgersLOV` | 1 row: PRIMARY, USD, its own calendar, chart of accounts number |
| Export | 11 files, 49 ledgers, about 45 to 125 s |
| View | 13 rows: the primary ledger and 1 secondary ledger (SUBLEDGER level, USD), 2 legal entities CONFIRMED, 3 balancing segment values |
