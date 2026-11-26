# Manage Pricing Matrix Types (ORA_QP_MANAGE_PRICING_MATRIX_TYPES) - create a new inactive matrix type by FSM CSV

## What it is and when to use
Pricing setup task **Manage Pricing Matrix Types**. A matrix type belongs to a dynamic matrix class (for example
Channel Program Eligibility, Pricing Segment) and defines the kind of pricing matrix (decision table) that pricing
algorithms and channel programs use. Use this skill to add a **new, inactive matrix type** through FSCR's task-level
CSV import. It never changes a seeded or existing matrix type.

Route: FSM CSV for the load; REST `pricingMatrixTypes` (VERIFIED, read only here) for checks and read-back.

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | run folder outside any git repo and outside shared folders | |
| `<PREFIX>` | test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<CODE>` | new MatrixTypeCode, e.g. `<PREFIX>MT1` | 15 chars VERIFIED |
| `<NAME>` | Name, e.g. `<CODE> test matrix type` | |
| `<CLASS>` | matrix class **name**, e.g. `Channel Program Eligibility` | read live (prerequisite 1) |

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
1. Read the matrix classes in use live and pick `<CLASS>` by name:
   `python3 gaps-filled/common-features/scripts/rest_read.py /fscmRestApi/resources/11.13.18.05/pricingMatrixTypes --limit 100 --fields MatrixTypeCode,MatrixClassName,Active`
   Pick the class your matrices will belong to; for a plain test record use the class of the existing custom rows
   (VERIFIED: Channel Program Eligibility). Do not copy a class id from an export: give only the class **name** (VERIFIED: Oracle resolves the id from
   `DynamicMatrixClassName`).

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_QP_MANAGE_PRICING_MATRIX_TYPES <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 3
```
One CSV, `ORA_QP_PRICING_MATRIX_TYPE.csv` (VERIFIED). It holds only part of the types REST lists (seeded types
are mostly left out, VERIFIED: 4 rows in the export, 18 by REST), so it is not incomplete. Columns: MatrixTypeCode, Name, Description, DynamicMatrixClassId,
MultipleMatricesFlag, ActiveFlag, SeededFlag, DynamicMatrixClassName, DynamicMatrixClassId1, MatrixClassGuid,
OwnerApplication, ModuleId. Check `<CODE>` is not already there.

## Build rows
```json
{"ORA_QP_PRICING_MATRIX_TYPE.csv": [{"MatrixTypeCode": "<CODE>", "Name": "<NAME>", "Description": "test record",
  "DynamicMatrixClassName": "<CLASS>", "MultipleMatricesFlag": "Y", "ActiveFlag": "N", "SeededFlag": "N",
  "OwnerApplication": "pricing"}]}
```
- Leave DynamicMatrixClassId, DynamicMatrixClassId1, MatrixClassGuid, ModuleId, CreatedBy, LastUpdatedBy empty
  (VERIFIED: Oracle filled the class id from the name).
- `ActiveFlag` `N` keeps the type out of use; `OwnerApplication` `pricing` as in the existing custom rows (VERIFIED).
```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json \
  --prefix <PREFIX> --out <RUN>/<CODE>.zip
```
Never import the full export.

## Import
```bash
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> ORA_QP_MANAGE_PRICING_MATRIX_TYPES <RUN>/<CODE>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Keep the ProcessId. Success (VERIFIED): business object "Pricing Matrix Logic Flow", detail `MatrixType` "1 rows were
processed. 0 rows of them failed". If the connection drops, never import again; wait 2 minutes and check.

## Read back
```bash
python3 gaps-filled/common-features/scripts/rest_read.py /fscmRestApi/resources/11.13.18.05/pricingMatrixTypes \
  --q "MatrixTypeCode='<CODE>'" --fields MatrixTypeCode,Name,MatrixClassName,Active
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_QP_MANAGE_PRICING_MATRIX_TYPES <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
Pass: REST returns 1 item with MatrixClassName `<CLASS>` and Active `N`; compare shows 1 row added and
`existing changed or missing 0`.

## Rules and limits
- New records only; never change a seeded (SeededFlag Y) or existing matrix type.
- Never print tokens, server addresses or user names; keep exports and logs in `<RUN>`.

## Worked example (VERIFIED live)
`FSCRT_AK_GF_MT1`, class Channel Program Eligibility, inactive: export ProcessId 100004743456213, import ProcessId
100004744422848 (1 row, 0 failed), after-export ProcessId 100004744431234: 1 new row, 0 existing changed; REST GET
returned it with the class resolved.
