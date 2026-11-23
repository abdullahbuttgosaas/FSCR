"""Read-only Fusion REST GET for Run 03. Refuses any method other than GET (hard rule 1).
Reuses FSCR's properties and token cache via fusion_auth.py (copy in fscr-work9); never prints the token.
Decodes gzip bodies (FSCR's REST client prints them compressed, Run 01 finding F5).
--all follows hasMore/offset paging. Writes the JSON to --out and prints a one-line summary.
Usage: rget.py /path --out file [--query k=v ...] [--all]"""
import gzip, json, sys, urllib.request, urllib.parse, urllib.error
from pathlib import Path

W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_09_impact\fscr-work9")
sys.path.insert(0, str(W / "core/auth/fusion-oauth-authentication/scripts"))
import fusion_auth as fa

args = sys.argv[1:]
if not args or args[0].upper() in ("POST", "PATCH", "PUT", "DELETE"):
    sys.exit("READ_ONLY: rget.py only performs GET")
path, out, query, page_all = args[0], None, [], False
i = 1
while i < len(args):
    if args[i] == "--out": out = args[i + 1]; i += 2
    elif args[i] == "--query": query.append(tuple(args[i + 1].split("=", 1))); i += 2
    elif args[i] == "--all": page_all = True; i += 1
    else: sys.exit(f"unknown arg {args[i]}")
props = fa.oauth_service_properties(fa.read_properties(W / "core/auth/fusionEnv.properties"), "standard")
token = fa.load_cached_access_token(props)
if not token:
    sys.exit("TOKEN_EXPIRED")


def get(q):
    url = props["restBaseUrl"].rstrip("/") + path + (("?" + urllib.parse.urlencode(q)) if q else "")
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("REST-Framework-Version", "9")
    req.add_header("Accept-Encoding", "identity")
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            raw, st = r.read(), r.status
    except urllib.error.HTTPError as e:
        raw, st = e.read(), e.code
    except urllib.error.URLError as e:
        sys.exit(f"TRANSPORT_ERROR (nothing received): {e.reason}")
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return st, raw.decode("utf-8", "replace")


st, text = get(query)
pages = 1
if st == 200 and page_all:
    d = json.loads(text)
    items = d.get("items", [])
    while d.get("hasMore"):
        q = [x for x in query if x[0] not in ("offset", "limit")] + [("limit", "500"), ("offset", str(len(items)))]
        st, t = get(q)
        if st != 200:
            break
        d = json.loads(t); items += d.get("items", []); pages += 1
    text = json.dumps({"items": items, "count": len(items), "pages": pages}, indent=1)
if out:
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(text, encoding="utf-8")
try:
    d = json.loads(text); n = d.get("count", len(d.get("items", []))) if isinstance(d, dict) else "?"
except Exception:
    n = "non-JSON"
print(f"HTTP {st} rows={n} pages={pages} -> {out}")
if st != 200:
    print(text[:1500])
