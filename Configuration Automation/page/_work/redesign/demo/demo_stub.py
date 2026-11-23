"""Demo stand-in for every folder script (Oracle replaced), for the redesign screenshots. Same command line as a
folder: --plan / --answer-check '<list>' (the preview's checks with "Oracle") and --run / --run-batch (the run).
Preview problems: a Payment Term Rank 5 (in use), a Business Unit Location "Lahor" (not a location).
Run: payment term NET30_ZZ is refused once for Months Ahead 0 (installment 1) until it gets another value."""
import json
import os
import sys
import time
from pathlib import Path

DELAY = float(os.environ.get("DEMO_DELAY") or 0)


def plan(r):
    probs = []
    if str(r.get("rank") or "") in ("5", "5.0"):
        probs.append({"key": "rank", "text": "Rank 5 is already used by payment term NET 45; Oracle allows each rank on "
                      "one payment term only.", "fix": "Use a rank no other term has, for example 6, or leave Rank empty."})
    if r.get("location") == "Lahor":
        probs.append({"key": "location", "text": "Oracle has no Location called 'Lahor'.",
                      "fix": "Pick one of: Go Saas Lahore Office, Karachi Office, Dallas HQ."})
    if any(v == "BAD_TYPED" for v in r.values()):
        probs.append({"key": "x", "text": "Oracle has no value 'BAD_TYPED'.", "fix": "Pick another value."})
    for row in r.get("installments") or []:
        if row.get("months_ahead") == "BAD_TYPED":
            probs.append({"key": "installments", "row": 1, "text": "Oracle has no value 'BAD_TYPED'.", "fix": "Use 0 or more."})
    return {"ok": True, "problems": probs, "found": {}, "fills": {}, "skipped": None}


def run_one(r):
    if DELAY:
        time.sleep(DELAY)
    name = str(r.get("name") or r.get("code") or r.get("lookup_type") or "record")
    refused = lambda field, value, reason, sugg, rows=None, row=None, where=None: {
        "ok": False, "text": f"Oracle refused {name}: {reason} Nothing was saved in Oracle.",
        "error": {"code": "INVALID_REQUEST", "step": "creating", "detail": {
            "message": reason, "saved": "no", "registry_id": None, "problems": [dict(
                {"field": field, "value": value, "reason": reason, "text": reason, "suggestions": sugg},
                **({"rows": rows, "row": row, "where": where} if rows else {}))]}}}
    if name == "RUSH_FLAKY":                         # a script failure once: the automatic repair runs
        flag = Path(__file__).parent / "work" / "flags" / "RUSH_FLAKY"
        if not flag.exists():
            flag.parent.mkdir(parents=True, exist_ok=True)
            flag.write_text("1")
            return {"ok": False, "text": "Something went wrong. Nothing was saved in Oracle.",
                    "error": {"code": "STEP_FAILED", "step": "creating",
                              "detail": {"message": "Timeout waiting for the Save button (demo)", "saved": "no"}}}
    if name == "RETURN_ORDER" and r.get("meaning") == "Return Order":
        return refused("meaning", "Return Order", "Another order type (RETURNS) already uses the name 'Return Order'.",
                       ["Return Order (RETURN_ORDER)", "Return Order 2"])
    if r.get("description") == "UNKNOWN_ME":         # a refusal no rule knows: Claude proposes a value
        reason = "ORA-20001: this description isn't accepted for this payment term (demo)."
        return {"ok": False, "text": f"Oracle refused the payment term {name}: {reason} Nothing was saved in Oracle.",
                "error": {"code": "INVALID_REQUEST", "step": "creating",
                          "detail": {"message": reason, "saved": "no", "registry_id": None}}}
    codes = r.get("codes") or []
    if codes and codes[0].get("meaning") == "Late delivery":
        return refused("meaning", "Late delivery", "Lookup Type ZZ_ORDER_REASON already has lookup code meaning Late "
                       "delivery. (FND-7103)", ["Late delivery (LATE)", "Late delivery 2"], "codes", 1, "Code 1 (LATE)")
    if name == "Dallas BU":                          # not created, and not a value the user can change
        return {"ok": False, "text": "Your Oracle user has no permission to create business units here. Nothing was "
                                     "saved in Oracle.",
                "error": {"code": "NO_PERMISSION", "step": "creating",
                          "detail": {"message": "HTTP 403 (demo)", "saved": "no", "registry_id": None}}}
    if name == "NET30_ZZ":
        rows = r.get("installments") or []
        if rows and str(rows[0].get("months_ahead")) in ("0", "None", ""):
            reason = "You must enter months ahead when Day of Month is used."
            return {"ok": False, "text": f"Oracle refused the payment term {name}: {reason} Nothing was saved in Oracle.",
                    "error": {"code": "INVALID_REQUEST", "step": "creating", "detail": {
                        "message": reason, "saved": "no", "registry_id": None, "problems": [{
                            "field": "months_ahead", "value": rows[0].get("months_ahead"), "reason": reason, "text": reason,
                            "suggestions": ["1", "2", "3"], "rows": "installments", "row": 1, "where": "Installment 1"}]}}}
    return {"ok": True, "text": f"Created {name} in Oracle and checked every value.", "created": None, "where": "demo"}


cmd, raw = sys.argv[1], json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
if cmd in ("--plan", "--answer-check"):
    reqs = raw if isinstance(raw, list) else [raw]
    print(json.dumps({"ok": True, "results": [plan(r) for r in reqs]}))
elif cmd == "--run":
    print(json.dumps(dict(run_one(raw), step="result", percent=100)))
elif cmd == "--run-batch":
    print(json.dumps({"step": "creating", "percent": 50, "text": "Creating them in Oracle"}), flush=True)
    res = [run_one(r) for r in raw]
    print(json.dumps({"step": "result", "percent": 100, "ok": all(x["ok"] for x in res), "text": "demo", "results": res}))
