---
skill_id: "gosaas.gap-fills.common-features.manage-shorthand-aliases"
name: "Manage Shorthand Aliases (GoSaaS gap fill)"
description: "Create a new, disabled shorthand account alias on an existing chart of accounts instance through FSCR's setup-task CSV export and import (ORA_GL_ACCOUNT_ALIAS package), copying the segment values of an existing alias, then read it back with a second export. New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 3 part 3, 2026-11-24. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_GL_MANAGE_SHORTHAND_ALIASES"
task_name: "Manage Shorthand Aliases"
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
  - "gosaas common-features/manage-tax-regimes/scripts/template_row.py"
  - "a chart of accounts instance that already has at least one shorthand alias"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import that creates one new shorthand alias, disabled (EnabledFlag=N), so nobody can pick it. It may not be deletable; plan as if it stays."
---

# Manage Shorthand Aliases (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file.
> Labels: **VERIFIED** = seen in our live test (2026-11-24) · **GUESS** = judgment, not tested.

## What this setup is
A shorthand alias is a short name for a full or partial account combination of one chart of accounts **instance** (key flexfield `GL#`). Users type the alias instead of the segments. This skill creates **one alias, disabled** (`EnabledFlag=N`), that copies the segment values of an existing alias on the same instance (so the segment values are known to be valid).

## When to use
- Someone asks to create a **new** shorthand alias for task `ORA_GL_MANAGE_SHORTHAND_ALIASES`.
- Do **not** use it to change or enable existing aliases. New records only. Enabling a test alias needs the person's explicit approval.

## Placeholders
```text
FSCR     = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
           If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS     = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H        = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
T        = <GAPS>/common-features/manage-tax-regimes/scripts          (template_row.py)
RUN      = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX   = your test prefix, e.g. GAPFILL_<INITIALS>_
ALIAS    = new alias code AND name: upper case letters, digits and _, starting with PREFIX, max 30 (GUESS)
DESC     = a description, e.g. "GAPFILL XX shorthand alias 1 (disabled test)" (no "|" character)
INSTANCE = StructureInstanceCode of the chart of accounts instance (the person names it, or Step 3)
TEMPLATE = Name of one existing alias on INSTANCE to copy the segment values from (Step 3)
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (never `/e/...`: FSCR then writes to a wrong folder), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_GL_MANAGE_SHORTHAND_ALIASES --data \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
```
Expect 3 files (VERIFIED, 25 to 200 s): `ORA_GL_ACCOUNT_ALIAS.csv` (113 columns: `ApplicationShortName, KeyFlexfieldCode, StructureInstanceCode, ShorthandAliasCode, EnabledFlag, StartDateActive, EndDateActive, Segment1..30, Name, Description, ...`), `ORA_GL_ACCOUNT_ALIAS_TRANSLATION.csv` and `ASM_SETUP_CSV_METADATA.xml`.
- If the export drops (no ZIP), run it again into a new folder, one at a time, up to 3 tries. If it still fails: **stop**.

## Step 3. Choose INSTANCE and TEMPLATE, check the name
```bash
python -I -c "import csv,sys; [print(r['StructureInstanceCode'],'|',r['Name'],'| enabled',r['EnabledFlag'],'| from',r['StartDateActive'],'| segs',[r['Segment%d'%i] for i in range(1,31) if r['Segment%d'%i]]) for r in csv.DictReader(open(sys.argv[1]+'/ORA_GL_ACCOUNT_ALIAS.csv',encoding='utf-8-sig'))]" "<RUN>/export_before/unz"
```
1. **INSTANCE**: the one the person names. If none is named, the instance of the **first listed** alias whose Name does not start with a test prefix. VERIFIED
2. **TEMPLATE**: the first listed alias on INSTANCE whose Name does not start with a test prefix. Its segment values are copied. VERIFIED
3. If INSTANCE has **no alias at all**, **stop**: an alias written out in full (segment values chosen by hand) was not tested.
4. **ALIAS is free:** it must not be in the Name list for INSTANCE (the builder checks the key again).
5. **About `ShorthandAliasCode`:** aliases made on the screen show a 16 to 17 digit number in front of the name (`<number><Name>`). That number is internal; **never copy it**. A new alias imported with `ShorthandAliasCode = ALIAS` (no number) was accepted and stored exactly as given. VERIFIED

## Step 4. Build a package with only the new alias
```bash
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_GL_ACCOUNT_ALIAS.csv \
  --match "StructureInstanceCode=<INSTANCE>" --match "Name=<TEMPLATE>" \
  --set "ShorthandAliasCode=<ALIAS>" --set "Name=<ALIAS>" --set "Description=<DESC>" \
  --set "EnabledFlag=N" --set "StartDateActive=<yyyy/mm/dd>" --clear EndDateActive --out "<RUN>/rows.txt"
python -I "<T>/template_row.py" --export-dir "<RUN>/export_before/unz" --file ORA_GL_ACCOUNT_ALIAS_TRANSLATION.csv \
  --match "ORA_GL_ACCOUNT_ALIAS.StructureInstanceCode=<INSTANCE>" --match "Name=<TEMPLATE>" --match "Language=US" \
  --set "ORA_GL_ACCOUNT_ALIAS.ShorthandAliasCode=<ALIAS>" --set "ShorthandAliasCode=<ALIAS>" \
  --set "Name=<ALIAS>" --set "Description=<DESC>" --out "<RUN>/rows.txt" --append
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name alias_new.zip --prefix <PREFIX> \
  --key "ORA_GL_ACCOUNT_ALIAS.csv=StructureInstanceCode,Name" \
  --key "ORA_GL_ACCOUNT_ALIAS_TRANSLATION.csv=ORA_GL_ACCOUNT_ALIAS.StructureInstanceCode,Name,Language" \
  --prefix-col "ORA_GL_ACCOUNT_ALIAS.csv=ShorthandAliasCode" --prefix-col "ORA_GL_ACCOUNT_ALIAS.csv=Name" \
  --max-len "Name=30" @"<RUN>/rows.txt"
```
- `StartDateActive`: today or the first day of this year (we used 2026/01/01). VERIFIED
- The builder must print `ORA_GL_ACCOUNT_ALIAS.csv: 1 new rows` and `ORA_GL_ACCOUNT_ALIAS_TRANSLATION.csv: 1 new rows`. It stops if ALIAS exists, lacks the prefix or is too long.
- If the translation file has no `Language=US` row for TEMPLATE, use the language your environment has.

## Step 5. Import
**Approval.** The person must approve the environment, the task, INSTANCE and the exact ALIAS before the import. If their brief names them (or lets you choose) and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_GL_MANAGE_SHORTHAND_ALIASES --task-name "Manage Shorthand Aliases" \
  --zip-file "<RUN>/payload/alias_new.zip" \
  --token-cache auto --wait-seconds 400 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- **Write down the `ProcessId`** the script prints (`Started setup task CSV import process: <id>`). It is the only key to the full process log later; the ESS request number does not open it.
- About 2 minutes. Print a short summary of the process log:
  ```bash
  python -I -c "import sys,glob,re; t=open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n',chr(10)).replace(chr(92)+'t',' ').replace(chr(92)+'/','/'); print(chr(10).join(sorted(set(re.findall(r'Detail Object: \w+\. Status: [^.]+\. Status Details: A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed|Message Text: [^\n]*|Total Objects \w+: [0-9]+',t)))))" "<RUN>/import_result"
  ```
- Success (VERIFIED): `Detail Object: AccountAlias. Status: Completed successfully ... A total of 1 rows were processed. 0 rows of them failed` and `Total Objects Failed: 0`. **`0 rows were processed` is a failure.**
- **If the script loses the connection after the process started**, the import still runs in Oracle. **Do not import again.** Wait 2 minutes and do Step 6.
- Rows failed: copy the error, change one thing, retry at most 3 times; never import twice while one may still be running.

## Step 6. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "ORA_GL_ACCOUNT_ALIAS.csv=StructureInstanceCode,Name" \
  --key "ORA_GL_ACCOUNT_ALIAS_TRANSLATION.csv=ORA_GL_ACCOUNT_ALIAS.StructureInstanceCode,Name,Language" \
  --expect "ORA_GL_ACCOUNT_ALIAS.csv=<INSTANCE>,<ALIAS>" --expect "ORA_GL_ACCOUNT_ALIAS_TRANSLATION.csv=<INSTANCE>,<ALIAS>,US" \
  --rows-out "<RUN>/added_rows.csv"
```
`RESULT: PASS` = only your alias and its translation were added, nothing removed or changed. Also check in `added_rows.csv` that `EnabledFlag` is `N`. If someone else changed aliases between your two exports, judge your own rows plus `removed 0` and `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export.
2. Keep both CSV files and the metadata XML unchanged in layout; only the new alias and its translation go in.
3. Keep the alias **disabled** in a test. Enabling needs the person's approval.
4. Test records may stay for good. This skill never deletes. Record every created alias.
5. No REST resource was searched for aliases; the export compare is the proof.
6. Not tested: aliases on an instance with no alias yet, partial combinations chosen by hand, end-dated aliases.
7. Tested on one environment (release 11.13.26.10.0).
8. Python flags: `-B` without `-I` for FSCR scripts; `-I` for `template_row.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-24). Do not reuse this name; it now exists.
| Step | Result |
|---|---|
| Export before | 7 aliases on 6 instances; about 200 s (3 exports in parallel) |
| Template | the first listed alias (a 4-segment cash account) on its instance |
| New record | `GAPFILL_AB_P3_SA1`, disabled, from 2026/01/01, same segment values as the template |
| Import | 1 attempt (ProcessId 100004742406277), about 2 min: AccountAlias 1 row, 0 failed |
| Export after + compare | 8 aliases; added 1 + 1, removed 0, changed 0; code stored as `GAPFILL_AB_P3_SA1` (no number prefix): PASS |
