"""POST one alternate name mapping rule. Usage: create.py <attempt_label> <payload.json>. Logs request+response (no token)."""
import sys, json, datetime; sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent)); import api
label, pf = sys.argv[1], sys.argv[2]
body = open(pf, encoding="utf-8").read()
name = json.loads(body)["AlternatePayerName"]
assert name.startswith("FSCRT_")
st0, t0 = api.call("GET", "alternateNameMappingRules", {"q": f"AlternatePayerName='{name}'", "onlyData": "true"})
if json.loads(t0)["count"] != 0: sys.exit("NAME_ALREADY_EXISTS - stop, no update")
ts = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
st, t = api.call("POST", "alternateNameMappingRules", body=body)
rec = {"attempt": label, "time": ts, "method": "POST", "path": "/fscmRestApi/resources/11.13.18.05/alternateNameMappingRules",
       "request_body": json.loads(body), "status": st, "response": t}
open(api.RUN / f"evidence/attempt_{label}.json", "w", encoding="utf-8").write(json.dumps(rec, indent=1))
print(st); print(t[:1500])
