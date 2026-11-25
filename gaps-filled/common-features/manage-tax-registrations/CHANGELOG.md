# CHANGELOG: manage-tax-registrations (GoSaaS gap fill)

- 2026-11-25, batch 09 (AB with Claude). Skill written; live tries 1 (refused ZX-885657, GB number format) and 2 (created, read back). Fresh test TRG3F: record created, read-back as written FAILED (q with 'and' returns 0 rows). Fixed: ';' between conditions in Prerequisite 3 and Step 3; HTTP check by grep; note that post_resp.json is a full row. Re-test TRG4R on new test customer GAPFILL_AB_B9_CUST3R: PASS.
- Tester suggestions not applied (no error): say 'Steps 1b and 1c' of manage-tax-exemptions; say which client (<W> or <C>) to use for the prerequisite POSTs (<W> worked); add fields= to the profile GET.
