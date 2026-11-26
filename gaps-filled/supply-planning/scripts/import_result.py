"""Safe summary of an FSCR task-level import: result, counts and Oracle's error messages, nothing private.

Usage: python import_result.py <import output folder>
Reads the *_process_log.txt that shared/setup-import/task-level-import wrote into that folder (the newest one).
Never prints the environment name, server addresses or user names: it prints only fixed status phrases, counts,
and Oracle error codes with their message text (FND_..., JBO-..., up to 200 characters, addresses removed).
Last line: RESULT: SUCCESS (no failed objects or rows) or RESULT: ERRORS.
Local files only; no sign-in, no network.
"""
import collections
import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    logs = sorted(Path(sys.argv[1]).glob("*_process_log.txt"), key=lambda p: p.stat().st_mtime)
    if not logs:
        sys.exit(f"No *_process_log.txt in {sys.argv[1]}")
    text = logs[-1].read_text(encoding="utf-8", errors="replace").replace("\\r\\n", "\n").replace("\\t", " ")
    text = re.sub(r"https?://\S+", "<url>", text)
    phrases = collections.Counter(re.findall(r"Completed successfully|Completed with errors|In progress", text))
    for p, n in phrases.items():
        print(f"{n} x {p}")
    for label in ("Total Objects Failed", "Total Objects Completed"):
        for v in re.findall(label + r":\s*(\d+)", text):
            print(f"{label}: {v}")
    for m in re.findall(r"A total of (\d+) rows were processed\. (\d+) rows of them failed", text):
        print(f"rows processed {m[0]}, failed {m[1]}")
    errors = collections.OrderedDict()
    clean = re.sub(r"<[^>]*>", " ", text)
    for m in re.finditer(r"(?=((?:FND_[A-Z_]+|JBO-\d+)[:\s][^\n]{0,400}))", clean):
        msg = re.split(r"(?<=.)(?=FND_[A-Z_]+:|JBO-\d+:|\bat oracle\.)", m.group(1))[0]
        msg = re.sub(r"\s+", " ", msg).strip()[:200]
        if not re.search(r"(?i)user ?name:|submitted|created by", msg):
            errors.setdefault(msg, 0)
            errors[msg] += 1
    for msg, n in errors.items():
        print(f"error ({n}x): {msg}")
    failed = "Completed with errors" in phrases or any(int(v) > 0 for v in re.findall(r"Total Objects Failed:\s*(\d+)", text)) \
        or any(int(f) > 0 for _, f in re.findall(r"A total of (\d+) rows were processed\. (\d+) rows of them failed", text))
    print("RESULT: ERRORS" if failed or errors else "RESULT: SUCCESS")


if __name__ == "__main__":
    main()
