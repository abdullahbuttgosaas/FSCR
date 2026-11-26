"""Rebuild my_gaps.csv and MODULE_TRACKER.csv for one module from the truth:
STATUS.md cards under the module folder, screen-only.csv and the seed list.

Usage: python3 build_tracker.py   (run from anywhere; paths are relative to this file)
Standard library only. Never writes user names, tokens or server addresses.
"""
import csv, datetime, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD_DIR = os.path.dirname(HERE)                       # gaps-filled/<module>
PACK = os.path.dirname(os.path.dirname(MOD_DIR))      # pack root
sys.path.insert(0, HERE)
from gaps_seed import SEED  # noqa: E402

SCOPE = os.path.join(PACK, "evidence", "Payables", "data", "scope_tasks.csv")
LEVEL_WORDS = {"b": "route only", "c": "neither"}


def read_cards():
    cards = {}
    for root, _dirs, files in os.walk(MOD_DIR):
        if "STATUS.md" in files and os.path.abspath(root) != os.path.abspath(MOD_DIR):
            d = {}
            with open(os.path.join(root, "STATUS.md"), encoding="utf-8") as fh:
                for line in fh:
                    if ":" in line:
                        k, v = line.split(":", 1)
                        d[k.strip()] = v.strip()
            if d.get("task_code"):
                d["_folder"] = os.path.relpath(root, MOD_DIR)
                cards[d["task_code"]] = d
    return cards


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path, header, rows):
    try:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=header)
            w.writeheader()
            w.writerows(rows)
        return path
    except PermissionError:
        alt = path.replace(".csv", "_NEW.csv")
        with open(alt, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=header)
            w.writeheader()
            w.writerows(rows)
        return alt


def minutes(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def main():
    scope = {r["task_code"]: r for r in read_csv(SCOPE) if r["level"] in ("b", "c")}
    cards = read_cards()
    screen = {r["task_code"]: r for r in read_csv(os.path.join(MOD_DIR, "screen-only.csv"))}
    notes = {r["task_code"]: r for r in read_csv(os.path.join(MOD_DIR, "open_notes.csv"))}
    seed = sorted(SEED, key=lambda s: s[0])
    today = datetime.date.today().isoformat()

    gaps, tracker = [], []
    for rank, code, ease, dep, decision, reason in seed:
        s = scope[code]
        level = LEVEL_WORDS[s["level"]]
        card = cards.get(code)
        ease_w = {0: "n/a", 1: "easy", 2: "medium", 3: "hard"}[ease]
        dep_v = card.get("depends_on", dep) if card else dep
        row_t = dict(task_code=code, task_name=s["task_name"], level=level, status="open",
                     skill_written="N", tested="N", reason_or_next_step="", test_records="",
                     working_minutes="", date="")
        if card:
            st = card.get("status", "")
            nt = card.get("notes", "")
            row_t.update(skill_written="Y", test_records=card.get("test_records", ""),
                         working_minutes=str(round(minutes(card.get("minutes_to_write")) +
                                                   minutes(card.get("minutes_to_test")))),
                         date=card.get("date", ""))
            if st == "tested":
                row_t.update(status="tested", tested="Y")
                decision, reason = "filled", "tested (fresh test passed)"
            elif st == "failed":
                row_t.update(status="failed", reason_or_next_step=nt)
                decision, reason = "failed", nt
            elif st.startswith("written"):
                unsafe = nt.lower().startswith("unsafe")
                row_t.update(status="skipped-unsafe" if unsafe else "written-untested",
                             reason_or_next_step=nt)
                decision, reason = ("written (unsafe to test)" if unsafe else "written"), nt
        elif code in screen:
            row_t.update(status="screen-only", reason_or_next_step=screen[code]["reason"], date=today)
            decision, reason = "screen-only", screen[code]["reason"]
        elif code in notes:
            row_t.update(reason_or_next_step=notes[code].get("note", ""))
        if not card and code not in screen and not row_t["reason_or_next_step"]:
            row_t["reason_or_next_step"] = "not started; planned order %d (%s)" % (rank, ease_w)
        gaps.append(dict(task_code=code, task_name=s["task_name"], level=level, ease=ease_w,
                         depends_on=dep_v, decision=decision, reason=reason))
        tracker.append(row_t)

    missing = set(scope) - {s[1] for s in seed}
    if missing:
        sys.exit("seed is missing tasks: %s" % sorted(missing))

    write_csv(os.path.join(MOD_DIR, "my_gaps.csv"),
              ["task_code", "task_name", "level", "ease", "depends_on", "decision", "reason"], gaps)
    out = write_csv(os.path.join(MOD_DIR, "MODULE_TRACKER.csv"),
                    ["task_code", "task_name", "level", "status", "skill_written", "tested",
                     "reason_or_next_step", "test_records", "working_minutes", "date"], tracker)
    counts = {}
    for r in tracker:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("tracker:", os.path.basename(out), "rows", len(tracker), counts)


if __name__ == "__main__":
    main()
