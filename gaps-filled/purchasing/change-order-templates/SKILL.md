# Manage Change Order Templates (PO_MANAGE_CHANGE_ORDER_TEMPLATES): create a change order template by FSM CSV

## What it is and when to use
A change order template lists which purchasing document attributes (header, lines, schedules, attachments, contract
terms) a buyer or supplier may change in a change order, and whether the change is sent to the supplier. Use this
skill to create a NEW template through FSCR's setup task CSV import. FSCR has no skill for this task.
Route: FSM setup CSV (task `PO_MANAGE_CHANGE_ORDER_TEMPLATES`, CSV supported: Y). VERIFIED.
No REST resource (`changeOrderTemplatesLOV` describe: not found). VERIFIED.

## Placeholders
See `../purchasing-common/COMMON_STEPS.md` (`<RUN>`, `<PREFIX>`, `$S`). Plus:
- `<CODE>`: new template code and name, `<PREFIX>` + short name, upper case, e.g. `FSCRT_AB_GF_CO1`.
- `<SOURCE_TEMPLATE>`: the code of an existing template in the before-export whose attribute list you copy.

## Sign-in
As in COMMON_STEPS.md.

## Prerequisites
1. A source template in the before-export (any template with attribute rows). Its rows are only READ and copied
   under your new code; the source is never changed. VERIFIED.
   ```bash
   python3 - <<'EOF'
   import zipfile, csv, io, glob, collections
   z = zipfile.ZipFile(glob.glob("<RUN>/before/*.zip")[0])
   rows = list(csv.DictReader(io.StringIO(z.read("PO_CHANGE_ORDER_TEMPLATE_ATTR_VALUE.csv").decode("utf-8-sig"))))
   print(collections.Counter(r["PO_CHANGE_ORDER_TEMPLATE.CoTemplateCode"] for r in rows))
   EOF
   ```
   Pick one code with attribute rows as `<SOURCE_TEMPLATE>`; prefer a template that is not a test record (no
   `FSCRT_` prefix), because its attribute list is the customer's real choice. Any listed code works for the copy
   (VERIFIED with both kinds); it is only read. If the export has no template with attribute rows,
   stop: the attribute list then has to be written in full from Oracle's documentation (not covered; GUESS).

## Export
COMMON_STEPS step 1 with `<TASK_CODE>` = `PO_MANAGE_CHANGE_ORDER_TEMPLATES`. Three CSVs:
`PO_CHANGE_ORDER_TEMPLATE.csv` (header), `PO_CHANGE_ORDER_TEMPLATE_TRANSLATION.csv` (name per language) and
`PO_CHANGE_ORDER_TEMPLATE_ATTR_VALUE.csv` (one row per attribute, about 130 per template, linked by
`PO_CHANGE_ORDER_TEMPLATE.CoTemplateCode`). User-created templates are exported; seeded ones were not seen. VERIFIED.

## Build rows
Write `<RUN>/rows.json` with this script (header + translation + a copy of the source's attribute rows under
`<CODE>`; who/date columns are left empty):
```bash
python3 - <<'EOF'
import zipfile, csv, io, glob, json
run, code, src = "<RUN>", "<CODE>", "<SOURCE_TEMPLATE>"
z = zipfile.ZipFile(glob.glob(run + "/before/*.zip")[0])
attrs = list(csv.DictReader(io.StringIO(z.read("PO_CHANGE_ORDER_TEMPLATE_ATTR_VALUE.csv").decode("utf-8-sig"))))
keep = ["EntityType", "AttrName", "DispatchToSupFlag", "ListOrder", "UserUpdatableFlag"]
text = code + " test change order template"
rows = {
  "PO_CHANGE_ORDER_TEMPLATE.csv": [{"CoTemplateCode": code, "TemplateName": code, "Description": text,
      "SeededTemplateId": "-1", "Status": "ACTIVE", "TypeLookupCode": "STANDARD"}],
  "PO_CHANGE_ORDER_TEMPLATE_TRANSLATION.csv": [{"PO_CHANGE_ORDER_TEMPLATE.CoTemplateCode": code, "TemplateName": code,
      "Description": text, "Language": "US", "SourceLang": "US"}],
  "PO_CHANGE_ORDER_TEMPLATE_ATTR_VALUE.csv": [dict({"PO_CHANGE_ORDER_TEMPLATE.CoTemplateCode": code}, **{k: r[k] for k in keep})
      for r in attrs if r["PO_CHANGE_ORDER_TEMPLATE.CoTemplateCode"] == src]}
json.dump(rows, open(run + "/rows.json", "w"))
print("attribute rows copied:", len(rows["PO_CHANGE_ORDER_TEMPLATE_ATTR_VALUE.csv"]))
EOF
```
- `SeededTemplateId` `-1` = user template; `Status` `ACTIVE` and `TypeLookupCode` `STANDARD` as on the existing
  user template. VERIFIED. An `INACTIVE` status was not tried (GUESS).
- To allow or forbid an attribute, change `UserUpdatableFlag` / `DispatchToSupFlag` (`Y`/`N`) in your copied rows
  only. VERIFIED for copying as is; other flag values GUESS.
Then COMMON_STEPS step 2 (package: 1 header, 1 translation, about 130 attribute rows).

## Import
COMMON_STEPS step 3. Expected log: "Business object: Purchasing Change Order Template. Status: Completed
successfully ... A total of 1 rows were processed. 0 rows of them failed" and "Purchasing Change Order Template
Attribute ... This object was already processed" (the attributes load with the header). VERIFIED.

## Read back
COMMON_STEPS step 4: header and translation `added 1 ['<CODE>']`, attribute CSV `added <n> ['<CODE>']` with n = the
copied row count, existing removed or changed 0 in all three. VERIFIED.

## Rules and limits
- New template codes only; the source template is read, never sent back.
- A template takes effect only where a buyer or a document setup selects it (GUESS from Oracle's docs; not tested).

## Worked example
`FSCRT_MZ_GF_CO1` copied from an existing user template (132 attribute rows): import ProcessId 100004744391044
(header 1 processed, 0 failed); after-export ProcessId 100004743404958: headers 1 -> 2, attributes 132 -> 264,
translations 1 -> 2, existing changed 0. VERIFIED.
