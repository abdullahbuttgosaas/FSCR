"""Run 30 REST helper (from Run 25). Never prints the token."""
import gzip, json, sys, urllib.request, urllib.parse, urllib.error
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
W = RUN.parent / "fscr-main" / "core"
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
    req.add_header("Authorization", "Bearer " + token()); req.add_header("REST-Framework-Version", "4"); req.add_header("Accept-Encoding", "identity")
    if data is not None: req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req, timeout=180) as r: raw, st = r.read(), r.status
    except urllib.error.HTTPError as e: raw, st = e.read(), e.code
    except urllib.error.URLError as e: return 0, str(e.reason)
    if raw[:2] == b"\x1f\x8b": raw = gzip.decompress(raw)
    return st, raw.decode("utf-8", "replace")
if __name__ == "__main__":
    a = sys.argv[1:]
    m, p = a[0], a[1]; q = json.loads(a[2]) if len(a) > 2 and a[2] else None
    api = a[3] if len(a) > 3 else "fscmRestApi"
    body = open(a[4], encoding="utf-8").read() if len(a) > 4 else None
    st, t = call(m, p, q, body, api=api); print(st); print(t[:int(__import__('os').environ.get('MAXC', '3000'))])
