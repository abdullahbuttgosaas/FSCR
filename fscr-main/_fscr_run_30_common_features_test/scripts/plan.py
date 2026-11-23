"""Run 30 step 2: FSCR plan for the 144 Common Features tasks + comparison with Oracle's documented order.
FSCR method = shared/implementation-planning/task-dependency-resolver: release catalog order (functionalAreaOrder, displaySequence),
graph enrichment (knowledge/dependency-graphs), plus prerequisites that the task's own FSCR skill files name. Read-only."""
import json, csv, re, collections
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]; F = RUN.parent / "fscr-main"
rows = list(csv.DictReader(open(RUN.parent / "_fscr_run_29_common_features/common_features_tasks.csv", encoding="utf-8")))
T = {r["task_code"]: r for r in rows}
cat = json.load(open(F / "knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json", encoding="utf-8"))["offerings"]
pm = {i["offeringShortName"]: i["pillar"] for i in json.load(open(F / "knowledge/setup-task-catalog/effective/pillars-offerings-mapping.json", encoding="utf-8"))["items"]}
AREAS = ["ORA_ASK_INITIAL_USER", "ORA_ASK_ENTERPRISE_PROFILE", "ORA_ASK_LEGAL_STRUCTURES", "ORA_ASK_FIN_REPORTING_STRUCT",
         "ORA_ASK_ORGANIZATION_STRUCTURE", "ORA_ASK_WORKFORCE_STRUCTURE", "ORA_ASK_USERS_AND_SECURITY", "ORA_ASK_APPLICATION_EXTENSIONS"]
# primary context = Financials offering; other ERP offerings fill tasks Financials lacks (resolver keeps that context's catalog sequence)
offs = ["XLE_FINANCIALS_JUR"] + sorted(o for o in cat if pm.get(o) == "ERP" and o != "XLE_FINANCIALS_JUR")
seq = {}
for oi, o in enumerate(offs):
    for a in AREAS:
        fa = cat[o]["functionalAreas"].get(a)
        if not fa: continue
        for t in fa["tasks"]:
            c = t["taskShortName"]
            if c in T and c not in seq:
                seq[c] = (AREAS.index(a), oi, int(t["displaySequence"]), o, fa["functionalAreaName"])
assert len(seq) == 144, len(seq)
order = sorted(seq, key=lambda c: seq[c][:3])
pos = {c: i + 1 for i, c in enumerate(order)}
names = {c: T[c]["task_name"] for c in T}

def skill_text(c):
    out = ""
    for p in [x.strip() for x in T[c]["skill_paths"].split("|") if x.strip()]:
        fp = F / p; d = fp.parent
        files = {fp, *d.glob("ora-resource/*readiness*.md")}
        for f in files:
            try: out += f.read_text(encoding="utf-8", errors="ignore") + "\n"
            except OSError: pass
    return out

# FSCR-declared prerequisites: other Common Features tasks named in the task's own skill / readiness file
fscr_dep = collections.defaultdict(set)
for c in T:
    txt = skill_text(c)
    if not txt: continue
    low = txt.lower()
    for d, n in names.items():
        if d != c and (d in txt or re.search(r"\b" + re.escape(n.lower()) + r"\b", low)):
            fscr_dep[c].add(d)
g = json.load(open(F / "knowledge/dependency-graphs/hcm-dependency-graph.json", encoding="utf-8"))
graph_hits = 0
for n in g["nodes"]:
    for t in n.get("taskCallSequence", []):
        c = t["id"].split(":", 1)[-1]
        for dep in t.get("dependsOn", []):
            d = str(dep).split(":", 1)[-1]
            if c in T and d in T: fscr_dep[c].add(d); graph_hits += 1

# Oracle documented prerequisites (prereq -> task). Sources listed in RESULT.md / ORACLE_SOURCES.md
ORA = [
 ("FND_CREATE_IMPLEMENTATION_USERS", "FND_CREATE_DATA_ROLE_FOR_IMPLEMENTATION_USERS"),
 ("FND_MANAGE_REFERENCE_DATA_SETS", "FND_MANAGE_REFERENCE_DATA_SET_ASSIGNMENTS"),
 ("FND_MANAGE_REFERENCE_DATA_SETS", "FUN_MANAGE_BUSINESS_UNIT"),
 ("HZ_MANAGE_GEOGRAPHIES", "XLE_MANAGE_LEGAL_ADDRESSES"),
 ("HZ_MANAGE_GEOGRAPHIES", "PER_MANAGE_LOCATIONS"),
 ("XLE_MANAGE_LEGAL_JURISDICTIONS", "XLE_MANAGE_LEGAL_AUTHORITIES"),
 ("XLE_MANAGE_LEGAL_JURISDICTIONS", "XLE_MANAGE_LEGAL_ENTITY_REGISTRATIONS"),
 ("XLE_MANAGE_LEGAL_ADDRESSES", "XLE_MANAGE_LEGAL_ENTITY"),
 ("XLE_MANAGE_LEGAL_ENTITY", "XLE_MANAGE_LEGAL_ENTITY_REGISTRATIONS"),
 ("XLE_MANAGE_LEGAL_ENTITY", "XLE_MANAGE_LEGAL_REPORTING_UNIT"),
 ("XLE_MANAGE_LEGAL_REPORTING_UNIT", "XLE_MANAGE_LEGAL_REPORTING_UNIT_REGISTRATIONS"),
 ("GL_MANAGE_CHART_OF_ACCOUNTS_VALUE_SETS", "GL_MANAGE_CHARTS_OF_ACCOUNTS"),
 ("GL_MANAGE_CHARTS_OF_ACCOUNTS", "GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES"),
 ("GL_MANAGE_CHART_OF_ACCOUNTS_VALUE_SETS", "GL_MANAGE_CHART_OF_ACCOUNTS_VALUE_SET_VALUES"),
 ("GL_MANAGE_CHART_OF_ACCOUNTS_VALUE_SET_VALUES", "GL_MANAGE_ACCOUNT_HIERARCHIES"),
 ("GL_MANAGE_ACCOUNT_HIERARCHIES", "GL_SELECT_AGGREGATION_OPTIONS_FOR_ACCOUNT_HIERARCHIES"),
 ("GL_MANAGE_CROSS-VALIDATION_RULES", "GL_MANAGE_ACCOUNT_COMBINATIONS"),
 ("FND_MANAGE_CURRENCIES", "GL_MANAGE_CONVERSION_RATE_TYPES"),
 ("GL_MANAGE_CONVERSION_RATE_TYPES", "GL_MANAGE_DAILY_RATES"),
 ("GL_MANAGE_CHARTS_OF_ACCOUNTS_STRUCTURE_INSTANCES", "GL_MANAGE_PRIMARY_LEDGERS"),
 ("GL_MANAGE_ACCOUNTING_CALENDARS", "GL_MANAGE_PRIMARY_LEDGERS"),
 ("FND_MANAGE_CURRENCIES", "GL_MANAGE_PRIMARY_LEDGERS"),
 ("GL_MANAGE_PRIMARY_LEDGERS", "GL_SPECIFY_LEDGER_OPTIONS"),
 ("GL_MANAGE_PRIMARY_LEDGERS", "GL_ASSIGN_LEGAL_ENTITIES"),
 ("XLE_MANAGE_LEGAL_ENTITY", "GL_ASSIGN_LEGAL_ENTITIES"),
 ("GL_ASSIGN_LEGAL_ENTITIES", "GL_ASSIGN_BALANCING_SEGMENT_VALUES_TO_LEGAL_ENTITIES"),
 ("GL_MANAGE_CHART_OF_ACCOUNTS_VALUE_SET_VALUES", "XLE_MANAGE_ASSOCIATED_BALANCING_SEGMENTS"),
 ("GL_MANAGE_PRIMARY_LEDGERS", "GL_ASSIGN_BALANCING_SEGMENT_VALUES_TO_LEDGER"),
 ("GL_SPECIFY_LEDGER_OPTIONS", "GL_REVIEW_AND_SUBMIT_ACCOUNTING_CONFIGURATION"),
 ("GL_ASSIGN_LEGAL_ENTITIES", "GL_REVIEW_AND_SUBMIT_ACCOUNTING_CONFIGURATION"),
 ("GL_REVIEW_AND_SUBMIT_ACCOUNTING_CONFIGURATION", "FUN_MANAGE_BUSINESS_UNIT"),
 ("FUN_MANAGE_BUSINESS_UNIT", "FUN_ASSIGN_BUSINESS_UNIT_BUSINESS_FUNCTION"),
 ("FUN_MANAGE_BUSINESS_UNIT", "FUN_MANAGE_BUSINESS_UNIT_SET_ASSIGNMENT"),
 ("FUN_ASSIGN_BUSINESS_UNIT_BUSINESS_FUNCTION", "FUN_MANAGE_SERVICE_PROVIDER_RELATIONSHIPS"),
 ("FUN_MANAGE_BUSINESS_UNIT", "ORA_FUN_MANAGE_BUSINESS_UNIT_DATA_ACCESS_FOR_USERS"),
 ("PER_MANAGE_LOCATIONS", "PER_MANAGE_DEPARTMENT"),
 ("PER_MANAGE_JOB_FAMILY", "PER_MANAGE_JOB"),
 ("GL_MANAGE_PRIMARY_LEDGERS", "GL_MANAGE_DATA_ACCESS_SETS"),
 ("ASXS_MANAGE_DUTIES", "ASXS_MANAGE_JOB_ROLES"),
 ("FND_MANAGE_APPLCORE_VALUE_SETS", "FND_MANAGE_APPLCORE_DESCRIPTIVE_FLEXFIELDS"),
]
for a, b in ORA: assert a in T and b in T, (a, b)
edge_rows = [dict(prereq=a, task=b, prereq_seq=pos[a], task_seq=pos[b], fscr_order_ok=pos[a] < pos[b], fscr_states_it=a in fscr_dep[b]) for a, b in ORA]
ok = sum(e["fscr_order_ok"] for e in edge_rows); st = sum(e["fscr_states_it"] for e in edge_rows)
in_edges = {c for e in ORA for c in e}
bad_tasks = {c for e in edge_rows if not e["fscr_order_ok"] for c in (e["prereq"], e["task"])}
with open(RUN / "plan.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["seq", "task_code", "task_name", "functional_area", "catalog_offering", "catalog_display_sequence",
                "fscr_prerequisites", "oracle_prerequisites", "order_vs_oracle"])
    for c in order:
        a, oi, ds, o, an = seq[c]
        orq = [x for x, y in ORA if y == c]
        w.writerow([pos[c], c, names[c], an, cat[o]["offeringName"], ds, "; ".join(sorted(fscr_dep[c])), "; ".join(orq),
                    "violates" if c in bad_tasks else ("ok" if c in in_edges else "no Oracle rule")])
with open(RUN / "evidence/oracle_edges_check.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(edge_rows[0])); w.writeheader(); w.writerows(edge_rows)
res = dict(tasks=144, not_in_financials_offering=sum(1 for c in T if seq[c][1] != 0),
           fscr_tasks_with_any_prereq=sum(1 for c in T if fscr_dep[c]), fscr_prereq_links=sum(len(v) for v in fscr_dep.values()),
           graph_links=graph_hits, oracle_edges=len(ORA), edges_order_ok=ok, edges_stated_by_fscr=st,
           tasks_in_oracle_rules=len(in_edges), tasks_in_rules_order_ok=len(in_edges - bad_tasks),
           tasks_order_ok_all=144 - len(bad_tasks),
           violations=[(e["prereq"], e["prereq_seq"], e["task"], e["task_seq"]) for e in edge_rows if not e["fscr_order_ok"]])
json.dump(res, open(RUN / "evidence/plan_summary.json", "w"), indent=1)
print(json.dumps(res, indent=1))
