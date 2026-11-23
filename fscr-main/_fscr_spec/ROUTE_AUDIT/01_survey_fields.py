"""Route audit step 1 (read-only): survey every SKILL.md in the FSCR repo for the places a route can be stated.

Counts, over all SKILL.md files: frontmatter keys, values of route-like keys, <!-- fscr-* --> comment tags, sibling
files (e2e-adapter.json keys, scripts/ names, ora-resource/ names). Writes 01_survey_fields.out.json next to itself.

  python 01_survey_fields.py
"""
import collections
import json
import re
from pathlib import Path

import yaml

REPO = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\fscr-main")
OUT = Path(__file__).with_suffix(".out.json")

ROUTE_KEYS = ("dataloader_import_mode", "businessObject", "export_import_supported_flag",
              "csv_export_import_supported_flag", "side_effects", "execution_mode", "type", "layer", "pillar",
              "write_route", "route", "routes", "import_mode", "write_routes", "required_privileges")


def front(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        return {"__yaml_error__": str(e)[:200]}


skills = sorted(REPO.rglob("SKILL.md"))
keys, values, tags, siblings, adapter_keys, scripts, bad = (collections.Counter() for _ in range(7))
for p in skills:
    t = p.read_text(encoding="utf-8", errors="replace")
    fm = front(t)
    if fm is None or "__yaml_error__" in (fm or {}):
        bad[str(p.relative_to(REPO))] += 1
        fm = fm or {}
    for k in fm:
        keys[k] += 1
    for k in ROUTE_KEYS:
        if k in fm:
            v = fm[k]
            values[f"{k} = {json.dumps(v, sort_keys=True)[:120]}"] += 1
    for tag in re.findall(r"<!--\s*(fscr-[a-z0-9-]+)\s*:", t):
        tags[tag] += 1
    d = p.parent
    for c in d.iterdir():
        siblings[c.name if c.is_file() else c.name + "/"] += 1
    a = d / "e2e-adapter.json"
    if a.exists():
        try:
            for k in json.loads(a.read_text(encoding="utf-8")):
                adapter_keys[k] += 1
        except (ValueError, AttributeError) as e:
            adapter_keys[f"__unreadable__ {type(e).__name__}"] += 1
    if (d / "scripts").is_dir():
        for s in (d / "scripts").iterdir():
            scripts[s.name] += 1

res = {"skill_files": len(skills), "frontmatter_unreadable": dict(bad), "frontmatter_keys": keys.most_common(),
       "route_like_values": values.most_common(), "fscr_comment_tags": tags.most_common(),
       "files_next_to_SKILL_md": siblings.most_common(60), "e2e_adapter_top_keys": adapter_keys.most_common(),
       "scripts_names": scripts.most_common(40)}
OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
print(json.dumps({k: (v if not isinstance(v, list) else v[:25]) for k, v in res.items()}, indent=1)[:9000])
