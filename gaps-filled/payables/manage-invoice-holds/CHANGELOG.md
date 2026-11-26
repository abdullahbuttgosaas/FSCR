# CHANGELOG - Manage Invoice Holds and Releases

## 2026-11-25 (sitting 1, batch 01)
- Own test: FSCRT_AK_GF_HLD1 (INVOICE HOLD REASON). Import ProcessId 100004744396632: 1 row processed, 0 failed.
  Export before 109 rows, after 110, only this row added. REST probes payablesHoldCodes / invoiceHoldCodes: 404.
- Fresh test F: FSCRT_AK_GF_HLD1F, ProcessId 100004744393889, PASS (110 -> 111).
- Fixes after the fresh test (tester error 1 and suggestions):
  - worked example: row counts are environment-specific; only "+1, removed/changed 0" matters (was a wrong
    universal count);
  - added `<YOUR_TEST_PREFIX>` to placeholders; create `<RUN>` first; do not share `<RUN>`;
  - `--grep` matches parts of codes: look for an exact match;
  - "StatusCode: (unknown)" console lines are normal; the process log decides;
  - sign-in: stop and report when not allowed to sign in.
- Retest R: FSCRT_AK_GF_HLD1R, ProcessId 100004744391997, PASS (111 -> 112), no errors reported.
- Own read-back of all three records: final export shows HLD1, HLD1F, HLD1R; compare with the first export:
  added 3, removed/changed 0.
- Tester suggestions not applied (no errors): move the existence check after the Export section; quote the
  full RESULT line; give a --grep example; put the "not allowed to sign in" exception first.
- Finding (later in batch 01, from the Payables lookups export): each new hold name also creates a lookup
  code with the same name under lookup type HOLD CODE (Payables lookups, ViewApplicationId 200). This is done
  by Oracle; no extra row is needed. Not a wording change to the skill.
