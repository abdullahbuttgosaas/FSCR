"""Run 34 step 1: FSCR plan for the 91 'Sourcing and Supplier Management' tasks (Run 32 tags; Shared left out), then check it
against Oracle dependency links. Same method as Run 33 (plan33.py):
FSCR method = shared/implementation-planning/task-dependency-resolver: release catalog order (offering PO_PROCUREMENT first,
displaySequence), dependency-graph enrichment (HCM graph only exists), plus prerequisites that the task's own FSCR skill / readiness
files name. Every Oracle link carries a quote; the script FAILS if the quote is not found, in order, in the saved Oracle page.
A link with no quote is 'unverified' and is left out of the percentage. Read-only (no Oracle calls)."""
import json, csv, re, collections
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]; ROOT = RUN.parent; F = ROOT / "fscr-main"
DOCS = RUN / "evidence" / "oracle_docs"
TAG = "Sourcing and Supplier Management"
rows = [r for r in csv.DictReader(open(ROOT / "_fscr_run_32_procurement_coverage/procurement_tasks.csv", encoding="utf-8")) if r["row_tag"] == TAG]
T = {r["task_code"]: r for r in rows}; assert len(T) == 91, len(T)
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
                if c not in seq or k < seq[c][:2]:
                    seq[c] = (oi, int(t["displaySequence"]), o, fa["functionalAreaName"])
for o in cat:   # fallback: any offering
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
        for f in {fp, *d.glob("ora-resource/*readiness*.md")}:
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

U = "https://docs.oracle.com/en/cloud/saas/procurement/26d/oapro/"
def D(p): return ("oapro_26d/" + p + ".txt", U + p)
D_CF, D_QA, D_QAC, D_QM, D_RS, D_ROLE, D_SPC, D_NUM, D_IMP, D_CERT, D_Q = (D("create-cost-factors.html"), D("qualification-areas.html"), D("create-a-qualification-area.html"),
    D("create-a-qualification-model.html"), D("supplier-qualification-rule-sets.html"), D("set-up-supplier-roles.html"), D("get-started-with-supplier-portal-configuration.html"),
    D("supplier-numbering.html"), D("create-suppliers-with-the-import-suppliers-process.html"), D("how-you-manage-certifying-agencies.html"), D("create-a-question.html"))
Q, QA, QM, RS = "ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_QUESTIONS", "ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_AREAS", "ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_MODELS", "ORA_POQ_MANAGE_SUPPLIER_REG_RULE_SETS"
LINKS = [
 ("PON_MANAGE_COST_FACTORS", "PON_MANAGE_COST_FACTOR_LISTS", "stated", D_CF, ["Once the cost factors are defined and enabled, they become available for buyers to use individually or as members of a cost factor list"]),
 (Q, QA, "stated", D_QA, ["Qualification areas are containers for your questions"]),
 (Q, QA, "stated", D_QAC, ["You use qualification areas to contain and organize your qualification questions", "This question has been defined earlier"]),
 (QA, QM, "stated", D_QM, ["Qualification models contain and organize qualification areas", "This area has been defined earlier"]),
 (QA, RS, "stated", D_RS, ["A rule set consists of one or more qualification areas"]),
 (Q, RS, "stated", D_RS, ["If you have to create a qualification area, note that: The questions must be at the supplier level. The questions are active"]),
 (QM, RS, "stated", D_RS, ["You can specify a sourcing qualification model for a particular procurement BU"]),
 ("POZ_MANAGE_SUPPLIER_USER_ROLES", "POZ_MANAGE_SUPPLIER_USER_ROLE_USAGES", "stated", D_ROLE, ["uses the Manage Supplier User Roles task", "then navigates to the Setup and Maintenance work area and uses the Manage Supplier User Role Usages task"]),
 ("POZ_MANAGE_SUPPLIER_USER_ROLE_USAGES", "POZ_CONFIGURE_SUPPLIER_REGISTRATION", "list order", D_SPC, ["Manage Supplier User Role Usages *Configure Supplier Registration"]),
 ("POZ_SPECIFY_SUPPLIER_NUMBERING", "POZ_IMPORT_SUPPLIERS", "stated", D_NUM, ["Suppliers created through the Create Supplier task flow, through the supplier registration process, or through supplier import, are automatically numbered. The starting supplier number is defined in the Specify Supplier Numbering Setup page"]),
 ("POZ_SPECIFY_SUPPLIER_NUMBERING", "POZ_CONFIGURE_SUPPLIER_REGISTRATION", "stated", D_NUM, ["through the supplier registration process", "are automatically numbered. The starting supplier number is defined in the Specify Supplier Numbering Setup page"]),
 ("ORA_POZ_LOAD_SUPPLIER_INTERFACE_VIA_SCHEDULED_PROCESS", "POZ_IMPORT_SUPPLIERS", "stated", D_IMP, ["load data to interface tables using predefined templates and the Load Interface File for Import scheduled process", "Data must first be inserted into the existing Open Interface Tables"]),
 ("POZ_MANAGE_BUSINESS_CLASSIFICATION_LOOKUP", "ORA_POZ_MANAGE_CERTIFYING_AGENCIES", "stated", D_CERT, ["Certifying agencies are maintained and associated with the applicable classifications"]),
 ("POZ_MANAGE_BUSINESS_CLASSIFICATION_LOOKUP", "POZ_IMPORT_SUPPLIERS", "stated", D_IMP, ["Import Supplier Business Classifications"]),
 ("POR_MANAGE_SUPPLIER_PRODUCTS_AND_SERVICES_CATEGORY_HIERARCHY", "POZ_IMPORT_SUPPLIERS", "stated", D_IMP, ["Import Supplier Products and Services Categories"]),
 # --- expected by a senior consultant but no page I read states it for this pair: unverified, not counted
 ("POZ_MANAGE_SUPPLIER_VALUE_SETS", "POZ_MANAGE_SUPPLIER_DESCRIPTIVE_FLEXFIELDS", "unverified", None, None),
 ("POZ_MANAGE_SUPPLIER_REGISTRATION_VALUE_SETS", "POZ_MANAGE_SUPPLIER_REGISTRATION_DESCRIPTIVE_FLEXFIELDS", "unverified", None, None),
 ("PON_MANAGE_SOURCING_VALUE_SETS", "PON_MANAGE_SOURCING_DESCRIPTIVE_FLEXFIELDS", "unverified", None, None),
 ("ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_VALUE_SETS", "ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_DESCRIPTIVE_FLEXFIELDS", "unverified", None, None),
 ("ORA_RCS_MANAGE_INV_ORG_VALUE_SETS", "ORA_RCS_MANAGE_INV_ORG_FLEXFIELDS", "unverified", None, None),
 ("ORA_RCS_MANAGE_ITEM_ORG_VALUE_SETS", "ORA_RCS_MANAGE_ITEM_ORG_FLEXFIELDS", "unverified", None, None),
 ("ORA_POZ_UPLOAD_SUPPLIER_IMPORT_FILE", "ORA_POZ_LOAD_SUPPLIER_INTERFACE_VIA_SCHEDULED_PROCESS", "unverified", None, None),
 ("POZ_MANAGE_SUPPLIER_TYPE_LOOKUP", "POZ_IMPORT_SUPPLIERS", "unverified", None, None),
 ("POZ_MANAGE_SUPPLIER_REGISTRATION_DESCRIPTIVE_FLEXFIELDS", "POZ_CONFIGURE_SUPPLIER_REGISTRATION", "unverified", None, None),
 ("HZ_MANAGE_TRADING_COMMUNITY_SOURCE_SYSTEMS", "POZ_IMPORT_SUPPLIERS", "unverified", None, None),
 ("PON_MANAGE_ATTRIBUTE_LISTS", "PON_MANAGE_NEGOTIATION_STYLES", "unverified", None, None),
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
    if kind == "unverified": status, doc, url, quote = "unverified", "", "", ""
    else:
        assert verify(d[0], q), ("quote not found", a, b, q)
        status, doc, url, quote = "sourced", d[0], d[1], " ... ".join(q)
    out_links.append(dict(prereq=a, task=b, link_type=kind, status=status, source_url=url, quote_checked_in_saved_page=quote,
                          prereq_seq=pos[a], task_seq=pos[b], plan_respects=(pos[a] < pos[b]), fscr_skill_states_it=(a in fscr_dep[b]), reused_from_run33="no"))
srcd = [l for l in out_links if l["status"] == "sourced"]
pairs = {(l["prereq"], l["task"]) for l in srcd}
resp = {p for p in pairs if pos[p[0]] < pos[p[1]]}
fst = {p for p in pairs if p[0] in fscr_dep[p[1]]}
with open(RUN / "oracle_links.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out_links[0])); w.writeheader(); w.writerows(out_links)
with open(RUN / "plan.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seq", "task_code", "task_name", "functional_area", "row_tag", "catalog_offering", "catalog_display_sequence", "level_run32", "fscr_prerequisites_found", "oracle_sourced_prerequisites"])
    for c in order:
        oi, ds, o, an = seq[c]
        w.writerow([pos[c], c, names[c], T[c]["functional_area"], T[c]["row_tag"], cat[o]["offeringName"], ds, T[c]["level"], "; ".join(sorted(fscr_dep[c])), "; ".join(sorted(a for a, b in pairs if b == c))])
# Area-level check (Oracle rapid implementation page: supplier configuration is in the common task list; then the optional modules
# are listed Supplier Portal -> Sourcing -> Supplier Qualification). Area of a task = first area named in Run 32.
area = {c: T[c]["functional_area"].split(";")[0].strip() for c in T}
ap = collections.defaultdict(list)
for c in order: ap[area[c]].append(pos[c])
assert verify("oapro_26d/get-started-with-your-procurement-rapid-implementation.html.txt",
              ["Define Common Procurement Configuration for Rapid Implementation", "Define Supplier Configuration for Rapid Implementation",
               "Use the following task lists to configure the applicable optional modules", "Define Supplier Portal Configuration for Rapid Implementation",
               "Define Sourcing Configuration for Rapid Implementation", "Define Supplier Qualification Configuration for Rapid Implementation"])
def before(x, y): return max(ap[x]) < min(ap[y])
def median(v): v = sorted(v); return v[len(v) // 2]
area_check = {
 "suppliers_all_before_sourcing": before("Suppliers", "Sourcing"), "suppliers_all_before_qualification": before("Suppliers", "Supplier Qualification"),
 "suppliers_median_before_sourcing": median(ap["Suppliers"]) < min(ap["Sourcing"]),
 "suppliers_tasks_after_first_sourcing_task": sum(1 for p in ap["Suppliers"] if p > min(ap["Sourcing"] + ap["Supplier Qualification"])),
 "portal_before_sourcing": before("Supplier Portal", "Sourcing"), "sourcing_before_qualification": before("Sourcing", "Supplier Qualification"),
 "area_ranges": {a: (min(p), max(p), len(p)) for a, p in sorted(ap.items(), key=lambda kv: min(kv[1]))}}
res = dict(tasks=91, levels=dict(lv), missing=f"{lv['b'] + lv['c']}/91", skills_read=skills_read, graph_links_used=graph_hits,
           fscr_tasks_with_any_prereq=sum(1 for c in T if fscr_dep[c]), fscr_prereq_links=sum(len(v) for v in fscr_dep.values()),
           oracle_links_rows=len(out_links), oracle_links_sourced_rows=len(srcd), oracle_pairs_sourced=len(pairs), oracle_pairs_respected=len(resp),
           oracle_pairs_stated_by_fscr_skills=len(fst), unverified=sum(1 for l in out_links if l["status"] == "unverified"),
           unverified_but_plan_respects=sum(1 for l in out_links if l["status"] == "unverified" and l["plan_respects"]),
           violations=[(a, pos[a], b, pos[b]) for a, b in sorted(pairs - resp)], area_check=area_check, run33_links_reused=0)
json.dump(res, open(RUN / "evidence/plan_summary.json", "w"), indent=1); json.dump({c: pos[c] for c in order}, open(RUN / "evidence/plan_order.json", "w"))
print(json.dumps(res, indent=1))
