"""Step 2b - Dependency-link checker. Proves every "A must come before B" link against a saved Oracle page.

Usage:
  python link_checker.py --links links_input.csv --docs work/Procurement/oracle_docs --out work/Procurement/oracle_links.csv
  python link_checker.py ... --plan work/Procurement/plan.csv     (also checks the plan order)

links_input.csv columns (one row per link; you write this file while reading Oracle pages):
  prereq      task code that must come first (for example PO_MANAGE_HAZARD_CLASSES)
  task        task code that depends on it
  link_type   stated | list order | unverified
  source_url  the Oracle page URL (https://docs.oracle.com/...); empty for unverified
  saved_page  file name of the page text inside --docs (saved by fetch_oracle_page.py); empty for unverified
  quote       words copied from that page; several pieces may be joined with " ... " and must appear in that order

Rules (a link that breaks one is FAILED, and the script exits 1):
  * a sourced link needs a docs.oracle.com URL, a saved page whose first line is "URL: <the same URL>",
    and every quote piece found in the page text, in order (spaces and case are ignored);
  * an unverified link has no URL and no quote. It is reported, never counted as verified.
Output: oracle_links.csv with status sourced / unverified / FAILED and, with --plan, the plan positions and
plan_respects (True when the prerequisite comes first). Read only. No sign-in, no network.
"""
from __future__ import annotations

import argparse
import re
import sys

from kitlib import Path, read_csv, write_csv

FIELDS = ["prereq", "task", "link_type", "status", "source_url", "saved_page", "quote_checked_in_saved_page",
          "check_note", "prereq_seq", "task_seq", "plan_respects", "fscr_skill_states_it"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_in_page(page_text: str, quote: str) -> tuple[bool, str]:
    txt = norm(page_text)
    at = 0
    for piece in [p for p in (x.strip() for x in quote.split("...")) if p]:
        i = txt.find(norm(piece), at)
        if i < 0:
            return False, f"quote piece not found (in order): '{piece[:60]}'"
        at = i + len(norm(piece))
    return True, "quote found in saved page"


def check_links(rows: list[dict], docs: Path) -> list[dict]:
    out = []
    for r in rows:
        kind = (r.get("link_type") or "").strip().lower()
        url = (r.get("source_url") or "").strip()
        page = (r.get("saved_page") or "").strip()
        quote = (r.get("quote") or "").strip()
        o = dict(prereq=r["prereq"].strip(), task=r["task"].strip(), link_type=kind, source_url=url, saved_page=page,
                 quote_checked_in_saved_page=quote)
        if kind == "unverified":
            if url or quote:
                o.update(status="FAILED", check_note="unverified links must not carry a URL or quote")
            else:
                o.update(status="unverified", check_note="no Oracle page states it; not counted as verified")
        elif kind not in ("stated", "list order"):
            o.update(status="FAILED", check_note=f"unknown link_type '{kind}'")
        elif not url.startswith("https://docs.oracle.com/"):
            o.update(status="FAILED", check_note="source_url must be an https://docs.oracle.com/ page")
        elif not quote:
            o.update(status="FAILED", check_note="no quote")
        elif not page or not (docs / page).is_file():
            o.update(status="FAILED", check_note=f"saved page missing: {page or '(empty)'}")
        else:
            text = (docs / page).read_text(encoding="utf-8", errors="replace")
            first = text.splitlines()[0] if text else ""
            if first.strip() != f"URL: {url}":
                o.update(status="FAILED", check_note="saved page's first line is not 'URL: <source_url>'")
            else:
                ok, note = quote_in_page(text, quote)
                o.update(status="sourced" if ok else "FAILED", check_note=note)
        out.append(o)
    return out


def add_plan_positions(links: list[dict], plan_rows: list[dict]) -> None:
    pos = {p["task_code"]: int(p["seq"]) for p in plan_rows}
    fscr = {p["task_code"]: set(filter(None, (p.get("fscr_prerequisites_found") or "").split("; "))) for p in plan_rows}
    for l in links:
        a, b = l["prereq"], l["task"]
        if a not in pos or b not in pos:
            l["status"] = "FAILED"
            l["check_note"] += f"; task code not in plan: {a if a not in pos else b}"
            continue
        l.update(prereq_seq=pos[a], task_seq=pos[b], plan_respects=pos[a] < pos[b],
                 fscr_skill_states_it=a in fscr.get(b, set()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--links", type=Path, required=True, help="links_input.csv you wrote")
    ap.add_argument("--docs", type=Path, required=True, help="folder with the saved Oracle page texts")
    ap.add_argument("--out", type=Path, required=True, help="oracle_links.csv to write")
    ap.add_argument("--plan", type=Path, help="plan.csv from plan_builder.py (adds positions and plan_respects)")
    a = ap.parse_args()

    links = check_links(read_csv(a.links), a.docs)
    if a.plan:
        add_plan_positions(links, read_csv(a.plan))
    write_csv(a.out, links, FIELDS)
    st = {k: sum(1 for l in links if l["status"] == k) for k in ("sourced", "unverified", "FAILED")}
    print(f"links: {len(links)} | sourced {st['sourced']} | unverified {st['unverified']} | FAILED {st['FAILED']}")
    for l in links:
        if l["status"] == "FAILED":
            print(f"  FAILED {l['prereq']} -> {l['task']}: {l['check_note']}")
    if a.plan:
        src = [l for l in links if l["status"] == "sourced"]
        unv = [l for l in links if l["status"] == "unverified"]
        print(f"sourced links respected by the plan: {sum(1 for l in src if l['plan_respects'] is True)} of {len(src)}")
        print(f"unverified links out of order: {sum(1 for l in unv if l['plan_respects'] is False)} of {len(unv)}")
    return 1 if st["FAILED"] else 0


if __name__ == "__main__":
    sys.exit(main())
