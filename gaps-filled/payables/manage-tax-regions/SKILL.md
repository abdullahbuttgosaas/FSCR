---
name: manage-tax-regions
task_code: AP_MANAGE_TAX_REGIONS
task_name: Manage Tax Regions
module: Payables
route: FSM setup CSV export/import (task level), AP_INCOME_TAX_REGION.csv; REST read-back payablesIncomeTaxRegions
---

# Manage Tax Regions (income tax regions, CSV)

## What it is and when to use

Creates a Payables income tax region (US 1099 reporting state/region; table AP_INCOME_TAX_REGIONS; business
object "TenNinetyNineTaxRegion") through the FSM setup CSV import of task `AP_MANAGE_TAX_REGIONS`. Regions
are used by 1099 reporting (combined filing program). The predefined list holds the US states and
territories (two-letter short names).

## Placeholders

| Placeholder | Meaning |
| --- | --- |
| `<FSCR_ROOT>` | FSCR repository root (run every command from there) |
| `<RUN>` | a run folder OUTSIDE the repository and outside any git repo |
| `<SHORT_NAME>` | the new region short name, MAX 10 characters (see Rules) |
| `<LONG_NAME>` | the region name shown to users (for a test, put your full test prefix here) |
| `<METHOD>` | reporting limit method: `FEDERAL`, `INDIVIDUAL` or `SUM` (VERIFIED in the data) |
| `<GF_SCRIPTS>` | `gaps-filled/payables/scripts` inside the pack (helper scripts, standard library only) |
| `<YOUR_TEST_PREFIX>` | a text every new row must contain (safety check in the builder) |
| `<REST_VER>` | `11.13.18.05` |

Create `<RUN>` first (`mkdir -p <RUN>`). Do not share it: the raw export CSVs and logs in it hold user names.

## Sign-in

Use FSCR's `core/auth/fusion-oauth-authentication` (`fusion_login.py`, token cache `auto`). A sign-in lasts
about one hour. If you are not allowed to sign in yourself, stop and report on HTTP 401/403; otherwise
sign in again and continue. Never print tokens, server addresses or user names.

## Prerequisites

1. Signed in. A region is stand-alone.
2. The short name must be new (REST, read only; `items: 0` = free). REST names the short name `state`
   (lower case; upper-case attribute names give HTTP 400, VERIFIED):
   ```bash
   python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/payablesIncomeTaxRegions \
     --q "state='<SHORT_NAME>'" --fields state,regionName --out <RUN>/check.json
   ```

## Export (read only)

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_TAX_REGIONS --run <RUN> --label before
python3 <GF_SCRIPTS>/inspect_export.py <RUN>/before.zip
```

"status (unknown)" is normal. One CSV (VERIFIED): `AP_INCOME_TAX_REGION.csv`: RegionShortName, RegionCode,
RegionLongName, ReportingLimit, NumOfPayees, ControlTotal1-10, ControlTotal13, ControlTotal14,
ControlTotal15a, ControlTotal15b, ActiveDate, InactiveDate, ReportingLimitMethodCode, who/date columns.

## Build rows

`<RUN>/rows.json`, ONE row (VERIFIED):

```json
{"AP_INCOME_TAX_REGION.csv": [{"RegionShortName": "<SHORT_NAME>", "RegionLongName": "<LONG_NAME>",
  "ReportingLimitMethodCode": "<METHOD>"}]}
```

- RegionCode (the state code used in the combined filing file), ReportingLimit (for method INDIVIDUAL) and
  the control totals are optional (GUESS: not loaded live; Oracle doc "Income Tax Reporting Options").
- Leave who-columns empty (VERIFIED).

```bash
python3 <GF_SCRIPTS>/build_fsm_package.py --export <RUN>/before.zip --rows <RUN>/rows.json \
  --prefix <YOUR_TEST_PREFIX> --max-len RegionShortName=10 --out <RUN>/load.zip
```

## Import

```bash
python3 <GF_SCRIPTS>/gf_import.py --task-code AP_MANAGE_TAX_REGIONS --zip <RUN>/load.zip --run <RUN> --label imp1
```

The console lines "StatusCode: (no result yet)" / "(unknown)" are normal. In the process-log lines that
gf_import prints look for (VERIFIED): "Detail Object: TenNinetyNineTaxRegion. Status: Completed successfully
... 1 rows were processed. 0 rows of them failed" and "Total Objects Failed: 0". Keep the ProcessId
(`<RUN>/imp1_processid.txt`). If the connection drops after the import started, do NOT import again: wait
2 minutes and run the REST check of Prerequisites step 2.

## Read back

```bash
python3 <GF_SCRIPTS>/gf_export.py --task-code AP_MANAGE_TAX_REGIONS --run <RUN> --label after
python3 <GF_SCRIPTS>/compare_fsm_exports.py --before <RUN>/before.zip --after <RUN>/after.zip --prefix <YOUR_TEST_PREFIX>
python3 <GF_SCRIPTS>/rest_read.py --endpoint /fscmRestApi/resources/<REST_VER>/payablesIncomeTaxRegions \
  --q "state='<SHORT_NAME>'" --fields state,regionName,reportingLimitMethod --out <RUN>/rest_readback.json
```

Pass = AP_INCOME_TAX_REGION.csv +1, `RESULT: OK - only prefix rows added, nothing removed or changed`, and REST
returns 1 item with your long name and method (VERIFIED).

## Rules and limits

- RegionShortName is short: 15 characters fail with `JBO-27040: Value ... for field RegionShortName exceeds
  the maximum length allowed` and 10 characters work (VERIFIED); the column is 10 characters (GUESS from
  Oracle's table docs). A 12-character test prefix does not fit: use a 10-character name that still starts
  with your record prefix rule (for example `FSCRT_XX_1`) and put the full test prefix in RegionLongName.
- New regions only; never re-send an existing region (the import merges by short name and would update the
  predefined states); never load the full export back.
- A new region appears in the 1099 region list for suppliers; give it a clear test name.

## Worked example (sitting 1)

- try 1 `FSCRT_AK_GF_TR1` refused (JBO-27040, ProcessId 100004743425947). try 2 `FSCRT_AK_1`, long name
  "FSCRT_AK_GF_ test income tax region 1", method FEDERAL: ProcessId 100004743427182, 1 row processed,
  0 failed; compare +1, removed/changed 0; REST 1 item (VERIFIED). Row counts depend on the environment.
