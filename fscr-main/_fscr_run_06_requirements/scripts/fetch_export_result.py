"""Download the file of an already-started FSCR task export process using FSCR's own engine (read-only GET).
Why: FSCR's export script lost its status poll to a DNS error after Oracle had started process;
re-running the export would create a second export process. FSCR has no "resume by process id" option.
Usage: fetch_export_result.py <TASK_CODE> <process_id> <out.zip>"""
import sys
from pathlib import Path

W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_06_requirements\fscr-work6")
sys.path.insert(0, str(W / "shared/setup-export/fsm-csv-export/scripts"))
sys.path.insert(0, str(W / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa
import fsm_csv_export_engine as eng

task, pid, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
props = fa.oauth_service_properties(fa.read_properties(W / "core/auth/fusionEnv.properties"), "standard")
token = fa.load_cached_access_token(props)
if not token:
    sys.exit("TOKEN_EXPIRED")
scope = eng.ExportScope(kind="task", primary_code=task)
content, enclosure = eng.download_result(props, token, scope, pid)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(content)
print(f"{enclosure}: {len(content)} bytes -> {out.name}; zip={content[:2] == b'PK'}")
