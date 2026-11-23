"""Receivables sheet test server (2026-11-02): the page's REAL server code (page/server.py: upload, check, preview,
create, queue, dependencies, read-back cards) on a spare port, for an upload of the four Receivables modules, which
use no browser. Two things differ from `python page/server.py`, both here and not in the page's code:
  1. the saved browser sign-in check (session_valid) answers "valid" without opening a browser: it gates every upload
     check and Create, but the four Receivables modules never use the browser (Basic auth calls only), and the saved
     sign-in had expired (renewing it is a manual step the user ruled out);
  2. Claude's tool is reported "not installed", so a failure is never handed to an automatic repair (plain card
     instead), and the setup checklist (which would open the sign-in window) is not started.
Logs and uploads go to page/_work/sheet_test/, not the page's own server.log.

  python page/_work/sheet_test/sheet_test_server.py --port 8799
"""
import argparse
import http.server
import sys
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "page"), str(ROOT)]
import run_summary  # noqa: E402
import server  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--port", type=int, default=8799)
args = ap.parse_args()

WORK = HERE / "work"
WORK.mkdir(parents=True, exist_ok=True)
server.WORK, server.LOGS, server.SERVER_LOG = WORK, WORK / "logs", WORK / "server.log"
run_summary.SERVER_LOG, run_summary.LOGS = WORK / "server.log", WORK / "logs"


def _valid():
    server.log("sheet test: browser sign-in check skipped (Receivables modules use no browser)")
    return {"valid": True, "reason": "skipped by the sheet test harness"}


server.session_valid = _valid
server.claude_status = lambda *a, **k: {"installed": False, "signed_in": False, "version": None}
server.find_claude = lambda *a, **k: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), server.Handler)
server.log(f"sheet test server started at http://127.0.0.1:{args.port} (environment {server.env_label()['name']})")
threading.Thread(target=server.load_folders, daemon=True).start()
threading.Thread(target=server.worker, daemon=True).start()
print(f"ready on {args.port}", flush=True)
srv.serve_forever()
