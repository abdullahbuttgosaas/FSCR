"""Post-freeze: compare manual Configuration Master Checklist tasks with the frozen Run 15 task map."""
import csv, json, re, sys
from collections import Counter, defaultdict

cmc, mine_csv, catalog_path, fa_csv, out_csv = sys.argv[1:6]
def norm(s):
    s = re.sub(r"[^a-z0-9]+", "", (s or "").lower())
    return re.sub(r"task$", "", s)

# manual tasks
sheet, manual = None, []
for line in open(cmc, encoding="utf-8"):
    line = line.rstrip("\n")
    m = re.match(r"### SHEET: (\w+)", line)
    if m:
        sheet = m.group(1); continue
    if not sheet or "|" not in line or line.startswith("Task List"):
        continue
    parts = [p.strip() for p in line.split("|")]
    name = parts[0]
    if not name or all(not p for p in parts[1:]):   # group header with empty trailing cells
        continue
    manual.append((sheet, name, parts[2] if len(parts) > 2 else ""))

mine = list(csv.DictReader(open(mine_csv, encoding="utf-8")))
mine_names = defaultdict(list)
for r in mine:
    mine_names[norm(r["Matched Task Name"])].append(r)
tbd_fas = {(r["offering_code"], r["fa_code"]) for r in csv.DictReader(open(fa_csv, encoding="utf-8")) if r["scope_class"] == "TBD"}

cat = json.load(open(catalog_path, encoding="utf-8"))
cat_loc = defaultdict(set)
for oc, o in cat["offerings"].items():
    for fc, f in o["functionalAreas"].items():
        for t in f.get("tasks", []):
            cat_loc[norm(t["taskName"])].add((oc, fc, f["functionalAreaName"]))

rows, stat = [], Counter()
for sheet, name, owner in manual:
    k = norm(name)
    if k in mine_names:
        status, why = "covered", "same task name in Run 15 map: " + ", ".join(sorted({r['Functional Area'] for r in mine_names[k]}))
    elif k in cat_loc and any((oc, fc) in tbd_fas for oc, fc, _ in cat_loc[k]):
        status, why = "partly", "in an FA listed as TBD (not expanded): " + ", ".join(sorted({n for oc, fc, n in cat_loc[k] if (oc, fc) in tbd_fas}))
    elif k in cat_loc:
        status, why = "missed", "in catalog FA(s) not selected: " + ", ".join(sorted({n for _, _, n in cat_loc[k]})[:4])
    else:
        status, why = "missed", "name not in FSCR effective catalog (custom / renamed / Redwood)"
    stat[(sheet, status)] += 1
    rows.append({"Sheet": sheet, "Manual task": name, "Manual owner": owner, "Status": status, "Reason": why})

with open(out_csv, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

tot = Counter(r["Status"] for r in rows)
print("manual task rows parsed:", len(rows), dict(tot))
for s in ["Financials", "Procurement", "Inventory", "Costing", "Manufacturing", "Maintenance", "PIM"]:
    print(s, {st: stat[(s, st)] for st in ("covered", "partly", "missed")})
miss_reason = Counter(r["Reason"].split(":")[0] for r in rows if r["Status"] == "missed")
print(miss_reason)
fa_missed = Counter()
for r in rows:
    if r["Status"] == "missed" and r["Reason"].startswith("in catalog"):
        for n in r["Reason"].split(": ", 1)[1].split(", "):
            fa_missed[n] += 1
print("FAs of missed:", fa_missed.most_common(15))
manual_keys = {norm(n) for _, n, _ in manual}
extra = [r for r in mine if norm(r["Matched Task Name"]) not in manual_keys]
print("Run15 rows not in manual list:", len(extra), "unique names:", len({norm(r['Matched Task Name']) for r in extra}))
print("Run15 unique names:", len(mine_names), "matched to manual:", len(set(mine_names) & manual_keys))
print(Counter(r["Functional Area"] for r in extra).most_common(12))
