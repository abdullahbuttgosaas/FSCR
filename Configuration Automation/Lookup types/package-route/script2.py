import zipfile, io, gzip, re, difflib

GUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

def flatten(z, prefix=""):
    out = {}
    for n in z.namelist():
        if n.endswith("/"):
            continue
        data = z.read(n)
        path = GUID.sub("<GUID>", prefix + n)
        low = n.lower()
        if low.endswith(".zip"):
            try:
                out.update(flatten(zipfile.ZipFile(io.BytesIO(data)), path + "!/"))
                continue
            except zipfile.BadZipFile:
                pass
        if low.endswith(".gz"):
            try:
                data = gzip.decompress(data)
                path = path[:-3]
            except OSError:
                pass
        out[path] = data
    return out

a = flatten(zipfile.ZipFile("baseline.zip"))
b = flatten(zipfile.ZipFile("postchange.zip"))

only_a, only_b = sorted(set(a) - set(b)), sorted(set(b) - set(a))
print("Only in baseline:", only_a)
print("Only in post-change:", only_b)

print("\n=== ZZ_POC_TEST in decompressed files ===")
for label, d in (("baseline", a), ("post", b)):
    for p in sorted(d):
        if b"ZZ_POC_TEST" in d[p]:
            print(label, "->", p)

print("\n=== NEW FILES (content) ===")
for p in only_b:
    if p.endswith(".xls"):
        continue
    print(f"\n--- {p} ({len(b[p])} bytes) ---")
    print(b[p].decode("utf-8", "replace")[:6000])

print("\n=== CHANGED FILES (diff, non-report only) ===")
for p in sorted(set(a) & set(b)):
    if a[p] != b[p] and not p.endswith(".xls") and not p.startswith("SETUP_DATA_REPORT"):
        print(f"\n--- {p} ---")
        d = [l for l in difflib.unified_diff(
                a[p].decode("utf-8", "replace").splitlines(),
                b[p].decode("utf-8", "replace").splitlines(),
                lineterm="", n=0)
             if l[:1] in "+-" and l[:3] not in ("+++", "---")]
        for l in d[:40]:
            print(l[:300])