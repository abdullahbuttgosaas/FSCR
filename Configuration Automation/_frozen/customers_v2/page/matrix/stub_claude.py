"""Stub for Claude's command-line tool (claude -p --output-format stream-json ...), for the offline matrix.
A repair prompt -> "no_change_needed" (the page then reruns the request); a proposal prompt -> the field whose
value is UNKNOWN_ME, with the value CLAUDE_FIX. Prints a "result" event with usage and cost like the real tool,
and records its command line, so the test can check the limits it was started with."""
import json
import os
import re
import sys
from pathlib import Path

prompt = sys.stdin.read()
(Path(os.environ.get("MATRIX_WORK") or Path(__file__).parent) / "claude_calls.jsonl").open("a", encoding="utf-8").write(
    json.dumps({"argv": sys.argv[1:], "proposal": prompt.startswith("PROPOSE A VALUE")}) + "\n")
if prompt.startswith("PROPOSE A VALUE"):
    req = json.loads(re.search(r"The request the page sent \(JSON\): (\{.*?\})\n\nFields", prompt, re.S).group(1))
    out = {"field": None, "value": "CLAUDE_FIX", "row": None, "why": "The stub proposes a value that works."}
    for k, v in req.items():
        if v == "UNKNOWN_ME":
            out["field"] = k
        elif isinstance(v, list):
            for n, row in enumerate(v, 1):
                for k2, v2 in (row.items() if isinstance(row, dict) else []):
                    if v2 == "UNKNOWN_ME":
                        out.update(field=k2, row=n)
else:
    out = {"status": "no_change_needed", "ask_kind": "none", "message": "It was a temporary problem (stub)."}
print(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "looking"}]}}), flush=True)
print(json.dumps({"type": "result", "total_cost_usd": 0.0123,
                  "usage": {"input_tokens": 120, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 2400,
                            "output_tokens": 60},
                  "structured_output": out}), flush=True)
