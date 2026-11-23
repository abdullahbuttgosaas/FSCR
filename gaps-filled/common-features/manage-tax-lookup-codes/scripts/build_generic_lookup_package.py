"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 2 (2026-11-20).

Build a Financials generic lookup CSV package (4 CSVs + metadata XML):
  ORA_FINANCIALS_GENERIC_LOOKUP_TYPE.csv, ORA_FINANCIALS_GENERIC_LOOKUP_TYPE_TRANSLATION.csv,
  FUN_APP_GENERIC_LOOKUP.csv, FUN_APP_GENERIC_LOOKUP_TRANSLATION.csv, ASM_SETUP_CSV_METADATA.xml
holding ONLY one new lookup type and its new codes. Works for any setup task that exports this package
(for example ORA_ZX_MANAGE_TAX_LOOKUP_CODES, XLE_MANAGE_APPLICATION_LOOKUP). Reads headers and the
metadata XML from an unzipped export of the SAME task. Makes no Oracle call. Standard library only (python -I).

Usage:
  python -I build_generic_lookup_package.py --export-dir <unzipped export> --out-dir <run>/payload \
     --view set-enabled --reference-group <REF_GROUP> --set-code COMMON \
     --module-id <ModuleId> --module-key <ModuleKey> --module-type <ModuleType> \
     --type "GAPFILL_XX_TYPE|Meaning|Description" --code "GAPFILL_XX_A|Meaning A|Description A"

--view standard     -> ViewApplicationId 0 (standard lookup view, read back with standardLookups REST)
--view set-enabled  -> ViewApplicationId 2 (set-enabled lookup view, read back with setEnabledLookups REST);
                       needs --reference-group (copy it from an existing set-enabled type of the same module by REST).
ModuleId / ModuleKey / ModuleType: if omitted, copied from the export code rows when they all share one value.
Language for translation rows: --language, else the most common Language in the export translations, else US.
"""
import argparse, collections, csv, shutil, sys, zipfile
from pathlib import Path

T_F, TT_F = "ORA_FINANCIALS_GENERIC_LOOKUP_TYPE.csv", "ORA_FINANCIALS_GENERIC_LOOKUP_TYPE_TRANSLATION.csv"
C_F, CT_F = "FUN_APP_GENERIC_LOOKUP.csv", "FUN_APP_GENERIC_LOOKUP_TRANSLATION.csv"
META = "ASM_SETUP_CSV_METADATA.xml"
FILES = (T_F, TT_F, C_F, CT_F, META)
VIEW_ID = {"standard": "0", "set-enabled": "2"}
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


def one_value(rows, col, arg, name):
    if arg:
        return arg.strip(), "from argument"
    vals = {r.get(col, "") for r in rows if r.get(col)}
    if len(vals) != 1:
        sys.exit(f"STOP: cannot take {col} from the export ({len(vals)} distinct values). Pass {name}.")
    return vals.pop(), "from export"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--type", required=True, help='"LOOKUP_TYPE|Meaning|Description"')
    ap.add_argument("--code", action="append", required=True, help='"CODE|Meaning|Description"')
    ap.add_argument("--view", choices=sorted(VIEW_ID), required=True)
    ap.add_argument("--reference-group", default="")
    ap.add_argument("--set-code", default="COMMON")
    ap.add_argument("--module-id", default="")
    ap.add_argument("--module-key", default="")
    ap.add_argument("--module-type", default="")
    ap.add_argument("--language", default="")
    ap.add_argument("--prefix", default="GAPFILL_")
    ap.add_argument("--max-codes", type=int, default=3)
    ap.add_argument("--zip-name", default="generic_lookup_new.zip")
    a = ap.parse_args()

    src, out = Path(a.export_dir), Path(a.out_dir)
    for n in FILES:
        if not (src / n).exists():
            sys.exit(f"STOP: {n} missing in {src}. This export is not the Financials generic lookup package.")
    th, trows = read(src / T_F)
    tth, _ = read(src / TT_F)
    ch, crows = read(src / C_F)
    cth, ctrows = read(src / CT_F)
    need = {T_F: (th, ("LookupType", "ViewApplicationId", "Meaning", "ModuleId", "ReferenceGroupName")),
            C_F: (ch, ("LookupType", "LookupCode", "ViewApplicationId", "SetCode", "Meaning", "EnabledFlag")),
            CT_F: (cth, ("FUN_APP_GENERIC_LOOKUP.LookupType", "FUN_APP_GENERIC_LOOKUP.LookupCode", "Language")),
            TT_F: (tth, ("ORA_FINANCIALS_GENERIC_LOOKUP_TYPE.LookupType", "Language"))}
    for f, (h, cols) in need.items():
        for c in cols:
            if c not in h:
                sys.exit(f"STOP: column {c} missing in {f}")

    ltype, tmean, tdesc = split3(a.type)
    codes = [split3(c) for c in a.code]
    if len(codes) > a.max_codes:
        sys.exit(f"STOP: {len(codes)} codes > --max-codes {a.max_codes}")
    for key in [ltype] + [c[0] for c in codes]:
        if not key.startswith(a.prefix):
            sys.exit(f"STOP: {key!r} must start with {a.prefix}")
        if len(key) > MAX_KEY or not key.replace("_", "").isalnum() or key.upper() != key:
            sys.exit(f"STOP: {key!r} must be upper case letters, digits and _ only, at most {MAX_KEY} characters")
    for _, m, d in [(ltype, tmean, tdesc)] + codes:
        if not m or len(m) > MAX_MEANING or len(d) > MAX_DESC:
            sys.exit(f"STOP: meaning must be 1-{MAX_MEANING} chars and description at most {MAX_DESC}: {m!r}")
    if len({c[0] for c in codes}) != len(codes) or len({c[1].casefold() for c in codes}) != len(codes):
        sys.exit("STOP: codes and their meanings must be unique")
    if any(r["LookupType"] == ltype for r in trows + crows):
        sys.exit(f"STOP: {ltype} already exists in the export; importing it would UPDATE it. Pick a new name.")
    if a.view == "set-enabled" and not a.reference_group:
        sys.exit("STOP: --view set-enabled needs --reference-group (read it by REST from an existing set-enabled type).")
    if a.view == "standard" and a.reference_group:
        sys.exit("STOP: a standard-view type has no reference group; drop --reference-group.")

    module_id, src_mid = one_value(crows, "ModuleId", a.module_id, "--module-id")
    module_key, _ = one_value(crows, "ModuleKey", a.module_key, "--module-key")
    module_type, _ = one_value(crows, "ModuleType", a.module_type, "--module-type")
    lang = a.language or (collections.Counter(r["Language"] for r in ctrows if r.get("Language")).most_common(1) or [("US", 0)])[0][0]
    vid = VIEW_ID[a.view]

    out.mkdir(parents=True, exist_ok=True)

    def write(name, header, dicts):
        with open(out / name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
            w.writerow(header)
            for d in dicts:
                w.writerow([d.get(c, "") for c in header])

    def keep(h, d):  # only columns this export really has; ChangeSinceLastRefresh is REQUIRED (import fails if empty)
        d = dict(d, ChangeSinceLastRefresh="N")
        return {k: v for k, v in d.items() if k in h}

    write(T_F, th, [keep(th, {"LookupType": ltype, "ViewApplicationId": vid, "Meaning": tmean, "Description": tdesc,
                              "ModuleId": module_id, "ModuleKey": module_key, "ModuleType": module_type,
                              "CustomizationLevel": "U", "RestAccessSecured": "SECURE",
                              "ReferenceGroupName": a.reference_group})])
    p = "ORA_FINANCIALS_GENERIC_LOOKUP_TYPE."
    write(TT_F, tth, [keep(tth, {p + "LookupType": ltype, p + "ViewApplicationId": vid, "LookupType": ltype,
                                 "ViewApplicationId": vid, "Meaning": tmean, "Description": tdesc,
                                 "Language": lang, "SourceLang": lang})])
    write(C_F, ch, [keep(ch, {"LookupType": ltype, "LookupCode": c, "ViewApplicationId": vid, "SetCode": a.set_code,
                              "Meaning": m, "Description": d, "EnabledFlag": "Y", "DisplaySequence": str(i),
                              "ModuleId": module_id, "ModuleKey": module_key, "ModuleType": module_type})
                    for i, (c, m, d) in enumerate(codes, 1)])
    q = "FUN_APP_GENERIC_LOOKUP."
    write(CT_F, cth, [keep(cth, {q + "LookupType": ltype, q + "LookupCode": c, q + "ViewApplicationId": vid,
                                 q + "SetCode": a.set_code, "LookupType": ltype, "LookupCode": c, "ViewApplicationId": vid,
                                 "Meaning": m, "Description": d, "Language": lang, "SourceLang": lang})
                      for (c, m, d) in codes])
    shutil.copy(src / META, out / META)
    z = out / a.zip_name
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in FILES:
            zf.write(out / n, n)
    print(f"type {ltype} ({a.view}, ViewApplicationId {vid}) with {len(codes)} codes, set {a.set_code}, "
          f"language {lang}; module values {src_mid}")
    print("wrote", z)


if __name__ == "__main__":
    main()
