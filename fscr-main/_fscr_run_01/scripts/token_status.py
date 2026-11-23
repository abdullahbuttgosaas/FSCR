"""Report whether FSCR's cached OAuth token is usable, without printing it. Read-only."""
import sys, time, json
from pathlib import Path
R = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01\fscr-work")
sys.path.insert(0, str(R / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa
props = fa.oauth_service_properties(fa.read_properties(R / "core/auth/fusionEnv.properties"), sys.argv[1] if len(sys.argv) > 1 else "standard")
p = fa.token_cache_path(props)
try:
    data = fa.read_private_json(p)
    left = int(data.get("expires_at", 0)) - int(time.time())
    print(json.dumps({"cache_exists": True, "seconds_left": left, "usable": fa.cached_access_token(data, props) is not None}))
except FileNotFoundError:
    print(json.dumps({"cache_exists": False}))
