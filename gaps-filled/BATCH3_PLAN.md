# Batch 3 plan: Common Features (AB)

GoSaaS work, not official FSCR. Written by AB with Claude on 2026-11-23, after 16 read-only exports on ETIA-TEST (22:53 to about 23:05; nothing was imported for the plan). Method, card format and helpers: batches 1 and 2 (`BATCH1_PART1..3_RESULT.md`, `BATCH2_PLAN.md`, `BATCH2_PART1..3_RESULT.md`).

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 22:38 | 23:08 | 30 | Start session, reading, sign-in (22:43:25 to about 22:44, not in any task), Tax Zone Types check (22:44 to 22:52), 14 read-only exports (2 lanes, then 2 more), choosing, this plan |

## 0. Tax Zone Types (batch 2 leftover): settled as failed
- The 3 failed imports are ESS requests 4,481,501, 4,481,510 and 4,481,523. All 3 show `SUCCEEDED` in ESS, but their ESS logs download as empty ZIPs, and the setup-import process cannot be read with those numbers (HTTP 404). The FSM `ProcessId` is a **different number** (batch 3's tax import got `100004741395551`), and batch 2 did not keep it. So the detailed ORA- cause could not be read.
- The one extra import you approved was only for an error that shows our file is wrong. No such error could be read, so **no extra import was made**.
- New export: still 1 zone type (`US Zone Type`, mixed case with spaces, CreatedBy filled). Nothing from batch 2 was created.
- `manage-tax-zone-types/STATUS.md` stays `failed`, with the cause and "cannot do by CSV (as tested)" in its notes.

## 1. How the 10 were chosen

Rules from the brief: CSV or REST route, no approvals, nothing irreversible, a new test record can be created and read back; skip screen-only tasks, Security access and the BOSS scope; group by pattern; not a batch 1 or 2 task.

Read-only export check (2026-11-23, ETIA-TEST, one FSCR `export_setup_task_csv.py --data` each; all worked; one needed a second try):

| Task | Export | Files | Decision |
|---|---|---:|---|
| Manage Taxes | ok, 93 s | 23 (`ZX_TAX` + translation, regime + subscription files) | **in** (Part 1) |
| Manage Tax Statuses | ok, 170 s | 33 (`ZX_TAX_STATUS` + translation, all rate files) | **in** (Part 1) |
| Manage Tax Formulas | ok, 81 s | 19 (`ZX_TAX_FORMULA` + translation, empty here; rule files) | **in** (Part 1) |
| Manage Tax Rates and Tax Recovery Rates | ok on try 2, 111 s (try 1: connection drop, no ZIP) | rate files (same 31 rate files as the statuses package) | **in** (Part 2) |
| Manage Tax Jurisdictions | ok, 69 s | 5 (`ZX_JURISDICTION` + translation, empty here) | **in** (Part 2) |
| Manage Tax Condition Sets | ok, 108 s | 16 (`ORA_ZX_TAX_RULE_CONDITION_SET` + conditions) | **in** (Part 2) |
| Manage Tax Rules | ok, 80 s | 15 (`ZX_TAX_RULE_SUPERTYPE`, results, conditions) | **in** (Part 2) |
| Manage Party Fiscal Classifications | ok, 154 s | 70 (`ORA_ZX_PARTY_CLASS` 2 rows, many class-code files) | **in** (Part 3) |
| Manage Shorthand Aliases | ok, 42 s | 3 (`ORA_GL_ACCOUNT_ALIAS` + translation) | **in** (Part 3) |
| Manage Legal Authorities | ok, 99 s | 15+ (legal authority party, address, phone ...) | **in** (Part 3) |
| Manage Tree Structures / Tree Labels / Account Hierarchy Labels | ok, 25 to 65 s | 6 (tree structure, data source, label) | out: a label or structure row needs the data source GUID from the export (rule: never take IDs from an export) |
| Manage Cross-Validation Rules | ok, 43 s | 8 (key flexfield structure only) | out: the package holds no rule file |

Not tried, out on sight: Daily Rates (rates not in the package, batch 2), Intercompany Exceptions and the other "change existing" legal entity / profile tasks, document sequence assignments (they number real documents), descriptive flexfields (deploy), tasks with no CSV route (screen-only, later phase), Data Access Sets and security profiles (Security), project billing tasks (not in this module's test data).

## 2. The 10 tasks

All tax records hang off batch 2's test regime `GAPFILL_AB_TR1`, which has **no subscription**, so no business unit, legal entity or transaction can ever use them.

### Part 1 (3 tasks): tax and its first children (P9, template-row pattern)

| # | Task code | Name | Route | Pattern | depends_on | Why easy |
|---|---|---|---|---|---|---|
| 1 | `ZX_MANAGE_TAXES` | Manage Taxes | FSM CSV (`ZX_TAX` + translation; regime rows copied as parents; other files header only); read back by export compare (REST `taxes`, `taxesLOV`: 404) | P9, template row from an existing tax + `copy_parent_rows.py` | `ZX_MANAGE_TAX_REGIMES` (uses `GAPFILL_AB_TR1`) | a new tax under an unsubscribed test regime, not live for processing |
| 2 | `ZX_MANAGE_TAX_STATUSES` | Manage Tax Statuses | FSM CSV (`ZX_TAX_STATUS` + translation; rate files header only); read back by export compare | P9 card, template row | `ZX_MANAGE_TAXES` (#1's tax) | a status under the #1 test tax only |
| 3 | `ORA_ZX_MANAGE_TAX_FORMULAS` | Manage Tax Formulas | FSM CSV (`ZX_TAX_FORMULA` + translation); read back by export compare | P9, rows written out in full (the test environment has no formula to copy) | `ZX_MANAGE_TAXES` (#1's tax) | a formula on the #1 test tax; no rule points to it |

### Part 2 (4 tasks): rates, jurisdictions, condition sets, rules (P9)

| # | Task code | Name | Route | Pattern | depends_on | Why easy |
|---|---|---|---|---|---|---|
| 4 | `ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES` | Manage Tax Rates and Tax Recovery Rates | FSM CSV (`ORA_ZX_TAX_RATE_PERCENT_TYPE` + translation; other rate files header only); read back by REST `taxRatesLOV` (answers, checked) + export compare | P9 card, template row | `ZX_MANAGE_TAX_STATUSES` (#2's status) | a percentage rate on the test status; nothing calculates with it |
| 5 | `ZX_MANAGE_TAX_JURISDICTIONS` | Manage Tax Jurisdictions | FSM CSV (`ZX_JURISDICTION` + translation); read back by export compare | P9, rows in full (none exist to copy); geography by names (country), no IDs | `ZX_MANAGE_TAXES` (#1's tax) | a country-level jurisdiction for the test tax only |
| 6 | `ZX_MANAGE_TAX_CONDITION_SETS` | Manage Tax Condition Sets | FSM CSV (`ORA_ZX_TAX_RULE_CONDITION_SET` + conditions + translation); read back by export compare | P9, template row | `ZX_MANAGE_TAX_DETERMINING_FACTOR_SETS` (uses `GAPFILL_AB_FS1`) | a condition set on the test factor set; no rule uses it until #7. Use a non-geography factor, so no geography ID is needed |
| 7 | `ZX_MANAGE_TAX_RULES` | Manage Tax Rules | FSM CSV (`ZX_TAX_RULE_SUPERTYPE` + rule result files); read back by export compare | P9, template row | `ZX_MANAGE_TAXES` (#1), `ZX_MANAGE_TAX_CONDITION_SETS` (#6) | a rule on the test tax only, **disabled** (`EnabledFlag=N`) |

### Part 3 (3 tasks): stand-alone records in other packages

| # | Task code | Name | Route | Pattern | depends_on | Why easy |
|---|---|---|---|---|---|---|
| 8 | `ZX_MANAGE_PARTY_FISCAL_CLASSIFICATIONS` | Manage Party Fiscal Classifications | FSM CSV (`ORA_ZX_PARTY_CLASS` + translation; ~68 other files header only); read back by export compare | P9, template row | none | a new fiscal classification type; no party or rule uses it. Check first whether a class category can be reused (the 2 rows point to different categories) |
| 9 | `ORA_GL_MANAGE_SHORTHAND_ALIASES` | Manage Shorthand Aliases | FSM CSV (`ORA_GL_ACCOUNT_ALIAS` + translation); read back by export compare | P7, template row | none (needs a chart of accounts instance with shorthand aliases on, taken by its code) | a **disabled** alias (`EnabledFlag=N`) on an existing chart instance; nobody can pick it. Check whether `ShorthandAliasCode` needs its number prefix (if it needs an internal ID, drop the task) |
| 10 | `XLE_MANAGE_LEGAL_AUTHORITIES` | Manage Legal Authorities | FSM CSV (legal authority party + address files); read back by export compare | P10 party record, template row | none | a new legal authority party; no legal entity or tax points to it. Address by names (country), no IDs |

**Update after Part 1 (23:20):** Manage Tax Statuses **failed** (Oracle rejects the test tax for a status: `ZX_INVALID_VALUE ... Tax attribute`; the tax is not live and its regime has no subscription, both on purpose). So:
- **#4 Tax Rates is blocked** (a rate needs a status). Part 2 should skip it and mark it `failed` with "blocked by ZX_MANAGE_TAX_STATUSES", A simulation tax (23:28 to 23:33) and a business-unit subscription of the test regime (23:52, AB approved) were both tried and do **not** help; statuses stopped at 3 attempts. Only a global configuration owner subscription (screen, or internal IDs) is left.
- **#5 Jurisdictions and #7 Rules** also point at the test tax and may hit the same check. Try each once; on the same `ZX_INVALID_VALUE ... Tax` error, stop that task (do not change the tax or add a subscription).
- **#6 Condition Sets** does not use the tax and is not affected. Formulas (#3) did accept the test tax.

**Order:** Part 1 first (1 before 2 and 3). Part 2 after Part 1: 4 needs #2, 5 needs #1, 7 needs #1 and #6, so 6 before 7. Part 3 does not depend on Parts 1 or 2 and can run at any time.

**Records from batch 2 that are needed:** `GAPFILL_AB_TR1` (regime, Parts 1 and 2), `GAPFILL_AB_FS1` (factor set, Part 2 #6). Neither is changed; a child package may carry the parent row unchanged.

## 3. Expected time (from batches 1 and 2)

| Kind | Working | Oracle waiting | Fresh test |
|---|---:|---:|---:|
| first skill of a new package (#1, #3, #5, #8, #10) | 5 to 11 | 3 to 6 | 3 to 5 |
| card on a known package / template row (#2, #4, #6, #7, #9) | 2 to 5 | 2 to 4 | 2 to 4 |

Tax exports take 70 to 170 s and imports about 80 s, so every tax task has 4 to 6 minutes of Oracle waiting. Plan a second sign-in after about 50 minutes.

## 4. RULES (every part)

```text
RULES
1. Skills must be generic and work in any Fusion environment; never specific to ETIA-TEST data, names or IDs. ETIA-TEST is only for verifying.
2. Test records are named GAPFILL_AB_P<part number>_<name> (for example GAPFILL_AB_P2_RT1), so chats running at the same time never see each other's records, and each fresh test compares only its own record.
3. No deletes.
4. Sign-in on port 8765; never print tokens or secret values.
5. Per task: export the task read-only, write SKILL.md, load a test record, read it back, then a fresh sub-agent tests using only the task name + SKILL.md.
6. A gap counts as filled only when tested.
7. If you change any wording after the fresh test, run the fresh test again; never leave retest_after_wording_fix pending.
8. Evidence screenshots (what was missing, how it was found, the skill, the test result) go in gaps-filled\evidence\batch-03\<task code>\.
9. STATUS.md keys in this order: task_code, task_name, module, status (tested|written|failed), filled_by, date, minutes_to_write, minutes_to_test, waiting_minutes, fresh_claude_pass, route, depends_on, test_records, notes.
10. Log working minutes separately from minutes waiting for approvals or sign-in.
11. Do not touch other parts' tasks.
12. At the end run python rebuild_index.py in gaps-filled and check there are no problems; write BATCH3_PART<n>_RESULT.md.
13. If the Oracle connection drops, retry the export (read-only, new folder, one at a time, up to 3 tries). Before any re-import, check whether the record already exists (REST or a new export); never import twice.
14. Text types may have a minimum length (for example a TEXT reporting type needs MinLength); read the error and set it.
15. Names may have maximum lengths (for example 15 characters for withholding tax calendar names). Find the limit in the live test and count the fresh tester's likely name (PREFIX + about 4 characters) against it; give the builder --max-len.
16. Never tell a skill to take IDs from an export (internal numbers, GUIDs). Use codes and names; if a row can only be built with an internal ID, the task is not easy: drop it or mark it failed.
17. Profile-style (hierarchical) imports need the parent row in the file: copy it unchanged with common-features\manage-profile-options\scripts\copy_parent_rows.py (only your own GAPFILL_ parents).
18. Keep the FSCR ProcessId printed by every import in the run log: it is the only key to the full process log (ESS request numbers do not open it).
```

## 5. Where things go
- Skills: `gaps-filled\common-features\<task-folder>\` (`SKILL.md`, `STATUS.md`, `CHANGELOG.md`, `scripts\` when needed). Task folders: `manage-taxes`, `manage-tax-statuses`, `manage-tax-formulas`, `manage-tax-rates`, `manage-tax-jurisdictions`, `manage-tax-condition-sets`, `manage-tax-rules`, `manage-party-fiscal-classifications`, `manage-shorthand-aliases`, `manage-legal-authorities`.
- Evidence: `gaps-filled\evidence\batch-03\<TASK_CODE>\`.
- Work files: a temporary `gaps-filled\_work_b3p<n>\` folder, deleted at the end of each part.
