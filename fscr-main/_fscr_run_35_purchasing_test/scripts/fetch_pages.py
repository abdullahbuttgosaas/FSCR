"""Run 35: fetch Oracle Help Center pages (read-only GET via curl); save plain text under evidence/oracle_docs/<book>.
Usage: fetch_pages.py <book: oapro|faepp|oaprc|faicf> page.html [page.html ...]"""
import re, sys, subprocess, html, pathlib
B = {"oapro": "https://docs.oracle.com/en/cloud/saas/procurement/26d/oapro/", "faepp": "https://docs.oracle.com/en/cloud/saas/procurement/26d/faepp/", "oaprc": "https://docs.oracle.com/en/cloud/saas/procurement/26d/oaprc/", "faicf": "https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faicf/"}[sys.argv[1]]
out = pathlib.Path(__file__).resolve().parents[1] / "evidence" / "oracle_docs" / (sys.argv[1] + "_26d"); out.mkdir(parents=True, exist_ok=True)
for p in sys.argv[2:]:
    raw = subprocess.run(["curl", "-sL", "--max-time", "60", B + p], capture_output=True).stdout.decode("utf-8", "replace")
    s = re.sub(r"<script.*?</script>|<style.*?</style>|<head>.*?</head>", "", raw, flags=re.S)
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)))
    (out / (p + ".txt")).write_text("URL: " + B + p + "\n" + t, encoding="utf-8")
    print(len(t), p)
