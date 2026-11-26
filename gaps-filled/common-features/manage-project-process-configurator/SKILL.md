---
skill_id: "gosaas.gap-fills.common-features.manage-project-process-configurator"
name: "Manage Project Process Configurator: add one configurator with its sources by FSM CSV (GoSaaS gap fill)"
description: "Adds ONE project process configurator (for example for Asset Line Grouping) with up to 8 sources through the task's FSM CSV package. For a test, the configurator is made INACTIVE so no project process uses it. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 16, 2026-11-26. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_PJF_MANAGE_PROJECT_PROC_CONFIGURATOR"
task_name: "Manage Project Process Configurator"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.1"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "Step 3 adds a configurator. Only ONE configurator per business process may be active; an ACTIVE one changes how that process works (for Asset Line Grouping: how project costs are grouped into asset lines). A test always loads Active N."
---

# Manage Project Process Configurator (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR's catalog only routes this task (CSV flag Y). This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen live (2026-11-26) · **GUESS** = not run live.

## What it is and when to use
A project process configurator tells a Project Financial Management process which sources to use, for example which attributes group cost lines into asset lines (business process **Asset Line Grouping**, code `PJC_CAP_LINE_GROUPING`, VERIFIED). The task's package (VERIFIED, 3 files):
- `ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.csv`: `Name`, `ConfigurationType`, `Description`, `UserConfiguration`, `Active`, `BusinessProcess`
- `ORA_PJF_PROJECT_PROCESS_CONFIGURATOR_TRANSLATION.csv`: Oracle fills it (one row per language); send it header only
- `ORA_PJF_PROJECT_PROC_CONFIGURATOR_SOURCES.csv`: `ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.Name` (parent), `Alias`, `EnteredLanguage`, `UserFilter`, `SourceName`
Use it to add a configurator. **For a test**, load it with `Active=N`: an inactive configurator is used by nothing.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
GAPS  = the gaps-filled folder (holds common-features\)
B     = <GAPS>/common-features/manage-docseq-categories/scripts/build_fsm_package.py   (offline builder, new rows only)
CMP   = <GAPS>/common-features/manage-docseq-categories/scripts/compare_fsm_exports.py
W     = <GAPS>/common-features/scripts/rest_call.py   (FSCR's REST client with readable errors)
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path)
PREFIX= your test prefix, e.g. GAPFILL_XX_
CFG   = new configurator name = PREFIX + short name (e.g. GAPFILL_XX_PPC1; up to 240 characters)
BP    = business process meaning, e.g. Asset Line Grouping
SRC   = a source name of that process, e.g. Expenditure Type
```
Git Bash: paths as `E:/...`; `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page on port 8765). About one hour; on HTTP 401/403 or a hang, sign in again. Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name).

## Prerequisites
None: the business process and the source names are seeded. Check the name is free (read only, VERIFIED; prints names and flags only):
```bash
cd "<RUN>"; python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/projectProcessConfigurators --query onlyData=true --query limit=200 --no-open-browser --output cfg0.json > cfg0.log 2>&1
python -I -c "import json; print([(r['Name'],r['BusinessProcess'],r['ActiveFlag']) for r in json.load(open('cfg0.json',encoding='utf-8'))['items']])"
```
`<CFG>` must not be in the list. (`BusinessProcess` is the name shown on the page, `BusinessProcessCode` its code, e.g. `PJC_CAP_LINE_GROUPING`; both describe the same thing.) Note which configurator (if any) is active for `<BP>`: a test never changes it.

## Step 1. Read-only export (VERIFIED, about 1 minute)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code ORA_PJF_MANAGE_PROJECT_PROC_CONFIGURATOR --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/exp1" > "<RUN>/exp1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/exp1"
```
3 CSVs + metadata. They may be empty or already hold other configurators (other testers' rows): the builder adds only your new rows and sends nothing else. No ZIP: run again into a NEW folder (`exp1b`, ...), up to 3 tries, and use that folder in Steps 2 and 4.

## Step 2. Build (offline, VERIFIED)
```bash
cd "<RUN>"; python -I "<B>" --export-dir exp1/unz --out-dir pay --zip-name cfg.zip --prefix <PREFIX> \
 --key "ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.csv=Name" --prefix-col "ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.csv=Name" \
 --row "ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.csv|Name=<CFG>|Description=Test configurator, inactive|Active=N|BusinessProcess=<BP>" \
 --row "ORA_PJF_PROJECT_PROC_CONFIGURATOR_SOURCES.csv|ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.Name=<CFG>|Alias=1|EnteredLanguage=US|SourceName=<SRC>"
```
Success: the builder prints `1 new rows` for the configurator file and for the sources file (the translation file stays header only) and `wrote pay\cfg.zip`.
Rules (VERIFIED by Oracle's refusals): a configurator needs at least one source (`PJB_CONFIG_NO_SOURCE` without it); `Alias` must be a whole number from 1 to 8 (`PJB_CONFIG_INVALID_NUM_ALIAS` for a text alias), one per source. `ConfigurationType` and `UserConfiguration` may stay empty. A second source = a second sources row with `Alias=2`; then, in Step 4, use `--key "ORA_PJF_PROJECT_PROC_CONFIGURATOR_SOURCES.csv=ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.Name,Alias"` and expect `<CFG>,1` and `<CFG>,2` (GUESS: only one source was tested). `UserFilter` was not tested (GUESS).

## Step 3. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code ORA_PJF_MANAGE_PROJECT_PROC_CONFIGURATOR --task-name "Manage Project Process Configurator" --zip-file "<RUN>/pay/cfg.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/imp" > "<RUN>/imp.log" 2>&1
grep -o "Started setup task CSV import process: [0-9]*" "<RUN>/imp.log"
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: [^.]+\. Status: [^.\]+|Message Code: [A-Z_0-9]+\. Message Text: [^\]{0,200}" "<RUN>"/imp/*_process_log.txt | sort -u
```
`--zip-file` must be an absolute path. Write down the ProcessId. Success: `A total of 1 rows were processed. 0 rows of them failed` and 3 `Business object` lines `Completed successfully`: `Project Process Configurator`, `Project Process Configurator Sources` and `Project Process Configurator Source Filters` (Oracle's object for `UserFilter`; it is processed even when no filter is sent). Print only these grep lines (the log holds the environment name and user). A refused row creates nothing. Dropped connection after the ProcessId: never import again; wait 2 minutes and go to Step 4.

## Step 4. Read back (VERIFIED)
Export again (Step 1's two lines with `exp2`), then:
```bash
cd "<RUN>"; python -I "<CMP>" exp1/unz exp2/unz --key "ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.csv=Name" --key "ORA_PJF_PROJECT_PROCESS_CONFIGURATOR_TRANSLATION.csv=ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.Name" --key "ORA_PJF_PROJECT_PROC_CONFIGURATOR_SOURCES.csv=ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.Name" --expect "ORA_PJF_PROJECT_PROCESS_CONFIGURATOR.csv=<CFG>" --expect "ORA_PJF_PROJECT_PROCESS_CONFIGURATOR_TRANSLATION.csv=<CFG>" --expect "ORA_PJF_PROJECT_PROC_CONFIGURATOR_SOURCES.csv=<CFG>"
python -B "<W>" "<FSCR>" /fscmRestApi/resources/11.13.18.05/projectProcessConfigurators --query "q=Name='<CFG>'" --query expand=SourceAsgnmts --query onlyData=true --no-open-browser --output cfg1.json > cfg1.log 2>&1
python -I -c "import json; r=json.load(open('cfg1.json',encoding='utf-8'))['items'][0]; print(r['Name'],r['BusinessProcessCode'],r['ActiveFlag'],[(s['Alias'],s['SourceName']) for s in r['SourceAsgnmts']])"
```
`RESULT: PASS` = one configurator, one translation and one source row added for `<CFG>`, nothing else changed. REST shows `ActiveFlag False` and your source.

## Rules and limits
1. A test loads `Active=N` only; never activate a test configurator (only one per business process may be active).
2. New configurators only: this skill never changes or deletes an existing one (the REST resource can delete; do not use it).
3. Tested only for Asset Line Grouping with one source; other business processes and `UserFilter` are GUESS.
4. Tested on one environment (release 11.13.26.10.0).

## Worked example (2026-11-26, codes and ProcessIds only)
| Step | Result |
|---|---|
| Try 1 (no source) | ProcessId 100004744435070: refused `PJB_CONFIG_NO_SOURCE`, nothing created |
| Try 2 (alias `ET`) | ProcessId 100004744436034: refused `PJB_CONFIG_INVALID_NUM_ALIAS`, nothing created |
| Import | `GAPFILL_AB_B16_PPC1`, Asset Line Grouping, Active N, source 1 = Expenditure Type: ProcessId 100004744435100; 1 processed, 0 failed |
| Compare | configurators 0 → 1, translations 0 → 1, sources 0 → 1, nothing else changed: PASS; REST `ActiveFlag False`, code `PJC_CAP_LINE_GROUPING` |
| Fresh test (another tester, only this skill) | `GAPFILL_AB_B16_PPC2F`: ProcessId 100004744434608; configurators 1 → 2, only own rows added: PASS |
