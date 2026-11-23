"""Route audit step 4 (read-only): from the files alone, is a declared route usable?

Sample (deterministic, from 02_route_audit.out.json): 10 SKILL.md units whose REST evidence is in the skill's own
text/files (not only a depends_on), and 10 SKILL.md units that declare FSM CSV and NOT REST, each picked round-robin
over the pillars in path order. For each, reads SKILL.md + ora-resource/ + references/ and reports, with the first
matching line quoted (file:line):
  REST: a real Fusion REST path (/fscmRestApi|hcmRestApi|crmRestApi/resources/<version>/<resource>, or the ESS scheduler
        path), a write method on such a path (POST / PATCH on the same line), an Oracle docs operation link, a "TBD" /
        "do not invent an endpoint" stop, required fields stated (ora_input_validation.md or "required" lines).
  CSV:  the task code, the template / export step that gives the file layout, entity or CSV file names, the metadata
        file ASM_SETUP_CSV_METADATA.xml, required fields stated, the import step (core.data-loader).
Writes 04_accuracy_sample.out.json and .txt.
"""
import collections
import json
import re
from pathlib import Path

REPO = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main")
HERE = Path(__file__).resolve().parent
units = [s for s in json.loads((HERE / "02_route_audit.out.json").read_text(encoding="utf-8"))["skills"]
         if s["kind"] == "skill" and s["in_catalog"]]

REST_PATH = re.compile(r"/(?:fscm|hcm|crm)RestApi/resources/(?:[0-9.]+|latest|\{[^}]+\})/[A-Za-z][A-Za-z0-9]+|"
                       r"/ess/rest/scheduler/v1/requests")
WRITE = re.compile(r"\b(POST|PATCH)\b")
DOCS_OP = re.compile(r"docs\.oracle\.com/\S*/op-[a-z0-9-]+-(post|patch)\.html")
STOP = re.compile(r"\bTBD\b|do not invent an endpoint|no (approved|verified) (endpoint|REST)", re.I)
REQ = re.compile(r"\b(required|mandatory|require explicit)\b", re.I)
CSVNAME = re.compile(r"\b[A-Z][A-Z0-9_]{3,}\.csv\b|\b[A-Z][A-Z0-9_]{3,}::[A-Za-z]")
TEMPLATE = re.compile(r"task-level-export|template", re.I)
META = re.compile(r"ASM_SETUP_CSV_METADATA")
IMPORT = re.compile(r"Import (reviewed )?(setup task|task setup) data with `core\.data-loader`|core\.data-loader`? in `?FSM|"
                    r"Route every import (exclusively )?through `core\.data-loader`")


def strong_rest(s):
    return "REST" in s["routes"] and any("depends_on/uses_core core.fusion-api" not in e for e in s["evidence"]["REST"])


def pick(rows, n=10):
    by = collections.defaultdict(list)
    for s in sorted(rows, key=lambda s: s["path"]):
        by[s["pillar"]].append(s)
    out = []
    while len(out) < n and any(by.values()):
        for pl in sorted(by):
            if by[pl] and len(out) < n:
                out.append(by[pl].pop(0))
    return out


def files_of(s):
    p = REPO / s["path"]
    d = p.parent
    fs = [p] + sorted(f for f in (d / "ora-resource").glob("*") if f.is_file()) if (d / "ora-resource").is_dir() else [p]
    if (d / "references").is_dir():
        fs += sorted(f for f in (d / "references").rglob("*") if f.is_file() and f.suffix in (".md", ".json"))
    return fs


def first(fs, rx, also=None, limit=3):
    hits = []
    for f in fs:
        for i, ln in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if rx.search(ln) and (also is None or also.search(ln)):
                hits.append(f"{f.relative_to(REPO).as_posix()}:{i}: {ln.strip()[:220]}")
                if len(hits) >= limit:
                    return hits
    return hits


def check_rest(s):
    fs = files_of(s)
    paths = sorted({m.group(0) for f in fs for m in REST_PATH.finditer(f.read_text(encoding="utf-8", errors="replace"))})
    return {"task": s["task_code"], "pillar": s["pillar"], "path": s["path"], "routes": s["routes"],
            "rest_paths_named": paths[:6], "write_on_a_rest_path": first(fs, REST_PATH, WRITE, 2),
            "oracle_docs_write_operation": first(fs, DOCS_OP, None, 2), "tbd_or_stop": first(fs, STOP, None, 2),
            "required_fields_file": "ora_input_validation.md" in s["ora_resource_files"],
            "required_fields_lines": first(fs, REQ, None, 1)}


def check_csv(s):
    fs = files_of(s)
    return {"task": s["task_code"], "pillar": s["pillar"], "path": s["path"], "routes": s["routes"],
            "task_code_stated": bool(first(fs, re.compile(re.escape(s["task_code"])), None, 1)),
            "template_or_export_step": first(fs, TEMPLATE, None, 1), "entity_or_csv_names": first(fs, CSVNAME, None, 2),
            "metadata_file_named": bool(first(fs, META, None, 1)), "import_step": first(fs, IMPORT, None, 1),
            "required_fields_file": "ora_input_validation.md" in s["ora_resource_files"],
            "create_fields_listed": s["create_fields_tag"], "required_fields_lines": first(fs, REQ, None, 1)}


rest = [check_rest(s) for s in pick([s for s in units if strong_rest(s)])]
csv = [check_csv(s) for s in pick([s for s in units if "FSM_CSV" in s["routes"] and "REST" not in s["routes"]])]
res = {"rest_sample": rest, "csv_sample": csv}
(HERE / "04_accuracy_sample.out.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
lines = ["REST sample (10)"]
for r in rest:
    lines.append(f"- {r['pillar']} {r['task']}: REST paths {len(r['rest_paths_named'])} {r['rest_paths_named'][:3]}; "
                 f"POST/PATCH on a path: {'yes' if r['write_on_a_rest_path'] else 'no'}; docs write op: "
                 f"{'yes' if r['oracle_docs_write_operation'] else 'no'}; TBD/stop: {'yes' if r['tbd_or_stop'] else 'no'}; "
                 f"required-fields file: {r['required_fields_file']}")
lines.append("CSV (FSM) sample (10)")
for r in csv:
    lines.append(f"- {r['pillar']} {r['task']}: task code {r['task_code_stated']}; template/export step "
                 f"{'yes' if r['template_or_export_step'] else 'no'}; entity/CSV names {'yes' if r['entity_or_csv_names'] else 'no'}; "
                 f"metadata file {r['metadata_file_named']}; import step {'yes' if r['import_step'] else 'no'}; "
                 f"required-fields file {r['required_fields_file']}; create fields listed {r['create_fields_listed']}")
(HERE / "04_accuracy_sample.out.txt").write_text("\n".join(lines), encoding="utf-8")
print("\n".join(lines))
