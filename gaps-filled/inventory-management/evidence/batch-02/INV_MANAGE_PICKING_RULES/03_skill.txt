# Manage Picking Rules (INV_MANAGE_PICKING_RULES): create a new record by FSM CSV

## What it is and when to use
A picking rule decides which material is picked first (for example by lot, revision, subinventory or locator order, with shelf-life and partial-pick options). Picking rule assignments (a separate task) attach a rule to an organization and criteria.

Use this skill to create a NEW picking rule through the setup task's FSM CSV import (task-level export, then
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
| `<NAME>` | the new record's code: `<PREFIX>` plus a short upper-case suffix, max 80 characters in total |
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
  --task-code INV_MANAGE_PICKING_RULES --data --wait-seconds 400 \
  --output-dir "<RUN_DIR>/export_before" --token-cache auto --no-open-browser
python3 <GF_SCRIPTS>/inspect_export.py "<RUN_DIR>/export_before/<export zip>"
```
`<export zip>` is the only `*.zip` file in that folder.
Expected package (VERIFIED): `ASM_SETUP_CSV_METADATA.xml` plus `ORA_INV_RULE.csv` (one row per rule), `ORA_INV_RULE_TRANSLATION.csv` (one row per rule and language) and `INV_RULE_SELECTION_CRITERION.csv` (rule assignments; leave it empty here).
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
  "ORA_INV_RULE.csv": [
    {
      "RuleName": "<NAME>",
      "EnabledFlag": "Y",
      "TypeCode": "2",
      "UserDefinedFlag": "Y",
      "HasActiveAssignments": "false",
      "SingleLot": "N",
      "PartialAllowedFlag": "Y",
      "CustSpecMatchFlag": "N",
      "AllocateLPNFlag": "N",
      "LPNLocationOnlyFlag": "N",
      "ObjectVersionNumber": "1",
      "ObjectVersionNumber1": "1",
      "PartialAllowedFlagBoolean": "true",
      "SingleLotBoolean": "false",
      "Description": "<NAME> test picking rule"
    }
  ],
  "ORA_INV_RULE_TRANSLATION.csv": [
    {
      "ORA_INV_RULE.RuleName": "<NAME>",
      "Language": "US",
      "SourceLang": "US",
      "RuleName": "<NAME>",
      "Description": "<NAME> test picking rule"
    }
  ]
}
```
These values are those of a working user-defined rule (VERIFIED). TypeCode `2` is a picking rule. Keep the flag and its Boolean twin consistent (PartialAllowedFlag Y with PartialAllowedFlagBoolean true; SingleLot N with SingleLotBoolean false). To add sort criteria (LotSort, LocatorSort and their ...Rank columns), copy the codes from an existing rule in your export that sorts that way (GUESS: not tested). Either write the JSON above by hand, or (instead) let `template_row.py` copies a working rule under your new name:
```bash
python3 <GF_SCRIPTS>/template_row.py --export "<RUN_DIR>/export_before/<export zip>" \
  --key-col ORA_INV_RULE.csv:RuleName --key-col ORA_INV_RULE_TRANSLATION.csv:RuleName \
  --template "<an existing user-defined rule with no assignments>" --new <NAME> --out "<RUN_DIR>/rows.json" \
  --set "ORA_INV_RULE.csv:HasActiveAssignments=false"
```
Never copy rows of INV_RULE_SELECTION_CRITERION.csv: they are assignments of other people's rules.

Build the import package (it keeps every CSV header and only your rows):
```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export "<RUN_DIR>/export_before/<export zip>" \
  --rows "<RUN_DIR>/rows.json" --prefix <PREFIX> --out "<RUN_DIR>/load.zip"
```
Never import the full export: an FSM import merges by key and would re-send every existing record.

## Step 3: Import
```bash
python3 shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code INV_MANAGE_PICKING_RULES --zip-file "<RUN_DIR>/load.zip" --wait-seconds 400 \
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
- RuleName is the key and must be unique (a 15-character name was VERIFIED; maximum not known, GUESS: 80).
- No REST resource for picking rules was found (pickingRules returns 404).
- New records only. Never edit, re-send or delete an existing record.
- Never print or save sign-in values, tokens, server addresses or user names.

## Worked example (VERIFIED; counts will differ in your run)
Record FSCRT_HF_GF_PR1. Export before: 24 rules. Import ProcessId 100004743457097: 0 failed objects. Export after: 25 rules and 25 translations, existing changed 0; selection criteria unchanged (18).
