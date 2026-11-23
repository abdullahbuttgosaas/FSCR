# CHANGELOG: manage-tax-regimes (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-23 (batch 2 part 3, filled by AB with Claude)
- Wrote SKILL.md on the batch 1 generic helpers plus a new generic helper `scripts/template_row.py`. It copies one export row as the template for a new record; manage-tax-factor-sets uses it too.
- Live test, in order:
  - **Export:** 12 regimes. The first try ran in parallel with other exports and lost the network. Because a `/e/...` path was passed, the script wrote the ZIP to a wrong folder (`E:\e\...`). I moved it back and added the `E:/` path rule to the skill.
  - **REST before-read:** 0 rows.
  - **Import:** 1 attempt. The script lost the connection after the process started. I did not re-import; REST showed the regime 1 minute later.
  - **REST read-back:** PASS.
  - **Export compare:** PASS. 1 regime and 1 translation were added; the 7 subscription and usage files were unchanged.
- REST: `taxRegimes` returns HTTP 404. `taxRegimesLOV` works with `--q "TaxRegimeCode='...'"`.

## Fresh test 1, 2026-11-23 21:19-21:22: PASS
- The sub-agent got only the task name and this SKILL.md path. It created `GAPFILL_AB_TR2F` (template GB) with 1 import, and both REST and the compare passed. It needed no help.
- Notes applied as wording after this test:
  - added a short one-liner that summarises the import log (the raw log repeats lines and keeps `\t` and `\/`);
  - the regime row shows as detail object `TaxRegime` under another business object's name;
  - which template to take when the person names no country.

## Re-test after the wording fix, 2026-11-23 21:30-21:33: PASS
- A new sub-agent ran under the same rules. It created `GAPFILL_AB_TR3R` (template: the first listed non-test regime) with 1 import. REST passed and the compare passed (14 -> 15 regimes).
- Note NOT applied (to keep the tested wording): the FSCR scripts print `StatusCode: (unknown)` even on success, and the skill does not say this is harmless.
- Main-session REST read-back at 21:36: TR1, TR2F and TR3R are all present. PASS.

## Test records created (may not be deletable; no subscription, so no transaction uses them)
| When | Who | Record |
|---|---|---|
| live test | main session | regime `GAPFILL_AB_TR1` (reporting types RT1 and RT2F were later added under it) |
| fresh test 1 | sub-agent | regime `GAPFILL_AB_TR2F` |
| re-test | sub-agent | regime `GAPFILL_AB_TR3R` |


## Note, 2026-11-23 23:52 (batch 3 part 1, AB approved): test regime now subscribed
- `GAPFILL_AB_TR1` was subscribed by the existing test business unit `ZZ_TEST_BU_1932` (one `ZX_MANAGE_TAX_REGIMES` import, ProcessId 100004741401398): `ORA_ZX_BU_REGIME_USAGE` + `ZX_BU_REGIME_SUBSCRIPTION` (`GCO_ONLY`, from 2026/01/01, enabled) + `ORA_ZX_BU_REGIME_SUB_DETAIL` (`ViewOptionsCode=NONE`, parent `GCO`), with the regime rows re-sent unchanged. First try failed (`ZX_REQUIRED_VALUE: FirstPtyOrgId`); it worked with `FirstPtyEnterpriseId=1` on the usage and detail rows (copied from every existing usage row). The after-export shows exactly these 3 rows added, nothing else changed.
- Why: a test for Manage Tax Statuses. It did not help (see `manage-tax-statuses`).
- Impact: the regime's taxes are not live (one is in simulation), so no transaction of that business unit changes. The subscription was not deleted (no-delete rule).
- SKILL.md was **not** changed (it still says: no subscription in a test), so no re-test is pending.
