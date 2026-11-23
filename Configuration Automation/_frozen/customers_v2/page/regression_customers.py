"""Customers regression check for the upload sheet (2026-10-25). Customers is frozen while
other setups are wired into the shared sheet code; this proves it did not change.

  python page/regression_customers.py --freeze      # once, BEFORE any change: snapshot + hashes
  python page/regression_customers.py --record      # once: the read-only checks with Oracle,
                                                    # answers saved; expected preview from the
                                                    # frozen code
  python page/regression_customers.py               # the check (offline, nothing sent to Oracle)

The snapshot is _frozen/customers_v1/: copies of page/, common/, Customers/ (without _work/ and
__pycache__/), the root CLAUDE.md, the customer sheet that worked (input/), manifest.json (SHA-256
of every copied file), answers.json (Oracle's answers of the recorded run) and expected.json (the
preview the frozen code builds from those answers).

The check:
 (a) every file of the Customers folder (without _work/ and __pycache__/) has the hash in the
     manifest, and no file was added or removed. Changes in page/, common/ and CLAUDE.md are
     listed for information (page/ is expected to change).
 (b) the preview of the customer sheet, built by the CURRENT page code (page/server.py
     full_check(), i.e. page/workbook.py reading and checking plus the Oracle checks), with every
     Oracle read-only answer replaced by the saved one, equals expected.json field by field.
     Keys the current code adds that the frozen version did not have are listed as additions,
     not as differences. Nothing is sent to Oracle.
Exit 0 when both hold, 1 otherwise.

Customers v2 (2026-10-26, the freeze lifted by the user for the fix): _frozen/customers_v1 stays as it was;
the fixed version is _frozen/customers_v2 with its own manifest, answers_v2.json and expected_v2.json.

  python page/regression_customers.py --freeze-v2   # once, after the fix: snapshot v2 + its recorded answers
  python page/regression_customers.py               # the check: (a)-(c) against v2, plus
                                                    # (d) v1 versus v2 preview, field by field: only the
                                                    #     differences in ALLOWED_V1_V2 may differ
  python page/regression_customers.py --v1          # the old check against v1 only
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FROZEN_V1 = ROOT / "_frozen" / "customers_v1"
FROZEN_V2 = ROOT / "_frozen" / "customers_v2"
FROZEN = FROZEN_V2 if (FROZEN_V2 / "manifest.json").exists() and "--v1" not in sys.argv else FROZEN_V1
ANSWERS = "answers_v2.json" if FROZEN == FROZEN_V2 else "answers.json"
EXPECTED = "expected_v2.json" if FROZEN == FROZEN_V2 else "expected.json"
# The intended differences between the v1 and the v2 preview of the working customer sheet: (path, v2 value), both
# regular expressions, paths as compare() prints them. Anything else that differs fails the check.
ALLOWED_V1_V2 = [
    # v2 finds the place through the same dialogs as Create and names the county it uses
    (r"^/records\[\d+\]/fields\[\d+\]/note$", r"^Found in Oracle: .+ \(.+ county\)"),
]
SHEET_SOURCE = Path(r"E:\GoSaaS\positive cases\Best Start.xlsx")   # the customer sheet that worked (2026-10-25)
SHEET = FROZEN_V1 / "input" / "customer_sheet.xlsx"
SKIP_DIRS = {"_work", "__pycache__"}
PARTS = ("page", "common", "Customers")


def files_of(base):
    """Relative paths of the files that count: page/, common/, Customers/ and CLAUDE.md."""
    out = []
    for part in PARTS:
        for p in sorted((base / part).rglob("*")):
            rel = p.relative_to(base)
            if p.is_file() and not SKIP_DIRS & set(rel.parts):
                out.append(rel.as_posix())
    if (base / "CLAUDE.md").exists():
        out.append("CLAUDE.md")
    return out


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- freeze

def freeze(force=False):
    if FROZEN.exists():
        if not force:
            sys.exit(f"{FROZEN} exists already; it is never overwritten (use --force only on purpose).")
        shutil.rmtree(FROZEN)
    manifest = {}
    for rel in files_of(ROOT):
        dst = FROZEN / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
        manifest[rel] = sha(dst)
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SHEET_SOURCE, SHEET)
    (FROZEN / "manifest.json").write_text(json.dumps(
        {"made": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
         "sheet": {"source": str(SHEET_SOURCE), "sha256": sha(SHEET)}, "files": manifest}, indent=1),
        encoding="utf-8")
    print(f"froze {len(manifest)} files into {FROZEN}")


# ---------------------------------------------------------------- one preview (child process)

def answer_key(*parts):
    return json.dumps(parts, sort_keys=True, ensure_ascii=False)


def child(root, mode, answers_path, sheet):
    """Run in a fresh process: the page code of <root> builds the preview of the sheet.
    mode "record": real read-only Oracle checks, every answer saved to answers_path.
    mode "replay": the saved answers instead of Oracle."""
    root = Path(root)
    sys.path[:0] = [str(root / "page"), str(root)]
    import server  # noqa: E402  (that root's page/server.py)
    server.log = lambda msg: print("  [server] " + msg, file=sys.stderr)
    server.run_active = lambda: False
    data = Path(sheet).read_bytes()
    if mode == "record":
        answers = {"lists": {}, "batches": {}, "today": None, "specs": {}}
        server.load_folders()
        answers["specs"] = {n: f["spec"] for n, f in server.FOLDERS.items()}
        real_today, real_list, real_batch = server.oracle_today, server.sheet_list, server.folder_batch

        def today(max_age=600):
            answers["today"] = real_today(max_age)
            return answers["today"]

        def lists(folder, field, full=False):
            got = real_list(folder, field, full)
            answers["lists"][answer_key(folder, field, bool(full))] = got
            return got

        def batch(folder, cmd, requests, timeout):
            got = real_batch(folder, cmd, requests, timeout)
            answers["batches"][answer_key(folder, cmd, requests)] = got
            return got
        server.oracle_today, server.sheet_list, server.folder_batch = today, lists, batch
        res = server.full_check(data)
        Path(answers_path).write_text(json.dumps(answers, indent=1, ensure_ascii=False), encoding="utf-8")
    else:
        answers = json.loads(Path(answers_path).read_text(encoding="utf-8"))
        missing = []
        server.FOLDERS.clear()
        for name, spec in answers["specs"].items():
            server.FOLDERS[name] = {"name": name, "script": server.folder_script(name), "spec": spec, "error": None}
        reg = server.workbook.load_registry()
        for g in reg["groups"]:            # a folder the frozen version didn't know: its own spec, offline
            if g["folder"] not in server.FOLDERS:
                p = subprocess.run([sys.executable, server.folder_script(g["folder"]), "--spec"], cwd=root,
                                   capture_output=True, text=True, encoding="utf-8")
                server.FOLDERS[g["folder"]] = {"name": g["folder"], "script": server.folder_script(g["folder"]),
                                               "spec": json.loads(p.stdout.strip().splitlines()[-1]), "error": None}
        server.oracle_today = lambda max_age=600: answers["today"]

        def lists(folder, field, full=False):
            k = answer_key(folder, field, bool(full))
            if k not in answers["lists"]:
                missing.append(["list", folder, field, bool(full)])
                return {"failed": "no saved answer (regression check)"}
            return answers["lists"][k]

        def batch(folder, cmd, requests, timeout):
            k = answer_key(folder, cmd, requests)
            if k not in answers["batches"]:
                missing.append(["batch", folder, cmd])
                return [{"ok": False, "text": "no saved answer (regression check)"} for _ in requests]
            return answers["batches"][k]
        server.sheet_list, server.folder_batch = lists, batch
        server.ADDRESS_CACHE.clear()
        res = server.full_check(data)
        res["_missing_answers"] = missing
    print(json.dumps(res, ensure_ascii=False))


def sheet_with_empty_tabs():
    """The customer sheet plus every tab of the current empty sheet it doesn't have (headers and
    hints only, no rows): "customers and an empty Order Types tab" (2026-10-25)."""
    import io
    sys.path.insert(0, str(HERE))
    import workbook
    from openpyxl import load_workbook
    wb = load_workbook(SHEET)
    tpl = load_workbook(io.BytesIO(workbook.make_template()))
    for ws in tpl.worksheets:
        if ws.title not in wb.sheetnames and ws.sheet_state == "visible":
            new = wb.create_sheet(ws.title)
            for row in ws.iter_rows(min_row=1, max_row=3):
                for c in row:
                    new.cell(c.row, c.column, c.value)
    out = FROZEN / "input" / "customer_sheet_with_empty_tabs.xlsx"
    wb.save(out)
    return out


def preview_with(root, mode, sheet=None, answers=None):
    p = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child", str(root), mode,
                        str(answers or FROZEN / ANSWERS), str(sheet or SHEET)], cwd=str(root),
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600)
    if p.returncode != 0 or not p.stdout.strip():
        sys.exit(f"the preview ({mode}, {root}) failed:\n{p.stderr[-3000:]}")
    return json.loads(p.stdout.strip().splitlines()[-1])


# ---------------------------------------------------------------- compare

def compare(expected, actual, path="", diffs=None, added=None):
    """Every value of expected must be in actual, equal. Keys only in actual are additions."""
    diffs = [] if diffs is None else diffs
    added = [] if added is None else added
    if isinstance(expected, dict) and isinstance(actual, dict):
        for k, v in expected.items():
            if k not in actual:
                diffs.append(f"{path}/{k}: missing now (was {json.dumps(v, ensure_ascii=False)[:200]})")
            else:
                compare(v, actual[k], f"{path}/{k}", diffs, added)
        for k in actual:
            if k not in expected:
                added.append(f"{path}/{k} = {json.dumps(actual[k], ensure_ascii=False)[:200]}")
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            diffs.append(f"{path}: {len(expected)} item(s) before, {len(actual)} now")
        for i, (a, b) in enumerate(zip(expected, actual)):
            compare(a, b, f"{path}[{i}]", diffs, added)
    elif expected != actual:
        diffs.append(f"{path}: was {json.dumps(expected, ensure_ascii=False)[:200]}, "
                     f"now {json.dumps(actual, ensure_ascii=False)[:200]}")
    return diffs, added


def count_fields(v):
    if isinstance(v, dict):
        return sum(count_fields(x) for x in v.values())
    if isinstance(v, list):
        return sum(count_fields(x) for x in v)
    return 1


# ---------------------------------------------------------------- record / check

def record():
    if not (FROZEN / "manifest.json").exists():
        sys.exit("Freeze first: python page/regression_customers.py --freeze")
    changed = hash_report(quiet=True)
    if any(changed.values()):
        sys.exit(f"The live files differ from the snapshot already ({changed}); record only right after --freeze.")
    print("recording: the live page code with the real read-only checks (lists, Oracle's today, "
          "same name, address places) ...")
    live = preview_with(ROOT, "record")
    print("expected: the FROZEN page code with the saved answers ...")
    expected = preview_with(FROZEN, "replay")
    if expected.pop("_missing_answers"):
        sys.exit("The frozen replay asked for an answer that wasn't recorded.")
    diffs, added = compare(live, expected)
    if diffs or added:
        sys.exit("The frozen replay differs from the live recording:\n  " + "\n  ".join(diffs + added))
    (FROZEN / "expected.json").write_text(json.dumps(expected, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"stored expected.json: {len(expected['records'])} record(s), {count_fields(expected)} values, "
          f"ok={expected['ok']}, {len(expected['problems'])} problem(s), {len(expected['stops'])} stop(s); "
          "identical to the live recording")


def hash_report(quiet=False):
    man = json.loads((FROZEN / "manifest.json").read_text(encoding="utf-8"))["files"]
    now = {rel: sha(ROOT / rel) for rel in files_of(ROOT)}
    out = {}
    for part in PARTS + ("CLAUDE.md",):
        inside = lambda rel: rel == part if part == "CLAUDE.md" else rel.startswith(part + "/")
        old = {k: v for k, v in man.items() if inside(k)}
        new = {k: v for k, v in now.items() if inside(k)}
        out[part] = ([f"changed {k}" for k in sorted(old) if k in new and new[k] != old[k]]
                     + [f"removed {k}" for k in sorted(set(old) - set(new))]
                     + [f"added {k}" for k in sorted(set(new) - set(old))])
        if not quiet:
            n = len(old)
            print(f"  {part}: {n} file(s) in the snapshot, " +
                  ("all identical" if not out[part] else f"{len(out[part])} difference(s): " + "; ".join(out[part])))
    return out


def check():
    print(f"(a) file hashes against {FROZEN / 'manifest.json'}:")
    hashes = hash_report()
    ok_a = not hashes["Customers"]
    print(f"    Customers folder: {'UNCHANGED' if ok_a else 'CHANGED'}"
          + ("" if not any(hashes[p] for p in ("page", "common", "CLAUDE.md")) else
             " (page/, common/ or CLAUDE.md differences above are for information)"))
    print("(b) the customer sheet's preview, current page code, saved Oracle answers:")
    expected = json.loads((FROZEN / EXPECTED).read_text(encoding="utf-8"))
    actual = preview_with(ROOT, "replay")
    missing = actual.pop("_missing_answers")
    diffs, added = compare(expected, actual)
    print(f"    compared {count_fields(expected)} values ({len(expected['records'])} record(s)); "
          f"{len(diffs)} difference(s)")
    for d in diffs:
        print("    DIFF  " + d)
    for a in added:
        print("    ADDED " + a)
    for m in missing:
        print(f"    note  no saved answer for {m} (not part of the frozen run)")
    ok_b = not diffs
    print("(c) the same sheet with the other modules' tabs added, empty (e.g. Order Types):")
    extra = sheet_with_empty_tabs()
    actual2 = preview_with(ROOT, "replay", extra)
    actual2.pop("_missing_answers")
    diffs2, added2 = compare(expected, actual2)
    print(f"    compared {count_fields(expected)} values; {len(diffs2)} difference(s)")
    for d in diffs2:
        print("    DIFF  " + d)
    for a in added2:
        print("    ADDED " + a)
    ok_b = ok_b and not diffs2
    ok_d = True
    if FROZEN == FROZEN_V2:
        ok_d = compare_v1_v2()
    print(f"RESULT: {'PASS' if ok_a and ok_b and ok_d else 'FAIL'} (hashes {'ok' if ok_a else 'changed'}, "
          f"preview {'identical' if ok_b else 'different'}"
          + (f", v1 versus v2 {'only the intended differences' if ok_d else 'UNINTENDED differences'}"
             if FROZEN == FROZEN_V2 else "") + ")")
    return 0 if ok_a and ok_b and ok_d else 1


def compare_v1_v2():
    """(d) The working customer sheet's preview: the frozen v1 code against v2 (expected_v2.json), field by
    field, both from the SAME Oracle answers (answers_v2.json), so only code differences show (not Oracle's
    data since v1 was recorded: its date, new same-name customers). A difference passes only when its path
    and its v2 value match ALLOWED_V1_V2."""
    import re as _re
    v1 = preview_with(FROZEN_V1, "replay", answers=FROZEN_V2 / "answers_v2.json")
    if v1.pop("_missing_answers", None):
        print("(d) the v1 code asked Oracle something v2's recording doesn't hold")
        return False
    v2 = json.loads((FROZEN_V2 / "expected_v2.json").read_text(encoding="utf-8"))
    print("(d) the same sheet's preview, v1 versus v2, field by field:")
    bad, good = [], []

    def walk(a, b, path=""):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in sorted(set(a) | set(b)):
                if k not in b:
                    bad.append(f"{path}/{k}: only in v1")
                elif k not in a:
                    good.append(f"{path}/{k}: added in v2 = {json.dumps(b[k], ensure_ascii=False)[:150]}")
                else:
                    walk(a[k], b[k], f"{path}/{k}")
        elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
            for i, (x, y) in enumerate(zip(a, b)):
                walk(x, y, f"{path}[{i}]")
        elif a != b:
            line = f"{path}: v1 {json.dumps(a, ensure_ascii=False)[:150]} -> v2 {json.dumps(b, ensure_ascii=False)[:150]}"
            ok = any(_re.search(pp, path) and _re.search(vp, str(b)) for pp, vp in ALLOWED_V1_V2)
            (good if ok else bad).append(line)
    walk(v1, v2)
    print(f"    compared {count_fields(v1)} values; {len(good)} intended difference(s), {len(bad)} other")
    for g in good:
        print("    INTENDED " + g)
    for b in bad:
        print("    DIFF     " + b)
    return not bad


def freeze_v2():
    """The fixed version: snapshot + manifest into _frozen/customers_v2 (never over v1), then the read-only
    checks with Oracle recorded (answers_v2.json) and the expected preview from the frozen v2 code."""
    if (FROZEN_V2 / "manifest.json").exists() and "--force" not in sys.argv:
        sys.exit(f"{FROZEN_V2} exists already; it is never overwritten (use --force only on purpose).")
    if FROZEN_V2.exists():
        shutil.rmtree(FROZEN_V2)
    manifest = {}
    for rel in files_of(ROOT):
        dst = FROZEN_V2 / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, dst)
        manifest[rel] = sha(dst)
    (FROZEN_V2 / "input").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SHEET, FROZEN_V2 / "input" / "customer_sheet.xlsx")
    (FROZEN_V2 / "manifest.json").write_text(json.dumps(
        {"made": __import__("datetime").datetime.now().isoformat(timespec="seconds"), "from": "customers v2 fix",
         "sheet": {"source": str(SHEET), "sha256": sha(SHEET)}, "files": manifest}, indent=1), encoding="utf-8")
    print(f"froze {len(manifest)} files into {FROZEN_V2}")
    answers = FROZEN_V2 / "answers_v2.json"
    print("recording: the v2 page code with the real read-only checks ...")
    live = preview_with(ROOT, "record", answers=answers)
    print("expected: the FROZEN v2 page code with the saved answers ...")
    expected = preview_with(FROZEN_V2, "replay", answers=answers)
    if expected.pop("_missing_answers"):
        sys.exit("The frozen v2 replay asked for an answer that wasn't recorded.")
    live.pop("_missing_answers", None)
    diffs, added = compare(live, expected)
    if diffs or added:
        sys.exit("The frozen v2 replay differs from the live recording:\n  " + "\n  ".join(diffs + added))
    (FROZEN_V2 / "expected_v2.json").write_text(json.dumps(expected, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"stored expected_v2.json: {len(expected['records'])} record(s), {count_fields(expected)} values, "
          f"ok={expected['ok']}; identical to the live recording")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--child"]:
        child(*a[1:5])
    elif a[:1] == ["--freeze"]:
        freeze("--force" in a)
    elif a[:1] == ["--freeze-v2"]:
        freeze_v2()
    elif a[:1] == ["--record"]:
        record()
    else:
        sys.exit(check())
