"""The page's real server code on its own port with Oracle stubbed, for the redesign screenshots. Nothing reaches
Oracle: the sign-in check, Oracle's today and the folder scripts are replaced; the sheet check is the page's own
offline check plus the folders' read-only checks through demo_stub.py (with a short delay, so the "Checking" stage
can be seen). Run: python page/_work/redesign/demo/demo_server.py [port]"""
import http.server
import os
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [str(ROOT / "page"), str(ROOT)]
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8797
os.environ.setdefault("DEMO_DELAY", "2.5")
sys.argv = ["server.py"]
import run_summary  # noqa: E402
import server  # noqa: E402

WORK = HERE / "work"
WORK.mkdir(exist_ok=True)
server.WORK, server.LOGS, server.SERVER_LOG = WORK, WORK / "logs", WORK / "server.log"
run_summary.SERVER_LOG, run_summary.LOGS = WORK / "server.log", WORK / "logs"
server.session_valid = lambda *a, **k: {"valid": True}
server.oracle_today = lambda *a, **k: "2026-10-26"
server.setup_quick = lambda *a, **k: True
server.claude_status = lambda *a, **k: {"installed": True, "signed_in": True, "signing_in": False}
server.claude_status_cached = server.claude_status
os.environ["MATRIX_WORK"] = str(WORK)                 # the Claude stub writes its call log there
server.ENV_CHILD["MATRIX_WORK"] = str(WORK)
server.find_claude = lambda *a, **k: "stub"           # Claude's tool replaced too (proposal and repair)
server.claude_command = lambda cli: [server.PY, str(ROOT / "page" / "matrix" / "stub_claude.py")]
STUB = str(HERE / "demo_stub.py")
for name in ("Customers", "Order Types", "Payment Terms", "Lookup types", "Business Units", "Price Lists"):
    server.FOLDERS[name] = {"name": name, "script": STUB, "spec": {"fields": []}, "error": None}


def demo_check_upload(data, file_name):
    """The page's own offline sheet check, then the folders' read-only checks (demo stub), as full_check does."""
    uid = server.uuid.uuid4().hex[:10]
    with server.LOCK:
        server.UPLOADS[uid] = {"preview": None, "file": file_name, "at": time.time(), "job": None, "data": data}
    time.sleep(float(os.environ.get("DEMO_CHECK_SECONDS") or 6))
    res = server.offline_check(data, "2026-10-26", None)
    if res["records"] and not res["stops"]:
        for r, got in zip(res["records"], server.oracle_checks(res["records"])):
            server.apply_oracle_check(res, r, got)
    for r in res["records"]:
        r["ok"] = not r["problems"]
    res["ok"] = bool(res["records"]) and not res["stops"] and not res["problems"]
    with server.LOCK:
        server.UPLOADS[uid]["preview"] = res
    server.log(f"upload {uid} ({file_name}): {'ready' if res['ok'] else 'not ready'}, {len(res['records'])} record(s), "
               f"{len(res['problems'])} problem(s), {len(res['stops'])} stop(s), checked in 6 s")
    return uid, res


server.check_upload = demo_check_upload
srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), server.Handler)
threading.Thread(target=server.worker, daemon=True).start()
print(f"demo page at http://127.0.0.1:{PORT} (Oracle stubbed)", flush=True)
srv.serve_forever()
