"""Run 35 REST helper (from Run 33/34). Never prints the token. ETIA-TEST only."""
import gzip, json, os, sys, time, urllib.request, urllib.parse, urllib.error
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
WORK = Path(r"C:/Users/PC/AppData/Local/Temp/claude/537d324d8fa4a5c1/7ac3c756-7f84-4cc1-8a73-06733818bf7d/scratchpad/fscr-work35")
W = WORK / "core"
sys.path.insert(0, str(W / "auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa
props = fa.oauth_service_properties(fa.read_properties(W / "auth/fusionEnv.properties"), "standard")
assert props["restBaseUrl"].startswith("https://fa-etia-test"), "ETIA-TEST only"
def token():
    t = fa.load_cached_access_token(props)
    if not t: sys.exit("TOKEN_EXPIRED")
    return t
def call(method, path, q=None, body=None, ctype="application/json", api="fscmRestApi"):
    base = props["restBaseUrl"].rstrip("/")
    url = base + path if path.startswith("/") else f"{base}/{api}/resources/11.13.18.05/{path}"
    if q: url += "?" + urllib.parse.urlencode(q)
    if isinstance(body, (dict, list)): body = json.dumps(body)
    data = body.encode("utf-8") if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token()); req.add_header("REST-Framework-Version", os.environ.get("FW", "4")); req.add_header("Accept-Encoding", "identity")
    if data is not None: req.add_header("Content-Type", ctype)
    for attempt in range(8):   # retry ONLY when DNS failed (request never left the machine, so it is safe to resend)
        try:
            with urllib.request.urlopen(req, timeout=180) as r: raw, st = r.read(), r.status
            break
        except urllib.error.HTTPError as e: raw, st = e.read(), e.code; break
        except urllib.error.URLError as e:
            if "getaddrinfo" in str(e.reason) and attempt < 7: time.sleep(3); continue
            return 0, str(e.reason)
    if raw[:2] == b"\x1f\x8b": raw = gzip.decompress(raw)
    return st, raw.decode("utf-8", "replace")
if __name__ == "__main__":
    a = sys.argv[1:]
    m, p = a[0], a[1]; q = json.loads(a[2]) if len(a) > 2 and a[2] else None
    api = a[3] if len(a) > 3 else "fscmRestApi"
    body = open(a[4], encoding="utf-8").read() if len(a) > 4 else None
    st, t = call(m, p, q, body, api=api); print(st); print(t[:int(os.environ.get('MAXC', '3000'))])
