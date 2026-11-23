"""Single PATCH to one whitelisted FSCRT record (Run 03 own call). Never DELETE, POST or PUT.
Why: FSCR has no route to edit an existing price list (its only price-list skill is an FBDI import that
cannot run in this pod). The whitelist enforces hard rule 1: only the named FSCRT records can be changed.
No automatic retry. Token from FSCR's cache (never printed). Writes Oracle's response to --out.
Usage: rmut.py <whitelist key> <body.json> --out <file>"""
import gzip, json, sys, urllib.request, urllib.error
from pathlib import Path

W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_03_change\fscr-work3")
sys.path.insert(0, str(W / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa

ALLOWED = {  # exact target records named in the Run 03 brief
    "pl_brindle": "/fscmRestApi/resources/11.13.18.05/priceLists/300000394623080",
}
key, body_file = sys.argv[1], Path(sys.argv[2])
out = Path(sys.argv[sys.argv.index("--out") + 1])
if key not in ALLOWED:
    sys.exit(f"NOT_WHITELISTED: {key}")
body = body_file.read_bytes()
json.loads(body)
props = fa.oauth_service_properties(fa.read_properties(W / "core/auth/fusionEnv.properties"), "standard")
token = fa.load_cached_access_token(props)
if not token:
    sys.exit("TOKEN_EXPIRED")
req = urllib.request.Request(props["restBaseUrl"].rstrip("/") + ALLOWED[key], data=body, method="PATCH")
for k, v in (("Authorization", "Bearer " + token), ("Content-Type", "application/json"),
             ("REST-Framework-Version", "9"), ("Accept-Encoding", "identity")):
    req.add_header(k, v)
try:
    with urllib.request.urlopen(req, timeout=180) as r:
        st, raw = r.status, r.read()
except urllib.error.HTTPError as e:
    st, raw = e.code, e.read()
except urllib.error.URLError as e:
    sys.exit(f"TRANSPORT_ERROR (nothing received): {e.reason}")
if raw[:2] == b"\x1f\x8b":
    raw = gzip.decompress(raw)
text = raw.decode("utf-8", "replace")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(text, encoding="utf-8")
print("PATCH", ALLOWED[key], "HTTP", st, "->", out.name)
if st >= 300:
    print(text[:1500])
