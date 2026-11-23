"""Run 35: read-only probes for the 'neither' task Manage Purchasing Messages. Prints status codes and allowed methods only."""
import api, json
for res in ["messages", "setupMessages", "applicationMessages", "fndMessages", "purchasingMessages"]:
    st, t = api.call("GET", res, {"limit": "1", "onlyData": "true"})
    print(f"GET /fscmRestApi/resources/11.13.18.05/{res}?limit=1 -> {st}")
st, t = api.call("GET", "messages/describe")
if st == 200:
    d = json.loads(t); r = d.get("Resources", {}).get("messages", {})
    acts = sorted({a.get("name") for item in r.get("collection", {}).get("actions", [])+r.get("item", {}).get("actions", []) for a in [item]})
    print("messages describe actions:", acts)
st, t = api.call("GET", "setupTasks/ORA_PO_MANAGE_PURCHASING_MESSAGES", {"onlyData": "true"})
print("setupTasks ORA_PO_MANAGE_PURCHASING_MESSAGES ->", st, {k: v for k, v in (json.loads(t).items() if st == 200 else []) if "Flag" in k or k in ("TaskName",)})
