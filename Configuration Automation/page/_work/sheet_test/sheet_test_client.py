"""Drive the sheet test server through the page's own HTTP calls, as the page's screen does: upload (= check and
preview), then optionally "Create in Oracle" and follow the run to its end.

  python sheet_test_client.py <port> <workbook.xlsx> <out.json> check|create
"""
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

port, wb, out, mode = int(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4]
URL = f"http://127.0.0.1:{port}"
now = lambda: datetime.now().strftime("%H:%M:%S")
rep = {"file": wb.name}


def call(path, data=None, headers=None, timeout=60):
    req = urllib.request.Request(URL + path, data=data, headers=headers or {}, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


def save():
    out.write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")


for _ in range(120):                      # the folders' specs load in the background at start
    st, s = call("/api/sheet/modules")
    if st == 200 and len(s.get("modules", s) if isinstance(s, dict) else s) >= 4:
        break
    time.sleep(2)
time.sleep(5)
rep["check_start"], t0 = now(), time.time()
st, pv = call("/api/sheet/upload", wb.read_bytes(), {"X-File-Name": wb.name,
                                                       "Content-Type": "application/octet-stream"}, timeout=1800)
rep["check_end"], rep["check_seconds"] = now(), round(time.time() - t0)
rep["upload_http"] = st
rep["preview"] = {k: pv.get(k) for k in ("ok", "stops", "notes", "oracle_stops", "signin")}
rep["preview"]["problems_count"] = len(pv.get("problems") or [])
rep["modules"] = [(m.get("name"), m.get("count"), m.get("text")) for m in pv.get("modules") or []]
rep["records"] = [{"group": r.get("group"), "name": r.get("name"), "ok": r.get("ok"), "skipped": r.get("skipped"),
                   "summary": r.get("oracle_summary") or r.get("summary"),
                   "problems": [p.get("text") for p in r.get("problems") or []],
                   "notes": [f.get("note") for f in r.get("fields") or [] if f.get("note")]}
                  for r in pv.get("records") or []]
uid = pv.get("id") or pv.get("upload")
rep["upload"] = uid
save()
if mode == "check":
    st, res = call("/api/sheet/create", json.dumps({"upload": uid}).encode(), {"Content-Type": "application/json"})
    rep["create_attempt"] = {"http": st, "answer": res}
    save()
    print(json.dumps({k: rep[k] for k in ("check_seconds", "preview", "create_attempt")}, ensure_ascii=False))
    sys.exit(0)
if not pv.get("ok"):
    rep["stopped"] = "the check is not clean: Create not pressed"
    save()
    print(json.dumps(rep, ensure_ascii=False)[:3000])
    sys.exit(2)
rep["create_start"], t1 = now(), time.time()
st, res = call("/api/sheet/create", json.dumps({"upload": uid}).encode(), {"Content-Type": "application/json"})
rep["create_http"], jid = st, res.get("id")
rep["job"], rep["progress"], last = jid, [], None
while jid:
    st, j = call(f"/api/job/{jid}")
    line = (j.get("state"), j.get("text"), json.dumps([(it.get("name"), it.get("state"), it.get("hold_text"))
                                                       for it in j.get("items", [])]))
    if line != last:
        rep["progress"].append({"at": now(), "state": j.get("state"), "text": j.get("text"),
                                "items": [(it.get("name"), it.get("state"), it.get("hold_text"))
                                          for it in j.get("items", [])]})
        last = line
        save()
    if j.get("state") in ("done", "failed", "asking", "needs_user"):
        break
    if time.time() - t1 > 2700:
        rep["stopped"] = "not finished in 45 minutes"
        break
    time.sleep(3)
rep["create_end"], rep["create_seconds"] = now(), round(time.time() - t1)
rep["job_final"] = j if jid else res
save()
print(json.dumps({k: rep.get(k) for k in ("check_seconds", "create_seconds", "create_http")}))
