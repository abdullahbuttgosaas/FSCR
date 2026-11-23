"""Offline analysis and grading of the 40 sampled skills (Run 05). Mechanical, repeatable feature detection.
Grading rules (fixed before grading):
  3 = has its own runnable script in the skill folder (a .py with argparse or a main entry point)
  2 = names a route AND lists fields AND has task rules AND shows an example
  1 = names a route AND lists fields
  0 = names a route only (or no route at all)
Feature detection:
  route   : "Data Loader import mode: `X`" (FSM/HDL/FBDI/REST/ESS/CXIMPORT); else REST endpoint paths; else "UI"/"manual"
            wording; else none. CSV routing flag from "CSV export/import supported: `Y/N`".
  fields  : fscr-create-fields marker, or >= 5 distinct ENTITY::Field pairs, or >= 5 distinct backticked CamelCase column names
  rules   : ora-resource/*.md with rule tables (ora_input_validation / ora_design_enforcement / ora_rule_registry.json)
  example : a fenced json/csv/xml/bash block in the skill folder, or an e2e/test/example file
  deps    : ora_dependency_readiness.md, or "prerequisite"/"depends on"/"dependency" wording
  verify  : "reconcile", "read-back"/"read back", "verify", "fresh export" wording
Writes evidence/analysis40.json; prints one line per skill."""
import json, re
from pathlib import Path

R5 = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_05_breadth")
W = R5 / "fscr-work5"
sample = json.loads((R5 / "evidence/sample40.json").read_text(encoding="utf-8"))
out = []
for i, s in enumerate(sample, 1):
    f = W / s["path"]
    d = f.parent
    txt = f.read_text(encoding="utf-8", errors="replace")
    files = [p for p in d.rglob("*") if p.is_file()] if f.name == "SKILL.md" else [f]
    # only this skill's own folder level for flat area skills: avoid counting child skills
    if f.name == "SKILL.md":
        files = [p for p in files if p.parent == d or p.parent.name in ("scripts", "ora-resource", "references", "assets")
                 or (p.parent.parent == d and p.parent.name in ("scripts", "ora-resource", "references", "assets"))]
    alltxt = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in files if p.suffix in (".md", ".json", ".py"))
    g = lambda pat, t=txt: (re.search(pat, t) or [None, None])[1]
    dl = g(r"Data Loader import mode: `([^`]*)`")
    csvflag = g(r"CSV export/import supported: `([^`]*)`")
    rest = sorted(set(re.findall(r"/(?:fscmRestApi|crmRestApi|hcmRestApi)/resources/[^\s`'\")|,]+", alltxt)))
    route = dl if dl else ("REST" if rest else ("UI/manual" if re.search(r"\b(UI|manual(ly)?|navigat)", txt, re.I) else "none"))
    scripts = sorted(p.name for p in files if p.suffix == ".py")
    runnable = [p.name for p in files if p.suffix == ".py" and re.search(r"argparse|def main\(|__main__", p.read_text(encoding="utf-8", errors="replace"))]
    marker = re.search(r"fscr-create-fields:\s*([^>]+)-->", alltxt)
    fld = set(re.findall(r"\b([A-Z][A-Z0-9_]{2,})::([A-Za-z0-9_.]+)", alltxt))
    camel = set(re.findall(r"`([A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+)`", alltxt))
    fields = bool(marker) or len(fld) >= 5 or len(camel) >= 5
    rules = any(p.parent.name == "ora-resource" and p.name in ("ora_input_validation.md", "ora_design_enforcement.md", "ora_rule_registry.json") for p in files)
    example = bool(re.search(r"```(json|csv|xml|bash|sh)\s*\n[^`]{20,}```", alltxt)) or any(re.search(r"e2e|example|test", p.name, re.I) for p in files)
    deps = any(p.name == "ora_dependency_readiness.md" for p in files) or bool(re.search(r"prerequisite|depends on|dependenc", alltxt, re.I))
    verify = bool(re.search(r"reconcil|read[- ]back|\bverif|fresh export", alltxt, re.I))
    grade = 3 if runnable else (2 if route != "none" and fields and rules and example else (1 if route != "none" and fields else 0))
    out.append({"n": i, **s, "task_code": g(r"Task code: `([^`]+)`") or g(r"task_code: `([^`]+)`"),
                "offering": g(r"offering: `([^`]+)`") or g(r"- offering:\s*`?([^`\n]+)"), "functional_area": g(r"functional_area: `([^`]+)`"),
                "execution_mode": g(r'execution_mode:\s*"([^"]+)"'), "route": route, "csv_supported": csvflag, "rest_paths": len(rest),
                "scripts": scripts, "runnable_scripts": runnable, "fields": fields, "field_pairs": sorted(f"{a}::{b}" for a, b in fld)[:400], "camel_fields": sorted(camel)[:400],
                "rules": rules, "example": example, "deps": deps, "verify": verify, "grade": grade, "files": len(files)})
(R5 / "evidence/analysis40.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for o in out:
    print(f"{o['n']:2} {o['area']:6} {o['type'][:5]:5} g={o['grade']} route={o['route']:<9} csv={o['csv_supported']} task={o['task_code']} "
          f"mode={o['execution_mode']} scripts={len(o['scripts'])} f={int(o['fields'])} r={int(o['rules'])} ex={int(o['example'])} dep={int(o['deps'])} ver={int(o['verify'])} :: {o['path'].split('/')[-2]}")
