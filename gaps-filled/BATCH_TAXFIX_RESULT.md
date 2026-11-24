# Batch taxfix: the 4 failed tax gaps (result)

GoSaaS work, not official FSCR. AB with Claude, 2026-11-24, ETIA-TEST only (release 11.13.26.10.0). FSCR scripts ran in place from `fscr-main/fscr-module-test-pack`; no FSCR file was edited. Nothing deleted, nothing committed or pushed.

## Result in short
| Task | Before | Now | Real cause |
|---|---|---|---|
| Manage Tax Statuses (`ZX_MANAGE_TAX_STATUSES`) | failed (3 tries) | **tested**, fresh test + re-test PASS | the tax's regime had no **global configuration owner (GCO) option row** (`ORA_ZX_BU_GCO_TAX_SUB.csv`) |
| Manage Tax Rates and Tax Recovery Rates (`ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES`) | failed (blocked) | **tested**, fresh test PASS | same: without the GCO row no status could exist |
| Manage Tax Rules (`ZX_MANAGE_TAX_RULES`) | failed (3 tries) | **tested**, fresh test PASS | same GCO row |
| Manage Tax Zone Types (`ZX_MANAGE_TAX_ZONE_TYPES`) | failed (3 tries) | **failed** (3 more tries) | not the file: Oracle's database refuses the insert into `HZ_GEOGRAPHY_TYPES_B` even for a row equal to the working zone type; the `ORA-` reason is not readable by CSV or REST |
| Prerequisite: Manage Tax Regimes Step 7 (`ZX_MANAGE_TAX_REGIMES`) | did not exist | **new step, tested**: fresh test + re-test PASS | - |

Index (`python rebuild_index.py`): **No problems**; all 19 modules **31 tested** of 935 (was 28); Common Features 29 tested, 1 failed.

## Time log
| Start | Finish | Minutes | What |
|---|---|---:|---|
| 14:34 | 14:35 | 1 | Read CONTEXT, CHANGELOG, the 4 skills, batch 2/3 results |
| 14:35:14 | 14:35:35 | 0 | Sign-in on port 8765 (browser still signed in; not counted) |
| 14:35 | 14:41 | 6 | 7 read-only exports (all first try, 42 to 99 s), old process logs by ProcessId, field-by-field compare |
| 14:41 | 14:44 | 3 | Prerequisite import + read-back export |
| 14:44 | 14:53 | 9 | Statuses, rates, rules: 1 import each, all first try; read-back exports |
| 14:53 | 14:56 | 3 | Zone types tries 1 and 2 |
| 14:56 | 15:01 | 5 | Skills rewritten (statuses, rates, rules, regimes Step 7) |
| 15:01 | 15:24 | 23 | Fresh tests: regimes Step 7 (+ re-test), statuses (+ re-test), rates, rules; test tax for them; zone types try 3 and after-export |
| 15:21 | 15:30 | 9 | Cards, changelogs, evidence, index, this report, cleanup |

Per task (also on each STATUS.md card; earlier batches included): statuses write 17 / test 12 / wait 24; rates 12 / 6 / 6; rules 14 / 6 / 11; zone types 16 / 0 / 9. Regimes Step 7 in this batch: write 5, test 6, wait 4 (the regimes card keeps its batch 2 numbers and a note).

## Step 1: diagnosis (read-only, with proof)
- **Old logs.** Status try 3 (ProcessId 100004741398375): row `GAPFILL_AB_TR1, GAPFILL_AB_P1_TX1, GAPFILL_AB_P1_ST3, -99`, `ZX_INVALID_VALUE: You must provide a valid value for the Tax attribute`. Rule try 3 (100004742403274): `ZX_RECRATE_DATE_INVALID ... {TAX_START_DATE} to {TAX_END_DATE}` with **empty placeholders**: the tax was not found. Zone types 4,481,501 / 510 / 523: the ProcessIds were never kept, and REST cannot list them (`SetupTaskCSVImportProcess` returns 0 items without an id), so their full logs stay unreadable; the evidence picture of batch 2 shows the row validated and the object failed with `JBO-26041`.
- **Working setup exported** (regimes, taxes, statuses, rates, rules, zone types, configuration owner tax options). Field by field:
  - The one GCO tax that has a status (and a rate) and our test tax differ only in option flags (rounding, recoverability, place of supply, live flag). Batch 3 had already ruled out "not live" (simulation tax) and "no subscription" (business-unit subscription).
  - `ORA_ZX_BU_GCO_TAX_SUB.csv` had **12 rows, one for every regime that owns tax content** (`FirstPtyOrgId` and `ParentFirstPtyOrgId` -99, `ViewOptionsCode` VFC, `SubscriptionOptionId` 0). Our test regime had **none**. That is the cause for statuses, rates and rules (proved: after adding it, all three imported on the first try).
  - Zone types: the export has 1 zone type, made on the screen; see Tax Zone Types below.

## Step 2: prerequisite
- The GCO option row is part of the task **Manage Tax Regimes** (its configuration options), in the same CSV package (`ORA_ZX_BU_GCO_TAX_SUB.csv`). The separate catalog task `ZX_MANAGE_CONFIGURATION_OWNER_TAX_OPTIONS` is something else (owner options per event class; exported read-only, not needed).
- Done by CSV: one row copied from an existing GCO row with `template_row.py` (no value typed in; -99 is Oracle's fixed id of the global configuration owner, the same on every row), regime code and start date set, the regime rows re-sent unchanged. ProcessId 100004742409055; read-back export: exactly 1 row added. The browser was not needed for this.
- Written as **Step 7 of `manage-tax-regimes`** (not a separate skill folder: it is the same Oracle task, and the index allows one card per task code). Listed in `depends_on` of statuses, rates and rules. Fresh test PASS on `GAPFILL_AB_TR2F`, 2 wording fixes, re-test PASS on `GAPFILL_AB_TR3R`.
- Effect: no tax is live, no business-unit or legal-entity subscription was added, so no transaction changes.
- Proof that the GCO row alone is enough: `GAPFILL_AB_TR2F` has **no** business-unit subscription, and the status, rate and rule fresh tests all passed on its new tax.

## Step 3: fix and retry (what changed before each import, and why)
Full notes: `_work_taxfix/LOG.md` (deleted with the work folder; summary here).
| # | Task | What changed and why | ProcessId | Result |
|---|---|---|---|---|
| P | regimes Step 7 | add the GCO row the working regimes have | 100004742409055 | created, read back |
| S1 | statuses | regime now has the GCO row; status copied from the working GCO status | 100004741413261 | created first try |
| R1 | rates | first rate import ever: status now exists; GCO percentage rate template, parent status re-sent | 100004741411939 | created first try |
| L1 | rules | same disabled rule as before; regime now has the GCO row; `EnterpriseId` empty like every GCO row | 100004742410090 | created first try |
| Z1 | zone types | no translation row; country by names | 100004742410256 | refused (`JBO-26041`); log now shows the SQL; names did not set the country limit |
| Z2 | zone types | whole working zone type row copied (limit id from the export) | 100004742410458 | refused, same |
| Z3 | zone types | as Z2 + code in the working row's style | 100004742411036 | refused, same; nothing created (after-export) |

## Step 4: tests and records
| Test | Who | Record | ProcessId | Result |
|---|---|---|---|---|
| regimes Step 7 | fresh sub-agent | GCO row of `GAPFILL_AB_TR2F` | 100004742409416 | PASS |
| regimes Step 7 re-test | fresh sub-agent | GCO row of `GAPFILL_AB_TR3R` | 100004742410710 | PASS |
| statuses | fresh sub-agent | `GAPFILL_AB_TF_ST2F` on `GAPFILL_AB_TF_TX2` | 100004741414186 | PASS |
| statuses re-test | fresh sub-agent | `GAPFILL_AB_TF_ST3R` on `GAPFILL_AB_P1_TX2F` | 100004741415225 | PASS |
| rates | fresh sub-agent | `GAPFILL_AB_TF_RT2F` (7 %) | 100004741413676 | PASS |
| rules | fresh sub-agent | `GAPFILL_AB_TF_RL2F` (disabled) | 100004741413821 | PASS |
Every one read back by me from its after-export. No `retest_after_wording_fix` is pending: statuses and regimes were re-tested after their wording fixes; the notes of the last tests are in each CHANGELOG and were not applied.

**All records created (none edited except the GCO rows added to test regimes; none deleted):** GCO option rows on `GAPFILL_AB_TR1`, `GAPFILL_AB_TR2F`, `GAPFILL_AB_TR3R`; tax `GAPFILL_AB_TF_TX2` (not live, for the fresh tests); statuses `GAPFILL_AB_TF_ST1`, `ST2F`, `ST3R`; rates `GAPFILL_AB_TF_RT1` (5 %), `RT2F` (7 %); rules `GAPFILL_AB_TF_RL1`, `RL2F` (both **disabled**). All on not-live test taxes. Zone types: none created.

Evidence: `evidence/batch-taxfix/<task code>/` (`01_cause`, `02_prerequisite`, `04_test_result`, `05_fresh_test`; zone types `04_test_result`). Text only, no tokens, server addresses or user names.

## Tax Zone Types: still failed, exact blocker
- The `GeographyType` row passes every application check (`1 rows were processed. 0 rows of them failed`). Then the database refuses `INSERT INTO HZ_GEOGRAPHY_TYPES_B(GEOGRAPHY_TYPE, OBJECT_VERSION_NUMBER, GEOGRAPHY_USE, POSTAL_CODE_RANGE_FLAG, LIMITED_BY_GEOGRAPHY_ID, CREATED_BY_MODULE, who columns, GEOGRAPHY_TYPE_ID)` with `JBO-26041`.
- Try Z3's row equals the working, screen-made zone type in every column except the code, so the CSV file is no longer the cause. Ruled out: translation row, missing country limit, dates, code style.
- The `ORA-` line is not readable by CSV or REST: the process log stops at the SQL; the import result has only the `ProcessLog` enclosure; the ESS log of requests 4,483,619 and 4,483,683 is an empty ZIP.
- Browser (last resort, only to read the request log): the browser pane reached Oracle's sign-in page; no one signed in during the run, so the log was not read. CSV/REST were not enough because they never return the database message.
- Follow-up, same day: AB opened request 4,483,683 in Scheduled Processes: `Export or Import Setup Data`, status Succeeded, **Log and Output attachment: None**. So the screen has no `ORA-` line either.
- Follow-up 2: AB made reference zone type `GAPFILL_AB_TF_ZT1` **on the screen and it saved**. Read-only export (ProcessId 100004742409666): use `TAX`, flag `N`, module `HZ_GEO_HIERARCHY`, no country limit. It was made by the **same Oracle user** that runs the CSV import. Batch 2 attempt 2 sent the same shape by CSV and was refused.
- **Conclusion:** not access, not the file. The setup CSV import of zone types fails where the screen works (GUESS: Oracle defect). **Needed: an Oracle SR** with ProcessId 100004742411036, the SQL from its process log, and this comparison (evidence `06_screen_reference.txt`). Until then, make zone types on the screen.

## What a skill needs as a prerequisite (for the next tax gaps)
- Tax statuses, rates, rules (and likely exemptions, exceptions and other content below a GCO tax): the regime's **GCO option row** (`manage-tax-regimes` Step 7). Check it in a **taxes** export (`ORA_ZX_BU_GCO_TAX_SUB.csv`).
- Rates: a status (`manage-tax-statuses`), whose parent rows go into the rate ZIP unchanged.
- Rules: factor set and condition set (`manage-tax-factor-sets`, `manage-tax-condition-sets`); keep rules disabled.
- A tax does **not** need to be live, and no business-unit subscription is needed.

## Cleanup
- Sub-agents: 6 fresh tests, all finished. The sign-in listener exited after sign-in; the export monitor expired; no Python process or server started here is left; nothing listens on port 8765. The browser pane tab was closed.
- Work folder `gaps-filled/_work_taxfix` (exports, payloads, logs) deleted after this report.
- `manage-taxes/SKILL.md` Rules item 5 corrected (the old GUESS about live taxes was wrong); its tested steps are unchanged.
