# Manage Release Sequence Rules (WSH_MANAGE_RELEASE_SEQUENCE_RULES): create a new record by FSM CSV

## What it is and when to use
A release sequence rule sets the order in which shipment lines are released for picking (by order, invoice value, schedule date, initial ship date or shipment priority), each criterion with a priority 1-5 and an ascending or descending sort. Pick wave release rules refer to it.

Use this skill to create a NEW release sequence rule through the setup task's FSM CSV import (task-level export, then
task-level import of a package that holds only your new rows). It never changes an existing record.

Route: FSM CSV (task-level export and import, FSCR `shared/setup-export/task-level-export` and
`shared/setup-import/task-level-import`). VERIFIED.

## Placeholders
| Placeholder | Meaning |
|---|---|
| `<FSCR_ROOT>` | the FSCR repository (pack) root; run every command from there |
| `<GF_SCRIPTS>` | `gaps-filled/inventory-management/scripts` inside `<FSCR_ROOT>` |
| `<RUN_DIR>` | a run folder OUTSIDE the repository (exports hold user names) |
| `<PREFIX>` | your test prefix, for example `FSCRT_AB_GF_` |
| `<NAME>` | the new record's code: `<PREFIX>` plus a short upper-case suffix, max 30 characters in total |
| `<TODAY>` | today's date |

## Sign-in
Use FSCR's PKCE login (the person types their own Oracle user name and password in the browser; never type or
print them, and never print tokens or server addresses):
```bash
python3 core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto
```
If a valid sign-in is already cached (you were told so, or a read-only call works), skip this login and use
`--token-cache auto --no-open-browser` on every command. A sign-in lasts about an hour. On HTTP 401/403 or a call
that hangs, a new sign-in is needed: run the login above if you may, otherwise stop and report "SIGN-IN NEEDED".
On Windows set `PYTHONUTF8=1` first.

Privacy: FSCR starts every export and import file name with the environment name, and the process log names the
submitting user. The export and import scripts also print `Wrote <file path>` lines that contain the environment
name. Never paste file names, folder listings, script output or raw log text into a report; quote only codes,
counts and ProcessIds. FSCR scripts print `StatusCode: (unknown)` even on success; that line is normal.

## Prerequisites
None. The record stands alone (VERIFIED: it loaded with no other record created first).

## Step 1: Read-only export (before)
```bash
python3 shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code WSH_MANAGE_RELEASE_SEQUENCE_RULES --data --wait-seconds 400 \
  --output-dir "<RUN_DIR>/export_before" --token-cache auto --no-open-browser
python3 <GF_SCRIPTS>/inspect_export.py "<RUN_DIR>/export_before/<export zip>"
```
`<export zip>` is the only `*.zip` file in that folder.
Expected package (VERIFIED): `ASM_SETUP_CSV_METADATA.xml` plus `WSH_PICK_SEQUENCE_RULE.csv` (one row per rule) and `WSH_PICK_SEQUENCE_RULE_TRANSLATION.csv` (one row per rule and language).
Check that `<NAME>` is not in the export: `inspect_export.py "<zip>" --grep <NAME>` still prints each CSV's header
and total row count, but there must be no line starting with `row:` whose key column equals `<NAME>` exactly
(`--grep` matches part of a value, so an older record whose name merely starts the same way can show up; that one
does not block you). If the exact name exists, pick
another `<NAME>`; never reuse or update an existing record.
If the export times out, run the same command once more; do not start a third.

## Step 2: Build the rows
Write `<RUN_DIR>/rows.json` with only your new row(s):
```json
{
  "WSH_PICK_SEQUENCE_RULE.csv": [
    {
      "PickSequenceRuleName": "<NAME>",
      "Description": "<PREFIX>TEST release sequence rule",
      "OrderIdPriority": "1",
      "OrderIdSort": "A",
      "StartDateActive": "<TODAY as YYYY/MM/DD> 00:00:00.0",
      "Priority1Rule": "OrderId",
      "Priority1Sort": "A",
      "ObjectVersionNumber": "1"
    }
  ],
  "WSH_PICK_SEQUENCE_RULE_TRANSLATION.csv": [
    {
      "WSH_PICK_SEQUENCE_RULE.PickSequenceRuleName": "<NAME>",
      "Description": "<PREFIX>TEST release sequence rule",
      "Language": "US",
      "PickSequenceRuleName": "<NAME>",
      "SourceLang": "US"
    }
  ]
}
```
**ObjectVersionNumber must be `1`.** Left empty, the import fails at the database insert with `JBO-26041: Failed to post data to database during "Insert"` while the row count still says `0 rows of them failed` (VERIFIED: try 1 failed this way, try 2 with `1` succeeded; existing rows also carry 1). Each criterion you use needs both its `<Criterion>Priority` / `<Criterion>Sort` columns and the matching `PriorityNRule` / `PriorityNSort` pair (criterion names as in the export: OrderId, InvoiceValue, ScheduleDate, ShipmentPri, InitialShipDate; sort `A` or `D`). StartDateActive uses `YYYY/MM/DD HH:MM:SS.0` (VERIFIED).

Build the import package (it keeps every CSV header and only your rows):
```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export "<RUN_DIR>/export_before/<export zip>" \
  --rows "<RUN_DIR>/rows.json" --prefix <PREFIX> --out "<RUN_DIR>/load.zip"
```
Never import the full export: an FSM import merges by key and would re-send every existing record.

## Step 3: Import
```bash
python3 shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code WSH_MANAGE_RELEASE_SEQUENCE_RULES --zip-file "<RUN_DIR>/load.zip" --wait-seconds 400 \
  --output-dir "<RUN_DIR>/import" --token-cache auto --no-open-browser
```
Note the ProcessId: the long number at the end of the written file names (for example 100004744433283). It is
the key to the full process log. The "Request ID" inside the log is a different number (the ESS request).
Check the log with the helper; do not print the raw log (it is one line with literal `\r\n` and names the
environment and the submitter):
```bash
python3 <GF_SCRIPTS>/check_import_log.py "<RUN_DIR>/import/<the only *_process_log.txt file in that folder>"
```
It must end with `IMPORT RESULT: OK (0 failed objects)`. Look at the business object line too: an insert error
shows there as `Completed with errors` with a JBO message even when the row count says `0 rows of them failed`.
If the connection drops after the import started, do NOT import again: wait 2 minutes and go to Step 4.

## Step 4: Read back
1. Export again into `<RUN_DIR>/export_after` (same command as Step 1, other folder).
2. Compare:
   ```bash
   python3 <GF_SCRIPTS>/compare_fsm_exports.py --before "<RUN_DIR>/export_before/<zip>" \
     --after "<RUN_DIR>/export_after/<zip>" --prefix <PREFIX>
   ```
   It must end with `RESULT: PASS` and list `<NAME>` among the added codes; existing rows changed or missing
   must be 0. Row counts differ from the worked example because other people add records over time.
3. No REST resource exists for this object (VERIFIED: the obvious resource names return HTTP 404). The export compare is the proof.

## Rules and limits
- PickSequenceRuleName is the key and must be unique (a 16-character name was VERIFIED; maximum not known, GUESS: 30).
- Always check the process log, not only the row count: the business object line shows `Completed with errors` and the JBO error when the insert fails.
- No REST resource for release sequence rules was found (pickReleaseSequenceRules returns 404).
- New records only. Never edit, re-send or delete an existing record.
- Never print or save sign-in values, tokens, server addresses or user names.

## Worked example (VERIFIED; counts will differ in your run)
Record FSCRT_HF_GF_RSR1. Export before: 8 rules. Try 1 (ProcessId 100004743455865) failed with JBO-26041 (ObjectVersionNumber empty), nothing created. Try 2 (ProcessId 100004744434147) succeeded. Export after: 9 rules and 9 translations, 1 added each, existing changed 0.
