"""Extract 'Required Dependency Order' tables from in-scope FSCR pillar dependency files (read-only)."""
import glob, os, re, sys

root = sys.argv[1]
pat = re.compile(r"pillars/(scm/(manufacturing|procurement|product-management)|erp/(financials|project)|common/security)")
files = []
for f in glob.glob(os.path.join(root, "pillars", "**", "ora_dependency_readiness.md"), recursive=True):
    rel = os.path.relpath(f, root).replace(os.sep, "/")
    if pat.search(rel):
        files.append(rel)
print(len(files), "in-scope dependency files")
for rel in sorted(files):
    t = open(os.path.join(root, rel), encoding="utf-8").read()
    m = re.search(r"## Required Dependency Order\s*\n(.*?)(\n## |\Z)", t, re.S)
    if not m:
        continue
    rows = [l for l in m.group(1).splitlines() if l.startswith("|") and not l.startswith("|---") and "Sequence" not in l]
    print("##", rel.replace("/ora-resource/ora_dependency_readiness.md", ""))
    for r in rows:
        c = [x.strip() for x in r.strip().strip("|").split("|")]
        print("  -", c[1] if len(c) > 1 else c, "::", (c[2][:160] if len(c) > 2 else ""))
