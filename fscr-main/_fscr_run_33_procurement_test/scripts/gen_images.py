"""Run 33 step 5: clear PNG table images at 2x (Edge headless, device scale factor 2). Numbers are read from the run's own files."""
import csv, json, html, subprocess, re, sys, pathlib
RUN = pathlib.Path(__file__).resolve().parents[1]; ROOT = RUN.parent
OUT = ROOT / "_fscr_evidence_pack" / "procurement"; OUT.mkdir(parents=True, exist_ok=True)
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
FOOT = "Run 33 · FSCR + Claude test, Procurement · ETIA-TEST · 2026-11-17 · Source: "
# 1 coverage
sel = [a for a in areas if a["group"].startswith(("TAG ", "ROW ", "ALL "))]
rows = [(a["group"].replace("TAG ", "").replace("ROW ", ""), a["tasks"], a["a_skill_and_route"], a["b_route_no_skill"], a["c_neither"], a["missing_N_of_total"]) for a in sel]
shot("01_procurement_coverage", page("Procurement coverage in FSCR (Run 32)", "Level a = skill or guide · b = CSV route, no skill · c = neither · Missing = tasks with no skill",
     ["Group", "Tasks", "a: skill/guide", "b: route only", "c: neither", "Missing (N/total)"], rows, FOOT + "_fscr_run_32_procurement_coverage/area_counts.csv", [40, 10, 14, 14, 10, 12]))
# 2 plan
NM = {r["task_code"]: r["task_name"] for r in csv.DictReader(open(RUN / "plan.csv", encoding="utf-8"))}
viol = [f"{NM[a]} (#{p}) before {NM[b]} (#{q})" for a, p, b, q in PS["violations"]]
rows = [("Tasks planned (Procurement + Shared)", PS["tasks"]), ("Oracle dependency links read and sourced", f"{PS['oracle_pairs_sourced']} (each with URL + quote in oracle_links.csv)"),
        ("Links the plan respects", f"{PS['oracle_pairs_respected']} of {PS['oracle_pairs_sourced']} ({round(100*PS['oracle_pairs_respected']/PS['oracle_pairs_sourced'])}%)"),
        ("…only links an Oracle page states outright", f"{PS['stated_only_respected']} of {PS['stated_only_pairs']} ({round(100*PS['stated_only_respected']/PS['stated_only_pairs'])}%)"),
        ("Links FSCR's own skills state", f"{PS['oracle_pairs_stated_by_fscr_skills']} of {PS['oracle_pairs_sourced']}"),
        ("Links left as 'unverified' (not in the %)", PS["unverified"]), ("Links the plan gets wrong", "; ".join(viol))]
shot("02_plan_result", page("Plan result: FSCR order vs Oracle-sourced links", "FSCR task-dependency-resolver method · order from the release catalog, Procurement offering", ["Measure", "Result"], rows,
     FOOT + "oracle_links.csv, plan.csv", [38, 62]))
# 3 runbook
rows = [("Run Book name in ETIA-TEST", "FSCRT_R33 Procurement (created; the create call timed out, found afterwards)"), ("Steps", RS["steps"]),
        ("Steps with a route (Data Loader)", RS["with_route"]), ("Steps that say manual", f"{RS['manual']} (25 of them have a CSV route in the catalog)"),
        ("Steps with a prerequisite", RS["with_prerequisite"]), ("Sourced links respected, runbook order", f"{RS['respected_in_oracle_runbook']} of {RS['links_checked']} (same 5 misses as the plan)"),
        ("Runbook order same as plan?", "No: Oracle groups steps by area, so Foundation is split in two"), ("Needed a hand fix", "Yes: bind the project to the Run Book after the timeout")]
shot("03_runbook_result", page("Runbook result", "FSCR Run Book generated from the 60-task plan", ["Measure", "Result"], rows, FOOT + "runbook/runbook_step_check.csv, runbook/runbook_summary.json", [38, 62]))
# 4 six tasks
cls = {"Done with a fix": "ok", "Not done": "bad"}
rows = [(i + 1, s["task"], s["group"], f"<span class={cls[s['result']]}>{e(s['result'])}</span>", s["note"]) for i, s in enumerate(SIX)]
shot("04_six_task_table", page("Six tasks done on ETIA-TEST (FSCRT_ records only)", "Route: Data Loader (FSM) + Task Hook · every record read back", ["#", "Task", "Group", "Result", "Record or reason"], rows,
     FOOT + "_fscr_run_33_procurement_test/RESULT.md, evidence/", [3, 22, 11, 11, 53], raw=(3,)))
# 5 tracker
rows = [(k, "<ul>" + "".join(f"<li>{e(x)}</li>" for x in v) + "</ul>") for k, v in T.items()]
shot("05_tracker_row_values", page("Tracker row: Procurement (SCM 24)", "Values ready to paste", ["Column", "Value"], rows, FOOT + "_fscr_run_33_procurement_test/RESULT.md", [20, 80], raw=(1,)))
