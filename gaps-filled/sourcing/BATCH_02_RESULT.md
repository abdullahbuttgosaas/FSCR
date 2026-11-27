# Sourcing batch 02 result (sitting 1, 2026-11-27)

Module: Sourcing and Supplier Management. Filled by AB with Claude. Prefix `GAPFILL_AB_S2_`. Work folder outside the repo (`gw\src\s1`).

## Time log
| Step | Start | Finish | Minutes |
|---|---|---|---:|
| Read-only exports of the 5 tasks (waiting, during batch 01 fresh tests) | 23:33 | 23:34 | 1 |
| Value set own tests (module id read live) | 23:35 | 23:36 | 2 |
| Negotiation style: new helper `clone_rows.py`, own test, REST probes | 23:36 | 23:38 | 3 |
| Attribute list try 1 (refused), export proof, try 2 (PASS) | 23:39 | 23:43 | 4 |
| Qualification area on own test unit, REST + export read-back | 23:43 | 23:45 | 2 |
| Skills written (5) | 23:45 | 23:48 | 5 |
| Fresh round F (5 in parallel) | 23:48 | 23:51 | 3 |
| Value set compare fix v1.0.1, round R (2) | 23:51 | 23:55 | 4 |
| Cards, evidence, tracker | 23:50 | 23:55 | 3 |

## Tasks
| Task | Status | Working min | Waiting min | Test records (ProcessId) |
|---|---|---:|---:|---|
| Manage Sourcing Value Sets | tested | 15 | 5 | SVS1 (100004743465550), SVS2F (100004744441184), SVS3R (100004743466262) |
| Manage Supplier Qualification Value Sets | tested | 15 | 5 | QVS1 (100004744440268), QVS2F (100004744441165), QVS3R (100004743464692) |
| Manage Negotiation Styles | tested | 13 | 4 | STY1 (100004743464567), STY2F (100004744442096) |
| Manage Attribute Lists | tested | 15 | 5 | try 1 refused (100004743465828, nothing created), ATL1 (100004744440351), ATL2F (100004743466110) |
| Manage Qualification Areas | tested | 14 | 4 | QA1 on own unit GAPFILL_AB_B15_BU1 (100004744440374), QA2F on own unit GAPFILL_AB_B15_BU2F (100004743464667) |

All names start with `GAPFILL_AB_S2_`. Value sets hold values `GAPFILL_A`, `GAPFILL_B`. The style is ACTIVE (copy of the seeded Standard_Negotiation, SystemFlag N); the attribute lists are ACTIVE; the qualification areas are DRAFT.

## Problems and findings
1. **Value set scope:** each task's export is scoped by module (`PrcPonCommon` Sourcing, `PrcPoqCommon` Supplier Qualification). The `ModuleId` is read live from a seeded lookup of the same module (`PON_LINE_ATTRIBUTE_GROUPS`, `POQ_ASSESSMENT_OUTCOME`); the after-export proves the value set landed in the task.
2. **Value set compare (wrong line, fixed):** v1.0.0 keyed values on `Value` alone; the same value names in another test value set showed as "changed" (false FAIL). Both fresh testers reported it. v1.0.1 keys on value set + value; round R 2 of 2 PASS, no wrong sentence.
3. **Attribute lists need `AuctionHeaderId=-1` and `LineNumber=-1`** on group and attribute rows. Without them every row is refused (`JBO-27014: Attribute AuctionHeaderId in SourcingRequirementSectionEO is required`); try 1 created nothing (proved by export).
4. **No REST resource** for negotiation styles or attribute lists (6 names tried, HTTP 404); the export compare is the read-back. Qualification areas have `supplierQualificationAreas` (read only used).
5. **Qualification areas** belong to a procurement business unit: tested on our own test units (made in Procurement sitting 4), DRAFT, no questions, so nobody else's unit or qualification is touched.
6. Two re-testers met a dropped export connection (WinError 10060) and followed the skill's rule (re-run into a new folder); no import was repeated. One re-tester printed an export output tail in its own console (not saved to any file or report); the skills already say not to.
7. New helper `scripts\clone_rows.py` (copy one record's rows under a new key, audit columns emptied, optional who columns from the metadata without printing them).

## What is left
16 tasks open in this module (next sitting): Qualification Models, the two DFF tasks, Qualification Rule Sets, Party Relationships for Supplier Match, Supplier Qualification Controls and 10 "neither" tasks (check for CSV and REST before calling any screen-only).
