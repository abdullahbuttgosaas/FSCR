# Changelog: Manage Special Handling Types

- 2026-11-25, batch-01 (AB with Claude). Skill written from the read-only export, the FSCR catalog and live tries. Own test: 1 try, 1 row processed 0 failed; Oracle made a new SpecialHandlingTypeId; empty contexts accepted.
- Test records: GAPFILL_AB_B1_SH1 (ProcessId 100004743406576); fresh GAPFILL_AB_B1_SH2F NOT created (tester stopped after its export).
- Fresh test: not finished (tester stopped by org spend limit). Next step: fresh test with a new name (e.g. GAPFILL_AB_B1_SH3F), then set tested.
- 2026-11-25, continuation (AB with Claude): fresh tests GAPFILL_AB_B1_SH3F (100004744394175), SH4R (100004744394477; connection dropped, log recovered by ProcessId), SH5R (100004744393577). Two wording fixes, re-tested (R, R2). Status tested. Suggestions not applied: Step 1: warn not to print audit columns when looking at the export.
