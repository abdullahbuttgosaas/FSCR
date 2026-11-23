"""Fetch a Fusion SOAP XSD (recursively follows imports within the same service) and print complexType field names. Read-only."""
import re, subprocess, sys, os
svc, root = sys.argv[1], sys.argv[2]
want = set(sys.argv[3:])
E = r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_01"
seen, queue = set(), [root]
while queue:
    x = queue.pop(0)
    if x in seen: continue
    seen.add(x)
    out = os.path.join(E, "evidence", "soap", svc + "_" + os.path.basename(x))
    subprocess.run([sys.executable, os.path.join(E, "scripts", "rest_diag.py"), "GET", f"/crmService/{svc}", "--query", f"XSD={x}", "--out", out], capture_output=True)
    if not os.path.exists(out): continue
    s = open(out, encoding="utf-8").read()
    for imp in re.findall(r'schemaLocation="[^"]*XSD=([^"]*)"', s):
        if "/xml/" not in imp and "META-INF" not in imp: queue.append(imp)
    for m in re.finditer(r'<xsd:complexType name="([^"]+)"(.*?)</xsd:complexType>', s, re.S):
        if not want or m.group(1) in want:
            print("##", m.group(1), ":", " ".join(re.findall(r'<xsd:element[^>]*name="([^"]+)"', m.group(2))))
