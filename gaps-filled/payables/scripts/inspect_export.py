"""Inspect an FSM setup CSV package (export ZIP): CSV files, columns, row counts and, optionally, rows.

Usage:
  python3 inspect_export.py <export.zip>                       # files, row counts, headers
  python3 inspect_export.py <export.zip> --file X.csv --rows 3 # first rows of one CSV
  python3 inspect_export.py <export.zip> --file X.csv --grep FSCRT_AK_GF_
  python3 inspect_export.py <export.zip> --metadata            # metadata keys (values of who-fields hidden)

Who-columns (CreatedBy, LastUpdatedBy, ...) and any value that looks like an e-mail are shown as <hidden>.
Standard library only; read only.
"""
import argparse, csv, io, re, sys, zipfile

WHO = re.compile(r"(CreatedBy|LastUpdatedBy|LastUpdateLogin|SubmittedBy|UserName|User_Name|Owner)$", re.I)
MAIL = re.compile(r"[^@\s]+@[^@\s]+")


def safe(col, val):
    if WHO.search(col or "") or MAIL.search(val or ""):
        return "<hidden>" if val else ""
    return val


def rows_of(zf, name):
    text = zf.read(name).decode("utf-8-sig")
    rd = csv.reader(io.StringIO(text))
    hdr = next(rd, [])
    return hdr, list(rd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip")
    ap.add_argument("--file")
    ap.add_argument("--rows", type=int, default=0)
    ap.add_argument("--grep")
    ap.add_argument("--cols", help="comma list of columns to show")
    ap.add_argument("--metadata", action="store_true")
    a = ap.parse_args()
    zf = zipfile.ZipFile(a.zip)
    if a.metadata:
        for n in zf.namelist():
            if n.lower().endswith(".xml"):
                x = zf.read(n).decode("utf-8", "replace")
                x = re.sub(r"(<[^>]*(SubmittedBy|User|ProcessEnv)[^>]*>)[^<]*", r"\1<hidden>", x, flags=re.I)
                x = re.sub(r"(?<=\n)[^<\n]*<hidden>[^<\n]*", "", x)
                x = MAIL.sub("<hidden>", x)
                print("==", n, "\n", x[:3000])
        return
    names = [n for n in zf.namelist() if n.endswith(".csv")]
    if not a.file:
        others = [n for n in zf.namelist() if not n.endswith(".csv")]
        print("non-CSV files:", others)
        for n in names:
            hdr, rows = rows_of(zf, n)
            print(f"{n}: {len(rows)} rows, {len(hdr)} cols")
            print("   ", ", ".join(hdr))
        return
    hdr, rows = rows_of(zf, a.file)
    cols = a.cols.split(",") if a.cols else hdr
    idx = [hdr.index(c) for c in cols if c in hdr]
    sel = rows
    if a.grep:
        sel = [r for r in rows if any(a.grep in v for v in r)]
    if a.rows:
        sel = sel[: a.rows]
    print(f"{a.file}: showing {len(sel)} of {len(rows)} rows")
    for r in sel:
        print({hdr[i]: safe(hdr[i], r[i] if i < len(r) else "") for i in idx})


if __name__ == "__main__":
    sys.exit(main())
