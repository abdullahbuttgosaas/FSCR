"""Run 35 step 2 check (from Run 33/34): FSCR's Run Book (local plan + what Oracle stored) vs the same sourced Oracle links as the plan.
Also scrubs performer names from the saved Oracle task list (no user names in evidence)."""
import json, csv, collections
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
P = RUN / "evidence/runbook35_tasks.json"
d = json.load(open(P, encoding="utf-8-sig"))
for x in d["items"]:
    for k in ("PerformerName", "PerformerUsername"): x.pop(k, None)
json.dump(d, open(P, "w", encoding="utf-8"), indent=1)
plan = json.load(open(RUN / "runbook/runbook-plan.json", encoding="utf-8"))["tasks"]
ora = d["items"]
T = {r["task_code"]: r for r in csv.DictReader(open(RUN.parent / "_fscr_run_32_procurement_coverage/procurement_tasks.csv", encoding="utf-8")) if r["row_tag"] == "Purchasing"}
links = list(csv.DictReader(open(RUN / "oracle_links.csv", encoding="utf-8")))
pairs = sorted({(l["prereq"], l["task"]) for l in links if l["status"] == "sourced"})
upairs = sorted({(l["prereq"], l["task"]) for l in links if l["status"] == "unverified"})
name2code = {t["name"]: t["task_id"] for t in plan}
ora_order = sorted(ora, key=lambda x: (int(x["StageSequence"] or 0), int(x["Sequence"]), int(x["SubSequence"] or 0)))
opos = {name2code[x["Name"]]: i + 1 for i, x in enumerate(ora_order)}
ppos = {t["task_id"]: t["sequence"] for t in plan}
planpos = json.load(open(RUN / "evidence/plan_order.json"))
assert len(opos) == 16 and len(ppos) == 16
rows = []
for i, x in enumerate(ora_order, 1):
    c = name2code[x["Name"]]; p = next(t for t in plan if t["task_id"] == c)
    rows.append(dict(seq=i, task=x["Name"], task_code=c, stage=x["StageName"], oracle_type=x["TypeMeaning"], has_route=(x["Type"] == "ORA_CHK_DATA_LOADER"),
                     says_manual=(x["Type"] == "ORA_CHK_MANUAL"), manual_but_catalog_csv=(x["Type"] == "ORA_CHK_MANUAL" and T[c]["csv_flag"] == "Y"),
                     has_prerequisite=bool(x.get("DependentTaskName")), plan_depends_on=len(p.get("depends_on") or []), status=x["Status"]))
with open(RUN / "runbook/runbook_step_check.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
res = dict(steps=len(rows), with_route=sum(r["has_route"] for r in rows), manual=sum(r["says_manual"] for r in rows),
           manual_with_csv_route=sum(r["manual_but_catalog_csv"] for r in rows),
           with_prerequisite=sum(r["has_prerequisite"] for r in rows), plan_depends_on_total=sum(r["plan_depends_on"] for r in rows),
           sourced_links=len(pairs), respected_in_oracle_runbook=sum(opos[a] < opos[b] for a, b in pairs),
           unverified_out_of_order_in_runbook=sum(not opos[a] < opos[b] for a, b in upairs),
           same_order_as_plan=all(planpos[c] == opos[c] for c in opos), statuses=collections.Counter(r["status"] for r in rows),
           stages=collections.Counter(r["stage"] for r in rows),
           oracle_runbook_violations=[(a, opos[a], b, opos[b]) for a, b in pairs if not opos[a] < opos[b]])
json.dump(res, open(RUN / "runbook/runbook_summary.json", "w"), indent=1)
print(json.dumps(res, indent=1))
