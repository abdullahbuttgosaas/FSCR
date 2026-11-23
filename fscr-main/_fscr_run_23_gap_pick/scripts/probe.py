"""Run 23 read-only probe. GET only; never prints the token. Saves each response to evidence/."""
import gzip, json, sys, urllib.request, urllib.parse, urllib.error, time
from pathlib import Path
W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_08_compare\fscr-work8")
sys.path.insert(0, str(W / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa
OUT = Path(__file__).resolve().parents[1] / "evidence"
props = fa.oauth_service_properties(fa.read_properties(W / "core/auth/fusionEnv.properties"), "standard")
token = fa.load_cached_access_token(props) or sys.exit("TOKEN_EXPIRED")
B = "/fscmRestApi/resources/11.13.18.05/"
def get(path, q=None):
    url = props["restBaseUrl"].rstrip("/") + B + path + (("?" + urllib.parse.urlencode(q)) if q else "")
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", "Bearer " + token); req.add_header("REST-Framework-Version", "9"); req.add_header("Accept-Encoding", "identity")
    try:
        with urllib.request.urlopen(req, timeout=120) as r: raw, st = r.read(), r.status
    except urllib.error.HTTPError as e: raw, st = e.read(), e.code
    except urllib.error.URLError as e: return 0, str(e.reason)
    if raw[:2] == b"\x1f\x8b": raw = gzip.decompress(raw)
    return st, raw.decode("utf-8", "replace")
probes = json.load(open(sys.argv[1]))
res = []
for p in probes:
    st, t = get(p["path"], p.get("q"))
    name = p["id"] + ".json"; (OUT / name).write_text(t, encoding="utf-8")
    summ = ""
    try:
        d = json.loads(t)
        if "items" in d: summ = f"items={len(d['items'])} hasMore={d.get('hasMore')}"
        elif "Resources" in d or "resources" in d: summ = "describe ok"
        else: summ = "keys=" + ",".join(list(d)[:6])
    except Exception: summ = t[:120].replace("\n", " ")
    res.append({"id": p["id"], "path": p["path"], "q": p.get("q"), "status": st, "summary": summ, "file": "evidence/" + name})
    print(st, p["id"], summ)
json.dump(res, open(OUT / "probe_results.json", "w"), indent=1)
