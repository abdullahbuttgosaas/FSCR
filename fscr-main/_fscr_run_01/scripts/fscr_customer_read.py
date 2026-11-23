"""Call FSCR's own read-only customer SOAP reader (manage-customer-uploads/scripts/customer_soap_read.read) for verification."""
import json, sys
from pathlib import Path
W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01\fscr-work")
sys.path.insert(0, str(W / "pillars/erp/financials/customers/manage-customer-uploads/scripts"))
sys.path.insert(0, str(W / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa
import customer_soap_read as csr
props_path = W / "core/auth/fusionEnv.properties"
props = fa.oauth_service_properties(fa.read_properties(props_path), "standard")
core = csr.load_core(W)
op, sel = sys.argv[1], dict(a.split("=", 1) for a in sys.argv[2:])
try:
    out = csr.read(core, props_path, fa.token_cache_path(props), props["restBaseUrl"], op, sel)
    print(json.dumps(out, indent=1, default=str)[:6000])
except Exception as e:
    print("FSCR_READ_ERROR", type(e).__name__, e)
