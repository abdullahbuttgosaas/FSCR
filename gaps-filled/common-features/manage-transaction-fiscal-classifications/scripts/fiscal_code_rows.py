"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 4 part 2 (2026-11-24). Offline: no Oracle call.

Write the 4 rows of ONE new tax fiscal classification code, copied from a template code of the same family
in an unzipped export of the fiscal classification package (ZX_MANAGE_TRANSACTION_FISCAL_CLASSIFICATIONS,
ORA_ZX_MANAGE_TRANSACTION_BASED_FISCAL_CLASSIFICATIONS, ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS):
  <code file>, <code file>_TRANSLATION, <denorm file>, <denorm file>_TRANSLATION
The rows go to --out in the "--row" format of build_fsm_package.py (read it with @file).

Families (code file / denorm file / parent type file):
  trx      ORA_ZX_TRANSACTION_CODE              / ORA_ZX_TRAN_DENORM_CLASS_CODE / ORA_ZX_TRANSACTION
  user     ORA_USER_DEFINED_CLASSIFICATION_CODE / ORA_ZX_USER_DENORM_CLASS_CODE / ORA_ZX_USER_DEFINED_TYPE
  product  ORA_ZX_PRODUCT_CLASS_CODE            / ORA_ZX_PRODUCT_CLASS_DENORM   / ORA_ZX_PRODUCT_CLASS_GENERIC

Usage:
  python -I fiscal_code_rows.py --export-dir <RUN>/export_before/unz --family trx \
      --template-code "OPERATION FISCAL CODE" [--template-parent PURCHASE_TRANSACTION] \
      --code GAPFILL_XX_TBC1 --name "Gapfill XX TBC1" --from 2026/01/01 --out <RUN>/rows.txt [--lang US] [--keep-country]

- The template is chosen by code (+ parent code when the code appears under several parents). Exactly one
  code row must match, or it stops. The new code gets the SAME parent and level as the template.
- Every value equal to the template code becomes the new code, every value equal to the template name becomes
  the new name, and path values ending in "/<template code>" or "/<template name>" are rewritten the same way.
- RecordTypeCode=USER_DEFINED, EffectiveFrom=--from, EffectiveTo and (unless --keep-country) CountryCode are
  cleared, audit columns (CreatedBy, CreationDate, LastUpdateDate, LastUpdateLogin, LastUpdatedBy) are cleared.
- It stops if the new code already exists in the code file, or a value holds "|".
- It prints the parent type file and type code, to copy UNCHANGED with copy_parent_rows.py.
"""
import argparse, csv, sys
from pathlib import Path

FAM = {
    "trx": ("ORA_ZX_TRANSACTION_CODE", "ORA_ZX_TRAN_DENORM_CLASS_CODE", "ORA_ZX_TRANSACTION"),
    "user": ("ORA_USER_DEFINED_CLASSIFICATION_CODE", "ORA_ZX_USER_DENORM_CLASS_CODE", "ORA_ZX_USER_DEFINED_TYPE"),
    "product": ("ORA_ZX_PRODUCT_CLASS_CODE", "ORA_ZX_PRODUCT_CLASS_DENORM", "ORA_ZX_PRODUCT_CLASS_GENERIC"),
}
AUDIT = {"CreatedBy", "CreationDate", "LastUpdateDate", "LastUpdateLogin", "LastUpdatedBy"}


def read(d, name):
    p = Path(d) / (name + ".csv")
    if not p.exists():
        sys.exit(f"STOP: {p.name} not in the export")
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def col(row, suffix):
    """value of the column named suffix, or <anything>.suffix (first match)"""
    if suffix in row:
        return row[suffix]
    for k in row:
        if k.endswith("." + suffix):
            return row[k]
    return None


def rewrite(row, a, tcode, tname, extra=None):
    out = {}
    for k, v in row.items():
        if k in AUDIT:
            v = ""
        elif v == tcode:
            v = a.code
        elif v == tname:
            v = a.name
        elif v.endswith("/" + tcode):
            v = v[: -len(tcode)] + a.code
        elif tname and v.endswith("/" + tname):
            v = v[: -len(tname)] + a.name
        base = k.split(".")[-1]
        if base == "RecordTypeCode":
            v = "USER_DEFINED"
        if base == "EffectiveFrom":
            v = a.date_from
        if base == "EffectiveTo":
            v = ""
        if base == "CountryCode" and not a.keep_country:
            v = ""
        if "|" in v:
            sys.exit(f"STOP: value of {k} holds '|'")
        out[k] = v
    return out


def emit(fname, row):
    parts = [f"{k}={v}" for k, v in row.items() if v != ""]
    return "--row\n" + fname + ".csv|" + "|".join(parts) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--export-dir", required=True)
    ap.add_argument("--family", required=True, choices=sorted(FAM))
    ap.add_argument("--template-code", required=True)
    ap.add_argument("--template-parent", default=None)
    ap.add_argument("--code", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--from", dest="date_from", required=True)
    ap.add_argument("--lang", default="US")
    ap.add_argument("--keep-country", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cfile, dfile, tfile = FAM[a.family]
    d = a.export_dir

    codes = read(d, cfile)
    if any(r["ClassificationCode"] == a.code for r in codes):
        sys.exit(f"STOP: {a.code} already exists in {cfile}.csv (importing it would update it)")
    hits = [r for r in codes if r["ClassificationCode"] == a.template_code
            and (a.template_parent is None or r.get("ParentClassificationCode", "") == a.template_parent)]
    if len(hits) != 1:
        sys.exit(f"STOP: template matched {len(hits)} code rows; give --template-parent to pick one")
    t = hits[0]
    tcode, tname, tparent = t["ClassificationCode"], t["ClassificationName"], t.get("ParentClassificationCode", "")
    ttype = t["ClassificationTypeCode"]
    text = emit(cfile, rewrite(t, a, tcode, tname))

    tr = [r for r in read(d, cfile + "_TRANSLATION")
          if col(r, "ClassificationCode") == tcode and (col(r, "ParentClassificationCode") or "") == tparent
          and r.get("Language") == a.lang]
    if len(tr) != 1:
        sys.exit(f"STOP: {len(tr)} template translation rows for language {a.lang}; need 1 (try --lang)")
    text += emit(cfile + "_TRANSLATION", rewrite(tr[0], a, tcode, tname))

    path = (tparent + "/" + tcode) if tparent else tcode
    dn = [r for r in read(d, dfile) if r.get("ClassificationCode") == tcode and r.get("ConcatClassifCode") == path]
    if len(dn) != 1:
        sys.exit(f"STOP: {len(dn)} template denorm rows with ConcatClassifCode={path}; need 1")
    text += emit(dfile, rewrite(dn[0], a, tcode, tname))
    dt = [r for r in read(d, dfile + "_TRANSLATION")
          if col(r, "ClassificationCode") == tcode and col(r, "ConcatClassifCode") in (None, path)
          and r.get("Language") == a.lang]
    if len(dt) != 1:
        sys.exit(f"STOP: {len(dt)} template denorm translation rows; need 1")
    text += emit(dfile + "_TRANSLATION", rewrite(dt[0], a, tcode, tname))

    Path(a.out).write_text(text, encoding="utf-8")
    newpath = (tparent + "/" + a.code) if tparent else a.code
    print(f"wrote 4 rows to {a.out}: {cfile}, {cfile}_TRANSLATION, {dfile}, {dfile}_TRANSLATION")
    print(f"new code {a.code} under type {ttype}, parent '{tparent or '-'}', path {newpath}")
    print(f"PARENT: copy unchanged: --file {tfile}.csv --where ClassificationTypeCode={ttype}")


if __name__ == "__main__":
    main()
