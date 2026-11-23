"""The "Run summary" of a finished run: only numbers the page already records, never guessed.

  python page/run_summary.py <run id>        # read-only: the summary of a run from the logs

Sources (all in page/_work/): server.log (one line per event, with its time: a run queued,
"customer 2 of 3: <name>", "<run>_2 done / stopped", "repair attempt 1: cost $0.7819", the
upload line "checked in 45 s" since 2026-10-23), logs/<run>.log (the folder's own output;
"== <name>" names the customer of an older single run) and logs/<run>.repair.log (one
"result" record per repair attempt, with its tokens and cost). A run still in the page's
memory adds what each customer's result said (created, failed, saved or not).

summary(run id) returns a plain dictionary of numbers and short texts, the same thing a
database could store later; lines(summary) turns it into the plain sentences the page shows.
To add a number: add it to the dictionary in summary() (from a log line the page writes;
add such a log line in server.py if it doesn't exist yet), then a sentence in lines().
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "_work"
SERVER_LOG = WORK / "server.log"
LOGS = WORK / "logs"
LINE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})  (.*)$")
FAILED_SHEET_FILE = re.compile(r"^Failed (customers|order types|rows)")   # the failed-only sheet's names


def _when(text):
    return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")


def _read_log(path=SERVER_LOG):
    out = []
    if path.exists():
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = LINE.match(raw)
            if m:
                out.append((_when(m.group(1)), m.group(2)))
    return out


def _repair_records(run_id, logs=LOGS):
    """Tokens and cost of each repair attempt of one run (its .repair.log), in order."""
    f = logs / f"{run_id}.repair.log"
    out = []
    if not f.exists():
        return out
    for raw in f.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            j = json.loads(raw)
        except ValueError:
            continue
        if j.get("type") != "result":
            continue
        u = j.get("usage") or {}
        new = (u.get("input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0)
        reread, output = u.get("cache_read_input_tokens") or 0, u.get("output_tokens") or 0
        out.append({"tokens_total": new + reread + output, "tokens_new_input": new,
                    "tokens_reread": reread, "tokens_output": output,
                    "cost_usd": j.get("total_cost_usd")} if u else {"cost_usd": j.get("total_cost_usd")})
    return out


def _saved_from_text(text):
    """What a failed customer's plain result says about saving (Customers' wording)."""
    m = re.search(r"was saved in Oracle \(Registry ID (\d+)\)|is in Oracle with Registry ID (\d+)", text or "")
    if m:
        return "yes", m.group(1) or m.group(2)
    m = re.search(r"may have been saved in Oracle \(Registry ID (\d+)", text or "")
    if m or "may have been saved" in (text or ""):
        return "maybe", m.group(1) if m else None
    if re.search(r"Nothing was saved", text or ""):
        return "no", None
    return None, None


def summary(run_id, job=None, log_path=None, logs=None):
    """The summary of one run as a plain dictionary (numbers, names, times as text). `job` is
    the run as the page keeps it in memory, when it is still there. Missing = None."""
    log_path, logs = log_path or SERVER_LOG, logs or LOGS
    lines = _read_log(log_path)
    mine = [(t, m) for t, m in lines if re.match(rf"job {re.escape(run_id)}(_\d+[pr]?)?[ :]", m)]   # p: proposal, r: batch repair
    if not mine:
        return None
    queued = next(((t, m) for t, m in mine if m.startswith(f"job {run_id} queued")), mine[0])
    q_index = lines.index(queued)
    # the upload this run came from: named on the queued line since 2026-10-23, else the last
    # checked upload before it
    up_id = re.search(r"\(upload (\w+)\)", queued[1])
    ups = [(t, m) for t, m in lines[:q_index] if m.startswith("upload ") and ": " in m]
    if up_id:
        ups = [(t, m) for t, m in ups if m.startswith(f"upload {up_id.group(1)} ")]
    upload = ups[-1] if ups else None
    up_file = re.search(r"^upload \w+ \((.*?)\):", upload[1]).group(1) if upload else None
    check = re.search(r"checked in (\d+) s", upload[1]) if upload else None

    records = {}
    for t, m in mine:
        s = re.match(rf"job {re.escape(run_id)}: (\w[\w ]*?) (\d+) of (\d+): (.+)$", m)
        if s:      # "customer 2 of 3: <name>", "order type 1 of 2: <name>" (several words since 2026-10-25)
            records[int(s.group(2))] = {"n": int(s.group(2)), "name": s.group(4), "started": t, "ended": None,
                                        "state": None, "saved": None, "registry_id": None, "what": s.group(1)}
            continue
        e = re.match(rf"job {re.escape(run_id)}_(\d+) (done|stopped \((\w+)\)): (.*)$", m)
        if e and int(e.group(1)) in records:
            r = records[int(e.group(1))]
            r["ended"], r["state"] = t, "created" if e.group(2) == "done" else "failed"
            if r["state"] == "created" and re.search(r"already exists in Oracle, so nothing was changed|"
                                                      r"is already in Oracle with .* so nothing was changed", e.group(4)):
                r["state"] = "skipped"
            if r["state"] == "failed":
                r["saved"], r["registry_id"] = _saved_from_text(e.group(4))
            continue
        f = re.match(rf"job {re.escape(run_id)}: (.+) (done|failed)$", m)
        if f:
            r = next((r for r in records.values() if r["name"] == f.group(1)), None)
            if r:
                r["ended"] = r["ended"] or t
                r["state"] = r["state"] or ("created" if f.group(2) == "done" else "failed")
    if not records:                                   # an older single run (before sheets)
        end = mine[-1]
        name = None
        runlog = logs / f"{run_id}.log"
        if runlog.exists():
            hit = re.search(r"^== (.+?)(?: \(person\))?$", runlog.read_text(encoding="utf-8", errors="replace"), re.M)
            name = hit.group(1) if hit else None
        done = next(((t, m) for t, m in mine if m.startswith(f"job {run_id} done")), None)
        stop = next(((t, m) for t, m in mine if m.startswith(f"job {run_id} stopped")), None)
        state = "created" if done else ("failed" if stop else None)
        saved, rid = _saved_from_text(stop[1]) if stop else (None, None)
        records[1] = {"n": 1, "name": name, "started": queued[0], "ended": end[0], "state": state,
                      "saved": saved, "registry_id": rid}
    if job and job.get("items"):                      # what the page still knows about each one
        for it in job["items"]:
            if it["n"] not in records and it.get("state") == "failed":
                # never sent (Price Lists: its business unit failed or was skipped, 2026-10-26): no log line
                records[it["n"]] = {"n": it["n"], "name": it.get("name"), "started": None, "ended": None, "state": None,
                                    "saved": None, "registry_id": None, "what": it.get("what")}
            r = records.get(it["n"])
            if r and it.get("state") in ("done", "failed"):
                r["state"] = "created" if it["state"] == "done" else "failed"
                if it["state"] == "done" and (it.get("result") or {}).get("skipped"):
                    r["state"] = "skipped"            # already in Oracle, nothing changed (Order Types)
                r["what"] = it.get("what") or r.get("what")
                if it["state"] == "failed":
                    d = ((it.get("result") or {}).get("error") or {}).get("detail")
                    if isinstance(d, dict) and d.get("saved"):
                        r["saved"], r["registry_id"] = d["saved"], d.get("registry_id")

    # questions (Business Units, 2026-10-26): a value Oracle refused, what the user decided
    questions = {}
    for t, m in mine:
        q = re.match(rf"job {re.escape(run_id)}: question (\d+) \((.*?)\)(:| answered:| skipped| tried again)(.*)$", m)
        if not q:
            continue
        n, name, kind, rest = int(q.group(1)), q.group(2), q.group(3), q.group(4).strip()
        e = questions.setdefault(n, {"n": n, "name": name, "label": None, "value": None, "state": "open",
                                     "answer": None, "asked": t.strftime("%Y-%m-%d %H:%M:%S")})
        if kind == ":":
            a = re.match(r"(.+?) '(.*)' refused: (.*?); suggested: (.*)$", rest)
            if a:
                e.update(label=a.group(1), value=a.group(2), reason=a.group(3), state="open")
            elif "not accepted" in rest:
                e["state"] = "open"
        elif kind == " answered:":
            a = re.match(r"(.+?) = (.*?); (trying again|done)$", rest)
            if a:
                e.update(label=a.group(1), answer=a.group(2), state="answered" if a.group(3) == "done" else "retrying")
        elif kind == " skipped":
            e["state"] = "skipped"
        elif kind == " tried again":
            e["state"] = "closed"
    if job and job.get("items"):                      # the run in memory knows the latest state
        for it in job["items"]:
            jq = it.get("question")
            if jq:
                e = questions.setdefault(it["n"], {"n": it["n"], "name": it["name"], "asked": None})
                e.update(label=jq.get("label"), value=jq.get("value"), state=jq.get("state"), answer=jq.get("answer"),
                         reason=jq.get("reason"))

    repairs = []
    for t, m in mine:
        a = re.match(rf"job ({re.escape(run_id)}(?:_(\d+)r?)?) repair attempt (\d+): cost \$([\d.]+)", m)
        if a:
            rec = records.get(int(a.group(2))) if a.group(2) else records.get(1)
            repairs.append({"run": a.group(1), "attempt": int(a.group(3)), "record": rec and rec["name"],
                            "cost_usd": float(a.group(4))})
            continue
        b = re.match(rf"job ({re.escape(run_id)}_(\d+)p) proposal: cost \$([\d.]+)", m)
        if b:                                         # Claude's proposal for a refusal no rule knew (2026-10-26)
            rec = records.get(int(b.group(2)))
            repairs.append({"run": b.group(1), "attempt": 1, "record": rec and rec["name"], "kind": "proposal",
                            "cost_usd": float(b.group(3))})
    by_run = {}
    for rp in repairs:
        by_run.setdefault(rp["run"], _repair_records(rp["run"], logs))
        recs = by_run[rp["run"]]
        if rp["attempt"] <= len(recs):
            got = recs[rp["attempt"] - 1]
            rp.update({k: v for k, v in got.items() if k != "cost_usd"})
            if got.get("cost_usd") is not None:
                rp["cost_usd"] = round(got["cost_usd"], 4)

    rs = sorted(records.values(), key=lambda r: r["n"])
    for r in rs:
        r["seconds"] = int((r["ended"] - r["started"]).total_seconds()) if r["ended"] else None
    starts = [r["started"] for r in rs if r["started"]]
    ends = [r["ended"] for r in rs if r["ended"]]
    toks = [rp.get("tokens_total") for rp in repairs]
    iso = lambda d: d.strftime("%Y-%m-%d %H:%M:%S") if d else None
    return {
        "run": run_id,
        "started": iso(min(starts)) if starts else None,
        "ended": iso(max(ends)) if ends else None,
        "seconds": int((max(ends) - min(starts)).total_seconds()) if starts and ends else None,
        "check_seconds": int(check.group(1)) if check else None,
        "upload_file": up_file,
        "from_failed_sheet": bool(up_file and FAILED_SHEET_FILE.match(up_file)),
        "records": [{"n": r["n"], "name": r["name"], "what": r.get("what"), "state": r["state"], "saved": r["saved"],
                     "registry_id": r["registry_id"], "started": iso(r["started"]), "ended": iso(r["ended"]),
                     "seconds": r["seconds"]} for r in rs],
        "created": sum(1 for r in rs if r["state"] == "created"),
        "skipped": sum(1 for r in rs if r["state"] == "skipped"),
        "failed": sum(1 for r in rs if r["state"] == "failed"),
        "saved_not_checked": sum(1 for r in rs if r["state"] == "failed" and r["saved"] in ("yes", "maybe")),
        "repairs": repairs,
        "repair_tokens": sum(toks) if repairs and all(x is not None for x in toks) else (None if repairs else 0),
        "repair_cost_usd": round(sum(rp["cost_usd"] for rp in repairs), 4),
        "questions": [questions[k] for k in sorted(questions)],
    }


# ---------------------------------------------------------------- plain words

def duration(sec):
    if sec is None:
        return None
    h, rest = divmod(int(sec), 3600)
    m, s = divmod(rest, 60)
    return " ".join(x for x in (f"{h} h" if h else "", f"{m} min" if m or h else "", f"{s} s") if x)


def money(usd):
    return f"${usd:,.2f}"


def tokens(n):
    return f"{n:,} tokens"


def lines(s):
    """The summary as plain sections for the page: [{"heading", "lines": [...]}]."""
    clock = lambda iso: iso[11:16] if iso else "?"
    out = []
    t = []
    if s["seconds"] is not None:
        t.append(f"The whole run took {duration(s['seconds'])} ({clock(s['started'])} to {clock(s['ended'])}).")
    for r in s["records"]:
        name = r["name"] or f"{(r.get('what') or 'customer').capitalize()} {r['n']}"
        t.append(f"{name}: {duration(r['seconds'])} ({clock(r['started'])} to {clock(r['ended'])})."
                 if r["seconds"] is not None else f"{name}: not sent (what it waited for wasn't ready)."
                 if r["started"] is None else f"{name}: started {clock(r['started'])}, end not recorded.")
    for word in ("payment term", "lookup type", "business unit", "price list"):   # one call per module
        shared = [r for r in s["records"] if r.get("what") == word]
        if len(shared) > 1 and len({(r["started"], r["ended"]) for r in shared}) == 1:
            t.append(f"The {len(shared)} {word}s were created together in one go, so they share one time.")
    if s["check_seconds"] is not None:
        t.append(f"Checking the sheet before Create took {duration(s['check_seconds'])}.")
    out.append({"heading": "Time", "lines": t})
    n = len(s["records"])
    res = [f"Created: {s['created']} of {n}.", f"Failed: {s['failed']}."]
    if s.get("skipped"):
        res.insert(1, f"Already in Oracle, skipped (nothing changed): {s['skipped']}.")
    if s["saved_not_checked"]:
        saved = [r for r in s["records"] if r["state"] == "failed" and r["saved"] in ("yes", "maybe")]
        res.append(f"Saved but not fully checked: {s['saved_not_checked']} ("
                   + ", ".join(f"{r['name']}" + (f", Registry ID {r['registry_id']}" if r["registry_id"] else "")
                               for r in saved) + ").")
    else:
        res.append("Saved but not fully checked: 0.")
    out.append({"heading": "Results", "lines": res})
    rep = []
    if not s["repairs"]:
        rep.append("No repairs. Claude was not used: 0 tokens, $0.")
    else:
        for rp in s["repairs"]:
            who = rp["record"] or "the customer"
            what = "Claude's proposal" if rp.get("kind") == "proposal" else f"Repair {rp['attempt']}"
            if rp.get("tokens_total") is not None:
                rep.append(f"{what} for {who}: {tokens(rp['tokens_total'])} "
                           f"({rp['tokens_new_input']:,} new, {rp['tokens_reread']:,} re-read, "
                           f"{rp['tokens_output']:,} written), {money(rp['cost_usd'])}.")
            else:
                rep.append(f"{what} for {who}: {money(rp['cost_usd'])} (tokens not recorded).")
        total = f"{tokens(s['repair_tokens'])}, " if s["repair_tokens"] is not None else ""
        rep.append(f"Total for repairs: {total}{money(s['repair_cost_usd'])}.")
    out.append({"heading": "Repairs", "lines": rep})
    qs = s.get("questions") or []
    if qs:                                            # Business Units: values Oracle refused, and the answers
        say = {"open": "waiting for your decision", "checking": "your answer is being checked",
               "retrying": "your answer is being tried", "skipped": "skipped by you (not created)",
               "closed": "tried again with your answer, still not created"}
        ql = []
        for q in qs:
            what = f"{q['name']}: {q.get('label') or 'a value'} '{q.get('value')}' was refused by Oracle"
            if q.get("state") == "answered":
                ql.append(f"{what}; you chose '{q.get('answer')}' and it was created with it.")
            else:
                ql.append(f"{what}; {say.get(q.get('state'), q.get('state'))}"
                          + (f" (last answer '{q['answer']}')" if q.get("answer") and q.get("state") != "skipped" else "") + ".")
        waiting = sum(1 for q in qs if q.get("state") in ("open", "checking", "retrying"))
        if waiting:
            ql.append(f"Still waiting for a decision: {waiting}. Everything else of this run is already done.")
        out.append({"heading": "Decisions", "lines": ql})
    words = list(dict.fromkeys(r.get("what") or "customer" for r in s["records"])) or ["customer"]
    plural = " and ".join(f"{w}s" for w in words)
    if s["from_failed_sheet"]:
        out.append({"heading": None, "lines": [f"This run was the upload of a sheet with only the failed {plural} "
                                               "of an earlier run."]})
    out.append({"heading": None, "lines": [f"Creating {'a customer' if words == ['customer'] else plural} uses no "
                                           "Claude tokens. Claude is only used when a run fails and an automatic "
                                           "repair starts."]})
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    s = summary(sys.argv[1])
    if s is None:
        print(f"No run {sys.argv[1]} in the page's log.")
        return
    print(json.dumps(s, indent=1))
    for sec in lines(s):
        if sec["heading"]:
            print(f"\n{sec['heading']}")
        for ln in sec["lines"]:
            print(f"  {ln}")


if __name__ == "__main__":
    main()
