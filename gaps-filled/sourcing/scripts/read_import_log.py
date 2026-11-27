"""Added by GoSaaS, not part of official FSCR. Gap fill, Procurement, 2026-11-25. Offline: no Oracle call.

Reads an FSCR setup-task CSV import process log safely. The log is one long line with literal \\r\\n and holds
the environment name and the "Submitted By" user name; this prints ONLY the result lines (business object status,
rows processed / failed, totals, Oracle message codes and texts, JBO/ORA errors). Never prints user names.

Usage: python -I read_import_log.py <RUN>/import_result      (a folder with one *_process_log.txt, or the file)
Exit 0 and "IMPORT: PASS" when every object completed successfully and 0 rows failed; else "IMPORT: FAIL".
"""
import glob
import re
import sys
from pathlib import Path

PAT = (r"Business object: [^.]+\. Status: [^.]+|A total of [0-9]+ rows were processed\. [0-9]+ rows of them failed"
       r"|Total Objects \w+: [0-9]+|Message Code: [A-Z_0-9]+\. Message Text: [^.]{0,200}"
       r"|JBO-[0-9]+: [^.]{0,200}|ORA-[0-9]+: [^.]{0,160}")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    p = Path(sys.argv[1])
    files = [p] if p.is_file() else [Path(f) for f in glob.glob(str(p / "*_process_log.txt"))]
    if len(files) != 1:
        print(f"IMPORT: FAIL (found {len(files)} process logs; need exactly 1)")
        return 1
    t = files[0].read_text(encoding="utf-8").replace("\\r\\n", "\n").replace("\\t", " ").replace("\\/", "/")
    hits = []
    for m in re.findall(PAT, t):
        if m not in hits:
            hits.append(m)
    for h in hits:
        print(h)
    st = [h for h in hits if h.startswith("Business object:")]
    rows = [h for h in hits if h.startswith("A total of")]
    ok = (st and all(h.endswith("Completed successfully") for h in st)
          and rows and all(re.search(r"\. 0 rows of them failed$", h) for h in rows))
    print("IMPORT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
