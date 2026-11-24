# Batch 4 plan: Common Features (AB)

GoSaaS work, not official FSCR. Written by AB with Claude on 2026-11-24, after 16 read-only planning exports on ETIA-TEST (17:12 to 17:20; nothing was imported for the plan). Method, card format and helpers: batches 1 to 3 and the two taxfix batches (`BATCH3_PLAN.md`, `BATCH3_PART1..3_RESULT.md`, `BATCH_TAXFIX_RESULT.md`, `BATCH_TAXFIX2_RESULT.md`).

| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 17:04 | 17:12 | 8 | Start session (git pull, CONTEXT, CHANGELOG, BIG_FILES, index: 935 rows, 32 tested, no problems), reading batch 3 plan and results, taxfix results, PEOPLE_PROMPT, 3 cards |
| 17:11:50 | 17:11:59 | 0 | Sign-in on port 8765 (nothing was listening there before; not counted in any task) |
| 17:12 | 17:21 | 9 | 16 read-only planning exports (4 lanes), REST look-ups of application and module ids, choosing |
| 17:29 | 17:33 | 4 | This plan (written after Part 1's live loads, which ran 17:18 to 17:29) |

## 1. How the 12 were chosen

Rules from the brief: CSV or REST route, a new test record can be created and read back, nothing irreversible, nothing that changes shared live settings or existing users, no screen-only tasks, no Security access, no Risk scope; easy first, then medium (said so); group by pattern; never a task already tested or failed (all 32 cards are tested; none of the 12 has a card).

Read-only export check (2026-11-24, ETIA-TEST, one FSCR `export_setup_task_csv.py --data` each, all worked first try):

| Task | Export | Files (rows) | Decision |
|---|---|---|---|
| Manage Legal Entity Configurator Profile Options | 29 s | 4 (1 seeded XLE option); scope `APPLICATION`/`XLE`/search | **in** (Part 1) |
| Manage Tax Profile Options | 28 s | 4 (0 rows; REST shows 9 seeded ZX options, the export leaves seeded ones out); scope `APPLICATION`/`ZX`/search | **in** (Part 1) |
| Manage Application Toolkit Administrator Profile Values | 42 s | 4 (3 ATK options, 2 values); scope `APPLICATION`/`ATK`/search | **in** (Part 1): value only on our own new ATK option |
| Manage Applications Core Attachment Entities | 42 s | 3 (0 rows); scope `APPLICATION`/`FND` | **in** (Part 1) |
| Manage Transaction Fiscal Classifications | 143 s | 73 (`ORA_ZX_TRANSACTION_CODE` 252 codes under `TRX_BUSINESS_CATEGORY`) | **in** (Part 2) |
| Manage Transaction-Based Fiscal Classifications | 124 s | 73, same files as above (`ORA_USER_DEFINED_CLASSIFICATION_CODE` 55 codes) | **in** (Part 2) |
| Manage Product-Based Fiscal Classifications | about 150 s | 73, same package (`ORA_ZX_PRODUCT_CLASS_CODE` 10 codes) | **in** (Part 2) |
| Manage Resource Note Type Mapping | 40 s | 3 (`ORA_OBJECT_LOOKUP` 18 objects, `ZMM_OBJECT_LOOKUP_MAPPING` 0) | **in** (Part 2) |
| Manage Party Tax Profiles | about 150 s | 87 (`ZX_TAX_AUTHORITY_PROFILE` 3 rows, `ZX_CUSTOMER_TAX_PROFILE` 0, ...) | **in** (Part 3, medium) |
| Manage Tax Exceptions | 41 s | 2 (`ZX_TAX_EXCEPTION`, 0 rows) | **in** (Part 3, medium) |
| Manage Location of Final Discharge | 28 s | 3 (`ORA_LOCATION_OF_FINAL_DISCHARGE` 113 columns, `ORA_ZX_LOCATION_OF_FINAL_DISCHARGE` 5 columns, 0 rows) | **in** (Part 3, medium: rows in full) |
| Manage Tax Exemptions | 74 s | 8 (`ZX_TAX_EXEMPTION` 86 columns, 0 rows) | **in** (Part 3, medium) |
| Manage Search Profile Options | 28 s | 4, scope = 2 named seeded options, mode `edit` | out: only edits seeded options that every user has |
| Manage Common CRM Business Unit Profile Options | 27 s | 4, scope = 1 named seeded option (`HZ_ENABLE_MULTIPLE_BU_CRM`) | out: same reason |
| Manage Tax Registrations | 62 s | 8, same package as exemptions; only legal reporting unit registrations | out: changes an existing legal reporting unit (shared) |
| Map Reports to Work Areas | 41 s | 3 (11 mappings, 13 reports) | out: a mapping shows a report in a work area to every user |

Not tried, out on sight (from the gap index notes): tree labels and account hierarchy labels (need a data source GUID, batch 3), cross-validation rules (no rule file), daily rates (rates not in the package), data access sets and data access for users (Security), the "change existing" legal entity, tax option, country default and set-assignment tasks, document sequence assignments, descriptive flexfields (deploy), ESS, help and telephony tasks, country-only tasks, and all "neither" (no CSV) tasks.

**Easy ran out after 8.** Parts 1 and 2 are easy (new stand-alone rows, pattern known). **Part 3 is medium**: each needs a prerequisite record or rows written in full.

## 2. The 12 tasks

### Part 1 (4 tasks, easy): new profile options in other applications, and attachment entities (P3 profile options)
Application and module ids are read **live by REST** (`profileOptions` filtered by `ApplicationShortName`, or the seeded `YES_NO` lookup), never from an export.

| # | Task code | Name | Route | Pattern | depends_on | Why easy |
|---|---|---|---|---|---|---|
| 1 | `XLE_MANAGE_LEGAL_ENITTY_PROFILE_OPTIONS` | Manage Legal Entity Configurator Profile Options | FSM CSV (`FND_APP_PROFILE_OPTION` + levels); read back REST `profileOptions` + export compare | P3, card over `manage-profile-options` with the XLE application id and module id | none | a new user-defined option that no code reads |
| 2 | `ORA_ZX_MANAGE_TAX_PROFILE_OPTIONS` | Manage Tax Profile Options | same, ZX application | P3, same card shape | none | same; no tax setting changes |
| 3 | `ORA_ATK_ADMIN_PROFILE_OPTION_VALUES` | Manage Application Toolkit Administrator Profile Values | FSM CSV: own ATK option + levels + SITE value in one package; REST `siteProfileOptionValues` + export compare | P3, option + value (batch 2 admin values card) | none outside the task (prerequisite = own option, made as Step 1 of the same import) | the value is set only on our own new option; seeded ATK values untouched |
| 4 | `FND_MANAGE_APPLICATIONS_CORE_ATTACHMENT_ENTITIES` | Manage Applications Core Attachment Entities | FSM CSV (`FND_APP_ATTACHMENT_ENTITY`); read back by export compare (no REST resource) | P4, row written in full (the scoped export is empty) | none (categories link optional, not done) | a new entity no category points to, so no screen shows it |

### Part 2 (4 tasks, easy): classification codes and a note type mapping
| # | Task code | Name | Route | Pattern | depends_on | Why easy |
|---|---|---|---|---|---|---|
| 5 | `ZX_MANAGE_TRANSACTION_FISCAL_CLASSIFICATIONS` | Manage Transaction Fiscal Classifications | FSM CSV (`ORA_ZX_TRANSACTION_CODE` + translation + denorm rows; ~70 other files header only); export compare | P9, template row (as batch 3 party fiscal classifications) | none | a new level-1 code under the seeded transaction business category type; no rule uses it |
| 6 | `ORA_ZX_MANAGE_TRANSACTION_BASED_FISCAL_CLASSIFICATIONS` | Manage Transaction-Based Fiscal Classifications | same package (`ORA_USER_DEFINED_CLASSIFICATION_CODE` + translation + denorm) | P9, template row | none | a new user-defined code; nothing uses it. Check first which file the task really owns (task 5 vs 6) |
| 7 | `ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS` | Manage Product-Based Fiscal Classifications | same package (`ORA_ZX_PRODUCT_CLASS_CODE` + translation + denorm) | P9, template row | none | a new product category code; no item or rule uses it |
| 8 | `HZ_MANAGE_RESOURCE_NOTE_TYPE_MAPPING` | Manage Resource Note Type Mapping | FSM CSV (`ZMM_OBJECT_LOOKUP_MAPPING`, parent `ORA_OBJECT_LOOKUP` copied unchanged); export compare | P12, child row + `copy_parent_rows.py` | `HZ_MANAGE_RESOURCE_NOTE_TYPE` (a `GAPFILL_` note type made with that skill) | maps our own note type to one object; if the object is shared, pick a test or soak custom object, else stop |

### Part 3 (4 tasks, medium): tax content on test records
| # | Task code | Name | Route | Pattern | depends_on | Why medium |
|---|---|---|---|---|---|---|
| 9 | `ORA_ZX_MANAGE_PARTY_TAX_PROFILES` | Manage Party Tax Profiles | FSM CSV (`ZX_TAX_AUTHORITY_PROFILE`, ~86 other files header only); export compare | P9/P10, template row | `XLE_MANAGE_LEGAL_AUTHORITIES` (a `GAPFILL_` legal authority party; batch 3 made `GAPFILL_AB_P3_LA1`) | large package; profile only on our own test authority party |
| 10 | `ZX_MANAGE_TAX_EXCEPTIONS` | Manage Tax Exceptions | FSM CSV (`ZX_TAX_EXCEPTION`, rows in full); export compare | P9, rows in full | `ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES` (test rate on the test tax, regime GCO row from `ZX_MANAGE_TAX_REGIMES` Step 7), `ORA_ZX_MANAGE_PRODUCT_BASED_FISCAL_CLASSIFICATIONS` (#7's code) | no template row; needs the tax chain |
| 11 | `ORA_ZX_MANAGE_LOCATION_FINAL_DISCHARGE` | Manage Location of Final Discharge | FSM CSV (HZ location file + ZX file, rows in full); export compare | P10, rows in full | none | no template row; address by names (country), no IDs |
| 12 | `ORA_ZX_MANAGE_TAX_EXEMPTIONS` | Manage Tax Exemptions | FSM CSV (`ZX_TAX_EXEMPTION`, rows in full); export compare | P9, rows in full | `ORA_ZX_MANAGE_PARTY_TAX_PROFILES` (#9, a test party profile), `ZX_MANAGE_TAX_RATES_AND_TAX_RECOVERY_RATES` | needs a party profile and the tax chain; check which party types the file accepts |

**Order:** Part 1 has no outside dependency (3's option is Step 1 of its own package). Part 2 does not depend on Part 1; #8 needs a batch 1 note type. Part 3 after Part 2 (#10 needs #7); inside Part 3: 9 before 12; 10 and 11 any time.

**Records from earlier batches that are needed:** `GAPFILL_AB_P3_LA1` (legal authority, #9), the batch taxfix rate `GAPFILL_AB_TF_RT1` with its tax and status (#10, #12), a batch 1 resource note type (#8). None is changed; a child package may carry the parent row unchanged.

## 3. Expected time (from batches 1 to 3)
| Kind | Working | Oracle waiting | Fresh test |
|---|---:|---:|---:|
| card on a known package (#1, #2, #3) | 2 to 5 | 2 to 3 | 3 to 5 |
| first skill of a package / template row (#4 to #9) | 5 to 11 | 3 to 6 | 4 to 8 |
| rows in full with a prerequisite (#10 to #12) | 10 to 25 | 5 to 10 | 6 to 10 |

Plan a second sign-in after about 50 minutes.

## 4. RULES (every part)

```text
RULES
1. Skills must be generic and work in any Fusion environment; never specific to ETIA-TEST data, names or IDs. ETIA-TEST is only for verifying.
2. Test records are named GAPFILL_AB_P<part number>_<name> (for example GAPFILL_AB_P2_TFC1), so chats running at the same time never see each other's records, and each fresh test compares only its own record.
3. No deletes.
4. Sign-in on port 8765; never print tokens or secret values.
5. Per task: export the task read-only, write SKILL.md, load a test record, read it back, then a fresh sub-agent tests using only the task name + SKILL.md.
6. A gap counts as filled only when tested.
7. If you change any wording after the fresh test, run the fresh test again; never leave retest_after_wording_fix pending.
8. Evidence screenshots (what was missing, how it was found, the skill, the test result) go in gaps-filled\evidence\batch-04\<task code>\.
9. STATUS.md keys in this order: task_code, task_name, module, status (tested|written|failed), filled_by, date, minutes_to_write, minutes_to_test, waiting_minutes, fresh_claude_pass, route, depends_on, test_records, notes.
10. Log working minutes separately from minutes waiting for approvals, sign-in or Oracle.
11. Do not touch other parts' tasks.
12. At the end run python rebuild_index.py in gaps-filled and check there are no problems; write BATCH4_PART<n>_RESULT.md.
13. If the Oracle connection drops, retry the export (read-only, new folder, one at a time, up to 3 tries). Before any re-import, check whether the record already exists (REST or a new export); never import twice.
14. Text types may have a minimum length (for example a TEXT reporting type needs MinLength); read the error and set it.
15. Names may have maximum lengths (for example 15 characters for withholding tax calendar names). Find the limit in the live test and count the fresh tester's likely name (PREFIX + about 4 characters) against it; give the builder --max-len.
16. Never tell a skill to take IDs from an export (internal numbers, GUIDs). Use codes and names, or read the id live by REST in the skill; if a row can only be built with an internal ID copied from an export, the task is not easy: drop it or mark it failed.
17. Profile-style (hierarchical) imports need the parent row in the file: copy it unchanged with common-features\manage-profile-options\scripts\copy_parent_rows.py (only your own GAPFILL_ parents; give the PARENT's own prefix).
18. Keep the FSCR ProcessId printed by every import in the run log: it is the only key to the full process log (ESS request numbers do not open it).

NEW IN BATCH 4
19. Names: test records are GAPFILL_AB_P<part number>_<name>. Fresh tests add F, re-tests add R (for example GAPFILL_AB_P1_XPO2F).
20. Generic database error at the insert (JBO-26041 or similar, often after "1 rows processed, 0 failed" at validation): first fill the audit columns CreatedBy and LastUpdatedBy with the export metadata's SubmittedBy value, read at run time (never hard-code a user name in a skill; never print it). Then do a round trip: take a working record from a read-only export and re-import it unchanged under a new GAPFILL code, to prove whether the CSV path works for this object.
21. Prerequisites: if a task needs a prerequisite row or setup (for example the tax regime's configuration owner row, or a parent record), write it in SKILL.md as a numbered step and in depends_on, and have FSCR and Claude create it through CSV or REST, never by hand on a screen.
22. Never mark a task "parked". After 3 failed tries: do the round trip (rule 20) and a column-by-column comparison of your row with a working record. Write "failed" only with a proven cause and the exact next step.
23. Work folders live OUTSIDE the repo (E:\GoSaaS\gw\<batch-part> or Claude's scratchpad), because exports hold user names. Evidence images and logs must never show user names, tokens or server addresses.
24. After every wording change to a SKILL.md, run the fresh test again (rule 7).
25. The usual: skills generic, ETIA-TEST only, no deletes, never import twice after a dropped connection (check first whether the record exists), fresh sub-agent given only the task name + SKILL.md path, STATUS.md key order (rule 9), working vs waiting minutes, evidence in gaps-filled\evidence\batch-04\<task code>\.
26. Fresh tests that share an FSM package AND an export scope run one after the other, not in parallel (tasks 5 to 7 share the fiscal classification package and scope; tasks 9 and 12 may share party files). Tasks 1 to 3 use the same files but disjoint scopes (XLE, ZX, ATK), so their exports never see each other's rows and they may run in parallel.
```

## 5. Where things go
- Skills: `gaps-filled\common-features\<task-folder>\` (`SKILL.md`, `STATUS.md`, `CHANGELOG.md`, `scripts\` when needed). Task folders: `manage-le-profile-options`, `manage-tax-profile-options`, `manage-atk-admin-profile-values`, `manage-attachment-entities`, `manage-transaction-fiscal-classifications`, `manage-transaction-based-fiscal-classifications`, `manage-product-fiscal-classifications`, `manage-resource-note-type-mapping`, `manage-party-tax-profiles`, `manage-tax-exceptions`, `manage-location-final-discharge`, `manage-tax-exemptions`.
- Evidence: `gaps-filled\evidence\batch-04\<TASK_CODE>\`.
- Work files: `E:\GoSaaS\gw\b4p<n>\` (outside the repo). Never inside `gaps-filled`.
