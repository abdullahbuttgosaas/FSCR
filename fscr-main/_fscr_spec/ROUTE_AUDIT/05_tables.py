"""Route audit step 5 (read-only): tables for the report, computed from 02_route_audit.out.json only.

- REST split by the kind of evidence (a unit can have several kinds):
    data_loader_bo   frontmatter REST mode with a business object, or the "Download Fusion Data Loader Sample" section
    rest_file        ora-resource/ora_rest_execution.md exists (its content may still say TBD / stop)
    task_rest        depends_on core.data-loader.task-rest / fscr-task-rest
    rest_mode_only   frontmatter REST mode, no business object, not disclaimed
    depends_only     only a depends_on to a REST core service (core.fusion-api.rest-api-client / apps-common)
- the catalog comparison with 10 examples of each contradiction and of "no route to compare".
Writes 05_tables.out.txt.
"""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.loads((HERE / "02_route_audit.out.json").read_text(encoding="utf-8"))
units = [s for s in d["skills"] if s["in_catalog"]]
L = []

kinds = collections.Counter()
for s in units:
    if "REST" not in s["routes"]:
        continue
    ev = s["evidence"]["REST"]
    k = set()
    for e in ev:
        if "with businessObject" in e or "Download Fusion Data Loader Sample" in e:
            k.add("data_loader_bo")
        elif "ora_rest_execution.md" in e:
            k.add("rest_file")
        elif "core.data-loader.task-rest" in e or "core.data-loader.fscr-task-rest" in e:
            k.add("task_rest")
        elif "(frontmatter)" in e:
            k.add("rest_mode_only")
    if not k:
        k.add("depends_only")
    for x in k:
        kinds[x] += 1
    kinds["REST units"] += 1
L.append("REST evidence kinds (a unit may have several): " + json.dumps(dict(kinds)))

L.append("\nRoutes by kind of unit: " + json.dumps(d["routes_by_kind"]))
L.append("All units: " + json.dumps(d["routes_all_linked"]))
L.append("By pillar: " + json.dumps(d["routes_by_pillar"]))
L.append("\nCatalog comparison: " + json.dumps(d["catalog_compare_counts"]))
groups = collections.defaultdict(list)
for s in units:
    f, fsm = s["catalog_csv_flag"], "FSM_CSV" in s["routes"]
    other = [r for r in s["routes"] if r != "FSM_CSV"]
    if f == "N" and fsm:
        groups["flag N, skill declares FSM CSV"].append(s)
    elif f == "Y" and not fsm and (other or s["manual"]):
        groups["flag Y, skill declares another route or manual, not FSM CSV"].append(s)
    elif f in ("Y", "N") and not s["routes"] and not s["manual"]:
        groups[f"no route to compare (flag {f})"].append(s)
    elif f == "UNKNOWN":
        groups["flag UNKNOWN"].append(s)
for g, rows in groups.items():
    L.append(f"\n{g}: {len(rows)}")
    for s in rows[:10]:
        e = [x for r in s["routes"] for x in s["evidence"][r][:1]] or s["manual"][:1] or [s["meta_mode_evidence"] or "-"]
        L.append(f"  {s['task_code']} [{s['kind']}] routes={s['routes'] or ('manual' if s['manual'] else 'none')} "
                 f"| {e[0][:170]}")
L.append("\nSkill frontmatter CSV flag differs from the catalog: " + str(len(d["skill_flag_copy_differs_from_catalog"])))
for x in d["skill_flag_copy_differs_from_catalog"]:
    L.append(f"  {x[0]}: skill {x[1]} / catalog {x[2]}")
L.append("\nNo-route units (no operative route): what they give: " + json.dumps(d["no_route_what_they_give"]))
for s in units:
    if not s["routes"]:
        L.append(f"  {s['task_code']} [{s['kind']}] manual={bool(s['manual'])} unclear={s['unclear']} "
                 f"ora-resource={len(s['ora_resource_files'])} headings={s['headings'][:8]}")
L.append("\nUnclear: " + json.dumps(d["unclear"]))
L.append("Browser/UI automation declared positively: " + str(len(d["browser_positive"])) +
         f"; units that explicitly forbid it: {d['browser_negated_count']}")
for x in d["browser_negated_examples"]:
    L.append("  " + x[:200])
(HERE / "05_tables.out.txt").write_text("\n".join(L), encoding="utf-8")
print("\n".join(L))
