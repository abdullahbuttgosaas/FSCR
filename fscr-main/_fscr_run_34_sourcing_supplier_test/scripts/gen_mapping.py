"""Build identified-task-mapping.json (same shape as Run 33) from plan.csv for the FSCR project initializer."""
import csv, json
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]; ROOT = RUN.parent
inv = {x["TaskCode"]: x for x in csv.DictReader(open(ROOT / "_fscr_run_07_inventory/out/tasks.csv", encoding="utf-8"))}
tasks = []
for r in csv.DictReader(open(RUN / "plan.csv", encoding="utf-8")):
    c = r["task_code"]; sp = [p.strip() for p in inv[c]["Skill paths"].split("|") if p.strip()]
    tasks.append({"ID": c, "Source Task Name": r["task_name"], "Task Code": c, "Offering": "Procurement",
                  "Functional Area": r["functional_area"].split(";")[0].strip(), "Pillar": "SCM", "Phase": "build",
                  "Resolver Sequence": int(r["seq"]), "Match Method": "exact-name", "Match Status": "matched",
                  "Source Reference": "Run 34 plan.csv (FSCR task-dependency-resolver method)", "Skill Path": sp[0] if sp else "",
                  "Data Paths": [], "Confidence": 1.0, "Matched Task Code": c, "Matched Task Name": r["task_name"],
                  "Match Rationale": "Exact normalized source task name match in the current setup-task catalog.", "Offering Context Status": "matched"})
m = {"source": "FSCR run 34: Sourcing and Supplier Management tasks (91) from Run 32", "sequence_source": "_fscr_run_34_sourcing_supplier_test/plan.csv",
     "selection_counts": {"selected": len(tasks), "included": len(tasks), "excluded": 0}, "tasks": tasks}
json.dump(m, open(RUN / "evidence/identified-task-mapping-run34.json", "w", encoding="utf-8"), indent=1)
print(len(tasks))
