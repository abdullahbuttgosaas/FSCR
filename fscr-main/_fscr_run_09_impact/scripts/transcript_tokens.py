"""Run 08: exact token usage from the session transcript (same method as earlier runs).
Each assistant response is counted once by message id; usage fields as recorded by the API.
Optional time window in local +05:00 'HH:MM:SS' bounds on 2026-11-04. Automatic summarising calls are not
recorded in the transcript, so they are not counted.  Usage: transcript_tokens.py <transcript.jsonl> [from] [to]"""
import json, sys
from datetime import datetime, timedelta, timezone

path = sys.argv[1]
tz = timezone(timedelta(hours=5))
lo = datetime.fromisoformat(f"2026-11-04T{sys.argv[2]}+05:00") if len(sys.argv) > 2 else None
hi = datetime.fromisoformat(f"2026-11-04T{sys.argv[3]}+05:00") if len(sys.argv) > 3 else None
seen, tot, first, last = {}, {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0}, None, None
for line in open(path, encoding="utf-8"):
    try:
        d = json.loads(line)
    except Exception:
        continue
    m = d.get("message") or {}
    u = m.get("usage") if isinstance(m, dict) else None
    if d.get("type") != "assistant" or not u or not m.get("id"):
        continue
    ts = datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")).astimezone(tz)
    if (lo and ts < lo) or (hi and ts > hi):
        continue
    seen[m["id"]] = (ts, u)  # last record per id carries the final usage
for ts, u in seen.values():
    tot["input"] += u.get("input_tokens", 0)
    tot["output"] += u.get("output_tokens", 0)
    tot["cache_read"] += u.get("cache_read_input_tokens", 0)
    tot["cache_write"] += u.get("cache_creation_input_tokens", 0)
    first = min(first, ts) if first else ts
    last = max(last, ts) if last else ts
print(json.dumps({"calls": len(seen), **tot, "total": sum(tot.values()),
                  "first": first and first.isoformat(), "last": last and last.isoformat()}))
