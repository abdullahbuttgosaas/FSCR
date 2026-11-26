"""Compare two FSM setup CSV exports (before / after an import) file by file.

Prints, per CSV: rows before, rows after, rows added, rows removed. Rows are compared as whole rows with
volatile columns ignored (who/date columns). Then checks that every added row holds the --prefix and that no
row was removed. Exit code 0 = "only rows with the prefix were added, nothing removed or changed".

Usage: python3 compare_fsm_exports.py --before before.zip --after after.zip --prefix FSCRT_AK_GF_
       [--allow-unchanged-parent]   (lists parent rows that appear in both, for hierarchical packages)
Standard library only; read only. Never prints who-column values.
"""
import argparse, csv, io, re, sys, zipfile

VOLATILE = re.compile(r"(CreatedBy|CreationDate|LastUpdatedBy|LastUpdateDate|LastUpdateLogin|ObjectVersionNumber"
                      r"|RequestId|JobDefinition|ProgramUpdateDate|ProgramApplicationId|ProgramId)$", re.I)


def load(path):
    zf = zipfile.ZipFile(path)
    out = {}
    for n in zf.namelist():
        if not n.endswith(".csv"):
            continue
        rd = csv.reader(io.StringIO(zf.read(n).decode("utf-8-sig")))
        hdr = next(rd, [])
        keep = [i for i, h in enumerate(hdr) if not VOLATILE.search(h)]
        rows = [tuple(r[i] if i < len(r) else "" for i in keep) for r in rd]
        out[n] = ([hdr[i] for i in keep], rows)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--prefix", required=True)
    a = ap.parse_args()
    b, f = load(a.before), load(a.after)
    ok = True
    total_added = 0
    for n in sorted(set(b) | set(f)):
        hb, rb = b.get(n, ([], []))
        hf, rf = f.get(n, ([], []))
        if hb and hf and hb != hf:
            print(f"{n}: header differs between exports")
        sb, sf = {}, {}
        for r in rb:
            sb[r] = sb.get(r, 0) + 1
        for r in rf:
            sf[r] = sf.get(r, 0) + 1
        added = [r for r in sf for _ in range(sf[r] - sb.get(r, 0)) if sf[r] > sb.get(r, 0)]
        removed = [r for r in sb for _ in range(sb[r] - sf.get(r, 0)) if sb[r] > sf.get(r, 0)]
        total_added += len(added)
        flag = ""
        bad_add = [r for r in added if not any(a.prefix in v for v in r)]
        if removed or bad_add:
            ok = False
            flag = "  <-- CHECK"
        print(f"{n}: before {len(rb)}, after {len(rf)}, added {len(added)}, removed/changed {len(removed)}{flag}")
        for r in bad_add[:5]:
            print("   added row without prefix:", dict(zip(hf, r)))
        for r in removed[:5]:
            print("   removed/changed row:", dict(zip(hb, r)))
    print("RESULT:", "OK - only prefix rows added, nothing removed or changed" if ok and total_added else
          ("NO ROWS ADDED" if ok else "DIFFERENCES FOUND"))
    return 0 if ok and total_added else 1


if __name__ == "__main__":
    sys.exit(main())
