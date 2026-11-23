"""Read-only after the live test: Oracle's import log of the run's process, one fresh data file of the task, and a
comparison of every term with FSCR's saved ETIA-TEST data file of 2026-10-28 (11 terms). Nothing is created."""
import io
import json
import shutil
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FOLDER = ROOT / "Receivables Payment Terms"
sys.path[:0] = [str(FOLDER), str(ROOT)]
from common import oracle  # noqa: E402

import rpt_package as pkg  # noqa: E402

PID = int(sys.argv[1])
TERM = json.loads((HERE / "term.json").read_text())["name"]
OLD = (ROOT.parent / "fscr-main" / "fscr-main" / "project" / "draft-impl-project-20261028" / "exports" / "financials"
       / "customer-billing" / "manage-receivables-payment-terms"
       / "ETIA-TEST_setup_task_csv_export_ar_manage_receivables_payment_terms_100004731498215.zip")
oracle.check_environment()
oracle.init_work_dir(FOLDER)
out = {}
_, result_url = oracle.process_urls("Import", pkg.TASK, PID)
res = oracle.call("GET", result_url).json()
out["process"] = {k: v for k, v in res.items() if k != "links"}
logs = {}
for link in res.get("links", []):
    if link.get("rel") == "enclosure":
        r, err = oracle.try_call("GET", link["href"], timeout=180)
        if r is not None and not err:
            texts = pkg.unpack(r.content)
            logs[link["name"]] = texts
            (HERE / f"import_{PID}_{link['name']}.txt").write_text("\n=====\n".join(texts), encoding="utf-8")
        else:
            logs[link["name"]] = [f"(not read: {(err or '')[:200]})"]
out["enclosures"] = sorted(logs)
data, path = oracle.export_task(pkg.TASK, "readback")
shutil.copy(path, HERE / "after_readback.zip")
oracle.cleanup_work_dir()
lay, now = pkg.read_rows(data)
_, old = pkg.read_rows(OLD.read_bytes())
H = pkg.ENTITIES["header"]
out["terms_before_2026_10_28"] = len(old[H])
out["terms_now"] = len(now[H])
out["names_now"] = sorted(f"{k[0]} ({k[1]})" for k in pkg.terms_in(now))
out["sets_used"] = sorted({k[1] for k in pkg.terms_in(now)})
mine = {e: [r for r in rows if pkg.key_of(r)[0] == TERM] for e, rows in now.items()}
out["new_term_rows"] = {e: rows for e, rows in mine.items()}
changed = []
for e in pkg.ENTITIES.values():
    a = sorted(tuple(sorted(r.items())) for r in old.get(e, []))
    b = sorted(tuple(sorted(r.items())) for r in now.get(e, []) if pkg.key_of(r)[0] != TERM)
    if a != b:
        changed.append(e)
out["other_terms_changed_entities_since_2026_10_28"] = changed
(HERE / "readback.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k != "new_term_rows"}, indent=1, ensure_ascii=False))
