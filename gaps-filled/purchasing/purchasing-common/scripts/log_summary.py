#!/usr/bin/env python3
"""Print the status lines of an FSM setup import/export process log, without user or environment names.

Usage: python3 log_summary.py [--full] <process_log.txt> [...]   (--full: do not cut long error lines)

Keeps only business-object / detail-object status lines, error lines and the totals. Drops "Submitted By",
environment and package names. Local files only: no sign-in, no network.
"""
import re
import sys

KEEP = re.compile(r"(Business object:|Detail Object:|Total Objects|error|Error|JBO-|ORA-|failed|required|invalid)")


LIMIT = 400


def main() -> int:
    global LIMIT
    if "--full" in sys.argv:
        sys.argv.remove("--full")
        LIMIT = 100000
    for path in sys.argv[1:]:
        text = open(path, encoding="utf-8", errors="replace").read()
        text = text.replace("\\r\\n", "\n").replace("\\t", " ").replace("\\/", "/")
        pid = re.findall(r"_(\d{6,})_process_log", path)
        print(f"[log] ProcessId {pid[0] if pid else '?'}")
        for line in text.splitlines():
            line = re.sub(r"Submitted By: \S+", "", line)
            if re.search(r"Environment:|environment |Submitted By", line):
                continue
            if KEEP.search(line) and line.strip():
                print("  " + line.strip()[:LIMIT])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
