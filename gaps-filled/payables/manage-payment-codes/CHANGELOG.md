# CHANGELOG - Manage Payment Codes

## 2026-11-25 (sitting 1, batch 02)
- Export (ProcessId 100004744396903): IBY_PAYMENT_CODE.csv 365 rows (PAYMENT_REASON 200, DELIVERY_CHANNEL 84,
  LOCAL_INSTRUMENT 37, BANK_INSTRUCTION 33, SERVICE_LEVEL 11), translation CSV 365 rows.
- Own test PAYMENT_REASON / FSCRT_AK_GF_PR1:
  - try 1, ProcessId 100004743427065: refused, JBO-27014 "Attribute EndDate in PaymentCodeEO is required".
  - try 2, ProcessId 100004744404205: EndDate 4712/12/31 added -> 1 row processed, 0 failed. Compare: codes
    365 -> 366, translations 365 -> 366 (US translation automatic), removed/changed 0. REST paymentCodesLOV 1 item.
- Fresh test F: FSCRT_AK_GF_PR1F, ProcessId 100004743427101, PASS first try (366 -> 367, REST 1 item). No errors.
- Own read-back: REST lists PR1 and PR1F (PAYMENT_REASON, aliases PR1/PR1F, EndDate 4712-12-31).
- Tester suggestions not applied: say which start date to use; give a Meaning limit/example; mention FromDate
  and PaymentCodeType in Pass; view rest_readback.json only through a field filter (rest_read.py already
  removes who-fields from the saved file).
