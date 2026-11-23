"""Run 30: build FSM CSV packages holding ONLY new FSCRT_ rows. Headers + metadata XML copied unchanged from the ETIA-TEST export."""
import csv, zipfile, shutil
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
def build(task, files):
    src = RUN / "export_before" / task / "unz"; out = RUN / "payload" / task; out.mkdir(parents=True, exist_ok=True)
    for name, rows in files.items():
        h = next(csv.reader(open(src / name, encoding="utf-8", newline="")))
        for r in rows: assert set(r) <= set(h), (name, set(r) - set(h))
        with open(out / name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n"); w.writerow(h)
            for r in rows: w.writerow([r.get(c, "") for c in h])
    shutil.copy(src / "ASM_SETUP_CSV_METADATA.xml", out / "ASM_SETUP_CSV_METADATA.xml")
    z = out / f"{task.lower()}_fscrt.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in ["ASM_SETUP_CSV_METADATA.xml", *files]: zf.write(out / n, n)
    print("wrote", z)
build("FND_MANAGE_REFERENCE_DATA_SETS", {"FND_APP_REFERENCE_DATA_SET.csv": [
    dict(SetCode="FSCRT_R30_SET", SetName="FSCRT_R30 Set", Description="FSCR Run 30 test reference data set")]})
build("GL_MANAGE_CONVERSION_RATE_TYPES", {"GL_DAILY_CONVERSION_TYPE.csv": [
    dict(UserConversionType="FSCRT_R30 Rate Type", Description="FSCR Run 30 test conversion rate type",
         SecurityFlag="N", EnforceInverseRateFlag="Y", UserOverrideCrossRateFlag="N", EnableCrossRateFlag="N")],
    "ORA_GL_CONVERSION_RATE_RULE.csv": []})
build("FND_MANAGE_APPLCORE_STANDARD_LOOKUPS", {
    "FND_APP_STANDARD_LOOKUP.csv": [dict(LookupType="FSCRT_R30_LOOKUP", Meaning="FSCRT_R30 Lookup", Description="FSCR Run 30 test lookup type",
        ModuleId="40B3FA7250D19380E040449823C67A1A", CustomizationLevel="U", RestAccessSecured="SECURE")],
    "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv": [
        {"FND_APP_STANDARD_LOOKUP.LookupType": "FSCRT_R30_LOOKUP", "LookupCode": c, "Meaning": m, "EnabledFlag": "Y", "StartDateActive": "2026/01/01", "DisplaySequence": s}
        for c, m, s in [("FSCRT_A", "FSCRT_R30 Alpha", "1"), ("FSCRT_B", "FSCRT_R30 Beta", "2")]]})
