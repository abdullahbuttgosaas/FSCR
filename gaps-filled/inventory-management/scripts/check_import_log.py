"""Check an FSM import process log without printing it whole.
The log is one line with literal \\r\\n and names the environment and the submitting user; this script prints only
the status lines, row counts and Oracle errors, with the environment and the submitter removed.
Usage: python check_import_log.py <process_log.txt>
Exit 0 when the import completed with 0 failed objects, else 1. Read only."""
import re, sys
t = open(sys.argv[1], encoding="utf-8", errors="ignore").read().replace("\\r\\n", "\n").replace("\\/", "/").replace("\\t", "  ")
out = []
for line in t.splitlines():
    line = line.strip()
    if not line or line.startswith(("Environment:", "Revision:", "The configuration package")):
        continue
    line = re.sub(r"Submitted By: .*?(?=\. Process Date|$)", "Submitted By: <hidden>", line)
    if re.search(r"Business object:|Detail Object:|Row Identifier:|JBO-|Total Objects|Status: Completed|required|Error", line):
        out.append(line)
print("\n".join(out))
failed = re.search(r"Total Objects Failed: (\d+)", t)
ok = failed is not None and failed.group(1) == "0" and "Completed with errors" not in t
print("IMPORT RESULT:", "OK (0 failed objects)" if ok else "NOT OK (see the lines above)")
sys.exit(0 if ok else 1)
