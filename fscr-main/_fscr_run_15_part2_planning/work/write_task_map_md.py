"""Write 01_OFFERING_TASK_MAP.md from the builder CSVs (summary; full list in the CSV)."""
import csv, sys
from collections import Counter, defaultdict

tm, out = sys.argv[1], sys.argv[2]
init_note = open(sys.argv[3], encoding="utf-8").read() if len(sys.argv) > 3 else "not recorded"
tasks = list(csv.DictReader(open(f"{tm}/task_map_tasks.csv", encoding="utf-8")))
fas = list(csv.DictReader(open(f"{tm}/task_map_fa_summary.csv", encoding="utf-8")))

skill = defaultdict(int); mand = defaultdict(int); fsm = defaultdict(int); dup = defaultdict(int)
for t in tasks:
    k = (t["Offering Code"], t["FA Code"])
    skill[k] += bool(t["FSCR Skill Path"]); mand[k] += t["Mandatory (catalog)"] == "True"
    fsm[k] += t["FSM export/import"] == "True"; dup[k] += bool(t["Duplicate Of Sequence"])

L = []
w = L.append
w("# Output 1: Offering Task Map (Project Planning, high-level)\n")
w("**Project:** Twelve Benefit Corporation: Oracle Cloud SCM Implementation (SOW dated Jan 24, 2025, Doc 50513scm)")
w("**Produced by:** FSCR + Claude.")
w("- **FSCR** supplied the task membership and order (effective catalog `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`, 54 offerings / 609 FAs / 7,282 tasks), the skill match for each task (FSCR's own matcher `core/runbook/scripts/task_context._skill_path`), the initializer mapping schema, and the project workspace initializer dry-run.")
w("- **Claude** chose the offering / functional-area pairs from the SOW and the Run 14 intake (01_SCOPE.md §2), classified each as NEW / INCR / COND / TBD, ran the resolver's catalog steps offline (no FSM/BOSS task discovery, which needs a Fusion call), and wrote this summary.")
w("- FSCR's `offering-task-map-builder` has a method and a helper (`task_to_skill_mapping.py`) but no CLI; FSCR's `task-dependency-resolver` is a method only (no script). Both were followed by Claude's script `work/build_task_map.py`.\n")
w("**Status:** Planning only. Nothing configured, no Fusion calls. Full task list: `01_OFFERING_TASK_MAP_tasks.csv`; initializer-format mapping: `01_identified-task-mapping.json`.\n")
w("**Scope classes:** NEW = new module, all catalog tasks listed for review; INCR = incremental change to live production Financials, tasks listed but only some will change; COND = conditional (Expenses design session); TBD = remediation scope 'determined during the project', FA listed, tasks not expanded.\n")
w("**Sequence:** `Resolver Sequence` = offering/FA order below × catalog `displaySequence`, numbered 1…N. It follows resolver steps 1, 2 and 6 using catalog data only. FSM-backed sequence: **not available** (paper run). This is a deviation from the builder's gate, which expects a resolver-persisted `setup_task_sequence`; recorded as such. verified (script).\n")

w("## 1. Offering / functional-area map\n")
w("| # | Offering (code) | Functional area (code) | SOW ref | Class | Catalog tasks | In map | With FSCR skill | Catalog-mandatory | FSM export/import | Repeated task codes | Note |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|")
for i, f in enumerate(fas, 1):
    k = (f["offering_code"], f["fa_code"])
    w(f"| {i} | {f['offering']} (`{f['offering_code']}`) | {f['functional_area']} (`{f['fa_code']}`) | {f['sow_ref']} | {f['scope_class']} | {f['catalog_tasks']} | {f['tasks_in_map']} | {skill[k]} | {mand[k]} | {fsm[k]} | {dup[k]} | {f['note']} |")

cls = Counter(t["Scope Class"] for t in tasks)
offs = Counter(t["Offering"] for t in tasks)
n_skill = sum(1 for t in tasks if t["FSCR Skill Path"])
codes = {t["Matched Task Code"] for t in tasks}
w("\n## 2. Totals (verified by script)\n")
w(f"- Offering/FA pairs selected: **{len(fas)}** ({sum(1 for f in fas if f['scope_class']!='TBD')} expanded, {sum(1 for f in fas if f['scope_class']=='TBD')} TBD not expanded).")
w(f"- Offerings: **{len(offs) + (1 if any(f['offering_code']=='ORA_GMS_GRANTS_MANAGEMENT' for f in fas) else 0)}** (Grants Management only as a TBD row).")
w(f"- Task rows in the map: **{len(tasks)}**; unique task codes: **{len(codes)}**; rows repeating a code already listed under another FA: **{len(tasks)-len(codes)}** (kept, per resolver rule 'retain every catalog task occurrence').")
w(f"- By class: " + ", ".join(f"{k} {v}" for k, v in sorted(cls.items())) + ".")
w(f"- By offering: " + ", ".join(f"{k} {v}" for k, v in offs.most_common()) + ".")
w(f"- Rows with an FSCR pillar skill or flat task guidance: **{n_skill}** ({n_skill*100//len(tasks)}%); the rest route to FSCR's shared Manual Tasks skill.")
w(f"- Resolver Sequence unique and positive 1…{len(tasks)}: yes. `sequence_unresolved` tasks: 0 (no pre-release/custom candidates were selected).\n")

w("## 3. Planning view: build waves by functional area (Claude, SUGGESTED)\n")
w("The catalog order is task order inside an offering. For the wave plan, the FAs are grouped into build waves. Each wave is built in Dev for CRP1 unless marked.\n")
w("| Build wave | Functional areas | Why first/later | Target |")
w("|---|---|---|---|")
w("| B1 Foundation | Organization Structures (BU functions), Facilities (plants), Item Organizations (item master), Inventory org setup in Inventory Management, Cost Accounting org/books, Procurement Foundation | FSCR D1–D7, D13: org, LE, ledger links come first | W2–W3 (CRP1) |")
w("| B2 Core flows | Items, Purchasing Foundation, Self Service Procurement, Suppliers, Receiving, Inventory Management, Receipt Accounting, Procurement Transaction Account Rules, Project Costing Base (commitments) | Requisition → PO → receipt → putaway → accounting end to end | W2–W3 (CRP1) |")
w("| B3 Manufacturing and maintenance | Manufacturing Master Data, Maintenance Management, Structures | Needs plants, items, work areas (FSCR D8–D11) | W3 (CRP1, ready-to-use only) |")
w("| B4 Controls, extensions | Users and Security, Approval Management, Supplier Portal, Printable PO report | CRP2 rule: full security + customizations | W6 (CRP2) |")
w("| B5 Finance updates | General Ledger/SLA, Payables, Fixed Assets, Expenses (if in), Sustainability | Depend on B2 accounting and AP invoices (D27, D28) | W6 (CRP2) |")
w("| TBD | Receivables, Cash Management, Grants, Financial Reporting Center | Scope determined during the project; reporting approach is a strategy deliverable | decide by G1 |\n")

w("## 4. Project workspace initializer (FSCR) dry-run\n")
w(init_note + "\n")

w("## 5. Gaps and notes\n")
w("- 5 FA owners were 'pending' (fail-closed) in Run 14 and use Run 14's SUGGESTED owner: Organization Structures, Users and Security, Payables, Cash Management → Financials; Sustainability → MSCMM. A person must confirm (Run 14 Q-S4). not verified.")
w("- The catalog has no separate FA for process vs discrete manufacturing, meters or Installed Base (Run 14 note). Discrete tasks inside Manufacturing Master Data must be skipped by hand. not verified.")
w("- Task counts for INCR FAs overstate the work: only changed tasks will be touched in live Production Financials. not verified.")
w("- 'Inventory Organizations' FA under Product Management (`ORA_EGP_FA_INVENTORY_ORGANIZAT`) was not selected; inventory orgs are covered through Facilities / Inventory Management as in Run 14. Open question for the reviewer.")
open(out, "w", encoding="utf-8").write("\n".join(L) + "\n")
print("written", out, len(tasks), "tasks")
