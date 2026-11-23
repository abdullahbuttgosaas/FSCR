"""Minimal Fusion REST caller that decodes gzip error bodies (FSCR's fusion_rest_client prints them compressed).
Reuses FSCR's own properties and token cache via fusion_auth.py; never prints the token.
Usage: rest_diag.py METHOD /path [body.json] [--out file] [--query k=v ...] [--header K:V ...]"""
import gzip, json, sys, urllib.request, urllib.parse, urllib.error
from pathlib import Path
R = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01\fscr-work")
sys.path.insert(0, str(R / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa

args = sys.argv[1:]
method, path = args[0], args[1]
body, out, query, headers = None, None, [], {}
i = 2
while i < len(args):
    a = args[i]
    if a == "--out": out = args[i + 1]; i += 2
    elif a == "--query": query.append(tuple(args[i + 1].split("=", 1))); i += 2
    elif a == "--header": k, v = args[i + 1].split(":", 1); headers[k.strip()] = v.strip(); i += 2
    else: body = Path(a).read_bytes(); i += 1
props = fa.oauth_service_properties(fa.read_properties(R / "core/auth/fusionEnv.properties"), "standard")
token = fa.load_cached_access_token(props)
if not token:
    sys.exit("TOKEN_EXPIRED: run fusion_login.py")
url = props["restBaseUrl"].rstrip("/") + path + (("?" + urllib.parse.urlencode(query)) if query else "")
req = urllib.request.Request(url, data=body, method=method)
req.add_header("Authorization", "Bearer " + token)
req.add_header("REST-Framework-Version", "9")
req.add_header("Accept-Encoding", "identity")
if body is not None:
    req.add_header("Content-Type", headers.pop("Content-Type", "application/json"))
for k, v in headers.items():
    req.add_header(k, v)
def decode(raw, enc):
    if enc == "gzip" or raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")
try:
    with urllib.request.urlopen(req, timeout=180) as r:
        status, text = r.status, decode(r.read(), r.headers.get("Content-Encoding"))
except urllib.error.HTTPError as e:
    status, text = e.code, decode(e.read(), e.headers.get("Content-Encoding"))
print("HTTP", status)
if out:
    Path(out).write_text(text, encoding="utf-8"); print("wrote", out)
else:
    print(text[:6000])
