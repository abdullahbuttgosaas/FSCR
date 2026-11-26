"""Build an FSM setup CSV import package that holds ONLY new test rows.

Copies the export ZIP (metadata XML and every CSV header) and writes only the rows given in a JSON file;
every other CSV keeps its header and no rows, so no existing record is re-sent.

rows JSON: {"<CSV file name>": [{"<column>": "<value>", ...}, ...], ...}
Special values:
  "@SUBMITTER"  -> replaced by the export metadata's SubmittedBy value (read at run time, never printed).
                   Use it for CreatedBy / LastUpdatedBy when Oracle raises a generic insert error (JBO-26041).
Options:
  --prefix      every row must contain this prefix in at least one value (FSCRT_<initials>_GF_)
  --max-len     COLUMN=N (repeatable): stop if a value is longer than N characters
  --parent-rows FILE.csv=COLUMN=VALUE (repeatable): copy matching rows UNCHANGED from the export
                (hierarchical packages need the parent row in the same ZIP)

Usage: python3 build_fsm_package.py --export export.zip --rows rows.json --prefix FSCRT_AK_GF_ --out load.zip
Standard library only; writes a local ZIP only.
"""
import argparse, csv, io, json, re, sys, zipfile


def submitter(zf):
    for n in zf.namelist():
        if n.lower().endswith(".xml"):
            x = zf.read(n).decode("utf-8", "replace")
            m = re.search(r"<(?:\w+:)?SubmittedBy>([^<]+)<", x)
            if m:
                return m.group(1).strip()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-len", action="append", default=[])
    ap.add_argument("--parent-rows", action="append", default=[])
    a = ap.parse_args()
    if not a.prefix.startswith("FSCRT_"):
        sys.exit("--prefix must start with FSCRT_")
    rows = json.load(open(a.rows, encoding="utf-8"))
    zi = zipfile.ZipFile(a.export)
    names = zi.namelist()
    who = None
    if "@SUBMITTER" in json.dumps(rows):
        who = submitter(zi)
        if not who:
            sys.exit("@SUBMITTER used but no SubmittedBy found in the export metadata")
    limits = {}
    for m in a.max_len:
        c, n = m.rsplit("=", 1)
        limits[c] = int(n)
    parents = {}
    for p in a.parent_rows:
        f, c, v = p.split("=", 2)
        parents.setdefault(f, []).append((c, v))
    for n, rs in rows.items():
        if n not in names:
            sys.exit(f"{n} is not in the package. CSVs: {sorted(x for x in names if x.endswith('.csv'))}")
        for r in rs:
            if not any(a.prefix in str(v) for v in r.values()):
                sys.exit(f"{n}: a row has no value with {a.prefix}; only new test records may be loaded")
            for c, lim in limits.items():
                if c in r and len(str(r[c])) > lim:
                    sys.exit(f"{n}: {c} '{r[c]}' is longer than {lim}")
    counts = {}
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in names:
            data = zi.read(n)
            if n.endswith(".csv"):
                rd = csv.reader(io.StringIO(data.decode("utf-8-sig")))
                hdr = next(rd, [])
                src = list(rd)
                buf = io.StringIO()
                w = csv.writer(buf, lineterminator="\r\n")
                w.writerow(hdr)
                k = 0
                for c, v in parents.get(n, []):
                    i = hdr.index(c)
                    for r in src:
                        if i < len(r) and r[i] == v:
                            w.writerow(r)
                            k += 1
                for r in rows.get(n, []):
                    bad = set(r) - set(hdr)
                    if bad:
                        sys.exit(f"{n}: unknown columns {sorted(bad)}")
                    w.writerow([who if r.get(h) == "@SUBMITTER" else r.get(h, "") for h in hdr])
                    k += 1
                if k:
                    counts[n] = k
                data = buf.getvalue().encode("utf-8")
            zo.writestr(n, data)
    print("wrote package:", ", ".join(f"{k} {v} row(s)" for k, v in counts.items()),
          "; all other CSVs header only")


if __name__ == "__main__":
    sys.exit(main())
