"""Single CustomerAccountService.updateCustomerAccount for one whitelisted FSCRT account (Run 03 own call).
Why: FSCR has no customer update route that can run here (manage-customer-uploads is FBDI-only and the pod
has no FBDI loader objects). Only the fields given are sent; Oracle's SOAP update changes only supplied
attributes. Whitelist enforces hard rule 1. No automatic retry; token never printed.
Usage: soap_update.py <account key> <fields.json> --out <file>
fields.json: {"account": {...CustomerAccount fields...}, "account_dff": {...CustAcctInformation fields...}}"""
import gzip, json, re, sys, urllib.request, urllib.error
from pathlib import Path
from xml.sax.saxutils import escape

W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_03_change\fscr-work3")
sys.path.insert(0, str(W / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa

ALLOWED = {"kestrel": "300000394607181", "linnea": "300000394593177"}  # CustomerAccountId, Run 01 state files
ACC = "http://xmlns.oracle.com/apps/cdm/foundation/parties/customerAccountService/"
DFF = "http://xmlns.oracle.com/apps/cdm/foundation/parties/flex/custAccount/"
key, fields = sys.argv[1], json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
out = Path(sys.argv[sys.argv.index("--out") + 1])
if key not in ALLOWED:
    sys.exit(f"NOT_WHITELISTED: {key}")
aid = ALLOWED[key]
acc = "".join(f"<acc:{k}>{escape(str(v))}</acc:{k}>" for k, v in fields.get("account", {}).items())
dff = ""
if fields.get("account_dff"):
    inner = "".join(f"<dff:{k}>{escape(str(v))}</dff:{k}>" for k, v in fields["account_dff"].items())
    dff = f"<acc:CustAcctInformation><dff:CustAccountId>{aid}</dff:CustAccountId>{inner}</acc:CustAcctInformation>"
env = (f'<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:typ="{ACC}applicationModule/types/" '
       f'xmlns:acc="{ACC}" xmlns:dff="{DFF}"><soapenv:Header/><soapenv:Body><typ:updateCustomerAccount><typ:customerAccount>'
       f"<acc:CustomerAccountId>{aid}</acc:CustomerAccountId>{acc}{dff}"
       "</typ:customerAccount></typ:updateCustomerAccount></soapenv:Body></soapenv:Envelope>")
props = fa.oauth_service_properties(fa.read_properties(W / "core/auth/fusionEnv.properties"), "standard")
token = fa.load_cached_access_token(props)
if not token:
    sys.exit("TOKEN_EXPIRED")
req = urllib.request.Request(props["restBaseUrl"].rstrip("/") + "/crmService/CustomerAccountService", data=env.encode("utf-8"), method="POST")
for k, v in (("Authorization", "Bearer " + token), ("Content-Type", "text/xml; charset=utf-8"), ("Accept-Encoding", "identity")):
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
(out.parent / (out.stem + "_request.xml")).write_text(env, encoding="utf-8")
out.write_text(text, encoding="utf-8")
m = re.search(r"<faultstring>(.*?)</faultstring>", text, re.S)
print("updateCustomerAccount", aid, "HTTP", st, "fault:", m.group(1).strip()[:800] if m else None, "->", out.name)
