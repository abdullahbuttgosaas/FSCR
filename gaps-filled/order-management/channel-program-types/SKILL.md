# Manage Channel Program Types (ORA_CJM_MANAGE_PROGRAM_TYPES) - create a new draft program type by FSM CSV

## What it is and when to use
Channel Revenue Management setup task **Manage Channel Program Types**. A program type is built on a program
template (for example Supplier Rebate) and gives defaults (currency, discount type, qualifiers) to the channel
programs created from it. Use this skill to add a **new program type in Draft status** with its qualifiers through
FSCR's task-level CSV import. It never changes an existing program type.

Route: FSM CSV for the load; REST `channelProgramTypes` (VERIFIED, read only here) for the read-back.

## Placeholders
| Placeholder | Meaning | Rule |
|---|---|---|
| `<FSCR>` | FSCR repository root (run every command from here) | |
| `<RUN>` | run folder outside any git repo and outside shared folders | |
| `<PREFIX>` | test prefix, e.g. `FSCRT_XX_GF_` | upper case |
| `<CODE>` | new ProgramTypeCode, e.g. `<PREFIX>PT1` | 15 chars VERIFIED |
| `<NAME>` | ProgramTypeName, e.g. `<CODE> test program type` | |
| `<PFX3>` | ProgramCodePrefix for programs created from this type | 3 letters VERIFIED; pick one no other row in the export uses (uniqueness rule not tested) |
| `<CUR>` | default currency code, e.g. USD | must be an enabled currency |

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
1. A program template must exist (seeded, e.g. `SUPPLIER_REBATE`). The export column ProgramTemplateCode shows the
   templates in use; when the export is empty, read them by REST:
   `python3 gaps-filled/common-features/scripts/rest_read.py /fscmRestApi/resources/11.13.18.05/channelProgramTypes --fields ProgramTypeCode,ProgramTemplateCode,ProgramTemplate,StatusCode`
   If the export has no row at all, see "Rows written in full" below.

## Export (read only)
```bash
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_CJM_MANAGE_PROGRAM_TYPES <RUN>/before
python3 gaps-filled/common-features/scripts/inspect_export.py <RUN>/before/*.zip --samples 2
```
CSVs (VERIFIED): `ORA_CJM_PROGRAM_TYPE.csv` (52 columns) and `ORA_CJM_PROGRAM_TYPE_QUALIFIER.csv`
(`ORA_CJM_PROGRAM_TYPE.ProgramTypeCode`, QualifierTypeCode, DefaultQualifierFlag, SeededFlag, DateQualifierFlag).
Check `<CODE>` is not already there.

## Build rows (template-row method)
Pick one existing **Draft** program type row of the template you want as a model; prefer a row created by an
earlier test with your prefix, and check its DefaultCurrencyCode (a model with another currency carries it over). Copy all its non-empty columns
except CreatedBy/LastUpdatedBy, then set ProgramTypeCode `<CODE>`, ProgramTypeName `<NAME>`, ProgramCodePrefix
`<PFX3>` (and DefaultCurrencyCode/DefaultCurrency if you want another currency). Copy the model's qualifier rows,
changing only `ORA_CJM_PROGRAM_TYPE.ProgramTypeCode` to `<CODE>`. A small script (save it as `<RUN>/make_rows.py`, replace the four `<...>` values in the first lines, run it with
`python3 <RUN>/make_rows.py <RUN>`):
```python
import csv, io, json, zipfile, glob, sys
RUN = sys.argv[1]
z = zipfile.ZipFile(glob.glob(RUN + "/before/*.zip")[0])
rd = lambda n: list(csv.DictReader(io.StringIO(z.read(n).decode("utf-8-sig"))))
model = "<an existing Draft ProgramTypeCode>"
skip = ("CreatedBy", "LastUpdatedBy")
pt = [r for r in rd("ORA_CJM_PROGRAM_TYPE.csv") if r["ProgramTypeCode"] == model][0]
new = {k: v for k, v in pt.items() if v and k not in skip}
new.update(ProgramTypeCode="<CODE>", ProgramTypeName="<NAME>", ProgramCodePrefix="<PFX3>")
q = [{**{k: v for k, v in r.items() if v and k not in skip}, "ORA_CJM_PROGRAM_TYPE.ProgramTypeCode": "<CODE>"}
     for r in rd("ORA_CJM_PROGRAM_TYPE_QUALIFIER.csv") if r["ORA_CJM_PROGRAM_TYPE.ProgramTypeCode"] == model]
json.dump({"ORA_CJM_PROGRAM_TYPE.csv": [new], "ORA_CJM_PROGRAM_TYPE_QUALIFIER.csv": q}, open(RUN + "/rows.json", "w"), indent=1)
```
VERIFIED columns that were enough (Supplier Rebate model): ProgramTemplateCode `SUPPLIER_REBATE`, ProgramTemplate,
CustomerProgramFlag `N`, Status `Draft`, StatusCode `DRAFT`, DefaultCurrencyCode/DefaultCurrency, EnableApprovalFlag
`N`, DefaultDiscountTypeCode `DISCOUNT_AMOUNT`/DefaultDiscountType, PriceTypeCode `ONE_TIME`,
DefaultApplyManuallyToOrderFlag `N`, DefaultOverrideProgramFlag `N`, AccrualPercentBasisOnImportedTrxCode
`ORA_UNIT_LIST_PRICE` (+ meaning); qualifiers `PO_DATE` (DateQualifierFlag Y) and `ORA_SHIP_TO_LOCATION`.

**Rows written in full** (empty export): use the column list above; read code values live by REST from
`channelProgramTypes` in another environment or Oracle's docs, and let Oracle's errors (JBO-27014 "... is required")
name any missing column (GUESS: not needed live).

```bash
python3 gaps-filled/common-features/scripts/build_fsm_package.py --export <RUN>/before/*.zip --rows <RUN>/rows.json \
  --prefix <PREFIX> --out <RUN>/<CODE>.zip
```
The builder refuses a row without `<PREFIX>`; qualifier rows pass because their parent column holds `<CODE>`.

## Import
```bash
bash gaps-filled/common-features/scripts/import_task.sh <FSCR> ORA_CJM_MANAGE_PROGRAM_TYPES <RUN>/<CODE>.zip <RUN>/import
python3 gaps-filled/common-features/scripts/read_import_log.py <RUN>/import
```
Keep the ProcessId. Success (VERIFIED): business object "Channel Program Type", detail `ProgramTypeVO` "A total of 1 rows
were processed. 0 rows of them failed and 0 rows completed with warnings"; the child "Channel Program Type
Qualifier" says "This object was already processed" (normal). If the connection drops, never import again; wait 2 minutes and check.

## Read back
```bash
python3 gaps-filled/common-features/scripts/rest_read.py /fscmRestApi/resources/11.13.18.05/channelProgramTypes \
  --q "ProgramTypeCode='<CODE>'" --fields ProgramTypeCode,ProgramTypeName,ProgramTemplateCode,StatusCode,DefaultCurrencyCode
bash gaps-filled/common-features/scripts/export_task.sh <FSCR> ORA_CJM_MANAGE_PROGRAM_TYPES <RUN>/after
python3 gaps-filled/common-features/scripts/compare_fsm_exports.py <RUN>/before/*.zip <RUN>/after/*.zip --prefix <PREFIX>
```
Pass: REST returns 1 item with StatusCode DRAFT; the compare shows 1 program type row + the qualifier rows added and
`existing changed or missing 0`.

## Rules and limits
- New records only; keep the new type in Draft (do not activate it; GUESS that activation is a screen action).
- Never print tokens, server addresses or user names; keep exports and logs in `<RUN>`.

## Worked example (VERIFIED live)
`FSCRT_AK_GF_PT1` (Supplier Rebate, Draft, USD, prefix FAK): export ProcessId 100004744431194, import ProcessId
100004744432477 (1 row, 0 failed), after-export ProcessId 100004744432496: 3 new rows (type + 2 qualifiers),
0 existing changed; REST GET returned the record.
