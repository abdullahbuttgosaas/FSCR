"""Added by GoSaaS, not part of official FSCR. Gap fill, sitting 2026-11-25. Offline: no Oracle call.

Builds (or rebuilds) the Common Features gap list and live tracker from files only:
  - gaps-filled/gap_index.csv        (every missing task and its level; never edited here)
  - gaps-filled/<MOD>/*/STATUS.md    (the cards: the truth for finished tasks)
  - gaps-filled/<MOD>/screen-only.csv (tasks proven screen-only, optional)
  - gaps-filled/<MOD>/my_gaps.csv    (decision + reason per task; kept, cards win)

Writes <MOD>/my_gaps.csv (task_code, task_name, level, ease, depends_on, decision, reason) and
<MOD>/MODULE_TRACKER.csv (or MODULE_TRACKER_NEW.csv if the first is locked).

Usage: python -I build_module_tracker.py [--module "Common Features"] [--set CODE=decision|reason ...]
"""
import argparse, csv, sys
from pathlib import Path

HERE = Path(__file__).resolve()
MODDIR = HERE.parents[1]
GF = MODDIR.parent

TRK_HEAD = ["task_code", "task_name", "level", "status", "skill_written", "tested",
            "reason_or_next_step", "test_records", "working_minutes", "date"]
GAP_HEAD = ["task_code", "task_name", "level", "ease", "depends_on", "decision", "reason"]


def read_card(p):
    d = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        k, sep, v = line.partition(":")
        if sep and k.strip() and k.strip() not in d:
            d[k.strip()] = v.strip()
    return d


def num(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", default="Common Features")
    ap.add_argument("--set", action="append", default=[], help="CODE=decision|reason (updates my_gaps.csv)")
    a = ap.parse_args()

    with open(GF / "gap_index.csv", encoding="utf-8", newline="") as f:
        idx = [r for r in csv.DictReader(f) if r["module"] == a.module]

    cards = {}
    for p in MODDIR.glob("*/STATUS.md"):
        c = read_card(p)
        if c.get("task_code"):
            c["_folder"] = p.parent.name
            cards[c["task_code"]] = c

    skills = set()  # task codes that have a SKILL.md (written, maybe not tested yet)
    for p in MODDIR.glob("*/SKILL.md"):
        for line in p.read_text(encoding="utf-8").splitlines()[:20]:
            if line.startswith("task_code:"):
                skills.add(line.split(":", 1)[1].strip().strip('"'))

    screen = {}
    sp = MODDIR / "screen-only.csv"
    if sp.exists():
        with open(sp, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                screen[r["task_code"]] = r.get("reason", "")

    gp = MODDIR / "my_gaps.csv"
    old = {}
    if gp.exists():
        with open(gp, encoding="utf-8", newline="") as f:
            old = {r["task_code"]: r for r in csv.DictReader(f)}
    for s in a.set:
        code, _, rest = s.partition("=")
        dec, _, reason = rest.partition("|")
        old.setdefault(code, {})
        old[code]["decision"] = dec
        old[code]["reason"] = reason

    gaps, trk = [], []
    for r in idx:
        code = r["task_id"]
        o = old.get(code, {})
        c = cards.get(code)
        if c:
            st = c.get("status", "")
            mins = num(c.get("minutes_to_write")) + num(c.get("minutes_to_test"))
            if st == "tested":
                tstat, dec, reason = "tested", "done", ""
            elif st == "written":
                tstat, dec = "skipped-unsafe", "written (unsafe to test)"
                reason = c.get("notes", "")
            elif st == "failed":
                tstat, dec = "failed", "failed"
                reason = c.get("notes", "")
            else:
                tstat, dec, reason = "open", o.get("decision", "open"), o.get("reason", "")
            trk.append([code, r["task_name"], r["level"], tstat, "Y",
                        "Y" if st == "tested" else "N", reason if tstat != "tested" else "",
                        c.get("test_records", ""), f"{mins:g}", c.get("date", "")])
            gaps.append([code, r["task_name"], r["level"], r["ease"], c.get("depends_on", r["depends_on"]),
                         dec, reason if dec != "done" else f"card {c['_folder']}/STATUS.md status tested"])
        elif code in screen:
            trk.append([code, r["task_name"], r["level"], "screen-only", "N", "N", screen[code], "", "0", ""])
            gaps.append([code, r["task_name"], r["level"], r["ease"], r["depends_on"], "screen-only", screen[code]])
        else:
            dec = o.get("decision") or "open"
            reason = o.get("reason") or ("next sitting: check for an FSM CSV (read-only export) and a REST resource before calling it screen-only"
                                         if r["level"] == "neither" else "next sitting: " + (r["notes"].split(" | ")[0]))
            trk.append([code, r["task_name"], r["level"], "open", "Y" if code in skills else "N", "N", reason, "", "0", ""])
            gaps.append([code, r["task_name"], r["level"], r["ease"], r["depends_on"], dec, reason])

    with open(gp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(GAP_HEAD)
        w.writerows(gaps)
    out = MODDIR / "MODULE_TRACKER.csv"
    try:
        f = open(out, "w", encoding="utf-8", newline="")
    except PermissionError:
        out = MODDIR / "MODULE_TRACKER_NEW.csv"
        f = open(out, "w", encoding="utf-8", newline="")
    with f:
        w = csv.writer(f)
        w.writerow(TRK_HEAD)
        w.writerows(trk)
    counts = {}
    for t in trk:
        counts[t[3]] = counts.get(t[3], 0) + 1
    print(f"{out.name}: {len(trk)} rows; " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    sys.exit(main())
