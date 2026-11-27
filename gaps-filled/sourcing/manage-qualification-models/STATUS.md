task_code: ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_MODELS
task_name: Manage Qualification Models
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-28
minutes_to_write: 7
minutes_to_test: 7
waiting_minutes: 4
fresh_claude_pass: yes (fresh F PASS, re-test R PASS on v1.0.1; no wrong sentence left)
route: FSM CSV (model package: ORA_POQ_QUAL_MODELS, _AREAS, _OUTCOMES, _BU_ACCESSES) + REST supplierQualificationModels read-back
depends_on: a procurement business unit (own test unit GAPFILL_AB_B15_BU1/BU2F); ORA_POQ_MANAGE_SUPPLIER_QUALIFICATION_AREAS (own DRAFT test area, revision 0)
test_records: GAPFILL_AB_S3_QM1 on own unit BU1, area QA1 (100004744440460, own test); GAPFILL_AB_S3_QM2F on BU2F, area QA2F (100004744440645, fresh F (v1.0.0)); GAPFILL_AB_S3_QM3R on BU1, area QA1 (100004744441922, re-test R (v1.0.1))
notes: Sourcing batch 03 (sitting 2). New DRAFT model with one area and one outcome, rows written in full (first export 0 rows although REST showed an ACTIVE model of another unit). Own test PASS first try (REST DRAFT, area and outcome ok; export 0 -> 1 in 3 files). Fresh F PASS; tester called "Our first export had 0 rows in every file" misleading (later exports list earlier test models): v1.0.1 reworded, re-test R PASS with no false sentence. Suggestions NOT applied: echo rc after export/import; print "build skipped"; print model names inside the ZIP before import; encoding in Step 2 json.load.
