# Manage Material Statuses (INV_MANAGE_MATERIAL_STATUSES): create a new record by FSM CSV

## What it is and when to use
A material status controls which transactions are allowed on material in a subinventory, locator, lot or serial number (for example a hold status that blocks sales order issues). Each status has control flags and one transaction-control row per status-controlled transaction type (allowed or not allowed).

Use this skill to create a NEW material status through the setup task's FSM CSV import (task-level export, then
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
1. Status-controlled inventory transaction types (task Manage Inventory Transaction Sources and Types). Seeded ones exist (VERIFIED: 41 with MaterialStatusEnabled Y); read them as shown in Step 2, nothing has to be created.

## Step 1: Read-only export (before)
```bash
python3 shared/setup-export/task-level-export/scripts/export_setup_task_csv.py \
  --task-code INV_MANAGE_MATERIAL_STATUSES --data --wait-seconds 400 \
  --output-dir "<RUN_DIR>/export_before" --token-cache auto --no-open-browser
python3 <GF_SCRIPTS>/inspect_export.py "<RUN_DIR>/export_before/<export zip>"
```
`<export zip>` is the only `*.zip` file in that folder.
Expected package (VERIFIED): `ASM_SETUP_CSV_METADATA.xml` plus `INV_INVENTORY_STATUS.csv` (one row per status), `INV_INVENTORY_STATUS_TRANSACTION_CONTROL.csv` (one row per status and transaction type) and `INV_INVENTORY_STATUS_TRANSLATION.csv` (one row per status and language).
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
  "INV_INVENTORY_STATUS.csv": [
    {
      "StatusCode": "<NAME>",
      "EnabledFlag": "1",
      "ZoneControl": "1",
      "LocatorControl": "1",
      "LotControl": "2",
      "SerialControl": "2",
      "Description": "<NAME> test status",
      "InventoryAtpCode": "2",
      "AvailabilityType": "2",
      "ReservableType": "2",
      "StatusAssigned": "0"
    }
  ],
  "INV_INVENTORY_STATUS_TRANSLATION.csv": [
    {
      "INV_INVENTORY_STATUS.StatusCode": "<NAME>",
      "StatusCode": "<NAME>",
      "Description": "<NAME> test status",
      "Language": "US",
      "SourceLang": "US"
    }
  ],
  "INV_INVENTORY_STATUS_TRANSACTION_CONTROL.csv": "<one row per status-controlled transaction type, built as shown below>"
}
```
Write the file with the status and translation rows first; the third CSV's rows are added by the snippet further down (it replaces the placeholder text).

The flag values follow the export (VERIFIED: copied from a working status): 1 = yes/enabled, 2 = no, and StatusAssigned 0 for a new status. Change them only to values you see on existing rows.

**Transaction control rows: use only transaction types with material status control enabled.** A row for a type whose MaterialStatusEnabled is `N` makes the whole status fail with `INV_INT_TRXTYPCODE ... You must provide a value for the TransactionTypeId attribute` (VERIFIED: try 1 failed on the type Cycle Count Transfer). Read the allowed types live and add the rows to rows.json:
```bash
python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py \
  "/fscmRestApi/resources/11.13.18.05/inventoryTransactionTypes?q=MaterialStatusEnabled='Y'&fields=TransactionTypeName&limit=500" \
  --token-cache auto --no-open-browser --output "<RUN_DIR>/status_types.json"
python3 -c "import json,sys; r=json.load(open(sys.argv[1])); t=json.load(open(sys.argv[2])); r['INV_INVENTORY_STATUS_TRANSACTION_CONTROL.csv']=[{'INV_INVENTORY_STATUS.StatusCode':sys.argv[3],'TransactionTypeName':i['TransactionTypeName'],'IsAllowed':'1'} for i in t['items']]; json.dump(r,open(sys.argv[1],'w'),indent=1)" "<RUN_DIR>/rows.json" "<RUN_DIR>/status_types.json" <NAME>
```
`IsAllowed` is `1` for allowed and `2` for not allowed (VERIFIED from existing rows). Send one row for every type the query returns. (VERIFIED: in the own test one type was left out by mistake and Oracle added it as allowed, so a missing row does no harm.)

Build the import package (it keeps every CSV header and only your rows):
```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export "<RUN_DIR>/export_before/<export zip>" \
  --rows "<RUN_DIR>/rows.json" --prefix <PREFIX> --out "<RUN_DIR>/load.zip"
```
Never import the full export: an FSM import merges by key and would re-send every existing record.

## Step 3: Import
```bash
python3 shared/setup-import/task-level-import/scripts/import_setup_task_csv.py \
  --task-code INV_MANAGE_MATERIAL_STATUSES --zip-file "<RUN_DIR>/load.zip" --wait-seconds 400 \
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
3. Read it back by REST as well (VERIFIED, resource exists):
   ```bash
   python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py \
     "/fscmRestApi/resources/11.13.18.05/inventoryMaterialStatuses?q=MaterialStatusName='<NAME>'" --token-cache auto --no-open-browser \
     --output "<RUN_DIR>/rest_readback.json"
   ```
   `count` must be 1.

## Rules and limits
- StatusCode is the key and must be unique (a 15-character code was VERIFIED; maximum not known, GUESS: 80).
- The import log names only the status row when a control row is wrong; check the message text (INV_INT_TRXTYPCODE).
- A REST resource exists: `inventoryMaterialStatuses` (VERIFIED: GET by MaterialStatusName returns the status; REST calls the code MaterialStatusName).
- New records only. Never edit, re-send or delete an existing record.
- Never print or save sign-in values, tokens, server addresses or user names.

## Worked example (VERIFIED; counts will differ in your run)
Record FSCRT_HF_GF_MS1. Export before: 51 statuses, 1445 control rows. Try 1 (ProcessId 100004744436442) failed: INV_INT_TRXTYPCODE (a control row for a type that is not status-controlled), nothing created. Try 2 (ProcessId 100004744435347) succeeded with 40 control rows. Export after: 52 statuses, 41 control rows for the new status, existing changed 0.
