"""Seeded, stratified sample of 40 working FSCR skills (Run 05). Repeatable: same repo + same SEED = same sample.
Population: every SKILL.md (and flat task .md with a skill_id front matter) under pillars/, shared/, core/, router/ with a
`type:` in the front matter. Area by path: pillars/erp, scm, hcm, cx; shared/core/common = "SHARED".
Strata: ERP 10, SCM 10, HCM 12, CX 4, SHARED 4. Within an area, per-type quotas are proportional to that area's type mix
(largest-remainder rounding), then random.Random(SEED).sample per type.
Exclusions: the 16 e2e create skills (Run 04) and every skill exercised in Runs 01-04.
Writes evidence/sample40.json and evidence/population_counts.json."""
import json, random, re
from collections import Counter, defaultdict
from pathlib import Path

SEED = 20261103
W = Path(r"E:\GoSaaS\Configuration Automation v2.1\fscr-main\_fscr_run_05_breadth\fscr-work5")
OUT = W.parent / "evidence"
QUOTA = {"ERP": 10, "SCM": 10, "HCM": 12, "CX": 4, "SHARED": 4}
EXCLUDE_DIRS = [  # Runs 01-04 (plus the 16 create skills)
    "organization-structures", "import-price-lists", "manage-receivables-payment-terms", "manage-order-lookups",
    "apps-common/lookups", "manage-customer-uploads", "task-level-export", "task-level-compare", "setup-data-validator",
    "data-loader", "fusion-oauth-authentication", "runbook", "project-workspace-initializer", "implementation-router",
    "project-objective-classifier", "rest-api-client",
    "manage-autoaccounting-rules", "manage-autoinvoice-grouping-rules", "manage-remit-to-addresses",
    "manage-transaction-sources", "manage-transaction-types", "manage-receipt-classes-and-methods", "manage-receipt-sources",
    "manage-conversion-rates-and-policies", "manage-bank-charges", "manage-common-options-for-payables-and-procurement",
    "manage-invoice-options", "manage-payables-calendars", "manage-payment-options", "payables/manage-payment-terms",
    "manage-receivables-system-options",
]


def area(rel):
    p = rel.split("/")
    if p[0] == "pillars":
        return {"erp": "ERP", "scm": "SCM", "hcm": "HCM", "cx": "CX"}.get(p[1], "SHARED")
    return "SHARED" if p[0] in ("shared", "core") or "common" in p[:2] else None


pop = []
for f in sorted(W.glob("**/*.md")):
    rel = str(f.relative_to(W)).replace("\\", "/")
    if rel.startswith(("project/", "knowledge/", "governance/", "schemas/", "router/")) or "/references/" in rel or "/ora-resource/" in rel:
        continue
    head = f.read_text(encoding="utf-8", errors="replace")[:1500]
    if not head.startswith("---"):
        continue
    t = re.search(r'^type:\s*"?([a-z]+)"?', head, re.M)
    sid = re.search(r'^skill_id:\s*"?([^"\n]+)"?', head, re.M)
    a = area(rel)
    if not (t and sid and a):
        continue
    excluded = any(x in rel for x in EXCLUDE_DIRS)
    pop.append({"path": rel, "skill_id": sid.group(1), "type": t.group(1), "area": a, "excluded": excluded})

counts = {a: dict(Counter(p["type"] for p in pop if p["area"] == a)) for a in QUOTA}
rng = random.Random(SEED)
sample = []
for a, n in QUOTA.items():
    elig = [p for p in pop if p["area"] == a and not p["excluded"]]
    mix = Counter(p["type"] for p in elig)
    total = sum(mix.values())
    raw = {t: n * c / total for t, c in mix.items()}
    q = {t: int(v) for t, v in raw.items()}
    for t in sorted(raw, key=lambda t: raw[t] - q[t], reverse=True)[: n - sum(q.values())]:
        q[t] += 1
    by_type = defaultdict(list)
    for p in elig:
        by_type[p["type"]].append(p)
    for t in sorted(q):
        sample += rng.sample(sorted(by_type[t], key=lambda x: x["path"]), q[t])
OUT.mkdir(exist_ok=True)
(OUT / "population_counts.json").write_text(json.dumps({"seed": SEED, "total": len(pop), "excluded": sum(p["excluded"] for p in pop),
    "by_area_type": counts}, indent=1), encoding="utf-8")
(OUT / "sample40.json").write_text(json.dumps(sample, indent=1), encoding="utf-8")
print("population", len(pop), "excluded", sum(p["excluded"] for p in pop), "| by area/type", json.dumps(counts))
for i, s in enumerate(sample, 1):
    print(i, s["area"], s["type"], s["path"])
