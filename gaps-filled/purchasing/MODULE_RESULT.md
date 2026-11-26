# Module result: Purchasing gap fill (tester MZ, prefix FSCRT_MZ_GF_)

## Sitting 1, batch 03 (26/11/2026 15:22 - 15:45, requested by the tester)

The tester confirmed the environment is used only for testing and asked to test the two skills that were written as
unsafe. Both are now **tested** (own live test, fresh test, two retests after wording fixes).

| Status change | Task | Final retest record (import ProcessId) |
|---|---|---|
| written -> tested | Buyer Assignment Rules | rule 10008 in FSCRT_MZ_GF_RS3R (100004743436885) |
| written -> tested | Purchasing Descriptive Flexfields | context FSCRT_MZ_GF_CTX2R on PO_LINE_TYPES (100004743447867) |

Minutes: Buyer Assignment Rules 24 working / 6 waiting; Purchasing DFFs 26 working / 8 waiting (batch 03 only).

Effect on the environment (please note): the FSM import of a DFF deploys the flexfield automatically. The 4 test
contexts FSCRT_MZ_GF_CTX1, _CTXF, _CTXR and _CTX2R are live as context choices on the Purchasing Line Types DFF
(PO_LINE_TYPES); nothing else changed. The 4 test buyer rules (sequences 9998, 9999, 10007, 10008) sit after all
existing rules and only match lines above 999,999,999.

Test records added in batch 03: buyer rules 9999 (FSCRT_MZ_GF_RS1), 9998 (FSCRT_MZ_GF_RSF), 10007
(FSCRT_MZ_GF_RS2R), 10008 (FSCRT_MZ_GF_RS3R); DFF contexts FSCRT_MZ_GF_CTX1, _CTXF, _CTXR, _CTX2R with segments
FSCRT_MZ_GF_SEG1, _SEGF, _SEGR, _SEG2R.

Failed: none. Left: none.

## Sitting 1 (25/11/2026 15:25 - 26/11/2026 15:08, paused overnight by an API spend limit)

Missing tasks from the module test: 11 of 14 (9 route only, 2 neither). All 11 are now settled.

| Status | Count | Tasks |
|---|---:|---|
| tested | 7 | Hazard Classes, Approved Supplier List Statuses, External Purchase Prices Lookups, UN Numbers, Purchasing Value Sets, Buyer Assignment Rule Sets Lookup, Change Order Templates |
| written (unsafe to test) | 2 | Buyer Assignment Rules, Purchasing Descriptive Flexfields |
| failed | 0 | |
| screen-only | 2 | Purchasing Messages, External Purchase Price Approvals |
| left | 0 | |

Batches: 01 (5 tasks), 02 (4 tasks). This sitting settled 9 tasks (7 tested + 2 written), under the limit of 10.

### Minutes per task (estimates from run timestamps)
| Task | Working | Waiting |
|---|---:|---:|
| PO_MANAGE_HAZARD_CLASSES | 15 | 6 |
| PO_MANAGE_APPROVED_SUPPLIER_LIST_STATUSES | 13 | 5 |
| ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_LOOKUPS | 16 | 6 |
| PO_MANAGE_UN_NUMBERS | 16 | 7 |
| PO_MANAGE_PURCHASING_VALUE_SETS | 17 | 6 |
| ORA_PO_MANAGE_ASSIGNMENT_RULE_SETS_LOOKUP | 17 | 6 |
| PO_MANAGE_CHANGE_ORDER_TEMPLATES | 16 | 6 |
| ORA_PO_MANAGE_BUYER_ASSIGNMENT_RULES | 6 | 1 |
| PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS | 7 | 1 |
| Screen-only checks (2 tasks) | 2 | 1 |
| **Total** | **125** | **51** (incl. 2 sign-ins, 6 min) |

### Failed tasks
None.

### Unsafe to test (skill written, not loaded)
- Buyer Assignment Rules: a rule assigns an existing buyer (by e-mail) to other people's requisition lines on the shared environment. Next step: run the skill on a project environment with sign-off.
- Purchasing Descriptive Flexfields: a context/segment on a seeded Purchasing DFF needs a deploy that changes pages for every user. Next step: same.

### Left for the next sitting
Nothing. Every CSV/API gap of Purchasing is tested, written (unsafe, with reason) or screen-only.

### Test records created (all new, prefix FSCRT_MZ_GF_; nothing existing edited or deleted)
- Hazard classes: HC1, HCF, HUF, HCR, HUR, HC2R, HU2R, HC3R, HU3R
- ASL statuses: AS1, ASF, ASR, A2R, A3R
- EPP lookup types (code FSCRT_MZ_GF_A each): LK1, LKF, LKR, LK2R, LK3R
- UN numbers: UN1, UNF, UNR, UN2R, UN3R
- Value sets (one value each): VS1, VSF, VSR, VS2R, VS3R
- Buyer assignment rule set codes (in PO_BUYER_ASSIGN_RULE_SETS): RS1, RSF, RS2R, RS3R
- Change order templates: CO1, COF, CO2R, CO3R
ProcessIds per record: each task's CHANGELOG.md and evidence/batch-NN/<TASK_CODE>/04_test_result.txt, 05_fresh_test.txt.

### Shared tools (purchasing-common/scripts)
inspect_export.py, build_fsm_package.py (with `_unchanged_parents`), compare_fsm_exports.py, log_summary.py, tracker_set.py; shared steps in purchasing-common/COMMON_STEPS.md.

## Cumulative counts (all sittings)
| Status | Count |
|---|---:|
| tested | 9 |
| written (unsafe to test) | 0 |
| failed | 0 |
| screen-only | 2 |
| left | 0 |
| **missing tasks** | **11** |
