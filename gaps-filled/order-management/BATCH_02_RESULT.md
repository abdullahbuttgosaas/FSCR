# Batch 02 - Order Management gap fill (sitting 1, 2026-11-26)

## Time log
| Step | Start | End | Kind |
|---|---|---|---|
| Read-only exports (5 tasks, parallel) | 17:33 | 17:33 | waiting |
| Results Presentation + Pricing Total imports (total try 1 refused, try 2 ok), read-back | 17:33 | 17:37 | working 3 / waiting 2 |
| Time unit: own unit by REST (2 refusals diagnosed, wrapper to read Oracle's gzipped error), mapping import, read-back | 17:37 | 17:42 | working 4 / waiting 2 |
| External service (3 tries), read-back with REST | 17:42 | 17:45 | working 2 / waiting 2 |
| Attachment category (3 tries; ModuleId read live), read-back | 17:46 | 17:50 | working 2 / waiting 2 |
| 5 SKILL.md written | 17:50 | 17:52 | working |
| Fresh tests F (5 parallel), wording fix + re-test R (1) | 17:52 | 17:57 | working |
| Cards, evidence, reports | 17:55 | 18:00 | working |

## Tasks
| Task | Status | Working min | Waiting min | Test records | Own-test import ProcessId |
|---|---|---:|---:|---|---|
| Manage Pricing Results Presentations | tested | 10 | 5 | FSCRT_AK_GF_RP1, _RPF, _RPR | 100004743455639 |
| Manage Pricing Totals | tested | 10 | 5 | FSCRT_AK_GF_TOA, _TOF | 100004744433010 (try 1 100004744431339 refused) |
| Manage Time Unit Mappings | tested | 12 | 5 | units ZK1/ZKF (FSCRT_AK_GF_U1, _UF); mappings FSCRT_AK_GF_TU1, _TUF | 100004743456567 |
| Manage External Service Details for Algorithms | tested | 12 | 6 | FSCRT_AK_GF_WS1, _WSF | 100004744434324 (tries 100004743456587, 100004744433377 refused) |
| Manage Order Attachment Categories | tested | 12 | 6 | FSCRT_AK_GF_AC2, _ACF (+ AC1 outside module) | 100004744435115 (tries 100004744436010 refused, 100004744435085 no module) |

All exports and fresh/re-test ProcessIds are in each task's CHANGELOG.md. Every read-back: only FSCRT_AK_GF_ rows
added, 0 existing rows changed or missing.

## Problems and findings
- Pricing Totals: TotalCode with a digit is refused (QP_CMN_INVALID_CODE although the message only mentions upper
  case, length and spaces). Proven by changing only the digit.
- Time Unit Mappings: mapping an existing unit would change other people's contracts, so the skill creates its own
  unit (REST POST, class read live) first. FSCR's REST client prints Oracle's gzipped error bodies unreadable;
  `common-features/scripts/rest_write.py` wraps FSCR's client unchanged and unzips the error ("BaseUomFlag is
  required").
- External Service Details for Algorithms: OrigSystemName needs the source system's **name**, not its code; the CSV has
  no URL/credential columns (URL is entered on the page; not done).
- Order Attachment Categories: `UserName` is the category display name (required); without ModuleId the category is
  created outside the DOO module and the task export never shows it (FSCRT_AK_GF_AC1, own record, left in place).
- Results Presentations: tester found one wrong column list; fixed and re-tested (R pass).
- Suggestion repeated by several testers, not applied (no wrong step): say that each export folder also holds a .txt
  file next to the ZIP.

## What is left
Sitting limit reached (10 tasks). 16 CSV tasks open for the next sitting; see MODULE_TRACKER.csv and MODULE_RESULT.md.
