"""Added by GoSaaS, not part of official FSCR. Origin: Run 25, ETIA-TEST. Written in Run 27a, unchanged check added in Run 27c.
OFFLINE. Makes no Oracle call. Reads JSON files that you saved with FSCR's REST client
(fusion_rest_client.py ... --output <file>) and checks them. Standard library only, so -I is fine.

Two modes:

  precheck  - before the POST. Checks your planned names against the "before" GET file:
              every name starts with the prefix, is at most 320 characters, is not repeated,
              and does not already exist (a POST with Upsert-Mode could update it; we never
              send that header, but a clash still means "pick another name").
      python -I verify_rules.py precheck --before before_all.json --name "FSCRT_RunNN Payer A" [--name ...]

  verify    - after the POST. Compares the "before" and "after" GET files of the whole collection:
              every expected name is in "after" and was not in "before";
              total rows after == total rows before + number of expected names;
              rows with the prefix after == rows with the prefix before + number of expected names;
              no row that existed before was removed;
              no row that existed before was changed (same payer name, account, bank names, Active,
              ObjectVersionNumber and LastUpdateDate; added in Run 27c);
              optional --account: each new row points at that CustomerAccountNumber;
              each new row has Active = Y (unless --allow-inactive).
      python -I verify_rules.py verify --before before_all.json --after after_all.json \
          --expect "FSCRT_RunNN Payer A" --expect "FSCRT_RunNN Payer B" [--account 21541] [--rows-out verify_rows.csv]

Exit code 0 = PASS, 1 = FAIL, 2 = bad input file.
"""
import argparse, csv, json, sys
from pathlib import Path

ROW_FIELDS = ("AlternateNameId", "AlternatePayerName", "CustomerAccountNumber", "CustomerName",
              "ZenginCustomerBankName", "ZenginCustomerBankBranchName", "Active",
              "CreatedBy", "CreationDate", "ObjectVersionNumber")
# Fields that must be the same before and after for every rule that existed before.
UNCHANGED_FIELDS = ("AlternatePayerName", "CustomerAccountNumber", "ZenginCustomerBankName",
                    "ZenginCustomerBankBranchName", "Active", "ObjectVersionNumber", "LastUpdateDate")


def load(path):
    """Load a saved collection GET. Returns (items, total_or_None, has_more)."""
    try:
        body = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"BAD INPUT: cannot read {path}: {exc}"); sys.exit(2)
    if not isinstance(body, dict) or "items" not in body:
        print(f"BAD INPUT: {path} is not a REST collection response (no 'items')"); sys.exit(2)
    items = body["items"]
    total = body.get("totalResults")
    has_more = bool(body.get("hasMore"))
    return items, total, has_more


def total_of(items, total):
    return total if isinstance(total, int) else len(items)


def precheck(a):
    items, total, has_more = load(a.before)
    existing = {i.get("AlternatePayerName") for i in items}
    ok = True
    print(f"before: {total_of(items, total)} rules in total, {len(items)} in this file, hasMore={has_more}")
    if has_more:
        print("FAIL: hasMore=true, the before file is cut off; re-run the GET with a bigger limit"); ok = False
    seen = set()
    for n in a.name:
        problems = []
        if not n.startswith(a.prefix): problems.append(f"does not start with {a.prefix}")
        if len(n) > 320: problems.append("longer than 320 characters")
        if n in seen: problems.append("repeated")
        if n in existing: problems.append("already exists in the before file")
        seen.add(n)
        print(f"  {n!r}: {'OK' if not problems else 'NO - ' + '; '.join(problems)}")
        ok = ok and not problems
    print("PRECHECK:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def verify(a):
    b_items, b_total, b_more = load(a.before)
    f_items, f_total, f_more = load(a.after)
    ok = True
    if b_more or f_more:
        print(f"FAIL: hasMore=true (before={b_more}, after={f_more}); counts are not reliable"); ok = False

    b_names = {i.get("AlternatePayerName") for i in b_items}
    f_by_name = {i.get("AlternatePayerName"): i for i in f_items}
    n_new = len(a.expect)

    # 1. expected names: present after, absent before
    for n in a.expect:
        if n in b_names:
            print(f"FAIL: {n!r} already existed before"); ok = False
        if n not in f_by_name:
            print(f"FAIL: {n!r} not found after"); ok = False

    # 2. total count
    bt, ft = total_of(b_items, b_total), total_of(f_items, f_total)
    print(f"total rules: before {bt} + new {n_new} = {bt + n_new}; after {ft}")
    if ft != bt + n_new: print("FAIL: total count is not before + new"); ok = False

    # 3. prefix count
    bp = sum(1 for i in b_items if str(i.get("AlternatePayerName", "")).startswith(a.prefix))
    fp = sum(1 for i in f_items if str(i.get("AlternatePayerName", "")).startswith(a.prefix))
    print(f"rules named {a.prefix}*: before {bp} + new {n_new} = {bp + n_new}; after {fp}")
    if fp != bp + n_new: print("FAIL: prefix count is not before + new"); ok = False

    # 4. nothing removed (by id)
    b_ids = {str(i.get("AlternateNameId")) for i in b_items}
    f_ids = {str(i.get("AlternateNameId")) for i in f_items}
    removed = sorted(b_ids - f_ids)
    if removed: print(f"FAIL: rows missing after: {removed}"); ok = False

    # 4b. earlier rows unchanged (added in Run 27c, from the Run 27b cold test)
    f_by_id = {str(i.get("AlternateNameId")): i for i in f_items}
    changed = []
    for b in b_items:
        f = f_by_id.get(str(b.get("AlternateNameId")))
        if f is None: continue  # already reported as missing
        diffs = [k for k in UNCHANGED_FIELDS if k in b and b.get(k) != f.get(k)]
        if diffs: changed.append((b.get("AlternateNameId"), b.get("AlternatePayerName"), diffs))
    for rid, name, diffs in changed:
        print(f"FAIL: earlier rule {rid} {name!r} changed: {', '.join(diffs)}"); ok = False
    print(f"earlier rules unchanged: {not changed and not removed} ({len(b_items)} checked)")

    # 5. new-row details
    rows = []
    for n in a.expect:
        r = f_by_name.get(n)
        if not r: continue
        if a.account and str(r.get("CustomerAccountNumber")) != a.account:
            print(f"FAIL: {n!r} points at account {r.get('CustomerAccountNumber')}, expected {a.account}"); ok = False
        if not a.allow_inactive and r.get("Active") != "Y":
            print(f"FAIL: {n!r} has Active={r.get('Active')!r}"); ok = False
        row = {k: r.get(k) for k in ROW_FIELDS}
        rows.append(row)
        print("  new:", row)

    if a.rows_out and rows:
        with open(a.rows_out, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(ROW_FIELDS)); w.writeheader(); w.writerows(rows)
        print("wrote", a.rows_out)
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="Offline checks for alternate name mapping rules (GoSaaS gap fill).")
    sub = ap.add_subparsers(dest="mode", required=True)
    p = sub.add_parser("precheck"); p.add_argument("--before", required=True)
    p.add_argument("--name", action="append", required=True); p.add_argument("--prefix", default="FSCRT_")
    v = sub.add_parser("verify"); v.add_argument("--before", required=True); v.add_argument("--after", required=True)
    v.add_argument("--expect", action="append", required=True); v.add_argument("--prefix", default="FSCRT_")
    v.add_argument("--account"); v.add_argument("--allow-inactive", action="store_true"); v.add_argument("--rows-out")
    a = ap.parse_args()
    return precheck(a) if a.mode == "precheck" else verify(a)


if __name__ == "__main__":
    sys.exit(main())
