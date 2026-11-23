---
skill_id: "gosaas.gap-fills.common-features.manage-transaction-calendars"
name: "Manage Transaction Calendars (GoSaaS gap fill)"
description: "Create a new General Ledger transaction calendar (business-day weekdays plus dated business days) through FSCR's setup-task CSV export and import (GL_TRANSACTION_CALENDAR + ORA_GL_TRANSACTION_CALENDAR_DATE package), built from the export headers, then read it back with a second export (there is no REST resource). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 3, 2026-11-20. Written and tested live on one test environment. NOT official FSCR."
tested_by_fresh_chat: "See gap_index.csv (fresh_claude_pass) and CHANGELOG.md"
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "GL_MANAGE_TRANSACTION_CALENDARS"
task_name: "Manage Transaction Calendars"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
type: "import"
execution_mode: "hybrid"
owner_team: "GoSaaS"
version: "0.1.0"
inputs:
  - "fusion_environment_context"
  - "new_calendar_name_weekdays_and_date_range"
outputs:
  - "csv_package_zip"
  - "import_process_log"
  - "export_compare_result"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Starts setup-task CSV export processes (read-only for Fusion data)."
  - "Starts one setup-task CSV import process that creates a new transaction calendar with its dates. It may not be deletable; plan as if it stays."
required_privileges:
  - "Export Import Functional Setups User plus the task privileges for GL_MANAGE_TRANSACTION_CALENDARS"
---

# Manage Transaction Calendars (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's export and import scripts in place and does not edit any FSCR file. It uses the generic helpers of the gap skill `manage-docseq-categories` plus its own `scripts/calendar_rows.py`.
> Labels: **VERIFIED** = seen in our live test (2026-11-20) · **FROM FSCR** = FSCR file · **GUESS** = judgment, not tested.

## What this setup is
A transaction calendar says which days are business days. General Ledger uses it for average balance processing: a ledger with average balances needs a transaction calendar. A calendar has a name, a business-day flag for each weekday (Monday to Sunday), and one row per date (with its day of week and a business-day flag, so a holiday can be a weekday that is not a business day).

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          Write it as E:/... (drive letter); a Git Bash $PWD like /e/... does not work for --fscr or other paths.
GAPS    = the gaps-filled folder (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers; this skill needs that folder in place)
SKILL   = the folder of this SKILL.md
RUN     = a NEW empty work folder OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix (GAPFILL_ in our tests)
NAME    = new calendar name, e.g. GAPFILL_TC_<something>: upper case, digits, _ ; max 25 characters (GUESS; 13 tried)
START, END = first and last date to load (yyyy-mm-dd), at most 31 days by default
```

## Step 0. Safe running
FSCR scripts with full path and `python -B`; always `--output-dir` under `RUN`. Git Bash: `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.

## Step 1. Export first (layout, names in use, sign-in check)
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code GL_MANAGE_TRANSACTION_CALENDARS --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz" --file GL_TRANSACTION_CALENDAR.csv --cols Name
```
- **Sign-in:** if the export says HTTP 401/403 or token expired, or hangs with no output (a token lasts about an hour), sign in: from `<FSCR>`, `python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600` in the background; a person completes the browser page (`Login complete for standard.`); never type credentials. Sign-in is waiting time.
- Expect 3 files (VERIFIED, about 25 to 35 s): `ASM_SETUP_CSV_METADATA.xml`; `GL_TRANSACTION_CALENDAR.csv` (31 columns: `Name, MonBusinessDayFlag ... SunBusinessDayFlag, CreationDate, CreatedBy, LastUpdateDate, LastUpdatedBy, LastUpdateLogin, Description, Attribute1..15, SecurityFlag, AttributeCategory`); `ORA_GL_TRANSACTION_CALENDAR_DATE.csv` (35 columns, starting `GL_TRANSACTION_CALENDAR.Name, TransactionDate, DayOfWeek, BusinessDayFlag`).
- The export holds **all** transaction calendars (VERIFIED: 0 before our test, our new ones after). It may be empty; the files still give the layout. If the export fails or lacks these files: **stop**, note it, do not import.
- **Before-check:** there is no REST resource for transaction calendars (VERIFIED: 5 likely names, all HTTP 404). NAME must not be in the `Name` list printed above.

## Step 2. Build the date rows and the package
```bash
python -I "<SKILL>/scripts/calendar_rows.py" --name <NAME> --start <START> --end <END> \
  --business MON,TUE,WED,THU,FRI [--holiday yyyy-mm-dd] --out "<RUN>/date_rows.txt"
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name txn_cal_new.zip --prefix <PREFIX> \
  --key "GL_TRANSACTION_CALENDAR.csv=Name" --key "ORA_GL_TRANSACTION_CALENDAR_DATE.csv=GL_TRANSACTION_CALENDAR.Name,TransactionDate" \
  --prefix-col "GL_TRANSACTION_CALENDAR.csv=Name" --max-len "Name=25" \
  --row "GL_TRANSACTION_CALENDAR.csv|Name=<NAME>|Description=<text>|MonBusinessDayFlag=Y|TueBusinessDayFlag=Y|WedBusinessDayFlag=Y|ThuBusinessDayFlag=Y|FriBusinessDayFlag=Y|SatBusinessDayFlag=N|SunBusinessDayFlag=N|SecurityFlag=N" \
  "@<RUN>/date_rows.txt"
```
- `@<file>` makes the builder read the date `--row` arguments from the file (one argument per line). Expect `ORA_GL_TRANSACTION_CALENDAR_DATE.csv: N new rows` with N = number of days.
- Keep the weekday flags in the header in line with `--business` (both Mon to Fri in our test).
- Date rows (VERIFIED, all three are required): `TransactionDate` as `yyyy/mm/dd`, `DayOfWeek` as `MON`..`SUN`, `BusinessDayFlag` `Y`/`N`. Without `DayOfWeek` Oracle rejects every date row **and the whole calendar** (`JBO-27014: Attribute DayOfWeek ... is required`; nothing is created).
- A header without date rows also imports cleanly, but Oracle then makes **no** date rows by itself (VERIFIED). Load dates if you need dated business days.
- GUESS: a very long range (a full year) works the same way, but only 7 days were tried; raise `--max-days` only if the person agrees.

## Step 3. Import
**Approval:** the person must approve the environment, the task, the calendar name and the date range; a brief that names them and says proceed is the approval (note it in your work folder).
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code GL_MANAGE_TRANSACTION_CALENDARS --task-name "Manage Transaction Calendars" \
  --zip-file "<RUN>/payload/txn_cal_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 25 s. `StatusCode: (unknown)` is normal; the real result is only in `<RUN>/import_result/*_process_log.txt`. Read it with
  `python -I -c "import sys; print(open(sys.argv[1],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<log file>"`
- Success (VERIFIED): `Business object: General Ledger Transaction Calendar. Status: Completed successfully.`, `TransactionCalendar ... A total of 1 rows were processed. 0 rows of them failed` (the count is calendars; dates are inside it), the date object "was already processed", `Total Objects Failed: 0`.
- Failure: `Completed with errors`, `1 rows of them failed`, `Total Objects Failed: 2`. Copy the JBO message, fix one thing, rebuild, retry at most 3 times. A failed calendar is not created, so the same name can be used again (VERIFIED).

## Step 4. Read back (second export, then compare)
Repeat Step 1 with `--output-dir "<RUN>/export_after"`, unzip, then (add one `--expect` per date; the dates are those in `date_rows.txt`):
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "GL_TRANSACTION_CALENDAR.csv=Name" --key "ORA_GL_TRANSACTION_CALENDAR_DATE.csv=GL_TRANSACTION_CALENDAR.Name,TransactionDate" \
  --expect "GL_TRANSACTION_CALENDAR.csv=<NAME>" \
  --expect "ORA_GL_TRANSACTION_CALENDAR_DATE.csv=<NAME>,<yyyy/mm/dd of day 1>" --expect "ORA_GL_TRANSACTION_CALENDAR_DATE.csv=<NAME>,<day 2>" ...
python -I "<H>/inspect_export.py" "<RUN>/export_after/unz" --file ORA_GL_TRANSACTION_CALENDAR_DATE.csv \
  --cols GL_TRANSACTION_CALENDAR.Name,TransactionDate,DayOfWeek,BusinessDayFlag --where "GL_TRANSACTION_CALENDAR.Name=<NAME>" --json-out "<RUN>/dates_after.json"
```
`RESULT: PASS` = only your calendar and its dates were added, nothing removed, nothing changed. The inspect output shows each stored date with its day and flag. VERIFIED. Evidence (optional): `python -B "<H>/render_readback.py" --json "<RUN>/dates_after.json" --title "..." --png <file.png>`.

## Rules and limits
1. New records only; never import a full export (a matching calendar name would update that calendar and its dates).
2. Keep all 3 files, metadata XML unchanged.
3. Test records may stay for good; this skill never deletes. Record every calendar you create.
4. A calendar is used only when a ledger with average balances points to it; our test calendars are not assigned to any ledger.
5. Tested on one environment (release 11.13.26.10.0), 7 dates, Mon to Fri business days, one weekday holiday.
6. Python flags: `-B` without `-I` for FSCR scripts and `render_readback.py`; `-I` for `calendar_rows.py`, `inspect_export.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the unzip one-liner.

## Worked example (VERIFIED, 2026-11-20). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 0 calendars, 0 dates |
| `GAPFILL_TC_T1` | header only, Mon to Fri: 1 attempt, 0 failed; no dates generated by Oracle |
| `GAPFILL_TC_T2` attempt 1 | header + 7 dates without DayOfWeek: rejected (`DayOfWeek ... is required`), nothing created |
| `GAPFILL_TC_T2` attempt 2 | header + 7 dates (one week, Thursday as a holiday) with MON..SUN: 0 failed |
| Export after + compare | 2 calendars, 7 dates added; removed 0, changed 0: PASS |
