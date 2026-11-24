# Batch 4 fix: Tax Exemptions (task 12) and Party Tax Profiles (task 9) (result)

GoSaaS work, not official FSCR. Done by AB with Claude, 2026-11-24. Tested on one test environment only (release 11.13.26.10.0).
- Rules: `BATCH4_PLAN.md` RULES block. Test records `GAPFILL_AB_B4FIX_<name>`. FSCR scripts and FSCR's REST client ran in place; no FSCR file was edited.
- Work folder `E:\GoSaaS\gw\b4fix` (outside the repo; exports there hold user names).

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 19:46 | 19:47 | 1 | Read brief, task 12 findings, task 9 tester note |
| 19:47 | 19:48 | 1 | Task 9: fix the Step 3 sentence; start its fresh re-test (ran 19:47 to 19:59) |
| 19:48 | 19:50 | 2 | Task 12: look for a customer route (FSCR task folders, FSCR REST client, Oracle docs); REST probes |
| 19:49 | 19:52 | 3 | Task 12 live: customer and third-party profile by REST, export, 1 import, after-export, compare, REST read-back |
| 19:52 | 19:53 | 1 | Task 12 skill rewritten |
| 19:53:29 | 19:53:37 | 0 | Second sign-in on port 8765 (listener checked free first; token from 19:06 near expiry; waiting time) |
| 19:53 | 20:00 | 7 | Task 12 fresh test; my REST re-check of both test exemptions |
| 19:54 | 20:02 | 8 | Evidence, STATUS, CHANGELOG, index, this report, cleanup (while the testers ran) |

**Waiting for your approvals:** 0 minutes (the brief was the approval).

## Results

| Task | Before | Now | Live test | Fresh test |
|---|---|---|---|---|
| Manage Tax Exemptions (`ORA_ZX_MANAGE_TAX_EXEMPTIONS`) | failed (3 tries) | **tested** | PASS, first try after the prerequisite | PASS |
| Manage Party Tax Profiles (`ORA_ZX_MANAGE_PARTY_TAX_PROFILES`) | tested, one wrong sentence | **tested**, sentence fixed | (not needed: wording fix) | re-test PASS |

- **No `retest_after_wording_fix` is pending.** Task 9 was re-tested after its fix; task 12's skill was not changed after its fresh test. Testers' notes are in each CHANGELOG and were **not** applied.

## 1. Tax Exemptions: how the prerequisite was solved
- **Cause (from Part 3):** `JBO-27014 PartyTaxProfileId ... required`. Exemptions live on the **customer (third-party) tax profile** only.
- **Route search:** no FSCR setup task creates customers (customers are data, not setup; FSCR has only customer lookups, flexfields and profile options). FSCR's REST client (`core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`) supports `/crmRestApi` and POST. Probes: CRM `accounts` GET/POST works; `partyTaxProfiles` GET/POST works; `taxExemptions` GET works; `organizations` and `receivablesCustomers` answer 404.
- **Done (VERIFIED):**
  1. `POST /crmRestApi/.../accounts` `{"OrganizationName":"GAPFILL_AB_B4FIX_CUST1","Type":"ZCA_CUSTOMER"}`: HTTP 201. Oracle gave the party number.
  2. `GET partyTaxProfiles` for that party: none. `POST partyTaxProfiles` `{"PartyTypeCode":"THIRD_PARTY","PartyNumber":"<party number>"}`: HTTP 201, a profile id.
  3. One `ZX_TAX_EXEMPTION.csv` row with `TaxProfilePartyTypeCode=THIRD_PARTY` and the customer's party number and name: ProcessId 100004742416701, 1 row, 0 failed, **first try**.
  4. Export compare 0 -> 1, removed 0, changed 0: PASS. REST `taxExemptions`: count 1, THIRD_PARTY, PRIMARY, DISCOUNT 10.
- **Skill:** `common-features/manage-tax-exemptions/SKILL.md` v0.1.0. Step 1 = test rate (read-only), customer and profile by REST (**GET first, POST only if missing**), written generic (placeholders; party number read from Oracle's answer). `depends_on` lists the customer + profile and the test rate.
- **Fresh test:** PASS (`GAPFILL_AB_B4FIX_CUST2F`, `GAPFILL_AB_B4FIX_EXM2F`, ProcessId 100004741430249). The import script lost its connection after the process started (WinError 10060). The tester did **not** import again, as the skill says, and proved the record by the second export (1 -> 2) and REST. I read both exemptions back by REST myself: present, THIRD_PARTY, PRIMARY, 10.

## 2. Party Tax Profiles: wording fix
- Step 3 said the copied profile has "reporting and collecting authority `Y`, every other flag `N`". Wrong: `ProcessForApplicabilityFlag` is also `Y`. Fixed; the unclear words "a profile an earlier test made by the legal authority skill" were removed too.
- Fresh re-test (task name + SKILL.md only): PASS, `GAPFILL_AB_B4FIX_LA5R` (legal authority ProcessId 100004741428757, profile ProcessId 100004741429245), about 11 minutes. I read the added profile row: TAX_AUTHORITY, the 3 flags `Y`.

## Test records created (all new; none edited or deleted; may not be deletable)
| Task | Live | Fresh test |
|---|---|---|
| 12 | customer `GAPFILL_AB_B4FIX_CUST1` + THIRD_PARTY profile; exemption `GAPFILL_AB_B4FIX_EXM1` (100004742416701) | customer `GAPFILL_AB_B4FIX_CUST2F` + profile; exemption `GAPFILL_AB_B4FIX_EXM2F` (100004741430249) |
| 9 | none (wording fix) | legal authority `GAPFILL_AB_B4FIX_LA5R` (no profile at first; 100004741428757) + its tax authority profile (100004741429245) |

Nothing uses them: the exemptions are on the test tax `GAPFILL_AB_P1_TX1`, which is not live; the customers have no account, site or transactions; the legal authority is linked to nothing.

Evidence: `evidence/batch-04fix/<TASK_CODE>/01_missing` to `05_fresh_test` (.png) for both. Rendered text, checked: no tokens, server addresses, environment names or user names.

## Open notes (not applied; each needs a re-test if applied)
- Task 12: no command to prove a tax is not live (REST `taxes` answers 404; use the taxes export); the summary one-liner crashes when a dropped connection leaves no process log; "8 files" = 7 CSVs + the metadata XML.
- Task 9: "first listed" may pick another run's test profile; exports can take over 2 minutes (run them in the background).

## Index and cleanup
- `python rebuild_index.py` in `gaps-filled`: 44 cards applied, **No problems**. Common Features: 42 tested of 148. All 19 modules: 44 tested of 935. Tax Exemptions is now `tested`.
- Both fresh-test sub-agents have finished. The sign-in listener exited right after sign-in (19:53:37). No Python process or server started by this session is left, and nothing listens on port 8765.
- The work folder `E:\GoSaaS\gw\b4fix` stays outside the repo; it is not in git.
- Nothing is committed or pushed.
