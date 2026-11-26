# Manage Buyer Assignment Rules (ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES): create a buyer assignment rule by FSM CSV

## What it is and when to use
Buyer assignment rules route requisition lines to a buyer when a requisition is submitted for approval. Oracle
evaluates ALL rules in ascending `RuleSeqNum` order; sequence numbers are unique across all rules. Rule sets
(`RuleSetCode`, codes of lookup `PO_BUYER_ASSIGN_RULE_SETS`) only group rules for searching; they do not limit which
rules are evaluated (Oracle 26D "What's a buyer assignment rule set?" and "Buyer Assignment Rules"). VERIFIED (docs).
Use this skill to add a NEW rule through FSCR's setup task CSV import. FSCR has no skill for this task.
Route: FSM setup CSV (task `ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES`, CSV supported: Y). VERIFIED.
No REST resource (`buyerAssignmentRules` describe: not found). VERIFIED.

## Placeholders
See `../purchasing-common/COMMON_STEPS.md` (`<RUN>`, `<PREFIX>`, `$S`). Plus:
- `<RULE_SET>`: an existing rule set code containing `<PREFIX>` (create one with `../buyer-rule-sets-lookup/SKILL.md`).
  The package builder needs `<PREFIX>` in the row, and `RuleSetCode` is where it goes.
- `<SEQ>`: a sequence number no rule uses yet (decimals allowed). To find one, run the Build rows script with any
  number: it first prints the existing sequences; if your number is taken it stops and writes nothing, so run it
  again with a free number.
- `<AMOUNT>`: the "exceeds line amount" condition.

## Sign-in
As in COMMON_STEPS.md.

## Prerequisites
1. `<RULE_SET>` exists: REST `standardLookups/PO_BUYER_ASSIGN_RULE_SETS/child/lookupCodes` lists it (see the rule
   sets skill). VERIFIED.
2. An existing rule to copy the BU, organization, supplier and buyer values from (step "Build rows"). Oracle requires
   a sequence, a procurement BU and a buyer, plus a requisitioning BU or a commodity (docs, VERIFIED). Copying them
   from an existing rule guarantees values Oracle accepts, and you never type or print the buyer's e-mail. VERIFIED.

## Export
COMMON_STEPS step 1 with `<TASK_CODE>` = `ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES`. One CSV:
`ORA_PO_BUYER_ASSIGNMENT_RULES.csv` with these columns (not in file order): RuleSeqNum, RuleSetCode,
ExceedsLineAmount, NonCatalogFlag, OrganizationCode, VendorName, ListName, ProcCategoryName, ProjectNumber,
ShortCodeReqBu, EnterpriseIdReqBU, ShortCodePrcBU, EnterpriseIdPrcBU, EgpCategoryCode, EmailAddress, CostCenter,
CreatedBy, LastUpdatedBy. The export holds buyer
e-mails: `$S/inspect_export.py` masks them; never print the raw CSV. VERIFIED.

## Build rows
Copy the existing rule with the LOWEST sequence (or any rule you choose) and change only the sequence, the rule set
and the amount. Run this script after editing the three values at its top (it prints no e-mail):
```bash
python3 - <<'EOF'
import zipfile, csv, io, glob, json
run, rule_set, seq, amount = "<RUN>", "<RULE_SET>", "<SEQ>", "<AMOUNT>"
z = zipfile.ZipFile(glob.glob(run + "/before/*.zip")[0])
rows = list(csv.DictReader(io.StringIO(z.read("ORA_PO_BUYER_ASSIGNMENT_RULES.csv").decode("utf-8-sig"))))
used = {float(r["RuleSeqNum"]) for r in rows}
print("existing sequences:", sorted(used))
if float(seq) in used:
    raise SystemExit("sequence " + seq + " is already used: pick a number higher than all of them; nothing written")
src = min(rows, key=lambda r: float(r["RuleSeqNum"]))
new = {k: v for k, v in src.items() if k not in ("CreatedBy", "LastUpdatedBy")}
new.update(RuleSeqNum=seq, RuleSetCode=rule_set, ExceedsLineAmount=amount)
json.dump({"ORA_PO_BUYER_ASSIGNMENT_RULES.csv": [new]}, open(run + "/rows.json", "w"))
print("copied rule", src["RuleSeqNum"], "-> new rule", seq, "in", rule_set, "; rows.json written")
EOF
```
- On a SHARED environment, keep the rule from catching other people's requisitions: use a `<SEQ>` higher than every
  existing sequence the script prints (so it is evaluated after them; earlier test rules may already use numbers
  such as 9999), and a very high `<AMOUNT>` (for example 999999999). VERIFIED (loaded).
- The script copies the rule with the lowest sequence; check that it is a real rule, not another test rule, if you
  need real values.
- `<RUN>/rows.json` and the package hold the copied buyer's e-mail in clear text: keep the run folder private.
  On a project environment, set the real conditions instead.
- Leave CreatedBy/LastUpdatedBy empty: the import fills them. VERIFIED.
Then COMMON_STEPS step 2.

## Import
COMMON_STEPS step 3. Expected log: "Business object: Purchasing Buyer Assignment Rules. Status: Completed successfully
... A total of 1 rows were processed. 0 rows of them failed". VERIFIED.

## Read back
COMMON_STEPS step 4: `ORA_PO_BUYER_ASSIGNMENT_RULES.csv` `added 1 ['<SEQ>']` (the first column is the sequence),
existing removed or changed 0, added without prefix 0. Check the row:
`python3 $S/inspect_export.py <RUN>/after/*.zip --match <RULE_SET>` shows your sequence, rule set and amount (the
buyer e-mail is masked). VERIFIED.

## Rules and limits
- New rules only. An existing sequence number would update that rule: the script refuses a used number.
- Every rule is live for every requisition, whatever its rule set: on a shared environment always use the high
  sequence and amount above.

## Worked example
Rule 9999 in rule set `FSCRT_MZ_GF_RS1`, amount 999999999, other values copied from rule 1: import ProcessId
100004744422117 (1 processed, 0 failed); after-export ProcessId 100004743447698: rules 2 -> 3, existing changed 0.
VERIFIED.
