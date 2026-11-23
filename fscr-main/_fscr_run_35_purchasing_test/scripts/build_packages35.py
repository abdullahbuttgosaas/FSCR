"""Run 35: build FSM CSV packages holding ONLY new FSCRT_ rows (Run 33/34 build_packages method).
Headers + metadata XML are copied unchanged from the ETIA-TEST export (export_before/<TASK>/unz). Also writes load_specs.json.
Usage: build_packages35.py <TASK_CODE> [...]"""
import csv, zipfile, shutil, sys, json
from pathlib import Path
RUN = Path(__file__).resolve().parents[1]
SPECF = RUN / "scripts" / "load_specs.json"

def build(task, files, names):
    src = RUN / "export_before" / task / "unz"; out = RUN / "payload" / task; out.mkdir(parents=True, exist_ok=True)
    for n in list(out.glob("*")):
        if n.is_file(): n.unlink()
    for name, rows in files.items():
        h = next(csv.reader(open(src / name, encoding="utf-8-sig", newline="")))
        for r in rows: assert set(r) <= set(h), (name, set(r) - set(h))
        with open(out / name, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n"); w.writerow(h)
            for r in rows: w.writerow([r.get(c, "") for c in h])
    shutil.copy(src / "ASM_SETUP_CSV_METADATA.xml", out / "ASM_SETUP_CSV_METADATA.xml")
    z = out / f"{task.lower()}_fscrt.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in ["ASM_SETUP_CSV_METADATA.xml", *files]: zf.write(out / n, n)
    specs = json.load(open(SPECF)) if SPECF.exists() else {}
    specs[task] = {"rowCounts": {k: len(v) for k, v in files.items()}, "names": names}
    json.dump(specs, open(SPECF, "w"), indent=1)
    print("wrote", z); return z

HC, HCN = "FSCRT_R35_HC", "FSCRT_R35 Hazard"
SPEC = {
 "PO_MANAGE_HAZARD_CLASSES": ({
  "PO_HAZARD_CLASS.csv": [dict(HazardClassCode=HC, HazardClass=HCN, Description="FSCR Run 35 test hazard class")],
  "PO_HAZARD_CLASS_TRANSLATION.csv": [{"PO_HAZARD_CLASS.HazardClassCode": HC, "HazardClass": HCN, "Description": "FSCR Run 35 test hazard class", "Language": "US", "SourceLang": "US"}]},
  [HC]),
}
EXTRA = RUN / "scripts" / "extra_specs.py"   # specs for tasks whose export arrives later
if EXTRA.exists(): exec(EXTRA.read_text(encoding="utf-8"))
if __name__ == "__main__":
    for t in sys.argv[1:]: build(t, *SPEC[t])
