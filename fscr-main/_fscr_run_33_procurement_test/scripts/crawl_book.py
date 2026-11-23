"""Crawl an Oracle Help Center book by following <link rel=next>; save plain text per page. Usage: crawl_book.py <base_url_ending_slash> <tag> [max]"""
import re, subprocess, html, pathlib, sys
base, tag = sys.argv[1], sys.argv[2]; mx = int(sys.argv[3]) if len(sys.argv) > 3 else 400
out = pathlib.Path(__file__).resolve().parents[1] / "evidence" / "oracle_docs" / tag; out.mkdir(parents=True, exist_ok=True)
cur = "index.html"; seen = []
while cur and cur not in seen and len(seen) < mx:
    seen.append(cur)
    raw = subprocess.run(["curl", "-s", "--max-time", "60", base + cur], capture_output=True).stdout.decode("utf-8", "replace")
    s = re.sub(r"<script.*?</script>|<style.*?</style>|<head>.*?</head>", "", raw, flags=re.S)
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)))
    (out / (cur + ".txt")).write_text("URL: " + base + cur + "\n" + t, encoding="utf-8")
    m = re.search(r'<link rel="next" href="([^"#]+\.html)"', raw)
    cur = m.group(1) if m else (None if cur != "index.html" else "title-and-copyright-information.html")
(out / "_pages.txt").write_text("\n".join(seen)); print(tag, len(seen))
