"""GET only: describe + existing rows + LOV for customer accounts."""
import sys, json; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent)); import api
checks = [("anmr_describe", "alternateNameMappingRules/describe", None),
          ("anmr_all", "alternateNameMappingRules", {"limit": 50, "onlyData": "true", "totalResults": "true"}),
          ("anmr_fscrt_before", "alternateNameMappingRules", {"q": "AlternatePayerName LIKE 'FSCRT_%'", "onlyData": "true"})]
for n, p, q in checks:
    st, t = api.call("GET", p, q); open(api.RUN/f"evidence/{n}.json", "w", encoding="utf-8").write(t)
    print(n, st, len(t))
d = json.load(open(api.RUN/"evidence/anmr_describe.json", encoding="utf-8"))
r = d["Resources"]["alternateNameMappingRules"]
print("actions:", [a.get("name")+":"+a.get("method","") for a in r.get("item",{}).get("actions",[])+r.get("collection",{}).get("actions",[])])
for a in r["attributes"]:
    print(" ", a["name"], a.get("type"), "upd="+str(a.get("updatable")), "mand="+str(a.get("mandatory")), a.get("lov",{}).get("childRef","") if isinstance(a.get("lov"),dict) else "")
print(json.dumps(r.get("item",{}).get("links",[]))[:300]); print(json.dumps(r.get("collection",{}).get("links",[]))[:200])
for k in ("lovs","LOVs"): 
    if k in r: print(k, json.dumps(r[k])[:800])
print(json.dumps({k:v for k,v in r.items() if k not in ("attributes","item","collection")})[:1500])
