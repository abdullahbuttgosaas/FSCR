# Sourcing batch 01 result (sitting 1, 2026-11-27)

Module: Sourcing and Supplier Management. Filled by AB with Claude. Prefix `GAPFILL_AB_S1_`. Work folder outside the repo (`gw\src\s1`).

## Time log
| Step | Start | Finish | Minutes |
|---|---|---|---:|
| Read context, gap list, helpers; my_gaps.csv and tracker | 23:18 | 23:25 | 7 |
| Sign-in (waiting, not task time) | 23:26 | 23:26 | 0.5 |
| Read-only exports of the 5 tasks (waiting) | 23:27 | 23:28 | 1 |
| Own live tests (4 in parallel, then Qualification Outcome after the type-name fix) | 23:29 | 23:31 | 3 |
| Skills written (one template, 5 skills) | 23:31 | 23:32 | 4 |
| Fresh round F (4 in parallel) | 23:32 | 23:35 | 3 |
| Wording fix v1.0.1; round R (AO, QO) + Sourcing Lookups F | 23:36 | 23:39 | 4 |
| Wording fix v1.0.2; round R2 (all 5) | 23:40 | 23:46 | 6 |
| Cards, evidence, tracker | 23:47 | 23:49 | 2 |

## Tasks
| Task | Status | Working min | Waiting min | Test records (ProcessId) |
|---|---|---:|---:|---|
| Manage Assessment Outcome Lookup | tested | 13 | 4 | AO1 (100004744437747), AO2F (100004744439842), AO3R (100004744439923), AO4R (100004743465925) |
| Manage Qualification Outcome Lookup | tested | 13 | 4 | QO1 (100004744437773), QO2F (100004744437829), QO3R (100004744439938), QO4R (100004744437960) |
| Manage Standards Organization Lookup | tested | 13 | 4 | SO1 (100004744439771), SO2F (100004744440224), SO3R (100004744439975) |
| Manage Subject Lookup | tested | 13 | 4 | SJ1 (100004743465489), SJ2F (100004743464541), SJ3R (100004744437977) |
| Manage Sourcing Lookups | tested | 13 | 4 | SL1 (100004743464452), SL2F (100004744437882), SL3R (100004743464640) |

All codes start with `GAPFILL_AB_S1_`. Minutes are each task's share of the batch (the 5 tasks share one skill template and ran in parallel).

## Problems and findings
1. **Qualification Outcome type name:** the type is `ORA_POQ_QUALIFICATION_OUTCOME` (with `ORA_`); `POQ_QUALIFICATION_OUTCOME` gives REST HTTP 404. Nothing was imported on that first attempt. The type name is in the export metadata scope; new helper `scripts\scope_lookup_types.py` prints it without printing the user name.
2. **Sourcing Lookups scope holds 6 types**, including `POQ_STDS_ORG` and `POQ_SUBJECT` (the scope of the Standards Organization and Subject tasks). Run those tasks one after the other; the compare lists codes others added there (it still passes).
3. **Wording:** round F found one wrong sentence (Step 4 "repeat the two export commands of Step 1": Step 1 has four). Round R found a READBACK check that crashed (KeyError) when CODE is missing, and Step 1 pointed to a level that Step 2 did not print. Both fixed (v1.0.1, v1.0.2); round R2 on v1.0.2: 5 of 5 PASS, no wrong sentence.
4. Existing codes in these types carry people's names (made by other testers): never copied into skills or evidence.
5. Suggestions not applied are listed in each `STATUS.md` and `CHANGELOG.md`.

## What is left
Batch 02 (value sets, negotiation styles, attribute lists, qualification areas) runs next in this sitting. 21 tasks open after this batch.
