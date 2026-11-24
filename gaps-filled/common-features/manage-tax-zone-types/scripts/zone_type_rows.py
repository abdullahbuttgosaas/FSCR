"""Added by GoSaaS, not part of official FSCR. Gap fill, batch taxfix2 (2026-11-24). Offline: no Oracle call.

Write the --row arguments for ONE new tax zone type (Trading Community geography type, use TAX), for
build_fsm_package.py (@file). Fills CreatedBy and LastUpdatedBy of the type row and its translation row
with the user who ran the read-only export (SubmittedBy in ASM_SETUP_CSV_METADATA.xml), which is the user
that will run the import. Why: if those two columns are EMPTY the setup import validates the row and then
the database insert fails with JBO-26041 (proved 2026-11-24). Prints no user name.

Usage:
  python -I zone_type_rows.py --export-dir <run>/export_before/unz --code GAPFILL_X_ZT1 \
      [--name "Display name"] [--language US] [--limit-like "<existing zone type code>"] --out <run>/rows.txt
  --name        default: the code in Oracle's screen style (underscores to spaces, Title Case).
  --limit-like  copy the country limit (LimitedByGeographyId, GeographyName, BoundaryGeographyType,
                GeographyElement1..10, StartDate, EndDate) from an existing zone type in the export.
                NOT TESTED with the fix (GUESS that it works); without it the zone type has no country limit.
Stops if the code already exists in the export (an import would UPDATE it).
"""
import argparse, csv, re, sys
from pathlib import Path

T = "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.csv"
TL = "ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE_TRANSLATION.csv"
LIMIT_COLS = ["LimitedByGeographyId", "GeographyName", "BoundaryGeographyType", "StartDate", "EndDate"] + \
             [f"GeographyElement{i}" for i in range(1, 11)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--name")
    ap.add_argument("--language", default="US")
    ap.add_argument("--limit-like")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    d = Path(a.export_dir)
    meta = d / "ASM_SETUP_CSV_METADATA.xml"
    for p in (meta, d / T, d / TL):
        if not p.exists():
            sys.exit(f"STOP: {p.name} not in the export folder; run the read-only export first.")
    m = re.search(r"<SubmittedBy>([^<]+)</SubmittedBy>", meta.read_text(encoding="utf-8"))
    if not m:
        sys.exit("STOP: SubmittedBy not found in ASM_SETUP_CSV_METADATA.xml.")
    user = m.group(1).strip()
    for bad in ("|", "\n", '"'):
        if bad in user or bad in a.code or (a.name and bad in a.name):
            sys.exit(f"STOP: character {bad!r} not allowed in code, name or user.")
    with open(d / T, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    codes = {r["GeographyType"] for r in rows}
    if a.code in codes:
        sys.exit(f"STOP: zone type {a.code} already exists in the export (importing would update it). Pick a new code.")
    name = a.name or a.code.replace("_", " ").title()
    t = {"GeographyType": a.code, "GeographyUse": "TAX", "PostalCodeRangeFlag": "N",
         "CreatedByModule": "HZ_GEO_HIERARCHY", "GeographyTypeName": name,
         "CreatedBy": user, "LastUpdatedBy": user}
    if a.limit_like:
        src = [r for r in rows if r["GeographyType"] == a.limit_like]
        if len(src) != 1:
            sys.exit(f"STOP: --limit-like {a.limit_like!r} matches {len(src)} zone types in the export (need 1).")
        if not src[0].get("LimitedByGeographyId"):
            sys.exit(f"STOP: {a.limit_like} has no country limit to copy.")
        for c in LIMIT_COLS:
            if src[0].get(c):
                t[c] = src[0][c]
    tl = {"ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE.GeographyType": a.code, "GeographyType": a.code,
          "GeographyTypeName": name, "Language": a.language, "SourceLang": a.language,
          "CreatedBy": user, "LastUpdatedBy": user}
    lines = ["--row", T + "|" + "|".join(f"{k}={v}" for k, v in t.items()),
             "--row", TL + "|" + "|".join(f"{k}={v}" for k, v in tl.items())]
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {a.out}: 1 zone type row + 1 translation row for {a.code} (name {name!r}); "
          f"who columns = the export's submitting user (not printed); country limit: {'copied from ' + a.limit_like if a.limit_like else 'none'}")


if __name__ == "__main__":
    main()
