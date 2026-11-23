"""Read-only proof runs: upload a sheet to the real page N times (its own check; Create is never pressed) and
record per run: seconds, ready or not, problems, stops, and the server.log lines about retries and re-runs."""
import json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOG = ROOT / "page" / "_work" / "server.log"
sheet, n, out = Path(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
for i in range(1, n + 1):
    start_size = LOG.stat().st_size
    req = urllib.request.Request("http://127.0.0.1:8765/api/sheet/upload", data=sheet.read_bytes(), method="POST",
                                 headers={"Content-Type": "application/octet-stream", "X-File-Name": sheet.name})
    t = time.time()
    try:
        up = json.loads(urllib.request.urlopen(req, timeout=3600).read())
        err = None
    except Exception as e:  # noqa: BLE001
        up, err = {}, f"{type(e).__name__}: {e}"
    secs = round(time.time() - t)
    with open(LOG, encoding="utf-8", errors="replace") as f:
        f.seek(start_size)
        lines = [l.strip() for l in f if any(k in l for k in ("another try", "running it again", "couldn't run",
                                                              "failed (", "upload "))]
    held = [r.get("name") for r in up.get("records", []) if r.get("held")]
    row = {"run": i, "seconds": secs, "ready": up.get("ok"), "records": len(up.get("records", [])),
           "problems": [p.get("text") for p in up.get("problems", [])][:10], "stops": up.get("stops"),
           "held": held, "error": err, "log": lines}
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"run {i}: ready={row['ready']} {secs}s retries={sum('another try' in l for l in lines)} "
          f"reruns={sum('running it again' in l for l in lines)} problems={len(row['problems'])} "
          f"stops={row['stops']} held={held} err={err}", flush=True)
