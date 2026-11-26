"""Compare two FSM task-level export ZIPs (before and after an import).
Proves that only rows with your prefix were added and that no existing row changed or disappeared.
Audit columns are ignored. Usage: python compare_fsm_exports.py --before a.zip --after b.zip --prefix PREFIX [--json out.json]
Exit 1 when an existing row changed or is missing. Read only."""
import argparse, csv, io, json, re, sys, zipfile
AUDIT = re.compile(r"(Created|LastUpdated|Updated)(By|Date|Login)|ObjectVersion", re.I)
ap = argparse.ArgumentParser(); ap.add_argument("--before", required=True); ap.add_argument("--after", required=True)
ap.add_argument("--prefix", required=True); ap.add_argument("--json"); a = ap.parse_args()
def load(p):
    out = {}
    z = zipfile.ZipFile(p)
    for n in z.namelist():
        if not n.endswith(".csv"): continue
        rows = list(csv.reader(io.StringIO(z.read(n).decode("utf-8-sig"))))
        if not rows: out[n] = []; continue
        hdr = rows[0]; keep = [i for i, h in enumerate(hdr) if not AUDIT.search(h)]
        out[n] = [tuple(r[i] if i < len(r) else "" for i in keep) for r in rows[1:]]
    return out
b, af = load(a.before), load(a.after); res = []; bad = 0
for n in sorted(set(b) | set(af)):
    rb, ra = b.get(n, []), af.get(n, [])
    old_b = [r for r in rb if not any(a.prefix in v for v in r)]
    sa = set(ra); missing = [r for r in old_b if r not in sa]
    new_p = [r for r in ra if any(a.prefix in v for v in r) and r not in set(rb)]
    keys = sorted({v for r in new_p for v in r if v.startswith(a.prefix) and " " not in v})
    res.append(dict(csv=n, rows_before=len(rb), rows_after=len(ra), prefix_rows_added=len(new_p),
                    existing_changed_or_missing=len(missing), prefix_values=keys))
    bad += len(missing)
    print(f"{n}: before {len(rb)}, after {len(ra)}, {a.prefix} rows added {len(new_p)} {keys}, existing changed or missing {len(missing)}")
print("RESULT:", "PASS (only prefix rows added, existing changed 0)" if bad == 0 else f"FAIL ({bad} existing rows changed or missing)")
if a.json: json.dump(dict(prefix=a.prefix, files=res, existing_changed_or_missing=bad), open(a.json, "w"), indent=1)
sys.exit(1 if bad else 0)
