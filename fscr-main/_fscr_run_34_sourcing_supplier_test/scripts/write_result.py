"""Run 34: write RESULT.md from tracker.json + six_tasks.json (same source as the images)."""
import json, pathlib
RUN = pathlib.Path(__file__).resolve().parents[1]
T = json.load(open(RUN / "scripts/tracker.json", encoding="utf-8")); SIX = json.load(open(RUN / "scripts/six_tasks.json", encoding="utf-8"))
st, fin = (RUN / "start_time.txt").read_text().strip(), (RUN / "finish_time.txt").read_text().strip()
mins = (int(fin[11:13]) * 60 + int(fin[14:16])) - (int(st[11:13]) * 60 + int(st[14:16]))
L = ["Verdict: **Mostly**. FSCR + Claude planned 91 tasks in the right order and loaded 3 of 4 loadable tasks; the Run Book needs prerequisites.", "",
     "| # | Task | Group | Result | Record / reason |", "|---|---|---|---|---|"]
SHORT = ["FSCRT_R34_CF read back. Fix: FSM CSV (skill's REST object not in Data Loader).",
         "Oracle CSV needs an internal AgencyId; 2 tries, 0 created. CSV limit + FSCR gap (Oracle REST create not in Data Loader).",
         "FSCRT_R34_STYLE read back via export. Fix: Run Book bound by hand.",
         "FSCRT_R34_VS + 2 values read back. Fix: Oracle rejected INDEPENDENT; resent as INDEP.",
         "Oracle has no CSV or API (Security Console; name must be SUPPLIER_USER).",
         "Oracle has no CSV or create API (REST read-only)."]
L += [f"| {i} | {s['task']} | {s['group']} | **{s['result']}** | {SHORT[i-1]} |" for i, s in enumerate(SIX, 1)]
L += ["", "**Plan:** 14 links checked (`oracle_links.csv`), 14 respected, FSCR states 1, 11 unverified. Run 33 links: none apply.",
            "**Run Book fixes:** create 1 failed on DNS (nothing in Oracle; state reset); create 2 timed out, found later, bound by hand.", "",
      "**Tracker row (paste)**"]
for k, v in T.items():
    L.append(f"- **{k}:** " + ("; ".join(v)))
L += ["", 
      f"| Start | Finish | Minutes |", "|---|---|---:|", f"| {st} | {fin} | {mins} |", "",
      "Created: Run Book, FSCRT_R34_CF, FSCRT_R34_STYLE, FSCRT_R34_VS. Nothing existing changed. Screen-only tasks not counted against FSCR."]
(RUN / "RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(len(" ".join(L).split()), "words")
