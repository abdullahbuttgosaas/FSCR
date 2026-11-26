---
skill_id: "gosaas.gap-fills.common-features.manage-tax-authority-profiles-brazil"
name: "Manage Tax Authority Profiles for Brazil: update the tax authority profile of YOUR OWN legal authority by FSM CSV (GoSaaS gap fill)"
description: "Updates ONE tax authority profile (ZX_TAX_AUTHORITY_PROFILE: reporting / collecting authority flags and other profile columns) of a legal authority you made yourself, through the task's FSM CSV package. Oracle makes the profile together with the legal authority; this task can only change it. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 16, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_MANAGE_TAX_AUTHORITY_TAX_PROFILES"
task_name: "Manage Tax Authority Profiles for Brazil"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "XLE_MANAGE_LEGAL_AUTHORITIES (your own test legal authority; gosaas manage-legal-authorities)"
side_effects:
  - "Step 3 changes the tax authority profile of ONE party. On a real tax authority this changes how taxes point to it (reporting / collecting). A test changes only a legal authority you made yourself."
---

# Manage Tax Authority Profiles for Brazil (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
A tax authority profile holds the tax settings of a tax authority party: whether it is a reporting authority and/or a collecting authority, plus Brazil-specific descriptive columns (`Attribute1`..`Attribute15`, `AttributeCategory`). The task's package has ONE file, `ZX_TAX_AUTHORITY_PROFILE.csv` (key `PartyNumber`, VERIFIED). Oracle creates the profile when the legal authority is created (GoSaaS skill manage-legal-authorities, VERIFIED), so this task **updates** an existing profile.
Use it to change a tax authority's profile. **For a test**, change only the profile of a legal authority you created yourself (party number starts with your prefix).

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
O     = <GAPS>/common-features/scripts/own_row_package.py   (builds an update of ONE own row; refuses other rows)
CO    = <GAPS>/common-features/scripts/compare_own_update.py (PASS only if no other row changed)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
PREFIX= your test prefix, e.g. GAPFILL_XX_
LA    = the party number of YOUR OWN test legal authority (starts with PREFIX)
FLAG  = CollectingAuthorityFlag or ReportingAuthorityFlag
NEW   = the new value, Y or N: the opposite of the current value (if the current value is empty, use Y)
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765; with a valid cached sign-in it returns at once). About one hour. Steps 1 and 3 use the cached sign-in (`--no-open-browser`): if one fails with HTTP 401/403 or hangs, run this sign-in again, then repeat that step (an import only after checking with an export that it did not run). Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name).

## Prerequisites
1. Your own test legal authority `<LA>`. Run Step 1 first and look for it in the list it prints. If it is missing, create one with `<GAPS>/common-features/manage-legal-authorities/SKILL.md` (it makes the profile too), then run Step 1 again into a new folder.

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_ZX_MANAGE_TAX_AUTHORITY_TAX_PROFILES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
python -I -c "import csv,sys; [print(r['PartyNumber'],'|',r['PartyName'],'| reporting',r['ReportingAuthorityFlag'],'| collecting',r['CollectingAuthorityFlag']) for r in csv.DictReader(open(sys.argv[1],encoding='utf-8-sig'))]" "<RUN>/exp1/unz/ZX_TAX_AUTHORITY_PROFILE.csv"
```
One CSV (`ZX_TAX_AUTHORITY_PROFILE.csv`) + metadata; the last line lists every tax authority profile. If the ZIP has no such CSV, stop: the export failed (check `exp1.log`). Pick `<LA>` (yours) and note its current `<FLAG>`; `<NEW>` is the opposite. No ZIP: run again into a NEW folder (`exp1b`, ...), up to 3 tries, and use that folder in Steps 2 and 4.

## Step 2. Build (offline, VERIFIED)
```bash
cd "<RUN>"; python -I "<O>" --export-dir exp1/unz --file ZX_TAX_AUTHORITY_PROFILE.csv --match PartyNumber=<LA> --prefix <PREFIX> --set <FLAG>=<NEW> --out-dir pay --zip-name tap.zip
```
Success: it prints `<FLAG>: '<old>' -> '<NEW>'` and `wrote pay\tap.zip (1 row in ZX_TAX_AUTHORITY_PROFILE.csv, other files header only)`. It refuses a party number without your prefix.
Do not use the rounding columns: `RoundingRuleCode` / `RoundingLevelCode` were sent (`NEAREST` / `HEADER`), the import said `1 rows processed, 0 failed`, but the export showed them still empty (VERIFIED). Rounding is not kept on a tax authority profile; change the authority flags or the descriptive columns (the latter GUESS).

## Step 3. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ORA_ZX_MANAGE_TAX_AUTHORITY_TAX_PROFILES --task-name "Manage Tax Authority Profiles for Brazil" --zip-file "<RUN>/pay/tap.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
`--zip-file` must be an absolute path. Write down the ProcessId. Success: `A total of 1 rows were processed. 0 rows of them failed` and `Business object: Tax Authority Tax Profile. Status: Completed successfully`. This alone is NOT proof (see Step 2): Step 4 is. Print only these grep lines (the log holds the environment name and user). Dropped connection after the ProcessId: never import again; wait 2 minutes and go to Step 4.

## Step 4. Read back (VERIFIED)
Export again: Step 1's first two lines with `exp1` replaced by `exp2` everywhere (output folder, log name and unzip path), then:
```bash
cd "<RUN>"; python -I "<CO>" exp1/unz exp2/unz --file ZX_TAX_AUTHORITY_PROFILE.csv --key PartyNumber --own <LA> --expect <FLAG>=<NEW>
```
`RESULT: PASS` = same row count, other rows changed 0, your row changed only `<FLAG>` to `<NEW>`.

## Rules and limits
1. Change only your own legal authority's profile; never a real tax authority without approval (Brazilian tax determination may use it).
2. A row is never deleted by CSV; a wrong value is put back by the same steps with the old value.
3. Brazil descriptive columns (`Attribute*`, `AttributeCategory`) were not tested (GUESS).
4. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Export | 6 profiles (5 of them GoSaaS test legal authorities) |
| Try 1 | `GAPFILL_AB_P3_LA3` rounding NEAREST / HEADER: ProcessId 100004743457000, 1 processed, 0 failed, but nothing changed (rounding not kept) |
| Import | `GAPFILL_AB_P3_LA3` CollectingAuthorityFlag Y → N: ProcessId 100004743457053; 1 processed, 0 failed |
| Compare | 6 → 6 rows, other rows changed 0, own row changed `CollectingAuthorityFlag`: PASS |
| Fresh test (another tester, only this skill) | `GAPFILL_AB_P3_LA4F` CollectingAuthorityFlag Y → N: ProcessId 100004744433945; other rows changed 0: PASS |
