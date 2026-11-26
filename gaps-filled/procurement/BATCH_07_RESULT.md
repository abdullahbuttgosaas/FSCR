# Procurement batch 07: result (2026-11-27, sitting 4, AB with Claude, PC)

The 4 cards that were "written (unsafe to test)", re-judged against the rule "a new prefix record nobody uses is not unsafe".

| Task | Status | Write / test / wait min | Test records (ProcessIds) |
|---|---|---|---|
| Manage Contract Terms Descriptive Flexfields | **tested** (re-opened) | 5 / 6 / 4 | own context `GAPFILL_AB_B7_CCX1` + segment `CSG1` (100004743464073); fresh `GAPFILL_AB_B7_CCX2F` + `CSG2F` (100004743464090) |
| Configure Procurement Business Function | **tested** (re-opened) | 8 / 7 / 6 | own unit `GAPFILL_AB_B15_BU1`: function 110 (100004744439440), try 1 refused (100004744439507), config (100004743463568); fresh `BU2F` (100004743465127, 100004744437693); re-test `BU5R` (100004743464296, 100004743463880) |
| Specify Supplier Contract Management BF Properties | **tested** (re-opened) | 6 / 6 / 4 | own `GAPFILL_AB_B15_BU1`: tries 1-3 refused (100004744437661, 100004743463605, 100004743465019), try 4 created (100004743463626); fresh `BU2F` (100004743464382) |
| Configure Electronic Signature for Procurement Documents | **written (unsafe)**, reason still holds | 1 / 0 / 1 | none (export only, 0 rows) |

## Time log
| Step | Start | Finish | Minutes | Kind |
|---|---|---|---|---|
| DFF: REST list of OKC flexfields, parent, export (empty) | 00:52 | 00:53 | 1 | waiting |
| DFF: build + import + after-export + check | 00:53 | 00:55 | 2 | working (+1 waiting) |
| DFF: skill rewrite, fresh test | 00:55 | 00:59 | 4 | working |
| BF: exports, find Procurement function id | 00:56 | 00:59 | 3 | working (+2 waiting) |
| BF: assign function to own unit, read back | 00:59 | 01:00 | 1 | waiting |
| BF: config tries 1-2, read back | 01:00 | 01:03 | 3 | working (+2 waiting) |
| Contract BF: export, unit id, tries 1-4, read back | 01:04 | 01:08 | 4 | working (+2 waiting) |
| Electronic Signature: fresh read-only export, re-judge | 01:09 | 01:10 | 1 | waiting |
| Both BF skills written | 01:08 | 01:12 | 4 | working |
| BF fresh F, wording fix, re-test R | 01:12 | 01:20 | 8 | working (tester time) |
| Contract BF fresh test, own read-backs | 01:20 | 01:25 | 5 | working |
| Cards, reports, tracker, index | 01:25 | 01:32 | 7 | working (not counted in a task) |

## Problems and findings
1. **Contract Terms DFF:** the 2026-11-25 card said a test needs a shared flexfield deployment. Wrong: a DISABLED context loads with no deployment and the flexfield stays `DEPLOYED` (as on the 3 Common Features DFF tasks). Export was empty (no OKC user context); parent read by REST. Both rounds PASS.
2. **Business function tasks:** the safe way is an own prefix business unit (Common Features batch 15 units). First assign the Procurement business function (`FUN_BU_USAGE`, `ModuleId` 110: the function every configured procurement unit has; name GUESS). Procurement config needs an inventory organization code (JBO-27014 without it); an existing code is used as a value only.
3. **Supplier contract properties** refusals, one change per try: short row → `OKC_BUSET_MIGINVALID_DATA`; template copy → `OKC_BUSET_GLOBALBUEXISTS` (only one global unit); `GlobalBusUnitYn=N` → JBO-27014 `DefaultCurrencyCode` (because `LedgerYn=Y` on a unit with no ledger); `LedgerYn=N` → created. Each refusal created nothing (export checked).
4. **Electronic Signature:** still written. The one setup row turns on e-signature for everyone and needs real provider credentials, which an agent must never enter; no own record and nothing to restore to.
5. BF fresh round F found one wrong sentence ("Step 3 lists them" → Step 1); fixed and re-tested (R PASS, no wrong sentence). Other suggestions are on each card, not applied.
6. Records left on the environment (new, prefix only): 6 disabled pending approval rules, 2 disabled OKC contexts with segments, function 110 + procurement config on BU1/BU2F/BU5R, contract properties on BU1/BU2F.

## What is left
Procurement: only Manage Freight Terms Lookup (reserved for the live demo, never touched).
