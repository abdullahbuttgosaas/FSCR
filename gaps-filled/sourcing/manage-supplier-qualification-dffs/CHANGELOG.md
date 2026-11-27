# Changelog: Manage Supplier Qualification Descriptive Flexfields (GoSaaS gap fill)

## 1.0.2 (2026-11-28)
- Sign-in: removed the unproved claim "a valid cached sign-in returns at once" (doubted by re-tester R); now: run the sign-in only when a call gives 401/403 or hangs.
- Re-test R2: GAPFILL_AB_S3_QDX4R / QDS4R on ATTRIBUTE13, ProcessId 100004744443166: RESULT PASS, EnabledFlag N, DEPLOYED. No false sentence.

## 1.0.1 (2026-11-28)
- Step 4: "Step 1's first two lines" was wrong (the unzip line is needed too): now "the export command AND its unzip line" (fresh tester F).
- Step 3: log rule reworded (the grep -o line and read_import_log.py are the only safe reads); parent_after.json/.log names; worked example explains the built-in context segment row.
- Re-test R: GAPFILL_AB_S3_QDX3R / QDS3R on ATTRIBUTE12, ProcessId 100004744441909: PASS.

## 1.0.0 (2026-11-28, Sourcing batch 03)
- Own test (Case A): GAPFILL_AB_S3_QDX1 / QDS1 on POQ_INITIATIVES ATTRIBUTE10, ProcessId 100004744442213: 3 rows, 0 failed, check_dff_rows PASS, DEPLOYED before and after.
- Fresh test F (Case B): GAPFILL_AB_S3_QDX2F / QDS2F on ATTRIBUTE11, ProcessId 100004744442270: PASS.
- Tester suggestions not applied: segment row EnabledFlag Y note; --parent-json ignored in Case B; payload check line; MSYS_NO_PATHCONV in Step 4; verified-column list and a Case B worked-example row.
