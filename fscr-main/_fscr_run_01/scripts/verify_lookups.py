"""Compare lookup read-back with what was sent; check existing ORA_DOO_ORDER_TYPES codes unchanged. Read-only."""
import json, glob, os
E = r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01"
P = os.path.join(E, "payloads")
def L(p): return json.load(open(p, encoding="utf-8"))
out = []
for lt, files in [("FSCRT_OUTDOOR_ACTIVITY_F01", ["lt1", "lc_hiking", "lc_paddling"]), ("FSCRT_CARRIER_SERVICE_TIER_F01", ["lt2", "lc_standard", "lc_freight"])]:
    rb = L(os.path.join(E, "evidence", f"readback_{lt}.json"))
    sent = L(os.path.join(P, files[0] + ".json"))
    mism = [k for k, v in sent.items() if rb.get(k) != v]
    out.append((lt, "type", "OK" if not mism else f"MISMATCH {mism}", {k: rb.get(k) for k in ("Meaning", "RestAccessSecured", "ModuleId")}))
    codes = {c["LookupCode"]: c for c in rb["lookupCodes"]}
    for f in files[1:]:
        s = L(os.path.join(P, f + ".json")); c = codes.get(s["LookupCode"])
        mism = "MISSING" if c is None else [k for k, v in s.items() if c.get(k) != v]
        out.append((lt, s["LookupCode"], "OK" if mism == [] else f"MISMATCH {mism}", None if c is None else {k: c.get(k) for k in ("EnabledFlag", "DisplaySequence", "Tag", "Meaning")}))
b = {i["LookupCode"]: i for i in L(os.path.join(E, "evidence", "ora_doo_order_types_before.json"))["items"]}
a = {i["LookupCode"]: i for i in L(os.path.join(E, "evidence", "ora_doo_order_types_after.json"))["items"]}
changed = [k for k in b if a.get(k) != b[k]]
new = sorted(set(a) - set(b))
for f in ["ot_trail", "ot_warranty"]:
    s = L(os.path.join(P, f + ".json")); c = a.get(s["LookupCode"])
    mism = "MISSING" if c is None else [k for k, v in s.items() if c.get(k) != v]
    out.append(("ORA_DOO_ORDER_TYPES", s["LookupCode"], "OK" if mism == [] else f"MISMATCH {mism}", None if c is None else {k: c.get(k) for k in ("EnabledFlag", "Meaning")}))
for r in out: print(r)
print("existing codes before", len(b), "after", len(a), "existing changed", changed, "new", new)
