---
skill_id: "gosaas.gap-fills.common-features.establish-enterprise-structures"
name: "Establish Enterprise Structures: create one new enterprise configuration (a wizard draft, never loaded) by FSM CSV (GoSaaS gap fill)"
description: "Creates ONE new enterprise configuration header (the draft that the Establish Enterprise Structures guided flow works on) through the task's own 16-file FSM CSV package. The draft is never loaded, so no business unit, legal entity, division or location is created. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 25, 2026-11-27. Tested live (own test, fresh test). NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "HRW_ESTABLISH_ENTERPRISE_STRUCTURES"
task_name: "Establish Enterprise Structures"
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
  - "Step 3 adds one enterprise configuration row (a draft). It shows in the list of the Establish Enterprise Structures page. Nothing is created in the enterprise until someone opens the draft and presses Load Configuration (never do that). No delete by CSV."
---

# Establish Enterprise Structures (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** Labels: **VERIFIED** = seen live 2026-11-27 · **GUESS** = not run live.

## What it is and when to use
*Establish Enterprise Structures* is a guided flow: you build an **enterprise configuration** (a draft with divisions, legal entities, business units, reference data sets, locations, job structures), review it, and then **load** it, which creates the real structures. The task's FSM CSV package (16 files, VERIFIED) holds these drafts. This skill creates **one new draft header** with your prefix and nothing else. Use it to prove the route or to start a draft that a person finishes on the page.

## Placeholders
```text
FSCR  = the FSCR root folder (holds core\, shared\ and the filled-in core\auth\fusionEnv.properties). Read only.
RUN   = a NEW empty work folder OUTSIDE FSCR and outside any git repo (absolute path, E:/... style)
PREFIX= your test prefix, e.g. GAPFILL_XX_
EC    = new configuration name = PREFIX + short name, e.g. GAPFILL_XX_EC1
```
Git Bash: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`.

## Sign-in
`cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` (a person completes the browser page; a valid cached sign-in returns at once). About one hour; on HTTP 401/403 or a hang, sign in again (before a new import, check with an export that the last one did not run). Never print tokens, the server address or user names; never copy FSCR's output file names (they hold the environment name); never print `ASM_SETUP_CSV_METADATA.xml`.

## Prerequisites
None. The enterprise id comes from the export (Step 1).

## Step 1. Read-only export (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code HRW_ESTABLISH_ENTERPRISE_STRUCTURES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/e1" > "<RUN>/e1.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/e1"
cat "<RUN>/e1/unz/HRW_ENTERPRISE_CONFIG.csv"
```
Expect 16 CSV files plus `ASM_SETUP_CSV_METADATA.xml`. `HRW_ENTERPRISE_CONFIG.csv` has the columns `Name`, `EnterpriseId`, `Description` (2026-11-27: 5 drafts, all `EnterpriseId` 1). Check that `<EC>` is not in the list. No ZIP: export again into a NEW folder (up to 3 tries).

## Step 2. Build the package (VERIFIED)
Every file keeps only its header line, except `HRW_ENTERPRISE_CONFIG.csv`, which gets one new row. Use the `EnterpriseId` that all existing rows show.
```bash
mkdir "<RUN>/p1"; cd "<RUN>/e1/unz"
for f in *.csv; do head -1 "$f" > "<RUN>/p1/$f"; done
cp ASM_SETUP_CSV_METADATA.xml "<RUN>/p1/"
printf '"%s","1","GoSaaS gap-fill test configuration, never loaded"\n' "<EC>" >> "<RUN>/p1/HRW_ENTERPRISE_CONFIG.csv"
cd "<RUN>/p1"; python -I -c "import zipfile,os;z=zipfile.ZipFile('../p1.zip','w',zipfile.ZIP_DEFLATED);[z.write(f) for f in sorted(os.listdir('.'))]"
```
Replace `1` if your enterprise id is different. Do not add rows to the other 15 files: they would describe divisions, legal entities and business units of the draft (still only a draft, but not needed to prove the route).

## Step 3. Import ONCE (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py --task-code HRW_ESTABLISH_ENTERPRISE_STRUCTURES --task-name "Establish Enterprise Structures" --zip-file "<RUN>/p1.zip" --token-cache auto --wait-seconds 500 --poll-interval 15 --no-open-browser --output-dir "<RUN>/i1" > "<RUN>/i1.log" 2>&1
grep -h -o -E "A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Business object: Enterprise Configuration\. Status: [^.]+" "<RUN>"/i1/*_process_log.txt
```
Expect `A total of 1 rows were processed. 0 rows of them failed` and `Enterprise Configuration. Status: Completed successfully` (the other 15 objects also say Completed successfully, with nothing to do). Never import twice: after a dropped connection, run Step 4 first.

## Step 4. Read back (VERIFIED)
```bash
cd "<FSCR>"; python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py --task-code HRW_ESTABLISH_ENTERPRISE_STRUCTURES --data --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser --output-dir "<RUN>/e2" > "<RUN>/e2.log" 2>&1
python -I -c "import sys,glob,zipfile; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/e2"
grep "<EC>" "<RUN>/e2/unz/"*.csv
for f in "<RUN>/e1/unz/"*.csv; do b=$(basename "$f"); [ "$(wc -l < "$f")" != "$(wc -l < "<RUN>/e2/unz/$b")" ] && echo "rows changed: $b"; done
```
PASS = `<EC>` is found once, in `HRW_ENTERPRISE_CONFIG.csv`, with your description; the only file whose row count changed is `HRW_ENTERPRISE_CONFIG.csv` (+1). (Another person may add a draft at the same time; then check that only your name is new.)

## Rules and limits
1. Never press **Load Configuration** on the page for a test draft: loading creates real legal entities, business units and locations that cannot be deleted.
2. Only new names with your prefix; a known `Name` would change that draft.
3. No delete by CSV; the draft stays in the list (a person can delete it on the page).

## Worked example (2026-11-27)
| Step | Result |
|---|---|
| Export | 16 files, 5 drafts, EnterpriseId 1 |
| Import `GAPFILL_AB_B25_EC1` | ProcessId 100004743463498, 1 row, 0 failed |
| Read back | new row found; only `HRW_ENTERPRISE_CONFIG.csv` changed (5 -> 6 rows) |
