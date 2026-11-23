"""Compare the field names each sampled skill lists with the real CSV columns of FSCR's template export (offline).
Skill fields = backticked CamelCase names and ENTITY::Field pairs found by analyze40.py (skill folder + ora-resource).
Template columns = header row of every CSV in the task's template export ZIP (audit who-columns ignored).
Per task: matched (listed and real), missing (listed but no such column; may include non-column terms), template
columns the skill never names, and coverage = matched / template columns. Also merges the export log into ledger.csv.
Writes evidence/field_compare.json and ledger.csv."""
import csv, glob, io, json, re, zipfile
from pathlib import Path

R5 = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_05_breadth")
A = json.loads((R5 / "evidence/analysis40.json").read_text(encoding="utf-8"))
LOG = (R5 / "evidence/exports/export_all.log").read_text(encoding="utf-8", errors="replace")
AUD = {"CreatedBy", "CreationDate", "LastUpdateDate", "LastUpdatedBy", "LastUpdateLogin", "ObjectVersionNumber"}
res, rows = {}, []
for x in A:
    t = x["task_code"]
    rec = {"export": "not attempted", "pids": [], "matched": None, "missing": None, "unnamed": None, "coverage": None}
    if t and x["csv_supported"] == "Y":
        blk = re.search(r"== %s --template-only start.*?== %s --data end[^\n]*" % (t, t), LOG, re.S)
        b = blk.group(0) if blk else ""
        rec["pids"] = re.findall(r"process: (\d+)", b)
        errs = re.findall(r"(?:Error|Exception)[^\n]{0,200}", b)
        tpl = sorted(glob.glob(str(R5 / "evidence/exports" / t / "*template_export*.zip")))
        data = [z for z in glob.glob(str(R5 / "evidence/exports" / t / "*.zip")) if "template_export" not in z]
        rec["export"] = f"template {'ok' if tpl else 'missing'}, data {'ok' if data else 'missing'}" + (f"; error: {errs[0][:160]}" if errs else "")
        if tpl:
            cols = set()
            for n in zipfile.ZipFile(tpl[0]).namelist():
                if n.endswith(".csv"):
                    h = next(csv.reader(io.StringIO(zipfile.ZipFile(tpl[0]).read(n).decode("utf-8-sig"))), [])
                    cols |= {c.split(".")[-1] for c in h} - AUD
            listed = set(x.get("camel_fields", [])) | {p.split("::")[1].split(".")[-1] for p in x.get("field_pairs", [])}
            m = listed & cols
            rec.update(matched=len(m), missing=sorted(listed - cols)[:15], n_missing=len(listed - cols),
                       unnamed=len(cols - listed), template_cols=len(cols),
                       coverage=round(len(m) / len(cols), 2) if cols else None)
    elif t:
        rec["export"] = f"not possible: catalog CSV export flag {x['csv_supported']} (route {x['route']})"
    else:
        rec["export"] = "no setup task (functional-area, advisory or core skill)"
    res[x["n"]] = rec
    rows.append([x["n"], x["path"], x["area"], x["type"], x["grade"], x["route"], ";".join(x["scripts"]) or "none",
                 "" if rec["coverage"] is None else f"{rec['matched']}/{rec['template_cols']} cols named ({rec['coverage']}); {rec.get('n_missing', 0)} listed names not columns",
                 rec["export"], " ".join(rec["pids"]), x["task_code"] or "", x["execution_mode"]])
(R5 / "evidence/field_compare.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
with open(R5 / "ledger.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["n", "skill", "area", "type", "grade", "route", "scripts", "fields_match", "export_result", "oracle_process_ids", "task_code", "execution_mode"])
    w.writerows(rows)
for n, r in res.items():
    if r["coverage"] is not None or "error" in r["export"]:
        print(n, r["export"][:90], "| cov", r["coverage"], "matched", r["matched"], "of", r.get("template_cols"), "| listed-not-column", r.get("n_missing"), r["missing"][:5])
