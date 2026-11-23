"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 2 (2026-11-20).

Read-only REST read of ONE Financials generic lookup type and its codes, through FSCR's generic lookups
skill (core/fusion-api/apps-common/lookups) and FSCR's shared REST client, in place. Prints no token or header.
  --view set-enabled -> setEnabledLookups/{LookupType}?expand=lookupCodes  (codes carry SetCode)
  --view standard    -> standardLookups/{LookupType}?expand=lookupCodes

Usage:
  python -B read_generic_lookup.py --fscr <FSCR root> --view set-enabled --type GAPFILL_XX --out <run>/rb.json \
      [--expect-meaning "Type meaning"] [--expect-code "GAPFILL_XX_A|Meaning A"] ... [--expect-set COMMON]
  python -B read_generic_lookup.py --fscr <FSCR root> --type GAPFILL_XX --out <run>/rb_before.json --expect-absent
      (absent = HTTP 404 in standard, set-enabled AND common lookups)
  python -B read_generic_lookup.py --fscr <FSCR root> --info-of SOME_EXISTING_TYPE
      (prints which view holds it, its ModuleId and ReferenceGroupName)

Result line: READBACK: PASS / FAIL (exit 0 / 1); exit 2 = sign-in, privilege or other HTTP problem.
Run WITHOUT -I (FSCR sign-in code needs pywin32 from the user site-packages on Windows).
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

B = "/fscmRestApi/resources/11.13.18.05/"
RES = {"set-enabled": "setEnabledLookups", "standard": "standardLookups", "common": "commonLookups"}


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
    if status is None and "404" in text:
        status = 404
    if status is None and ("401" in text or "TOKEN_EXPIRED" in text):
        status = 401
    return status, text


def auth_stop(st, txt):
    if st in (401, 403) or "TOKEN_EXPIRED" in txt:
        print(f"HTTP {st}: sign-in or privilege problem, not proof of absence. Sign in again (SKILL.md Step 1).")
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fscr", required=True)
    ap.add_argument("--view", choices=["set-enabled", "standard"])
    ap.add_argument("--type")
    ap.add_argument("--info-of")
    ap.add_argument("--out")
    ap.add_argument("--expect-meaning")
    ap.add_argument("--expect-code", action="append", default=[])
    ap.add_argument("--expect-set")
    ap.add_argument("--expect-absent", action="store_true")
    a = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="gapfill_glk_"))
    try:
        if a.info_of:
            for view in ("set-enabled", "standard", "common"):
                st, txt = rest_get(a.fscr, B + RES[view] + "/" + a.info_of, ["onlyData=true"], tmp / "i.json")
                auth_stop(st, txt)
                if st == 200:
                    d = json.load(open(tmp / "i.json", encoding="utf-8"))
                    print(f"{d.get('LookupType')} view={view} ModuleId={d.get('ModuleId')} "
                          f"ReferenceGroupName={d.get('ReferenceGroupName') or ''} level={d.get('CustomizationLevel')}")
                    return 0
            print(f"{a.info_of}: not found in set-enabled, standard or common lookups")
            return 1
        if not a.type or not a.out:
            sys.exit("STOP: --type and --out are required")
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)

        if a.expect_absent:
            found = []
            for view in ("set-enabled", "standard", "common"):
                st, txt = rest_get(a.fscr, B + RES[view] + "/" + a.type, ["onlyData=true"], tmp / "x.json")
                auth_stop(st, txt)
                print(f"  {RES[view]}/{a.type}: HTTP {st}")
                if st == 200:
                    found.append(view)
                elif st != 404:
                    print("  unexpected status; last lines:\n" + "\n".join(txt.splitlines()[-3:]))
                    return 2
            json.dump({"LookupType": a.type, "view": a.view or "", "found": bool(found), "found_in": found,
                       "http": 200 if found else 404}, open(out, "w", encoding="utf-8"), indent=2)
            print(f"{a.type}: {'FOUND in ' + ','.join(found) if found else 'NOT FOUND (HTTP 404 in all three views)'}")
            print("READBACK:", "FAIL" if found else "PASS")
            return 1 if found else 0

        if not a.view:
            sys.exit("STOP: --view is required for a read-back")
        st, txt = rest_get(a.fscr, B + RES[a.view] + "/" + a.type, ["expand=lookupCodes", "onlyData=true"], tmp / "t.json")
        auth_stop(st, txt)
        if st == 404:
            json.dump({"LookupType": a.type, "view": a.view, "found": False, "http": 404}, open(out, "w", encoding="utf-8"), indent=2)
            print(f"{a.type}: NOT FOUND in {RES[a.view]} (HTTP 404)")
            print("READBACK: FAIL")
            return 1
        if st != 200:
            print(f"HTTP {st}. Last lines:\n" + "\n".join(txt.splitlines()[-3:]))
            return 2
        d = json.load(open(tmp / "t.json", encoding="utf-8"))
        lc = d.get("lookupCodes") or []
        items = lc.get("items", []) if isinstance(lc, dict) else lc
        keep = ("LookupCode", "Meaning", "Description", "EnabledFlag", "DisplaySequence", "SetCode")
        rec = {"LookupType": d.get("LookupType"), "view": a.view, "Meaning": d.get("Meaning"),
               "Description": d.get("Description"), "ModuleId": d.get("ModuleId"),
               "ReferenceGroupName": d.get("ReferenceGroupName"), "CustomizationLevel": d.get("CustomizationLevel"),
               "http": 200, "found": True,
               "lookupCodes": [{k: i.get(k) for k in keep} for i in sorted(items, key=lambda x: x.get("LookupCode") or "")]}
        json.dump(rec, open(out, "w", encoding="utf-8"), indent=2)
        print(f"{rec['LookupType']} | {rec['Meaning']} | view {a.view} | ref group {rec['ReferenceGroupName'] or '-'} | level {rec['CustomizationLevel']}")
        for c in rec["lookupCodes"]:
            print(f"  {c['LookupCode']} | {c['Meaning']} | set {c.get('SetCode') or '-'} | enabled {c['EnabledFlag']} | seq {c['DisplaySequence']}")
        problems = []
        if a.expect_meaning and rec["Meaning"] != a.expect_meaning:
            problems.append(f"type meaning {rec['Meaning']!r} != {a.expect_meaning!r}")
        got = {c["LookupCode"]: c for c in rec["lookupCodes"]}
        for e in a.expect_code:
            code, _, mean = e.partition("|")
            if code not in got:
                problems.append(f"code {code} missing")
                continue
            if mean and got[code]["Meaning"] != mean:
                problems.append(f"code {code} meaning {got[code]['Meaning']!r} != {mean!r}")
            if a.expect_set and a.view == "set-enabled" and got[code].get("SetCode") != a.expect_set:
                problems.append(f"code {code} set {got[code].get('SetCode')!r} != {a.expect_set!r}")
            if got[code]["EnabledFlag"] != "Y":
                problems.append(f"code {code} is not enabled")
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
