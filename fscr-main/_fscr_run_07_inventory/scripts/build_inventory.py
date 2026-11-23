"""Run 07 inventory: join files and outputs we already have. Read-only; no network, no Oracle.

Inputs (read only):
  REPO  = original FSCR repo (catalogs, SKILL.md front matter, folder listing)
  AUDIT = _fscr_spec/ROUTE_AUDIT/02_route_audit.out.json  (route audit, 2026-11-02; per-file routes)
  R04   = _fscr_run_04_create16/ledger.csv                 (Run 04 scorecard for the 16 adapters)
  R05   = _fscr_run_05_breadth/ledger.csv                  (Run 05 sample, exported task codes)
Outputs: ../out/*.csv and summary.json (consumed by write_workbook.py).

Definitions computed here (everything else is copied from the inputs):
  area (task)    = pillar of the linked FSCR skill file(s) (route audit), else the pillar(s) of the catalog
                   offerings that contain the task (offering-functional-area-task-catalog + pillars-offerings-mapping).
  own script     = the skill file's folder has a scripts/ folder holding .py or .sh files.
  adapter        = the skill file's folder has e2e-adapter.json.
  leaf skill     = folder holding SKILL.md (any case) with no other such folder beneath it (rule behind 934).
"""
import csv, json, os, re, collections

BASE = r"E:\GoSaaS\Configuration Automation v2.1\fscr-main"
REPO = os.path.join(BASE, "fscr-main")
OUT = os.path.join(BASE, "_fscr_run_07_inventory", "out")
os.makedirs(OUT, exist_ok=True)
CAT = os.path.join(REPO, "knowledge", "setup-task-catalog", "effective")

audit = json.load(open(os.path.join(BASE, "_fscr_spec", "ROUTE_AUDIT", "02_route_audit.out.json"), encoding="utf-8"))
catalog = json.load(open(os.path.join(CAT, "setupTasksAll.json"), encoding="utf-8"))["items"]
ofa = json.load(open(os.path.join(CAT, "offering-functional-area-task-catalog.json"), encoding="utf-8"))["offerings"]
pmap = {i["offeringShortName"]: i["pillar"] for i in json.load(open(os.path.join(CAT, "pillars-offerings-mapping.json"), encoding="utf-8"))["items"]}

# --- task -> offerings / pillars (catalog join)
task_offerings = collections.defaultdict(set)
for code, off in ofa.items():
    for fa in off.get("functionalAreas", {}).values():
        for t in fa.get("tasks", []):
            task_offerings[t["taskShortName"]].add(code)

def folder_facts(rel_path):
    d = os.path.join(REPO, os.path.dirname(rel_path))
    sd = os.path.join(d, "scripts")
    has_script = os.path.isdir(sd) and any(f.endswith((".py", ".sh")) for _, _, fs in os.walk(sd) for f in fs)
    return has_script, os.path.isfile(os.path.join(d, "e2e-adapter.json"))

def route_label(rec):
    if rec["routes"]:
        return rec["routes"]
    if rec.get("manual"):
        return ["MANUAL_ONLY"]
    if rec.get("unclear"):
        return ["UNCLEAR"]
    return ["NONE_DECLARED"]

by_task = collections.defaultdict(list)
for rec in audit["skills"]:
    rec["_routes"] = route_label(rec)
    rec["_script"], rec["_adapter"] = folder_facts(rec["path"])
    by_task[rec["task_code"]].append(rec)

# --- Run 04 scorecard and Run 05 exported tasks
r04 = {}
for r in csv.DictReader(open(os.path.join(BASE, "_fscr_run_04_create16", "ledger.csv"), encoding="utf-8")):
    s = r["final_status"].lower()
    r04[r["task_code"]] = ("failed" if s.startswith("failed") else
                           "blocked: no safe target" if "missing safe target" in s else
                           "blocked by FSCR guard" if s.startswith("blocked") else
                           "works with a patch" if "patch" in s else "works unmodified")
r05 = {r["task_code"] for r in csv.DictReader(open(os.path.join(BASE, "_fscr_run_05_breadth", "ledger.csv"), encoding="utf-8"))
       if r["task_code"] and "template ok" in r["export_result"]}

TESTED = {  # from run reports (Runs 01-06); task code -> what we did
    "FUN_MANAGE_BUSINESS_UNIT": "R01 create (own builder + FSCR import); R02 read (export); R03 update refused by FSCR rule",
    "AR_MANAGE_RECEIVABLES_PAYMENT_TERMS": "R01 create (patched script); R02 read + reconcile; R03 end-date change; R04 S1",
    "DOO_MANAGE_ORCHESTRATION_LOOKUPS": "R01 create via REST route (own bodies); R02 read; R03 change; R06 new requirements",
    "CUSTOM_IMPORT_PRICE_LISTS": "R01 FBDI route not runnable on pod; price lists done with own REST",
    "AR_MANAGE_AUTOINVOICE_GROUPING_RULES": "R04 S8 create; R06 new rule FSCRT_GRP6",
}
for code, st in r04.items():
    TESTED.setdefault(code, f"R04 {st}")
for code in r05:
    TESTED.setdefault(code, "R05 export only (read)")

MANUALISH = {"MANUAL_ONLY", "NONE_DECLARED", "UNCLEAR"}
WORKED = {"works unmodified", "works with a patch"}

def status(code, flag, recs):
    if code in r04:
        st = r04[code]
        return ("1 Adapter: created a record in our tests" if st in WORKED else
                "3 Adapter: not tested (no safe target)" if st == "blocked: no safe target" else
                "2 Adapter: failed or blocked in our tests")
    if recs:
        routes = {x for r in recs for x in r["_routes"]}
        return "5 Skill: manual steps or no route" if routes <= MANUALISH else "4 Skill: route named, no create recipe"
    return "6 No skill: FSCR export/read only (CSV flag Y)" if flag == "Y" else "7 No skill: no FSCR route (CSV flag N/UNKNOWN)"

tasks = []
for it in catalog:
    code = it["TaskCode"]
    recs = by_task.get(code, [])
    offs = task_offerings.get(code, set())
    # 12 offerings have an empty pillar in pillars-offerings-mapping.json; shown as "Unmapped", never guessed
    opillars = sorted({pmap.get(o) or "Unmapped" for o in offs})
    real = [p for p in opillars if p != "Unmapped"]
    spillars = sorted({r["pillar"] for r in recs})
    if spillars:
        area, basis = "/".join(spillars), "FSCR skill pillar"
    elif len(real) == 1:
        area, basis = real[0], "catalog offering pillar" + (" (also in an unmapped offering)" if "Unmapped" in opillars else "")
    elif real:
        area, basis = "Multiple", "catalog offering pillars: " + ", ".join(opillars)
    elif opillars:
        area, basis = "Unmapped offering", "only in offerings with no pillar in pillars-offerings-mapping.json"
    else:
        area, basis = "No offering", "task not in any enabled offering"
    kinds = {r["kind"] for r in recs}
    skill = ("both" if kinds == {"skill", "task guide"} else "SKILL.md" if kinds == {"skill"}
             else "task guide only" if kinds else "none")
    flag = it.get("CSVExportImportSupportedFlag") or "UNKNOWN"
    tasks.append({
        "TaskCode": code, "TaskName": it.get("TaskName", ""), "Area": area, "Area basis": basis,
        "Offering pillars": ", ".join(opillars), "Offerings": len(offs),
        "CSV export/import (catalog)": flag, "Export/import flag (catalog)": it.get("ExportImportSupportedFlag") or "UNKNOWN",
        "Skill": skill, "Skill files": len(recs),
        "Route(s) declared": ", ".join(sorted({x for r in recs for x in r["_routes"]})) or "-",
        "Own script": "Y" if any(r["_script"] for r in recs) else "N",
        "Adapter": "Y" if any(r["_adapter"] for r in recs) else "N",
        "Run 04 result": r04.get(code, ""), "Tested in our runs": TESTED.get(code, ""),
        "Status": status(code, flag, recs),
        "Skill paths": " | ".join(r["path"] for r in recs),
    })

# --- leaf skills (934 rule)
skill_dirs = set()
for root, dirs, files in os.walk(REPO):
    dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "project")]
    if any(f.lower() == "skill.md" for f in files):
        skill_dirs.add(os.path.relpath(root, REPO).replace("\\", "/"))
leaf = sorted(d for d in skill_dirs if not any(o != d and o.startswith(d + "/") for o in skill_dirs))
audit_by_path = {r["path"]: r for r in audit["skills"]}

def front(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    m = re.match(r"---\s*\n(.*?)\n---", txt, re.S)
    out = {}
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
            if mm:
                out[mm.group(1)] = mm.group(2).strip().strip('"').strip("'")
    return out

AREA = {"erp": "ERP", "hcm": "HCM", "scm": "SCM", "cx": "CX", "common": "Common"}
skills = []
for d in leaf:
    fn = next(f for f in os.listdir(os.path.join(REPO, d)) if f.lower() == "skill.md")
    rel = f"{d}/{fn}"
    fm = front(os.path.join(REPO, rel))
    parts = d.split("/")
    area = AREA.get(parts[1], parts[1]) if parts[0] == "pillars" else parts[0].capitalize()
    rec = audit_by_path.get(rel)
    guides = [r for r in audit["skills"] if r["kind"] == "task guide" and os.path.dirname(r["path"]) == d]
    script, adapter = folder_facts(rel)
    skills.append({
        "Skill path": rel, "Skill id": fm.get("name", ""), "Area": area, "Type": fm.get("type", ""),
        "Execution mode": fm.get("execution_mode", ""),
        "Task code (SKILL.md)": rec["task_code"] if rec else fm.get("task_code", ""),
        "Task codes (task guides in folder)": ", ".join(sorted({g["task_code"] for g in guides})),
        "Route(s) declared": ", ".join(rec["_routes"]) if rec else ("-" if not guides else "see guides: " + ", ".join(sorted({x for g in guides for x in g["_routes"]}))),
        "Own script": "Y" if script else "N", "Adapter": "Y" if adapter else "N",
        "Run 04 result": r04.get(rec["task_code"], "") if rec else "",
    })

def write(name, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

write("tasks.csv", tasks)
write("skills_leaf.csv", skills)

# --- summaries
AREAS = ["ERP", "SCM", "HCM", "CX", "Common", "Multiple", "Unmapped offering", "No offering"]
def area_key(a):
    return a if a in AREAS else "Multiple"   # e.g. 'CX/SCM' when a task has skills in two pillars
status_by_area = collections.defaultdict(collections.Counter)
for t in tasks:
    status_by_area[t["Status"]][area_key(t["Area"])] += 1

route_task = collections.defaultdict(collections.Counter)
for t in tasks:
    if t["Skill"] == "none":
        continue
    for r in t["Route(s) declared"].split(", "):
        route_task[r][area_key(t["Area"])] += 1

nos = [t for t in tasks if t["Skill"] == "none"]
summary = {
    "tasks": len(tasks), "tasks_with_skill": sum(t["Skill"] != "none" for t in tasks),
    "csv_flag": collections.Counter(t["CSV export/import (catalog)"] for t in tasks),
    "area_counts": collections.Counter(area_key(t["Area"]) for t in tasks),
    "area_basis": collections.Counter(t["Area basis"].split(":")[0] for t in tasks),
    "status_by_area": {k: dict(v) for k, v in sorted(status_by_area.items())},
    "route_tasks_by_area": {k: dict(v) for k, v in sorted(route_task.items())},
    "no_skill_by_flag": collections.Counter(t["CSV export/import (catalog)"] for t in nos),
    "no_skill_flag_by_area": {f: dict(collections.Counter(area_key(t["Area"]) for t in nos if t["CSV export/import (catalog)"] == f)) for f in ("Y", "N", "UNKNOWN")},
    "tasks_own_script": sum(t["Own script"] == "Y" for t in tasks),
    "tasks_adapter": sum(t["Adapter"] == "Y" for t in tasks),
    "fsm_no_adapter": sum("FSM_CSV" in t["Route(s) declared"] and t["Adapter"] == "N" for t in tasks),
    "rest_no_adapter": sum("REST" in t["Route(s) declared"] and t["Adapter"] == "N" for t in tasks),
    "rest_only_tasks": sum(t["Route(s) declared"] == "REST" for t in tasks),
    "hdl_tasks": sum("HDL" in t["Route(s) declared"] for t in tasks),
    "fbdi_tasks": sum("FBDI" in t["Route(s) declared"] for t in tasks),
    "release_drift_adapters": None,
    "leaf_skills": len(skills),
    "leaf_by_area": collections.Counter(s["Area"] for s in skills),
    "leaf_own_script": sum(s["Own script"] == "Y" for s in skills),
    "leaf_own_script_by_area": collections.Counter(s["Area"] for s in skills if s["Own script"] == "Y"),
    "leaf_with_task_code": sum(bool(s["Task code (SKILL.md)"] or s["Task codes (task guides in folder)"]) for s in skills),
    "leaf_types": collections.Counter(s["Type"] or "(none)" for s in skills),
    "leaf_modes": collections.Counter(s["Execution mode"] or "(none)" for s in skills),
    "skill_dirs_total": len(skill_dirs),
}
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8"), indent=1, default=dict)
print(json.dumps(summary, indent=1, default=dict))
