"""Build offering task map from selection.json + FSCR effective catalog; resolve skill paths with FSCR's
offering-task-map-builder (task_to_skill_mapping.build_task_to_skill_mapping). Paper only."""
import json, sys, csv
from pathlib import Path
RUN = Path(sys.argv[1]).resolve(); REPO = RUN / "repo"
sys.path.insert(0, str(REPO / "core/runbook/scripts"))
sys.path.insert(0, str(REPO / "shared/implementation-planning/offering-task-map-builder/scripts"))
from task_to_skill_mapping import build_task_to_skill_mapping
cat = json.load(open(REPO/"knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json", encoding="utf-8"))
rel = json.load(open(REPO/"knowledge/setup-task-catalog/release/offering-functional-area-task-catalog.json", encoding="utf-8"))
allt = json.load(open(REPO/"knowledge/setup-task-catalog/effective/setupTasksAll.json", encoding="utf-8"))["items"]
name_count = {}
for it in allt:
    n = " ".join(str(it.get("TaskName","")).split()).casefold(); name_count[n] = name_count.get(n,0)+1
sel = json.load(open(RUN/"work/scripts/selection.json", encoding="utf-8"))
rows = []; fa_summary = []
for off in sel["offerings"]:
    o = cat["offerings"][off["code"]]
    ro = rel.get("offerings", {}).get(off["code"], {})
    for fa_code, why in off["fas"]:
        fa = o["functionalAreas"][fa_code]
        rfa = ro.get("functionalAreas", {}).get(fa_code, {})
        rel_ids = {t["taskListItemShortName"] for t in rfa.get("tasks", [])}
        tasks = fa["tasks"]
        def key(t):
            ds = t.get("displaySequence")
            return (0, int(ds)) if ds not in (None, "") else (1, t["taskShortName"])
        tasks = sorted(tasks, key=key)
        fa_summary.append({"offering": off["code"], "offering_name": o["offeringName"], "status": off["status"], "fa": fa_code,
                           "fa_name": fa["functionalAreaName"], "tasks": len(tasks), "sow_basis": why})
        for t in tasks:
            n = " ".join(t["taskName"].split())
            rows.append({"Offering": o["offeringName"], "Offering Code": off["code"], "Pillar": off["pillar"],
                "Offering Status": off["status"], "Functional Area": fa["functionalAreaName"], "Functional Area Code": fa_code,
                "Source Task Name": n, "Task Code": t["taskShortName"], "Task List Item": t["taskListItemShortName"],
                "Catalog Display Sequence": t.get("displaySequence"), "Mandatory": t.get("MandatoryFlag"),
                "Source Layer": "release" if t["taskListItemShortName"] in rel_ids else "pre_release/custom",
                "SOW Basis": why, "Requested Phase": "build", "Name Matches In setupTasksAll": name_count.get(n.casefold(),0)})
# resolver-style sequence (Claude applying task-dependency-resolver step 2/5/6 by hand: catalog order, tails last)
for i, r in enumerate(rows, 1):
    r["Resolver Sequence"] = i
    r["Sequence Source"] = "release" if r["Catalog Display Sequence"] not in (None, "") else "functional_area_tail"
# FSCR skill path resolution
plan = {"plan": {"offering": "Multiple Offerings", "functional_area": "Multiple Functional Areas",
        "tasks": [{"name": r["Source Task Name"], "sequence": r["Resolver Sequence"], "offering": r["Offering"],
                   "functional_area": r["Functional Area"], "offering_code": r["Offering Code"]} for r in rows]}}
m = build_task_to_skill_mapping(REPO, plan)
by_seq = {t["sequence"]: t for t in m["tasks"]}
for r in rows:
    t = by_seq[r["Resolver Sequence"]]
    r["Skill Path"] = t.get("skill_path") or t.get("execution_skill_path")
    r["Skill Match"] = t.get("skill_selection", {}).get("selected_by") if t.get("match_status") == "matched" else "unmatched: " + t.get("match_reason","")[:120]
out = RUN/"outputs"
json.dump({"project": "Twelve Oracle Cloud SCM (SOW 50513scm)", "tasks": rows}, open(RUN/"work/identified-task-mapping.json","w",encoding="utf-8"), indent=1)
with open(out/"01_offering_task_map.csv","w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(fa_summary, open(RUN/"work/fa_summary.json","w",encoding="utf-8"), indent=1)
uniq = len({r["Task Code"] for r in rows})
skills = sum(1 for r in rows if r["Skill Path"] and "manual-tasks" not in r["Skill Path"])
print("rows", len(rows), "unique task codes", uniq, "with pillar skill", skills,
      "tail", sum(r["Sequence Source"]=="functional_area_tail" for r in rows),
      "ambiguous names", sum(r["Name Matches In setupTasksAll"]!=1 for r in rows))
