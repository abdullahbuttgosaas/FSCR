---
skill_id: "gosaas.gap-fills.common-features.manage-archive-purge-policies"
name: "Manage Archive and Purge Policies: read the policies, and (on an owned environment only) add a ledger-level retention row by FSM CSV (GoSaaS gap fill)"
description: "Reads the Financials archive and purge policies (global retention years per business object, and ledger / balancing segment exceptions) through the task's FSM CSV export, and describes how to add one ledger-level exception row. The load is UNSAFE on a shared environment: a row needs a real ledger and balancing segment value and changes how long that ledger's accounting data is kept before purge. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 17, 2026-11-26. Export VERIFIED; load not run (unsafe). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_MANAGE_FINANCIALS_BUSINESS_OBJECTS_ARCHIVE"
task_name: "Manage Archive and Purge Policies"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Step 1 is read only. Step 3 (not run) sets a retention period for one ledger and balancing segment value: Oracle's archive and purge programs then keep or purge that ledger's accounting data by it. There is no delete by CSV."
---

# Manage Archive and Purge Policies (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.
> **Status: written, unsafe to test on a shared environment.** Run Step 3 only on an environment you own, with the finance owner's written approval.

## What it is and when to use
The task sets how many years Financials keeps data before the archive and purge programs may remove it. The package (VERIFIED, 2 files):
- `ORA_ARCHIVE_AND_PURGE_POLICY.csv`: one row per business object: `BusinessObjectCode`, `RetentionYears`, `TransactionRetentionYears` (VERIFIED: one row, `ORA_ACCOUNTING_DATA`)
- `ORA_ARCHIVE_AND_PURGE_POLICY_DETAIL.csv`: exceptions per ledger: `BalancingSegmentValue`, `LedgerName`, `BusinessObjectCode`, `LegalEntityIdentifier`, `RetentionYears` (VERIFIED: 0 rows)
Use Steps 1-2 to read the policies. Use Step 3 only to add an approved exception on an owned environment.

## Why it is unsafe to test here (VERIFIED)
1. The policy file has one global row per business object. Changing it changes the rule for every ledger; this skill never sends it changed.
2. A detail row **must** name a ledger and a balancing segment value. Try 1 (ProcessId 100004743458273) sent a row with only a test legal entity (`GAPFILL_AB_B14_LE1`, which has no ledger) and was refused: `JBO-27014: Attribute LedgerId in GlPurgeSetupDetailsEO is required.` and `... BalancingSegmentValue ... is required.` (1 processed, 1 failed). The export after it still has 0 detail rows: nothing was created.
3. The test legal entities have no ledger, and no test ledger exists. A detail row on a real ledger changes when that ledger's accounting data may be purged, and there is no delete by CSV.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
LEDGER= an approved ledger name (read by REST ledgersLOV, read only)
BSV   = a balancing segment value of that ledger's chart of accounts
LE    = the legal entity identifier tied to that BSV (optional, GUESS)
YEARS = retention years (whole number, GUESS: not less than the global row's value)
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; with a valid cached sign-in it returns at once). Never print tokens, the server address or user names; never copy FSCR's output file names; never print the ZIP's `ASM_SETUP_CSV_METADATA.xml`.

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_MANAGE_FINANCIALS_BUSINESS_OBJECTS_ARCHIVE --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
python -I -c "import csv,sys,glob,os; [print(os.path.basename(f), list(csv.DictReader(open(f,encoding='utf-8-sig')))) for f in sorted(glob.glob(sys.argv[1]+'/*.csv'))]" "<RUN>/exp1/unz"
```
2 CSVs + metadata. The rows hold no who columns (VERIFIED), so printing them is safe. No ZIP: run again into a NEW folder, up to 3 tries.

## Step 2. Read the ledgers (REST, read only, VERIFIED)
`python -B <GAPS>/common-features/scripts/rest_call.py "<FSCR>" /fscmRestApi/resources/11.13.18.05/ledgersLOV --query onlyData=true --query limit=200 --no-open-browser --output "<RUN>/ledgers.json"`, then print only `Name`, `LedgerCategoryCode`, `ChartOfAccountsId`. Pick `<LEDGER>` with the finance owner (PRIMARY ledger, GUESS).

## Step 3. Build and import ONCE (GUESS, owned environment only)
Build a ZIP from the export: keep both CSV headers and the metadata XML; leave the policy file header only (GUESS: the detail import does not need its parent row; try 1 was processed without it) and write one detail row:
```text
"BalancingSegmentValue","LedgerName","BusinessObjectCode","LegalEntityIdentifier","RetentionYears"
"<BSV>","<LEDGER>","ORA_ACCOUNTING_DATA","<LE>","<YEARS>"
```
Then:
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ORA_MANAGE_FINANCIALS_BUSINESS_OBJECTS_ARCHIVE --task-name "Manage Archive and Purge Policies" --zip-file "<RUN>/pay/arc.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|JBO-[0-9]+: [^\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
Want `1 rows were processed. 0 rows of them failed`. Print only these grep lines (the log holds the environment name and a user).

## Step 4. Read back (GUESS)
Export again into `exp2` and check that the detail file has exactly one more row, yours, and the policy row is unchanged (`compare_fsm_exports.py` with `--key "ORA_ARCHIVE_AND_PURGE_POLICY.csv=BusinessObjectCode" --key "ORA_ARCHIVE_AND_PURGE_POLICY_DETAIL.csv=LedgerName,BalancingSegmentValue,BusinessObjectCode" --expect "ORA_ARCHIVE_AND_PURGE_POLICY_DETAIL.csv=<LEDGER>,<BSV>,ORA_ACCOUNTING_DATA"`).

## Rules and limits
1. Never send the global policy row changed. Never run Step 3 on a shared environment.
2. There is no delete by CSV; a wrong detail row must be fixed on the page.
3. Tested on one environment (release 11.13.26.10.0): Steps 1-2 and the refusal of a row without ledger.

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Export | policy `ORA_ACCOUNTING_DATA` 99 / 98 years; 0 detail rows |
| Try 1 | detail row with only test legal entity `GAPFILL_AB_B14_LE1`: ProcessId 100004743458273; 1 processed, 1 failed (LedgerId and BalancingSegmentValue required) |
| Export after | still 1 policy row (unchanged) and 0 detail rows: nothing created |
