"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 1 (2026-11-20).

Build a standard-lookup CSV package (FND_APP_STANDARD_LOOKUP + ORA_FND_APP_STANDARD_LOOKUP_CODE)
that holds ONLY one new lookup type and its new codes. Works for any setup task that exports the
standard lookup package (for example FND_MANAGE_APPLCORE_STANDARD_LOOKUPS, HZ_MANAGE_GEOGRAPHY_LOOKUPS,
HZ_MANAGE_RESOURCE_NOTE_TYPE). Reads headers and the metadata XML from an unzipped export of the
SAME task. Makes no Oracle call. Standard library only (run with python -I).

Usage:
  python -I build_lookup_package.py --export-dir <unzipped export> --out-dir <run>/payload \
     --type "GAPFILL_XX_TYPE|Meaning|Description" \
     --code "GAPFILL_A|Meaning A|Description A" --code "GAPFILL_B|Meaning B|" \
     [--module-id <ModuleId>] [--prefix GAPFILL_] [--zip-name x.zip]

ModuleId: if omitted, it is copied from the export rows when they all share one value.
If the export has no rows, pass --module-id (read it from a lookup type of the same module by REST,
see SKILL.md) or the script stops.
"""
import argparse, csv, shutil, sys, zipfile
from pathlib import Path

TYPE_F, CODE_F, META = "FND_APP_STANDARD_LOOKUP.csv", "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv", "ASM_SETUP_CSV_METADATA.xml"
PARENT_COL = "FND_APP_STANDARD_LOOKUP.LookupType"
MAX_KEY, MAX_MEANING, MAX_DESC = 30, 80, 240


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.reader(f)
        h = next(r)
        return h, [dict(zip(h, row)) for row in r]


def split3(s):
    parts = [x.strip() for x in s.split("|")]
    parts += [""] * (3 - len(parts))
    return parts[0], parts[1], parts[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--type", required=True, help='"LOOKUP_TYPE|Meaning|Description"')
    ap.add_argument("--code", action="append", required=True, help='"CODE|Meaning|Description"')
    ap.add_argument("--module-id", default="")
    ap.add_argument("--prefix", default="GAPFILL_")
    ap.add_argument("--max-codes", type=int, default=3)
    ap.add_argument("--zip-name", default="standard_lookup_new.zip")
    a = ap.parse_args()

    src, out = Path(a.export_dir), Path(a.out_dir)
    for n in (TYPE_F, CODE_F, META):
        if not (src / n).exists():
            sys.exit(f"STOP: {n} missing in {src}. This export is not the standard lookup package.")
    th, trows = read(src / TYPE_F)
    ch, crows = read(src / CODE_F)
    for col in ("LookupType", "Meaning", "Description", "ModuleId"):
        if col not in th:
            sys.exit(f"STOP: column {col} missing in {TYPE_F}")
    for col in (PARENT_COL, "LookupCode", "Meaning", "EnabledFlag"):
        if col not in ch:
            sys.exit(f"STOP: column {col} missing in {CODE_F}")

    ltype, tmean, tdesc = split3(a.type)
    codes = [split3(c) for c in a.code]
    if len(codes) > a.max_codes:
        sys.exit(f"STOP: {len(codes)} codes > --max-codes {a.max_codes}")
    if not ltype.startswith(a.prefix):
        sys.exit(f"STOP: lookup type must start with {a.prefix}: {ltype!r}")
    for key in [ltype] + [c[0] for c in codes]:
        if len(key) > MAX_KEY or not key.replace("_", "").isalnum() or key.upper() != key:
            sys.exit(f"STOP: {key!r} must be upper case letters, digits and _ only, at most {MAX_KEY} characters")
    for c in codes:
        if not c[0].startswith(a.prefix):
            sys.exit(f"STOP: lookup code must start with {a.prefix}: {c[0]!r}")
    if not tmean:
        sys.exit("STOP: the lookup type needs a meaning")
    for _, m, d in [(ltype, tmean, tdesc)] + codes:
        if not m or len(m) > MAX_MEANING or len(d) > MAX_DESC:
            sys.exit(f"STOP: meaning must be 1-{MAX_MEANING} chars and description at most {MAX_DESC}: {m!r}")
    if len({c[0] for c in codes}) != len(codes) or len({c[1].casefold() for c in codes}) != len(codes):
        sys.exit("STOP: codes and their meanings must be unique")
    if any(r["LookupType"] == ltype for r in trows):
        sys.exit(f"STOP: {ltype} already exists in the export; importing it would UPDATE it. Pick a new name.")

    module_id = a.module_id.strip()
    if not module_id:
        mods = {r["ModuleId"] for r in trows if r.get("ModuleId")}
        if len(mods) != 1:
            sys.exit("STOP: cannot take ModuleId from the export (it has %d distinct values). Pass --module-id." % len(mods))
        module_id = mods.pop()

    out.mkdir(parents=True, exist_ok=True)

    def write(name, header, dicts):
        with open(out / name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
            w.writerow(header)
            for d in dicts:
                w.writerow([d.get(c, "") for c in header])

    write(TYPE_F, th, [{"LookupType": ltype, "Meaning": tmean, "Description": tdesc, "ModuleId": module_id,
                        "CustomizationLevel": "U" if "CustomizationLevel" in th else "",
                        "RestAccessSecured": "SECURE" if "RestAccessSecured" in th else ""}])
    write(CODE_F, ch, [{PARENT_COL: ltype, "LookupCode": c, "Meaning": m, "Description": d, "EnabledFlag": "Y",
                        "DisplaySequence": str(i)} for i, (c, m, d) in enumerate(codes, 1)])
    shutil.copy(src / META, out / META)
    z = out / a.zip_name
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in (META, TYPE_F, CODE_F):
            zf.write(out / n, n)
    print(f"type {ltype} with {len(codes)} codes; ModuleId taken {'from --module-id' if a.module_id else 'from export'}")
    print("wrote", z)


if __name__ == "__main__":
    main()
