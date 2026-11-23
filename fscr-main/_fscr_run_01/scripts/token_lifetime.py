"""Print only the lifetime (expires_at - saved_at) of FSCR's cached token. Read-only, prints no token."""
import sys
from pathlib import Path
R = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01\fscr-work")
sys.path.insert(0, str(R / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa
props = fa.oauth_service_properties(fa.read_properties(R / "core/auth/fusionEnv.properties"), "standard")
d = fa.read_private_json(fa.token_cache_path(props))
print("lifetime_seconds", int(d["expires_at"]) - int(d["saved_at"]))
