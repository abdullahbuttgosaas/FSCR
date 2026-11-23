"""Run 34 step 5 (from Run 33 gen_images.py): clear PNG table images at 2x (Edge headless, device scale factor 2). Numbers are read from the run's own files."""
import csv, json, html, subprocess, re, sys, pathlib
RUN = pathlib.Path(__file__).resolve().parents[1]; ROOT = RUN.parent
OUT = ROOT / "_fscr_evidence_pack" / "sourcing_supplier"; OUT.mkdir(parents=True, exist_ok=True)
TMP = RUN / "evidence" / "img_html"; TMP.mkdir(parents=True, exist_ok=True)
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
T = json.load(open(RUN / "scripts/tracker.json", encoding="utf-8"))
SIX = json.load(open(RUN / "scripts/six_tasks.json", encoding="utf-8"))
PS = json.load(open(RUN / "evidence/plan_summary.json")); RS = json.load(open(RUN / "runbook/runbook_summary.json"))
areas = list(csv.DictReader(open(ROOT / "_fscr_run_32_procurement_coverage/area_counts.csv", encoding="utf-8")))
e = html.escape
CSS = """body{margin:0;background:#fff;font-family:'Segoe UI',Arial,sans-serif;color:#1b2a3a}
.w{width:1400px;padding:28px 32px 20px}h1{font-size:26px;margin:0 0 6px}.sub{color:#5a6b7d;font-size:14px;margin-bottom:16px}
table{border-collapse:collapse;width:100%;font-size:15px}th{background:#1f3b57;color:#fff;text-align:left;padding:8px 10px}
td{padding:7px 10px;border-bottom:1px solid #d9e0e7;vertical-align:top}tr:nth-child(even) td{background:#f5f8fb}
.f{margin-top:14px;color:#5a6b7d;font-size:12.5px;border-top:1px solid #d9e0e7;padding-top:8px}
.ok{color:#1a7f37;font-weight:600}.bad{color:#b42318;font-weight:600}.mid{color:#9a6700;font-weight:600}.n{text-align:right}
ul{margin:0;padding-left:18px}li{margin:1px 0}"""
def page(title, sub, head, rows, foot, widths=None, raw=()):
    th = "".join(f"<th>{e(h)}</th>" for h in head)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(f"<td>{c if i in raw else e(str(c))}</td>" for i, c in enumerate(r)) + "</tr>"
    cg = "".join(f"<col style='width:{w}%'>" for w in widths) if widths else ""
    return f"<!doctype html><meta charset=utf-8><style>{CSS}</style><div class=w><h1>{e(title)}</h1><div class=sub>{e(sub)}</div><table><colgroup>{cg}</colgroup><tr>{th}</tr>{body}</table><div class=f>{e(foot)}</div></div><script>document.title=document.querySelector('.w').offsetHeight</script>"
def shot(name, doc):
    f = TMP / (name + ".html"); f.write_text(doc, encoding="utf-8")
    base = [EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", f"--user-data-dir={TMP / 'prof'}"]
    d = subprocess.run(base + ["--window-size=1464,3000", "--dump-dom", f.as_uri()], capture_output=True, text=True, encoding="utf-8").stdout
    h = int(re.search(r"<title>(\d+)</title>", d).group(1)) + 4
    png = OUT / (name + ".png")
    subprocess.run(base + [f"--window-size=1464,{h}", "--force-device-scale-factor=2", f"--screenshot={png}", f.as_uri()], capture_output=True)
    print(name, h, png.exists(), png.stat().st_size if png.exists() else 0)
FOOT = "Run 34 · FSCR + Claude test, Sourcing and Supplier Management (SCM 25) · ETIA-TEST · 2026-11-17 · Source: "
# 1 coverage (copied from Run 32, not redone)
want = ["Suppliers [Sourcing and Supplier Management]", "Sourcing [Sourcing and Supplier Management]", "Supplier Qualification [Sourcing and Supplier Management]",
        "Supplier Portal [Sourcing and Supplier Management]", "TAG Sourcing and Supplier Management"]
sel = [next(a for a in areas if a["group"] == w) for w in want]
rows = [(a["group"].replace(" [Sourcing and Supplier Management]", "").replace("TAG ", "Row total: "), a["tasks"], a["a_skill_and_route"], a["b_route_no_skill"], a["c_neither"], a["missing_N_of_total"]) for a in sel]
shot("01_coverage", page("Sourcing and Supplier Management: FSCR coverage (from Run 32)",
     "a = skill or guide · b = CSV route, no skill · c = neither · Missing = no skill · areas overlap, so area rows add up to more than the row total",
     ["Area", "Tasks", "a: skill/guide", "b: route only", "c: neither", "Missing (N/total)"], rows, FOOT + "_fscr_run_32_procurement_coverage/area_counts.csv (Run 32)", [40, 10, 14, 14, 10, 12]))
# 2 plan
ac = PS["area_check"]
rows = [("Tasks planned", PS["tasks"]), ("Supplier setup before sourcing and qualification", "Yes: the 34 Procurement supplier tasks are #1–36; sourcing starts at #41"),
        ("Oracle area order Portal → Sourcing → Qualification", "Yes" if ac["portal_before_sourcing"] and ac["sourcing_before_qualification"] else "No"),
        ("Oracle dependency links checked (URL + quote)", PS["oracle_pairs_sourced"]),
        ("Links the plan respects", f"{PS['oracle_pairs_respected']} of {PS['oracle_pairs_sourced']} ({round(100*PS['oracle_pairs_respected']/PS['oracle_pairs_sourced'])}%)"),
        ("Links FSCR's own skills state", f"{PS['oracle_pairs_stated_by_fscr_skills']} of {PS['oracle_pairs_sourced']}"),
        ("Links left 'unverified' (not in the %)", f"{PS['unverified']} (plan order fits {PS['unverified_but_plan_respects']})"),
        ("Run Book order vs the same links", f"{RS['respected_in_oracle_runbook']} of {RS['links_checked']} (Oracle groups steps by area)"),
        ("Run Book steps", f"{RS['steps']}: {RS['with_route']} with a route, {RS['manual']} manual, {RS['with_prerequisite']} prerequisites")]
shot("02_plan_result", page("Plan result: FSCR order vs Oracle-sourced links", "FSCR task-dependency-resolver method · release catalog order, Procurement offering first",
     ["Measure", "Result"], rows, FOOT + "_fscr_run_34_sourcing_supplier_test/oracle_links.csv, plan.csv, runbook/runbook_summary.json", [40, 60]))
# 3 six tasks
cls = {"Done": "ok", "Done with a fix": "ok", "Not done": "bad"}
rows = [(i + 1, s["task"], s["area"], s["group"], f"<span class={cls[s['result']]}>{e(s['result'])}</span>", s["note"]) for i, s in enumerate(SIX)]
shot("03_six_task_table", page("Six tasks on ETIA-TEST (FSCRT_ records only)", "Route: Data Loader (FSM CSV) + Task Hook · every record read back",
     ["#", "Task", "Area", "Group", "Result", "Record or reason"], rows, FOOT + "_fscr_run_34_sourcing_supplier_test/scripts/six_tasks.json, evidence/", [3, 19, 12, 9, 10, 47], raw=(4,)))
# 4 tracker
rows = [(k, "<ul>" + "".join(f"<li>{e(x)}</li>" for x in v) + "</ul>") for k, v in T.items()]
shot("04_tracker_row_values", page("Tracker row: Sourcing and Supplier Management (SCM 25)", "Values ready to paste (same as RESULT.md)", ["Column", "Value"], rows,
     FOOT + "_fscr_run_34_sourcing_supplier_test/scripts/tracker.json, RESULT.md", [22, 78], raw=(1,)))
