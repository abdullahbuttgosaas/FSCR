# Manage Purchasing Descriptive Flexfields (PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS): add a DFF context and segment by FSM CSV

## What it is and when to use
Purchasing descriptive flexfields (DFFs) add customer fields to purchasing pages. Use this skill to add a NEW context
with a context-sensitive segment to a Purchasing DFF through FSCR's setup task CSV import. FSCR has no skill for this.
Route: FSM setup CSV (task `PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS`, CSV supported: Y; export scoped to module
`PrcPoCommonPo`). VERIFIED. Parent read and read-back also by REST `descriptiveFlexfields` (get only). VERIFIED.
The import ALSO DEPLOYS the flexfield: REST `DeploymentDate` moved to the import time on every import (status stays
`DEPLOYED`), so the new context is live on the DFF's pages right after the import. No separate deploy step is needed
(and FSCR has none). VERIFIED (3 imports, 26/11/2026).

## Placeholders
See `../purchasing-common/COMMON_STEPS.md` (`<RUN>`, `<PREFIX>`, `$S`). Plus:
- `<DFF_CODE>`: a Purchasing DFF code, e.g. `PO_LINE_TYPES` (prerequisite 1). Application ID: `201`.
- `<CONTEXT>`: new context code, `<PREFIX>` + short name, e.g. `FSCRT_AB_GF_CTX1`; `<CONTEXT_ID>`: its API name,
  letters and digits only, starting with a letter, e.g. `fscrtAbGfCtx1`.
- `<SEGMENT>`: new segment code, e.g. `FSCRT_AB_GF_SEG1`; `<SEGMENT_ID>`: its API name, e.g. `fscrtAbGfSeg1`.
- `<COLUMN>`: storage column, e.g. `ATTRIBUTE1` (prerequisite 3).
- `<VALUE_SET>`: an existing value set code (create one with `../purchasing-value-sets/SKILL.md`).

## Sign-in
As in COMMON_STEPS.md.

## Prerequisites
1. Pick the DFF and read its parent row live (VERIFIED). Query by code only: a filter with `and ApplicationId=...`
   returned 0 items.
   ```bash
   python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --method GET --token-cache auto \
     --no-open-browser --query "q=DescriptiveFlexfieldCode='<DFF_CODE>'" --output <RUN>/parent_before.json \
     "/fscmRestApi/resources/11.13.18.05/descriptiveFlexfields" > <RUN>/rest.log 2>&1
   python3 -c "import json;print([(i['DescriptiveFlexfieldCode'],i['ApplicationId'],i['DeploymentStatus']) for i in json.load(open('<RUN>/parent_before.json'))['items']])"
   ```
   It must print one entry with application `201`. To list all Purchasing DFFs use
   `q=DescriptiveFlexfieldCode LIKE 'PO_%'`. `DeploymentStatus` must be `DEPLOYED`; note `DeploymentDate`: the
   import will set it to the import time. VERIFIED.
2. A value set for the segment: `../purchasing-value-sets/SKILL.md` (tested skill). Check it exists:
   ```bash
   python3 core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --method GET --token-cache auto \
     --no-open-browser --query "q=ValueSetCode='<VALUE_SET>'" --output <RUN>/vs_check.json \
     "/fscmRestApi/resources/11.13.18.05/valueSets" > <RUN>/rest.log 2>&1
   python3 -c "import json;print(len(json.load(open('<RUN>/vs_check.json'))['items']))"
   ```
   It must print `1`.
3. A free storage column: in the before-export, no row of `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_GLOBAL_SEGMENT.csv`
   for this DFF uses `<COLUMN>` (a global segment's column cannot be reused in a context). Context-sensitive segments
   in different contexts may use the same column. VERIFIED (no global segments; ATTRIBUTE1 accepted).

## Export
COMMON_STEPS step 1 with `<TASK_CODE>` = `PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS`. 13 CSVs. Only DFFs that already
have user contexts or segments are exported (with their parent row and Oracle's context segment `ATTRIBUTE_CATEGORY`);
an unconfigured DFF is not in the export. VERIFIED.
The context-sensitive segment goes in `ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv` (child of the context), not in
`..._CONTEXT_SEGMENT.csv` (that one holds the context selector itself). VERIFIED.

## Build rows
Edit the values at the top, then run (the parent row is copied from the REST read, unchanged):
```bash
python3 - <<'EOF'
import json
run, dff, ctx, ctx_id, seg, seg_id, col, vs = ("<RUN>", "<DFF_CODE>", "<CONTEXT>", "<CONTEXT_ID>",
                                              "<SEGMENT>", "<SEGMENT_ID>", "<COLUMN>", "<VALUE_SET>")
p = [i for i in json.load(open(run + "/parent_before.json"))["items"] if i["ApplicationId"] == 201][0]
parent = {k: ("" if p.get(k) is None else str(p[k])) for k in ("ApplicationId", "DescriptiveFlexfieldCode", "Name", "Description", "Delimiter")}
key = {"FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode": dff, "FND_APP_DESCRIPTIVE_FLEXFIELD.ApplicationId": "201"}
rows = {"_unchanged_parents": {"FND_APP_DESCRIPTIVE_FLEXFIELD.csv": [parent]},
  "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv": [dict(key, ContextCode=ctx, ContextIdentifier=ctx_id, Name=ctx,
      Description=ctx + " test context", EnabledFlag="Y")],
  "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv": [dict(key, **{"ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.ContextCode": ctx},
      SegmentCode=seg, SegmentIdentifier=seg_id, ColumnName=col, Name=seg, Description=seg + " test segment",
      Prompt=seg, ShortPrompt=seg[-10:], SequenceNumber="10", EnabledFlag="Y", DisplayType="LOV",
      RequiredFlag="N", ReadOnlyFlag="N", BIEnabledFlag="N", ValueSetCode=vs)]}
json.dump(rows, open(run + "/rows.json", "w"), indent=1)
print("rows written")
EOF
```
Learned from Oracle's errors (VERIFIED):
- Leave the context's `MultirowFlag`, `TranslatableFlag` and `AdvancedQueryFlag` EMPTY. `N` is refused for this DFF:
  "cannot have a context with multiple rows" (FND-2771) and "cannot have a translatable context" ("must be null").
- `DisplayType` takes the code from lookup `FND_DF_SEGMENT_DISPLAY_TYPES` (REST
  `standardLookups/FND_DF_SEGMENT_DISPLAY_TYPES/child/lookupCodes`): `LOV` for a list of values, `TEXT_BOX`,
  `DROP_DOWN_LIST`, ... `LIST_OF_VALUES` is refused (FND-2777).
Then COMMON_STEPS step 2.

## Import
COMMON_STEPS step 3. Expected log: "Business object: Application Descriptive Flexfield. Status: Completed successfully
... A total of 3 rows were processed. 0 rows of them failed" (parent + context + segment). A refused row shows
"Completed with errors" and 0 rows processed; read the cause with `python3 $S/log_summary.py --full ...` (the
`<TEXT>` parts). VERIFIED.

## Read back
1. COMMON_STEPS step 4. Expected: the context CSV and the segment CSV each add 1 row (listed under the DFF code, the
   first column), existing removed or changed 0. If the DFF had no user context before, the after-export also shows
   the parent row and Oracle's `ATTRIBUTE_CATEGORY` context segment as "added without prefix": check that their
   `LastUpdateDate` is not today (they were only exported, not changed). VERIFIED.
2. REST parent unchanged: run the prerequisite 1 command again into `<RUN>/parent_after.json` and compare Name,
   Description, Delimiter and ModuleId with `parent_before.json` (they must be equal). `DeploymentStatus` stays
   `DEPLOYED` and `DeploymentDate` changes to the import time: that is the automatic deploy, not a change of the
   definition. VERIFIED.

## Rules and limits
- New contexts and segments only; never change or remove an existing one.
- The import deploys the whole flexfield at once: your context becomes a choice on every page that shows this DFF
  (context-sensitive, so its segment appears only when that context is selected). On a shared environment, import
  only with the environment owner's agreement, and prefer a DFF on a setup page (such as `PO_LINE_TYPES`) over one
  on transaction pages (headers, lines, distributions).

## Worked example
DFF `PO_LINE_TYPES`, context `FSCRT_MZ_GF_CTX1`, segment `FSCRT_MZ_GF_SEG1` on `ATTRIBUTE1` with value set
`FSCRT_MZ_GF_VS1`. Try 1 ProcessId 100004743436790: refused (multirow `N`; display type `LIST_OF_VALUES`). Try 2
ProcessId 100004744417669: refused (translatable `N`). Try 3 ProcessId 100004744422130: 3 rows, 0 failed. After-export
ProcessId 100004743454753: context and segment added; parent and Oracle's context segment exported unchanged (last
updated before the test); REST: parent definition unchanged, DEPLOYED, DeploymentDate moved from 04/04/2026 to the
import time (automatic deploy). VERIFIED.
