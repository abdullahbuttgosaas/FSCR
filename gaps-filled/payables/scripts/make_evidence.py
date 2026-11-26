"""Write the evidence text files for one task and scan them.

Evidence goes to gaps-filled/payables/evidence/batch-NN/<TASK_CODE>/ as UTF-8 .txt files
(01_missing, 02_found, 03_skill, 04_test_result, 05_fresh_test). The pack's CLAUDE.md allows PNG images only
through module-test-kit/scripts/make_images.py (max 4), so gap-fill evidence stays text.

Input: a JSON spec {"task_code":..., "batch":"01", "files": {"02_found": "text", ...}}. 01_missing and 03_skill
are generated (from scope_tasks.csv and the SKILL.md). Every file is scanned: e-mail-like values, http(s)
addresses, the configured environment name, host names and the person's sign-in names (read from the
properties file / names file at run time, never printed) must not appear. Exit 1 if the scan finds one.

Usage: python3 make_evidence.py spec.json [--names @<file with one name per line>]
Standard library only.
"""
import argparse, csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
PACK = os.path.dirname(os.path.dirname(MOD))


def secrets_to_block(names_file):
    block = []
    props = os.path.join(PACK, "core", "auth", "fusionEnv.properties")
    if os.path.exists(props):
        for line in open(props, encoding="utf-8"):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                v = v.strip()
                if k.strip() in ("environment", "restBaseUrl", "clientId") and len(v) > 3:
                    block.append(v)
                    if "://" in v:
                        block.append(v.split("://", 1)[1].split("/")[0])
    if block:
        env = block[0]
        block += [env.lower(), env.upper()]
    if names_file and os.path.exists(names_file):
        block += [l.strip() for l in open(names_file, encoding="utf-8") if len(l.strip()) > 2]
    return [b for b in block if b]


def scan(text, block):
    hits = []
    if re.search(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", text):
        hits.append("e-mail-like value")
    if re.search(r"https?://(?!docs\.oracle\.com|github\.com/oracle)", text):
        hits.append("server address")
    for b in block:
        if b.lower() in text.lower():
            hits.append("blocked value (environment/host/client/name)")
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--names")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    code = spec["task_code"]
    folder = os.path.join(MOD, "evidence", "batch-" + spec["batch"], code.replace(":", "-"))
    os.makedirs(folder, exist_ok=True)
    scope = {r["task_code"]: r for r in csv.DictReader(open(
        os.path.join(PACK, "evidence", "Payables", "data", "scope_tasks.csv"), encoding="utf-8"))}
    r = scope[code]
    files = {
        "01_missing": (f"01 MISSING - {code}\nTask: {r['task_name']}\nModule: Payables\n"
                       f"Coverage level in evidence/Payables/data/scope_tasks.csv: {r['level']} "
                       f"({'route only' if r['level'] == 'b' else 'neither'}); FSCR skill or guide: {r['skill_or_guide']}\n"
                       f"Catalog CSV export/import flag: {r['csv_flag']}\n"
                       "Source: evidence/Payables/data/scope_tasks.csv\n"),
    }
    files.update(spec.get("files", {}))
    skill = spec.get("skill")
    if skill:
        sk = open(os.path.join(MOD, skill), encoding="utf-8").read()
        heads = [l for l in sk.splitlines() if l.startswith("#")]
        files["03_skill"] = (f"03 SKILL - {code}\nFile: gaps-filled/payables/{skill}\nSections:\n  " +
                             "\n  ".join(heads) + f"\nLength: {len(sk.splitlines())} lines\n")
    block = secrets_to_block(a.names)
    bad = False
    for name, text in sorted(files.items()):
        if not text.endswith("\n"):
            text += "\n"
        text += f"\n-- source: gaps-filled/payables/evidence/batch-{spec['batch']}/{code.replace(':', '-')}/{name}.txt\n"
        hits = scan(text, block)
        if hits:
            bad = True
            print(f"{name}: NOT written, scan found: {sorted(set(hits))}")
            continue
        with open(os.path.join(folder, name + ".txt"), "w", encoding="utf-8") as fh:
            fh.write(text)
    print("evidence:", os.path.relpath(folder, MOD), "files", sorted(files), "scan", "FAILED" if bad else "clean")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
