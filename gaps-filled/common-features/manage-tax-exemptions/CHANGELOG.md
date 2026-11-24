# CHANGELOG: manage-tax-exemptions (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-24 (batch 4 fix, AB with Claude): tested
- Routes checked with FSCR's REST client: CRM `accounts` (GET/POST), `partyTaxProfiles` (GET/POST), `taxExemptions` (GET) work; `organizations` and `receivablesCustomers` answer 404. No FSCR setup task creates customers.
- Live: customer `GAPFILL_AB_B4FIX_CUST1` (POST accounts, HTTP 201, Type ZCA_CUSTOMER), its THIRD_PARTY profile (POST partyTaxProfiles, HTTP 201), exemption `GAPFILL_AB_B4FIX_EXM1` (ProcessId 100004742416701, 1 row, 0 failed, first try). Export compare (0 -> 1) PASS; REST taxExemptions count 1.
- SKILL.md rewritten: Step 1 prerequisites (test rate; customer and profile by REST, GET first), export, one row with `TaxProfilePartyTypeCode=THIRD_PARTY`, import, compare + REST read-back.
- Fresh test (task name + SKILL.md only): PASS, `GAPFILL_AB_B4FIX_CUST2F` + profile + `GAPFILL_AB_B4FIX_EXM2F` (ProcessId 100004741430249), about 6 minutes. The import script lost its connection after the process started (WinError 10060); the tester did not import again, as the skill says. Export compare (1 -> 2) PASS and REST read-back PASS; checked again in the main session by REST (both exemptions, THIRD_PARTY, PRIMARY, 10).
- Tester notes, **not applied** (tested wording stays on disk): no way given to check that the tax is not live (REST `taxes` 404); after a dropped connection the summary one-liner crashes (no process log); "8 files" = 7 CSVs + metadata XML (the "other 7 files" wording is off by one); the export may already hold earlier test exemptions; no log file named for the approval.

## 0.0.1, 2026-11-24 (batch 4 part 3, AB with Claude): failed
- Read-only export: 8 files, `ZX_TAX_EXEMPTION.csv` 0 rows.
- Try 1 (ProcessId 100004742416395) TAX_AUTHORITY profile of test legal authority `GAPFILL_AB_P3_LA3`; try 2 (100004741425310) PartyTypeCode HZ_PARTIES; try 3 (100004741427510) THIRD_PARTY. All: `JBO-27014 PartyTaxProfileId ... is required`, nothing created.

## Test records created
- customer GAPFILL_AB_B4FIX_CUST1 + its THIRD_PARTY tax profile + exemption GAPFILL_AB_B4FIX_EXM1 (live); customer GAPFILL_AB_B4FIX_CUST2F + profile + exemption GAPFILL_AB_B4FIX_EXM2F (fresh test); 10 % discounts on the not live test tax GAPFILL_AB_P1_TX1.
