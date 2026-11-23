"""Fetch Oracle doc pages with curl, save html + plain text under evidence/oracle_docs. Usage: fetch_text.py url [url...]"""
import re, sys, subprocess, html, pathlib
out = pathlib.Path(__file__).resolve().parents[1] / "evidence" / "oracle_docs"
for u in sys.argv[1:]:
    raw = subprocess.run(["curl", "-sL", "--max-time", "60", u], capture_output=True).stdout.decode("utf-8", "replace")
    name = re.sub(r"[^A-Za-z0-9]+", "_", u.split("docs.oracle.com/")[-1])[:120]
    s = re.sub(r"<script.*?</script>|<style.*?</style>|<head>.*?</head>", "", raw, flags=re.S)
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)))
    (out / (name + ".txt")).write_text("URL: " + u + "\n" + t, encoding="utf-8")
    print(len(t), name)
