# Changelog: Create Supplier in Procurement (GoSaaS gap fill, REST)

## 1.0.0 (2026-11-28, Sourcing batch 04)
- Task export refused (`CSVExportImportSupportedFlag N`); REST `suppliers` describe shows `create`.
- Own test `GAPFILL_AB_S4_SUP1`: POST HTTP 201, supplier number 12331, PROSPECTIVE, read back by REST.
- Fresh test F: `GAPFILL_AB_S4_SUP2F`: HTTP 201, number 12332, READBACK PASS. No false sentence.
- Tester suggestions not applied: escape `'` in the control supplier name or use SupplierId; add encoding to Step 1's json.load; `echo rc` for every call; record the supplier number.
