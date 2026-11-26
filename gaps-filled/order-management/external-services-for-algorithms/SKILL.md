# Manage External Service Details for Algorithms (ORA_QP_MANAGE_EXT_SERVICES_FOR_ALGORITHMS) - register a new service by FSM CSV

## What it is and when to use
Pricing setup task **Manage External Service Details for Algorithms**. It registers a named external web service
that a pricing algorithm step can call. Use this skill to add a **new service definition** through FSCR's
task-level CSV import. It never changes an existing connector or source system.
Route: FSM CSV for the load; REST `omWebServiceDefinitions` (VERIFIED, read only) for the read-back.
The CSV has **no URL or credential columns** (VERIFIED); the service URL and sign-in details are entered on the
setup page afterwards (GUESS: not done live; never put credentials in a CSV).

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | run folder outside any git repo and outside shared folders (exports hold user names) | |
| `<PREFIX>` | your test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<CODE>` | new ServiceName, e.g. `<PREFIX>WS1` | 15 chars VERIFIED |
| `<SYSNAME>` | name (not code) of a source system | read live (prerequisite 1) |

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
1. A source system to act as the target system, given by its **name**. Read it read-only from the export of task
   DOO_ORCHESTRATION_MANAGE_SOURCE_SYSTEMS:
   ```bash
   bash gaps-filled/common-features/scripts/export_task.sh <FSCR> DOO_ORCHESTRATION_MANAGE_SOURCE_SYSTEMS <RUN>/systems
   python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/systems/*.zip --csv ORA_MSC_APPS_INSTANCE --samples 20
   ```
   Use the `InstanceName` of the row with `InstanceCode` OPS (VERIFIED: "Oracle Fusion Order Orchestration And
   Planning"). The system is only referenced, not changed. VERIFIED: the code `OPS` is refused (JBO-25072 "LOV_OrigSystemName
   ... no matching row") and an empty value is refused (JBO-27014 "TargetSystemId ... is required").
2. The invocation mode code, read live:
   `python3 gaps-filled/common-features/scripts/rest_read.py /fscmRestApi/resources/11.13.18.05/standardLookups/ORA_DOO_INVOCATION_MODE/child/lookupCodes --fields LookupCode,Meaning`
   (VERIFIED: ORA_SYNC, ORA_ASYNC, ORA_EVENT) and the response option:
   `.../standardLookups/ORA_DOO_RESPONSE_PROCESS_OPTNS/child/lookupCodes` (VERIFIED: ANY, EXTERNAL, GROUP).

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_QP_MANAGE_EXT_SERVICES_FOR_ALGORITHMS <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 3
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --find <CODE>
```
One CSV, `DOO_WEB_SERVICE_DETAILS.csv` (VERIFIED): OrchestrationApplicationCode, ServiceName, CreatedBy,
LastUpdatedBy, Description, OrigSystemName, ResponseProcessPartialMode, SendAttachmentsFlag, InvocationMode. The
export can be empty (VERIFIED: 0 rows); it holds only pricing services, not Order Management connectors.

## Build rows (written in full)
```json
{"DOO_WEB_SERVICE_DETAILS.csv": [{"OrchestrationApplicationCode": "QP", "ServiceName": "<CODE>",
  "Description": "test service", "OrigSystemName": "<SYSNAME>", "InvocationMode": "ORA_SYNC",
  "ResponseProcessPartialMode": "ANY", "SendAttachmentsFlag": "N"}]}
```
`OrchestrationApplicationCode` `QP` (pricing) is VERIFIED; it scopes the row to this task.

## Import
```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json --prefix <PREFIX> --out <RUN>/<CODE>.zip
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> ORA_QP_MANAGE_EXT_SERVICES_FOR_ALGORITHMS <RUN>/<CODE>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Never import the full export (the import merges by key and would re-send existing records). Keep the ProcessId.
Success (VERIFIED): business object "Orchestration Web Service", detail `WebServiceDetailsMigrationVO` "A total of 1 rows were processed. 0 rows of them failed". If the connection drops after the import started, never import again: wait 2 minutes and
export to check.

## Read back
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_QP_MANAGE_EXT_SERVICES_FOR_ALGORITHMS <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
and REST:
```bash
python3 gaps-filled/common-features/scripts/rest_read.py /fscmRestApi/resources/11.13.18.05/omWebServiceDefinitions --q "ServiceName='<CODE>'" --fields ServiceName,InvocationMode,ResponseProcessPartialMode
```
Pass: the compare shows `+ DOO_WEB_SERVICE_DETAILS.csv: <CODE>` and `existing changed or missing 0`; REST returns 1
item (VERIFIED: InvocationMode "Synchronous service").

## Rules and limits
- New records only; never edit or delete an existing record.
- Never print tokens, server addresses, environment names or user names; keep exports and logs in `<RUN>`.

## Worked example (VERIFIED live)
`FSCRT_AK_GF_WS1`: export ProcessId 100004744422916; try 1 (no OrigSystemName) refused, ProcessId 100004743456587;
try 2 (code OPS) refused, ProcessId 100004744433377; try 3 (system name) loaded, ProcessId 100004744434324 (1 row,
0 failed); after-export ProcessId 100004744433467: 1 new row, 0 existing changed; REST GET returned it.
