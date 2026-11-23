"""Shared helpers for the module test kit scripts (Python 3.10+, standard library only).

Paths are found from this file's location, so the scripts work wherever the pack is unzipped:
    <pack>/module-test-kit/scripts/kitlib.py
    <pack>/module-test-kit/module_scope_map.csv
    <pack>/knowledge/...            (the official FSCR repo copy)
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):  # Windows consoles: print dashes and bullets without errors
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

SCRIPTS = Path(__file__).resolve().parent
KIT = SCRIPTS.parent
PACK = KIT.parent
SCOPE_MAP = KIT / "module_scope_map.csv"
COUNTS = KIT / "module_counts.csv"

# Six-task sample groups (PLAYBOOK step 4)
GROUP_SKILL_ROUTE = "Skill + route"
GROUP_ROUTE_ONLY = "Route only"
GROUP_NEITHER = "Neither"


def norm_module(name: str) -> str:
    """Compare module names loosely: case, spaces and dash style (- – —) do not matter."""
    s = name.replace("–", "-").replace("—", "-")
    s = re.sub(r"\s*-\s*", " - ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


def module_names(scope_map: Path = SCOPE_MAP) -> list[str]:
    return sorted({r["tracker_row"] for r in read_csv(scope_map)})


def resolve_module(name: str, scope_map: Path = SCOPE_MAP) -> str:
    """Return the exact tracker_row spelling for a module name, or exit with the list of valid names."""
    names = module_names(scope_map)
    hit = [n for n in names if norm_module(n) == norm_module(name)]
    if not hit:
        sys.exit(f"Module '{name}' is not in {scope_map.name}. Valid names:\n  " + "\n  ".join(names))
    return hit[0]


def task_group(row: dict) -> str:
    """Six-task sample group for one scope-map row.
    Skill + route: level a and the skill names a route.  Route only: level b.  Neither: level c.
    Level a with a skill that names no route ('skill but no route') is in no sample group."""
    if row["level"] == "a":
        return GROUP_SKILL_ROUTE if row.get("skill_but_no_route", "N") != "Y" else "Skill, no route"
    if row["level"] == "b":
        return GROUP_ROUTE_ONLY
    return GROUP_NEITHER


def safe_folder_name(module: str) -> str:
    return re.sub(r"[^A-Za-z0-9 _.-]+", "-", module.replace("–", "-")).strip()
