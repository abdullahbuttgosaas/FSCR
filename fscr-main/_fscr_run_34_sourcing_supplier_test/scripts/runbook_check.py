"""Run 34 step 2 check (from Run 33): FSCR's Run Book (local plan + what Oracle stored) vs the same sourced Oracle links as the plan."""
import json, csv, collections
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
from api import WORK; W = WORK / "project/fscrt-r34-sourcing-supplier/artifacts/shared/runbook/current"
plan = json.load(open(W / "runbook-plan.json", encoding="utf-8"))["tasks"]
ora = json.load(open(RUN / "evidence/runbook34_tasks.json", encoding="utf-8-sig"))["items"]
links = [l for l in csv.DictReader(open(RUN / "oracle_links.csv", encoding="utf-8")) if l["status"] == "sourced"]
pairs = sorted({(l["prereq"], l["task"]) for l in links})
name2code = {t["name"]: t["task_id"] for t in plan}
ora_order = sorted(ora, key=lambda x: (int(x["StageSequence"] or 0), int(x["Sequence"]), int(x["SubSequence"] or 0)))
opos = {name2code[x["Name"]]: i + 1 for i, x in enumerate(ora_order)}
ppos = {t["task_id"]: t["sequence"] for t in plan}
assert len(opos) == 91 and len(ppos) == 91
rows = []
for i, x in enumerate(ora_order, 1):
    c = name2code[x["Name"]]; p = next(t for t in plan if t["task_id"] == c)
    rows.append(dict(seq=i, task=x["Name"], task_code=c, stage=x["StageName"], oracle_type=x["TypeMeaning"], has_route=(x["Type"] == "ORA_CHK_DATA_LOADER"),
                     says_manual=(x["Type"] == "ORA_CHK_MANUAL"), has_prerequisite=bool(x.get("DependentTaskName")), plan_depends_on=len(p.get("depends_on") or [])))
with open(RUN / "runbook/runbook_step_check.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
res = dict(steps=len(rows), with_route=sum(r["has_route"] for r in rows), manual=sum(r["says_manual"] for r in rows),
           with_prerequisite=sum(r["has_prerequisite"] for r in rows), plan_depends_on_total=sum(r["plan_depends_on"] for r in rows),
           links_checked=len(pairs), respected_local_plan=sum(ppos[a] < ppos[b] for a, b in pairs),
           respected_in_oracle_runbook=sum(opos[a] < opos[b] for a, b in pairs),
           same_order_as_plan=all(ppos[c] == opos[c] for c in opos),
           stages=collections.Counter(r["stage"] for r in rows),
           oracle_runbook_violations=[(a, opos[a], b, opos[b]) for a, b in pairs if not opos[a] < opos[b]])
json.dump(res, open(RUN / "runbook/runbook_summary.json", "w"), indent=1)
print(json.dumps(res, indent=1))
