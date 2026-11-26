# Changelog: Configure Procurement Business Function

- 2026-11-25, batch-03 (AB with Claude, sitting 2). Skill written from the read-only export / REST and live tries. Export read; change package built offline (one field of one BU); import blocked as unsafe, not run.
- Test records: none (package built offline, not imported).
- Fresh test: n/a (unsafe to test: changes a live BU's setup).

- 2026-11-27, batch-07 (AB with Claude, sitting 4). Status: tested.
- Test records: own unit GAPFILL_AB_B15_BU1: function 110 (ProcessId 100004744439440); config try 1 refused JBO-27014 InventoryOrganizationId (100004744439507, nothing created); config row (100004743463568). Fresh: GAPFILL_AB_B15_BU2F function (100004743465127) + config (100004744437693). Re-test: GAPFILL_AB_B15_BU5R function (100004743464296) + config (100004743463880)
- Fresh test: yes (round F on GAPFILL_AB_B15_BU2F PASS, one wrong sentence 'Step 3 lists them' fixed to Step 1; re-test R on GAPFILL_AB_B15_BU5R PASS, no wrong sentence)
- Notes: Batch 07 (sitting 4). Re-opened from written (unsafe): the safe way is an own prefix business unit nobody uses (units made in Common Features batch 15). PO_SYSTEM_PARAMETER 14 -> 17 (only the 3 own units added; document types 84, negotiation terms 2 unchanged; read back by AB 01:21). ModuleId 110 = Procurement: VERIFIED as the function every configured procurement unit has, name GUESS (pairs 120 -> 110 in service providers). Settings copied from a working row except unit, inventory org, currency, audit columns. Suggestions NOT applied: say 6 document types per configured real unit; command for 'unit not in list'; note PON_CONTRACTS_TRANSLATION compare needs no --key; print only key columns when inspecting a ZIP. Where it shows: Configure Procurement Business Function page, business unit GAPFILL_AB_B15_BU1.
