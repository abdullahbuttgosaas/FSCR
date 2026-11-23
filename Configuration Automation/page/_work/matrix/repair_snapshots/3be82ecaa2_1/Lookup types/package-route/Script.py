import zipfile, io, difflib

def flatten(z, prefix=""):
    out = {}
    for n in z.namelist():
        if n.endswith("/"):
            continue
        data = z.read(n)
        path = prefix + n
        if n.lower().endswith(".zip"):
            try:
                out.update(flatten(zipfile.ZipFile(io.BytesIO(data)), path + "!/"))
                continue
            except zipfile.BadZipFile:
                pass
        out[path] = data
    return out

a = flatten(zipfile.ZipFile("baseline.zip"))
b = flatten(zipfile.ZipFile("postchange.zip"))

print("=== FILE TREE (post-change) ===")
for p in sorted(b):
    print(f"{len(b[p]):>10} bytes  {p}")

print("\nOnly in baseline:", sorted(set(a) - set(b)))
print("Only in post-change:", sorted(set(b) - set(a)))

print("\n=== CHANGED FILES ===")
for p in sorted(set(a) & set(b)):
    if a[p] != b[p]:
        ta = a[p].decode("utf-8", "replace").splitlines()
        tb = b[p].decode("utf-8", "replace").splitlines()
        d = [l for l in difflib.unified_diff(ta, tb, lineterm="", n=0)
             if l[:1] in "+-" and l[:3] not in ("+++", "---")]
        print(f"{len(d):>6} diff lines  {p}")

print("\n=== ZZ_POC_TEST hits ===")
with open("poc_hits.txt", "w", encoding="utf-8") as out:
    total = 0
    for p in sorted(b):
        text = b[p].decode("utf-8", "replace")
        idx = text.find("ZZ_POC_TEST")
        while idx != -1:
            total += 1
            out.write(f"\n----- {p} @ char {idx} -----\n")
            out.write(text[max(0, idx - 400): idx + 600] + "\n")
            idx = text.find("ZZ_POC_TEST", idx + 600)
    print("total hits:", total)