# Procurement batch 05: result (2026-11-25, sitting 3, AB with Claude)

Only task this run: **Manage FOB Lookup** (`PO_MANAGE_FOB_LOOKUP`), released from the demo reserve and filled for the demo. Batch size 1, sitting limit 1. Manage Freight Terms Lookup stays reserved and untouched.

| Task | Status | Write / test / wait min | Test records |
|---|---|---|---|
| Manage FOB Lookup | **tested** (FSM CSV + REST read-back) | 4 / 12 / 5 | own `GAPFILL_AB_B5_FOB1` (100004744393796); fresh F `GAPFILL_AB_B5_FOB2F` not created (network drop before a ProcessId); re-test `GAPFILL_AB_B5_FOB3R` (100004744397138) |

## Time log
| Step | Start | Finish | Minutes | Kind |
|---|---|---|---|---|
| Read context, gap index, reserve note, helpers | 19:30 | 19:40 | 10 | working (reading, not counted in the task) |
| Sign-in (cached token had expired) | 19:40 | 19:42 | 2 | waiting |
| Read-only export + REST read of type FOB | 19:42 | 19:43 | 1 | waiting |
| Build package, import, read back, after-export | 19:43 | 19:45 | 2 own test (+2 waiting) | working / waiting |
| SKILL.md written, evidence 01-04 | 19:45 | 19:49 | 4 | working |
| Fresh round F (dropped connection) | 19:46 | 19:55 | 9 | working |
| Check nothing created, wording fix, round R | 19:55 | 19:58 | 3 | working |
| Cards, tracker, reports, index | 19:58 | 20:05 | 7 | working (not counted in the task) |

## Problems and findings
1. The cached sign-in had expired: the first REST read hung (stopped by a 90 s timeout); new sign-in at 19:42.
2. Round F: the import broke with "Remote end closed connection without response" **before** Oracle gave a ProcessId. The tester did not import again. REST (8 reads over 7 minutes, plus mine at 19:55) and a new export prove `GAPFILL_AB_B5_FOB2F` was not created and nothing changed. The skill had no rule for a drop with no ProcessId: added (poll REST for 10 minutes, prove with the export, a second try needs approval), plus "run Step 4 also after a failed import" and an empty-grep note. Re-test R passed with no wrong sentence.
3. Export behaviour: the first export was empty although type FOB has a seeded code (`NONE`); after the first import the export holds the type row and its codes. So the load carries the seeded type row unchanged from REST (same as Contract Clause Types).
4. Suggestions not applied (each would need another re-test): safe row-count line in Step 1, after-export command written out, MEANING-unique check command, no "|" in MEANING/DESC, unattended run must stop on 401/403.

## For the demo slides
- Record to open in Fusion: lookup code **`GAPFILL_AB_B5_FOB1`** ("GAPFILL AB Demo FOB Point 1") on lookup type **`FOB`** ("Valid FOB Codes").
- Screen: Setup and Maintenance > Procurement > Procurement Foundation > **Manage FOB Lookup** (the type FOB, then its codes). The fresh-test code `GAPFILL_AB_B5_FOB3R` shows in the same list.
- Images: `evidence/batch-05/PO_MANAGE_FOB_LOOKUP/01_missing.png` to `05_fresh_test.png`.

## What is left
Procurement: 6 open (Manage Freight Terms Lookup, reserved for the demo; 4 approval tasks and task configurations).
