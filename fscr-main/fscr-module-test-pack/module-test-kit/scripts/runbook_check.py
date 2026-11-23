"""Step 3 - Run Book check. Count what FSCR's Run Book gives a consultant and test its order against the Oracle links.

Usage:
  python runbook_check.py --runbook-plan <project>/.../runbook-plan.json --scope work/X/scope_tasks.csv \
      --links work/X/oracle_links.csv --out work/X
  add --oracle-tasks runbook_tasks.json   (the Run Book's task list as Oracle stored it, if you read it back)

Inputs:
  runbook-plan.json  written by FSCR core/runbook when it builds the Run Book (keys: tasks[].task_id, name,
                     sequence, taskType, depends_on)
  oracle tasks JSON  optional; {"items": [...]} with Name, Type, TypeMeaning, StageName, StageSequence, Sequence,
                     SubSequence, DependentTaskName, Status. Performer names and Oracle self links (they hold your
                     environment's host name) are removed from the copy this script keeps.
Counts per step: has a route (Data Loader type), says manual, manual although the catalog has a CSV route,
has a prerequisite. Owner and validation fields are NOT used as criteria (they are empty by design in FSCR).
Writes runbook_step_check.csv and runbook_summary.json. Read only. No sign-in, no network.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys

from kitlib import Path, read_csv, write_csv, write_json

ROUTE = "ORA_CHK_DATA_LOADER"
MANUAL = "ORA_CHK_MANUAL"
DROP = ("PerformerName", "PerformerUsername", "PerformerUserName", "CreatedBy", "LastUpdatedBy", "Owner", "OwnerName")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runbook-plan", type=Path, required=True)
    ap.add_argument("--scope", type=Path, required=True, help="scope_tasks.csv")
    ap.add_argument("--links", type=Path, help="oracle_links.csv from plan_builder.py")
    ap.add_argument("--oracle-tasks", type=Path, help="Run Book tasks read back from Oracle (JSON)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    plan = json.loads(a.runbook_plan.read_text(encoding="utf-8-sig"))["tasks"]
    T = {r["task_code"]: r for r in read_csv(a.scope)}
    by_code = {t["task_id"]: t for t in plan}
    name2code = {t["name"]: t["task_id"] for t in plan}

    steps = []
    if a.oracle_tasks:
        d = json.loads(a.oracle_tasks.read_text(encoding="utf-8-sig"))
        items = d.get("items", d if isinstance(d, list) else [])
        for x in items:
            for k in DROP + ("links", "@context"):  # Oracle self links carry the environment's host name
                x.pop(k, None)
        write_json(a.out / "runbook_tasks_oracle_clean.json", {"items": items})
        items.sort(key=lambda x: (int(x.get("StageSequence") or 0), int(x.get("Sequence") or 0), int(x.get("SubSequence") or 0)))
        for i, x in enumerate(items, 1):
            c = name2code.get(x["Name"], "")
            steps.append(dict(seq=i, task=x["Name"], task_code=c, stage=x.get("StageName", ""), type=x.get("Type", ""),
                              has_prerequisite=bool(x.get("DependentTaskName")), status=x.get("Status", ""),
                              plan_depends_on=len((by_code.get(c) or {}).get("depends_on") or [])))
        source = "Oracle Run Book read back"
    else:
        for t in sorted(plan, key=lambda t: int(t.get("sequence") or 0)):
            steps.append(dict(seq=int(t.get("sequence") or 0), task=t["name"], task_code=t["task_id"],
                              stage=f"{t.get('offering', '')} - {t.get('functional_area', '')}", type=t.get("taskType", ""),
                              has_prerequisite=bool(t.get("depends_on")), status="(local plan)",
                              plan_depends_on=len(t.get("depends_on") or [])))
        source = "FSCR runbook-plan.json (local)"
    for s in steps:
        s["has_route"] = s["type"] == ROUTE
        s["says_manual"] = s["type"] == MANUAL
        s["manual_but_catalog_csv"] = s["says_manual"] and T.get(s["task_code"], {}).get("csv_flag") == "Y"
        s["in_module_scope"] = s["task_code"] in T
    fields = ["seq", "task", "task_code", "stage", "type", "has_route", "says_manual", "manual_but_catalog_csv",
              "has_prerequisite", "plan_depends_on", "in_module_scope", "status"]
    write_csv(a.out / "runbook_step_check.csv", steps, fields)

    pos = {s["task_code"]: s["seq"] for s in steps if s["task_code"]}
    links = read_csv(a.links) if a.links else []
    src = [(l["prereq"], l["task"]) for l in links if l["status"] == "sourced"]
    unv = [(l["prereq"], l["task"]) for l in links if l["status"] == "unverified"]
    known = [(p, t) for p, t in src if p in pos and t in pos]
    res = dict(source=source, steps=len(steps), with_route=sum(s["has_route"] for s in steps),
               manual=sum(s["says_manual"] for s in steps), manual_with_csv_route=sum(s["manual_but_catalog_csv"] for s in steps),
               with_prerequisite=sum(s["has_prerequisite"] for s in steps),
               plan_depends_on_total=sum(s["plan_depends_on"] for s in steps),
               module_tasks=len(T), module_tasks_missing_from_runbook=sorted(set(T) - set(pos)),
               steps_outside_module=sum(1 for s in steps if not s["in_module_scope"]),
               sourced_links=len(src), sourced_links_found_in_runbook=len(known),
               respected_in_runbook=sum(1 for p, t in known if pos[p] < pos[t]),
               runbook_violations=[[p, pos[p], t, pos[t]] for p, t in known if pos[p] >= pos[t]],
               unverified_out_of_order_in_runbook=sum(1 for p, t in unv if p in pos and t in pos and pos[p] >= pos[t]),
               statuses=dict(collections.Counter(s["status"] for s in steps)))
    write_json(a.out / "runbook_summary.json", res)
    print(f"Run Book ({source}): {res['steps']} steps | route {res['with_route']} | manual {res['manual']} "
          f"({res['manual_with_csv_route']} have a CSV route) | prerequisites {res['with_prerequisite']}")
    if links:
        print(f"Sourced links in order in the Run Book: {res['respected_in_runbook']} of {res['sourced_links_found_in_runbook']}")
    if res["module_tasks_missing_from_runbook"]:
        print(f"Module tasks not in the Run Book: {len(res['module_tasks_missing_from_runbook'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
