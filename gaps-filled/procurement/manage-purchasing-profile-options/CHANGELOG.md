# Changelog: Manage Purchasing Profile Options

- 2026-11-25, batch-02 (AB with Claude). Skill written from the read-only export, the FSCR catalog and live tries. Own test: 1 try, 5 rows processed 0 failed; REST read-back PASS.
- Test records: GAPFILL_AB_B2_PO1 (3 levels + SITE value Y; ProcessId 100004743407091).
- Fresh test: not finished (tester stopped by org spend limit). Next step: fresh test with a new name (e.g. GAPFILL_AB_B2_PO2F).
- 2026-11-25, continuation (AB with Claude): fresh tests GAPFILL_AB_B2_PO2F (100004743406790), PO3R (100004744394653), PO4R (100004744396141; connection dropped, log recovered by ProcessId). Two wording fixes, re-tested (R, R2). Status tested. Suggestions not applied: mkdir the import folder before the recovery fetch; StatusCode '(no result yet)' is normal too.
