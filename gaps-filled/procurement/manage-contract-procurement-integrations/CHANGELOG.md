# Changelog: Manage Contract and Procurement System Integrations

- 2026-11-25, batch-01 (AB with Claude). Skill written from the read-only export, the FSCR catalog and live tries. Tries 1-3 refused (URL, then User Name required), nothing created; round trip created TS4R. Oracle set InactiveDate to the load time and kept isdeleteDisabled=Y on the copied row.
- Test records: GAPFILL_AB_B1_TS1, TS2, TS3 refused (not created; ProcessIds 100004744391264, 100004743405950, 100004744393274); GAPFILL_AB_B1_TS4R round trip created (100004744392872); fresh GAPFILL_AB_B1_TS5F NOT created (tester stopped after its export).
- Fresh test: not finished (tester stopped by org spend limit). Next step: fresh test of path A with a new name (e.g. GAPFILL_AB_B1_TS6F).
- 2026-11-25, continuation (AB with Claude): fresh tests GAPFILL_AB_B1_TS6F (100004744393438), TS7R (100004744395059), TS8R (100004743407825); path A (internal). Two wording fixes, re-tested (R, R2). Status tested. Suggestions not applied: Step 3 code block: add `> "<RUN>/import.out" 2>&1`; worked-example counts are old (skill already says counts grow).
