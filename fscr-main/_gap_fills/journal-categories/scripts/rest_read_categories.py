"""Added by GoSaaS, not part of official FSCR. Origin: Run 24, ETIA-TEST. Fixed in Run 26c.
READ-ONLY. One GET on journalCategoriesLOV, filtered by name prefix. Never prints the token.
Uses FSCR's own auth module IN PLACE (no copy). Adapted from the probe script that ran in Runs 23-24.

Run WITHOUT the Python -I flag: FSCR's Windows token storage needs pywin32, which is installed in the
user site-packages folder, and -I hides that folder (Run 26b: "Windows Fusion OAuth storage requires pywin32").

Usage:
  python -B rest_read_categories.py [--prefix FSCRT_] [--out rows.json]
      [--before-dir <unzipped export taken before the import>] [--expect "name1" --expect "name2" ...]
With --expect, the script also checks (and exits 1 if not true):
  - every expected name is in the REST result;
  - if --before-dir is given: REST row count == (rows with the prefix in the before export) + (number of --expect names).
"""
import argparse, csv, gzip, json, sys, urllib.parse, urllib.request, urllib.error
sys.dont_write_bytecode = True            # do not write __pycache__ inside FSCR folders
from pathlib import Path
FSCR = Path(__file__).resolve().parents[3] / "fscr-main"      # <fscr-main>/fscr-main
sys.path.insert(0, str(FSCR / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa

ap = argparse.ArgumentParser()
ap.add_argument("--prefix", default="FSCRT_"); ap.add_argument("--out")
ap.add_argument("--before-dir"); ap.add_argument("--expect", action="append", default=[])
a = ap.parse_args()
props = fa.oauth_service_properties(fa.read_properties(FSCR / "core/auth/fusionEnv.properties"), "standard")
token = fa.load_cached_access_token(props) or sys.exit("TOKEN_EXPIRED: sign in again (see SKILL.md step 1)")
q = {"q": f"UserJeCategoryName LIKE '{a.prefix}%'", "limit": "500", "totalResults": "true"}
url = props["restBaseUrl"].rstrip("/") + "/fscmRestApi/resources/11.13.18.05/journalCategoriesLOV?" + urllib.parse.urlencode(q)
req = urllib.request.Request(url, method="GET")           # GET only
req.add_header("Authorization", "Bearer " + token); req.add_header("REST-Framework-Version", "9"); req.add_header("Accept-Encoding", "identity")
try:
    with urllib.request.urlopen(req, timeout=120) as r: raw, st = r.read(), r.status
except urllib.error.HTTPError as e: raw, st = e.read(), e.code
if raw[:2] == b"\x1f\x8b": raw = gzip.decompress(raw)
print("HTTP", st)
if st != 200: sys.exit(raw.decode("utf-8", "replace")[:300])
body = json.loads(raw)
items = [{k: i.get(k) for k in ("JeCategoryName", "UserJeCategoryName", "Description")} for i in body["items"]]
for i in items: print(i)
print("rows:", len(items))
if body.get("hasMore"): print("WARNING: hasMore=true, result was cut off; counts below are not reliable")
if a.out: Path(a.out).write_text(json.dumps(items, indent=1), encoding="utf-8")

if a.expect:
    names = {i["JeCategoryName"] for i in items}
    missing = [n for n in a.expect if n not in names]
    print("expected names present:", not missing, ("missing: %s" % missing) if missing else "")
    ok = not missing and not body.get("hasMore")
    if a.before_dir:
        with open(Path(a.before_dir) / "GL_JOURNAL_CATEGORY_DEF.csv", encoding="utf-8", newline="") as f:
            before = sum(1 for r in csv.DictReader(f) if r["JeCategoryName"].startswith(a.prefix))
        want = before + len(a.expect)
        print(f"count check: before export had {before} rows with prefix {a.prefix!r} + {len(a.expect)} new = {want}; REST has {len(items)}")
        ok = ok and len(items) == want
    print("REST CHECK:", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
