"""Run 35 step 1: FSCR plan for the 16 'Purchasing' tasks (Run 32 tags; Shared left out), checked against Oracle dependency links.
Same method as Run 33/34: FSCR shared/implementation-planning/task-dependency-resolver = release catalog order (offering PO_PROCUREMENT
first, displaySequence), dependency-graph enrichment (HCM graph only), plus prerequisites the task's own FSCR skill/readiness files name.
Every Oracle link carries a quote; the script FAILS if the quote is not found, in order, in the saved Oracle page. Read-only."""
import json, csv, re, collections
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]; ROOT = RUN.parent; F = ROOT / "fscr-main"
DOCS = RUN / "evidence" / "oracle_docs"
TAG = "Purchasing"
rows = [r for r in csv.DictReader(open(ROOT / "_fscr_run_32_procurement_coverage/procurement_tasks.csv", encoding="utf-8")) if r["row_tag"] == TAG]
T = {r["task_code"]: r for r in rows}; assert len(T) == 16, len(T)
lv = collections.Counter(r["level"] for r in rows)
inv = {x["TaskCode"]: x for x in csv.DictReader(open(ROOT / "_fscr_run_07_inventory/out/tasks.csv", encoding="utf-8"))}
cat = json.load(open(F / "knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json", encoding="utf-8"))["offerings"]
pm = {i["offeringShortName"]: i["pillar"] for i in json.load(open(F / "knowledge/setup-task-catalog/effective/pillars-offerings-mapping.json", encoding="utf-8"))["items"]}
offs = ["PO_PROCUREMENT"] + sorted(o for o in cat if o != "PO_PROCUREMENT" and pm.get(o) == "SCM")
seq = {}
for oi, o in enumerate(offs):
    for fsn, fa in cat[o]["functionalAreas"].items():
        for t in fa["tasks"]:
            c = t["taskShortName"]
            if c in T:
                k = (oi, int(t["displaySequence"]))
                if c not in seq or k < seq[c][:2]: seq[c] = (oi, int(t["displaySequence"]), o, fa["functionalAreaName"])
for o in cat:
    for fsn, fa in cat[o]["functionalAreas"].items():
        for t in fa["tasks"]:
            c = t["taskShortName"]
            if c in T and c not in seq: seq[c] = (99, int(t["displaySequence"]), o, fa["functionalAreaName"])
assert all(c in seq for c in T), [c for c in T if c not in seq]
order = sorted(seq, key=lambda c: seq[c][:2] + (c,))
pos = {c: i + 1 for i, c in enumerate(order)}
names = {c: T[c]["task"] for c in T}

def skill_text(c):
    out = ""
    for p in [x.strip() for x in inv.get(c, {}).get("Skill paths", "").split("|") if x.strip()]:
        fp = F / p; d = fp.parent
        for f in {fp, *d.glob("ora-resource/*.md")}:
            try: out += f.read_text(encoding="utf-8", errors="ignore") + "\n"
            except OSError: pass
    return out

fscr_dep = collections.defaultdict(set); skills_read = 0
for c in T:
    txt = skill_text(c)
    if not txt: continue
    skills_read += 1; low = txt.lower()
    for d, n in names.items():
        if d != c and (d in txt or re.search(r"\b" + re.escape(n.lower()) + r"\b", low)): fscr_dep[c].add(d)
g = json.load(open(F / "knowledge/dependency-graphs/hcm-dependency-graph.json", encoding="utf-8")); graph_hits = 0
for n in g["nodes"]:
    for t in n.get("taskCallSequence", []):
        c = t["id"].split(":", 1)[-1]
        for dep in t.get("dependsOn", []):
            d = str(dep).split(":", 1)[-1]
            if c in T and d in T: fscr_dep[c].add(d); graph_hits += 1

O = "https://docs.oracle.com/en/cloud/saas/procurement/26d/oapro/"; E = "https://docs.oracle.com/en/cloud/saas/procurement/26d/faepp/"
D_RS = ("oapro_26d/what-s-a-buyer-assignment-rule-set.html.txt", O + "what-s-a-buyer-assignment-rule-set.html")
D_EPP = ("faepp_26d/how-do-i-set-up-external-purchase-prices.html.txt", E + "how-do-i-set-up-external-purchase-prices.html")
MAP, PAD, SEL, LKP = ("ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_" + x for x in ("REQBU_MAPPING", "PA_DEFAULTS", "SELECTION_CRITERIA", "LOOKUPS"))
LINKS = [
 ("ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP", "ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES", "stated", D_RS,
  ["You can use rule sets to manage large numbers of assignment rules", "Rules that share a common use can be grouped under a name",
   "use the Manage Buyer Assignment Rule Sets Lookup task"]),
 (MAP, PAD, "list order", D_EPP, ["Perform these setup tasks: Define mappings . Define default attribute values for blanket purchase agreements"]),
 (PAD, SEL, "list order", D_EPP, ["Define default attribute values for blanket purchase agreements created from external purchase prices . Define the selection criteria"]),
 (MAP, SEL, "list order", D_EPP, ["Define mappings", "Define the selection criteria"]),
 # expected by a senior consultant, but no Oracle page I read states it for this pair: unverified, not counted in (a)
 ("PO_MANAGE_HAZARD_CLASSES", "PO_MANAGE_UN_NUMBERS", "unverified", None, None),
 ("PO_MANAGE_PURCHASING_VALUE_SETS", "PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS", "unverified", None, None),
 (LKP, MAP, "unverified", None, None),
 (LKP, SEL, "unverified", None, None),
]
norm = lambda s: re.sub(r"\s+", " ", s).strip().lower()

def verify(doc, frags):
    txt = norm((DOCS / doc).read_text(encoding="utf-8")); at = 0
    for fr in frags:
        i = txt.find(norm(fr), at)
        if i < 0: return False
        at = i
    return True

out_links = []
for a, b, kind, d, q in LINKS:
    assert a in T and b in T, (a, b)
    if kind == "unverified": status, url, quote = "unverified", "", ""
    else:
        assert verify(d[0], q), ("quote not found", a, b, q)
        status, url, quote = "sourced", d[1], " ... ".join(q)
    out_links.append(dict(prereq=a, task=b, link_type=kind, status=status, source_url=url, quote_checked_in_saved_page=quote,
                          prereq_seq=pos[a], task_seq=pos[b], plan_respects=(pos[a] < pos[b]), fscr_skill_states_it=(a in fscr_dep[b]),
                          reused_from_earlier_runs="no"))
srcd = [l for l in out_links if l["status"] == "sourced"]; unv = [l for l in out_links if l["status"] == "unverified"]
pairs = {(l["prereq"], l["task"]) for l in srcd}
resp = {p for p in pairs if pos[p[0]] < pos[p[1]]}
fscr_pairs = {(d, c) for c in fscr_dep for d in fscr_dep[c]}
with open(RUN / "oracle_links.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out_links[0])); w.writeheader(); w.writerows(out_links)
with open(RUN / "plan.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seq", "task_code", "task_name", "functional_area", "row_tag", "catalog_offering", "catalog_functional_area", "catalog_display_sequence",
                "level_run32", "fscr_prerequisites_found", "oracle_sourced_prerequisites"])
    for c in order:
        oi, ds, o, an = seq[c]
        w.writerow([pos[c], c, names[c], T[c]["functional_area"], T[c]["row_tag"], cat[o]["offeringName"], an, ds, T[c]["level"],
                    "; ".join(sorted(fscr_dep[c])), "; ".join(sorted(a for a, b in pairs if b == c))])
res = dict(tasks=16, levels=dict(lv), missing=f"{lv['b'] + lv['c']}/16", skills_read=skills_read, graph_links_used=graph_hits,
           a_sourced_links=len(pairs), a_respected=len(resp), a_stated_by_fscr_skills=len(pairs & fscr_pairs),
           a_violations=[(a, pos[a], b, pos[b]) for a, b in sorted(pairs - resp)],
           b_unverified=len(unv), b_unverified_out_of_order=sum(1 for l in unv if not l["plan_respects"]),
           b_out_of_order=[(l["prereq"], l["prereq_seq"], l["task"], l["task_seq"]) for l in unv if not l["plan_respects"]],
           c_fscr_skill_prereqs=len(fscr_pairs), c_out_of_order=sum(1 for d, c in fscr_pairs if pos[d] > pos[c]),
           c_pairs=sorted((d, pos[d], c, pos[c]) for d, c in fscr_pairs), order=[(pos[c], c, seq[c][3]) for c in order])
json.dump(res, open(RUN / "evidence/plan_summary.json", "w"), indent=1)
json.dump({c: pos[c] for c in order}, open(RUN / "evidence/plan_order.json", "w"))
print(json.dumps(res, indent=1))
