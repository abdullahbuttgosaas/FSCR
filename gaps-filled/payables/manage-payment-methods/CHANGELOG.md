# CHANGELOG - Manage Payment Methods

## 2026-11-25 (sitting 1, batch 02)
- Export (ProcessId 100004744404456): 5 CSVs; methods 42 (32 seeded), usage rules 517, translations 42,
  validation assignments 8, validation values 4.
- Row shape taken from a screen-created method (flags and usage-rule types only; no ids copied), limited to
  Payables (PmtEnableAr/Ce N) and the 6 AP usage rules.
- Own test FSCRT_AK_GF_PM1, ProcessId 100004743428080: DisbursementPaymentMethod 1 row processed, 0 failed.
  Compare: method 42 -> 43, usage 517 -> 523, translation 42 -> 43 (automatic), validations +0, removed/changed 0.
  REST disbursementPaymentMethodsLOV: 1 item.
- Fresh test F: FSCRT_AK_GF_PM1F, ProcessId 100004743427230, PASS first try (43 -> 44, usage +6, REST 1 item).
  No errors.
- Own read-back: REST LOV lists PM1 and PM1F.
- Tester suggestions not applied: mention that the business object "Disbursement Payment Method" says
  "already processed"; say whether BuApFlag/LeApFlag/TypeApFlag/AutoPayeeFlag/PaymentModeCode may stay empty
  (Oracle defaulted AutoPayeeAssignIndicator Y); give a name length; the LOV may hide inactive methods;
  list the AplFlag keys once.
