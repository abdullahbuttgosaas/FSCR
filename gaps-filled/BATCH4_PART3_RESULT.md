# Batch 4, part 3: party tax profiles, tax exceptions, location of final discharge, tax exemptions (result)

GoSaaS work, not official FSCR. Filled by AB with Claude, 2026-11-24. Tested on one test environment only (release 11.13.26.10.0).
- The FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`. No FSCR file was edited.
- Plan and rules: `BATCH4_PLAN.md` (RULES 1 to 26). Reused Parts 1 and 2: the driver pattern, the filtered log one-liner, the batch 1 to 3 helpers, `template_row.py`, the legal authority skill (batch 3), the taxfix test rates and Part 2's test product category codes.
- Work folder `E:\GoSaaS\gw\b4p3` (outside the repo; exports there hold user names).

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 19:05 | 19:06 | 1 | Read plan, Part 1 result, rules (plan time) |
| 19:06:14 | 19:06:21 | 0 | Sign-in on port 8765 (listener checked free first; browser was still signed in; not counted in any task) |
| 19:06 | 19:08 | 2 | 4 read-only exports + read-only rates export (test chain), lookups by REST |
| 19:08 | 19:14 | 6 | Task 11 live (3 tries) and task 10 live (1 try), after-exports, compares |
| 19:14 | 19:24 | 10 | Task 9: legal authority export, prerequisite authority without profile, re-export, profile import, after-export, compare |
| 19:23 | 19:27 | 4 | Task 12: 3 tries, all refused with the same cause; check export (0 created) |
| 19:27 | 19:31 | 4 | Skills 9, 10, 11 and the task 12 findings page |
| 19:28 | 19:40 | 12 | Fresh tests 9, 10, 11 in parallel (different packages and records); my re-check of each record |
| 19:30 | 19:42 | 12 | Evidence, STATUS, CHANGELOG, this report, index, cleanup (while the testers ran) |

**Waiting for your approvals:** 0 minutes (the brief was the approval). No second sign-in.

## Results

| # | Task | Status | Working min (write + own live test) | Oracle waiting min | Fresh test | Fresh test min |
|---|---|---|---:|---:|---|---:|
| 9 | Manage Party Tax Profiles (`ORA_ZX_MANAGE_PARTY_TAX_PROFILES`) | tested | 13 | 9 | PASS | 10 |
| 10 | Manage Tax Exceptions (`ZX_MANAGE_TAX_EXCEPTIONS`) | tested | 8 | 3 | PASS | 5 |
| 11 | Manage Location of Final Discharge (`ORA_ZX_MANAGE_LOCATION_FINAL_DISCHARGE`) | tested (try 3) | 10 | 2 | PASS | 2 |
| 12 | Manage Tax Exemptions (`ORA_ZX_MANAGE_TAX_EXEMPTIONS`) | **failed** (3 tries, cause proven) | 10 | 4 | not run | - |
| | **Total** | **3 of 4 tested, 1 failed** | **41** | **18** | 3 of 3 | **17** |

- **No `retest_after_wording_fix` is pending.** No SKILL.md changed after its fresh test. The testers' notes are in each CHANGELOG and were **not** applied, so the wording on disk is the wording that was tested. One tester note is a real wording error (task 9 Step 3: `ProcessForApplicabilityFlag` is also `Y`, not only the two authority flags); fix it with a re-test.
- `rebuild_index.py`: see the end of this report.

## Test records created (all new; none edited or deleted; may not be deletable)

| Task | Live test (ProcessId) | Fresh test (ProcessId) |
|---|---|---|
| 9 tax authority profile | prerequisite legal authority `GAPFILL_AB_P3_LA3` without profile (100004741425152); its profile (100004741427305) | legal authority `GAPFILL_AB_P3_LA4F` (100004741428097); its profile (100004741428317) |
| 10 tax exception | `GAPFILL_AB_P3_EXC1`: 10 % discount, product category `GAPFILL_AB_P2_PCC1`, rate `GAPFILL_AB_TF_RT1` (100004741425074) | `GAPFILL_AB_P3_EXC2F`: same on `GAPFILL_AB_P2_PCC2F`, rate `GAPFILL_AB_TF_RT2F` (100004742415631) |
| 11 location of final discharge | `GAPFILL_AB_P3_LFD1`, US test street (100004741426100; tries 100004741423731 and 100004741423798 created nothing) | `GAPFILL_AB_P3_LFD2F` (100004741427754) |
| 12 tax exemption | none: 3 tries refused (100004742416395, 100004741425310, 100004741427510); export after: 0 exemptions | not run |

Nothing uses them: the exceptions sit on taxes that are not live; the legal authorities are linked to no legal entity, registration or tax; the final discharge locations are at test streets and no rule points to them.

Evidence: `evidence/batch-04/<TASK_CODE>/01_missing` to `05_fresh_test` (.png) for all 4. Rendered text, checked: no tokens, server addresses, environment names or user names.

## Problems and findings
1. **Task 9: the test authorities already had profiles.** The batch 3 legal authority skill sends a `ZX_TAX_AUTHORITY_PROFILE` row, so `GAPFILL_AB_P3_LA1` and `LA2F` already had one; a new row for them would be an update. Third-party (customer, supplier) profiles are **not** in this package (`ZX_CUSTOMER_TAX_PROFILE.csv` holds customer registrations). Fix (rule 21): Step 1 makes a new test legal authority with the legal authority skill **minus its profile row** (VERIFIED: 6 rows, no profile created by Oracle), then this task adds the profile.
2. **Task 11: rows in full, values from Oracle's errors and docs.** `CreatedByModule` (`HZ_CBM_REQD_ERROR`; read live from lookup `HZ_CREATED_BY_MODULES`, `HZ_WS`), `OrigSystemReference`, `StatusFlag=A` and `EntityCode=HZ_LOCATIONS` (`JBO-27014`; the value comes from Oracle's documentation of table ZX_FINAL_DISCHARGE_LOCATIONS). The refused tries created nothing.
3. **Task 10 worked first try** with codes only: the taxfix rate chain (GCO owner) and Part 2's product category code. Lookups `ZX_EXCEPTION_CLASS` / `_TYPE` / `_REASON` read live by REST.
4. **Task 12 failed, cause proven:** all 3 tries `JBO-27014: Attribute PartyTaxProfileId in TaxExemptionEO is required`. Oracle's tax guide says exemptions belong to the **customer and customer site** (third-party) tax profile only. No test customer exists that CSV or FSCR's REST client can reach (customer resources are on `crmRestApi`; FSCR's client answers 404 for `accounts` and `hubOrganizations`), and a real customer is shared. The round trip (rule 20) was impossible: the export has 0 exemptions. **Next step:** create a `GAPFILL_` test customer with a site (customer import or CRM REST), then one `THIRD_PARTY` exemption row on a not live test tax; the row is written out in `manage-tax-exemptions/SKILL.md`.
5. **Plan correction:** `BATCH4_PLAN.md` says task 9 puts the profile on `GAPFILL_AB_P3_LA1`; that party already had one (finding 1). The plan also assumed exemptions on a party tax profile from task 9; they need a customer profile (finding 4).
6. **Tester notes, not applied (each needs a re-test if applied):** files are no longer empty after the first run (10, 11); choose among several test rates/codes (10); no live check that a tax is not live (10); TPROF wording and the flag sentence (9); Step 1 template and builder key (9); no safe command to view added rows (11).
7. **Part 1 follow-up still open:** the `manage-profile-options` Step 5 log one-liner prints a `Submitted By` user name (`BATCH4_PART1_RESULT.md` finding 6). The Part 3 skills use the filtered one-liner.

## Index and cleanup
- `python rebuild_index.py` in `gaps-filled`: 44 cards applied, **No problems**. Common Features: 41 tested of 148 (task 12 is a failed card, counted as open). All 19 modules: 43 tested of 935.
- All 3 fresh-test sub-agents have finished. The sign-in listener exited right after sign-in (19:06:21). No Python process or server started by this session is left, and nothing listens on port 8765.
- The work folder `E:\GoSaaS\gw\b4p3` stays outside the repo (exports, payloads, logs, fresh-test folders); it is not in git.
- Nothing is committed or pushed.
