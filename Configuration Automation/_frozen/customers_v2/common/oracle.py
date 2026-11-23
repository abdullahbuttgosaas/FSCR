"""Shared helpers for Oracle Fusion setup-task CSV export/import.

Only proven, documented endpoints are used here (see the root CLAUDE.md).
Every failure prints the exact error and stops. The target is chosen by
ORACLE_HOST and labelled by ORACLE_ENV; production needs ALLOW_PROD=yes.
"""
import base64
import csv
import io
import os
import shutil
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORK_DIR_NAME = "_work"
# Set by init_work_dir(); every temporary file goes here, never elsewhere.
WORK_DIR = None


def init_work_dir(config_dir):
    """Use <config folder>/_work/ for this run's temporary files."""
    global WORK_DIR
    config_dir = Path(config_dir).resolve()
    if config_dir.parent != PROJECT_ROOT:
        fail(f"{config_dir} is not a configuration folder at the project root.")
    WORK_DIR = config_dir / WORK_DIR_NAME
    if WORK_DIR.exists() and any(WORK_DIR.iterdir()):
        print(f"Note: {WORK_DIR} already has files from an earlier run; "
              "they are deleted only if this run is verified successfully.")
    WORK_DIR.mkdir(exist_ok=True)
    return WORK_DIR


def _work_dir():
    if WORK_DIR is None:
        fail("init_work_dir() must be called before writing files.")
    return WORK_DIR


def cleanup_work_dir():
    """Delete <config>/_work/ after a verified success. Deletes nothing else."""
    w = WORK_DIR
    if w is None or not w.exists():
        return
    w = w.resolve()
    if w.name != WORK_DIR_NAME or w.parent.parent != PROJECT_ROOT:
        fail(f"Refusing to delete {w}: not a <config>/{WORK_DIR_NAME} folder.")
    shutil.rmtree(w)
    print(f"Cleaned up {w}")


def _find_env_file():
    """Search upward from the running script's folder for a .env file."""
    starts = []
    if sys.argv and sys.argv[0]:
        starts.append(Path(sys.argv[0]).resolve().parent)
    starts.append(PROJECT_ROOT)
    for start in starts:
        for folder in (start, *start.parents):
            candidate = folder / ".env"
            if candidate.is_file():
                return candidate
    return None


# Real environment variables win over the file (override=False).
_env_file = _find_env_file()
if _env_file:
    load_dotenv(_env_file, override=False, encoding="utf-8-sig")  # Notepad may add a BOM

HOST = os.environ.get("ORACLE_HOST", "").strip().rstrip("/")
ORACLE_ENV = os.environ.get("ORACLE_ENV", "").strip()
API_BASE = f"{HOST}/fscmRestApi/resources/11.13.18.05"
PROD_LABELS = ("prod", "production")

POLL_SECONDS = 10
POLL_TIMEOUT_SECONDS = 30 * 60
DONE_STATUSES = ("COMPLETED", "COMPLETED_WARNINGS", "COMPLETED_ERRORS")
RUNNING_STATUSES = ("NOT_STARTED", "IN_PROGRESS")


def fail(message):
    print(f"\nERROR: {message}", file=sys.stderr)
    if WORK_DIR is not None and WORK_DIR.exists() and any(WORK_DIR.iterdir()):
        print(f"Files kept for inspection in: {WORK_DIR}", file=sys.stderr)
    sys.exit(1)


_ENV_CHECKED = False


def check_environment():
    """Print host and ORACLE_ENV, then enforce the environment rules.

    ORACLE_ENV is an explicit label (dev, test, uat, sit, prod or custom).
    prod/production also needs ALLOW_PROD=yes. No hostname pattern matching.
    """
    global _ENV_CHECKED
    if _ENV_CHECKED:
        return
    print(f"Host: {HOST or '(ORACLE_HOST not set)'}")
    print(f"ORACLE_ENV: {ORACLE_ENV or '(not set)'}")
    if not ORACLE_ENV:
        fail("ORACLE_ENV is not set. Add a line like ORACLE_ENV=test to the .env file "
             "in the project root (dev, test, uat, sit, prod or your own label).")
    if not HOST:
        fail("ORACLE_HOST is not set. Add ORACLE_HOST=https://<your-pod> to .env.")
    if ORACLE_ENV.lower() in PROD_LABELS and os.environ.get("ALLOW_PROD", "").strip().lower() != "yes":
        fail(f"Refusing to run: ORACLE_ENV is '{ORACLE_ENV}'. Running against production "
             "requires ALLOW_PROD=yes in .env, set by you, not by Claude.")
    _ENV_CHECKED = True


def _session():
    check_environment()
    user = os.environ.get("ORACLE_USER")
    password = os.environ.get("ORACLE_PASS")
    if not user or not password:
        fail("ORACLE_USER and ORACLE_PASS must be set (in .env at the project root "
             "or as environment variables).")
    s = requests.Session()
    s.auth = (user, password)
    # No global Accept header: enclosure downloads return 406 with
    # "Accept: application/json" (proven 2026-10-15).
    return s


_SESSION = None


def session():
    global _SESSION
    if _SESSION is None:
        _SESSION = _session()
    return _SESSION


def call(method, url, **kwargs):
    """Make one HTTP call; on any failure print the exact error and stop."""
    kwargs.setdefault("timeout", 300)
    try:
        r = session().request(method, url, **kwargs)
    except requests.RequestException as e:
        fail(f"{method} {url}\n{type(e).__name__}: {e}")
    if not r.ok:
        fail(f"{method} {url}\nHTTP {r.status_code} {r.reason}\n{r.text}")
    return r


def rest(method, path, timeout=120, **kwargs):
    """Call API_BASE/<path> (direct REST resources) and return the parsed JSON."""
    r = call(method, f"{API_BASE}/{path}", timeout=timeout, **kwargs)
    return r.json() if r.content else {}


def rest_items(path, **params):
    """GET a collection (onlyData) and return its items list."""
    params.setdefault("onlyData", "true")
    params.setdefault("limit", 100)
    return rest("GET", path, params=params).get("items", [])


def try_call(method, url, **kwargs):
    """Like call(), but never stops the run: returns (response, None) on success or
    (response_or_None, "exact error text") on failure, so a script can switch to a
    fallback route. The error text is what call() would have printed."""
    kwargs.setdefault("timeout", 300)
    try:
        r = session().request(method, url, **kwargs)
    except requests.RequestException as e:
        return None, f"{method} {url}\n{type(e).__name__}: {e}"
    if not r.ok:
        return r, f"{method} {url}\nHTTP {r.status_code} {r.reason}\n{r.text[:2000]}"
    return r, None


def link_href(item, name, rel=None):
    """The href of a link Oracle returned in a REST item (e.g. a child collection),
    so no URL is ever built by hand. None when the item has no such link."""
    for link in item.get("links", []):
        if link.get("name") == name and (rel is None or link.get("rel") == rel):
            return link.get("href")
    return None


def server_date(response):
    """Oracle's own date from a REST response's Date header (the server's clock, UTC),
    as a datetime.date. Never the PC clock."""
    from email.utils import parsedate_to_datetime
    value = response.headers.get("Date") if response is not None else None
    if not value:
        fail("Oracle's response has no Date header to read Oracle's today from.")
    return parsedate_to_datetime(value).date()


def task_url(kind, task_code):
    """kind is 'Export' or 'Import'."""
    return f"{API_BASE}/setupTaskCSV{kind}s/{task_code}"


def process_urls(kind, task_code, process_id):
    proc = f"{task_url(kind, task_code)}/child/SetupTaskCSV{kind}Process"
    # The result collection comes back empty; only the item URL by id works.
    result = f"{proc}/{process_id}/child/SetupTaskCSV{kind}ProcessResult/{process_id}"
    return proc, result


def export_supported(task_code):
    """GET setupTaskCSVExports/<task> and return ExportSupportedFlag."""
    data = call("GET", task_url("Export", task_code)).json()
    return data.get("ExportSupportedFlag"), data


def poll_result(result_url, label):
    """Poll a process result item every 10s until it finishes."""
    start = time.time()
    while True:
        time.sleep(POLL_SECONDS)
        data = call("GET", result_url).json()
        status = data.get("StatusCode")
        elapsed = int(time.time() - start)
        print(f"  [{label}] {elapsed:>4}s  StatusCode={status}")
        if status in DONE_STATUSES:
            return data
        if status not in RUNNING_STATUSES:
            fail(f"Unexpected StatusCode '{status}' from {result_url}\n{data}")
        if elapsed > POLL_TIMEOUT_SECONDS:
            fail(f"Timed out after {elapsed}s waiting for {result_url}")


def _save_result_attachments(result, prefix):
    """Download log/report attachments using the links Oracle returned."""
    saved = []
    for link in result.get("links", []):
        name = link.get("name", "")
        if link.get("rel") == "enclosure" and name in (
                "ProcessLog", "ProcessResultsReport", "ProcessResultsSummaryReport"):
            r = call("GET", link["href"])
            path = _work_dir() / f"{prefix}_{name}"
            path.write_bytes(r.content)
            saved.append(path)
    return saved


def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_work_file(data, task_code, tag):
    path = _work_dir() / f"{task_code}_{stamp()}_{tag}.zip"
    path.write_bytes(data)
    return path


def export_task(task_code, tag="export"):
    """Run a CSV export for a setup task; return (zip bytes, saved path)."""
    print(f"Exporting {task_code} ...")
    proc_url, _ = process_urls("Export", task_code, 0)
    r = call("POST", proc_url, json={"TaskCode": task_code})
    pid = r.json().get("ProcessId")
    if pid is None:
        fail(f"No ProcessId in export response:\n{r.text}")
    print(f"  ProcessId={pid}")
    _, result_url = process_urls("Export", task_code, pid)
    result = poll_result(result_url, "export")
    if result.get("StatusCode") != "COMPLETED":
        saved = _save_result_attachments(result, f"{task_code}_{pid}_export")
        fail(f"Export finished with {result.get('StatusCode')}.\n{_strip(result)}"
             + "".join(f"\n  saved {p}" for p in saved))
    data = call("GET", f"{result_url}/enclosure/FileContent").content
    if not zipfile.is_zipfile(io.BytesIO(data)):
        fail(f"Export download is not a zip ({len(data)} bytes): {data[:300]!r}")
    path = save_work_file(data, task_code, tag)
    print(f"  saved {path}")
    return data, path


def import_task(task_code, zip_bytes):
    """Run a CSV import for a setup task; return the final result item."""
    print(f"Importing {task_code} ({len(zip_bytes)} bytes) ...")
    proc_url, _ = process_urls("Import", task_code, 0)
    body = {"TaskCode": task_code,
            "FileContent": base64.b64encode(zip_bytes).decode(),
            "SourceTargetDiffOkFlag": True}
    r = call("POST", proc_url, json=body)
    pid = r.json().get("ProcessId")
    if pid is None:
        fail(f"No ProcessId in import response:\n{r.text}")
    print(f"  ProcessId={pid}")
    _, result_url = process_urls("Import", task_code, pid)
    result = poll_result(result_url, "import")
    status = result.get("StatusCode")
    if status != "COMPLETED":
        saved = _save_result_attachments(result, f"{task_code}_{pid}_import")
        msg = (f"Import finished with {status}.\n{_strip(result)}"
               + "".join(f"\n  saved {p}" for p in saved))
        if status == "COMPLETED_ERRORS":
            fail(msg)
        print(f"WARNING: {msg}")
    return result


def _strip(result):
    """Result item without the bulky links list, for printing."""
    return {k: v for k, v in result.items() if k != "links"}


# ---------------------------------------------------------------- CSV helpers

def find_member(z, suffix):
    names = [n for n in z.namelist() if n.endswith(suffix)]
    if len(names) != 1:
        fail(f"Expected exactly one '{suffix}' in the zip, found {names}")
    return names[0]


def read_csv(z, name):
    """Return (header, rows) for a CSV inside an open ZipFile."""
    rows = list(csv.reader(io.StringIO(z.read(name).decode("utf-8-sig"))))
    if not rows:
        fail(f"{name} is empty")
    return rows[0], rows[1:]


def write_csv(header, rows):
    """Fully quoted CSV with \\n line endings, as Oracle accepts it."""
    buf = io.StringIO()
    w = csv.writer(buf, quoting=csv.QUOTE_ALL, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def build_zip(members):
    """members: {name: bytes}. Each name appears exactly once."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zo:
        for name, data in members.items():
            zo.writestr(name, data)
    return buf.getvalue()
