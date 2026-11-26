# CHANGELOG - Manage Disbursement Lookups

## 2026-11-25 (sitting 1, batch 01)
- Before export (ProcessId 100004743425266): all four lookup CSVs empty (no user codes in the IBY module yet).
- IBY lookup types are standard lookups (ViewApplicationId 0, application FND); extensible ones found live
  with genericLookups `LookupType LIKE 'IBY%';CustomizationLevel<>'S'` (56 types).
- Own test: IBY_BANK_CHARGE_BEARER / FSCRT_AK_GF_BCB1 with the row shape proven in Manage Payables Lookups
  (ChangeSinceLastRefresh N, no translation row). ProcessId 100004743426030: 1 row processed, 0 failed.
  Export compare: codes 0 -> 1, translations 0 -> 1. REST standardLookups/IBY_BANK_CHARGE_BEARER/child/lookupCodes: 1 item.
  Oracle stores ModuleKey IBY for the code (the type's application short name FND was sent).
- Fresh test F: FSCRT_AK_GF_BCB1F, ProcessId 100004743426058, PASS (1 -> 2, REST 1 item).
  Tester error: step 3 used ModuleId from type.json but did not list it in --fields -> fixed (field added,
  note that the whole item is saved); added the rows.json snippet; StatusCode (unknown) also normal for the
  import; type CSVs stay at 0.
- Retest R: FSCRT_AK_GF_BCB1R, ProcessId 100004744396882, PASS (2 -> 3, REST 1 item). No errors.
- Own read-back: REST lists BCB1, BCB1F, BCB1R.
- Finding: the Manage Payment System Connectivity Lookups export shows the same codes, so both IBY lookup
  tasks share package and export scope; their fresh tests must run one after the other.
- Tester suggestions not applied: say "LookupTypeGeneric1 ... 0 rows" is normal; verify the 30-character
  limit and give a Meaning limit; say the snippet values are typed in by hand.
