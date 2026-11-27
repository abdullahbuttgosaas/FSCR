# Changelog: Manage Qualification Models (GoSaaS gap fill)

## 1.0.1 (2026-11-28)
- Step 1 note and worked example: the 0-row export was only the first run; later exports list earlier test models (fresh tester F). Re-test R: `GAPFILL_AB_S3_QM3R`, ProcessId 100004744441922, READBACK PASS, RESULT PASS, no false sentence.

## 1.0.0 (2026-11-28, Sourcing batch 03)
- Own test `GAPFILL_AB_S3_QM1` (ProcessId 100004744440460): PASS first try. Column is `ReassessQualificationFlag`.
- Fresh test F: `GAPFILL_AB_S3_QM2F` (ProcessId 100004744440645): PASS.
- Tester suggestions not applied: `echo rc` after export and import; print "build skipped"; list the model names inside the ZIP before import; add encoding to Step 2's json.load.
