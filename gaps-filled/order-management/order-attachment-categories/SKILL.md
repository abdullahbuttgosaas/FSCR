# Manage Order Attachment Categories (DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES) - create a new category for orders by FSM CSV

## What it is and when to use
Order Management (Orders) setup task **Manage Order Attachment Categories**. An attachment category (for example
"Internal note") is made available on an order entity so users can classify attachments. Use this skill to create
a **new category and map it to the order header entity** through FSCR's task-level CSV import. It never changes an
existing category or mapping. Route: FSM CSV; read back with a second export.

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | run folder outside any git repo and outside shared folders (exports hold user names) | |
| `<PREFIX>` | your test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<CODE>` | new CategoryName, e.g. `<PREFIX>AC1` | 15 chars VERIFIED |
| `<NAME>` | display name of the category (column `UserName`: the category's name, **not** a person) | holds the prefix |
| `<MODULE>` | ModuleId of an Order Management (DOO) module | read live (prerequisite 1) |

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
1. Read the DOO ModuleId live by REST from a DOO lookup type:
   `python3 gaps-filled/common-features/scripts/rest_read.py /fscmRestApi/resources/11.13.18.05/standardLookups --q "LookupType='ORA_DOO_INVOCATION_MODE'" --fields ModuleId`
   VERIFIED: without ModuleId the category is created but belongs to no module, so the task export (scoped to
   module DOO) never shows it.

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 3
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --find <CODE>
```
CSVs (VERIFIED): `FND_APP_ATTACHMENT_CATEGORY.csv` (CategoryName, ApplicationId, Description, ModuleId, UserName,
audit columns) and `ORA_FND_APP_ATTACHMENT_CATEGORY.csv` (CategoryName, EntityName, ModuleId, audit columns). The
export can be empty (VERIFIED: 0 rows).

## Build rows (written in full)
```json
{"FND_APP_ATTACHMENT_CATEGORY.csv": [{"CategoryName": "<CODE>", "Description": "test attachment category",
   "UserName": "<NAME>", "ModuleId": "<MODULE>"}],
 "ORA_FND_APP_ATTACHMENT_CATEGORY.csv": [{"CategoryName": "<CODE>", "EntityName": "DOO_HEADERS_ALL", "ModuleId": "<MODULE>"}]}
```
- `UserName` is required (VERIFIED: JBO-27014 "Attribute UserName in FndDocumentCategoriesTlEO is required" without it).
- EntityName `DOO_HEADERS_ALL` (order header) is VERIFIED; other order entities (for example lines) are GUESS.
- Leave ApplicationId and the audit columns empty (VERIFIED).

## Import
```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json --prefix <PREFIX> --out <RUN>/<CODE>.zip
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES <RUN>/<CODE>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Never import the full export (the import merges by key and would re-send existing records). Keep the ProcessId.
Success (VERIFIED): business object "Application Attachment Category", detail objects `FndDocumentCategoriesVLSD.xml` and `FndDocCategoriesToEntitiesVLSD.xml` each "A total of 1 rows were processed. 0 rows of them failed". If the connection drops after the import started, never import again: wait 2 minutes and
export to check.

## Read back
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
Pass: `+ FND_APP_ATTACHMENT_CATEGORY.csv: <CODE>` and `+ ORA_FND_APP_ATTACHMENT_CATEGORY.csv: <CODE>`, and
`existing changed or missing 0`.

## Rules and limits
- New records only; never edit or delete an existing record.
- Never print tokens, server addresses, environment names or user names; keep exports and logs in `<RUN>`.
- If a category was created without ModuleId (not in the export), do not re-send the same name; use a new `<CODE>`.

## Worked example (VERIFIED live)
`FSCRT_AK_GF_AC2` on DOO_HEADERS_ALL: export ProcessId 100004744432568; try 1 (no UserName) refused, ProcessId
100004744436010; try 2 (no ModuleId) loaded `FSCRT_AK_GF_AC1` outside the module, ProcessId 100004744435085; try 3
with ModuleId, ProcessId 100004744435115 (2 rows, 0 failed); after-export ProcessId 100004744434550: 2 new rows,
0 existing changed.
