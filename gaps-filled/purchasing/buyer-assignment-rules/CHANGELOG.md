# CHANGELOG: Manage Buyer Assignment Rules

- 25/11/2026 (sitting 1, batch 02): skill written, not tested (unsafe to test, see STATUS.md). Read-only export only:
  1 CSV (ORA_PO_BUYER_ASSIGNMENT_RULES.csv), 2 existing rules in rule set DEFAULT. No test records.
- 26/11/2026: placeholder `S` changed to `$S` and REST output redirect added (common wording fix from the other skills' fresh tests).
- 26/11/2026: environment confirmed test-only by the tester; skill rewritten from a live test. Own test: import 100004744422117, after-export 100004743447698.
- Fresh test F: rule 9998, import ProcessId 100004743454843, after-export 100004744417713: PASS; reported example sequence 9999 already taken and column-order wording.
- Fresh test R: rule 10007, import ProcessId 100004743454882, after-export 100004743454893: PASS; reported that the script stopped before printing sequences.
- Fresh test 2R: rule 10008, import ProcessId 100004743436885, after-export 100004743447880: PASS; no factual error.
- Wording fixes after the fresh tests: see the findings above (each fixed before the next retest).
- Tester suggestions not applied (not errors): make the script also refuse free numbers below the existing rules, or add a list-only mode; heredoc placeholders typed by hand.
