task_code: ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_DESCRIPTIVE_FLEXFIELDS
task_name: Manage Supplier Qualification Descriptive Flexfields
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-28
minutes_to_write: 6
minutes_to_test: 8
waiting_minutes: 5
fresh_claude_pass: yes (fresh F PASS, re-test R PASS on v1.0.1, re-test R2 PASS on v1.0.2; no false sentence left)
route: FSM CSV (standard flexfield package, module PrcPoqCommon); parent row read by REST descriptiveFlexfields in Case A
depends_on: none (the flexfield's parent row is sent unchanged; disabled context, no deployment)
test_records: POQ_INITIATIVES: context GAPFILL_AB_S3_QDX1 + segment GAPFILL_AB_S3_QDS1 on ATTRIBUTE10 (100004744442213, own test, Case A); QDX2F/QDS2F on ATTRIBUTE11 (100004744442270, fresh F (v1.0.0), Case B); QDX3R/QDS3R on ATTRIBUTE12 (100004744441909, re-test R (v1.0.1)); QDX4R/QDS4R on ATTRIBUTE13 (100004744443166, re-test R2 (v1.0.2)); all contexts disabled (EnabledFlag N), value set Text 150
notes: Sourcing batch 03 (sitting 2). First export had 0 rows in every file (no user context yet: Case A); parent read by REST (ProtectedFlag N, DEPLOYED). Own test with common-features dff_context_package.py: 3 rows, 0 failed; check_dff_rows.py PASS; DEPLOYED before and after. Fresh F PASS (Case B) but reported a false sentence: Step 4 'Step 1's first two lines' misses the unzip line: v1.0.1 fixed (also the log-reading sentence and parent_after names), re-test R PASS. R tester doubted 'a valid cached sign-in returns at once' (not proved either way): v1.0.2 removed the claim, re-test R2 PASS with no false sentence. Suggestions NOT applied: say the segment row carries EnabledFlag Y; say --parent-json is ignored in Case B; one-line payload check; MSYS_NO_PATHCONV in Step 4; update the verified column list (ATTRIBUTE10-13 used) and add a Case B worked-example row.
