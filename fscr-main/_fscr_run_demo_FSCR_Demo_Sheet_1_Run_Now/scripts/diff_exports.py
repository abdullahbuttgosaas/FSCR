"""Local, offline diff of two FSM setup-task CSV export ZIPs (no Oracle call).
Why: FSCR's only compare (shared/baseline-assessment/setup-compare/task-level-compare) uploads both ZIPs to
Fusion and submits a compare process, which is a write and is not allowed in this read-only test.
Rows are matched on a key: the first column in KEYS present in the CSV, else the whole row.
Audit columns (who/when) are ignored when deciding whether a matched row changed.
Usage: diff_exports.py <old.zip> <new.zip> <out.json>"""
import csv, io, json, sys, zipfile

KEYS = ["Name", "BusinessUnitName", "LookupType", "LookupCode", "SequenceNum"]
AUDIT = {"LastUpdateDate", "LastUpdatedBy", "CreationDate", "CreatedBy", "LastUpdateLogin", "ObjectVersionNumber"}


def load(path):
    z = zipfile.ZipFile(path)
    out = {}
    for n in z.namelist():
        if n.lower().endswith(".csv"):
            out[n] = list(csv.DictReader(io.StringIO(z.read(n).decode("utf-8-sig"))))
    return out


def key_of(row, cols):
    ks = [c for c in cols if c in row and row[c] not in (None, "")]
    return tuple((c, row[c]) for c in ks) if ks else tuple(sorted(row.items()))


def main():
    a, b, out = load(sys.argv[1]), load(sys.argv[2]), sys.argv[3]
    report = {"old": sys.argv[1], "new": sys.argv[2], "files": {}}
    for n in sorted(set(a) | set(b)):
        ra, rb = a.get(n, []), b.get(n, []);
        cols = [k for k in KEYS if (ra or rb) and k in (ra or rb)[0]]
        # parent-key columns that identify a child row (e.g. payment term line: SetCode + parent name)
        extra = [c for c in ((ra or rb)[0].keys() if (ra or rb) else []) if c.endswith("Name") or c in ("SetCode", "Language")]
        cols = cols + [c for c in extra if c not in cols]
        ma = {key_of(r, cols): r for r in ra}
        mb = {key_of(r, cols): r for r in rb}
        added = [dict(k) for k in mb if k not in ma]
        removed = [dict(k) for k in ma if k not in mb]
        changed = []
        for k in set(ma) & set(mb):
            d = {c: (ma[k].get(c), mb[k].get(c)) for c in set(ma[k]) | set(mb[k])
                 if c not in AUDIT and ma[k].get(c) != mb[k].get(c)}
            if d:
                changed.append({"key": dict(k), "diff": d})
        report["files"][n] = {"rows_old": len(ra), "rows_new": len(rb), "key_columns": cols,
                              "added": added, "removed": removed, "changed": changed}
    open(out, "w", encoding="utf-8").write(json.dumps(report, indent=1))
    for n, f in report["files"].items():
        print(f"{n}: old {f['rows_old']} new {f['rows_new']} added {len(f['added'])} removed {len(f['removed'])} changed {len(f['changed'])}")


if __name__ == "__main__":
    main()
