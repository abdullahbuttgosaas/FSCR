"""Added by GoSaaS, not part of official FSCR. Gap fill, batch 1 part 3 (2026-11-20).

Read-only REST GET of one Fusion resource (or a child collection) through FSCR's shared REST client
(core/fusion-api/rest-api-client/scripts/fusion_rest_client.py), used in place. Saves the rows to JSON,
prints them, and checks expectations. Prints no token, header or server address.

Usage:
  python -B rest_read.py --fscr <FSCR root> --resource documentSequenceCategoriesLOV \
      --q "Code LIKE 'GAPFILL_%'" --fields Code,Name,Description --out <run>/readback.json \
      [--expect "Code=GAPFILL_X,Name=GAPFILL_X"] [--expect ...] [--expect-count N] [--expect-absent]
  --resource can be a path below /fscmRestApi/resources/11.13.18.05/ such as valueSets/<id>/child/values
  --q      the q= filter (Oracle REST syntax). --finder can be given instead or as well.
  --expect one expected row: comma-separated Col=Value pairs; a row must match all of them.
  --expect-count  exact number of rows the query must return.
  --expect-absent PASS only if no row is returned.
Result line: READBACK: PASS / FAIL (exit 0 / 1). Exit 2 = sign-in, privilege or HTTP problem.
Run WITHOUT -I (FSCR sign-in code needs pywin32 from the user site-packages on Windows).
From Git Bash set MSYS_NO_PATHCONV=1 (this script builds the /fscmRestApi path itself, so it is safe either way).
"""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

BASE = "/fscmRestApi/resources/11.13.18.05/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fscr", required=True)
    ap.add_argument("--resource", required=True)
    ap.add_argument("--q")
    ap.add_argument("--finder")
    ap.add_argument("--fields")
    ap.add_argument("--limit", default="200")
    ap.add_argument("--out", required=True)
    ap.add_argument("--expect", action="append", default=[])
    ap.add_argument("--expect-count", type=int)
    ap.add_argument("--expect-absent", action="store_true")
    a = ap.parse_args()

    client = Path(a.fscr) / "core" / "fusion-api" / "rest-api-client" / "scripts" / "fusion_rest_client.py"
    if not client.exists():
        sys.exit(f"STOP: FSCR REST client not found at {client}. --fscr must be the folder holding core\\ and shared\\.")
    tmp = Path(tempfile.mkdtemp(prefix="gapfill_rr_"))
    raw = tmp / "r.json"
    cmd = [sys.executable, "-B", str(client), BASE + a.resource.strip("/"), "--no-open-browser", "--output", str(raw),
           "--query", "onlyData=true", "--query", f"limit={a.limit}"]
    if a.q:
        cmd += ["--query", f"q={a.q}"]
    if a.finder:
        cmd += ["--query", f"finder={a.finder}"]
    if a.fields:
        cmd += ["--query", f"fields={a.fields}"]
    env = dict(os.environ, MSYS_NO_PATHCONV="1", PYTHONUTF8="1")
    p = subprocess.run(cmd, cwd=str(a.fscr), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    text = (p.stdout or "") + (p.stderr or "")
    try:
        if not raw.exists():
            code = None
            for tok in ("401", "403", "404", "400", "500"):
                if f"HTTP {tok}" in text:
                    code = tok
                    break
            if "TOKEN_EXPIRED" in text or code in ("401", "403"):
                print(f"HTTP {code}: sign-in or privilege problem. Sign in again (see the skill's sign-in step).")
            else:
                print(f"HTTP {code or '?'}: request failed. Check the resource name and the q filter.")
            return 2
        d = json.load(open(raw, encoding="utf-8"))
    finally:
        for f in tmp.glob("*"):
            f.unlink()
        tmp.rmdir()

    items = d.get("items", [d] if d and "items" not in d else [])
    if a.fields:
        keep = [c.strip() for c in a.fields.split(",")]
        items = [{k: i.get(k) for k in keep} for i in items]
    else:
        items = [{k: v for k, v in i.items() if k != "links"} for i in items]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"resource": a.resource, "q": a.q, "count": len(items), "hasMore": d.get("hasMore"), "items": items},
              open(out, "w", encoding="utf-8"), indent=2, default=str)
    print(f"{a.resource}: {len(items)} row(s){' (hasMore=true: result cut off)' if d.get('hasMore') else ''}")
    for i in items[:50]:
        print("  " + " | ".join(f"{k}={v}" for k, v in i.items()))

    problems = []
    if a.expect_absent and items:
        problems.append(f"{len(items)} row(s) found but --expect-absent was given")
    if a.expect_count is not None and len(items) != a.expect_count:
        problems.append(f"{len(items)} rows, expected {a.expect_count}")
    for e in a.expect:
        want = {}
        for pair in e.split(","):
            k, _, v = pair.partition("=")
            want[k.strip()] = v.strip()
        if not any(all(str(i.get(k)) == v for k, v in want.items()) for i in items):
            problems.append(f"no row matches {want}")
    for pr in problems:
        print("  problem:", pr)
    print("READBACK:", "FAIL" if problems else "PASS")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
