# Procurement batch 06: result (2026-11-27, sitting 4, AB with Claude, PC)

The 5 approval / task-configuration tasks (open since sitting 2). Route: Oracle REST (`approvalTasks`, `approvalAttributesLOV`, `approvalRules`); new helper `scripts/approval_rule.py`.

| Task | Status | Write / test / wait min | Test records |
|---|---|---|---|
| Manage Requisition Approvals | **tested** (REST) | 6 / 8 / 2 | own `GAPFILL_AB_B6_RQ1`; fresh `GAPFILL_AB_B6_RQ2F`; re-test `GAPFILL_AB_B6_RQ3R` |
| Manage Purchasing Document Approvals | **tested** (REST) | 3 / 5 / 1 | own `GAPFILL_AB_B6_PO1`; fresh `GAPFILL_AB_B6_PO2F`; re-test `GAPFILL_AB_B6_PO3R` |
| Manage Work Confirmation Approvals | **written (unsafe to test)** | 2 / 1 / 1 | none: `GAPFILL_AB_B6_WC1` refused POR-2011627 |
| Manage Intake Request Approvals | **written (unsafe to test)** | 2 / 1 / 1 | none: `GAPFILL_AB_B6_IR1` refused POR-2011627 |
| Manage Task Configurations for Procurement | **screen-only** (proof on card) | 0 / 2 / 3 | none |

All rules are **disabled**, priority LOW, one condition "amount greater than 999999999999", action Automatic / Rejected. REST creates them as **pending** rule changes; nothing was deployed or discarded. REST calls have no ProcessId; the read-back is the participant's rule list before/after (1 added, 0 removed, 0 changed).

## Time log
| Step | Start | Finish | Minutes | Kind |
|---|---|---|---|---|
| Read context, cards, tracker, reserve note | about 00:35 | 00:42 | about 7 | working (not counted in a task; start time not logged) |
| Sign-in | 00:42 | 00:43 | 1 | waiting |
| Read approval tasks, participants, rules, attributes (read only) | 00:43 | 00:46 | 3 | waiting (REST) + working |
| Own tries on Requisition Approvals (3 tries, RQ1 created) | 00:46 | 00:47 | 1 | working |
| Helper script, PO1 own test, WC1/IR1 tries | 00:47 | 00:50 | 3 | working |
| Task Configurations: export x3 + 8 REST probes | 00:50 | 00:51 | 1 | waiting |
| 4 SKILL.md files | 00:50 | 00:52 | 2 | working |
| Fresh tests RQ2F + PO2F (parallel) | 00:52 | 00:53 | 1 | working |
| Wording fix, re-tests RQ3R + PO3R (parallel) | 00:53 | 00:55 | 2 | working |
| Cards, evidence, tracker | 01:10 | 01:14 | 4 | working (not counted in a task) |

## Problems and findings
1. `approvalRules` GET needs `q=ParticipantId=<id>` (POR-2011550). `Task` (approvalTasks) and `AttributeKey` (approvalAttributesLOV) are **not queriable**: filter in Python. Join filters with `;`.
2. POST refused fields: `ConditionTypeCode`, `ActionNumber`, `ConditionAttributeKey` ("cannot be set"); the condition needs `ConditionAttributeId`, read live from `approvalAttributesLOV` (found by probing; it is not in the approvalRules describe).
3. A REST-created rule is a pending change: `HasPendingRuleChangesFlag` False → True. `deployRulesToBPM` and `discardPendingRuleChanges` exist; neither was used (discard would also drop other people's pending changes). No DELETE.
4. Work Confirmation and Intake Request tasks have `IsRulesUpgradedFlag=False`; every create is refused `POR-2011627` (rules must be upgraded from BPM first). The upgrade is a one-time shared action on the page, with no REST undo: **written (unsafe)**. Same script works there once upgraded.
5. Task Configurations: CSV flag N (export refused 3 times), 8 REST names 404, approvalTasks has no configuration fields: **screen-only** (BPM Worklist).
6. Fresh round F (both tasks) reported a misleading sentence: "pending flag False → True" (it may already be True). Fixed, plus mkdir RUN, `--prefix` meaning, 401 grep, task grep hint; re-test R passed with no wrong sentence. Suggestions not applied are on each card.

## What is left
Batch 07 (same sitting): Contract Terms DFF, Configure Procurement Business Function, Supplier Contract BF Properties, Electronic Signature (re-judged written cards).
