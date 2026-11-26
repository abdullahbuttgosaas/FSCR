# Manage Task Types (DOO_MANAGE_TASK_TYPES) - create a new custom orchestration task type by FSM CSV

## What it is and when to use
Order Management (Orders) setup task **Manage Task Types**. A task type groups the services (create, inbound,
cancel, ...) that orchestration process steps call. Use this skill to add a **new custom task type** with its
services and translations through FSCR's task-level CSV import. It never changes a seeded or existing task type.

Route: FSM CSV. No public REST resource used; the read-back is a second export.

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | run folder outside any git repo and outside shared folders (exports hold user names) | |
| `<PREFIX>` | your test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<TT>` | new task type code, e.g. `<PREFIX>TT1` | 15 chars VERIFIED to work; keep it short (service names add 7-8 chars) |

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
(the person signs in in the browser; never type or print a password or token). On 401/403 sign in again.

## Prerequisites
1. None. A custom task type is stand-alone (VERIFIED). Status values for it (Manage Task Status Conditions) and its
   use in an orchestration process are separate tasks.

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> DOO_MANAGE_TASK_TYPES <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 2
```
CSVs (VERIFIED): `DOO_TASK.csv` (task type), `ORA_DOO_TRANS_ORCH_TASK.csv` (its translation),
`ORA_DOO_TASK_TYPE_SERVICE_DEF.csv` (services), `ORA_DOO_TRANS_ORCH_SERVICE_DEF.csv` (service translations),
`ORA_DOO_TASK_TYPE_DEF_SETUP.csv` / `ORA_DOO_TRANS_ORCH_TASK_DEF.csv` (seeded task definitions), `ORA_DOO_ACTIVITY.csv`
and `ORA_DOO_TRANS_ACTIVITY.csv` (activities). Check `<TT>` is not already in `DOO_TASK.csv`.

## Build rows
Allowed `OperationCode` values: list them from the export with
`python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --csv ORA_DOO_TASK_TYPE_SERVICE_DEF --samples 100`
(VERIFIED values on custom rows: APPLY_HOLD, CANCEL, CREATE, GET_STATUS, INBOUND, RELEASE_HOLD, UPDATE, WAIT;
`CREATE` and `INBOUND` are the two this skill loads). Write `<RUN>/rows.json`:
```json
{
 "DOO_TASK.csv": [{"TaskType": "<TT>", "OrchestrationApplicationCode": "DOO", "TaskSubTypeCode": "GENERIC", "SeededFlag": "N"}],
 "ORA_DOO_TRANS_ORCH_TASK.csv": [{"DOO_TASK.TaskType": "<TT>", "DOO_TASK.OrchestrationApplicationCode": "DOO",
   "Language": "US", "Description": "<TT> test task type", "SourceLang": "US"}],
 "ORA_DOO_TASK_TYPE_SERVICE_DEF.csv": [
  {"DOO_TASK.TaskType": "<TT>", "DOO_TASK.OrchestrationApplicationCode": "DOO", "ServiceName": "<TT> Create",
   "OrchestrationApplicationCode": "DOO", "CheckHolds": "Y", "OperationCode": "CREATE", "SystemFlag": "N", "ServiceCode": "<TT> Create"},
  {"DOO_TASK.TaskType": "<TT>", "DOO_TASK.OrchestrationApplicationCode": "DOO", "ServiceName": "<TT> Inbound",
   "OrchestrationApplicationCode": "DOO", "CheckHolds": "N", "OperationCode": "INBOUND", "SystemFlag": "N", "ServiceCode": "<TT> Inbound"}],
 "ORA_DOO_TRANS_ORCH_SERVICE_DEF.csv": [
  {"DOO_TASK.TaskType": "<TT>", "DOO_TASK.OrchestrationApplicationCode": "DOO", "ORA_DOO_TASK_TYPE_SERVICE_DEF.ServiceName": "<TT> Create",
   "ORA_DOO_TASK_TYPE_SERVICE_DEF.OrchestrationApplicationCode": "DOO", "Language": "US", "ServiceName": "<TT> Create", "SourceLang": "US"},
  {"DOO_TASK.TaskType": "<TT>", "DOO_TASK.OrchestrationApplicationCode": "DOO", "ORA_DOO_TASK_TYPE_SERVICE_DEF.ServiceName": "<TT> Inbound",
   "ORA_DOO_TASK_TYPE_SERVICE_DEF.OrchestrationApplicationCode": "DOO", "Language": "US", "ServiceName": "<TT> Inbound", "SourceLang": "US"}]
}
```
- `TaskSubTypeCode` `GENERIC` is the custom sub-type (VERIFIED). A custom task type needs at least the create and
  inbound services (Oracle docs, GUESS that the import enforces it).
- Leave CreatedBy / LastUpdatedBy empty (VERIFIED).

```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json \
  --prefix <PREFIX> --out <RUN>/<TT>.zip
```
Never import the full export.

## Import
```bash
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> DOO_MANAGE_TASK_TYPES <RUN>/<TT>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Keep the ProcessId. Success (VERIFIED): business object "Orchestration Task", detail `TaskTypeSetupVO` "1 rows were
processed. 0 rows of them failed". `OrchestrationActivityDefinitionSetupVO` with 0 rows is normal. Services and
translations are not counted in the log.
If the connection drops after the import started, never import again; wait 2 minutes and export to check.

## Read back
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> DOO_MANAGE_TASK_TYPES <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
Pass: 6 new rows (1 `DOO_TASK`, 1 task translation, 2 services, 2 service translations) and `existing changed or missing 0`.

## Rules and limits
- New records only; never change a seeded task type (SeededFlag Y) or another person's task type.
- Never print tokens, server addresses or user names; keep exports and logs in `<RUN>`.

## Worked example (VERIFIED live)
Task type `FSCRT_AK_GF_TT1` with services `... Create` and `... Inbound`: export ProcessId 100004744422798, import
ProcessId 100004743456286 (1 row, 0 failed), after-export ProcessId 100004743455410: 6 new rows, 0 existing changed.
