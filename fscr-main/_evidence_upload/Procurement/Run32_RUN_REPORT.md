# Run 32: how well does FSCR cover Procurement?

Paper review, same method as Run 29. **No Oracle calls; nothing changed outside this folder.** Files: `procurement_tasks.csv` (167 tasks), `area_counts.csv`, `scripts/build.py`.

| Start | Finish | Minutes |
|---|---|---:|
| 2026-11-17 01:01 | 2026-11-17 01:01 | n/a: start was stamped when the folder was created, after reading the catalog; true total not recorded |

## Scope and method (VERIFIED, `scripts/build.py`)
- Catalog areas taken: Purchasing Foundation, Purchasing Categories, External Purchase Prices, Procurement Foundation, Approval Management, Procurement Transaction Account Rules, Self Service Procurement, Procurement Contracts, Compliance Checklists, Suppliers (supplier model), Sourcing, Supplier Qualification, Supplier Portal. Tasks pooled across every offering that lists these areas (Procurement, Manufacturing and Supply Chain, Product Management, Enterprise Contracts), counted once by task code.
- **35 tasks removed** because Run 29 already counts them (shared ORA_ASK_ setup such as locations, legal entity, chart of accounts, business units).
- Levels use Run 29 / Run 07 rules: **a** = has an FSCR skill or guide; **b** = no skill, catalog CSV flag Y; **c** = neither. Skill-but-no-route is reported separately.
- Not counted (borderline, sensitivity rows in `area_counts.csv`): Items 36, Receiving 6, Receipt Accounting 16, Supplier Incentives 32, Sustainability 7, Suppliers for Product Management 1, Payables 38. Adding them would change every total.

## Counts
| Tag | Tasks | a | b | c | Missing (no skill) |
|---|---:|---:|---:|---:|---:|
| Procurement | 52 | 17 | 25 | 10 | 35/52 |
| Sourcing and Supplier Management | 91 | 45 | 35 | 11 | 46/91 |
| Purchasing | 16 | 6 | 9 | 1 | 10/16 |
| Shared | 8 | 4 | 0 | 4 | 4/8 |
| **Procurement row (SCM 24) = Procurement + Shared** | **60** | 21 | 25 | 14 | **39/60** |
| All in scope | 167 | 72 | 69 | 26 | 95/167 |

- **Skill but no route: yes, 9 tasks** (all supplier-portal, approval or import tasks; the skill names no CSV or REST route). Counting them strictly, a = 63 with skill and route.
- Shared = task sits in areas I mapped to different tags (8 tasks, mostly approvals and supplier-portal tasks).

## Proposed coverage: **Partial** (GUESS, from the counts)
72 of 167 tasks (43%) have a skill. Supplier setup (37 of 65), Procurement Foundation (10 of 15) and Self Service Procurement (6 of 11) have skills, so the core is touched. But whole areas have none, so this is not Full.

## Weakest areas (missing / total)
Procurement Contracts 10/10 · Procurement Transaction Account Rules 9/9 · Compliance Checklists 3/3 · Purchasing Foundation 9/11 · Approval Management 9/14 · Supplier Qualification 12/19. Strongest: Purchasing Categories 0/3, Supplier Portal 1/7.

## What I could not determine
- **Row tags are my area-level mapping** (Sourcing, Supplier Qualification, Supplier Portal, Suppliers → Sourcing and Supplier Management; Purchasing Foundation, Categories, External Purchase Prices → Purchasing; the rest → Procurement). I found no tracker file defining the rows, so please check it. Moving an area changes the per-tag numbers, not the 167 total.
- Whether the borderline areas belong in scope.
- REST support for tasks without a skill was not scanned (same caveat as Run 29); skill quality and whether skills work were not tested.
- Counts rely on Run 07 `tasks.csv`; I did not rebuild it.

**Clean-up:** no servers or browsers started. One slow background search was stopped. Nothing is running.
