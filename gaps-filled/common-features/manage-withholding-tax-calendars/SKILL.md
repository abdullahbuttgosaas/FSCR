---
skill_id: "gosaas.gap-fills.common-features.manage-withholding-tax-calendars"
name: "Manage Withholding Tax Calendars (GoSaaS gap fill)"
description: "Create a new withholding tax calendar (Payables 'other period' calendar header + monthly periods) through FSCR's setup-task CSV export and import (AP_OTHER_PERIOD_TYPE + AP_OTHER_PERIOD_PERIOD), then read it back with a second export and compare (no REST resource found). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 2, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "ORA_ZX_MANAGE_WITHHOLDING_TAX_CALENDARS"
task_name: "Manage Withholding Tax Calendars"
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
  - "Starts one setup-task CSV import that creates one new calendar and its periods. It is used only when a withholding tax (or a Payables setting) points to it. It may not be deletable; plan as if it stays."
---

# Manage Withholding Tax Calendars (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** FSCR has no skill for this task. This skill runs FSCR's scripts in place and edits no FSCR file. It uses the generic helpers of the gap skill `manage-docseq-categories` plus its own `scripts/period_rows.py`.
> Labels: **VERIFIED** = seen in our live test (2026-11-23) · **GUESS** = judgment, not tested.

## What this setup is
Withholding tax uses a Payables "other period" calendar to group withheld amounts by period (for example monthly withholding thresholds and reports). The task's package holds **all** Payables special calendars: a header (`AP_OTHER_PERIOD_TYPE`: name, calendar type, periods per year, frequency, start date, period name format) and one row per period (`AP_OTHER_PERIOD_PERIOD`). Calendar types seen in an export: `GENERAL` and `PAYMENT TERMS`. A withholding tax calendar is a `GENERAL` calendar (GUESS from the screen; the test used `GENERAL`). A new calendar does nothing until a withholding tax or tax code points to it.

## When to use
- Someone asks to create a **new** withholding tax calendar for task `ORA_ZX_MANAGE_WITHHOLDING_TAX_CALENDARS`.
- Do **not** use it to change existing calendars or periods. New records only.

## Placeholders
```text
FSCR    = the FSCR root folder: the one that directly holds core\, shared\ and core\auth\fusionEnv.properties. Read only, never edit.
          If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.
GAPS    = the gaps-filled folder that holds this skill (two levels above this SKILL.md)
H       = <GAPS>/common-features/manage-docseq-categories/scripts   (generic helpers)
SKILL   = the folder of this SKILL.md
RUN     = a NEW empty work folder for this run, OUTSIDE FSCR, with no folder in its path named exactly "project"
PREFIX  = your test prefix, e.g. GAPFILL_<INITIALS>_
NAME    = new CalendarName, starting with PREFIX (upper case, digits, _). MAX 15 CHARACTERS (VERIFIED: 15 worked,
          16 was rejected with JBO-27040 and nothing was created). Count before you build; the builder also checks.
YEAR    = the year whose 12 monthly periods you load, e.g. 2027
```

## Step 0 and Step 1 (safe run, sign-in)
- FSCR scripts with their full path and `python -B`; always `--output-dir` under RUN. Git Bash on Windows: paths as `E:/...` (not `/e/...`), `export PYTHONUTF8=1 MSYS_NO_PATHCONV=1`. Never print tokens, headers, the sign-in URL or the server address.
- Run Step 2 first; if it reports HTTP 401/403 or an expired token, sign in as in FSCR `core/auth/fusion-oauth-authentication`, in the background: `cd "<FSCR>"; python -B core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser --callback-timeout 600`. A person completes the browser page; never type credentials. Sign-in time is waiting time.

## Step 2. Read-only export
```bash
cd "<FSCR>"
python -B shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_WITHHOLDING_TAX_CALENDARS --data \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/export_before"
python -I -c "import sys,zipfile,glob; zipfile.ZipFile(glob.glob(sys.argv[1]+'/*.zip')[0]).extractall(sys.argv[1]+'/unz')" "<RUN>/export_before"
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz" --file AP_OTHER_PERIOD_TYPE.csv --cols CalendarName,CalendarType,PeriodFrequency
python -I "<H>/inspect_export.py" "<RUN>/export_before/unz" --file AP_OTHER_PERIOD_PERIOD.csv --cols ApplicationId
```
Expect 3 files (VERIFIED, 25 to 120 s; counts differ per environment):
- `AP_OTHER_PERIOD_TYPE.csv` (30 columns): `CalendarName, CalendarType, ..., PeriodsPerYear, Description, AttributeCategory, Attribute1..15, ..., PeriodFrequency, StartDate, EffectiveFrom, EffectiveTo, PeriodNameFormat`
- `AP_OTHER_PERIOD_PERIOD.csv` (34): `AP_OTHER_PERIOD_TYPE.CalendarName, AP_OTHER_PERIOD_TYPE.CalendarType, ApplicationId, PeriodYear, EnteredPeriodName, CalendarType, CalendarName, PeriodName, ..., StartDate, EndDate, PeriodNum, Description, ..., DueDate`
- `ASM_SETUP_CSV_METADATA.xml`. If it fails or lacks these files: **stop**.
- **NAME is free:** it must not be in the CalendarName list (no REST resource was found: `payablesCalendars`, `payablesCalendarsLOV`, `specialCalendarsLOV` gave HTTP 404, VERIFIED; the export is the proof).
- **ApplicationId of the periods:** the second command prints the value the existing period rows carry (the Payables application). Use it as APP. If the export has no period rows, stop and ask the person (do not guess).

## Step 3. Build the period rows and the package
```bash
python -I "<SKILL>/scripts/period_rows.py" --name <NAME> --type GENERAL --year <YEAR> --app-id <APP> --out "<RUN>/period_rows.txt"
python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --zip-name wht_cal_new.zip --prefix <PREFIX> \
  --key "AP_OTHER_PERIOD_TYPE.csv=CalendarName,CalendarType" \
  --key "AP_OTHER_PERIOD_PERIOD.csv=AP_OTHER_PERIOD_TYPE.CalendarName,AP_OTHER_PERIOD_TYPE.CalendarType,PeriodName" \
  --prefix-col "AP_OTHER_PERIOD_TYPE.csv=CalendarName" --max-len "CalendarName=15" \
  --row "AP_OTHER_PERIOD_TYPE.csv|CalendarName=<NAME>|CalendarType=GENERAL|PeriodsPerYear=12|Description=<text>|PeriodFrequency=MONTHLY|StartDate=<YEAR>/01/01|PeriodNameFormat=MMM" \
  "@<RUN>/period_rows.txt"
```
- `period_rows.py` writes 12 monthly rows (`PeriodName` like `Jan-27`, `EnteredPeriodName` `Jan`, `PeriodNum` 1 to 12, `PeriodYear` = YEAR, start and end dates `yyyy/mm/dd`); `@file` makes the builder read them. Expect `AP_OTHER_PERIOD_PERIOD.csv: 12 new rows`, `AP_OTHER_PERIOD_TYPE.csv: 1 new rows`. VERIFIED
- The header shape (MONTHLY, 12, format MMM) is the one existing monthly calendars use. Oracle does **not** make the periods from the header in this route: load them (GUESS from the transaction calendar lesson; here the periods were loaded and stored as given).
- Other frequencies (quarterly, weekly) and `DueDate` (payment terms calendars): not tested.

## Step 4. Import
**Approval.** The person must approve the environment, the task, NAME and YEAR. If their brief names them and says to proceed, that is the approval; write it in your log.
```bash
cd "<FSCR>"
python -B shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code ORA_ZX_MANAGE_WITHHOLDING_TAX_CALENDARS --task-name "Manage Withholding Tax Calendars" \
  --zip-file "<RUN>/payload/wht_cal_new.zip" \
  --token-cache auto --wait-seconds 300 --poll-interval 15 --no-open-browser \
  --output-dir "<RUN>/import_result"
```
- About 25 s. `StatusCode: (unknown)` is normal; read `<RUN>/import_result/*_process_log.txt` with
  `python -I -c "import sys,glob; print(open(glob.glob(sys.argv[1]+'/*_process_log.txt')[0],encoding='utf-8').read().replace(chr(92)+'r'+chr(92)+'n', chr(10)))" "<RUN>/import_result"`
- Success (VERIFIED): `Business object: Payables Calendar Period. Status: Completed successfully`, `SpecialCalendarType ... A total of 1 rows were processed. 0 rows of them failed` (the count is calendars; the periods are inside it), `Payables Calendar Type ... This object was already processed`, `Total Objects Failed: 0`.
- `0 rows were processed` is a failure. Rows failed: copy the error, change one thing, retry at most 3 times. `JBO-27040 ... CalendarName exceeds the maximum length` = name over 15 characters; the whole calendar is rejected and nothing is created (VERIFIED).

## Step 5. Read back: second export and compare
Repeat Step 2 with `--output-dir "<RUN>/export_after"`, unzip, then (one `--expect` per period, in the form `<NAME>,GENERAL,<PeriodName>`):
```bash
python -I "<H>/compare_fsm_exports.py" "<RUN>/export_before/unz" "<RUN>/export_after/unz" \
  --key "AP_OTHER_PERIOD_TYPE.csv=CalendarName,CalendarType" \
  --key "AP_OTHER_PERIOD_PERIOD.csv=AP_OTHER_PERIOD_TYPE.CalendarName,AP_OTHER_PERIOD_TYPE.CalendarType,PeriodName" \
  --expect "AP_OTHER_PERIOD_TYPE.csv=<NAME>,GENERAL" \
  --expect "AP_OTHER_PERIOD_PERIOD.csv=<NAME>,GENERAL,Jan-<yy>" --expect "AP_OTHER_PERIOD_PERIOD.csv=<NAME>,GENERAL,Feb-<yy>" ... (all 12) \
  --rows-out "<RUN>/added_rows.csv"
python -I "<H>/inspect_export.py" "<RUN>/export_after/unz" --file AP_OTHER_PERIOD_PERIOD.csv \
  --cols PeriodName,PeriodNum,StartDate,EndDate --where CalendarName=<NAME> --json-out "<RUN>/periods_after.json"
```
A bash loop builds the 12 `--expect` arguments: `E=(); for m in Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec; do E+=(--expect "AP_OTHER_PERIOD_PERIOD.csv=<NAME>,GENERAL,$m-<yy>"); done`, then pass `"${E[@]}"`.
`RESULT: PASS` = only your calendar and its 12 periods were added, nothing removed or changed; the inspect lists each stored period with its number and dates. VERIFIED. If someone else imported calendars between your two exports, judge your own rows plus `removed 0`, `changed 0`, and report the extras.

## Rules and limits
1. New records only; never import a full export (a matching name + type would update that calendar).
2. Keep all 3 files, metadata XML unchanged.
3. Test records may stay for good; this skill never deletes. Record every calendar.
4. Not tested: linking the calendar to a withholding tax, other frequencies, more than one year, `PAYMENT TERMS` calendars.
5. Tested on one environment (release 11.13.26.10.0).
6. Python flags: `-B` without `-I` for FSCR scripts; `-I` for `period_rows.py`, `inspect_export.py`, `build_fsm_package.py`, `compare_fsm_exports.py` and the one-liners.

## Worked example (VERIFIED, 2026-11-23). Do not reuse this name; it now exists.
| Step | Result |
|---|---|
| Export before | 7 calendars, 48 periods; 28 s |
| New records | `GAPFILL_AB_WHT1`, GENERAL, monthly, 12 periods Jan-27 to Dec-27 |
| Import | 1 attempt, 24 s: 1 calendar processed, 0 failed |
| Export after + compare | 8 calendars, 60 periods; added 1 + 12, removed 0, changed 0: PASS |
