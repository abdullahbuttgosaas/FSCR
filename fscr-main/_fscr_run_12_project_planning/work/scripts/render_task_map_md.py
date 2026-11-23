"""Render outputs/01_offering_task_map.md from work/fa_summary.json + work/identified-task-mapping.json."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path
RUN = Path(sys.argv[1]).resolve()
fas = json.load(open(RUN / "work/fa_summary.json", encoding="utf-8"))
rows = json.load(open(RUN / "work/identified-task-mapping.json", encoding="utf-8"))["tasks"]
sel = json.load(open(RUN / "work/scripts/selection.json", encoding="utf-8"))
init = (RUN / "work/initializer_dryrun.txt").read_text(encoding="utf-8") if (RUN / "work/initializer_dryrun.txt").exists() else "not run"
cv = {}
if (RUN / "work/initializer_validation.json").exists():
    cv = json.load(open(RUN / "work/initializer_validation.json", encoding="utf-8"))

L = []
L.append("# Output 1: Offering Task Map (Twelve, SOW 50513scm)\n")
L.append("**Who produced it: FSCR + Claude.** Claude chose the offerings and functional areas from the SOW (`work/scripts/selection.json`, each with its SOW clause). "
         "FSCR's effective catalog `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json` supplied every task, its code and its display sequence. "
         "FSCR's offering-task-map-builder code (`shared/implementation-planning/offering-task-map-builder/scripts/task_to_skill_mapping.py`, which calls `core/runbook/scripts/task_context.py`) resolved each task to an FSCR skill path. "
         "Full row-level list: `outputs/01_offering_task_map.csv`; initializer input: `work/identified-task-mapping.json`.\n")
L.append("Legend: V = read from an FSCR file or the SOW in this run. NV = Claude's judgment, needs confirmation.\n")
L.append("## 1. Offerings to enable\n")
L.append("| Offering code | Offering | Status | SOW basis | FAs selected | Tasks | Status of mapping |")
L.append("|---|---|---|---|---|---|---|")
per_off = defaultdict(lambda: [0, 0])
for f in fas:
    per_off[f["offering"]][0] += 1; per_off[f["offering"]][1] += f["tasks"]
names = {f["offering"]: f["offering_name"] for f in fas}
for o in sel["offerings"]:
    c = o["code"]; n, t = per_off.get(c, [0, 0])
    L.append(f"| `{c}` | {names.get(c, '(no FA mapped)')} | {o['status']} | {o['sow']} | {n} | {t} | NV (Claude selection; codes V from catalog) |")
L.append("")
L.append("`new` = to be opted in for this project. `incremental` = already in Twelve's production (SOW Fin intro); only changes, which the SOW leaves to be decided (intake S5). `ORA_GMS_GRANTS_MANAGEMENT` has no task mapping because its changes are not defined.\n")
L.append("## 2. Functional areas and task counts\n")
L.append("| Offering | Functional area (code) | Tasks | SOW basis |")
L.append("|---|---|---|---|")
for f in fas:
    L.append(f"| {f['offering']} | {f['fa_name']} (`{f['fa']}`) | {f['tasks']} | {f['sow_basis']} |")
L.append("")
L.append("Excluded functional areas and the reason for each are listed in `work/scripts/selection.json` (`excluded`).\n")
uniq = len({r["Task Code"] for r in rows})
skill = Counter("pillar skill" if (r.get("Skill Path") and "manual-tasks" not in r["Skill Path"]) else "manual (no FSCR skill)" for r in rows)
seqsrc = Counter(r["Sequence Source"] for r in rows)
layer = Counter(r["Source Layer"] for r in rows)
amb = Counter("exact 1" if r["Name Matches In setupTasksAll"] == 1 else ("0 matches" if r["Name Matches In setupTasksAll"] == 0 else ">1 matches") for r in rows)
L.append("## 3. Totals\n")
L.append("| Measure | Value | Status |")
L.append("|---|---|---|")
L.append(f"| Task rows (task occurrences per offering/FA) | {len(rows)} | V (counted) |")
L.append(f"| Unique task codes | {uniq} | V (counted) |")
L.append(f"| Rows with an FSCR pillar skill | {skill['pillar skill']} | V (FSCR code) |")
L.append(f"| Rows routed to manual (no FSCR task skill) | {skill['manual (no FSCR skill)']} | V (FSCR code) |")
L.append(f"| Sequence source: catalog display sequence | {seqsrc.get('release', 0)} | V |")
L.append(f"| Sequence source: functional-area tail (no catalog sequence) | {seqsrc.get('functional_area_tail', 0)} | V |")
L.append(f"| Source layer release / pre_release-custom | {layer.get('release', 0)} / {layer.get('pre_release/custom', 0)} | V |")
L.append(f"| Task names with exactly 1 / 0 / >1 matches in effective setupTasksAll.json | {amb['exact 1']} / {amb['0 matches']} / {amb['>1 matches']} | V |")
L.append("")
L.append("`Resolver Sequence` was assigned **by Claude** following the resolver's written method (catalog order within offering/FA, then functional-area tail). It is **not** output from FSCR's `task-dependency-resolver`, which has no script and needs FSM/BOSS (see Output 3, section 2).\n")
L.append("## 4. SOW items with no clear catalog task (NV)\n")
L.append("| SOW item | Note |")
L.append("|---|---|")
L.append("| 7.5 Meters, 7.6 Maintenance Programs, 7.7 Installed Base | No task named meter, maintenance program or installed base was found in the selected offerings' FAs by a name search. These are probably transactional/master data, not setup tasks. NV |")
L.append("| Reporting approach (Fin 6) | Advisory deliverable; no setup task |")
L.append("| RICE 1 printable PO | BI Publisher build; no setup task |")
L.append("| Training (Change Mgmt) | Not a setup task |")
L.append("")
L.append("## 5. Project workspace initializer dry run\n")
L.append("```text\n" + init.strip() + "\n```\n")
if cv:
    L.append(f"Initializer catalog validation (exact-name, `{cv.get('catalog')}`): matched {cv.get('matched')}, unmatched {cv.get('unmatched')}, ambiguous {cv.get('ambiguous')}, total {cv.get('total')}. V (run in this session)\n")
extra = RUN / "work/initializer_findings.md"
if extra.exists():
    L.append(extra.read_text(encoding="utf-8"))
(RUN / "outputs/01_offering_task_map.md").write_text("\n".join(L), encoding="utf-8")
print("written")
