# Manage Status Values (DOO_MANAGE_STATUS_VALUES) - create a new orchestration status code by FSM CSV

## What it is and when to use
Order Management (Orders) setup task **Manage Status Values**. It holds the status codes that orchestration
processes, fulfillment lines and task types use (code, display name, translations), plus process classes and the
status lists per task type. Use this skill to add a **new status code** (and its translation) through FSCR's
task-level CSV import. It never changes an existing status, process class or task-type status list.

Route: FSM CSV (setupTaskCSVExports / setupTaskCSVImports). No public REST resource for status codes (VERIFIED: GET
`orchestrationStatusValues` returns 404); the read-back is a second export.

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | a run folder outside any git repo and outside shared folders (exports hold user names) | |
| `<PREFIX>` | your test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<CODE>` | new status code, e.g. `<PREFIX>ST1` | upper case, letters/digits/underscore; 15 chars VERIFIED to work |
| `<NAME>` | display name, e.g. `<CODE> test status` | |

## Notes for every run (VERIFIED in fresh tests)
- Use a new, empty `<RUN>` and separate empty `before/` and `after/` folders: the compare step expects exactly one
  ZIP in each. FSCR names its output files after the environment, so never list, print or share the file names in
  `<RUN>` or the raw logs; quote only ProcessIds, codes and counts.
- If a sign-in is still valid (token cache), do not sign in again; sign in only on 401/403.
- Check a code is free: `python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --find <CODE>`
  must print 0 rows for every CSV.
- `import_task.sh` prints interim lines such as "StatusCode: (unknown)" or "(no result yet)": ignore them. Judge the
  import only by `read_import_log.py`: the final "Status: Completed successfully" line and "Total Objects Failed: 0".
  An "In progress" line before it, other detail objects with "0 rows were processed", and child business objects
  marked "This object was already processed" are normal.
- Code length: the codes in the worked examples are 15 characters and work; longer codes were not tested (GUESS:
  the column allows more). With a 12-character prefix such as `FSCRT_XX_GF_`, keep the suffix to 3 characters.

## Sign-in
`python3 core/auth/fusion-oauth-authentication/scripts/fusion_login.py --token-cache auto --open-browser`
(the person signs in in the browser; never type or print a password or token). A sign-in lasts about an hour; on
401/403 sign in again. All later commands use `--token-cache auto`.

## Prerequisites
1. None. A status code is stand-alone (VERIFIED). To use it in an orchestration process or a task type later, add
   it there with the tasks Manage Task Status Conditions / Manage Orchestration Process Definitions (other skills).

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> DOO_MANAGE_STATUS_VALUES <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 2
```
The package holds 7 CSVs (VERIFIED): `DOO_STATUS_CODES_DEF.csv` (codes), `ORA_DOO_TRANS_ORCH_STATUS_CODE.csv`
(translations), `ORA_DOO_LINE_STATUS.csv`, `ORA_DOO_PROCESS_CLASS_SETUP.csv`, `ORA_DOO_PROCESS_CLASS_STATUS.csv`,
`ORA_DOO_TRANS_ORCH_PROC_CLASS_SETUP.csv`, `ORA_DOO_PROCESS_TASK_STATUS.csv`. Check `<CODE>` is not already in
`DOO_STATUS_CODES_DEF.csv`; if it is, pick another code (never re-load an existing one).

## Build rows
Write `<RUN>/rows.json` with only the new code and its US translation:
```json
{
 "DOO_STATUS_CODES_DEF.csv": [
  {"StatusCode": "<CODE>", "OrchestrationApplicationCode": "DOO", "DisplayName": "<NAME>"}],
 "ORA_DOO_TRANS_ORCH_STATUS_CODE.csv": [
  {"DOO_STATUS_CODES_DEF.StatusCode": "<CODE>", "DOO_STATUS_CODES_DEF.OrchestrationApplicationCode": "DOO",
   "Language": "US", "DisplayName": "<NAME>", "SourceLang": "US"}]
}
```
- `OrchestrationApplicationCode` is `DOO` (VERIFIED: every row in the export uses it).
- Leave CreatedBy / LastUpdatedBy empty (VERIFIED: Oracle fills them).
- If the environment's base language is not US, use the `Language`/`SourceLang` value the existing translation rows
  use (GUESS: not seen live).

Build the package (keeps every other CSV header-only, refuses rows without `<PREFIX>`):
```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json \
  --prefix <PREFIX> --out <RUN>/<CODE>.zip
```
Never import the full export: the import merges by key and would re-send every existing record.

## Import
```bash
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> DOO_MANAGE_STATUS_VALUES <RUN>/<CODE>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Keep the **ProcessId** (the only key to the full process log). Success (VERIFIED): business object "Orchestration
Status Code", detail object `StatusSetupVO`: "A total of 1 rows were processed. 0 rows of them failed".
If the connection drops after the import started, do not import again: wait 2 minutes and export to check.

## Read back
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> DOO_MANAGE_STATUS_VALUES <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
Pass when it shows `+ DOO_STATUS_CODES_DEF.csv: <CODE>` and `+ ORA_DOO_TRANS_ORCH_STATUS_CODE.csv: <CODE>` and
`existing changed or missing 0`.

## Rules and limits
- New records only; never edit or delete an existing status code, process class or task-type status row.
- The import log counts only the top object (1 row); the translation row is proven by the after-export.
- Never print tokens, server addresses or user names; exports and logs hold user names, keep them in `<RUN>`.

## Worked example (VERIFIED live)
Code `FSCRT_AK_GF_ST1`: export ProcessId 100004744432201, import ProcessId 100004743455333 (1 row processed, 0 failed),
after-export ProcessId 100004744422896: 2 new rows (code + US translation), 0 existing changed.
