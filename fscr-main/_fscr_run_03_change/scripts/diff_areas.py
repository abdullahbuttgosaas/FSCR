"""Whole-area before/after diff of the Run 03 REST snapshots (offline).
Each area's items are keyed by their natural key; audit-only fields are reported separately so a record whose
only change is LastUpdateDate/LastUpdateLogin still shows up (it means Oracle touched it).
Usage: diff_areas.py <before_dir> <after_dir> <out.json>"""
import json, sys
from pathlib import Path

AUDIT = {"LastUpdateDate", "LastUpdateLogin", "LastUpdatedBy", "@context", "links"}
AREAS = {
    "priceLists_all.json": ("PriceListId", "PriceListName"),
    "order_types_all.json": ("LookupCode", "LookupCode"),
    "finBusinessUnitsLOV.json": ("BusinessUnitId", "BusinessUnitName"),
    "customerAccountSitesLOV_all.json": ("SiteUseId", "CustomerName"),
    "hubOrganizations_fscrt.json": ("PartyId", "OrganizationName"),
    "hubPersons_fscrt.json": ("PartyId", "PersonName"),
}


def norm(v):
    return json.dumps(v, sort_keys=True, default=str)


def items(path, key):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return {str(i[key]): i for i in d["items"]}


def lookups(path):
    out = {}
    for t in json.loads(Path(path).read_text(encoding="utf-8"))["items"]:
        out["TYPE " + t["LookupType"]] = {k: v for k, v in t.items() if k != "lookupCodes"}
        for c in t["lookupCodes"]["items"]:
            out[t["LookupType"] + " / " + c["LookupCode"]] = c
    return out


bd, ad, outp = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
report = {}
for f, (key, label) in list(AREAS.items()) + [("standardLookups_fscrt.json", (None, None))]:
    b = lookups(bd / f) if key is None else items(bd / f, key)
    a = lookups(ad / f) if key is None else items(ad / f, key)
    rows = {"before": len(b), "after": len(a), "added": sorted(set(a) - set(b)), "removed": sorted(set(b) - set(a)), "changed": {}}
    for k in set(a) & set(b):
        fields = set(a[k]) | set(b[k])
        biz = {x: (b[k].get(x), a[k].get(x)) for x in fields if x not in AUDIT and norm(b[k].get(x)) != norm(a[k].get(x))}
        aud = [x for x in fields if x in AUDIT - {"@context", "links"} and norm(b[k].get(x)) != norm(a[k].get(x))]
        if biz or aud:
            name = (a[k].get(label) if label else k) or k
            rows["changed"][f"{name} [{k}]"] = {"business": biz, "audit_only_fields": aud}
    report[f] = rows
    print(f"{f}: before {rows['before']} after {rows['after']} added {len(rows['added'])} removed {len(rows['removed'])} changed {len(rows['changed'])}")
    for n, d in rows["changed"].items():
        print("   ", n, "| business:", list(d["business"]), "| audit:", d["audit_only_fields"])
outp.write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
