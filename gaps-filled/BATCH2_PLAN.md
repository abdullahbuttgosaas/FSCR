# Batch 2 plan: Common Features (AB)

GoSaaS work, not official FSCR. Written by AB with Claude on 2026-11-23, after 21 read-only exports on ETIA-TEST (19:34 to 19:45; nothing was imported for the plan). Method and card format: batch 1 (`BATCH1_PART1..3_RESULT.md`, the 10 cards in `common-features\`).

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 19:26 | 19:46 | 20 | Start session, reading, sign-in (19:31:40 to 19:34:27, about 3 min, not in any task), 21 read-only exports (about 9 min Oracle waiting, in 4 parallel waves), choosing, this plan |

## 1. How the 10 were chosen

Rules from the brief: CSV or REST route exists, no approvals, nothing irreversible that others would notice, a new test record can be created and read back; skip screen-only tasks and anything needing Security access or the BOSS scope; group by pattern so later tasks reuse earlier work.

Read-only export check (2026-11-23, ETIA-TEST, one FSCR `export_setup_task_csv.py --data` each):

| Task | Export | Files | Decision |
|---|---|---:|---|
| Manage Applications Core Profile Options | ok, 24 s | 3 | **in** (Part 1) |
| Manage Applications Core Administrator Profile Values | ok, 27 s | 3 (same package as profile options) | **in** (Part 1) |
| Manage Applications Core Profile Categories | ok, 42 s | 2 | **in** (Part 1) |
| Manage Profile Categories | ok, 24 s | 2 (same package) | **in** (Part 1) |
| Manage Document Sequences | ok, 61 s | 2 | **in** (Part 2) |
| Manage Withholding Tax Calendars | ok, 116 s | 2 (`AP_OTHER_PERIOD_TYPE` + periods) | **in** (Part 2) |
| Manage Tax Zone Types | ok, 165 s | 8 (geography type + 7 empty) | **in** (Part 2) |
| Manage Tax Regimes | ok, 117 s | 8 | **in** (Part 3) |
| Manage Tax Reporting Types | ok, 78 s | 13 (all empty but 2) | **in** (Part 3) |
| Manage Tax Determining Factor Sets | ok, 149 s | 14 | **in** (Part 3) |
| Manage Daily Rates | ok, 25 s | export holds only rate types, no daily rates | out: the rates are not in the package |
| Manage Resource Note Type Mapping | ok, 26 s | 2 | out: a mapping changes which note types an existing object shows (shared) |
| Manage Intercompany Exceptions | ok, 60 s | 7 legal entity files | out: changes existing legal entities |
| Manage Location of Final Discharge | ok, 114 s | 2 (113-column location file) | out: needs a real address/location; not easy |
| Manage Transaction (Based) Fiscal Classifications | ok, 235 to 269 s | 40 | out: large package |
| Manage Taxes, Manage Tax Statuses | **failed** (no ZIP) | | out |
| Manage Applications Core Attachment Entities | **failed** (no ZIP) | | out |

## 2. The 10 tasks

### Part 1 (4 tasks): Applications Core profiles (one FSM package family; full skill first, then cards)

| # | Task code | Name | Route | Pattern | depends_on | Why easy |
|---|---|---|---|---|---|---|
| 1 | `FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS` | Manage Applications Core Profile Options | FSM CSV (`FND_APP_PROFILE_OPTION` + levels + values); read back by REST `profileOptions/<name>` + export compare | P3 profiles, full skill | none | a new `GAPFILL_AB_` profile option definition is stand-alone: no code reads it, so no one is affected; batch 1 helpers build and compare the package |
| 2 | `FND_MANAGE_APPLICATIONS_CORE_ADMINISTRATOR_PROFILE_VALUES` | Manage Applications Core Administrator Profile Values | FSM CSV (same package, value file only); read back by REST `profileOptions/<name>/child/siteProfileOptionValues` | P3 card over #1 | `FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS` | sets a site value only on the `GAPFILL_AB_` option made in #1, never on a real option; same package and helpers |
| 3 | `FND_MANAGE_APPLICATIONS_CORE_PROFILE_CATEGORIES` | Manage Applications Core Profile Categories | FSM CSV (`FND_APP_PROFILE_CATEGORY` + category options); read back by export compare (REST checked first) | P3, small new package | `FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS` | new stand-alone category; its one option link points to the `GAPFILL_AB_` option from #1, so no real option is regrouped |
| 4 | `FND_MANAGE_PROFILE_CATEGORIES` | Manage Profile Categories | FSM CSV (same package as #3) | P3 card over #3 | `FND_MANAGE_APPLICATIONS_CORE_PROFILE_OPTIONS` | same 2 files as #3 (export checked); only the task code and scope differ |

### Part 2 (3 tasks): stand-alone records with child rows (P7/P8, batch 1 generic helpers)

| # | Task code | Name | Route | Pattern | depends_on | Why easy |
|---|---|---|---|---|---|---|
| 5 | `FND_MANAGE_DOCUMENT_SEQUENCES` | Manage Document Sequences | FSM CSV (`FND_APP_DOCSEQ` + assignment file, header only); read back by export compare | P8, helpers from batch 1 | none for the sequence alone; `FND_MANAGE_DOCUMENT_SEQUENCE_CATEGORIES` only if an assignment is added (not in the test) | a new sequence with **no assignment** numbers nothing; application and module copied from an export row |
| 6 | `ORA_ZX_MANAGE_WITHHOLDING_TAX_CALENDARS` | Manage Withholding Tax Calendars | FSM CSV (`AP_OTHER_PERIOD_TYPE` + `AP_OTHER_PERIOD_PERIOD`); read back by export compare | P7, same shape as transaction calendars (batch 1) | none | new calendar header + 12 periods; no withholding tax uses it |
| 7 | `ZX_MANAGE_TAX_ZONE_TYPES` | Manage Tax Zone Types | FSM CSV (`ORA_TRADING_COMMUNITY_GEOGRAPHY_TYPE` + translation, 6 other files header only); read back by export compare | P9, first tax package | none | a new zone type (geography use TAX) with no zones and no ranges; nothing calculates with it |

### Part 3 (3 tasks): transaction tax roots (P9)

| # | Task code | Name | Route | Pattern | depends_on | Why easy |
|---|---|---|---|---|---|---|
| 8 | `ZX_MANAGE_TAX_REGIMES` | Manage Tax Regimes | FSM CSV (`ZX_TAX_REGIME` + translation, subscription files header only); read back by export compare and REST if a resource exists | P9, full skill for the ZX header shape | none | a new `GAPFILL_AB_` regime with **no subscription** and no taxes is not used by any business unit or legal entity |
| 9 | `ZX_MANAGE_TAX_REPORTING_TYPES` | Manage Tax Reporting Types | FSM CSV (`ORA_ZX_REPORTING_TYPE` + translation + codes + usage); read back by export compare | P9 card on #8 | `ZX_MANAGE_TAX_REGIMES` (the test type is attached to the #8 regime) | new reporting type and code on the test regime only |
| 10 | `ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS` | Manage Tax Determining Factor Sets | FSM CSV (`ORA_ZX_TAX_RULE_TEMPLATE` + translation; other files header only); read back by export compare | P9, same header shape as #8 | none | a new factor set is a stand-alone header + factor lines; no condition set or rule uses it (Tax Condition Sets is a later task) |

**Order inside the batch:** 1 before 2, 3 and 4; 3 before 4 (card); 8 before 9. Parts 2 and 3 do not need Part 1's records, so they can run in either order, but Part 2's #7 opens the ZX package shape that Part 3 reuses, so Part 2 should run before Part 3.

**Records from batch 1 that are not needed:** the sequence in #5 is tested without an assignment, so `GAPFILL_DSC_T1` is not touched.

## 3. Expected time (from batch 1)

| Kind | Working | Oracle waiting | Fresh test |
|---|---:|---:|---:|
| first skill of a new package (#1, #3, #8) | 5 to 11 | 2 to 3 | 2 to 3 |
| card on a known package (#2, #4, #9) | 1 to 3 | 1 to 2 | 2 to 3 |
| simple package with batch 1 helpers (#5, #6, #7, #10) | 2 to 4 | 1 to 3 | 2 to 3 |

Tax exports are slow (78 to 270 s each), so Parts 2 and 3 will have more waiting than Part 1. Plan a second sign-in after about 50 minutes of a run.

## 4. RULES (every part)

```text
RULES
1. Skills must be generic and work in any Fusion environment; never specific to ETIA-TEST data, names or IDs. ETIA-TEST is only for verifying.
2. Test records are named GAPFILL_AB_<name>.
3. No deletes.
4. Sign-in on port 8765; never print tokens or secret values.
5. Per task: export the task read-only, write SKILL.md, load a test record, read it back, then a fresh sub-agent tests using only the task name + SKILL.md.
6. A gap counts as filled only when tested.
7. If you change any wording after the fresh test, run the fresh test again; never leave retest_after_wording_fix pending.
8. Evidence screenshots (what was missing, how it was found, the skill, the test result) go in gaps-filled\evidence\batch-02\<task code>\.
9. STATUS.md keys in this order: task_code, task_name, module, status (tested|written|failed), filled_by, date, minutes_to_write, minutes_to_test, waiting_minutes, fresh_claude_pass, route, depends_on, test_records, notes.
10. Log working minutes separately from minutes waiting for approvals or sign-in.
11. Do not touch other parts' tasks.
12. At the end run python rebuild_index.py in gaps-filled and check there are no problems; write BATCH2_PART<n>_RESULT.md.
```

## 5. Where things go

- Skills: `gaps-filled\common-features\<task-folder>\` (`SKILL.md`, `STATUS.md`, `CHANGELOG.md`, `scripts\` when needed). Task folders: `manage-profile-options`, `manage-admin-profile-values`, `manage-appcore-profile-categories`, `manage-profile-categories`, `manage-document-sequences`, `manage-withholding-tax-calendars`, `manage-tax-zone-types`, `manage-tax-regimes`, `manage-tax-reporting-types`, `manage-tax-factor-sets`.
- Evidence: `gaps-filled\evidence\batch-02\<TASK_CODE>\` (rule 8; this follows the brief, not the README's per-module evidence folder).
- Work files (exports, payloads, logs): a temporary `gaps-filled\_work_b2\` folder, deleted at the end of each part.
