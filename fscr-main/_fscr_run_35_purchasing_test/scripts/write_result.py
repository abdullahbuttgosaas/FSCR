"""Run 35: write RESULT.md from tracker.json + six_tasks.json + plan/runbook summaries (same source as the images)."""
import json, pathlib
RUN = pathlib.Path(__file__).resolve().parents[1]
T = json.load(open(RUN / "scripts/tracker.json", encoding="utf-8")); SIX = json.load(open(RUN / "scripts/six_tasks.json", encoding="utf-8"))
PS = json.load(open(RUN / "evidence/plan_summary.json")); RS = json.load(open(RUN / "runbook/runbook_summary.json"))
st, fin = (RUN / "start_time.txt").read_text().strip(), (RUN / "finish_time.txt").read_text().strip()
mins = (int(fin[11:13]) * 60 + int(fin[14:16])) - (int(st[11:13]) * 60 + int(st[14:16]))
assert PS["missing"] == T["Missing (N/total)"][0]
L = ["Verdict: **Mostly**. FSCR + Claude planned all 16 tasks, built the Run Book first try and loaded 3 of 5 loadable tasks; one sourced link is out of order.", "",
     "| # | Task | Group | Result | Record / reason |", "|---|---|---|---|---|"]
L += [f"| {i} | {s['task']} | {s['group']} | **{s['result']}** | {s['short']} |" for i, s in enumerate(SIX, 1)]
L += ["",
      f"**Plan:** (a) {PS['a_respected']} of {PS['a_sourced_links']} sourced links in order; "
      f"(b) {PS['b_unverified_out_of_order']} of {PS['b_unverified']} unverified out of order; (c) skills name {PS['c_fscr_skill_prereqs']} in-row prerequisites, "
      f"{PS['c_out_of_order']} out of order. Missing 10/16 confirmed from CSV.",
      "**Score reasons:** Plan 3: right tasks, some links missed. Runbook 3: usable after edits. Execution 3: one fix, two gaps. Fit Medium. Messages (no Oracle CSV/API) not counted.", "",
      "**Tracker row (paste)**"]
for k, v in T.items():
    L.append(f"- **{k}:** " + "; ".join(v))
L += ["", "| Start | Finish | Minutes |", "|---|---|---:|", f"| {st} | {fin} | {mins} |", "",
      "Created: Run Book, FSCRT_R35_HC, FSCRT_R35_UN, FSCRT_R35_EPP_LKP; no BU. Nothing existing changed."]
(RUN / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
import re
print(len(re.findall(r"[A-Za-z0-9][\w./'+-]*", " ".join(L))), "words (letters/digits only)")
