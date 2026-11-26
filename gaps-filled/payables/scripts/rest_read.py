"""Read-only REST GET through FSCR's REST client, printing only chosen fields (never tokens or server names).

Usage (run from the FSCR root):
  python3 <this> --fscr-root . --endpoint /fscmRestApi/resources/11.13.18.05/<resource> \
      --q "Code=FSCRT_AK_GF_X" --fields Code,Name --out <WORK>/runs/x/rest.json
Prints HTTP outcome, item count and the chosen fields. Who-fields, links and e-mail-like values are hidden, also in the saved file.
Standard library only. Sign-in must already exist (FSCR token cache).
"""
import argparse, json, os, re, subprocess, sys

MAIL = re.compile(r"[^@\s]+@[^@\s]+|(?<=Submitted By: )[^.\s]+(\.[A-Za-z0-9_]+)?|(?<=SubmittedBy\W{3})[^\"\s,]+")
WHO = re.compile(r"(CreatedBy|LastUpdatedBy|UserName|LastUpdateLogin|SubmittedBy)$", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fscr-root", default=".")
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--q")
    ap.add_argument("--finder")
    ap.add_argument("--fields")
    ap.add_argument("--limit", default="25")
    ap.add_argument("--extra", action="append", default=[], help="extra key=value query params")
    ap.add_argument("--out", required=True)
    ap.add_argument("--child", help="follow this child link of the FIRST parent item (e.g. lookupCodes)")
    ap.add_argument("--child-q", help="q filter for the child GET")
    a = ap.parse_args()
    if a.child:
        tmp = a.out + ".parent.tmp"
        cli0 = os.path.join(a.fscr_root, "core/fusion-api/rest-api-client/scripts/fusion_rest_client.py")
        c0 = [sys.executable, cli0, a.endpoint, "--method", "GET", "--token-cache", "auto", "--no-open-browser",
              "--output", tmp, "--query", "limit=1"]
        if a.q:
            c0 += ["--query", "q=" + a.q]
        p0 = subprocess.run(c0, cwd=a.fscr_root, capture_output=True, text=True)
        try:
            d0 = json.load(open(tmp, encoding="utf-8"))
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
        if p0.returncode != 0 or not d0.get("items"):
            print("parent not found (exit %s)" % p0.returncode)
            return 1
        href = [l["href"] for l in d0["items"][0].get("links", []) if l.get("rel") == "child" and l.get("name") == a.child]
        if not href:
            print("parent has no child link", a.child)
            return 1
        a.endpoint = re.sub(r"^https?://[^/]+", "", href[0])
        a.q = a.child_q
    cli = os.path.join(a.fscr_root, "core/fusion-api/rest-api-client/scripts/fusion_rest_client.py")
    cmd = [sys.executable, cli, a.endpoint, "--method", "GET", "--token-cache", "auto", "--no-open-browser",
           "--output", a.out, "--query", "limit=" + a.limit, "--query", "onlyData=true"]
    if a.q:
        cmd += ["--query", "q=" + a.q]
    if a.finder:
        cmd += ["--query", "finder=" + a.finder]
    for e in a.extra:
        cmd += ["--query", e]
    p = subprocess.run(cmd, cwd=a.fscr_root, capture_output=True, text=True)
    err = re.sub(r"https?://\S+", "<url>", (p.stderr or "") + (p.stdout or ""))
    err = MAIL.sub("<hidden>", err)
    if p.returncode != 0:
        print("REST GET failed, exit", p.returncode, "\n", err[-1500:])
        return p.returncode
    try:
        d = json.load(open(a.out, encoding="utf-8"))
    except Exception:
        print("response is not JSON; saved to the run folder")
        return 0
    def scrub(o):
        if isinstance(o, dict):
            return {k: ("<hidden>" if WHO.search(k) or MAIL.search(str(v)) else scrub(v))
                    for k, v in o.items() if k != "links"}
        if isinstance(o, list):
            return [scrub(x) for x in o]
        return o
    d = scrub(d)
    with open(a.out, "w", encoding="utf-8") as fh:  # saved file keeps no user names
        json.dump(d, fh, indent=1)
    items = d.get("items", [d] if isinstance(d, dict) else [])
    print("OK, items:", len(items), "hasMore:", d.get("hasMore"))
    fields = a.fields.split(",") if a.fields else None
    for it in items[:50]:
        shown = {k: ("<hidden>" if WHO.search(k) or MAIL.search(str(v)) else v)
                 for k, v in it.items() if (fields is None or k in fields) and not isinstance(v, (list, dict))}
        print(shown)
    return 0


if __name__ == "__main__":
    sys.exit(main())
