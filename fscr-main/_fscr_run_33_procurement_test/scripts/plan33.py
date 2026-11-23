"""Run 33 step 1: FSCR plan for the 60 Procurement + Shared tasks, then check it against Oracle dependency links.
FSCR method = shared/implementation-planning/task-dependency-resolver: release catalog order (offering context PO_PROCUREMENT,
displaySequence), dependency-graph enrichment (HCM graph only), plus prerequisites that the task's own FSCR skill / readiness files name.
Every Oracle link below carries a quote; the script FAILS if the quote is not found, in order, inside the saved Oracle page.
A link with no quote is written as 'unverified' and is left out of the percentage. Read-only."""
import json, csv, re, collections, sys
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]; ROOT = RUN.parent; F = ROOT / "fscr-main"
DOCS = RUN / "evidence" / "oracle_docs"
rows = [r for r in csv.DictReader(open(ROOT / "_fscr_run_32_procurement_coverage/procurement_tasks.csv", encoding="utf-8")) if r["row_tag"] in ("Procurement", "Shared")]
T = {r["task_code"]: r for r in rows}; assert len(T) == 60, len(T)
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
missing = [c for c in T if c not in seq]
if missing:   # fall back to the effective catalog / any offering
    for o in cat:
        for fsn, fa in cat[o]["functionalAreas"].items():
            for t in fa["tasks"]:
                c = t["taskShortName"]
                if c in missing and c not in seq: seq[c] = (99, int(t["displaySequence"]), o, fa["functionalAreaName"])
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

# ---- Oracle links: (prereq, task, kind, doc file under evidence/oracle_docs, URL, quote fragments in order). quote=None => unverified
U = "https://docs.oracle.com/en/cloud/saas/"
D_TAB = ("sla_26d/transaction-account-builder.html.txt", U + "financials/26d/faisl/transaction-account-builder.html")
D_MAP = ("sla_26d/how-you-define-mapping-sets.html.txt", U + "financials/26d/faisl/how-you-define-mapping-sets.html")
D_OVR = ("en_cloud_saas_procurement_25d_oapro_overview_of_managing_approvals_and_notifications_html.txt", U + "procurement/25d/oapro/overview-of-managing-approvals-and-notifications.html")
D_APR = ("en_cloud_saas_procurement_25d_oapro_various_aspects_of_approval_rules_html.txt", U + "procurement/25d/oapro/various-aspects-of-approval-rules.html")
D_RBF = ("en_cloud_saas_procurement_25c_oapro_how_you_configure_business_units_with_requisitioning_business_html.txt", U + "procurement/25c/oapro/how-you-configure-business-units-with-requisitioning-business.html")
D_INF = ("en_cloud_saas_procurement_26a_oapro_how_you_use_information_templates_html.txt", U + "procurement/26a/oapro/how-you-use-information-templates.html")
D_CCL = ("en_cloud_saas_procurement_25c_oaprc_create_a_compliance_checklist_html.txt", U + "procurement/25c/oaprc/create-a-compliance-checklist.html")
D_CON = ("en_cloud_saas_sales_oacts_set_up_procurement_contracts_html.txt", U + "sales/oacts/set-up-procurement-contracts.html")
D_CPR = ("expenses_26c/what-s-a-corporate-card-program.html.txt", U + "financials/26c/faiex/what-s-a-corporate-card-program.html")
D_ISS = ("expenses_26c/how-can-i-configure-corporate-card-issuers.html.txt", U + "financials/26c/faiex/how-can-i-configure-corporate-card-issuers.html")
D_CRD = ("expenses_26c/options-for-creating-corporate-cards.html.txt", U + "financials/26c/faiex/options-for-creating-corporate-cards.html")
SRC, ACR, TAD, TAT, MAP = "XLA_MANAGE_SOURCES", "XLA_MANAGE_ACCOUNT_RULE", "XLA_MANAGE_TRANSACTION_ACCOUNT_DEFINITION", "XLA_MANAGE_TRANSACTION_ACCOUNT_TYPES", "XLA_MANAGE_MAPPING_SET"
LINKS = [
 (SRC, TAT, "stated", D_TAB, ["Sources are assigned to transaction account types"]),
 (TAT, TAD, "stated", D_TAB, ["Transaction account types are assigned to transaction account definitions"]),
 (SRC, ACR, "stated", D_TAB, ["Assigned sources in each transaction account type are available for use in account rules"]),
 (ACR, TAD, "stated", D_TAB, ["Assign account combination or segment rules to each transaction account type assignment in a transaction account definition"]),
 (MAP, ACR, "stated", D_MAP, ["Mapping set with account combination output type can be assigned to account rule"]),
 ("PO_MANAGE_TASK_CONFIGURATIONS", "ORA_MANAGE_APPROVAL_GROUPS", "list order", D_OVR, ["Manage Task Configurations Manage Approval Groups"]),
 ("ORA_MANAGE_APPROVAL_GROUPS", "POR_MANAGE_REQUISITION_APPROVALS", "list order", D_OVR, ["Manage Approval Groups Manage Requisition Approvals"]),
 ("ORA_MANAGE_APPROVAL_GROUPS", "POR_MANAGE_REQUISITION_APPROVALS", "stated", D_APR, ["Approval Group: Specify the Approval Group to use"]),
 ("ORA_MANAGE_APPROVAL_GROUPS", "PO_MANAGE_PURCHASING_DOCUMENT_APPROVALS", "stated", D_APR, ["Approval Group: Specify the Approval Group to use"]),
 ("PO_MANAGE_PURCHASING_LINE_TYPES", "POR_CONFIGURE_REQUISITIONING_BUSINESS_FUNCTION", "stated", D_RBF, ["Line Type specifies the default line type to be used for requisition lines created for the requisitioning BU"]),
 ("POR_MANAGE_REQUISITION_DESCRIPTIVE_FLEXFIELDS", "POR_CONFIGURE_REQUISITIONING_BUSINESS_FUNCTION", "stated", D_RBF, ["Specifying the context value pulls in the associated descriptive flex-fields"]),
 ("POR_MANAGE_INFORMATION_TEMPLATE_VALUE_SETS", "POR_MANAGE_INFORMATION_TEMPLATE_DESCRIPTIVE_FLEXFIELDS", "stated", D_INF, ["Value sets can be added to Information Templates through descriptive flexfields"]),
 ("ORA_PO_COMPLIANCE_CHECKLIST_QUESTIONS", "ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS", "stated", D_CCL, ["for any sections that include the outdated question"]),
 ("ORA_PO_COMPLIANCE_CHECKLIST_SECTIONS", "ORA_PO_COMPLIANCE_CHECKLIST_TEMPLATES", "stated", D_CCL, ["any templates containing the outdated section should also uptake the new section revision"]),
 ("OKC_SPECIFY_PROCUREMENT_CONTRACT_MGMT_BUSINESS_FUNC_PROP", "OKC_MANAGE_CONTRACT_LINE_TYPES", "list order", D_CON, ["Configure contract management business functions", "Define contract line types"]),
 ("OKC_MANAGE_CONTRACT_LINE_TYPES", "AP_MANAGE_PAYMENT_TERMS", "list order", D_CON, ["Define contract line types", "Define payment terms"]),
 ("AP_MANAGE_PAYMENT_TERMS", "PO_MANAGE_FOB_LOOKUP", "list order", D_CON, ["Define payment terms. Define FOB and freight terms"]),
 ("AP_MANAGE_PAYMENT_TERMS", "PO_MANAGE_FREIGHT_TERM_LOOKUP", "list order", D_CON, ["Define payment terms. Define FOB and freight terms"]),
 ("OKC_SPECIFY_PROCUREMENT_CONTRACT_MGMT_BUSINESS_FUNC_PROP", "ORA_MANAGE_APPROVAL_GROUPS", "list order", D_CON, ["Configure contract management business functions", "Set up approval groups and approval task configurations"]),
 ("EXM_MANAGE_CORPORATE_CARD_ISSUERS", "EXM_MANAGE_CORPORATE_CARD_PROGRAMS", "stated", D_CPR, ["Each company account is associated with: A card issuing bank, known as a card issuer"]),
 ("AP_MANAGE_PAYMENT_TERMS", "EXM_MANAGE_CORPORATE_CARD_PROGRAMS", "stated", D_CPR, ["A card issuing bank, known as a card issuer Payment terms"]),
 ("EXM_MANAGE_CORPORATE_CARD_PROGRAMS", "EXM_MANAGE_CORPORATE_CARDS", "stated", D_CRD, ["selecting an employee matching rule for new cards on the Upload Rules tab of the Create Corporate Card Program page"]),
 # --- links a senior consultant would expect but that no page I read states: kept, labelled unverified, not counted
 ("PO_MANAGE_PURCHASING_LINE_TYPES", "PO_MANAGE_DOCUMENT_STYLES", "unverified", None, None),
 ("INV_MANAGE_UNITS_OF_MEASURE", "PO_MANAGE_PURCHASING_LINE_TYPES", "unverified", None, None),
 ("POR_MANAGE_REQUISITION_VALUE_SETS", "POR_MANAGE_REQUISITION_DESCRIPTIVE_FLEXFIELDS", "unverified", None, None),
 ("XLA_MANAGE_SUBLEDGER_APPLICATION", SRC, "unverified", None, None),
 ("XLA_MANAGE_SUBLEDGER_APPLICATION", MAP, "unverified", None, None),
 ("PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION", "PO_MANAGE_DOCUMENT_STYLES", "unverified", None, None),
 ("PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION", "PO_MANAGE_PROCUREMENT_AGENTS", "unverified", None, None),
 ("AP_MANAGE_COMMON_OPTIONS_FOR_PAYABLES_AND_PROCUREMENT", "PO_CONFIGURE_PROCUREMENT_BUSINESS_FUNCTION", "unverified", None, None),
 ("ORA_XLA_MANAGE_FORMULA", ACR, "unverified", None, None),
 ("XLA_MANAGE_TRANSACTION_ACCOUNT_DEFINITION", "XLA_UPDATE_SUBLEDGER_APPLICATION_OPTIONS", "unverified", None, None),
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
    if kind == "unverified":
        status, doc, url, quote = "unverified", "", "", ""
    else:
        ok = verify(d[0], q); assert ok, ("quote not found", a, b, q)
        status, doc, url, quote = "sourced", d[0], d[1], " ... ".join(q)
    out_links.append(dict(prereq=a, task=b, link_type=kind, status=status, source_url=url, quote_checked_in_saved_page=quote,
                          prereq_seq=pos[a], task_seq=pos[b], plan_respects=(pos[a] < pos[b]), fscr_skill_states_it=(a in fscr_dep[b])))
srcd = [l for l in out_links if l["status"] == "sourced"]
# distinct sourced pairs (a pair can be backed by two pages)
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
# area order vs Oracle rapid-implementation module order (Common config -> Purchasing -> SSP -> ... -> Contract Terms)
area_first = collections.defaultdict(list)
for c in order: area_first[T[c]["functional_area"].split(";")[0]].append(pos[c])
res = dict(tasks=60, skills_read=skills_read, graph_links_used=graph_hits, fscr_tasks_with_any_prereq=sum(1 for c in T if fscr_dep[c]),
           fscr_prereq_links=sum(len(v) for v in fscr_dep.values()), oracle_links_total=len(out_links), oracle_links_sourced_rows=len(srcd),
           oracle_pairs_sourced=len(pairs), oracle_pairs_respected=len(resp), oracle_pairs_stated_by_fscr_skills=len(fst),
           unverified=sum(1 for l in out_links if l["status"] == "unverified"),
           unverified_but_plan_respects=sum(1 for l in out_links if l["status"] == "unverified" and l["plan_respects"]),
           violations=[(a, pos[a], b, pos[b]) for a, b in sorted(pairs - resp)],
           stated_only_pairs=len({(l["prereq"], l["task"]) for l in srcd if l["link_type"] == "stated"}),
           stated_only_respected=len({(l["prereq"], l["task"]) for l in srcd if l["link_type"] == "stated" and l["plan_respects"]}),
           area_order=[(a, min(p), max(p)) for a, p in sorted(area_first.items(), key=lambda kv: min(kv[1]))])
json.dump(res, open(RUN / "evidence/plan_summary.json", "w"), indent=1); json.dump({c: pos[c] for c in order}, open(RUN / "evidence/plan_order.json", "w"))
print(json.dumps(res, indent=1))
