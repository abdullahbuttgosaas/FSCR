"""Added by GoSaaS, not part of official FSCR. Gap fill, Procurement, 2026-11-25. Offline: no Oracle call.

Turns a REST read of ONE existing standard lookup type (standardLookups/<TYPE>?expand=lookupCodes&onlyData=true)
into the UNCHANGED type row for build_csv_package.py (the FSM lookup package needs the parent type row in the
same ZIP for a new code to be processed). Copies only LookupType, Meaning, Description, ModuleId,
CustomizationLevel and RestAccessSecured, exactly as read; audit columns stay empty.

Also checks: the type allows new codes (CustomizationLevel E or U; S = system, refused) and the new codes
are not already in the type.

Usage: python -I lookup_type_row.py <type.json> [--new-code CODE ...]   -> prints the --row value on one line
"""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--new-code", action="append", default=[])
    a = ap.parse_args()
    d = json.load(open(a.json, encoding="utf-8"))
    if "items" in d:
        if len(d["items"]) != 1:
            sys.exit(f"STOP: expected 1 lookup type, found {len(d['items'])}")
        d = d["items"][0]
    lvl = d.get("CustomizationLevel")
    if lvl not in ("E", "U"):
        sys.exit(f"STOP: CustomizationLevel {lvl!r}: this type does not allow new codes")
    have = {c.get("LookupCode") for c in (d.get("lookupCodes") or [])}
    if isinstance(d.get("lookupCodes"), dict):
        have = {c.get("LookupCode") for c in d["lookupCodes"].get("items", [])}
    for c in a.new_code:
        if c in have:
            sys.exit(f"STOP: code {c} already exists in {d['LookupType']}: importing it would UPDATE it")
    vals = []
    for k in ("LookupType", "Meaning", "Description", "ModuleId", "CustomizationLevel", "RestAccessSecured"):
        v = d.get(k) or ""
        if "|" in v:
            sys.exit(f"STOP: {k} holds '|', which the builder cannot pass")
        vals.append(f"{k}={v}")
    print("FND_APP_STANDARD_LOOKUP.csv|" + "|".join(vals))


if __name__ == "__main__":
    main()
