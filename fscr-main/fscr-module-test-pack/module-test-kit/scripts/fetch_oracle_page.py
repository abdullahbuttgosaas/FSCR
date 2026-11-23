"""Save the text of a public Oracle documentation page so link_checker.py can check quotes against it.

Usage:
  python fetch_oracle_page.py --out work/Procurement/oracle_docs https://docs.oracle.com/en/cloud/saas/procurement/26d/oapro/negotiation-styles.html

Only https://docs.oracle.com/ pages are allowed. This is a plain public web page read: it does not sign in
and does not touch any Oracle environment. Each page is saved as <last-part-of-url>.txt with the first
line "URL: <url>", then the page text without HTML tags.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
import urllib.request

from kitlib import Path


def page_text(raw: str) -> str:
    s = re.sub(r"<script.*?</script>|<style.*?</style>|<head>.*?</head>", " ", raw, flags=re.S | re.I)
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def file_name(url: str) -> str:
    parts = [p for p in url.split("?")[0].split("/") if p]
    book = parts[-2] if len(parts) >= 2 else "page"
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{book}__{parts[-1]}") + ".txt"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+", help="one or more https://docs.oracle.com/ page URLs")
    ap.add_argument("--out", type=Path, required=True, help="folder for the saved page texts")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    bad = 0
    for url in a.urls:
        if not url.startswith("https://docs.oracle.com/"):
            print(f"SKIPPED (not docs.oracle.com): {url}")
            bad += 1
            continue
        req = urllib.request.Request(url, headers={"User-Agent": "fscr-module-test-kit/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode("utf-8", "replace")
        except Exception as e:  # network errors are reported, not hidden
            print(f"FAILED {url}: {e}")
            bad += 1
            continue
        txt = page_text(raw)
        name = file_name(url)
        (a.out / name).write_text(f"URL: {url}\n{txt}\n", encoding="utf-8")
        print(f"saved {name} ({len(txt)} characters)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
