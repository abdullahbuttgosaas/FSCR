"""GET only. For each 'neither' task ask FSM if CSV import/export is supported."""
import csv, json, sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent)); import api
rows = list(csv.reader(open(api.RUN/"evidence/neither_erp_scm.csv", encoding="utf-8")))
out = []
for r in rows:
    code = r[3]
    si, ti = api.call("GET", "setupTaskCSVImports/" + code, {"onlyData": "true"})
    se, te = api.call("GET", "setupTaskCSVExports/" + code, {"onlyData": "true"})
    def flag(t, k):
        try: return json.loads(t).get(k)
        except Exception: return None
    out.append({"area": r[0], "module": r[2], "code": code, "name": r[4], "imp_status": si, "ImportSupportedFlag": flag(ti, "ImportSupportedFlag"), "exp_status": se, "ExportSupportedFlag": flag(te, "ExportSupportedFlag")})
    print(si, flag(ti, "ImportSupportedFlag"), se, flag(te, "ExportSupportedFlag"), code)
json.dump(out, open(api.RUN/"evidence/csv_support_probe.json", "w"), indent=1)
with open(api.RUN/"evidence/csv_support_probe.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
