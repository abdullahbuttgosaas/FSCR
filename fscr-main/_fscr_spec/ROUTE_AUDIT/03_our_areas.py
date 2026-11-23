"""Route audit step 3 (read-only): our areas and the 16 create skills (SKILL.md and task guide files), quoted with file and line.

For each area: the catalog tasks whose name matches (with their CSV flag), whether a skill has that task_code, and
for each such skill the exact lines that state the route (frontmatter dataloader_import_mode, the CSV workflow
section's route lines, any "core.data-loader ... FSM" line, ora_rest_execution / ora_fbdi_processing files, e2e-adapter
importMode). Also: any skill folder that mentions the task code without being its skill. Writes 03_our_areas.out.txt.
"""
import json
import re
from pathlib import Path

import yaml

REPO = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main")
OUT = Path(__file__).with_name("03_our_areas.out.txt")
CAT = json.loads((REPO / "knowledge/setup-task-catalog/effective/setupTasksAll.json").read_text(encoding="utf-8"))["items"]
AREAS = {"Order Types (our folder: lookup ORA_DOO_ORDER_TYPES via Manage Order Lookups)": r"order lookups|order types?$",
         "Business Units": r"business unit",
         "Price Lists": r"price list",
         "Payment Terms (Payables)": r"^manage payment terms$",
         "Customers": r"^(manage |create |import )?customers?$|^manage customers|customer account$|import customer",
         "Receivables Payment Terms": r"^manage receivables payment terms$",
         "AutoInvoice Grouping Rules": r"^manage autoinvoice grouping rules$",
         "Transaction Sources": r"^manage transaction sources$",
         "Transaction Types": r"^manage transaction types$"}
ROUTE_LINE = re.compile(r"dataloader_import_mode|Import setup task data with|Route every import|core\.data-loader`? in|"
                        r"CSVExportImportSupportedFlag` is|importMode|businessObject:|non-operative|metadata only|"
                        r"manual-tasks|fsm-csv-import|task-level-import|rest-api-client|ess-job-submitter", re.I)

skills = {}
for p in REPO.rglob("*.md"):                    # SKILL.md / skill.md and the task guide .md files
    t = p.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", t, re.S)
    try:
        fm = yaml.safe_load(m.group(1)) if m else {}
    except yaml.YAMLError:
        fm = {}
    fm = fm if isinstance(fm, dict) else {}
    code = (fm or {}).get("task_code") or (fm or {}).get("setup_task_code")
    if code:
        skills.setdefault(code, []).append(p)


def rel(p):
    return str(Path(p).relative_to(REPO)).replace("\\", "/")


def quote(p):
    out = []
    for i, ln in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if ROUTE_LINE.search(ln):
            out.append(f"    {rel(p)}:{i}: {ln.strip()[:230]}")
    d = p.parent
    for f in ("ora_rest_execution.md", "ora_fbdi_processing.md"):
        if (d / "ora-resource" / f).exists():
            out.append(f"    {rel(d / 'ora-resource' / f)}: exists")
    a = d / "e2e-adapter.json"
    if a.exists():
        task = json.loads(a.read_text(encoding="utf-8")).get("task", {})
        out.append(f"    {rel(a)}: task = {json.dumps(task)}")
    return out


lines = []
mentions_cache = None
for area, rx in AREAS.items():
    lines.append(f"\n=== {area}")
    tasks = [c for c in CAT if re.search(rx, c["TaskName"], re.I)]
    if not tasks:
        lines.append("  no catalog task name matches")
    for c in tasks:
        sk = skills.get(c["TaskCode"], [])
        lines.append(f"  catalog: {c['TaskCode']} | {c['TaskName']} | CSV flag {c['CSVExportImportSupportedFlag']} | "
                     f"skills: {len(sk)}")
        for p in sk:
            lines += quote(p)
        if not sk:
            if mentions_cache is None:
                mentions_cache = {q: q.read_text(encoding="utf-8", errors="replace") for q in REPO.rglob("*.md")}
            hits = sorted(rel(q) for q, t in mentions_cache.items() if re.search(r"\b" + c["TaskCode"] + r"\b", t))
            lines.append(f"    no skill with this task_code; files mentioning the code: {len(hits)} "
                         f"{hits[:3]}")

lines.append("\n=== The skills with <!-- fscr-create-fields --> (the create skills)")
for code, ps in sorted(skills.items()):
    for p in ps:
        t = p.read_text(encoding="utf-8", errors="replace")
        if re.search(r"<!--\s*fscr-create-fields\s*:", t):
            ops = re.search(r"<!--\s*fscr-supported-operations\s*:\s*(.*?)\s*-->", t)
            lines.append(f"  {code} (operations: {ops.group(1) if ops else '?'})")
            lines += quote(p)[:8]

OUT.write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
