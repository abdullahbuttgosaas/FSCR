# Changelog: Configure Party Relationships for Supplier Match (GoSaaS gap fill)

## 1.0.1 (2026-11-28)
- Fresh tester F: "Its export holds 0 type rows ... before and after our create" was false on its run (the type export listed RT1, then RT2F). Reworded in P-intro, P1 and Step 4: the export lists only types made by this route and can lag; read back by REST. Step 1 note: earlier test types may be in the list.
- Re-test R: type `GAPFILL_AB_S3_RT3R` (ProcessId 100004743466917), list row (100004743464856): TYPE PASS, both RESULT PASS, no false sentence.

## 1.0.0 (2026-11-28, Sourcing batch 03)
- Prerequisite relationship type by CSV: tries 1-4 refused (Name required; CreatedByModule required; duplicate role meaning from try 2's leftover lookup; subject plural = object plural), try 5 `GAPFILL_AB_S3_RT1` (100004744441598). Supplier match row `GAPFILL_AB_S3_RT1` (100004743464762): PASS.
- Fresh test F: `GAPFILL_AB_S3_RT2F` (100004743466695, 100004744442300): PASS.
- Tester suggestions not applied: expected builder counts in P2; CSV row counts in P1; one RM_USER_ROLE lookup per run; check RT in HZ_RELATIONSHIP_TYPES.csv in Step 4.
