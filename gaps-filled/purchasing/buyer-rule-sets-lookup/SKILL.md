# Manage Buyer Assignment Rule Sets Lookup (ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP): add a rule set code by FSM CSV

## What it is and when to use
Buyer assignment rules are grouped into rule sets. The rule sets are the codes of the extensible standard lookup
type `PO_BUYER_ASSIGN_RULE_SETS` (Purchasing module; seeded code `DEFAULT`). Use this skill to add a NEW rule set
code through FSCR's setup task CSV import. FSCR has no skill for this task. Adding a code does not change any rule
or assignment; rules are added to a rule set in "Manage Buyer Assignment Rules".
Route: FSM setup CSV (task `ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP`, CSV supported: Y; the export is scoped to
lookup type `PO_BUYER_ASSIGN_RULE_SETS`). VERIFIED. Read-back by REST `standardLookups`. VERIFIED.

## Placeholders
See `../purchasing-common/COMMON_STEPS.md` (`<RUN>`, `<PREFIX>`, `$S`). Plus:
- `<RULE_SET>`: the new code, `<PREFIX>` + short name, upper case, e.g. `FSCRT_AB_GF_RS1`.

## Sign-in
As in COMMON_STEPS.md.

## Prerequisites
1. The parent lookup type row, read live and copied UNCHANGED (VERIFIED: an FSM child row is skipped when its parent
   row is not in the same ZIP; Oracle's log says "Parent row is missing in file FND_APP_STANDARD_LOOKUP.csv ...
   Row will be skipped" and 0 rows are processed):
   ```bash
   R=core/fusion-api/rest-api-client/scripts/fusion_rest_client.py
   python3 $R --method GET --token-cache auto --no-open-browser \
     --query fields=LookupType,Meaning,Description,ModuleId,CustomizationLevel,RestAccessSecured \
     --output <RUN>/type_before.json "/fscmRestApi/resources/11.13.18.05/standardLookups/PO_BUYER_ASSIGN_RULE_SETS" > <RUN>/rest.log 2>&1
   python3 $R --method GET --token-cache auto --no-open-browser --query limit=500 \
     --output <RUN>/codes_before.json "/fscmRestApi/resources/11.13.18.05/standardLookups/PO_BUYER_ASSIGN_RULE_SETS/child/lookupCodes" > <RUN>/rest.log 2>&1
   python3 -c "import json;print([i['LookupCode'] for i in json.load(open('<RUN>/codes_before.json'))['items']])"
   ```
   The last line lists the existing codes; `<RULE_SET>` must not be among them. The codes read has no `fields`
   filter (all attributes) and `limit=500`, so the later unchanged-check sees every attribute of every code; if the
   file shows `"hasMore": true`, stop and page with `offset` first.

## Export
COMMON_STEPS step 1 with `<TASK_CODE>` = `ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP`. Two CSVs: `FND_APP_STANDARD_LOOKUP.csv`
and `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv`. While the type holds only seeded codes, the export has 0 rows; once a
user code exists (for example an earlier test code), the export holds the type row and all its codes. VERIFIED.

## Build rows
Build `<RUN>/rows.json` from the live parent row (so it is sent exactly as Oracle holds it) plus your new code:
```bash
python3 - <<'EOF'
import json
run = "<RUN>"
parent = {k: ("" if v is None else v) for k, v in json.load(open(run + "/type_before.json")).items() if k != "links"}
rows = {"_unchanged_parents": {"FND_APP_STANDARD_LOOKUP.csv": [parent]},
        "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv": [{"FND_APP_STANDARD_LOOKUP.LookupType": "PO_BUYER_ASSIGN_RULE_SETS",
            "LookupCode": "<RULE_SET>", "Meaning": "<RULE_SET> rule set", "Description": "<RULE_SET> test rule set",
            "EnabledFlag": "Y", "StartDateActive": "2026/01/01", "DisplaySequence": "99"}]}
json.dump(rows, open(run + "/rows.json", "w"), indent=1)
EOF
```
- `_unchanged_parents` rows go into the package as they are (`build_fsm_package.py` does not check them for the
  prefix). Never edit the parent's values. VERIFIED.
- Dates use `YYYY/MM/DD`. VERIFIED.
Then COMMON_STEPS step 2.

## Import
COMMON_STEPS step 3. Expected log: "Business object: Application Standard Lookup ... A total of 2 rows were
processed. 0 rows of them failed" (unchanged parent + new code). VERIFIED.

## Read back
1. REST, the proof that nothing existing changed (VERIFIED):
   ```bash
   R=core/fusion-api/rest-api-client/scripts/fusion_rest_client.py
   python3 $R --method GET --token-cache auto --no-open-browser \
     --query fields=LookupType,Meaning,Description,ModuleId,CustomizationLevel,RestAccessSecured \
     --output <RUN>/type_after.json "/fscmRestApi/resources/11.13.18.05/standardLookups/PO_BUYER_ASSIGN_RULE_SETS" > <RUN>/rest.log 2>&1
   python3 $R --method GET --token-cache auto --no-open-browser --query limit=500 \
     --output <RUN>/codes_after.json "/fscmRestApi/resources/11.13.18.05/standardLookups/PO_BUYER_ASSIGN_RULE_SETS/child/lookupCodes" > <RUN>/rest.log 2>&1
   python3 - <<'EOF'
   import json
   run = "<RUN>"
   s = lambda f: {k: v for k, v in json.load(open(run + "/" + f)).items() if k != "links"}
   c = lambda f: {i["LookupCode"]: {k: v for k, v in i.items() if k != "links"} for i in json.load(open(run + "/" + f))["items"]}
   # all attributes are compared, including Description, EndDateActive, Tag and the who/date columns
   b, a = c("codes_before.json"), c("codes_after.json")
   print("parent unchanged:", s("type_before.json") == s("type_after.json"))
   print("existing codes unchanged:", all(a.get(k) == v for k, v in b.items()))
   print("new codes:", sorted(set(a) - set(b)))
   EOF
   ```
   Pass = `parent unchanged: True`, `existing codes unchanged: True`, and `<RULE_SET>` in new codes.
2. COMMON_STEPS step 4 (export compare): `existing removed or changed` must be 0. Both checks together are the
   proof. When the before-export was empty (0 rows: only seeded codes existed), the after-export shows the unchanged
   parent type and the seeded codes too, so `added without prefix` is not 0 there: that is expected. When earlier
   user codes already existed, the before-export holds the type and its codes, and `added without prefix` is 0.
   VERIFIED (both cases).

## Rules and limits
- Only add codes. Never change `DEFAULT` or any other existing code, and never edit the parent row.
- Disabling or end-dating a rule set used by rules changes buyer assignment for everyone: not part of this skill.

## Worked example
Code `FSCRT_MZ_GF_RS1`: try 1 without the parent row: ProcessId 100004743404860, "Parent row is missing ... Row will
be skipped", 0 processed, nothing created. Try 2 with the unchanged parent: ProcessId 100004743404898, 2 rows, 0
failed; REST: parent unchanged True, existing codes (`DEFAULT`) unchanged True, new code `FSCRT_MZ_GF_RS1`;
after-export ProcessId 100004743404936, existing removed or changed 0. VERIFIED.
