"""Stub for a configuration folder's script (Oracle replaced), for the offline behaviour matrix.
Same command line as a real folder: --run '<request>' / --run-batch '<list>' / --plan | --answer-check '<list>'.
Markers in any request value decide what "Oracle" does:
  REFUSE_ME   -> a value refusal the folder recognises (structured problem with suggestions GOOD_1, GOOD_2)
  UNKNOWN_ME  -> a refusal no rule recognises (INVALID_REQUEST, saved "no", no problems)
  FLAKY_ME    -> the first try fails for a script reason (FAILED, saved "no"), later tries work
  BAD_TYPED   -> refused by the read-only check (--plan / --answer-check)
  CHECK_FAILS -> the read-only check can't run at all: {"ok": false, "text": <a real failed step>} (2026-10-26)
  CHECK_FLAKY -> the same on its first call only; later calls answer (each call is counted in flags/check_calls)
The page's test switch (no browser) -> every record fails for a script reason."""
import json
import os
import sys
from pathlib import Path

FLAGS = Path(os.environ.get("MATRIX_WORK") or Path(__file__).parent) / "flags"


def walk(req):
    """(field, value, rows_key, row) for every value of the request, child rows included."""
    for k, v in req.items():
        if isinstance(v, list):
            for n, row in enumerate(v, 1):
                if isinstance(row, dict):
                    for k2, v2 in row.items():
                        yield k2, v2, k, n
        else:
            yield k, v, None, None


def name_of(req):
    return str(req.get("name") or req.get("code") or req.get("lookup_type") or "record")


def result_for(req):
    if str(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "")).endswith("no-browser-here"):
        return {"ok": False, "text": "Something went wrong. Nothing was saved in Oracle.",
                "error": {"code": "FAILED", "step": "checking",
                          "detail": {"message": "BrowserType.launch: Executable doesn't exist", "saved": "no"}}}
    for field, value, rows, n in walk(req):
        if value == "FLAKY_ME" or field == "flaky":
            FLAGS.mkdir(exist_ok=True)
            flag = FLAGS / f"{name_of(req)}.flaky"
            if not flag.exists():
                flag.write_text("1")
                return {"ok": False, "text": "Something went wrong. Nothing was saved in Oracle.",
                        "error": {"code": "STEP_FAILED", "step": "creating",
                                  "detail": {"message": "Timeout 30000ms waiting for the Save button (stub)",
                                             "saved": "no"}}}
        if value == "REFUSE_ME":
            p = {"field": field, "value": value, "reason": f"Oracle has no value '{value}' (stub).",
                 "text": f"Oracle has no value '{value}' (stub).", "suggestions": ["GOOD_1", "GOOD_2"]}
            if rows:
                p.update(rows=rows, row=n, where=f"Row {n}")
            return {"ok": False, "text": f"Oracle refused {name_of(req)}: {p['reason']} Nothing was saved in Oracle.",
                    "error": {"code": "INVALID_REQUEST", "step": "creating",
                              "detail": {"message": p["reason"], "saved": "no", "registry_id": None, "problems": [p]}}}
        if value == "UNKNOWN_ME":
            msg = "ORA-99999: a rule nobody has written down yet refused this (stub)."
            return {"ok": False, "text": f"Oracle refused {name_of(req)}: {msg} Nothing was saved in Oracle.",
                    "error": {"code": "INVALID_REQUEST", "step": "creating",
                              "detail": {"message": msg, "saved": "no", "registry_id": None}}}
    return {"ok": True, "text": f"Created {name_of(req)} (stub) and checked it.", "created": dict(req),
            "where": "stub"}


def main():
    cmd, raw = sys.argv[1], json.loads(sys.argv[2])
    if cmd in ("--plan", "--answer-check"):
        reqs = raw if isinstance(raw, list) else [raw]
        marks = {v for r in reqs for _, v, _, _ in walk(r)}
        if marks & {"CHECK_FAILS", "CHECK_FLAKY"}:
            FLAGS.mkdir(exist_ok=True)
            with open(FLAGS / "check_calls", "a", encoding="utf-8") as f:
                f.write(name_of(reqs[0]) + "\n")
            flag = FLAGS / f"{name_of(reqs[0])}.check"
            if "CHECK_FAILS" in marks or not flag.exists():
                flag.write_text("1")
                print(json.dumps({"ok": False, "text": "Oracle's Setup page did not open Create Customer after 3 tries"}))
                sys.exit(1)
        res = []
        for r in reqs:
            bad = [(f, v) for f, v, _, _ in walk(r) if v == "BAD_TYPED"]
            res.append({"ok": True, "problems": [{"key": f, "text": f"Oracle has no value '{v}' (stub check).",
                                                  "fix": "Pick another value."} for f, v in bad],
                        "found": {}, "fills": {}, "skipped": None})
        print(json.dumps({"ok": True, "results": res}))
        return
    print(json.dumps({"step": "reading", "percent": 5, "text": "Reading your request"}), flush=True)
    if cmd == "--run":
        print(json.dumps(dict(result_for(raw), step="result", percent=100)))
    elif cmd == "--run-batch":
        results = [result_for(r) for r in raw]
        line = {"step": "result", "percent": 100, "ok": all(r["ok"] for r in results), "text": "stub batch",
                "results": results}
        if results and all((r.get("error") or {}).get("code") == "FAILED" for r in results):
            line["error"] = {"code": "FAILED", "step": "checking", "detail": "BrowserType.launch failed (stub)"}
        print(json.dumps(line))


if __name__ == "__main__":
    main()
