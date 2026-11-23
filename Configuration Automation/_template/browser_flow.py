"""<Configuration name>: create records from request.json through the Oracle UI, then verify.

TEMPLATE - copy the whole _template/ folder to a new folder at the project root,
rename request.json, and fill in every TODO. Keep the three modes:

  python "<Folder>/browser_flow.py" --check     # read-only: screens + values, nothing created
  python "<Folder>/browser_flow.py"             # full run (headless)
  python "<Folder>/browser_flow.py" --headed    # same, browser visible

and the three page commands (root CLAUDE.md > Page interface, common/page.py):

  python "<Folder>/browser_flow.py" --spec                 # the form, as JSON
  python "<Folder>/browser_flow.py" --options FIELD        # live values of a pick list
  python "<Folder>/browser_flow.py" --run '{"name": "..."}'  # one request, JSON progress lines

Rules (root CLAUDE.md): this folder imports only common/ (never another folder);
common/ is additive only, so behavior this folder needs differently lives here.
Every step has a timeout (OracleUI waits are 60 s by default; ui.step() names the
step on failure and keeps a screenshot in _work/). "today" in a request = Oracle's
today (read from the screen, never the PC clock) minus one day.
"""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from common import browser, oracle, page  # noqa: E402

OFFERING, AREA, TASK = "TODO offering", "TODO functional area", "TODO task name"
TODAY = "today"
HERE = Path(__file__).resolve().parent

# The form for the page (root CLAUDE.md > Page interface). One entry per request key,
# the same keys and defaults as the Input rules in CLAUDE.md. Plain words only.
SPEC = {
    "title": "TODO Create a <thing>",
    "description": "TODO One line: what this creates in Oracle.",
    "fields": [
        {"key": "name", "label": "Name", "required": True, "type": "text",
         "placeholder": "ZZ_TEST_1234", "default": None},
        # TODO every Input rules field, e.g.
        # {"key": "start_date", "label": "Start date", "required": True, "type": "date",
        #  "placeholder": "2026-10-21", "default": None},
        # {"key": "business_unit", "label": "Business unit", "required": False,
        #  "type": "pick", "placeholder": "ABD", "default": None},
        # A repeating group (the request sends a list of objects):
        # {"key": "installments", "label": "Installments", "required": True, "type": "rows",
        #  "min_rows": 1, "add_label": "Add an installment", "row_label": "Installment",
        #  "fields": [
        #      {"key": "percent", "label": "Percent due", "required": True, "type": "number",
        #       "placeholder": "50"},
        #      {"key": "days", "label": "Days", "required": True, "type": "number",
        #       "placeholder": "30"}]},
    ],
}


# ---------------------------------------------------------------- requirements

def load_requirements(path):
    """Validate the request file against the Input rules in CLAUDE.md."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        oracle.fail(f"Cannot read {path}: {e}")
    records = data.get("records")
    if not isinstance(records, list) or not records:
        oracle.fail(f"{path} must contain a non-empty 'records' list")
    for r in records:
        if not r.get("name"):
            oracle.fail("Every record needs a 'name'. Ask the user in one plain message.")
        # TODO: every REQUIRED field from the Input rules; reject unknown keys.
    return records


# ---------------------------------------------------------------- steps

def exists(ui, record):
    """TODO: read-only existence check (search on screen or fresh export)."""
    raise NotImplementedError


def check_screens(ui):
    """TODO: open every screen the full run uses and leave each with Cancel (or use
    ui.check_actions(TASK, AREA, OFFERING) for an export/import task)."""
    raise NotImplementedError


def create(ui, record):
    """TODO: fill and save one record. Never change or delete an existing one."""
    raise NotImplementedError


def verify(ui, record):
    """TODO: read every requested value (and the defaults) back from Oracle and
    print OK/FAIL per value. Return True only if all match."""
    raise NotImplementedError


def run_records(records, headed=False, progress=None):
    """The normal flow, shared by the command line and --run. Returns
    {name: "created" | "skipped"}; stops (oracle.fail) if verification fails."""
    work = oracle.init_work_dir(HERE)
    outcome, all_ok = {}, True
    with browser.OracleUI(work, headless=not headed) as ui:
        for r in records:
            if exists(ui, r):
                print(f"  SKIP  {r['name']}: already exists - not touched")
                outcome[r["name"]] = "skipped"
                continue
            if progress:
                progress.step("creating")
            with ui.step(f"create {r['name']}"):
                create(ui, r)
            if progress:
                progress.step("verifying")
            all_ok &= verify(ui, r)
            outcome[r["name"]] = "created"
    if not all_ok:
        oracle.fail("Verification failed - see FAIL lines above.")
    oracle.cleanup_work_dir()
    return outcome


# ---------------------------------------------------------------- page commands

def options_for(key):
    """Live values of a pick-from-a-list field, read by this folder's own route
    (REST where possible): [{"value": <what the request sends>, "label": <plain name>}].
    A pick sub-field of a rows field comes as "<rows key>.<sub key>"."""
    oracle.check_environment()
    # TODO e.g. if key == "business_unit": return [{"value": i["BusinessUnitName"],
    #   "label": i["BusinessUnitName"]} for i in oracle.rest_items("finBusinessUnitsLOV", ...)]
    raise page.PageError("FAILED", detail=f"options_for has no list for {key!r} yet")


def run_request(request, progress):
    """--run: one validated request (keys from SPEC; pick values already in Oracle's
    spelling) through the normal flow. Returns the result for the page."""
    oracle.check_environment()
    browser.refuse_production()
    record = {k: v for k, v in request.items()}  # TODO map page keys to request.json keys
    outcome = run_records([record], progress=progress)[record["name"]]
    progress.step("done")
    if outcome == "skipped":
        return {"text": f"{record['name']} already exists in Oracle, so nothing was changed.",
                "skipped": True, "created": None,
                "where": "TODO Setup and Maintenance > <offering> > <area> > <task>"}
    return {"text": f"Created {record['name']} and checked it in Oracle.",
            "created": record,   # TODO the values as read back by verify()
            "where": "TODO Setup and Maintenance > <offering> > <area> > <task>"}


# ---------------------------------------------------------------- main

def main():
    page.main(SPEC, options_for, run_request)   # --spec / --options / --run; else returns
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=str(HERE / "request.json"), help="requirements JSON")
    ap.add_argument("--check", action="store_true", help="read-only check, nothing created")
    ap.add_argument("--headed", action="store_true", help="show the browser window")
    args = ap.parse_args()

    oracle.check_environment()
    browser.refuse_production()
    records = load_requirements(args.file)
    print(f"{len(records)} record(s) requested in {args.file}")
    if args.check:
        work = oracle.init_work_dir(HERE)
        with browser.OracleUI(work, headless=not args.headed) as ui:
            with ui.step("check screens"):
                check_screens(ui)
            for r in records:
                print(f"  {r['name']}: " + ("exists - would be skipped" if exists(ui, r)
                                            else "not found - would be created"))
        print("Check passed: nothing was created, changed or deleted in Oracle.")
        oracle.cleanup_work_dir()
        return
    run_records(records, headed=args.headed)


if __name__ == "__main__":
    main()
