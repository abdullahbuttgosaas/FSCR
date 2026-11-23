"""Route audit (read-only): which route does FSCR declare for each setup task skill?

Reads only files in the FSCR repo; writes only next to this script (02_route_audit.out.json and .txt).
No network, no Oracle.

DEFINITIONS (every number in the report depends on these):
- catalog       = knowledge/setup-task-catalog/effective/setupTasksAll.json, "items" (TaskCode, CSVExportImportSupportedFlag).
- task skill    = a SKILL.md whose YAML frontmatter has `task_code` (or `setup_task_code`).
- link L1       = the skill's frontmatter task_code equals a catalog TaskCode (exact).
- link L2       = wider: a catalog TaskCode appears (as a whole word) in any file of a skill folder (SKILL.md,
                  ora-resource/, references/, e2e-adapter.json), for any SKILL.md in the repo.
- pillar        = frontmatter `pillar`, else the top folder (pillars/<x>, shared, core).
- route signals (each with the file and line that produced it):
    meta_mode      frontmatter `dataloader_import_mode` value, as written.
    meta_disclaim  the body calls that value non-operative / inactive / "catalog metadata only".
    FSM_CSV        the generated "CSV Export, Import, and Validation Workflow" section in its POSITIVE form (it routes the
                   import to a skill: "Import setup task data with" / "Route every import exclusively through", or its
                   first line says the flag "is `Y`" and is not "catalog metadata only"; NOTE this section is generated
                   from the catalog flag, so it agrees with the catalog by construction), or a line
                   naming `core.data-loader` in `FSM` mode, or e2e-adapter.json task.importMode FSM.
    REST           ora-resource/ora_rest_execution.md exists, or frontmatter depends_on names a REST core service
                   (core.fusion-api.rest-api-client, core.fusion-api.apps-common*, core.data-loader.task-rest,
                   core.data-loader.fscr-task-rest), or meta_mode REST with a non-empty businessObject(s), or the
                   "Download Fusion Data Loader Sample" section (Fusion Data Loader business object, a REST loader).
    FBDI           meta_mode FBDI, or ora-resource/ora_fbdi_processing.md.
    ESS            meta_mode ESS, or depends_on core.fusion-api.ess-job-submitter.
    HDL            meta_mode HDL (HCM Data Loader) -> reported under "other".
    CX_IMPORT      meta_mode CXIMPORT, or depends_on core.fusion-api.cx-import-export-management.
    MANUAL         the body invokes / depends on shared.common.manual-tasks (the user does it in the UI).
    BROWSER        a line naming browser / UI automation (Playwright, Selenium, browser automation, UI automation,
                   direct UI control, screen automation) that is NOT negated. A line is negated when it, the sentence it
                   continues (up to 4 lines back), or the list header above it (nearest preceding line ending with ':')
                   contains do not / must not / never / not / no / without / blocked / refused, or it is a table row
                   marked UNSUPPORTED or Error.
  meta_mode is counted as a declared route only when it is not disclaimed and the body does not route the task to
  manual-tasks.
- operative routes = the union of FSM_CSV, REST, FBDI, ESS, HDL, CX_IMPORT, BROWSER, plus meta_mode when it counts.
- unclear       = a task skill whose meta_mode is disclaimed and that has no operative route and no MANUAL route,
                  or whose only evidence is a meta_mode value that is not one of FSM/REST/HDL/FBDI/ESS/CXIMPORT.
"""
import collections
import json
import re
from pathlib import Path

import yaml

REPO = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main")
HERE = Path(__file__).resolve().parent
CATALOG = REPO / "knowledge" / "setup-task-catalog" / "effective" / "setupTasksAll.json"
REST_DEPS = ("core.fusion-api.rest-api-client", "core.fusion-api.apps-common", "core.data-loader.task-rest",
             "core.data-loader.fscr-task-rest")
NEG = re.compile(r"\b(do not|don't|must not|never|not|no|without|forbid\w*|prohibit\w*|block\w*|refuse\w*)\b", re.I)
BROWSER = re.compile(r"playwright|selenium|browser[- ]automation|browser\b.{0,40}\b(control|automat|drive)|"
                     r"ui[- ]automation|direct ui control|screen automation|automate the (ui|screen)|"
                     r"drive the (ui|browser|screen)|headless browser", re.I)
KNOWN_MODES = {"FSM", "REST", "HDL", "FBDI", "ESS", "CXIMPORT"}


def rel(p):
    return str(Path(p).relative_to(REPO)).replace("\\", "/")


def front(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def section(text, head):
    m = re.search(r"^" + re.escape(head) + r"\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m


def line_no(text, pos):
    return text.count("\n", 0, pos) + 1


def negated(lines, i):
    if NEG.search(lines[i]) or (lines[i].lstrip().startswith("|") and re.search(r"UNSUPPORTED|\bError\b", lines[i])):
        return True
    # the sentence the line belongs to: back to the previous sentence end or blank line (at most 4 lines)
    sent = []
    for j in range(i - 1, max(-1, i - 5), -1):
        s = lines[j].strip()
        if not s:
            break
        tail = re.split(r"[.;]\s", s)[-1]
        sent.insert(0, tail)
        if tail != s:
            break
    if sent and NEG.search(" ".join(sent)):
        return True
    for j in range(i - 1, max(-1, i - 15), -1):
        s = lines[j].strip()
        if not s:
            continue
        if s.endswith(":"):
            return bool(NEG.search(s))
        if not s.startswith(("-", "*")) and not re.match(r"\d+\.", s):
            return False
    return False


def pillar_of(fm, path):
    names = {"erp": "ERP", "hcm": "HCM", "scm": "SCM", "cx": "CX", "common": "Common", "core": "Core", "shared": "Shared"}
    if fm.get("pillar"):
        v = str(fm["pillar"]).strip()
        return names.get(v.lower(), v)
    parts = Path(rel(path)).parts
    v = parts[1] if parts[0] == "pillars" else parts[0]
    return names.get(v.lower(), v)


catalog = json.loads(CATALOG.read_text(encoding="utf-8"))["items"]
CAT = {i["TaskCode"]: i for i in catalog}
CODES = set(CAT)
code_re = re.compile(r"\b(" + "|".join(sorted(map(re.escape, CODES), key=len, reverse=True)) + r")\b")

skills, l2_tasks, l2_skill_dirs = [], set(), set()
for p in sorted(REPO.rglob("*.md")):
    is_skill = p.name.lower() == "skill.md"          # two are named skill.md
    d = p.parent
    text = p.read_text(encoding="utf-8", errors="replace")
    if not is_skill and not text.startswith("---"):
        continue
    try:
        fm = front(text)
    except yaml.YAMLError:
        fm = {}
    if not isinstance(fm, dict):
        fm = {}
    if is_skill:
        # L2: every file in this skill folder (not sub-skills' folders)
        blob = [text]
        for sub in ("ora-resource", "references"):
            if (d / sub).is_dir():
                blob += [f.read_text(encoding="utf-8", errors="replace") for f in (d / sub).rglob("*") if f.is_file()
                         and f.suffix in (".md", ".json", ".yaml", ".yml", ".txt")]
        if (d / "e2e-adapter.json").exists():
            blob.append((d / "e2e-adapter.json").read_text(encoding="utf-8", errors="replace"))
        found = set(code_re.findall("\n".join(blob)))
        if found:
            l2_tasks |= found
            l2_skill_dirs.add(rel(d))
    code = fm.get("task_code") or fm.get("setup_task_code")
    if not code:
        continue
    lines = text.splitlines()
    ev = collections.defaultdict(list)          # route -> [evidence]
    neg = collections.defaultdict(list)
    mode = fm.get("dataloader_import_mode")
    bo = fm.get("businessObject") or fm.get("businessObjects")
    deps = [str(x) for x in (fm.get("depends_on") or []) + (fm.get("uses_core") or [])]
    m_mode = re.search(r"^dataloader_import_mode:.*$", text, re.M)
    mode_ev = f"{rel(p)}:{line_no(text, m_mode.start())}: {m_mode.group(0).strip()}" if m_mode else None
    disclaim = None
    for i, ln in enumerate(lines):
        if re.search(r"non-operative|inactive generator compatibility metadata|is catalog metadata only|"
                     r"compatibility metadata", ln, re.I):
            disclaim = f"{rel(p)}:{i + 1}: {ln.strip()[:200]}"
            break
    # FSM CSV
    sec = section(text, "## CSV Export, Import, and Validation Workflow")
    if sec:
        body = sec.group(1)
        at = line_no(text, sec.start())
        first = (body.strip().splitlines() or [""])[0]
        if re.search(r"Import setup task data with|Route every import exclusively through", body) or (
                re.search(r"is `Y`", first) and not re.search(r"metadata only", first, re.I)):
            k = next((i for i, x in enumerate(lines) if re.search(r"Import setup task data with|Route every import "
                                                                  r"exclusively through", x)), at)
            ev["FSM_CSV"].append(f"{rel(p)}:{k + 1}: {lines[k].strip()[:200] if k != at else first[:200]}")
        else:
            neg["FSM_CSV"].append(f"{rel(p)}:{at}: CSV section says: {(body.strip().splitlines() or ['(empty section)'])[0][:200]}")
    for i, ln in enumerate(lines):
        if re.search(r"core\.data-loader`?\s+in\s+`?FSM`?\s+mode", ln):
            (neg if negated(lines, i) else ev)["FSM_CSV"].append(f"{rel(p)}:{i + 1}: {ln.strip()[:200]}")
    if is_skill and (d / "e2e-adapter.json").exists():
        try:
            a = json.loads((d / "e2e-adapter.json").read_text(encoding="utf-8"))
            if (a.get("task") or {}).get("importMode") == "FSM":
                ev["FSM_CSV"].append(f"{rel(d / 'e2e-adapter.json')}: task.importMode = FSM")
        except ValueError:
            pass
    # REST
    if is_skill and (d / "ora-resource" / "ora_rest_execution.md").exists():
        ev["REST"].append(f"{rel(d / 'ora-resource' / 'ora_rest_execution.md')}: exists")
    for x in deps:
        if x.startswith(REST_DEPS):
            ev["REST"].append(f"{rel(p)}: frontmatter depends_on/uses_core {x}")
    if mode == "REST" and bo:
        ev["REST"].append(f"{mode_ev} with businessObject {json.dumps(bo)[:80]}")
    ds = section(text, "## Download Fusion Data Loader Sample")
    if ds:
        ev["REST"].append(f"{rel(p)}:{line_no(text, ds.start())}: section 'Download Fusion Data Loader Sample' "
                          "(Fusion Data Loader business object)")
    # FBDI / ESS / CX / HDL
    if is_skill and (d / "ora-resource" / "ora_fbdi_processing.md").exists():
        ev["FBDI"].append(f"{rel(d / 'ora-resource' / 'ora_fbdi_processing.md')}: exists")
    for x in deps:
        if x.startswith("core.fusion-api.ess-job-submitter"):
            ev["ESS"].append(f"{rel(p)}: frontmatter depends_on {x}")
        if x.startswith("core.fusion-api.cx-import-export-management"):
            ev["CX_IMPORT"].append(f"{rel(p)}: frontmatter depends_on {x}")
    # MANUAL
    manual = [x for x in deps if x == "shared.common.manual-tasks"]
    for i, ln in enumerate(lines):
        if "shared.common.manual-tasks" in ln and not negated(lines, i):
            manual.append(f"{rel(p)}:{i + 1}: {ln.strip()[:200]}")
    # BROWSER (SKILL.md and ora-resource files)
    files = [p] + ([f for f in sorted((d / "ora-resource").glob("*.md"))] if is_skill and (d / "ora-resource").is_dir() else [])
    for f in files:
        fl = f.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, ln in enumerate(fl):
            if BROWSER.search(ln):
                (neg if negated(fl, i) else ev)["BROWSER"].append(f"{rel(f)}:{i + 1}: {ln.strip()[:200]}")
    # meta mode counts?
    meta_counts = bool(mode) and not disclaim and not manual
    if meta_counts:
        key = {"FSM": "FSM_CSV", "CXIMPORT": "CX_IMPORT"}.get(mode, mode)
        ev[key].append(f"{mode_ev} (frontmatter)")
    routes = sorted(k for k, v in ev.items() if v)
    unclear = None
    if not routes and not manual and disclaim:
        unclear = "frontmatter mode disclaimed in the body, no other route found"
    if mode and mode not in KNOWN_MODES:
        unclear = f"unknown dataloader_import_mode {mode!r}"
    cat = CAT.get(code)
    skills.append({
        "path": rel(p), "kind": "skill" if is_skill else "task guide", "task_code": code, "task_name": fm.get("task_name") or fm.get("setup_task_name"),
        "pillar": pillar_of(fm, p), "in_catalog": cat is not None,
        "catalog_csv_flag": (cat or {}).get("CSVExportImportSupportedFlag"),
        "skill_csv_flag": fm.get("csv_export_import_supported_flag"),
        "meta_mode": mode, "meta_mode_evidence": mode_ev, "business_object": bo, "meta_disclaimed": disclaim,
        "manual": manual[:3], "routes": routes, "evidence": {k: v[:4] for k, v in ev.items() if v},
        "negated_mentions": {k: v[:3] for k, v in neg.items() if v}, "unclear": unclear,
        "create_fields_tag": bool(re.search(r"<!--\s*fscr-create-fields\s*:", text)),
        "supported_operations": (re.search(r"<!--\s*fscr-supported-operations\s*:\s*(.*?)\s*-->", text) or [None, None])[1],
        "ora_resource_files": sorted(f.name for f in (d / "ora-resource").glob("*")) if is_skill and (d / "ora-resource").is_dir() else [],
        "references_files": len(list((d / "references").rglob("*"))) if is_skill and (d / "references").is_dir() else 0,
        "headings": re.findall(r"^## (.+)$", text, re.M),
    })

# ---------------------------------------------------------------- counts
linked = [s for s in skills if s["in_catalog"]]
l1_tasks = {s["task_code"] for s in linked}
out = {"definitions": __doc__, "catalog_tasks": len(CAT),
       "catalog_csv_flag": collections.Counter(i["CSVExportImportSupportedFlag"] for i in catalog),
       "skill_md_files": sum(1 for q in REPO.rglob("*.md") if q.name.lower() == "skill.md"), "task_skills": len(skills),
       "task_skills_linked_L1": len(linked), "tasks_linked_L1": len(l1_tasks),
       "task_skills_not_in_catalog": [(s["path"], s["task_code"]) for s in skills if not s["in_catalog"]],
       "tasks_with_more_than_one_skill_L1": {c: n for c, n in collections.Counter(s["task_code"] for s in linked).items() if n > 1},
       "tasks_linked_L2": len(l2_tasks), "skill_folders_mentioning_a_task_L2": len(l2_skill_dirs),
       "tasks_L2_not_L1": len(l2_tasks - l1_tasks)}

ROUTES = ["REST", "FSM_CSV", "FBDI", "ESS", "HDL", "CX_IMPORT", "BROWSER"]


def route_counts(rows):
    c = collections.Counter()
    for s in rows:
        for r in s["routes"]:
            c[r] += 1
        if s["manual"] and not s["routes"]:
            c["MANUAL_ONLY (user does it in the UI)"] += 1
        if s["manual"]:
            c["MANUAL (any)"] += 1
        if s["unclear"]:
            c["UNCLEAR"] += 1
        elif not s["routes"] and not s["manual"]:
            c["NONE_DECLARED"] += 1
        if len(s["routes"]) > 1:
            c["more than one route"] += 1
    return dict(c)


out["routes_all_linked"] = route_counts(linked)
_sk = {s["task_code"] for s in linked if s["kind"] == "skill"}
_gd = {s["task_code"] for s in linked if s["kind"] == "task guide"}
out["link_by_kind"] = {"SKILL.md units": sum(1 for s in linked if s["kind"] == "skill"),
                       "task guide .md units": sum(1 for s in linked if s["kind"] == "task guide"),
                       "tasks with a SKILL.md": len(_sk), "tasks with a SKILL.md or a task guide": len(_sk | _gd),
                       "tasks with only a task guide": len(_gd - _sk), "tasks with both": len(_sk & _gd)}
out["routes_by_kind"] = {k: route_counts([s for s in linked if s["kind"] == k]) for k in ("skill", "task guide")}
_rest = [s for s in linked if "REST" in s["routes"]]
out["REST_evidence_strength"] = {
    "REST skills": len(_rest),
    "REST stated in the skill's own text or files (ora_rest_execution.md, task-rest, REST mode with a business object, "
    "Data Loader sample section, or REST mode not disclaimed)":
        sum(1 for s in _rest if any("depends_on/uses_core core.fusion-api" not in e for e in s["evidence"]["REST"])),
    "REST only because depends_on names a REST core service (may be used for reads only)":
        sum(1 for s in _rest if all("depends_on/uses_core core.fusion-api" in e for e in s["evidence"]["REST"]))}
out["meta_mode_all_linked"] = collections.Counter(str(s["meta_mode"]) for s in linked)
out["meta_mode_disclaimed"] = sum(1 for s in linked if s["meta_disclaimed"])
pillars = sorted({s["pillar"] for s in linked})
out["routes_by_pillar"] = {pl: dict(skills=sum(1 for s in linked if s["pillar"] == pl),
                                    **route_counts([s for s in linked if s["pillar"] == pl])) for pl in pillars}
out["browser_positive"] = [(s["path"], s["evidence"]["BROWSER"]) for s in linked if "BROWSER" in s["evidence"]]
out["browser_negated_count"] = sum(1 for s in linked if "BROWSER" in s["negated_mentions"])
out["browser_negated_examples"] = [s["negated_mentions"]["BROWSER"][0] for s in linked if "BROWSER" in s["negated_mentions"]][:10]
out["unclear"] = [(s["path"], s["unclear"], s["meta_disclaimed"]) for s in linked if s["unclear"]]

# ---------------------------------------------------------------- catalog flag comparison
cmp = collections.defaultdict(list)
for s in linked:
    f, fsm, other = s["catalog_csv_flag"], "FSM_CSV" in s["routes"], [r for r in s["routes"] if r != "FSM_CSV"]
    if f == "Y" and fsm:
        k = "agree: flag Y, skill declares FSM CSV"
    elif f == "N" and not fsm and (other or s["manual"]):
        k = "agree: flag N, skill declares another route or manual (no FSM CSV)"
    elif f == "N" and fsm:
        k = "CONTRADICTS: flag N but skill declares FSM CSV"
    elif f == "Y" and not fsm and (other or s["manual"]):
        k = "CONTRADICTS (reverse): flag Y but skill declares only another route or manual, not FSM CSV"
    elif f in ("Y", "N"):
        k = f"no route to compare (flag {f})"
    else:
        k = f"flag {f} in catalog"
    cmp[k].append(s)
out["catalog_compare_counts"] = {k: len(v) for k, v in sorted(cmp.items())}
out["catalog_compare_examples"] = {k: [{"path": s["path"], "task": s["task_code"], "flag": s["catalog_csv_flag"],
                                        "routes": s["routes"], "manual": bool(s["manual"]),
                                        "evidence": [e for r in s["routes"] for e in s["evidence"][r][:1]]}
                                       for s in v[:10]] for k, v in cmp.items() if "CONTRADICTS" in k or "flag UNKNOWN" in k}
out["skill_flag_copy_differs_from_catalog"] = [(s["path"], s["skill_csv_flag"], s["catalog_csv_flag"])
                                                for s in linked if s["skill_csv_flag"] != s["catalog_csv_flag"]]

# ---------------------------------------------------------------- our areas and the create skills
AREAS = {"Order Types": r"order type|order lookup", "Business Units": r"business unit",
         "Price Lists": r"price list", "Payment Terms (Payables)": r"^manage payment terms$",
         "Customers": r"^(manage|create) customers?$|customer account",
         "Receivables Payment Terms": r"receivables payment terms", "AutoInvoice Grouping Rules": r"grouping rule",
         "Transaction Sources": r"transaction sources", "Transaction Types": r"^manage transaction types$"}
area = {}
for a, rx in AREAS.items():
    area[a] = [{"path": s["path"], "task": s["task_code"], "name": s["task_name"], "catalog_csv_flag": s["catalog_csv_flag"],
                "routes": s["routes"], "manual": s["manual"], "meta_mode_evidence": s["meta_mode_evidence"],
                "disclaimed": s["meta_disclaimed"], "evidence": s["evidence"]}
               for s in linked if re.search(rx, str(s["task_name"] or ""), re.I)]
out["our_areas"] = area
out["create_skills"] = [{"path": s["path"], "task": s["task_code"], "ops": s["supported_operations"], "routes": s["routes"],
                         "evidence": s["evidence"]} for s in linked if s["create_fields_tag"]]

# ---------------------------------------------------------------- no route: what they give
none = [s for s in linked if not s["routes"]]
give = collections.Counter()
for s in none:
    give["skills with no operative route"] += 1
    give["  of which route to manual-tasks"] += bool(s["manual"])
    give["  with ora-resource/ files"] += bool(s["ora_resource_files"])
    give["  with ora_input_validation.md (fields / rules)"] += "ora_input_validation.md" in s["ora_resource_files"]
    give["  with ora_dependency_readiness.md (requirements)"] += "ora_dependency_readiness.md" in s["ora_resource_files"]
    give["  with ora_reference_lookups.md (references)"] += "ora_reference_lookups.md" in s["ora_resource_files"]
    give["  with references/ folder"] += bool(s["references_files"])
    give["  with fscr-create-fields tag"] += s["create_fields_tag"]
    give["  only the generated sections (no ora-resource, no references)"] += not s["ora_resource_files"] and not s["references_files"]
out["no_route_what_they_give"] = dict(give)
out["no_route_examples"] = [(s["path"], s["meta_mode"], s["catalog_csv_flag"], s["headings"][:12]) for s in none[:10]]

# ---------------------------------------------------------------- accuracy sample (deterministic: round-robin by pillar)
def sample(route, n=10):
    by = collections.defaultdict(list)
    for s in sorted(linked, key=lambda s: s["path"]):
        if route in s["routes"]:
            by[s["pillar"]].append(s)
    pick = []
    while len(pick) < n and any(by.values()):
        for pl in sorted(by):
            if by[pl] and len(pick) < n:
                pick.append(by[pl].pop(0))
    return pick


ENDPOINT = re.compile(r"/(fscm|hcm|crm)RestApi/|/resources/\d+\.\d+|/api/boss/|/ess/rest/|\bop-[a-z0-9-]+\.html|"
                      r"\b(GET|POST|PATCH|PUT|DELETE)\s+/?[a-zA-Z]+", re.I)


def check_usable(s):
    d = REPO / Path(s["path"]).parent
    txt = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in [REPO / s["path"]] +
                    sorted((d / "ora-resource").glob("*")) if f.is_file())
    refs = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in sorted((d / "references").rglob("*"))
                     if f.is_file() and f.suffix in (".md", ".json")) if (d / "references").is_dir() else ""
    return {"path": s["path"], "pillar": s["pillar"], "task": s["task_code"], "routes": s["routes"],
            "endpoint_or_rest_path_named": bool(ENDPOINT.search(txt + refs)),
            "endpoint_examples": sorted({m.group(0) for m in ENDPOINT.finditer(txt + refs)})[:5],
            "csv_entity_or_file_named": bool(re.search(r"\b[A-Z][A-Z0-9_]{3,}\.csv\b|\b[A-Z]{2,}_[A-Z0-9_]{3,}::", txt + refs)),
            "csv_file_examples": sorted(set(re.findall(r"\b[A-Z][A-Z0-9_]{3,}\.csv\b", txt + refs)))[:5],
            "create_fields_listed": s["create_fields_tag"],
            "required_fields_stated": bool(re.search(r"required|mandatory|explicit create values", txt, re.I)),
            "input_validation_file": "ora_input_validation.md" in s["ora_resource_files"],
            "business_object_named": bool(s["business_object"]),
            "route_given_only_as_a_skill_name": not ENDPOINT.search(txt + refs)}


out["accuracy_sample_REST"] = [check_usable(s) for s in sample("REST")]
out["accuracy_sample_FSM_CSV"] = [check_usable(s) for s in sample("FSM_CSV")]
out["skills"] = skills

(HERE / "02_route_audit.out.json").write_text(json.dumps(out, indent=1, default=list), encoding="utf-8")
summary = {k: v for k, v in out.items() if k not in ("skills", "definitions", "our_areas", "create_skills",
                                                     "accuracy_sample_REST", "accuracy_sample_FSM_CSV",
                                                     "catalog_compare_examples", "no_route_examples", "unclear",
                                                     "browser_negated_examples", "task_skills_not_in_catalog",
                                                     "skill_flag_copy_differs_from_catalog")}
summary["unclear_count"] = len(out["unclear"])
summary["task_skills_not_in_catalog_count"] = len(out["task_skills_not_in_catalog"])
summary["skill_flag_copy_differs_from_catalog_count"] = len(out["skill_flag_copy_differs_from_catalog"])
txt = json.dumps(summary, indent=1, default=list)
(HERE / "02_route_audit.out.txt").write_text(txt, encoding="utf-8")
print(txt)
