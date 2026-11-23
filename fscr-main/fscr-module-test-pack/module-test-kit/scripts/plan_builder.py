"""Step 2 - Plan. Order a module's tasks the way FSCR's task-dependency-resolver does, then score that order.

Usage:
  python plan_builder.py --module "Procurement" --scope work/Procurement/scope_tasks.csv --out work/Procurement
  python plan_builder.py ... --links work/Procurement/links_input.csv --docs work/Procurement/oracle_docs

Method (shared/implementation-planning/task-dependency-resolver in the FSCR copy of this pack):
  1. Order = the FSCR release catalog (knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json).
     The module's main offering comes first (the offering most of its tasks belong to, or --primary-offering),
     then the other offerings of the same pillar, then the rest. Inside an offering: displaySequence.
  2. FSCR-stated prerequisites = other tasks of this module that the task's own FSCR skill or ora-resource files
     name, plus links in knowledge/dependency-graphs (only an HCM graph exists).
  3. With --links: every Oracle link is checked by link_checker.py against the saved Oracle page.

Writes into --out: plan.csv, plan_summary.json and (with --links) oracle_links.csv.
plan_summary.json holds the three plan measures:
  (a) sourced Oracle links the plan respects, (b) unverified links out of order, (c) FSCR-stated prerequisites out of order.
Exit 1 if a link FAILED its check. Read only. No sign-in, no network.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys

from kitlib import PACK, Path, read_csv, resolve_module, write_csv, write_json
import link_checker

CATALOG = "knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json"
PILLARS = "knowledge/setup-task-catalog/effective/pillars-offerings-mapping.json"
GRAPHS = "knowledge/dependency-graphs"


def walk_graph(nodes):
    for n in nodes:
        yield n
        yield from walk_graph(n.get("children") or [])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", required=True)
    ap.add_argument("--scope", type=Path, required=True, help="scope_tasks.csv from scope_filter.py")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--fscr", type=Path, default=PACK, help="root of the FSCR copy (default: this pack)")
    ap.add_argument("--primary-offering", help="offering short name or name to put first (default: most common)")
    ap.add_argument("--links", type=Path, help="links_input.csv (see link_checker.py --help)")
    ap.add_argument("--docs", type=Path, help="folder of saved Oracle pages (needed with --links)")
    a = ap.parse_args()
    if a.links and not a.docs:
        ap.error("--docs is needed with --links")

    module = resolve_module(a.module)
    rows = [r for r in read_csv(a.scope) if r["tracker_row"] == module]
    if not rows:
        sys.exit(f"No rows for '{module}' in {a.scope}")
    T = {r["task_code"]: r for r in rows}
    F = a.fscr
    cat = json.loads((F / CATALOG).read_text(encoding="utf-8"))["offerings"]
    pillar_of = {i["offeringShortName"]: i["pillar"] for i in json.loads((F / PILLARS).read_text(encoding="utf-8"))["items"]}
    name2code = {v["offeringName"]: k for k, v in cat.items()}

    # main offering
    if a.primary_offering:
        primary = a.primary_offering if a.primary_offering in cat else name2code.get(a.primary_offering)
        if not primary:
            sys.exit(f"Unknown offering: {a.primary_offering}")
    else:
        votes = collections.Counter()
        for r in rows:
            for o in filter(None, (x.strip() for x in r["offering"].split(";"))):
                if o in name2code:
                    votes[name2code[o]] += 1
        if not votes:
            sys.exit("None of the module's tasks is in a catalog offering; pass --primary-offering")
        primary = sorted(votes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    pillar = rows[0]["tracker_pillar"]
    offs = [primary] + sorted(o for o in cat if o != primary and pillar_of.get(o) == pillar)
    offs += sorted(o for o in cat if o not in offs)

    seq = {}
    for oi, o in enumerate(offs):
        for fa in cat[o]["functionalAreas"].values():
            for t in fa["tasks"]:
                c = t["taskShortName"]
                if c in T and c not in seq:
                    seq[c] = (oi, int(t["displaySequence"]), cat[o]["offeringName"], fa["functionalAreaName"], t["displaySequence"])
    missing = sorted(c for c in T if c not in seq)
    for i, c in enumerate(missing):  # not in the release catalog: placed last, flagged
        seq[c] = (10_000, i, "(not in release catalog)", T[c]["functional_area"], "")
    order = sorted(seq, key=lambda c: seq[c][:2] + (c,))
    pos = {c: i + 1 for i, c in enumerate(order)}

    # FSCR-stated prerequisites
    names = {c: T[c]["task_name"] for c in T}
    fscr_dep = collections.defaultdict(set)
    skills_read = 0
    for c, r in T.items():
        txt = ""
        for p in filter(None, (x.strip() for x in r["skill_paths"].split("|"))):
            fp = F / p
            files = {fp, *fp.parent.glob("ora-resource/*.md")} if fp.exists() else set()
            for f in files:
                try:
                    txt += f.read_text(encoding="utf-8", errors="ignore") + "\n"
                except OSError:
                    pass
        if not txt:
            continue
        skills_read += 1
        low = txt.lower()
        for d, n in names.items():
            if d != c and (d in txt or re.search(r"\b" + re.escape(n.lower()) + r"\b", low)):
                fscr_dep[c].add(d)
    graph_hits = 0
    for g in sorted((F / GRAPHS).glob("*.json")):
        data = json.loads(g.read_text(encoding="utf-8"))
        for n in walk_graph(data.get("nodes", [])):
            for t in n.get("taskCallSequence") or []:
                c = str(t.get("id", "")).split(":", 1)[-1]
                for dep in t.get("dependsOn") or []:
                    d = str(dep).split(":", 1)[-1]
                    if c in T and d in T and d not in fscr_dep[c]:
                        fscr_dep[c].add(d)
                        graph_hits += 1

    links = []
    failed = 0
    if a.links:
        links = link_checker.check_links(read_csv(a.links), a.docs)
    sourced_pairs = {(l["prereq"], l["task"]) for l in links if l["status"] == "sourced"}

    plan = []
    for c in order:
        oi, ds, off, area, raw_ds = seq[c]
        plan.append(dict(seq=pos[c], task_code=c, task_name=names[c], functional_area=T[c]["functional_area"],
                         level=T[c]["level"], sample_group=T[c].get("sample_group", ""), catalog_offering=off,
                         catalog_functional_area=area, catalog_display_sequence=raw_ds,
                         fscr_prerequisites_found="; ".join(sorted(fscr_dep[c])),
                         oracle_sourced_prerequisites="; ".join(sorted(p for p, t in sourced_pairs if t == c))))
    write_csv(a.out / "plan.csv", plan)

    if a.links:
        link_checker.add_plan_positions(links, plan)
        write_csv(a.out / "oracle_links.csv", links, link_checker.FIELDS)
        failed = sum(1 for l in links if l["status"] == "FAILED")

    src = [l for l in links if l["status"] == "sourced"]
    unv = [l for l in links if l["status"] == "unverified"]
    fscr_pairs = sorted((d, c) for c in fscr_dep for d in fscr_dep[c])
    lv = collections.Counter(r["level"] for r in rows)
    summary = dict(
        module=module, tasks=len(rows), levels=dict(lv), missing_N_of_total=f"{lv['b'] + lv['c']}/{len(rows)}",
        primary_offering=cat[primary]["offeringName"], not_in_release_catalog=missing,
        skills_read=skills_read, graph_links_used=graph_hits,
        a_sourced_links=len(src), a_respected=sum(1 for l in src if l["plan_respects"] is True),
        a_stated_by_fscr_skills=sum(1 for l in src if l["fscr_skill_states_it"] is True),
        a_violations=[[l["prereq"], l["prereq_seq"], l["task"], l["task_seq"]] for l in src if l["plan_respects"] is False],
        b_unverified=len(unv), b_unverified_out_of_order=sum(1 for l in unv if l["plan_respects"] is False),
        b_out_of_order=[[l["prereq"], l["prereq_seq"], l["task"], l["task_seq"]] for l in unv if l["plan_respects"] is False],
        c_fscr_skill_prereqs=len(fscr_pairs), c_out_of_order=sum(1 for d, c in fscr_pairs if pos[d] > pos[c]),
        c_pairs_out_of_order=[[d, pos[d], c, pos[c]] for d, c in fscr_pairs if pos[d] > pos[c]],
        links_failed=failed,
        order=[[pos[c], c, seq[c][3]] for c in order])
    write_json(a.out / "plan_summary.json", summary)

    print(f"{module}: {len(order)} tasks planned, main offering {summary['primary_offering']}"
          + (f", {len(missing)} not in the release catalog (placed last)" if missing else ""))
    print(f"FSCR skills read: {skills_read}; FSCR-stated prerequisites: {len(fscr_pairs)} "
          f"({summary['c_out_of_order']} out of order); dependency-graph links: {graph_hits}")
    if a.links:
        print(f"(a) sourced Oracle links respected: {summary['a_respected']} of {summary['a_sourced_links']}; "
              f"stated by FSCR skills: {summary['a_stated_by_fscr_skills']}")
        print(f"(b) unverified links out of order: {summary['b_unverified_out_of_order']} of {summary['b_unverified']}")
        if failed:
            print(f"{failed} link(s) FAILED the quote check - see oracle_links.csv (check_note). Fix or remove them.")
    else:
        print("No --links given: oracle_links.csv not written. Read Oracle pages, write links_input.csv, run again.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
