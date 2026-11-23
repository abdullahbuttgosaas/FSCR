"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 1 (2026-11-20).

Read-only REST read of ONE standard lookup type and its codes, through FSCR's generic lookups skill
(core/fusion-api/apps-common/lookups -> standardLookups/{LookupType}?expand=lookupCodes), using FSCR's
shared REST client in place. Prints no token and no header.

Usage:
  python -B read_lookup.py --fscr <FSCR root> --type GAPFILL_XX_TYPE --out <run>/readback.json \
      [--expect-meaning "Type meaning"] [--expect-code "GAPFILL_A|Meaning A"] [--expect-code ...] \
      [--expect-absent]
  python -B read_lookup.py --fscr <FSCR root> --module-of SOME_EXISTING_TYPE   (prints its ModuleId only)

Result line: READBACK: PASS / FAIL (exit code 0 / 1). With --expect-absent, PASS means HTTP 404.
Run WITHOUT -I (FSCR sign-in code needs pywin32 from the user site-packages on Windows).
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

BASE = "/fscmRestApi/resources/11.13.18.05/standardLookups/"


def rest_get(fscr, path, query, out_file):
    client = Path(fscr) / "core" / "fusion-api" / "rest-api-client" / "scripts" / "fusion_rest_client.py"
    if not client.exists():
        sys.exit(f"STOP: FSCR REST client not found at {client}")
    cmd = [sys.executable, "-B", str(client), path, "--no-open-browser", "--output", str(out_file)]
    for q in query:
        cmd += ["--query", q]
    p = subprocess.run(cmd, cwd=str(fscr), capture_output=True, text=True, encoding="utf-8", errors="replace")
    text = (p.stdout or "") + (p.stderr or "")
    status = None
    for line in text.splitlines():
        if line.startswith("HTTP "):
            try:
                status = int(line.split()[1])
            except ValueError:
                pass
    if "404" in text and status is None:
        status = 404
    return status, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fscr", required=True)
    ap.add_argument("--type")
    ap.add_argument("--module-of")
    ap.add_argument("--out")
    ap.add_argument("--expect-meaning")
    ap.add_argument("--expect-code", action="append", default=[])
    ap.add_argument("--expect-absent", action="store_true")
    a = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="gapfill_lk_"))
    try:
        if a.module_of:
            st, txt = rest_get(a.fscr, BASE + a.module_of, ["onlyData=true", "fields=LookupType,ModuleId"], tmp / "m.json")
            if st != 200:
                sys.exit(f"STOP: HTTP {st} reading {a.module_of}. Last lines:\n" + "\n".join(txt.splitlines()[-3:]))
            d = json.load(open(tmp / "m.json", encoding="utf-8"))
            print(f"{d.get('LookupType')} ModuleId={d.get('ModuleId')}")
            return 0
        if not a.type or not a.out:
            sys.exit("STOP: --type and --out are required")
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        st, txt = rest_get(a.fscr, BASE + a.type, ["expand=lookupCodes", "onlyData=true"], tmp / "t.json")
        if "TOKEN_EXPIRED" in txt or st in (401, 403):
            print(f"HTTP {st}: sign-in or privilege problem, not proof that the lookup is absent. Sign in again (SKILL.md Step 1).")
            return 2
        if st == 404 or (st is None and not (tmp / "t.json").exists()):
            json.dump({"LookupType": a.type, "http": 404, "found": False}, open(out, "w", encoding="utf-8"), indent=2)
            print(f"{a.type}: NOT FOUND (HTTP 404)")
            ok = a.expect_absent
            print("READBACK:", "PASS" if ok else "FAIL")
            return 0 if ok else 1
        if st != 200:
            print(f"HTTP {st}. Last lines:\n" + "\n".join(txt.splitlines()[-3:]))
            return 2
        d = json.load(open(tmp / "t.json", encoding="utf-8"))
        lc = d.get("lookupCodes") or []
        items = lc.get("items", []) if isinstance(lc, dict) else lc
        keep = ("LookupCode", "Meaning", "Description", "EnabledFlag", "DisplaySequence")
        rec = {"LookupType": d.get("LookupType"), "Meaning": d.get("Meaning"), "Description": d.get("Description"),
               "ModuleId": d.get("ModuleId"), "CustomizationLevel": d.get("CustomizationLevel"), "http": 200, "found": True,
               "lookupCodes": [{k: i.get(k) for k in keep} for i in sorted(items, key=lambda x: x.get("LookupCode") or "")]}
        json.dump(rec, open(out, "w", encoding="utf-8"), indent=2)
        print(f"{rec['LookupType']} | {rec['Meaning']} | ModuleId {rec['ModuleId']} | level {rec['CustomizationLevel']}")
        for c in rec["lookupCodes"]:
            print(f"  {c['LookupCode']} | {c['Meaning']} | enabled {c['EnabledFlag']} | seq {c['DisplaySequence']}")
        problems = []
        if a.expect_absent:
            problems.append("lookup type exists but --expect-absent was given")
        if a.expect_meaning and rec["Meaning"] != a.expect_meaning:
            problems.append(f"type meaning {rec['Meaning']!r} != {a.expect_meaning!r}")
        got = {c["LookupCode"]: c["Meaning"] for c in rec["lookupCodes"]}
        for e in a.expect_code:
            code, _, mean = e.partition("|")
            if code not in got:
                problems.append(f"code {code} missing")
            elif mean and got[code] != mean:
                problems.append(f"code {code} meaning {got[code]!r} != {mean!r}")
        if a.expect_code and len(got) != len(a.expect_code):
            problems.append(f"{len(got)} codes found, {len(a.expect_code)} expected")
        for p in problems:
            print("  problem:", p)
        print("READBACK:", "FAIL" if problems else "PASS")
        return 1 if problems else 0
    finally:
        for f in tmp.glob("*"):
            f.unlink()
        tmp.rmdir()


if __name__ == "__main__":
    sys.exit(main())
