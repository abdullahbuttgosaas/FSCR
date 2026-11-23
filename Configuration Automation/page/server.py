"""The page: a small local web server with one thing on it, the upload of an Excel sheet.

  python page/server.py            # start on http://127.0.0.1:8765
  python page/server.py --open     # same, and open it in the default browser
  python page/server.py --port 8800
  python page/server.py --test-mode   # adds a "force one failure" switch for testing repair

Standard library only (plus openpyxl in page/workbook.py). Bound to 127.0.0.1 (this PC
only). An uploaded workbook is read and checked by page/workbook.py from the sheet
definition (page/sheet_definition.json); the registry (page/sheet_registry.json) says which
folder runs which tabs. The page talks to each folder's script only through the Page
interface (--spec, --options FIELD, --run JSON) and never changes a configuration folder or
common/ itself. Runs are queued: one at a time. There are no folder cards and no forms.

A run that fails for a reason the user can't fix is handed to Claude's command-line tool
(claude -p) for an automatic repair inside that one folder (see repair()). Every repair's
cost is written to page/_work/server.log.

Never reads, shows or types credentials: the only lines read from .env are ORACLE_ENV and
ALLOW_PROD; the setup checks run common/check_setup.py, which prints key names only.
"""
import argparse
import http.server
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import uuid
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STATIC = HERE / "static"
WORK = HERE / "_work"
CACHE = WORK / "cache"
LOGS = WORK / "logs"
SERVER_LOG = WORK / "server.log"
PY = sys.executable
PROD_LABELS = ("prod", "production")

# Automatic repair limits (one failed run)
REPAIR_ATTEMPTS = 5
REPAIR_MINUTES = 20
REPAIR_BUDGET_USD = 2.0            # spending cap per repair attempt (claude --max-budget-usd)
ASK_USER = {"INVALID_REQUEST", "NOT_IN_ORACLE"}          # the user changes a value
STOP_PLAIN = {"NO_PERMISSION", "PRODUCTION_REFUSED", "SETUP_NEEDED"}
TEST_MODE = {"on": False}

ENV_CHILD = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
LOCK = threading.Lock()
sys.path.insert(0, str(ROOT))
from common import page as contract  # noqa: E402  (the Page interface contract; standard library only)
from common import claude_tool  # noqa: E402  (finds / installs Claude's tool per user; standard library only)
import workbook  # noqa: E402  (page/workbook.py: the upload sheet; needs openpyxl only when used)
import run_summary  # noqa: E402  (page/run_summary.py: the "Run summary" of a finished run, from the logs)
CLAUDE_SKIP = WORK / "claude_skipped"   # the user chose "Continue without automatic fixes" on this PC


def log(msg):
    WORK.mkdir(parents=True, exist_ok=True)
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(line, flush=True)
    with SERVER_LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_py(args, timeout, cwd=ROOT):
    """Run a Python script of the project; returns (exit code, stdout, stderr)."""
    try:
        p = subprocess.run([PY] + args, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout, env=ENV_CHILD)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired as e:
        return -1, e.stdout or "", (e.stderr or "") + f"\n(timed out after {timeout}s)"


# ---------------------------------------------------------------- environment label

def env_label():
    """ORACLE_ENV and ALLOW_PROD only: from the environment, else from those two .env lines."""
    vals = {k: os.environ.get(k, "") for k in ("ORACLE_ENV", "ALLOW_PROD")}
    env_file = ROOT / ".env"
    if env_file.exists() and not all(vals.values()):
        for line in env_file.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            m = re.match(r"\s*(ORACLE_ENV|ALLOW_PROD)\s*=\s*(.*?)\s*$", line)
            if m and not vals[m.group(1)]:
                vals[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    label = vals["ORACLE_ENV"]
    prod = label.lower() in PROD_LABELS
    return {"name": label, "production": prod,
            "allowed": (not prod) or vals["ALLOW_PROD"].lower() == "yes"}


# ---------------------------------------------------------------- configuration folders

FOLDERS = {}       # name -> {"name", "script", "spec" | None, "error"}


def index_folders():
    """Folder names from the root CLAUDE.md Configuration index (first column)."""
    text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    part = text.split("## Configuration index", 1)[1].split("\n## ", 1)[0]
    names = []
    for line in part.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not line.strip().startswith("|") or cells[0] in ("Folder", "") \
                or set(cells[0]) <= set("-: "):
            continue
        if (ROOT / cells[0]).is_dir():
            names.append(cells[0])
    return names


def folder_script(name):
    for s in ("browser_flow.py", "run.py"):
        if (ROOT / name / s).exists():
            return f"{name}/{s}"
    return None


def sheet_folders():
    """Folders the upload sheet runs (page/sheet_registry.json), in the Configuration index."""
    wanted = {g["folder"] for g in workbook.load_registry()["groups"]}
    return [n for n in index_folders() if n in wanted]


def load_folders():
    found = {}
    for name in sheet_folders():
        script = folder_script(name)
        entry = {"name": name, "script": script, "spec": None, "error": None}
        if script:
            code, out, err = run_py([script, "--spec"], 90)
            try:
                entry["spec"] = json.loads(out.strip().splitlines()[-1])
            except (ValueError, IndexError):
                entry["error"] = (err or out).strip()[-500:]
                log(f"--spec failed for {name}: {entry['error'][:200]}")
        found[name] = entry
    with LOCK:
        FOLDERS.clear()
        FOLDERS.update(found)
    log(f"folders: {', '.join(n for n, f in found.items() if f['spec']) or 'none'}")


# ---------------------------------------------------------------- Oracle's today (date rules)

TODAY = {"value": None, "at": 0}


def oracle_today(max_age=600):
    """Oracle's today (page/oracle_today.py: the date of a read-only REST answer), kept
    for 10 minutes. None when Oracle can't be reached."""
    with LOCK:
        if TODAY["value"] and time.time() - TODAY["at"] < max_age:
            return TODAY["value"]
    code, out, err = run_py(["page/oracle_today.py"], 90)
    try:
        value = json.loads(out.strip().splitlines()[-1]).get("today")
    except (ValueError, IndexError):
        value = None
    if value:
        with LOCK:
            TODAY.update(value=value, at=time.time())
    else:
        log(f"Oracle's today could not be read: {(err or out)[-200:]}")
    return value


# ---------------------------------------------------------------- pick lists

OPT_LOCKS = {}
OPT_SEM = threading.Semaphore(1)     # one list at a time: some lists open an Oracle screen (2026-10-26)
# One Oracle browser at a time on the one saved sign-in (2026-10-26): a preview's checks, an answer's check and a
# run never use Oracle side by side (three browsers at once made Oracle's busy Setup page drop clicks).
ORACLE_LOCK = threading.RLock()
CHECK_RERUNS, CHECK_RERUN_PAUSE = 2, 20     # a check that couldn't run is run again up to 2 more times, 20 s apart


def cache_file(folder, field):
    return CACHE / (re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{folder}__{field}") + ".json")


def cached_options(folder, field):
    f = cache_file(folder, field)
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            return None
    return None


def live_options(folder, field, full=False):
    """Read a list live through the folder's --options (one read per list at a time).
    full: the whole list (--options FIELD --all) of a field whose drop-down holds samples."""
    name = field + ("__all" if full else "")
    key = (folder, name)
    with LOCK:
        lock = OPT_LOCKS.setdefault(key, threading.Lock())
    with lock:
        recent = cached_options(folder, name)
        if recent and time.time() - recent.get("saved", 0) < 20:      # just read by another caller
            return recent, None
        script = FOLDERS[folder]["script"]
        with OPT_SEM:
            code, out, err = run_py([script, "--options", field] + (["--all"] if full else []), 300)
        try:
            data = json.loads(out.strip().splitlines()[-1])
        except (ValueError, IndexError):
            data = {"ok": False, "text": "Oracle didn't answer.", "error": {"detail": err[-500:]}}
        if not data.get("ok"):
            return None, data
        entry = {"values": data["values"], "read_at": data.get("read_at") or now_iso(),
                 "saved": time.time()}
        CACHE.mkdir(parents=True, exist_ok=True)
        cache_file(folder, name).write_text(json.dumps(entry), encoding="utf-8")
        return entry, None


def run_active():
    """True while a request is running or being repaired: lists are never read then."""
    with LOCK:
        return any(j["state"] in ("running", "repairing", "signing") for j in JOBS.values())


def sheet_live_fields():
    """(folder, --options field) for every sheet column that is checked against a live list."""
    reg, d = workbook.load_registry(), workbook.load_definition()
    tab_folder = {workbook.norm(t): g["folder"] for g in reg["groups"]
                  for t in list(g["record_tabs"]) + list(g["child_tabs"])}
    out = []
    for tab in d["tabs"]:
        folder = tab_folder.get(workbook.norm(tab["name"]))
        for c in tab["columns"]:
            if folder and c.get("live") and (folder, c["live"]) not in out:
                out.append((folder, c["live"]))
    return out


def warm_options():
    """Fill the list cache once at start (lists that were never read); it pauses while a
    request runs and never reads a list during one."""
    for folder, field in sheet_live_fields():
        while run_active():
            time.sleep(5)
        if folder in FOLDERS and FOLDERS[folder]["spec"] and not cached_options(folder, field):
            live_options(folder, field)


def sheet_list(folder, field, full=False):
    """The lists helper for page/workbook.py: the folder's --options, kept a while
    (samples 10 minutes, a whole list a day). Never read while a request runs."""
    f = FOLDERS.get(folder) or {}
    spec_field = contract._field(f.get("spec") or {"fields": []}, field)
    if not spec_field:
        return {"failed": "This list isn't known."}
    partial = spec_field.get("list") == "samples" and not full
    old = cached_options(folder, field + ("__all" if full else ""))
    if old and time.time() - old.get("saved", 0) < (86400 if full else 600):
        return {"values": old["values"], "partial": partial}
    if run_active() or not env_label()["allowed"]:
        return {"values": old["values"], "partial": partial} if old else \
            {"failed": "Oracle's list can't be read while a request runs."}
    entry, err = live_options(folder, field, full)
    if entry:
        return {"values": entry["values"], "partial": partial}
    if old:
        return {"values": old["values"], "partial": partial}
    return {"failed": (err or {}).get("text") or "Oracle's list couldn't be read."}


# ---------------------------------------------------------------- the upload sheet

UPLOADS = {}       # id -> {"preview", "file", "at", "job"}


def check_upload(data, file_name):
    """Read and check an uploaded workbook: the preview. Nothing is created in Oracle. The saved
    Oracle sign-in is checked first (2026-10-23): when it is missing or expired, the sheet is
    checked offline only, the sign-in window opens at once, and the checks with Oracle run
    after the sign-in; Create stays off until they are done, so a run never stops to ask."""
    uid, began = uuid.uuid4().hex[:10], time.time()
    with LOCK:
        UPLOADS[uid] = {"preview": None, "file": file_name, "at": time.time(), "job": None, "data": data}
    signin = needs_signin(offline_check(data).get("records") or [])
    if not signin:
        log(f"upload {uid}: no module of this sheet uses the browser, so the Oracle sign-in isn't checked")
    if not signin or session_valid().get("valid"):
        res = full_check(data)
    else:
        res = offline_check(data)
        res.update(ok=False, signin="waiting")
        threading.Thread(target=signin_then_check, args=(uid,), daemon=True).start()
    with LOCK:
        UPLOADS[uid]["preview"] = res
    log(f"upload {uid} ({file_name}): {'ready' if res['ok'] else 'not ready'}, "
        f"{len(res['records'])} record(s), {len(res['problems'])} problem(s), {len(res['stops'])} stop(s)"
        + (", waiting for the Oracle sign-in" if res.get("signin") else
           f", checked in {int(time.time() - began)} s"))      # read by page/run_summary.py
    return uid, res


def offline_check(data, today=None, lists=None):
    try:
        return workbook.preview(data, today, lists)
    except ImportError:
        return {"ok": False, "stops": ["A helper program for reading Excel files is missing. Restart the "
                                       "page; its setup checklist installs the helper programs."],
                "notes": [], "problems": [], "records": [], "today": today}


def signin_then_check(uid):
    """The sign-in window for an upload (at the preview, never during a run), then the full check."""
    ok = oracle_signin()
    with LOCK:
        u = UPLOADS.get(uid)
    if not u:
        return
    if not ok:
        with LOCK:
            u["preview"] = dict(u["preview"], signin="failed")
        log(f"upload {uid}: Oracle sign-in not finished")
        return
    res = full_check(u["data"])
    with LOCK:
        u["preview"] = res
    log(f"upload {uid} ({u['file']}): signed in; {'ready' if res['ok'] else 'not ready'}, "
        f"{len(res['problems'])} problem(s)")


def full_check(data):
    """Everything before Create, for every record of the sheet: the sheet, Oracle's lists, then
    the read-only checks with Oracle, one after another (2026-10-26; before: side by side): records with the same
    name (one browser visit for all), the address places (each distinct State / City / Postal Code once, answers
    kept an hour, ADDRESS_CACHE), then the folders' own checks. Holds ORACLE_LOCK (one Oracle browser at a time),
    except while a run is active (the checks then answer "another task is running", as before)."""
    if run_active():
        return _full_check(data)
    with ORACLE_LOCK:
        return _full_check(data)


def _full_check(data):
    fields = [(fo, fi) for fo, fi in sheet_live_fields() if fo in FOLDERS and FOLDERS[fo]["spec"]]
    threads = [threading.Thread(target=sheet_list, args=x, daemon=True) for x in fields]
    for t in threads:                        # the short lists, read side by side (3 at a time)
        t.start()
    today = oracle_today()
    for t in threads:
        t.join(timeout=120)
    res = offline_check(data, today, sheet_list)
    for r in res["records"]:
        if r["folder"] not in FOLDERS or not FOLDERS[r["folder"]]["spec"]:
            res["stops"].append(f"The {r['group']} part of the page isn't ready yet. Please try again in a minute.")
    if res["records"] and not res["stops"]:      # all problems at once: also when the sheet has others
        out = {"same": same_name_notes(res["records"]), "addr": address_checks(res["records"])}   # one after another
        if any(group_of(r).get("oracle_check") for r in res["records"]):     # Order Types (2026-10-25)
            out["plan"] = oracle_checks(res["records"])
        for r, note in zip(res["records"], out.get("same") or []):
            r["same_name"] = note                  # shown on the preview above the record
        for r, got in zip(res["records"], out.get("addr") or []):
            apply_address_check(res, r, got)
        for r, got in zip(res["records"], out.get("plan") or []):
            apply_oracle_check(res, r, got)
    for r in res["records"]:
        r["ok"] = not r["problems"]
    res["ok"] = bool(res["records"]) and not res["stops"] and not res["problems"]
    if not today:
        res["notes"].append("Oracle couldn't be reached to read its date; dates are checked again when you press Create.")
    return res


def group_of(rec):
    return next((g for g in workbook.load_registry()["groups"] if g["name"] == rec["group"]), {})


def needs_signin(records):
    """Whether a sheet needs the saved Oracle browser sign-in (2026-11-02): yes unless every record's module says
    "uses_browser": false in the registry (the four Receivables modules: Basic auth calls only). A sheet with no
    records keeps the old behaviour (yes)."""
    return not records or any(group_of(r).get("uses_browser", True) for r in records)


def folder_batch(folder, cmd, requests, timeout):
    """One read-only folder command for a list of requests (one browser visit): the answers in
    order, or one {"ok": False, "text"} per request when it couldn't run."""
    code, out, err = run_py([FOLDERS[folder]["script"], cmd, json.dumps(requests)], timeout)
    again = [ln.split("[ui] ", 1)[-1].strip() for ln in err.splitlines() if ": done on try " in ln]
    if again:                       # browser steps the shared retry helper had to do again (2026-10-26)
        log(f"{cmd} for {folder}: {len(again)} browser step(s) needed another try: {'; '.join(again)[:400]}")
    try:
        data = json.loads(out.strip().splitlines()[-1])
        if isinstance(data.get("results"), list) and len(data["results"]) == len(requests):
            return data["results"]
    except (ValueError, IndexError, AttributeError):
        data = None
    log(f"{cmd} for {len(requests)} record(s) failed ({code}): {err[-300:].strip()}")
    # the folder's own reason when it gave one (2026-10-26: e.g. "Oracle's Setup page did not open Create Customer
    # after 3 tries"), else "no answer" as before
    why = data.get("text") if isinstance(data, dict) and isinstance(data.get("text"), str) and data["text"] else "no answer"
    return [{"ok": False, "text": why, "oracle": True} for _ in requests]


def folder_check(folder, cmd, requests, timeout):
    """folder_batch for a preview check (2026-10-26): when the check couldn't run at all (every answer "not ok", no
    run active), it is run again up to CHECK_RERUNS more times, CHECK_RERUN_PAUSE seconds apart, before the page
    hears of it. Read-only checks only: nothing is created, so a re-run is always safe."""
    answers = folder_batch(folder, cmd, requests, timeout)
    for n in range(1, CHECK_RERUNS + 1):
        if any(a.get("ok") for a in answers) or run_active():
            break
        log(f"{cmd} for {folder} couldn't run ({answers[0].get('text')}); running it again in {CHECK_RERUN_PAUSE} s "
            f"(re-run {n}/{CHECK_RERUNS})")
        time.sleep(CHECK_RERUN_PAUSE)
        answers = folder_batch(folder, cmd, requests, timeout)
    return answers


ADDRESS_CACHE = {}          # (folder, country, state, city, postal code) -> (time, answer)
ADDRESS_KEEP = 3600


def address_checks(records):
    """Read-only: the registry's "address_check" command (Customers: --check-address) for every
    record, but each distinct country / State / City / Postal Code once, and an answer from the
    last hour is reused. One answer per record: None (no check), {"ok": False, "text"} or the
    folder's answer."""
    out, todo = [None] * len(records), {}
    for i, rec in enumerate(records):
        cmd = group_of(rec).get("address_check")
        if not cmd:
            continue
        q = rec["request"]
        key = (rec["folder"], *(workbook.flat(q.get(k)) for k in ("country", "state", "city", "postal_code")))
        hit = ADDRESS_CACHE.get(key)
        if hit and time.time() - hit[0] < ADDRESS_KEEP:
            out[i] = hit[1]
        else:
            todo.setdefault((rec["folder"], cmd), {}).setdefault(key, []).append(i)
    for (folder, cmd), combos in todo.items():
        if run_active():
            for idx in combos.values():
                for i in idx:
                    out[i] = {"ok": False, "text": "another task is running"}
            continue
        keys = list(combos)
        log(f"address check: {len(keys)} distinct place(s) for {sum(map(len, combos.values()))} record(s)")
        answers = folder_batch(folder, cmd, [records[combos[k][0]]["request"] for k in keys], 300 + 60 * len(keys))
        bad = [j for j, got in enumerate(answers) if not got.get("ok") and got.get("held")]
        if bad and group_of(records[combos[keys[0]][0]]).get("address_check_hold") and \
                not any("sign-in" in (answers[j].get("text") or "") for j in bad):
            # Customers v2: the folder already tried 3 times; one more fresh try for the rest after 20 s
            log(f"address check: {len(bad)} place(s) not checked; one more try in 20 s")
            time.sleep(20)
            again = folder_batch(folder, cmd, [records[combos[keys[j]][0]]["request"] for j in bad], 300 + 60 * len(bad))
            for j, got in zip(bad, again):
                answers[j] = got
        for k, got in zip(keys, answers):
            if got.get("ok"):
                ADDRESS_CACHE[k] = (time.time(), got)
            for i in combos[k]:
                out[i] = got
    return out


def apply_address_check(res, rec, got):
    """Problems of the address check go red on their field and on the record (Create stays off);
    places found get a note. A check that couldn't run stops the preview (it is part of
    "everything is checked")."""
    if got is None:
        return
    if not got.get("ok") and got.get("held") and group_of(rec).get("address_check_hold"):
        # Customers v2 (2026-10-26): after the folder's retries this place still couldn't be checked: the
        # customer is held with the plain reason, the rest goes on; Create checks it on the same path and a
        # refusal there asks the user (decision panel). Not a stop.
        note = ("Held: Oracle's places couldn't be confirmed just now (" + (got.get("text") or "no answer").rstrip(".")
                + "). It is checked again when it is created; if Oracle refuses it, you'll be asked.")
        rec["held"] = note
        tab = next(t for t in workbook.load_definition()["tabs"] if workbook.norm(t["name"]) == workbook.norm(rec["tab"]))
        lab = {c.get("key"): c["label"] for c in tab["columns"]}
        for key in ("city", "state", "postal_code"):
            line = next((l for l in rec["fields"] if l["label"] == lab.get(key)), None)
            if line and line.get("sheet") and not line.get("problem"):
                line["note"] = note
                break
        return
    if not got.get("ok"):
        stop = ("The address couldn't be checked with Oracle just now (" + (got.get("text") or "no answer")
                + "). Please upload the sheet again in a minute.")
        if stop not in res["stops"]:
            res["stops"].append(stop)
            res.setdefault("oracle_stops", []).append(stop)     # shown under "Oracle" (2026-10-26)
        return
    tab = next(t for t in workbook.load_definition()["tabs"] if workbook.norm(t["name"]) == workbook.norm(rec["tab"]))
    label = {c.get("key"): c["label"] for c in tab["columns"]}
    for key, text in (got.get("found") or {}).items():
        line = next((l for l in rec["fields"] if l["label"] == label.get(key)), None)
        if line and not line.get("problem"):
            line["note"] = text
    state_line = next((l for l in rec["fields"] if l["label"] == label.get("state")), None)
    for p in got.get("problems") or []:
        col = label.get(p["key"], p["key"])
        line = next((l for l in rec["fields"] if l["label"] == col), None)
        if (group_of(rec).get("address_check_hold") and p["key"] in ("city", "postal_code")
                and state_line and state_line.get("problem")):
            # Customers v2: the State is already red from the sheet check; its City / Postal Code are checked
            # within the State, so they are checked again once the State is fixed (no second red line)
            continue
        if line:
            line.update(problem=p["text"], fix=p["fix"], note=None)
        prob = {"tab": rec["tab"], "row": rec["row"], "column": col, "text": p["text"], "fix": p["fix"]}
        res["problems"].append(prob)
        rec["problems"].append(prob)


def oracle_checks(records):
    """Read-only, before Create: the registry's "oracle_check" command (Order Types: --plan) for
    the group's records, all in one call and in sheet order (the folder plans them as the run
    will make them, one after another). One answer per record, None for other groups."""
    out, todo = [None] * len(records), {}
    for i, rec in enumerate(records):
        cmd = group_of(rec).get("oracle_check")
        if cmd:
            todo.setdefault((rec["folder"], cmd), []).append(i)
    for (folder, cmd), idx in todo.items():
        if run_active():
            answers = [{"ok": False, "text": "another task is running"}] * len(idx)
        else:
            answers = folder_check(folder, cmd, [records[i]["request"] for i in idx], 300)
        for i, got in zip(idx, answers):
            out[i] = got
    return out


def apply_oracle_check(res, rec, got):
    """What the folder says a run would do, on the preview: "skipped" (already in Oracle; not an
    error, nothing is changed), problems in red on their field (Create stays off), notes on
    fields ("found", yellow) and values the automation fills in ("fills"). A check that couldn't
    run stops the preview, like the address check."""
    if got is None:
        return
    if not got.get("ok"):
        why = got.get("text") or "no answer"
        if why not in ("no answer", "another task is running"):      # the folder's real reason (2026-10-26)
            stop = (f"The {group_of(rec).get('record', 'record')}s couldn't be checked with Oracle: {why.rstrip('.')}. "
                    "Nothing was created. Please upload the sheet again.")
        else:
            stop = (f"The {group_of(rec).get('record', 'record')}s couldn't be checked with Oracle just now ("
                    + why + "). Please upload the sheet again in a minute.")
        if stop not in res["stops"]:
            res["stops"].append(stop)
            res.setdefault("oracle_stops", []).append(stop)     # the page shows these under "Oracle", not "Sheet"
        return
    # labels from the record's own tab; an entry made of code rows only (Lookup Types) uses the
    # record tab's labels ("label_tab")
    tab_name = rec.get("label_tab") or rec["tab"]
    tab = next(t for t in workbook.load_definition()["tabs"] if workbook.norm(t["name"]) == workbook.norm(tab_name))
    label = {c.get("key"): c["label"] for c in tab["columns"]}
    line_of = lambda key: next((l for l in rec["fields"] if l["label"] == label.get(key, key)), None)
    if got.get("skipped"):
        rec["skipped"] = got["skipped"]
    for key, text in (got.get("fills") or {}).items():
        line = line_of(key)
        if line and not line.get("problem"):
            line.update(oracle=text, default=False, note="Filled in by the automation")
    for key, text in (got.get("found") or {}).items():
        line = line_of(key)
        if line and not line.get("problem"):
            line["note"] = text
    for key, text in (got.get("oracle") or {}).items():   # what Oracle will get per field (Business Units)
        line = line_of(key)
        if line and not line.get("problem") and text:
            line.update(oracle=text, default=False)
    if got.get("summary"):                         # what Oracle will get, in plain words (Payment Terms)
        rec["oracle_summary"] = got["summary"]
    for p in got.get("problems") or []:
        if group_of(rec).get("plan_skips_red_fields") and (line_of(p.get("key")) or {}).get("problem"):
            continue                               # already red from the sheet check (Business Units)
        if child_problem(res, rec, p):             # a problem of one line / set row (Payment Terms)
            continue
        child_tab = {r["into"]: n for n, r in (group_of(rec).get("child_tabs") or {}).items()}.get(p["key"])
        col = label.get(p["key"]) or child_tab or p["key"]
        line = line_of(p["key"])
        if line:
            line.update(problem=p["text"], fix=p.get("fix"), note=None)
        prob = {"tab": rec["tab"], "row": rec["row"], "column": col, "text": p["text"], "fix": p.get("fix")}
        res["problems"].append(prob)
        rec["problems"].append(prob)


def child_problem(res, rec, p):
    """A folder problem about a child row (key = the child tab's "into", e.g. "installments" with
    "row" = the n-th installment; or a set whose value the text quotes) goes red on that sheet row,
    in its own table. False when it isn't one (then it stays on the record)."""
    rule_tab = {r["into"]: name for name, r in (group_of(rec).get("child_tabs") or {}).items()}
    table = next((t for t in rec.get("child_tables") or [] if workbook.norm(t["tab"]) ==
                  workbook.norm(rule_tab.get(p.get("key"), "\0"))), None)
    if table is None and len(rule_tab) == 1 and p.get("key") in rule_tab and rec.get("children"):
        # a group with one child tab (Lookup Types: Lookup Codes): its one table of rows
        table = dict(rec["children"], tab=rule_tab[p["key"]])
    if not table or not table["rows"]:
        return False
    row = None
    if p.get("row") and 0 < p["row"] <= len(table["rows"]):
        row = table["rows"][p["row"] - 1]
    else:
        row = next((r for r in table["rows"] if any(c.get("sheet") and f"'{c['sheet']}'" in p["text"]
                                                    for c in r["cells"][1:])), None)
    if row is None:
        return False
    cell = row["cells"][0]                         # the row's first cell (its term's name) carries the message
    cell.update(problem=p["text"], fix=p.get("fix"))
    prob = {"tab": table["tab"], "row": row["row"], "column": cell["label"], "text": p["text"], "fix": p.get("fix")}
    res["problems"].append(prob)
    rec["problems"].append(prob)
    return True


def same_name_notes(records):
    """Read-only, before Create: the records Oracle already has with each record's name, for
    groups whose registry entry names a "same_name_check" command (Customers: --existing), all
    in one browser visit. Names are not unique in Oracle; the note only tells the user, Create
    still makes a new one. One note (or None) per record."""
    out, todo = [None] * len(records), {}
    for i, rec in enumerate(records):
        cmd = group_of(rec).get("same_name_check")
        if cmd:
            todo.setdefault((rec["folder"], cmd), []).append(i)
    for (folder, cmd), idx in todo.items():
        what = group_of(records[idx[0]]).get("record", "record")
        if run_active():
            answers = [{"ok": False, "text": "another task is running"}] * len(idx)
        else:
            answers = folder_check(folder, cmd, [records[i]["request"] for i in idx], 300 + 30 * len(idx))
        for i, data in zip(idx, answers):
            if not data.get("ok"):
                out[i] = (f"Oracle couldn't be checked for {what}s with the same name ({data.get('text') or 'no answer'}). "
                          f"Create still makes a new {what}.")
                continue
            ids, name = [m["registry_id"] for m in data["matches"]], data.get("name") or records[i]["name"]
            n = len(ids)
            out[i] = (f"No {what} named {name} exists in Oracle yet." if not ids else
                      f"{n} {what}{'s' if n != 1 else ''} named {name} already exist{'s' if n == 1 else ''} "
                      f"(Registry ID{'s' if n != 1 else ''} {', '.join(ids)}). Create will make a new one.")
    return out


def upload_view(uid):
    """The preview for the page (the folder request itself stays on the server)."""
    u = UPLOADS[uid]
    res = json.loads(json.dumps(u["preview"]))
    for r in res["records"]:
        r.pop("request", None)
    return dict(res, id=uid, file=u["file"], job=u["job"] if u["job"] in JOBS else None,
                test_mode=TEST_MODE["on"])


# ---------------------------------------------------------------- Claude's command-line tool

def find_claude():
    if claude_tool.simulated():                      # --simulate-claude-blocked (testing)
        return None
    for name in ("claude", "claude.exe", "claude.cmd"):
        p = shutil.which(name)
        if p:
            return p
    for p in (Path(os.environ.get("APPDATA", "")) / "npm" / "claude.cmd",
              Path.home() / ".local" / "bin" / "claude.exe", Path.home() / ".local" / "bin" / "claude"):
        if p.exists():
            return str(p)
    return claude_tool.find_path()                   # per-user installs in the tools folder


def claude_command(cli):
    """The command that runs the tool. For an npm install (claude.cmd) the real program is
    called directly, so long arguments are not mangled by cmd.exe."""
    if cli.lower().endswith(".cmd"):
        base = Path(cli).parent / "node_modules" / "@anthropic-ai" / "claude-code"
        for exe in (base / "bin" / "claude.exe", base / "claude.exe"):
            if exe.exists():
                return [str(exe)]
        js = base / "cli.js"
        node = shutil.which("node") or claude_tool.node_exe()
        if js.exists() and node:
            return [node, str(js)]
    return [cli]


def claude_status():
    cli = find_claude()
    if not cli:
        st = {"installed": False, "signed_in": False}
    else:
        try:
            p = subprocess.run(claude_command(cli) + ["auth", "status"], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=60, cwd=ROOT)
            data = json.loads(p.stdout[p.stdout.index("{"):])
            st = {"installed": True, "signed_in": bool(data.get("loggedIn"))}
        except Exception as e:  # noqa: BLE001
            log(f"claude auth status failed: {e}")
            st = {"installed": True, "signed_in": False}
    with LOCK:
        CLAUDE.update(st, at=time.time())
    return st


CLAUDE = {"installed": False, "signed_in": False, "at": 0, "signing_in": False, "install": None}


def claude_status_cached(max_age=30):
    if time.time() - CLAUDE["at"] > max_age and not CLAUDE["signing_in"]:
        claude_status()
    return dict({k: CLAUDE[k] for k in ("installed", "signed_in", "signing_in")}, skipped=claude_skipped())


def claude_skipped():
    return CLAUDE_SKIP.exists()


def claude_install():
    """Install Claude's tool for this user without administrator rights: the routes of
    common/claude_tool.py in order (the npm route used before comes first). The result,
    with each route's plain reason, is kept for the checklist."""
    res = claude_tool.install(log=log)
    claude_tool.add_to_path(os.environ)
    claude_tool.add_to_path(ENV_CHILD)
    with LOCK:
        CLAUDE["install"] = res
    log(f"Claude's tool: {'installed via ' + res['route'] + ' (' + str(res['version']) + ')' if res['ok'] else 'not installed: ' + res['reason']}")
    return res


def claude_unavailable_text():
    """Why automatic fixes can't be used, in plain words (with each route's reason)."""
    res = CLAUDE.get("install") or {}
    lines = [f"- {t['text']}: {t['reason']}" for t in res.get("routes", []) if not t["ok"]]
    return ("Claude's helper couldn't be installed on this computer without administrator rights, "
            "so problems can't be fixed automatically here. Everything else works." +
            ("\nWhat was tried:\n" + "\n".join(lines) if lines else ""))


def claude_ok_text():
    res = CLAUDE.get("install") or {}
    if res.get("ok") and res.get("route") != "already":
        return f"Installed with {res['route_text']}, and signed in"
    return "Ready and signed in"


def claude_skip():
    """'Continue without automatic fixes': remember it on this PC and let setup finish.
    An install still running carries on in the background."""
    WORK.mkdir(parents=True, exist_ok=True)
    CLAUDE_SKIP.write_text(f"chosen {now_iso()}\n", encoding="utf-8")
    log("Claude step: the user chose to continue without automatic fixes")
    others_ok = all(SETUP["steps"][d["key"]]["state"] == "ok" for d in STEP_DEFS if d["key"] != "claude")
    if SETUP["steps"]["claude"]["state"] != "ok":
        set_step("claude", "skipped", SKIPPED_TEXT, button="Try again", retry=True)
    if others_ok and not SETUP["complete"]:
        threading.Thread(target=finish_setup, daemon=True).start()


def claude_signin(job_id=None):
    """One click: open Claude's sign-in in its own window and watch until the user is
    signed in; then carry on by itself (setup continues, a waiting repair starts)."""
    cli = find_claude()
    if not cli:
        setup_start("claude")                       # the setup step installs it first
        return False
    with LOCK:
        already = CLAUDE["signing_in"]
        CLAUDE["signing_in"] = True
        if job_id:
            CLAUDE.setdefault("jobs", set()).add(job_id)
    if already:
        return True
    cmd = claude_command(cli) + ["auth", "login"]
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", "start", "Sign in to Claude", "cmd", "/c"] + cmd, cwd=ROOT)
    else:
        subprocess.Popen(cmd, cwd=ROOT)
    log("Claude sign-in window opened")

    def watch():
        deadline = time.time() + 15 * 60
        ok = False
        while time.time() < deadline:
            time.sleep(4)
            if claude_status()["signed_in"]:
                ok = True
                break
        with LOCK:
            CLAUDE["signing_in"] = False
            jobs = CLAUDE.pop("jobs", set())
        log(f"Claude sign-in {'finished' if ok else 'not finished within 15 minutes'}")
        if not ok:
            return
        if SETUP["steps"]["claude"]["state"] != "ok":
            setup_start("claude")
        for jid in jobs:
            retry_repair(JOBS.get(jid))
    threading.Thread(target=watch, daemon=True).start()
    return True


# ---------------------------------------------------------------- setup checklist

STEP_DEFS = [
    {"key": "packages", "title": "Helper programs for the automation",
     "auto": "Installing the helper programs"},
    {"key": "browser", "title": "The browser the automation uses",
     "auto": "Installing the browser"},
    {"key": "login_file", "title": "Your Oracle details",
     "user": "Enter your Oracle details",
     "how": "A small file opens in Notepad. Fill in your own Oracle user name and password, "
            "the address of your Oracle environment (it starts with https://) and a name for "
            "the environment, for example test. Save the file and close Notepad; the page "
            "carries on by itself. Nobody else sees these details; this page never reads them."},
    {"key": "connection", "title": "Connection to Oracle"},
    {"key": "session", "title": "Your Oracle sign-in",
     "user": "Sign in to Oracle",
     "how": "A browser window opens on Oracle's sign-in page. Sign in there yourself. The "
            "window closes by itself when you reach the Oracle home page, and the page carries on."},
    {"key": "look", "title": "Looking at Oracle's screens",
     "user": "Try again",
     "how": "The automation opens one Oracle screen with your sign-in, reads a field name and "
            "closes it without saving. Automatic fixes use this to see what changed in Oracle."},
    {"key": "claude", "title": "Claude, for fixing problems automatically",
     "auto": "Installing Claude's helper", "user": "Sign in to Claude",
     "how": "Press the button. Claude's sign-in page opens in your browser (a small window "
            "opens too and closes by itself). Sign in there with your own Claude account. "
            "The page notices by itself when you are done; you don't need to press anything else."},
]
SIGNIN_TEXT = "Sign in to Oracle once in the window that opened; it closes by itself, and the page carries on."
SKIP_LABEL = "Continue without automatic fixes"
SKIPPED_TEXT = ("Skipped: automatic fixes are off on this computer. Everything else works as usual; if a run "
                "fails, the page shows what went wrong and a message you can copy into Claude. "
                "Press Try again at any time to set it up.")
SIGNIN_LOCK = threading.Lock()


def session_valid():
    """Quick read-only check of the saved Oracle sign-in (common/session_check.py). It waits for another preview's
    checks to finish (one Oracle browser at a time), but never for a whole run: while a run is active it goes
    ahead as before."""
    if run_active():
        return _session_valid()
    with ORACLE_LOCK:
        return _session_valid()


def _session_valid():
    code, out, err = run_py(["common/session_check.py"], 150)
    try:
        res = json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        res = {"valid": False, "reason": (err or "no answer").strip()[-200:]}
    log(f"saved Oracle sign-in: {res.get('reason')} (saved {res.get('saved_at')}, {res.get('seconds')}s)")
    return res


def oracle_signin():
    """Open the Oracle sign-in window (common/login_once.py) and wait until it closes.
    One window at a time: a second caller waits, then finds the session valid."""
    with SIGNIN_LOCK:
        if session_valid().get("valid"):
            return True
        log("Oracle sign-in window opened")
        code, out, err = run_py(["common/login_once.py"], 16 * 60)
        log(f"Oracle sign-in window closed (exit {code})")
        return code == 0
SETUP = {"steps": {d["key"]: {"state": "pending", "text": ""} for d in STEP_DEFS},
         "running": False, "complete": False, "waiting": None, "action": None}


def plain_failure(key, res):
    lines = " ".join(res.get("lines", []))
    if key == "packages":
        return "Some helper programs are missing and couldn't be installed. Check the internet connection and try again."
    if key == "browser":
        return ("The automation's browser couldn't start or be installed. Check the internet "
                "connection and try again; if your company blocks downloads, ask IT to allow it.")
    if key == "login_file":
        if not res.get("exists"):
            return "The login file doesn't exist yet."
        if "production" in lines.lower():
            return ("The login file names the live (production) Oracle. Changes there are switched off; "
                    "use a test environment, or add the production switch yourself on purpose.")
        if "https://" in lines:
            return "The Oracle address in the login file must start with https://."
        return "Some details in the login file are still empty."
    if key == "connection":
        if "HTTP 401" in lines:
            return "Oracle didn't accept the user name or password in the login file, or the account is locked."
        if "HTTP 403" in lines:
            return "Your Oracle user isn't allowed to use this kind of connection. Ask your Oracle administrator."
        if "HTTP 404" in lines:
            return "The Oracle address in the login file doesn't look right. Check it."
        if "secure connection" in lines:
            return "A secure connection to Oracle couldn't be made. Your company network may block it; ask IT."
        return "Oracle can't be reached. Check the internet or VPN connection and the Oracle address."
    if key == "session":
        return "You aren't signed in to Oracle in the automation's browser yet, or the sign-in has expired."
    if key == "look":
        if "expired" in lines.lower():
            return "Your Oracle sign-in expired while checking. Press Try again; the sign-in window opens if needed."
        if "didn't open" in lines:
            return ("The automation couldn't open an Oracle screen. Check the internet connection and that "
                    "your Oracle user may open Setup and Maintenance, then press Try again.")
        return ("An Oracle screen opened but didn't look as expected, so automatic fixes can't see Oracle's "
                "screens yet. Everything else still works. Press Try again, or tell the person who looks "
                "after this project.")
    return "This step didn't pass."


def check_step(key):
    if key == "claude":
        st = claude_status()
        if st["installed"] and st["signed_in"]:
            CLAUDE_SKIP.unlink(missing_ok=True)       # automatic fixes work again
        return {"ok": st["installed"] and st["signed_in"], **st}
    if key == "session":
        if env_label()["production"]:
            return {"ok": True, "production": True}
        res = session_valid()
        return {"ok": bool(res.get("valid")), "lines": [str(res.get("reason"))], **res}
    if key == "look":
        if env_label()["production"]:
            return {"ok": True, "production": True}
        if (ROOT / ".setup_ok").exists():          # confirmed when this PC was set up
            return {"ok": True, "earlier": True}
    code, out, err = run_py(["page/setup_check.py", key], 300)
    try:
        return json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {"ok": False, "lines": [err.strip()[-300:]]}


def auto_fix(key, res):
    """Automatic fixes; True when something was tried."""
    if key == "packages":
        run_py(["-m", "pip", "install", "-r", "requirements.txt"], 900)
        return True
    if key == "browser":
        run_py(["-m", "playwright", "install", "chromium"], 1800)
        return True
    if key == "claude" and not res.get("installed"):
        claude_install()
        return True
    return False


def set_step(key, state, text="", **extra):
    with LOCK:
        SETUP["steps"][key] = {"state": state, "text": text, **extra}


def setup_routine(from_key=None):
    """Run the checklist in order; automatic fixes run by themselves, a user step waits."""
    with LOCK:
        if SETUP["running"]:
            return
        SETUP["running"], SETUP["waiting"] = True, None
    try:
        started = from_key is None
        for d in STEP_DEFS:
            key = d["key"]
            if not started and key != from_key and SETUP["steps"][key]["state"] == "ok":
                continue
            started = True
            set_step(key, "checking", "Checking ...")
            res = check_step(key)
            if not res.get("ok") and d.get("auto") and (key != "claude" or not res.get("installed")) \
                    and not (key == "claude" and claude_skipped() and from_key != "claude"):
                # Claude's helper: installed again only on a fresh setup or "Try again", never
                # at every start once the user chose to continue without it.
                set_step(key, "fixing", d["auto"] + " ...", **({"skip": SKIP_LABEL} if key == "claude" else {}))
                if auto_fix(key, res):
                    res = check_step(key)
            if not res.get("ok") and key == "session":
                # Missing or expired: open the sign-in window right away, before the cards.
                set_step(key, "signing", SIGNIN_TEXT)
                if oracle_signin():
                    res = check_step(key)
            if res.get("ok"):
                set_step(key, "ok", "Not needed here (live environment)" if res.get("production")
                         else "Checked when this computer was set up" if res.get("earlier")
                         else "Signed in" if key == "session"
                         else "Opened an Oracle screen and closed it without saving" if key == "look"
                         else claude_ok_text() if key == "claude"
                         else "Done")
                continue
            if key == "claude":
                # Optional: never blocks setup. Not installed or not signed in -> the user may
                # continue without automatic fixes (remembered on this PC, see claude_skip()).
                if claude_skipped():
                    set_step(key, "skipped", SKIPPED_TEXT, button="Try again", retry=True)
                    continue
                if not res.get("installed"):
                    set_step(key, "waiting", claude_unavailable_text(), button="Try again", retry=True,
                             skip=SKIP_LABEL)
                elif CLAUDE["signing_in"]:
                    set_step(key, "signing", "Waiting for you to sign in to Claude in the window that "
                             "opened. This page carries on by itself as soon as you are signed in.",
                             skip=SKIP_LABEL)
                else:
                    set_step(key, "waiting", "Please sign in to Claude (one click).", button=d["user"],
                             how=d["how"], skip=SKIP_LABEL)
            elif d.get("user"):
                set_step(key, "waiting", plain_failure(key, res), button=d["user"], how=d["how"])
            else:
                set_step(key, "failed", plain_failure(key, res))
            with LOCK:
                SETUP["waiting"] = key
            log(f"setup step {key} not passed: {res.get('lines', res)}")
            break
        else:
            finish_setup()
    except Exception:  # noqa: BLE001
        log("setup routine error:\n" + traceback.format_exc())
    finally:
        with LOCK:
            SETUP["running"] = False


FINISH_LOCK = threading.Lock()


def finish_setup():
    """All steps passed (or Claude's helper was skipped): the marker, then the cards."""
    with FINISH_LOCK:
        _finish_setup()


def _finish_setup():
    if SETUP["complete"]:
        return
    env = env_label()
    if not env["allowed"]:
        with LOCK:
            SETUP["complete"] = False
        return
    if not (ROOT / ".setup_ok").exists():          # first time on this PC: the marker
        code, out, err = run_py(["common/check_setup.py", "--final"], 600)
        log(f"check_setup --final exit {code}")
    with LOCK:
        SETUP["complete"] = True
    log("setup checklist passed; showing the cards" +
        (" (without automatic fixes)" if SETUP["steps"]["claude"]["state"] != "ok" else ""))
    threading.Thread(target=warm_options, daemon=True).start()


def setup_action(key):
    """A step the user does: open the login file, sign in to Claude, sign in to Oracle."""
    if key == "login_file":
        env_file = ROOT / ".env"
        if not env_file.exists():
            shutil.copyfile(ROOT / ".env.example", env_file)      # empty values; the user fills them in
        if sys.platform == "win32":
            editor = subprocess.Popen(["notepad.exe", str(env_file)])
        elif sys.platform == "darwin":
            editor = subprocess.Popen(["open", "-W", "-e", str(env_file)])
        else:
            editor = subprocess.Popen(["xdg-open", str(env_file)])
        set_step(key, "waiting", "Fill in your Oracle details in the file that opened, save it and "
                 "close it. The page carries on by itself (or press Continue).",
                 button="Continue", how=STEP_DEFS[2]["how"], opened=True)
        before = env_file.stat().st_mtime

        def watch():
            # carry on when the editor closes or the file is saved (whichever comes first)
            for _ in range(30 * 60):
                time.sleep(1)
                if editor.poll() is not None and time.time() - start > 3 or env_file.stat().st_mtime != before:
                    time.sleep(1)
                    if SETUP["steps"][key]["state"] == "waiting":
                        setup_start(key)
                    return
        start = time.time()
        threading.Thread(target=watch, daemon=True).start()
        return
    if key == "claude":
        if claude_signin():
            set_step(key, "signing", "Waiting for you to sign in to Claude in the window that opened. "
                     "This page carries on by itself as soon as you are signed in.")
        return
    if key == "session":
        set_step(key, "signing", SIGNIN_TEXT)

        def go():
            oracle_signin()
            with LOCK:
                SETUP["steps"]["session"]["state"] = "pending"
            setup_start("session")
        threading.Thread(target=go, daemon=True).start()


def setup_start(from_key=None):
    threading.Thread(target=setup_routine, args=(from_key,), daemon=True).start()


def setup_quick():
    """Is setup complete? The checklist runs at every start (a few seconds when this PC is
    set up: quick checks plus the saved Oracle sign-in), so this is its outcome."""
    return SETUP["complete"]


# ---------------------------------------------------------------- runs (one at a time)

JOBS = {}
JOB_QUEUE = queue.Queue()


def new_job(folder, request, force_fail=False, title=None, extra=None):
    job = {"id": uuid.uuid4().hex[:10], "folder": folder, "request": request, "title": title,
           "state": "queued", "step": None, "percent": 0, "text": "Waiting for its turn",
           "result": None, "ask": None, "repairs": 0, "created_at": time.time(),
           "force_fail": bool(force_fail and TEST_MODE["on"]), "history": [], **(extra or {})}
    with LOCK:
        JOBS[job["id"]] = job
    JOB_QUEUE.put(job["id"])
    log(f"job {job['id']} queued: {folder}" + (f" (upload {job['upload']})" if job.get("upload") else ""))
    return job


def update(job, **kw):
    with LOCK:
        job.update(kw)


def queue_position(job):
    with LOCK:
        waiting = [j for j in JOBS.values() if j["state"] == "queued" and j["created_at"] < job["created_at"]]
        running = any(j["state"] in ("running", "repairing") for j in JOBS.values())
    return len(waiting) + (1 if running else 0)


def run_folder(job, record=True):
    """The folder's --run; progress lines update the job. Returns the result line."""
    script = FOLDERS[job["folder"]]["script"]
    LOGS.mkdir(parents=True, exist_ok=True)
    logf = LOGS / f"{job['id']}.log"
    env = dict(ENV_CHILD)
    if job.get("force_fail"):
        # Test switch: point the automation at a browser that doesn't exist, so the run
        # fails for a real reason that is not in the request and not in the folder.
        env["PLAYWRIGHT_BROWSERS_PATH"] = str(WORK / "no-browser-here")
        job["force_fail"] = False
        log(f"job {job['id']}: test switch - this run is made to fail (no browser)")
    with logf.open("a", encoding="utf-8") as lf:
        lf.write(f"\n===== run {datetime.now():%H:%M:%S}\n")
        p = subprocess.Popen([PY, script, job.get("cmd") or "--run", json.dumps(job["request"])], cwd=ROOT,
                             stdout=subprocess.PIPE, stderr=lf, text=True, encoding="utf-8",
                             errors="replace", env=env)
        result = None
        done_lines = []          # finished parts ("Order Manager access: done"), shown under the bar
        for line in p.stdout:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if ev.get("step") == "result":
                result = ev
            elif record:
                if (ev.get("text") or "").endswith(": done"):
                    done_lines.append(ev["text"])
                update(job, step=ev.get("step"), percent=ev.get("percent") or job["percent"],
                       text=ev.get("text") or job["text"], done_lines=list(done_lines))
        p.wait()
    if result is None:
        tail = logf.read_text(encoding="utf-8", errors="replace")[-1500:]
        result = {"step": "result", "ok": False, "text": "Something went wrong.",
                  "error": {"code": "FAILED", "step": job.get("step"), "detail": tail}}
    return result


def new_batch(records, upload, force_fail=False):
    """One run for a whole checked sheet: its records one after another, in sheet order, each
    through its folder's --run (2026-10-23). The test switch makes the first record fail once."""
    items = [{"n": i + 1, "folder": r["folder"], "request": r["request"], "title": r["title"], "name": r["name"],
              "rows": r["rows"], "state": "waiting", "result": None, "ask": None, "repairs": 0,
              "what": group_of(r).get("record", "record"), "group": r["group"]}
             for i, r in enumerate(records)]
    words = list(dict.fromkeys(it["what"] for it in items))
    what = words[0] if len(words) == 1 else "row"
    # a sheet with several modules (2026-10-25): "3 customers and 1 order type from your sheet"
    title = (f"{len(items)} {what}s from your sheet" if len(words) == 1 else
             " and ".join(counted(sum(1 for it in items if it["what"] == w), w) for w in words) + " from your sheet") \
        if len(items) > 1 else records[0]["title"]
    return new_job(records[0]["folder"], None, force_fail, title,
                   extra={"items": items, "upload": upload, "what": what, "words": words})


def counted(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


def batch_text(items, what):
    """The run's closing line. One module without skips: as before ("Created 2 of 3 customers.")."""
    n = len(items)
    skipped = sum(1 for it in items if it["state"] == "done" and (it.get("result") or {}).get("skipped"))
    made = sum(1 for it in items if it["state"] == "done") - skipped
    failed = sum(1 for it in items if it["state"] == "failed")
    if not skipped and what != "row":
        return f"Created {made} of {n} {what}{'s' if n != 1 else ''}."
    text = f"Created {made} of {n} {what}{'s' if n != 1 else ''}"
    parts = ([f"{skipped} already existed and {'were' if skipped != 1 else 'was'} skipped (nothing changed)"]
             if skipped else []) + ([f"{failed} failed"] if failed else [])
    return text + (": " + ", ".join(parts) if parts else "") + "."


def run_batch(job):
    """Each record through the normal single run: progress lines, automatic repair, then a
    plain result. A failed record doesn't stop the others; nothing asks the user anything.
    Duplicates after a failed try are prevented by each folder per record (Customers: the
    rerun note in its _work/, one entry per customer)."""
    items, n = job["items"], len(job["items"])
    done_groups = set()
    for it in items:
        if it["state"] != "waiting" or it.get("group") in done_groups:   # already run with its module
            continue
        cmd = group_of(it).get("batch_run")
        if cmd:                                       # e.g. Payment Terms: all in one import
            done_groups.add(it.get("group"))
            mine = [x for x in items if x.get("group") == it.get("group")]
            hold_dependents(job, mine)                # Price Lists: after their business units (2026-10-26)
            # only the records still waiting (all of them on the first run; a retry after the user
            # answered a question sends only the answered ones, 2026-10-26), never a held one
            todo = [x for x in mine if x["state"] == "waiting" and not x.get("held")]
            if todo:
                run_module_batch(job, todo, cmd)
            ask_questions(job, mine)
            continue
        sub = {"id": f"{job['id']}_{it['n']}", "folder": it["folder"], "request": it["request"],
               "title": it["title"], "state": "running", "step": None, "percent": 0, "text": "Starting",
               "result": None, "ask": None, "repairs": 0, "created_at": time.time(), "history": [],
               "force_fail": bool(job.get("force_fail")) and it["n"] == 1}
        with LOCK:
            job["sub"], it["state"] = sub, "running"
        log(f"job {job['id']}: {it.get('what') or job.get('what', 'record')} {it['n']} of {n}: {it['name']}")
        try:
            handle_result(sub, run_folder(sub))
        except Exception:  # noqa: BLE001 - one record's crash never stops the others
            log(f"job {sub['id']} crashed:\n{traceback.format_exc()}")
            update(sub, state="failed", ask={"kind": "stop", "text": "Something went wrong on this PC.",
                                             "todo": None})
        with LOCK:
            it.update(state="done" if sub["state"] == "done" else "failed", result=sub["result"],
                      ask=sub["ask"], repairs=sub["repairs"])
        log(f"job {job['id']}: {it['name']} {it['state']}")
        ask_questions(job, [it])                      # Customers v2: a refused value asks (registry ask_on_refusal)
    done = sum(1 for it in items if it["state"] == "done")
    text = batch_text(items, job.get("what", "record"))
    update(job, state="done" if done == n else "failed", percent=100, text=text, sub=None,
           result={"ok": done == n, "text": text}, ask=None if done == n else {"kind": "stop", "text": text})
    still_asking(job)


# ---------------------------------------------------------------- questions (Business Units, 2026-10-26)
# A registry group with "ask_on_refusal" (Business Units): a record Oracle refused for a value doesn't
# end the run silently. Everything else is made first; then the run stays open ("asking") with one
# question per refused record (what was refused and why, the sheet row, Oracle's suggested values,
# another value, or skip). An answer is checked with the folder's --plan (Oracle's lists) before it is
# accepted; then only that record goes through the folder's batch command again (rerun rules: what is
# saved is skipped, nothing is made twice). The questions live in the run (they survive a page
# refresh) and in server.log (the Run summary).

OPEN_Q = ("open", "checking", "retrying")


def label_of(group, key, rows_key=None):
    tabs = {workbook.norm(t) for t in group.get("record_tabs", {})}
    if rows_key:                                   # a value of a child row (2026-10-26): that child tab's column
        tabs = {workbook.norm(t) for t, c in group.get("child_tabs", {}).items() if c.get("into") == rows_key} or tabs
    for t in workbook.load_definition()["tabs"]:
        if workbook.norm(t["name"]) in tabs:
            for c in t["columns"]:
                if c.get("key") == key:
                    return c["label"]
    return key


def child_row_of(group, it, rows_key, n):
    """The sheet place [tab, row] of the n-th row (1-based) of a record's child rows `rows_key` (Payment Terms'
    installments, Lookup Types' codes), or None. An orphan record's own row is its first child row."""
    tabs = {workbook.norm(t) for t, c in group.get("child_tabs", {}).items() if c.get("into") == rows_key}
    rows = (it.get("rows") or {})
    places = sorted({tuple(r) for r in [rows.get("record")] + list(rows.get("children") or [])
                     if r and workbook.norm(r[0]) in tabs}, key=lambda r: r[1])
    return list(places[n - 1]) if n and 0 < n <= len(places) else None


def ask_questions(job, group_items):
    """After a module's batch: a question for each record the folder refused for a value it can be
    asked about (the result's problems with a field the group allows, nothing saved)."""
    g = group_of(group_items[0]) if group_items else {}
    rule = g.get("ask_on_refusal")
    if not rule:
        return
    for it in group_items:
        if it["state"] != "failed":
            if it.get("question") and it["question"]["state"] == "retrying":
                with LOCK:
                    it["question"].update(state="answered")
                log(f"job {job['id']}: question {it['n']} ({it['name']}) answered: "
                    f"{it['question']['label']} = {it['question'].get('answer')}; done")
            continue
        if (it.get("question") or {}).get("state") in ("open", "checking", "skipped", "closed"):
            continue                               # already asked (not part of this try): left as it is
        err = (it.get("result") or {}).get("error") or {}
        d = err.get("detail") if isinstance(err.get("detail"), dict) else {}
        probs = [p for p in d.get("problems") or [] if isinstance(p, dict) and p.get("field") in rule["fields"]]
        if not probs and err.get("code") in ASK_USER and d.get("saved") == "no" \
                and (it.get("question") or {}).get("tries", 0) < REPAIR_ATTEMPTS:
            # 2026-10-26: a refusal that matches no known rule: Claude proposes a field and a value; it is
            # only offered in the panel (the user accepts, changes or skips it), never applied by itself
            with LOCK:
                job["text"] = f"Asking Claude what to change for {it['name']}"
            got = propose_value(job, it, g, rule, err, d)
            probs = [got] if got else []
        if err.get("code") not in ASK_USER or d.get("saved") != "no" or not probs:
            if (it.get("question") or {}).get("state") == "retrying":   # failed again, not for a value
                with LOCK:
                    it["question"].update(state="closed", message=(it.get("result") or {}).get("text"))
                log(f"job {job['id']}: question {it['n']} ({it['name']}) tried again: failed, not for a value")
            continue
        p = probs[0]
        q_old = it.get("question") or {}
        rows = it.get("rows") or {}
        child = child_row_of(g, it, p.get("rows"), p.get("row")) if p.get("rows") else None
        q = {"field": p["field"], "label": label_of(g, p["field"], p.get("rows")), "value": p.get("value"),
             "reason": p.get("reason") or p.get("text") or (it.get("result") or {}).get("text"),
             "suggestions": [s for s in p.get("suggestions") or [] if s != p.get("value")][:12],
             "tab": (child or rows.get("record") or [None, None])[0], "row": (child or rows.get("record") or [None, None])[1],
             "state": "open", "message": None, "tries": q_old.get("tries", 0), "answer": None,
             **({"rows": p["rows"], "row_n": p.get("row"), "where": p.get("where")} if p.get("rows") else {}),
             **({"proposed": p["proposed"], "proposed_cost": p.get("proposed_cost")} if p.get("proposed") else {})}
        if q_old.get("state") == "retrying":       # the answered value was refused again
            q["message"] = f"Oracle refused {q_old.get('answer')!r} too: {q['reason']}"
        with LOCK:
            it["question"] = q
        log(f"job {job['id']}: question {it['n']} ({it['name']}): {q['label']} '{q['value']}' refused: "
            f"{q['reason']}; suggested: {', '.join(q['suggestions']) or 'none'}")


PROPOSAL_SCHEMA = {
    "type": "object",
    "properties": {
        "field": {"type": "string", "description": "the request key of the ONE field to change (one of the listed keys)"},
        "value": {"type": "string", "description": "the new value most likely to be accepted, as the user would type it"},
        "row": {"type": ["integer", "null"], "description": "1-based row number when the field is in a repeating group, else null"},
        "why": {"type": "string", "description": "one plain sentence for the user, no technical terms"},
    },
    "required": ["field", "value", "why"],
}


def proposal_permissions(folder):
    """Least privilege for a proposal: read the folder's notes and the root CLAUDE.md; no edits, no commands."""
    deny = ["Read(./.env)", "Read(./.session/**)", "Read(./.session)", "Edit", "Write", "Bash", "PowerShell",
            "WebFetch", "WebSearch", "NotebookEdit"]
    return {"permissions": {"allow": [f"Read(./{folder}/**)", "Read(./CLAUDE.md)"], "deny": deny,
                            "defaultMode": "dontAsk"}}


def rows_key_of(group, field):
    """The request rows key whose child tab has this field (Payment Terms installments, Lookup Types codes)."""
    for t, c in group.get("child_tabs", {}).items():
        tab = next((x for x in workbook.load_definition()["tabs"] if workbook.norm(x["name"]) == workbook.norm(t)), None)
        if tab and c.get("into") and any(col.get("key") == field for col in tab["columns"]):
            return c["into"]
    return None


def propose_value(job, it, group, rule, err, detail):
    """One Claude call (claude -p with the repair's limits: REPAIR_BUDGET_USD, REPAIR_MINUTES, no MCP, no browser; and
    the repair's do-not-start rules: Claude's tool installed and signed in) for a refusal no folder rule recognises.
    Returns a problem {field, value, reason, suggestions: [proposed value], proposed: why, rows?, row?} or None.
    Logged as "job <run>_<n>p proposal: cost $x" with its .repair.log, so the Run summary shows tokens and cost."""
    reason = (detail.get("message") if isinstance(detail.get("message"), str) else None) \
        or (it.get("result") or {}).get("text")
    st = claude_status()
    if not st["installed"] or not st["signed_in"]:
        log(f"job {job['id']}: question {it['n']} ({it['name']}) not asked: refusal not recognised and Claude is not "
            f"available (installed={st['installed']}, signed in={st['signed_in']}): {reason}")
        return None
    pid = f"{job['id']}_{it['n']}p"
    WORK.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    settings = WORK / f"proposal_settings_{pid}.json"
    settings.write_text(json.dumps(proposal_permissions(it["folder"])), encoding="utf-8")
    fields = {f: label_of(group, f, rows_key_of(group, f)) for f in rule["fields"]}
    prompt = (f"PROPOSE A VALUE. Oracle Fusion refused to create one {it.get('what') or 'record'} from an upload sheet "
              f"and nothing was saved. Oracle's message: {reason}\n\nThe request the page sent (JSON): "
              f"{json.dumps(it['request'], ensure_ascii=False)}\n\nFields the user may change (key: label): "
              f"{json.dumps(fields, ensure_ascii=False)}\n\nRead '{it['folder']}/CLAUDE.md' and "
              f"'{it['folder']}/sheet_fields.md' for Oracle's rules. Do not edit anything and do not run anything. "
              "Answer with the ONE field (its key) and the new value most likely to be accepted; when the field is in "
              "a repeating group (a list in the request), give its 1-based row. The user decides; you only propose.")
    cmd = claude_command(find_claude()) + ["-p", "--output-format", "stream-json", "--verbose",
                                           "--json-schema", json.dumps(PROPOSAL_SCHEMA),
                                           "--permission-mode", "dontAsk", "--permission-prompts", "none",
                                           "--settings", str(settings), "--strict-mcp-config", "--no-chrome",
                                           "--max-budget-usd", str(REPAIR_BUDGET_USD), "--no-session-persistence"]
    pjob = {"id": pid, "state": "running", "text": "", "percent": 0}
    out, cost = run_claude(pjob, cmd, prompt, REPAIR_MINUTES * 60, "")
    field, value = out.get("field"), out.get("value")
    log(f"job {pid} proposal: cost ${cost:.4f}, field {field}, value {value!r}: {out.get('why') or out.get('error')}")
    if field not in rule["fields"] or value in (None, ""):
        return None
    rows_key = rows_key_of(group, field)
    req = it["request"]
    if rows_key:
        n = out.get("row") or 1
        rows = req.get(rows_key) if isinstance(req.get(rows_key), list) else []
        if not 0 < n <= len(rows):
            return None
        old = rows[n - 1].get(field)
        where = {"installments": f"Installment {n}",
                 "codes": f"Code {n} ({rows[n - 1].get('code')})"}.get(rows_key, f"Row {n}")
        extra = {"rows": rows_key, "row": n, "where": where}
    else:
        old, extra = req.get(field), {}
    return {"field": field, "value": old, "reason": reason, "text": reason, "suggestions": [str(value)],
            "proposed": out.get("why") or "Claude's proposal", "proposed_cost": round(cost, 4), **extra}


def hold_dependents(job, group_items):
    """A group "depends_on" another (Price Lists on Business Units, 2026-10-26). A record whose request
    carries the rule's key (business_unit_pending: its business unit is on the sheet) runs only after
    that record of the other group is done (created, or already there): while it waits for a decision
    or hasn't run, it is held; when it failed or was skipped, the record is not sent and says why. The
    folder itself then waits until Oracle shows the business unit for pricing."""
    dep = (group_of(group_items[0]) if group_items else {}).get("depends_on")
    if not dep:
        return
    for it in group_items:
        if it["state"] != "waiting" or not (it.get("request") or {}).get(dep["key"]):
            continue
        name = it["request"].get(dep["request_key"])
        x = next((y for y in job["items"] if y.get("group") == dep["group"]
                  and (y.get("request") or {}).get("name") == name), None)
        if x is None or x["state"] == "done":
            with LOCK:
                it.pop("held", None)
                it.pop("hold_text", None)
            continue
        q = (x.get("question") or {}).get("state")
        what = group_of(x).get("record", "record")
        if x["state"] in ("waiting", "running") or q in OPEN_Q:
            text = (f"Waits for its {what} {name}, which needs your decision first." if q in OPEN_Q else
                    f"Waits for its {what} {name}, which is created first.")
            with LOCK:
                it.update(held=True, hold_text=text)
            continue
        why = "you chose to skip it" if q == "skipped" else \
            re.sub(r"\s+", " ", str(((x.get("ask") or {}).get("text") or (x.get("result") or {}).get("text") or
                                     "it didn't work")))[:300]
        text = (f"Not sent: its {what} {name} wasn't made ready in this run ({why}). Nothing of this "
                f"{it.get('what', 'record')} was saved; a rerun makes it once the {what} is there.")
        res = {"ok": False, "text": text, "error": {"code": "INVALID_REQUEST", "detail": {
            "saved": "no", "registry_id": None, "message": text, "waited_for": name}}}
        with LOCK:
            it.update(state="failed", result=res, held=False, hold_text=None,
                      ask={"kind": "stop", "text": text, "todo": f"Fix the {what} first, then upload the sheet again."})
        log(f"job {job['id']}: {it.get('what', 'record')} {it['n']} ({it['name']}) not sent: its {what} {name} "
            f"isn't ready ({why})")


def still_asking(job):
    """The run stays open while a question waits for the user (or its answer is being tried)."""
    open_q = [it for it in job.get("items", []) if (it.get("question") or {}).get("state") in OPEN_Q]
    if not open_q:
        return
    text = job["text"] + f" {counted(len(open_q), 'question')} waiting for your decision."
    update(job, state="asking", text=text, ask={"kind": "questions", "text": text})


def answer_question(job, n, value=None, skip=False):
    """The user's answer to one question: skip it, or a value (a suggested one or typed), which is
    checked with the folder's --plan first; a value Oracle's lists don't have stays open with the
    folder's reason. Returns {"ok", "text"}."""
    it = next((x for x in job.get("items", []) if x["n"] == n), None)
    q = (it or {}).get("question")
    if not q or q["state"] != "open":
        return {"ok": False, "text": "This question isn't open any more."}
    if skip:
        with LOCK:
            q.update(state="skipped", answer=None)
        log(f"job {job['id']}: question {n} ({it['name']}) skipped by the user")
        for g in {x.get("group") for x in job["items"]}:          # Price Lists waiting for it (2026-10-26)
            hold_dependents(job, [x for x in job["items"] if x.get("group") == g])
        if job["state"] == "asking" and not any((x.get("question") or {}).get("state") in OPEN_Q for x in job["items"]):
            done = sum(1 for x in job["items"] if x["state"] == "done")
            text = batch_text(job["items"], job.get("what", "record"))
            update(job, state="done" if done == len(job["items"]) else "failed", text=text,
                   result={"ok": False, "text": text}, ask={"kind": "stop", "text": text})
        return {"ok": True, "text": "Skipped."}
    value = (value or "").strip() if q["field"] != "name" else (value or "")
    if not value:
        return {"ok": False, "text": "Please pick or type a value."}
    with LOCK:
        q.update(state="checking", message=None, answer=value)

    def check():
        if q.get("rows"):                          # a child row's value (2026-10-26): put it into that row
            req = json.loads(json.dumps(it["request"]))
            req[q["rows"]][q["row_n"] - 1][q["field"]] = value
        else:
            req = dict(it["request"], **{q["field"]: value})
        g_ = group_of(it)
        with ORACLE_LOCK:
            got = folder_batch(it["folder"], g_.get("answer_check") or g_.get("oracle_check") or "--plan", [req], 600)[0]
        probs = [p for p in got.get("problems") or [] if p.get("key", p.get("field")) == q["field"]] \
            or got.get("problems") or []
        if not got.get("ok") or probs:
            why = (probs[0].get("text") or probs[0].get("reason")) if probs else (got.get("text") or "no answer")
            sugg = (probs[0].get("suggestions") if probs else None) or q["suggestions"]
            with LOCK:
                q.update(state="open", message=f"'{value}' can't be used: {why}", suggestions=sugg[:12])
            log(f"job {job['id']}: question {n} ({it['name']}): '{value}' not accepted: {why}")
            return
        with LOCK:
            it.update(request=req, state="waiting", result=None, ask=None)
            q.update(state="retrying", tries=q.get("tries", 0) + 1)
            for other in job.get("items", []):     # a value now taken is no longer offered elsewhere (2026-10-26)
                oq = other.get("question") or {}
                if other is not it and oq.get("state") == "open" and oq.get("field") == q["field"] \
                        and other.get("group") == it.get("group") and value in (oq.get("suggestions") or []):
                    oq["suggestions"] = [x for x in oq["suggestions"] if x != value]
        log(f"job {job['id']}: question {n} ({it['name']}) answered: {q['label']} = {value}; trying again")
        if job["state"] not in ("running", "queued"):
            update(job, state="queued", text=f"Trying {it['name']} again with the answered value")
        JOB_QUEUE.put(job["id"])
    threading.Thread(target=check, daemon=True).start()
    return {"ok": True, "text": "Checking the value with Oracle."}


def repairable(r):
    """A failed result the automatic repair may try (the same rule as handle_result): not a value the user must
    change, not a stop only a person can solve, not an expired sign-in, and nothing that may have been saved."""
    e = r.get("error") or {}
    d = e.get("detail") if isinstance(e.get("detail"), dict) else {}
    return e.get("code", "FAILED") not in ASK_USER | STOP_PLAIN | {"SIGN_IN_NEEDED"} and d.get("saved") != "maybe"


def run_module_batch(job, group_items, cmd):
    """A module whose registry group names a "batch_run" command (Payment Terms: --run-batch,
    2026-10-25) runs all its records of the sheet in ONE folder call (one import). The folder
    answers one result per record, in order; each goes on that record's card. A stop with no
    per-record answer (a screen or sign-in problem) follows the normal repair rules for the
    whole call, and the rerun skips what was saved."""
    n, first, last = len(job["items"]), group_items[0]["n"], group_items[-1]["n"]
    what = group_items[0].get("what", "record")
    sub = {"id": f"{job['id']}_{first}", "folder": group_items[0]["folder"], "cmd": cmd,
           "request": [it["request"] for it in group_items], "title": f"{len(group_items)} {what}s",
           "state": "running", "step": None, "percent": 0, "text": "Starting", "result": None, "ask": None,
           "repairs": 0, "created_at": time.time(), "history": [],
           "force_fail": bool(job.get("force_fail")) and first == 1}
    label = (f"{what.capitalize()}s {first}-{last} of {n}, in one go" if len(group_items) > 1
             else f"{what.capitalize()} {first} of {n}")
    with LOCK:
        job["sub"] = sub
        for it in group_items:
            it.update(state="running", batch_label=label)
    for it in group_items:                            # read by page/run_summary.py
        log(f"job {job['id']}: {what} {it['n']} of {n}: {it['name']}")
    res = None
    try:
        res = run_folder(sub)
        per = res.get("results") if isinstance(res.get("results"), list) else None
        code = (res.get("error") or {}).get("code")
        if per is None or (code and not any(r.get("ok") for r in per)
                           and code not in ASK_USER | STOP_PLAIN | {"SIGN_IN_NEEDED"}):
            handle_result(sub, res)                   # no answer per record: the normal rules (repair)
            res = sub["result"] or res
    except Exception:  # noqa: BLE001 - one module's crash never stops the others
        log(f"job {sub['id']} crashed:\n{traceback.format_exc()}")
        update(sub, state="failed", ask={"kind": "stop", "text": "Something went wrong on this PC.", "todo": None})
    per = (res or {}).get("results") if isinstance((res or {}).get("results"), list) else None
    if per is not None and sub.get("state") != "failed":
        # 2026-10-26: a record of the batch failed for a reason that isn't the user's (script, screen, verify): the
        # same automatic repair and do-not-start rules as a one-by-one run, for those records only (the folder's
        # batch command skips what is saved, so nothing is made twice)
        fix = [k for k, r in enumerate(per[:len(group_items)]) if not r.get("ok") and repairable(r)]
        if fix:
            sub2 = dict(sub, id=f"{job['id']}_{group_items[fix[0]]['n']}r",      # named after the failed record
                        request=[group_items[k]["request"] for k in fix], force_fail=False,
                        state="running", result=None, ask=None, repairs=0, history=[])
            first_bad = per[fix[0]]
            res2 = {"step": "result", "ok": False, "text": first_bad.get("text"), "error": first_bad.get("error"),
                    "results": [per[k] for k in fix]}
            log(f"job {job['id']}: {len(fix)} {what}(s) of the batch failed for a reason that isn't a value; "
                "automatic repair for those")
            src, dst = LOGS / f"{sub['id']}.log", LOGS / f"{sub2['id']}.log"   # the repair reads the run's log
            dst.write_text(src.read_text(encoding="utf-8", errors="replace") if src.exists() else "", encoding="utf-8")
            try:
                handle_result(sub2, res2)
            except Exception:  # noqa: BLE001
                log(f"job {sub2['id']} crashed:\n{traceback.format_exc()}")
            got = (sub2.get("result") or {}).get("results")
            for j, k in enumerate(fix):
                if isinstance(got, list) and j < len(got):
                    per[k] = got[j]
            sub["repairs"] = sub.get("repairs", 0) + sub2.get("repairs", 0)
    for k, it in enumerate(group_items):
        r = per[k] if per and k < len(per) else None
        if r is None:                                 # the whole call failed: the same card for each
            state, result, ask = "failed", sub["result"] or res, sub["ask"] or {
                "kind": "stop", "text": (res or {}).get("text") or "Something went wrong.", "todo": None}
        elif r.get("ok"):
            state, result, ask = "done", r, None
        else:
            c = (r.get("error") or {}).get("code")
            state, result = "failed", r
            ask = {"kind": "stop", "text": r.get("text"),
                   "todo": AFTER_FAILURE["value"] if c in ASK_USER else
                   AFTER_FAILURE["sign_in"] if c == "SIGN_IN_NEEDED" else WHAT_TO_DO.get(c)}
        with LOCK:
            it.update(state=state, result=result, ask=ask, repairs=sub["repairs"])
        log(f"job {job['id']}_{it['n']} {'done' if state == 'done' else 'stopped (' + str(((result or {}).get('error') or {}).get('code') or 'FAILED') + ')'}: "
            f"{(result or {}).get('text') or (ask or {}).get('text')}")
        log(f"job {job['id']}: {it['name']} {state}")


def saved_state(it):
    """For a failed record: "no" (nothing saved), "yes" / "maybe" (with its Registry ID), from
    the folder's error detail ("saved", "registry_id"); a value refused before the folder ran
    saved nothing; anything else is "maybe"."""
    err = (it.get("result") or {}).get("error") or {}
    d = err.get("detail")
    if isinstance(d, dict) and d.get("saved") in ("no", "yes", "maybe"):
        return d["saved"], d.get("registry_id")
    if err.get("code") in ASK_USER:
        return "no", None
    return "maybe", None


def batch_view(job):
    """The page's view of a sheet run: the record being run with its own progress, and one
    entry per record (created with what Oracle shows, or failed with the plain reason and
    whether anything was saved)."""
    items, n = job["items"], len(job["items"])
    sub = job.get("sub")
    view = {"total": n, "items": []}
    for it in items:
        e = {k: it[k] for k in ("n", "name", "title", "state", "repairs")}
        e["what"] = it.get("what") or job.get("what", "record")
        res = it.get("result") or {}
        if it["state"] == "done":
            e.update(text=res.get("text"), created=res.get("created"), where=res.get("where"),
                     repaired=bool(res.get("repaired")))
            if res.get("skipped"):                  # already in Oracle, nothing changed (Order Types)
                e["skipped"] = True
        elif it["state"] == "failed":
            saved, rid = saved_state(it)
            e.update(text=(it.get("ask") or {}).get("text") or res.get("text"),
                     todo=(it.get("ask") or {}).get("todo"), saved=saved, registry_id=rid)
        if it.get("question"):                      # Business Units: a refused value to decide on
            e["question"] = dict(it["question"])
        if it["state"] == "waiting" and it.get("held"):   # Price Lists: waits for its business unit
            e.update(held=True, text=it.get("hold_text"))
        view["items"].append(e)
    if sub and job["state"] in ("running", "repairing"):
        cur = next(it for it in items if it["state"] == "running")
        what = (cur.get("what") or job.get("what", "record")).capitalize()
        view["text"] = cur.get("batch_label") or f"{what} {cur['n']} of {n}: {cur['name']}"
        view["sub_text"] = sub.get("text")
        view["percent"] = int(((cur["n"] - 1) + (sub.get("percent") or 0) / 100) / n * 100)
        view["repairing"] = sub.get("state") == "repairing"
    failed = [it for it in items if it["state"] == "failed"]
    view["failed_sheet"] = any(saved_state(it)[0] == "no" for it in failed)
    skipped = sum(1 for e in view["items"] if e.get("skipped"))
    view["created"] = sum(1 for it in items if it["state"] == "done") - skipped
    if skipped:
        view["skipped"] = skipped
    view["words"] = job.get("words") or [job.get("what", "record")]
    view["questions"] = sum(1 for it in items if (it.get("question") or {}).get("state") in OPEN_Q)
    view["failed_name"] = failed_sheet_name(job)
    return view


def failed_sheet_name(job):
    """The failed-only sheet's file name: "Failed customers.xlsx" as before, "Failed order
    types.xlsx", or "Failed rows.xlsx" for a sheet of several modules."""
    words = job.get("words") or [job.get("what", "record")]
    return f"Failed {words[0]}s.xlsx" if len(words) == 1 else "Failed rows.xlsx"


def summary_view(run_id, job=None):
    """The "Run summary" (page/run_summary.py): the plain numbers and the sentences shown."""
    try:
        s = run_summary.summary(run_id, job)
    except Exception:  # noqa: BLE001 - the summary never breaks the result screen
        log(f"run summary for {run_id} failed: {traceback.format_exc()}")
        return None
    return {"numbers": s, "sections": run_summary.lines(s)} if s else None


def failed_sheet(job):
    """The upload's workbook with only the records that failed and saved nothing (their rows
    on the record tabs and their child rows), in the same layout."""
    u = UPLOADS.get(job.get("upload")) or {}
    keep, cells = {}, {}
    for it in job["items"]:
        if it["state"] == "failed" and saved_state(it)[0] == "no":
            for tab, row in [it["rows"]["record"]] + it["rows"]["children"]:
                keep.setdefault(tab, []).append(row)
            q = it.get("question")
            if q and q.get("tab"):                  # the refused value: Oracle's reason and the suggestions
                cells[(q["tab"], q["row"], workbook.norm(q["label"]))] = {
                    "value": q.get("answer") if q["state"] in ("open", "closed") and q.get("answer") else None,
                    "comment": f"Oracle refused '{q.get('value')}': {str(q.get('reason') or '').rstrip('. ')}."
                               + (f" Suggested: {', '.join(q['suggestions'])}." if q.get("suggestions") else "")
                               + (f" Your last answer '{q['answer']}' is written in the cell." if q.get("answer")
                                  and q["state"] in ("open", "closed") else "")}
    if not (keep and u.get("data")):
        return None
    if cells:                                       # only for runs with questions (Business Units)
        return workbook.subset_sheet(u["data"], keep, sheet_list, cells)
    return workbook.subset_sheet(u["data"], keep)


def ask_from_result(res):
    detail = (res.get("error") or {}).get("detail")
    problems = detail if isinstance(detail, list) else []
    return {"kind": "value", "text": res.get("text"),
            "problems": [{"field": p.get("field"), "row": p.get("row"), "text": p.get("text"),
                          "valid": p.get("valid")} for p in problems if isinstance(p, dict)]}


WHAT_TO_DO = {
    "NO_PERMISSION": "Ask your Oracle administrator to give your Oracle user access to this, then try again.",
    "PRODUCTION_REFUSED": "This page only makes changes in a test environment.",
    "SETUP_NEEDED": "Open the setup checklist and finish it, then try again.",
}


AFTER_FAILURE = {
    "value": "Change it in the sheet, save, and upload the sheet again.",
    "sign_in": "Upload the sheet again: the page renews the Oracle sign-in before Create.",
}


def fail_plain(job, res, text=None, todo=None, copy=False):
    """A run that ended without success: one plain card (what happened, what was and wasn't
    created, what to do next). Nothing asks the user anything during a run (2026-10-23)."""
    ask = {"kind": "stop", "text": text or res.get("text") or "Something went wrong.", "todo": todo}
    if copy:
        ask["copy"] = copy_message(job, res)
    update(job, state="failed", result=res, ask=ask)


def handle_result(job, res):
    """What happens after a run (or a repaired run) ended. No questions: a value Oracle
    refused, an expired sign-in or a stop is shown as a plain failure card; the sign-in is
    renewed at the preview, before Create, never in the middle of a run."""
    if res.get("ok"):
        update(job, state="done", result=res, percent=100, text=res.get("text"))
        log(f"job {job['id']} done: {res.get('text')}")
        return
    code = (res.get("error") or {}).get("code", "FAILED")
    if code in ASK_USER:
        fail_plain(job, res, todo=AFTER_FAILURE["value"])
    elif code == "SIGN_IN_NEEDED":
        fail_plain(job, res, todo=AFTER_FAILURE["sign_in"])
    elif code in STOP_PLAIN:
        fail_plain(job, res, todo=WHAT_TO_DO.get(code))
    else:
        repair(job, res)
        return
    log(f"job {job['id']} stopped ({code}): {res.get('text')}")


def worker():
    while True:
        jid = JOB_QUEUE.get()
        job = JOBS.get(jid)
        if not job:
            continue
        try:
            env = env_label()
            if not env["allowed"]:
                update(job, state="failed", ask={"kind": "stop", "text": WHAT_TO_DO["PRODUCTION_REFUSED"]})
                continue
            if job.pop("retry_repair", False):
                with ORACLE_LOCK:
                    repair(job, job["result"])
                continue
            update(job, state="running", text="Starting", percent=2)
            with ORACLE_LOCK:                          # one Oracle browser at a time (2026-10-26)
                if job.get("items"):
                    run_batch(job)
                else:
                    handle_result(job, run_folder(job))
        except Exception:  # noqa: BLE001
            log(f"job {jid} crashed:\n{traceback.format_exc()}")
            update(job, state="failed", ask={"kind": "stop", "text": "Something went wrong on this PC.",
                                             "todo": "Try again. If it happens again, restart the page."})


def retry_repair(job):
    """Start the automatic repair again for a run that stopped only because Claude
    wasn't signed in (the same request, queued like any run)."""
    if not job or job["state"] != "failed" or (job.get("ask") or {}).get("kind") != "claude":
        return
    update(job, state="queued", ask=None, retry_repair=True, text="Waiting for its turn")
    JOB_QUEUE.put(job["id"])
    log(f"job {job['id']}: repair queued again after the Claude sign-in")


def continue_after_signin(job):
    """The user pressed "Sign in to Oracle": sign in, then run the same request again (the
    folder skips anything that already exists, so nothing is made twice)."""
    update(job, state="signing", ask=None, text="Your Oracle sign-in has expired. " + SIGNIN_TEXT)

    def go():
        ok = oracle_signin()
        log(f"job {job['id']}: Oracle sign-in {'done' if ok else 'not finished'}")
        if not ok:
            update(job, state="needs_user", ask={"kind": "sign_in", "text": "The sign-in didn't finish. "
                                                 "Please try again; the task continues afterwards."})
            return
        update(job, state="queued", text="Signed in. Waiting for its turn")
        JOB_QUEUE.put(job["id"])
    threading.Thread(target=go, daemon=True).start()


# ---------------------------------------------------------------- automatic repair

RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["fixed", "no_change_needed", "needs_user", "failed"],
                   "description": "fixed = you changed the folder's code; no_change_needed = the cause "
                                  "was temporary; the server then runs the same request again"},
        "ask_kind": {"type": "string",
                     "enum": ["none", "sign_in", "value", "permission", "production", "outside_folder"]},
        "message": {"type": "string", "description": "plain words for the user, no technical terms"},
        "what_was_fixed": {"type": "string", "description": "for the log: files and what changed"},
        "already_created_before_repair": {"type": "string"},
    },
    "required": ["status", "ask_kind", "message"],
}

# Code a repair adds to a folder is refused when it touches credentials, the saved
# sign-in, the environment, or runs/sends anything new (checked before every rerun).
FORBIDDEN = [
    (r"\.env\b|dotenv|load_dotenv|dotenv_values", "the login file"),
    (r"\.session\b|state\.json|STATE_FILE|SESSION_DIR|storage_state", "the saved sign-in"),
    (r"ORACLE_(USER|PASS)|ALLOW_PROD|ORACLE_ENV|ORACLE_HOST", "login or environment settings"),
    (r"os\.environ|getenv|putenv", "the environment"),
    (r"\bsubprocess\b|os\.system|os\.popen|\bPopen\b|\bexec\s*\(|\beval\s*\(|__import__|importlib", "running other programs or code"),
    (r"^\s*(import|from)\s+(requests|urllib|http|socket|smtplib|ftplib|paramiko|httpx|aiohttp)\b",
     "a new network connection"),
    (r"\bshutil\.(rmtree|move)|os\.remove|os\.unlink|\.unlink\(|rmdir", "deleting files"),
]
CODE_SUFFIXES = {".py", ".ps1", ".psm1", ".cmd", ".bat", ".sh", ".js", ".vbs"}


def snapshot_folder(job, folder):
    """A copy of the folder (without _work/) taken before the repair: what the screen-look
    helper uses, what the edits are compared with, and what a refused edit goes back to."""
    snap = WORK / "repair_snapshots" / job["id"]
    if snap.exists():
        shutil.rmtree(snap)
    shutil.copytree(ROOT / folder, snap / folder, ignore=shutil.ignore_patterns("_work", "__pycache__"))
    return snap


def changed_files(snap, folder):
    """{relative path: (old text or None, new text or None)} for files the repair changed."""
    old_root, new_root = snap / folder, ROOT / folder
    names = set()
    for root in (old_root, new_root):
        for p in root.rglob("*"):
            rel = p.relative_to(root)
            if p.is_file() and "_work" not in rel.parts and "__pycache__" not in rel.parts:
                names.add(rel)
    out = {}
    for rel in sorted(names):
        a, b = old_root / rel, new_root / rel
        ta = a.read_text(encoding="utf-8", errors="replace") if a.exists() else None
        tb = b.read_text(encoding="utf-8", errors="replace") if b.exists() else None
        if ta != tb:
            out[str(rel)] = (ta, tb)
    return out


def check_edits(changes):
    """Problems in the code lines a repair added or changed (documentation is not code)."""
    problems = []
    for rel, (old, new) in changes.items():
        if Path(rel).suffix.lower() not in CODE_SUFFIXES:
            continue
        if new is None:
            problems.append(f"{rel}: the repair deleted a code file")
            continue
        before = set((old or "").splitlines())
        for n, line in enumerate(new.splitlines(), 1):
            if line in before:
                continue
            for pattern, what in FORBIDDEN:
                if re.search(pattern, line):
                    problems.append(f"{rel} line {n} ({what}): {line.strip()[:160]}")
    return problems


def restore_folder(snap, folder, changes):
    for rel, (old, new) in changes.items():
        target = ROOT / folder / rel
        if old is None:
            target.unlink(missing_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(snap / folder / rel, target)


def repair_permissions(folder):
    """Least privilege for one repair. Reading: the folder, common/, the root CLAUDE.md and
    the screen-look helper with its screenshots (not other folders). Editing: the folder
    only. Running: only page/look.py. Everything else is refused (dontAsk). Note: a rule
    like "./CLAUDE.md" also matches the folder's own CLAUDE.md (seen 2026-10-21), so edits
    are limited by the allow list alone, not by deny rules on file names."""
    look = "python page/look.py"
    allow = [f"Read(./{folder}/**)", "Read(./common/**)", "Read(./CLAUDE.md)",
             "Read(./page/look.py)", "Read(./page/_work/look/**)",
             f"Edit(./{folder}/**)", f"Write(./{folder}/**)",
             f"Bash({look}:*)", f"Bash({look} *)", f"PowerShell({look}:*)", f"PowerShell({look} *)"]
    deny = ["Read(./.env)", "Read(./.session/**)", "Read(./.session)",
            "Edit(./.env)", "Write(./.env)", "Edit(./.session/**)", "Write(./.session/**)",
            "Edit(./common/**)", "Write(./common/**)",
            "Edit(./page/**)", "Write(./page/**)", "Edit(./_template/**)", "Write(./_template/**)",
            "WebFetch", "WebSearch"]
    return {"permissions": {"allow": allow, "deny": deny, "defaultMode": "dontAsk"}}


def look_example(folder):
    """A look command for the folder, from its own CLAUDE.md task line when possible."""
    return (f'python page/look.py --folder "{folder}" --task "<task name>" --area "<functional area>" '
            f'--offering "<offering>" [--heading "<screen heading>"] [--label "<field label>"] '
            f'[--click "<link or tab text>"] [--buttons] [--text] [--screenshot <name>]')


def repair_prompt(job, res, attempt, history):
    folder = job["folder"]
    script = FOLDERS[folder]["script"]
    logtail = (LOGS / f"{job['id']}.log").read_text(encoding="utf-8", errors="replace")[-6000:]
    earlier = "\n".join(f"- attempt {i}: {h}" for i, h in enumerate(history, 1)) or "- none"
    return f"""You are repairing a failed run that the local page started. Attempt {attempt} of {REPAIR_ATTEMPTS}.

Configuration folder: "{folder}"   (script: {script})
The user's original request (Page interface --run JSON):
{json.dumps(job["request"], indent=1)}

The run's final result line (exact):
{json.dumps(res, indent=1)}

The end of the run's log (stderr of the folder's script):
{logtail}

Earlier repair attempts for this same run:
{earlier}

How this repair works: you find the cause and, if it is in the folder's code, fix it. You
do NOT run the folder's script yourself: when you are done, the page's server checks your
edits and then runs the same request again (the folder skips what already exists, so a
rerun never duplicates). Tell it with "status".

Rules (from the root CLAUDE.md; read it and "{folder}/CLAUDE.md" first, they apply in full):
- Work only inside "{folder}/" (Isolation rules, Self-repair rule). You may read the
  project, edit files inside "{folder}/" and its _work/, and look at Oracle's screens with
  the read-only helper (Bash tool):
    {look_example(folder)}
  It opens a task screen with the saved sign-in, reads labels / page text, lists the
  buttons and icons with their names and titles (--buttons), takes a screenshot
  (page/_work/look/<name>.png, view it with Read) and leaves without saving. It never
  types or saves. The task, area and offering are in "{folder}/CLAUDE.md". Use it to
  check the live screen before you change a selector. You can read "{folder}/",
  common/ and the root CLAUDE.md, not other folders. Use the Read, Grep and Glob tools
  (with a path inside those) rather than shell commands; the only command allowed is the
  helper above, run on its own (no "cd ... &&").
- Never read .env or .session/, never change ALLOW_PROD or ORACLE_ENV, nothing outside the
  project. Code you add must not touch the login file, the saved sign-in, environment
  settings, other programs, new network connections or deleting files: the server refuses
  such edits and puts the files back. If the fix would need a change in common/ or another
  folder, stop: status "needs_user", ask_kind "outside_folder", and say what and why.
- Never create a duplicate, never change or delete an existing record. Work out from the
  log and "{folder}/_work/" (fail_*.png / .txt) what the failed run already did.
- If the cause is in the folder's code (e.g. a changed Oracle screen), fix it there and add
  a dated line to "{folder}/CLAUDE.md" Known gotchas: status "fixed". If it was temporary
  (network, slowness, an environment problem on this PC that is gone now), change nothing:
  status "no_change_needed". Never change the request's values.
- Stop and ask (status "needs_user") only for: an expired Oracle sign-in or MFA
  (ask_kind "sign_in"), a value Oracle doesn't have ("value", name the valid ones), a
  missing permission ("permission"), production ("production"), or a fix outside the
  folder ("outside_folder"). Otherwise "failed" with what you found.
- message: one or two short sentences in plain, friendly words for a non-technical user
  (no file names, commands or technical terms).
"""


def stop_ask(job, kind, text, res):
    """The repair says the user must act: shown as a plain failure card (no questions mid-run)."""
    todo = {"sign_in": AFTER_FAILURE["sign_in"], "value": AFTER_FAILURE["value"],
            "permission": WHAT_TO_DO["NO_PERMISSION"], "production": WHAT_TO_DO["PRODUCTION_REFUSED"],
            "outside_folder": "This needs a change that Claude may not make on its own. Ask the person "
                              "who looks after this project."}.get(kind)
    fail_plain(job, res, text=" ".join(x for x in (res.get("text"), text) if x), todo=todo,
               copy=kind == "outside_folder")


def copy_message(job, res):
    return (f'The page run of "{job["folder"]}" failed and couldn\'t be repaired automatically. '
            f"Please repair the folder and finish the same request without creating duplicates.\n"
            f"Request: {json.dumps(job['request'])}\n"
            f"Error: {(res.get('error') or {}).get('code')} - {res.get('text')}\n"
            f"Detail: {str((res.get('error') or {}).get('detail'))[:800]}")


def repair(job, res):
    """Up to REPAIR_ATTEMPTS rounds within REPAIR_MINUTES: Claude finds the cause and fixes
    the folder (or says it was temporary); the server checks every edited code line, then
    reruns the same request itself. A refused edit is put back and the run stops."""
    st = claude_status()
    if not st["installed"]:
        # Automatic fixes are off on this PC (the tool couldn't be installed): a plain error
        # and a message to copy, nothing else.
        update(job, state="failed", result=res, ask={
            "kind": "stop", "text": "A problem stopped the run. Automatic fixes are switched off on this "
            "computer, so it couldn't be fixed by itself.", "todo": "Copy the message below and paste it "
            "into Claude, or give it to the person who looks after this project.",
            "copy": copy_message(job, res)})
        log(f"job {job['id']}: repair not possible (Claude's tool isn't installed on this PC)")
        return
    if not st["signed_in"]:
        # No question mid-run: a plain card; the sign-in to Claude is offered on the page's
        # header and setup checklist, not here (2026-10-23).
        fail_plain(job, res, text=f"{res.get('text') or 'A problem stopped the run.'} It couldn't be "
                   "fixed automatically because Claude isn't signed in on this computer.",
                   todo="Sign in to Claude (button at the top of the page) for automatic fixes next "
                        "time, or copy the message below and paste it into Claude.", copy=True)
        log(f"job {job['id']}: repair not possible (Claude's tool installed={st['installed']}, "
            f"signed in={st['signed_in']})")
        return
    cmd0 = claude_command(find_claude())
    folder = job["folder"]
    WORK.mkdir(parents=True, exist_ok=True)
    settings = WORK / f"repair_settings_{job['id']}.json"
    settings.write_text(json.dumps(repair_permissions(folder)), encoding="utf-8")
    started, history, total_cost, fixed_note = time.time(), [], 0.0, None
    for attempt in range(1, REPAIR_ATTEMPTS + 1):
        left = REPAIR_MINUTES * 60 - (time.time() - started)
        if left < 60:
            break
        update(job, state="repairing", repairs=attempt, percent=max(job["percent"], 10),
               text="Fixing a small problem" + (f" (try {attempt})" if attempt > 1 else ""))
        snap = snapshot_folder(job, folder)
        cmd = cmd0 + ["-p", "--output-format", "stream-json", "--verbose",
                      "--json-schema", json.dumps(RESULT_SCHEMA),
                      "--permission-mode", "dontAsk", "--permission-prompts", "none",
                      "--settings", str(settings), "--strict-mcp-config", "--no-chrome",
                      "--max-budget-usd", str(REPAIR_BUDGET_USD), "--no-session-persistence"]
        out, cost = run_claude(job, cmd, repair_prompt(job, res, attempt, history), left, snap)
        total_cost += cost
        status = out.get("status")
        changes = changed_files(snap, folder)
        log(f"job {job['id']} repair attempt {attempt}: cost ${cost:.4f} (this run ${total_cost:.4f}), "
            f"status {status}, changed {sorted(changes) or 'nothing'}: {out.get('message')}")
        problems = check_edits(changes)
        if problems:
            restore_folder(snap, folder, changes)
            log(f"job {job['id']}: repair edits REFUSED and put back:\n  " + "\n  ".join(problems))
            update(job, state="failed", result=res, ask={
                "kind": "stop", "text": "The automatic fix tried a change that isn't allowed, so it "
                "was undone and nothing was run.", "todo": "Ask the person who looks after this "
                "project, or copy the message below and paste it into Claude.",
                "copy": copy_message(job, res)})
            return
        if status == "needs_user":
            stop_ask(job, out.get("ask_kind"), out.get("message"), res)
            return
        if status not in ("fixed", "no_change_needed"):
            history.append(out.get("message") or out.get("error") or "no result")
            continue
        fixed_note = out.get("message") or fixed_note
        update(job, state="repairing", text="Fixing a small problem: trying again")
        new = run_folder(job)
        log(f"job {job['id']}: rerun after repair attempt {attempt}: "
            f"{'ok' if new.get('ok') else (new.get('error') or {}).get('code')} - {new.get('text')}")
        code = (new.get("error") or {}).get("code", "FAILED")
        if new.get("ok") or code in ASK_USER | STOP_PLAIN | {"SIGN_IN_NEEDED"}:
            if new.get("ok"):
                new = dict(new, repaired=fixed_note)
            log(f"job {job['id']}: repair finished, total cost ${total_cost:.4f}")
            handle_result(job, new)
            return
        history.append(f"{out.get('message')} -> the rerun still failed: {new.get('text')}")
        res = new
    log(f"job {job['id']}: repair gave up after {len(history)} attempt(s), total cost ${total_cost:.4f}")
    fail_plain(job, res, text=f"{res.get('text') or 'A problem stopped the run.'} It couldn't be "
               "fixed automatically.", todo="Copy the message below and paste it into Claude, or ask "
               "the person who looks after this project.", copy=True)


def run_claude(job, cmd, prompt, timeout, snap):
    """Run one repair; returns (structured result, cost in USD). PAGE_LOOK_SNAPSHOT makes
    the screen-look helper open screens with the folder's pre-repair code."""
    logf = LOGS / f"{job['id']}.repair.log"
    result, cost = {}, 0.0
    env = dict(os.environ, PAGE_LOOK_SNAPSHOT=str(snap), PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    try:
        with logf.open("a", encoding="utf-8") as lf:
            lf.write(f"\n===== repair {datetime.now():%H:%M:%S}\n")
            p = subprocess.Popen(cmd, cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=lf, text=True, encoding="utf-8", errors="replace", env=env)
            p.stdin.write(prompt)
            p.stdin.close()
            timer = threading.Timer(timeout, p.kill)
            timer.start()
            for line in p.stdout:
                lf.write(line)
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if ev.get("type") == "result":
                    cost = float(ev.get("total_cost_usd") or 0)
                    out = ev.get("structured_output")
                    if not isinstance(out, dict):
                        try:
                            txt = ev.get("result") or ""
                            out = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
                        except ValueError:
                            out = {"status": "failed", "message": "", "error": str(ev.get("result"))[:300]}
                    result = out
                elif ev.get("type") == "assistant":       # what Claude is doing, in plain words
                    for c in (ev.get("message") or {}).get("content", []) or []:
                        if c.get("type") == "tool_use" and "look.py" in json.dumps(c.get("input")):
                            update(job, text="Fixing a small problem: looking at the Oracle screen")
            p.wait()
            timer.cancel()
    except Exception as e:  # noqa: BLE001
        log(f"job {job['id']}: repair run error: {e}")
        result = {"status": "failed", "message": "", "error": str(e)}
    return result, cost


# ---------------------------------------------------------------- HTTP

def ago(iso):
    try:
        secs = (datetime.now(timezone.utc) - datetime.fromisoformat(iso)).total_seconds()
    except (TypeError, ValueError):
        return None
    return int(max(secs, 0))


class Handler(http.server.BaseHTTPRequestHandler):
    server_version = "ConfigPage/1"

    def log_message(self, fmt, *args):   # quiet: the server log has what matters
        pass

    def allowed(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    def send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else (
            json.dumps(body).encode("utf-8") if ctype == "application/json" else body.encode("utf-8"))
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if "text" in ctype or "json" in ctype else ""))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def raw_body(self, limit):
        n = int(self.headers.get("Content-Length") or 0)
        if n > limit:
            self.rfile.read(n)
            return None
        return self.rfile.read(n)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return {}

    def do_GET(self):
        if not self.allowed():
            return self.send(403, {"error": "local only"})
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        path = u.path
        if path in ("/", "/index.html"):
            return self.send(200, (STATIC / "index.html").read_bytes(), "text/html")
        if path.startswith("/static/"):
            f = (STATIC / path[len("/static/"):]).resolve()
            if STATIC in f.parents and f.exists():
                ctype = {".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml"}.get(
                    f.suffix, "application/octet-stream")
                return self.send(200, f.read_bytes(), ctype)
            return self.send(404, {"error": "not found"})
        if path == "/api/today":
            return self.send(200, {"today": oracle_today()})
        if path == "/api/state":
            env = env_label()
            return self.send(200, {"env": env, "setup_complete": setup_quick(),
                                   "test_mode": TEST_MODE["on"], "claude": claude_status_cached()})
        if path == "/api/setup":
            with LOCK:
                steps = [dict(d, **SETUP["steps"][d["key"]]) for d in STEP_DEFS]
                return self.send(200, {"steps": steps, "running": SETUP["running"],
                                       "complete": SETUP["complete"], "env": env_label()})
        if path == "/api/spec":
            f = FOLDERS.get(q.get("folder", ""))
            if not f or not f["spec"]:
                return self.send(404, {"error": "unknown folder"})
            return self.send(200, f["spec"])
        if path == "/api/sheet/modules":                   # the Upload screen's module cards per area (2026-10-30)
            reg = workbook.load_registry()
            return self.send(200, {"areas": workbook.areas(), "default": workbook.DEFAULT_AREA, "modules": [
                {"name": g["name"], "area": workbook.area_of_group(g), "record": g.get("record", "record"),
                 "tabs": list(g["record_tabs"]) + list(g["child_tabs"])} for g in reg["groups"]]})
        if path == "/api/sheet/template":                  # "Download the empty sheet"
            # ?area= (2026-10-30, the Order Management | Receivables switch): only that area's tabs; without it every tab
            area = q.get("area") if q.get("area") in workbook.areas() else None
            try:
                data = workbook.make_template(sheet_list, area=area)    # live drop-downs ("values_live", 2026-10-26)
            except ImportError:
                return self.send(503, {"error": "The helper for Excel files is missing; restart the page."})
            fname = "Upload sheet.xlsx" if area in (None, workbook.DEFAULT_AREA) else f"Upload sheet - {area}.xlsx"
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)
            return
        m = re.match(r"^/api/summary/(\w+)$", path)     # the Run summary of a run, also an older one
        if m:
            sv = summary_view(m.group(1), JOBS.get(m.group(1)))
            return self.send(200 if sv else 404, sv or {"error": "unknown run"})
        m = re.match(r"^/api/sheet/(\w+)$", path)
        if m:
            if m.group(1) not in UPLOADS:
                return self.send(404, {"error": "unknown upload"})
            return self.send(200, upload_view(m.group(1)))
        if path.startswith("/api/job/"):
            job = JOBS.get(path.split("/")[3])
            if not job:
                return self.send(404, {"error": "unknown run"})
            if path.endswith("/failed.xlsx"):              # "Download a sheet with only the failed customers"
                data = failed_sheet(job) if job.get("items") and job["state"] in ("done", "failed", "asking") else None
                if not data:
                    return self.send(404, {"error": "no failed rows"})
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                self.send_header("Content-Disposition", f'attachment; filename="{failed_sheet_name(job)}"')
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(data)
                return
            with LOCK:
                view = {k: job.get(k) for k in ("id", "folder", "title", "upload", "state", "step",
                                                "percent", "text", "result", "ask", "repairs")}
                view["done_lines"] = job.get("done_lines") or []
                if job.get("items"):
                    view.update(batch_view(job))
            if job.get("items") and view["state"] in ("done", "failed", "asking"):
                view["summary"] = summary_view(job["id"], job)
            if view["state"] == "queued":
                view["ahead"] = queue_position(job)
            return self.send(200, view)
        return self.send(404, {"error": "not found"})

    def do_POST(self):
        if not self.allowed():
            return self.send(403, {"error": "local only"})
        path = urlparse(self.path).path
        if path == "/api/sheet/upload":                    # the file itself, read and checked here
            data = self.raw_body(workbook.MAX_BYTES)
            name = re.sub(r"[^\w .()-]+", "_", self.headers.get("X-File-Name") or "sheet.xlsx")[:120]
            if data is None:
                return self.send(200, {"ok": False, "stops": ["This file is too big (more than 10 MB). "
                                                              "Please upload the sheet only."]})
            uid, _ = check_upload(data, name)
            return self.send(200, upload_view(uid))
        if path == "/api/sheet/peek":                      # which modules have rows (offline, a moment)
            data = self.raw_body(workbook.MAX_BYTES)
            try:
                mods = offline_check(data or b"").get("modules") or []
            except Exception:  # noqa: BLE001 - the upload itself gives the plain answer
                mods = []
            return self.send(200, {"modules": [{"name": m["name"], "record": m["record"], "count": m["count"]}
                                               for m in mods if m["count"]]})
        body = self.body()
        if path == "/api/setup/start":
            if body.get("from") or not SETUP["complete"]:
                setup_start(body.get("from"))
            return self.send(200, {"ok": True})
        if path == "/api/setup/action":
            key = body.get("step")
            st = SETUP["steps"].get(key, {})
            if key == "claude" and body.get("skip"):                  # "Continue without automatic fixes"
                claude_skip()
            elif st.get("opened") or key in ("connection", "look"):     # "Continue" / "Try again"
                setup_start(key)
            else:
                setup_action(key)
            return self.send(200, {"ok": True})
        if path == "/api/sheet/create":
            # "Create in Oracle": the checked upload's record goes to its folder's --run. Nothing
            # was sent to Oracle before this; one press per upload (a second gets the same run).
            uid = body.get("upload")
            if uid not in UPLOADS:
                return self.send(404, {"error": "unknown upload"})
            if not env_label()["allowed"]:
                return self.send(403, {"error": "production"})
            with LOCK:
                u = UPLOADS[uid]
                if u["job"]:
                    return self.send(200, {"id": u["job"]})
                if not (u["preview"] or {}).get("ok"):
                    return self.send(400, {"error": "not ready"})
                u["job"] = "checking"
            # The sign-in once more right before the run (it may have expired while the preview
            # was open): renewed here, at the preview, never during the run (2026-10-23).
            if needs_signin(u["preview"]["records"]) and not session_valid().get("valid"):
                with LOCK:
                    u["job"] = None
                    u["preview"] = dict(u["preview"], ok=False, signin="waiting")
                threading.Thread(target=signin_then_check, args=(uid,), daemon=True).start()
                return self.send(200, {"signin": True})
            with LOCK:
                recs = u["preview"]["records"]
                u["job"] = "pending"
            job = new_batch(recs, uid, body.get("force_failure"))
            with LOCK:
                u["job"], job["upload"] = job["id"], uid
            return self.send(200, {"id": job["id"]})
        if path == "/api/claude/signin":
            jid = body.get("job")
            started = claude_signin(jid if jid in JOBS else None)
            return self.send(200, {"ok": started})
        m = re.match(r"^/api/sheet/(\w+)/signin$", path)          # the preview's sign-in, again
        if m and m.group(1) in UPLOADS:
            with LOCK:
                u = UPLOADS[m.group(1)]
                u["preview"] = dict(u["preview"], signin="waiting")
            threading.Thread(target=signin_then_check, args=(m.group(1),), daemon=True).start()
            return self.send(200, {"ok": True})
        m = re.match(r"^/api/job/(\w+)/answer$", path)            # a question's answer (Business Units)
        if m and m.group(1) in JOBS:
            try:
                n = int(body.get("n"))
            except (TypeError, ValueError):
                return self.send(400, {"ok": False, "text": "Which question?"})
            return self.send(200, answer_question(JOBS[m.group(1)], n, body.get("value"), bool(body.get("skip"))))
        m = re.match(r"^/api/job/(\w+)/signin$", path)
        if m and m.group(1) in JOBS:
            continue_after_signin(JOBS[m.group(1)])
            return self.send(200, {"ok": True})
        return self.send(404, {"error": "not found"})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--open", action="store_true", help="open the page in the default browser")
    ap.add_argument("--test-mode", action="store_true", help="offer a switch that makes one run fail")
    ap.add_argument("--simulate-claude-blocked", action="store_true",
                    help="test: act as if every way to install Claude's tool were blocked on this PC")
    args = ap.parse_args()
    TEST_MODE["on"] = args.test_mode
    if args.simulate_claude_blocked:
        os.environ["CONFIG_AUTOMATION_SIMULATE_BLOCKED"] = "1"
        ENV_CHILD["CONFIG_AUTOMATION_SIMULATE_BLOCKED"] = "1"
    # Per-user installs of Claude's tool (tools folder, ~/.local/bin): on the PATH of this
    # page's own processes only; the PATH of the PC and of the user is never changed.
    claude_tool.add_to_path(os.environ)
    claude_tool.add_to_path(ENV_CHILD)
    WORK.mkdir(parents=True, exist_ok=True)
    try:
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        print(f"The page can't start: something else already uses port {args.port}. "
              f"If the page is already open, use http://127.0.0.1:{args.port}", flush=True)
        sys.exit(1)
    url = f"http://127.0.0.1:{args.port}"
    log(f"page started at {url} (environment {env_label()['name'] or 'not set'})")
    threading.Thread(target=load_folders, daemon=True).start()
    threading.Thread(target=worker, daemon=True).start()
    setup_start()          # every start: the checklist, then the saved Oracle sign-in (window if needed)
    if args.open:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
