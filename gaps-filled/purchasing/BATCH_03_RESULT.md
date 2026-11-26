# Batch 03 result: Purchasing gap fill (requested by the tester)

The tester confirmed on 26/11/2026 that the environment is used only for testing and asked to test the two skills
batch 02 had written as unsafe. Both were tested with safeguards.

## Time log
| Start | Finish | Note |
|---|---|---|
| 26/11/2026 15:22 | 26/11/2026 15:45 | own live tests, skill rewrites, fresh test F, retests R and 2R; one new sign-in at 15:34 |

## Tasks
| Task | Status | Working min | Waiting min | Own test record | Own import ProcessId(s) | Final fresh retest (record, import ProcessId) |
|---|---|---:|---:|---|---|---|
| ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES | tested | 24 | 6 | rule 9999 in FSCRT_MZ_GF_RS1 | 100004744422117 | rule 10008 in FSCRT_MZ_GF_RS3R, 100004743436885 |
| PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS | tested | 26 | 8 | context FSCRT_MZ_GF_CTX1 on PO_LINE_TYPES | try 1 100004743436790, try 2 100004744417669 (both refused), try 3 100004744422130 | context FSCRT_MZ_GF_CTX2R, 100004743447867 |

Every successful import: 0 failed; after-export compare: only test rows added, existing rows changed 0.

## Problems and findings
- Buyer rules: Oracle 26D docs say rule sets only group rules for search; ALL rules are evaluated in ascending
  sequence. Safeguard used: sequence above every existing rule and ExceedsLineAmount 999999999; BU, organization,
  supplier and buyer copied from an existing rule (no e-mail printed). First try worked.
- DFF: Oracle refused `MultirowFlag` N (FND-2771), display type `LIST_OF_VALUES` (FND-2777) and `TranslatableFlag`
  N. Fixes: leave the three context options empty; take display type codes from lookup FND_DF_SEGMENT_DISPLAY_TYPES
  (`LOV`). Third try worked. The DFF parent row is read live by REST `descriptiveFlexfields` and sent unchanged.
- DFF finding (from the fresh retest): the FSM import DEPLOYS the flexfield automatically: REST DeploymentDate of
  PO_LINE_TYPES moved from 04/04/2026 to each import time. So the 4 test contexts (FSCRT_MZ_GF_CTX1, CTXF, CTXR,
  CTX2R) are live as context choices on the Purchasing Line Types DFF. They are context-sensitive (their segment shows
  only when one of them is chosen); no other DFF, page or existing segment changed. The skill first said the import
  did not deploy; that was corrected and retested.
- Fresh testers found wrong sentences (example sequence already taken; script stopped before printing the used
  sequences; DEPLOYED status claim; "import does not deploy"). All fixed; both skills passed retest 2R with no factual
  error.

## What is left
Nothing.
