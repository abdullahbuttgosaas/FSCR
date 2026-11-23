"""Crawl Oracle 'Implementing Procurement' 26D HTML by following 'Next' links; save pages. Read-only web GET via curl."""
import re, subprocess, pathlib
B = "https://docs.oracle.com/en/cloud/saas/procurement/26d/oapro/"
out = pathlib.Path(__file__).resolve().parents[1] / "evidence" / "oracle_docs"
cur = "index.html"; seen = []
while cur and cur not in seen and len(seen) < 400:
    seen.append(cur)
    raw = subprocess.run(["curl", "-s", "--max-time", "60", B + cur], capture_output=True).stdout.decode("utf-8", "replace")
    (out / cur).write_text(raw, encoding="utf-8")
    m = re.search(r'<link rel="next" href="([^"#]+.html)"', raw)
    if not m:
        cur = "get-help-FA.html" if cur == "index.html" else None
    else:
        cur = m.group(1)
(out / "_pages.txt").write_text("\n".join(seen))
print(len(seen))
