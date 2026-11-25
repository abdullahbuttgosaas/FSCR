"""Rebuild the FSCR gap-filling dashboard data.

Run from anywhere:  python dashboard\\update.py
Reads (read only):
  gaps-filled/gap_index.csv                         one row per missing task (status, module)
  gaps-filled/gap_progress.tsv                      the 19 owned module names, in tracker order
  gaps-filled/<module>/MODULE_TRACKER.csv           cross-check only
  gaps-filled/<module>/MODULE_RESULT.md             cross-check only
  fscr-main/_fscr_all_module_counts/module_totals.csv   total tasks per module (FSCR catalog)
Writes: dashboard/data/data.json, data.js, history.json
Standard library only. No network.
"""
import csv
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GAPS = os.path.join(ROOT, "gaps-filled")
INDEX = os.path.join(GAPS, "gap_index.csv")
PROGRESS = os.path.join(GAPS, "gap_progress.tsv")
TOTALS = os.path.join(ROOT, "fscr-main", "_fscr_all_module_counts", "module_totals.csv")
OUT = os.path.join(HERE, "data")

STATUS_MAP = {
    "tested": "tested",
    "written": "written",
    "skipped-unsafe": "written",
    "written-unsafe": "written",
    "screen-only": "screen_only",
    "failed": "failed",
    "open": "open",
    "": "open",
}
SEGMENTS = ["tested", "written", "screen_only", "failed", "open"]
LEFT_OUT = {"Security"}  # no gap rows; kept out of every chart


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def owned_modules():
    """The 19 owned modules, in tracker order, from gap_progress.tsv."""
    with open(PROGRESS, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return [r["Module"].strip() for r in rows if not r["Module"].startswith("All ")]


def catalog_totals():
    out = {}
    for r in read_csv(TOTALS):
        out[r["Module"].strip()] = {
            "pillar": r["Pillar"].strip(),
            "total": int(r["Total Tasks"]),
            "catalog_missing": int(r["Missing (b+c)"]),
        }
    return out


def tracker_counts():
    """Counts from each module's MODULE_TRACKER.csv and MODULE_RESULT.md (cross-check)."""
    trackers, results = {}, {}
    for d in sorted(os.listdir(GAPS)):
        p = os.path.join(GAPS, d)
        if not os.path.isdir(p) or d.startswith("_"):
            continue
        t = os.path.join(p, "MODULE_TRACKER.csv")
        if os.path.isfile(t):
            c = {k: 0 for k in SEGMENTS}
            for r in read_csv(t):
                c[STATUS_MAP.get(r.get("status", "").strip().lower(), "open")] += 1
            trackers[d] = c
        m = os.path.join(p, "MODULE_RESULT.md")
        if os.path.isfile(m):
            with open(m, encoding="utf-8") as f:
                text = f.read()
            # first "Cumulative counts" table, else first table with a tested row
            part = text.split("Cumulative counts", 1)[-1]
            tested = re.search(r"^\|\s*tested\s*\|\s*(\d+)", part, re.M)
            written = re.findall(r"^\|\s*written[^|]*\|\s*(\d+)", part.split("\n## ", 1)[0], re.M)
            if tested:
                results[d] = {"tested": int(tested.group(1)),
                              "written": sum(int(x) for x in written)}
    return trackers, results


def main():
    today = datetime.date.today().isoformat()
    rows = read_csv(INDEX)
    totals = catalog_totals()
    names = owned_modules()
    trackers, results = tracker_counts()

    per = {n: {k: 0 for k in SEGMENTS} for n in names}
    unknown_status = 0
    for r in rows:
        mod = r["module"].strip()
        st = r["status"].strip().lower()
        if st not in STATUS_MAP:
            unknown_status += 1
        per.setdefault(mod, {k: 0 for k in SEGMENTS})[STATUS_MAP.get(st, "open")] += 1

    modules, notes = [], []
    for n in names:
        c = per.get(n, {k: 0 for k in SEGMENTS})
        missing = sum(c.values())
        t = totals.get(n)
        m = {"name": n, "pillar": t["pillar"] if t else "", "missing": missing, **c}
        if t is None:
            m.update(total=None, before=None, available=None, check="total not found")
            notes.append(f"{n}: total not found")
        else:
            before = t["total"] - missing
            m.update(total=t["total"], before=before,
                     available=before + c["tested"] + c["written"])
            ok = before >= 0 and before + missing == t["total"] and missing == t["catalog_missing"]
            m["check"] = "ok" if ok else (
                f"index has {missing} missing, catalog says {t['catalog_missing']}")
            if not ok:
                notes.append(f"{n}: {m['check']}")
        m["in_charts"] = n not in LEFT_OUT and missing > 0
        modules.append(m)

    # cross-check the per-module trackers and result files against the index
    folder_of = {"common-features": "Common Features", "procurement": "Procurement",
                 "general-ledger": "General Ledger", "receivables": "Receivables"}
    for d, c in trackers.items():
        n = folder_of.get(d)
        if n and n in per:
            for k in SEGMENTS:
                if per[n][k] != c[k]:
                    notes.append(f"{n}: tracker {k} {c[k]} vs index {per[n][k]}")
    for d, c in results.items():
        n = folder_of.get(d)
        if n and n in per:
            if per[n]["tested"] != c["tested"] or per[n]["written"] != c["written"]:
                notes.append(f"{n}: MODULE_RESULT tested/written {c['tested']}/{c['written']}"
                             f" vs index {per[n]['tested']}/{per[n]['written']}")
    extra = sorted(set(per) - set(names))
    if extra:
        notes.append("modules in index but not owned: " + ", ".join(extra))
    if unknown_status:
        notes.append(f"{unknown_status} rows with an unknown status, counted as open")

    shown = [m for m in modules if m["in_charts"] and m["total"] is not None]
    S = lambda k: sum(m[k] for m in shown)
    summary = {k: S(k) for k in ["total", "before", "available", "missing"] + SEGMENTS}
    summary["gain"] = summary["tested"] + summary["written"]
    summary["gain_pct"] = round(100.0 * summary["gain"] / summary["before"], 1) if summary["before"] else 0
    summary["index_rows"] = len(rows)
    summary["all_missing"] = sum(sum(per[n].values()) for n in per)

    data = {
        "title": "FSCR gap filling: ERP and SCM",
        "updated": today,
        "summary": summary,
        "modules": modules,
        "left_out": [m["name"] for m in modules if not m["in_charts"]],
        "checks": notes or ["all checks passed"],
    }

    os.makedirs(OUT, exist_ok=True)
    hist_path = os.path.join(OUT, "history.json")
    history = []
    if os.path.isfile(hist_path):
        try:
            with open(hist_path, encoding="utf-8") as f:
                history = json.load(f)
        except (ValueError, OSError):
            history = []
    history = [h for h in history if h.get("date") != today]
    history.append({"date": today, "skills_available": summary["available"],
                    "tested": summary["tested"], "written": summary["written"]})
    history.sort(key=lambda h: h["date"])

    with open(os.path.join(OUT, "data.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=1)
    with open(os.path.join(OUT, "data.js"), "w", encoding="utf-8") as f:
        f.write("window.DASHBOARD_DATA = ")
        json.dump(dict(data, history=history), f, separators=(",", ":"))
        f.write(";\n")

    s = summary
    print(f"Updated {today}: {len(shown)} modules in charts (left out: {', '.join(data['left_out']) or 'none'})")
    print(f"Total tasks {s['total']}, skills before {s['before']}, skills available now {s['available']} (+{s['gain']}, {s['gain_pct']}% more)")
    print(f"Missing {s['missing']} (index rows {s['index_rows']}): tested {s['tested']}, written {s['written']}, screen-only {s['screen_only']}, failed {s['failed']}, open {s['open']}")
    top = sorted(shown, key=lambda m: -m["open"])[:3]
    print("Most open: " + ", ".join(f"{m['name']} {m['open']}" for m in top))
    print("Checks: " + "; ".join(data["checks"]) + f" | history points: {len(history)}")
    return 0 if not notes else 1


if __name__ == "__main__":
    sys.exit(main())
