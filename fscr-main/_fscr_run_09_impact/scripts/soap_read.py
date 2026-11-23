"""Read-only SOAP call for Run 03. Only allows get*/find* operations (hard rule 1).
Why: FSCR's customer_soap_read hides SOAP fault text by design ("CUSTOMER_SOAP_HTTP_500"), so the exact
Oracle reason for a failed read cannot be recorded through it. Token from FSCR's cache; never printed.
Usage: soap_read.py <service path e.g. /fscmService/ReceivablesCustomerProfileService> <body.xml> <out.xml>"""
import gzip, re, sys, urllib.request, urllib.error
from pathlib import Path

W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_09_impact\fscr-work9")
sys.path.insert(0, str(W / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa

svc, body_file, out = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
body = body_file.read_text(encoding="utf-8")
ops = re.findall(r"<(?:\w+:)?(\w+)[ >]", body.split("Body>", 1)[1]) if "Body>" in body else []
if not ops or not re.match(r"(get|find)", ops[0]):
    sys.exit(f"READ_ONLY: first body element must be get*/find*, got {ops[:1]}")
props = fa.oauth_service_properties(fa.read_properties(W / "core/auth/fusionEnv.properties"), "standard")
token = fa.load_cached_access_token(props)
if not token:
    sys.exit("TOKEN_EXPIRED")
req = urllib.request.Request(props["restBaseUrl"].rstrip("/") + svc, data=body.encode("utf-8"), method="POST")
req.add_header("Authorization", "Bearer " + token)
req.add_header("Content-Type", "text/xml; charset=utf-8")
req.add_header("Accept-Encoding", "identity")
try:
    with urllib.request.urlopen(req, timeout=120) as r:
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
m = re.search(r"<faultstring>(.*?)</faultstring>", text, re.S)
print("HTTP", st, ops[0], "fault:", (m.group(1).strip()[:600] if m else None), "->", out.name)
