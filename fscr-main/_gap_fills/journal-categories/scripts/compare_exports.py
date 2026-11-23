"""Added by GoSaaS, not part of official FSCR. Origin: Run 24, ETIA-TEST. Offline: no Oracle call.
Compare the export taken BEFORE the import with the export taken AFTER it.
Usage: python -I compare_exports.py <before unzipped dir> <after unzipped dir> [--prefix FSCRT_] [--expect "name1" --expect "name2"] [--rows-out verify_rows.csv]
Exit 0 only if: only the expected new rows were added, nothing removed, no existing row changed."""
import argparse, csv, sys
D, T = "GL_JOURNAL_CATEGORY_DEF.csv", "GL_JOURNAL_CATEGORY_DEF_TRANSLATION.csv"
ap = argparse.ArgumentParser(); ap.add_argument("before"); ap.add_argument("after")
ap.add_argument("--prefix", default="FSCRT_"); ap.add_argument("--expect", action="append", default=[]); ap.add_argument("--rows-out")
a = ap.parse_args()
load = lambda d, f: list(csv.DictReader(open(f"{d}/{f}", encoding="utf-8", newline="")))
b, n = load(a.before, D), load(a.after, D)
kb, kn = {r["JeCategoryName"]: r for r in b}, {r["JeCategoryName"]: r for r in n}
added, removed = sorted(set(kn) - set(kb)), sorted(set(kb) - set(kn))
changed = [k for k in kb if k in kn and kb[k] != kn[k]]
print(f"before {len(b)}  after {len(n)}  added {added}  removed {removed}  existing rows changed {len(changed)}")
tr = {r["JeCategoryName"] for r in load(a.after, T) if r["JeCategoryName"] in added}
print("translation rows for added:", sorted(tr))
ok = not removed and not changed and all(x.startswith(a.prefix) for x in added) and tr == set(added) \
     and (not a.expect or sorted(a.expect) == added)
if a.rows_out:
    cols = ["JeCategoryName", "UserJeCategoryName", "JeCategoryKey", "Description", "CreationDate", "CreatedBy"]
    with open(a.rows_out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(kn[k] for k in added)
print("RESULT:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
