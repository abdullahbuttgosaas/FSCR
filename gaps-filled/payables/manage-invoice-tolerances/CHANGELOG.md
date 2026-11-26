# CHANGELOG - Manage Invoice Tolerances

## 2026-11-25 (sitting 1, batch 01)
- Own test: FSCRT_AK_GF_TOL1 (QUANTITY BASED, 2/5/5). Import ProcessId 100004744396658: 1 row processed, 0 failed.
  Export before 3 rows, after 4, only this row added. REST payablesInvoiceTolerances: 1 item.
  Finding: REST `q` needs lower-case attribute names (`toleranceName`); `ToleranceName` gives HTTP 400.
- Fresh test F: FSCRT_AK_GF_TOL1F, ProcessId 100004744403910, PASS (4 -> 5, REST 1 item).
  Tester errors: (1) worked-example counts read as universal; (2) rest_read.py saved the full JSON including
  who-fields (user names) into the run folder. The tester also printed that file once in its own tool output
  (not saved anywhere, not in its report).
- Fixes: rest_read.py now removes who-fields, links and e-mail-like values from the JSON it saves; SKILL
  worked example says counts are environment-specific; added `<YOUR_TEST_PREFIX>`, create/do-not-share `<RUN>`,
  "StatusCode (unknown) is normal", sign-in exception, neutral description note, full RESULT line.
- Retest R: FSCRT_AK_GF_TOL1R, ProcessId 100004744397350, PASS (5 -> 6, REST 1 item), no errors.
- Own read-back: REST lists TOL1, TOL1F, TOL1R with their values.
- Tester suggestions not applied: show a token-cache check command; say --prefix is checked on the whole row;
  point to the "== log" part of the output; Windows `python` + PYTHONUTF8=1 note; AMOUNT BASED stays GUESS.
