# Procurement: demo reserve (2 tasks kept open for a live demo)

Picked 2026-11-25 by AB with Claude, before any Procurement task was filled. These 2 tasks are **not filled, loaded or tested in any sitting**. Their status stays `open`, reason "reserved for live demo".

| Task code | Task name | Why it was picked | Where the record shows in Fusion |
|---|---|---|---|
| PO_MANAGE_FOB_LOOKUP | Manage FOB Lookup | Easiest task in the module: one new lookup code (for example `GAPFILL_AB_DEMO_FOB`) on the seeded, extensible lookup type `FOB` ("Valid FOB Codes"). Known route: the standard lookup FSM CSV package (same 3 files as `common-features/manage-standard-lookups`). No prerequisite. Stand-alone: nothing else uses a new code. | Setup and Maintenance > Procurement > Procurement Foundation > **Manage FOB Lookup** (search type FOB, the new code is in the list). Also the **FOB** list on a purchase order's Terms. |
| PO_MANAGE_FREIGHT_TERM_LOOKUP | Manage Freight Terms Lookup | Same pattern as FOB: one new lookup code on the seeded, extensible type `FREIGHT TERMS` ("Valid Freight Terms"). Same package, no prerequisite, stand-alone. | Setup and Maintenance > Procurement > Procurement Foundation > **Manage Freight Terms Lookup**. Also the **Freight Terms** list on a purchase order's Terms. |

## Read-only checks done (no load)
- FSM CSV export of each task: OK, 3 files (`ASM_SETUP_CSV_METADATA.xml`, `FND_APP_STANDARD_LOOKUP.csv`, `ORA_FND_APP_STANDARD_LOOKUP_CODE.csv`), 0 rows each. The export scope is the one lookup type (`lookupType` = `FOB` / `FREIGHT TERMS`, mode `edit`). VERIFIED
- REST GET `standardLookups/FOB` and `standardLookups/FREIGHT TERMS`: both exist, `CustomizationLevel` = `E` (extensible: new codes allowed), same ModuleId. VERIFIED
- Because the export has 0 rows, a load must carry the seeded type row **unchanged** (built from the REST read) plus the new code row. The same pattern is tested in this module on `OKC_SUBJECT` (Manage Contract Clause Types, folder `manage-contract-clause-types`), so the demo can follow that skill with the task code changed.

## For the demo
1. Run the export (read only), show the scope.
2. Build the package with the type row unchanged + one new `GAPFILL_AB_DEMO_...` code.
3. Import, show the ProcessId and "0 rows failed".
4. Open the Fusion screen above and show the new code.

Do not reuse these names in a test before the demo.
