"""Step 1 - Coverage. Pick one module's tasks from module_scope_map.csv and count them.

Usage:
  python scope_filter.py --list
  python scope_filter.py --module "Procurement" --out work/Procurement

Writes into --out:
  scope_tasks.csv        every task of the module (one row per task code) with its sample group
  coverage.csv           one row: totals a/b/c, Missing N/total, proposed FSCR coverage
  coverage_by_area.csv   the same counts per functional area
  sample_candidates.csv  tasks per six-task group (Skill + route / Route only / Neither)

The counts are re-derived from module_scope_map.csv and compared with module_counts.csv.
If they differ, the script stops with exit code 2 (nothing should be typed by hand).
Levels: a = FSCR skill or guide, b = no skill but the catalog CSV flag is Y, c = neither.
Read only. No sign-in, no network.
"""
from __future__ import annotations

import argparse
import collections
import sys

from kitlib import (COUNTS, SCOPE_MAP, GROUP_NEITHER, GROUP_ROUTE_ONLY, GROUP_SKILL_ROUTE, Path,
                    module_names, read_csv, resolve_module, task_group, write_csv)


def coverage_rule(total: int, a: int) -> tuple[str, str]:
    """Same proxy as the scope map: Full if >= 75% of tasks have a skill or guide, Partial 1-74%, None 0%."""
    if total == 0:
        return "Unknown", "no tasks in this row"
    pct = round(100 * a / total)
    if a == 0:
        return "None", "no task in this row has an FSCR skill or guide"
    if a / total >= 0.75:
        return "Full", f"{a}/{total} ({pct}%) tasks have a skill or guide (rule: >=75% = Full)"
    return "Partial", f"{a}/{total} ({pct}%) tasks have a skill or guide (rule: 1-74% = Partial)"


def count(rows: list[dict]) -> dict:
    lv = collections.Counter(r["level"] for r in rows)
    total = len(rows)
    strict = sum(1 for r in rows if r["level"] == "a" and r["skill_but_no_route"] != "Y")
    no_route = sum(1 for r in rows if r["skill_but_no_route"] == "Y")
    cov, basis = coverage_rule(total, lv["a"])
    return dict(total_tasks=total, a_skill_or_guide=lv["a"], b_route_no_skill=lv["b"], c_neither=lv["c"],
                a_strict_skill_and_route=strict, skill_but_no_route=no_route,
                missing_N_of_total=f"{lv['b'] + lv['c']}/{total}", proposed_coverage=cov, coverage_basis=basis)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", help='tracker row name, for example "Procurement"')
    ap.add_argument("--out", type=Path, help="output folder (created if missing)")
    ap.add_argument("--map", type=Path, default=SCOPE_MAP, help="module_scope_map.csv (default: the kit copy)")
    ap.add_argument("--counts", type=Path, default=COUNTS, help="module_counts.csv (default: the kit copy)")
    ap.add_argument("--list", action="store_true", help="list the module names and stop")
    a = ap.parse_args()

    if a.list:
        for n in module_names(a.map):
            print(n)
        return 0
    if not a.module or not a.out:
        ap.error("--module and --out are required (or use --list)")

    module = resolve_module(a.module, a.map)
    if module == "Unmapped":
        sys.exit("'Unmapped' is not a tracker row. Pick a real module.")
    rows = [r for r in read_csv(a.map) if r["tracker_row"] == module]
    codes = collections.Counter(r["task_code"] for r in rows)
    dup = [c for c, n in codes.items() if n > 1]
    if dup:
        sys.exit(f"Task codes listed twice in the scope map: {dup}")

    for r in rows:
        r["sample_group"] = task_group(r)
    rows.sort(key=lambda r: (r["functional_area"], r["task_name"]))
    write_csv(a.out / "scope_tasks.csv", rows)

    c = count(rows)
    pillar = rows[0]["tracker_pillar"]
    cov_row = dict(pillar=pillar, module=module, **c)

    # Cross-check with module_counts.csv (Run 36 totals shipped with the kit)
    ref = [r for r in read_csv(a.counts) if r["row"] == module]
    check = "not in module_counts.csv"
    if ref:
        r0 = ref[0]
        diffs = [k for k in ("total_tasks", "a_skill_or_guide", "b_route_no_skill", "c_neither",
                             "a_strict_skill_and_route", "skill_but_no_route", "missing_N_of_total", "proposed_coverage")
                 if str(r0[k]) != str(cov_row[k])]
        check = "match" if not diffs else "MISMATCH: " + ", ".join(diffs)
    cov_row["check_vs_module_counts"] = check
    write_csv(a.out / "coverage.csv", [cov_row])

    by_area = []
    for area in sorted({r["functional_area"] for r in rows}):
        sub = [r for r in rows if r["functional_area"] == area]
        x = count(sub)
        by_area.append(dict(functional_area=area, tasks=x["total_tasks"], a_skill_or_guide=x["a_skill_or_guide"],
                            b_route_no_skill=x["b_route_no_skill"], c_neither=x["c_neither"],
                            missing_N_of_total=x["missing_N_of_total"]))
    by_area.append(dict(functional_area=f"Row total: {module}", tasks=c["total_tasks"], a_skill_or_guide=c["a_skill_or_guide"],
                        b_route_no_skill=c["b_route_no_skill"], c_neither=c["c_neither"], missing_N_of_total=c["missing_N_of_total"]))
    write_csv(a.out / "coverage_by_area.csv", by_area)

    cands = [dict(sample_group=r["sample_group"], task_code=r["task_code"], task_name=r["task_name"],
                  functional_area=r["functional_area"], csv_flag=r["csv_flag"], routes_declared=r["routes_declared"],
                  first_skill_path=r["skill_paths"].split(" | ")[0] if r["skill_paths"] else "")
             for r in rows if r["sample_group"] in (GROUP_SKILL_ROUTE, GROUP_ROUTE_ONLY, GROUP_NEITHER)]
    order = {GROUP_SKILL_ROUTE: 0, GROUP_ROUTE_ONLY: 1, GROUP_NEITHER: 2}
    cands.sort(key=lambda r: (order[r["sample_group"]], r["functional_area"], r["task_name"]))
    write_csv(a.out / "sample_candidates.csv", cands)

    g = collections.Counter(r["sample_group"] for r in cands)
    print(f"{module} ({pillar}): {c['total_tasks']} tasks | a {c['a_skill_or_guide']} | b {c['b_route_no_skill']} | "
          f"c {c['c_neither']} | Missing {c['missing_N_of_total']} | coverage {c['proposed_coverage']}")
    print(f"Sample candidates: {GROUP_SKILL_ROUTE} {g[GROUP_SKILL_ROUTE]}, {GROUP_ROUTE_ONLY} {g[GROUP_ROUTE_ONLY]}, "
          f"{GROUP_NEITHER} {g[GROUP_NEITHER]}")
    print(f"Check against module_counts.csv: {check}")
    print(f"Written to {a.out}")
    return 2 if check.startswith("MISMATCH") else 0


if __name__ == "__main__":
    sys.exit(main())
