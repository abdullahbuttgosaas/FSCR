---
name: manage-aging-periods
task_code: AP_MANAGE_AGING_PERIODS
task_name: Manage Aging Periods
module: Payables
route: FSM setup CSV export/import (task level); header + lines in one package
---

# Manage Aging Periods (CSV)

## What it is and when to use

Creates a Payables aging period definition (tables AP_AGING_PERIODS and AP_AGING_PERIOD_LINES; business
objects "Aging Period Header" and "Aging Period Line") through the FSM setup CSV import of task
`AP_MANAGE_AGING_PERIODS`. An aging period is a named set of day ranges (columns) used by the Payables
invoice aging report, for example "Current", "1 to 60 days", "Over 60 days".

## Placeholders

| Placeholder | Meaning |
| --- | --- |
| `<FSCR_ROOT>` | FSCR repository root (run every command from there) |
| `<RUN>` | a run folder OUTSIDE the repository and outside any git repo |
| `<NAME>` | the new aging period name (GUESS: up to 15 characters is safe; tested with 17, so longer works) |
| `<DESCRIPTION>` | short neutral description (for a test, start it with your prefix) |
| `<GF_SCRIPTS>` | `gaps-filled/payables/scripts` inside the pack (helper scripts, standard library only) |
| `<YOUR_TEST_PREFIX>` | the common start of your new names (for example your test prefix); a safety check in the builder |

Create `<RUN>` first (`mkdir -p <RUN>`). Do not share it: the raw export CSVs and logs in it hold user names.

## Sign-in

Use FSCR's `core/auth/fusion-oauth-authentication` (`fusion_login.py`, token cache `auto`). A sign-in lasts
about one hour. If you are not allowed to sign in yourself, stop and report on HTTP 401/403; otherwise
sign in again and continue. Never print tokens, server addresses or user names.

## Prerequisites

1. Signed in. An aging period is stand-alone; nothing else must exist.
2. The name must be new: after the export below, search for it (step "Export"). `--grep` matches parts of
   names, so look for an EXACT PeriodName match. If it exists, pick another name.

## Export (read only)

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_AGING_PERIODS --run <RUN> --label before
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip --file AP_AGING_PERIOD.csv --grep <NAME> --cols PeriodName,Status
```

Two CSVs (VERIFIED):
- `AP_AGING_PERIOD.csv` (header): PeriodName, Description, Status, AttributeCategory, Attribute1-15 and
  who/date columns.
- `AP_AGING_PERIOD_LINE.csv` (lines): `AP_AGING_PERIOD.PeriodName` (link to the header), PeriodSequenceNum,
  DaysStart, DaysTo, Type, ReportHeading1, ReportHeading2, ReportHeading3, AttributeCategory, Attribute1-15
  and who/date columns.

## Build rows

The header and ALL its lines go in the same package (lines are processed under the header object).
`<RUN>/rows.json` (VERIFIED):

```json
{"AP_AGING_PERIOD.csv": [{"PeriodName": "<NAME>", "Description": "<DESCRIPTION>", "Status": "A"}],
 "AP_AGING_PERIOD_LINE.csv": [
  {"AP_AGING_PERIOD.PeriodName": "<NAME>", "PeriodSequenceNum": "1", "DaysStart": "-30", "DaysTo": "0",
   "Type": "CURRENT", "ReportHeading1": "Current", "ReportHeading2": "not due"},
  {"AP_AGING_PERIOD.PeriodName": "<NAME>", "PeriodSequenceNum": "2", "DaysStart": "1", "DaysTo": "60",
   "Type": "PAST", "ReportHeading1": "1 to 60", "ReportHeading2": "days overdue"},
  {"AP_AGING_PERIOD.PeriodName": "<NAME>", "PeriodSequenceNum": "3", "DaysStart": "61", "DaysTo": "999999999",
   "Type": "PAST", "ReportHeading1": "Over 60", "ReportHeading2": "days overdue"}]}
```

- Status `A` = active (VERIFIED: all existing rows use A).
- Type `CURRENT` (not yet due, days <= 0) or `PAST` (overdue) (VERIFIED in the data).
- PeriodSequenceNum = column order on the report, 1, 2, 3 ...; day ranges should not overlap (GUESS: not
  validated by the import).
- `999999999` = open-ended last column (VERIFIED, used by existing rows).
- Who-columns stay empty (VERIFIED: the import fills them).

```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export <RUN>/before.zip --rows <RUN>/rows.json \
  --prefix <YOUR_TEST_PREFIX> --out <RUN>/load.zip
```

The builder must report `AP_AGING_PERIOD.csv 1 row(s), AP_AGING_PERIOD_LINE.csv <n> row(s)`.

## Import

```bash
python3 <GF_SCRIPTS>/gf_import.py --task-code AP_MANAGE_AGING_PERIODS --zip <RUN>/load.zip --run <RUN> --label imp1
```

The console lines "StatusCode: (no result yet)" / "(unknown)" are normal; the process log text decides.
Success (VERIFIED): "Aging Period Header ... A total of 1 rows were processed. 0 rows of them failed" and
"Aging Period Line ... This object was already processed ... listed under the Aging Period Header" (the
log counts only the header; the export compare below proves the lines). Keep the ProcessId
(`<RUN>/imp1_processid.txt`). If the connection drops after the import started, do NOT import again: wait
2 minutes and export again to check.

## Read back

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_AGING_PERIODS --run <RUN> --label after
python3 <GF_SCRIPTS>/compare_fsm_exports.py --before <RUN>/before.zip --after <RUN>/after.zip --prefix <YOUR_TEST_PREFIX>
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/after.zip --file AP_AGING_PERIOD_LINE.csv --grep <NAME> \
  --cols AP_AGING_PERIOD.PeriodName,PeriodSequenceNum,DaysStart,DaysTo,Type
```

Pass = header +1, lines +<n>, and `RESULT: OK - only prefix rows added, nothing removed or changed`.
There is no REST resource for aging periods (VERIFIED: `payablesAgingPeriods`, `agingPeriods` return 404).

## Rules and limits

- New names only. Never re-send an existing period or its lines (the import merges by name and sequence
  and would update them); never load the full export back.
- To add a line to your OWN period later, send its header row unchanged plus the new line (GUESS).

## Worked example (sitting 1)

- `FSCRT_AK_GF_AGE1` with 3 lines: import ProcessId 100004744404007, header 1 row processed, 0 failed;
  export compare: header +1, lines +3, removed/changed 0 (VERIFIED). Row counts depend on the environment;
  only the "+" numbers and "removed/changed 0" matter.
