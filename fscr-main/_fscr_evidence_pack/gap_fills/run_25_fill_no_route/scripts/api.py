"""Run 25 helper. Never prints the token."""
import gzip, json, sys, urllib.request, urllib.parse, urllib.error, base64, time
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
W = RUN / "work"
sys.path.insert(0, str(W / "auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa
props = fa.oauth_service_properties(fa.read_properties(W / "auth/fusionEnv.properties"), "standard")
def token():
    t = fa.load_cached_access_token(props)
    if not t: sys.exit("TOKEN_EXPIRED")
    return t
def call(method, path, q=None, body=None, ctype="application/json", accept=None, raw_url=False):
    base = props["restBaseUrl"].rstrip("/")
    url = (base + path) if raw_url else (base + "/fscmRestApi/resources/11.13.18.05/" + path)
    if q: url += "?" + urllib.parse.urlencode(q)
    data = body.encode("utf-8") if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token()); req.add_header("REST-Framework-Version", "9"); req.add_header("Accept-Encoding", "identity")
    if data is not None: req.add_header("Content-Type", ctype)
    if accept: req.add_header("Accept", accept)
    try:
        with urllib.request.urlopen(req, timeout=180) as r: raw, st = r.read(), r.status
    except urllib.error.HTTPError as e: raw, st = e.read(), e.code
    except urllib.error.URLError as e: return 0, str(e.reason)
    if raw[:2] == b"\x1f\x8b": raw = gzip.decompress(raw)
    return st, raw.decode("utf-8", "replace")
if __name__ == "__main__":
    st, t = call("GET", "setupTaskCSVImports", {"limit": 1, "onlyData": "true"})
    print(st, t[:200])
