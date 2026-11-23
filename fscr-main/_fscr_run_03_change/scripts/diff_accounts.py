"""Field-level diff of FSCR customer-reader XML (getCustomerAccount) before vs after (offline).
Why: FSCR's reader returns raw XML and says persisted_reconciliation_complete=false; it has no compare.
Flattens every leaf element to path=value (namespace prefixes dropped, repeated siblings indexed) and diffs.
Usage: diff_accounts.py <before_dir> <after_dir> <account numbers...>"""
import json, sys
import xml.etree.ElementTree as ET
from pathlib import Path


def flat(xml):
    root = ET.fromstring(xml)
    out = {}

    def walk(el, path):
        kids = list(el)
        if not kids:
            out[path] = (el.text or "").strip()
            return
        seen = {}
        for k in kids:
            tag = k.tag.split("}")[-1]
            seen[tag] = seen.get(tag, -1) + 1
            walk(k, f"{path}/{tag}[{seen[tag]}]")
    walk(root, "")
    return out


bd, ad = Path(sys.argv[1]), Path(sys.argv[2])
for n in sys.argv[3:]:
    b = flat(json.loads((bd / f"acct_{n}.json").read_text(encoding="utf-8"))[0])
    a = flat(json.loads((ad / f"acct_{n}.json").read_text(encoding="utf-8"))[0])
    diffs = {k: (b.get(k), a.get(k)) for k in set(a) | set(b) if b.get(k) != a.get(k) and "MessageID" not in k}
    print(f"account {n}: {len(b)} fields before, {len(a)} after, {len(diffs)} differ")
    for k, v in sorted(diffs.items()):
        print("   ", k.split("Body")[-1][-110:], v)
