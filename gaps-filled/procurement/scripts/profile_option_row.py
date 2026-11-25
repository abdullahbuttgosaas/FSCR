"""Added by GoSaaS, not part of official FSCR. Gap fill, Procurement, 2026-11-25. Offline: no Oracle call.

Works on a REST read of ONE profile option:
  /fscmRestApi/resources/11.13.18.05/profileOptions?q=ProfileOptionName='<NAME>'&expand=all&onlyData=true

  python -I profile_option_row.py <option.json>              -> prints the UNCHANGED option row for build_csv_package.py
  python -I profile_option_row.py <option.json> --show       -> prints name, ApplicationId, levels and level values only
  python -I profile_option_row.py <after.json> --same-as <before.json>
                                                             -> SAME: PASS when option fields, levels and values are equal
Never prints audit fields (they hold user names).
"""
import argparse
import json
import sys

OPT_COLS = ("ProfileOptionName", "ApplicationId", "ModuleId", "Description", "StartDateActive", "EndDateActive",
            "UserProfileOptionName", "SqlValidation")


def one(path):
    d = json.load(open(path, encoding="utf-8"))
    items = d.get("items", [d])
    if len(items) != 1:
        sys.exit(f"STOP: expected 1 profile option, found {len(items)}")
    return items[0]


def levels(x):
    return sorted((l.get("LevelName"), l.get("EnabledFlag"), l.get("UpdateableFlag")) for l in x.get("profileOptionLevels") or [])


def values(x):
    out = []
    for k, v in x.items():
        if isinstance(v, list) and k.endswith("ProfileOptionValues"):
            out += sorted((k, i.get("LevelValue"), i.get("ProfileOptionValue")) for i in v)
    return out


def date(v):
    return (v or "")[:10].replace("-", "/")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--same-as")
    a = ap.parse_args()
    x = one(a.json)
    if a.same_as:
        b = one(a.same_as)
        diff = [c for c in OPT_COLS if x.get(c) != b.get(c)]
        ok = not diff and levels(x) == levels(b) and values(x) == values(b)
        print("option fields changed:", diff)
        print("levels equal:", levels(x) == levels(b), "| values equal:", values(x) == values(b))
        print("values now:", values(x))
        print("SAME:", "PASS" if ok else "FAIL")
        return 0 if ok else 1
    if a.show:
        print(x.get("ProfileOptionName"), "ApplicationId", x.get("ApplicationId"), x.get("ApplicationShortName"))
        print("levels (name, enabled, updatable):", levels(x))
        print("values:", values(x))
        return 0
    vals = {c: str(x.get(c) or "") for c in OPT_COLS}
    vals["StartDateActive"] = date(x.get("StartDateActive"))
    vals["EndDateActive"] = date(x.get("EndDateActive"))
    for c, v in vals.items():
        if "|" in v:
            sys.exit(f"STOP: {c} holds '|', which the builder cannot pass")
    print("FND_APP_PROFILE_OPTION.csv|" + "|".join(f"{c}={v}" for c, v in vals.items() if v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
