"""Call FSCR's own read-only customer SOAP reader (manage-customer-uploads/scripts/customer_soap_read.read)
from the Run 03 working copy and save its full result. Read operations only (getCustomerAccount,
getLocation, findOrganization, getActiveCustomerProfile); FSCR's reader has no write operation.
Usage: fscr_cust_read2.py <out.json> <operation> key=value [key=value ...]"""
import json, sys
from pathlib import Path

W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_09_impact\fscr-work9")
sys.path.insert(0, str(W / "pillars/erp/financials/customers/manage-customer-uploads/scripts"))
sys.path.insert(0, str(W / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa
import customer_soap_read as csr

out, op = Path(sys.argv[1]), sys.argv[2]
sel = dict(a.split("=", 1) for a in sys.argv[3:])
props_path = W / "core/auth/fusionEnv.properties"
props = fa.oauth_service_properties(fa.read_properties(props_path), "standard")
core = csr.load_core(W)
try:
    res = csr.read(core, props_path, fa.token_cache_path(props), props["restBaseUrl"], op, sel)
    text = json.dumps(res, indent=1, default=lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else str(b))
    status = "OK"
except Exception as e:
    text = json.dumps({"FSCR_READ_ERROR": type(e).__name__, "message": str(e)})
    status = f"FSCR_READ_ERROR {type(e).__name__} {e}"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(text, encoding="utf-8")
print(op, sel, status, len(text), "chars ->", out.name)
