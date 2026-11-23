"""Offline survey of the 16 FSCR skills that ship an e2e-adapter.json (Run 04).
For each: task code, release the adapter was built for, readiness label, scripts, test files, supported operations,
Data Loader mode, rule-registry presence, and the entities/CSVs the adapter declares.
Writes evidence/survey16.json and prints one line per skill. Read-only."""
import json, re
from pathlib import Path

W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_04_create16\fscr-work4")
OUT = W.parent / "evidence" / "survey16.json"
rows = []
for a in sorted(W.glob("pillars/**/e2e-adapter.json")):
    d = a.parent
    skill = (d / "SKILL.md").read_text(encoding="utf-8", errors="replace") if (d / "SKILL.md").exists() else ""
    ad = json.loads(a.read_text(encoding="utf-8"))
    flat = json.dumps(ad)
    g = lambda pat, t=skill: (re.search(pat, t) or [None, None])[1]
    rel = None
    for k in ("release", "targetRelease", "builtOnRelease", "fusionRelease", "built_on_release", "sourceRelease"):
        m = re.search(r'"%s"\s*:\s*"([^"]+)"' % k, flat)
        if m:
            rel = m.group(1); break
    ready = re.findall(r'"(readiness|e2eReadiness|status|readinessStatus)"\s*:\s*"([^"]+)"', flat)[:3]
    scripts = sorted(p.name for p in d.rglob("*.py") if "test" not in p.name.lower())
    tests = sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file() and re.search(r"test", p.name, re.I))
    rows.append({
        "skill": str(d.relative_to(W)).replace("\\", "/"),
        "task_code": g(r"Task code: `([^`]+)`") or (re.search(r'"taskCode"\s*:\s*"([^"]+)"', flat) or [None, None])[1],
        "built_release": rel,
        "adapter_labels": ready,
        "execution_mode": g(r'execution_mode:\s*"([^"]+)"'),
        "supported_ops": g(r"fscr-supported-operations:\s*([^>]+?)\s*-->"),
        "dl_mode": g(r"Data Loader import mode: `([^`]+)`"),
        "registry": (d / "ora-resource" / "ora_rule_registry.json").exists(),
        "scripts": scripts,
        "tests": tests,
        "adapter_keys": list(ad.keys())[:12],
        "csv_entities": sorted(set(re.findall(r'"([A-Z][A-Z0-9_]+\.csv)"', flat)))[:12],
    })
OUT.write_text(json.dumps(rows, indent=1), encoding="utf-8")
for r in rows:
    print(f"{r['skill'].split('/')[-1]} | {r['task_code']} | rel={r['built_release']} | mode={r['execution_mode']} | ops={r['supported_ops']} | dl={r['dl_mode']} | reg={r['registry']} | scripts={r['scripts']} | tests={len(r['tests'])} | csv={len(r['csv_entities'])}")
