---
skill_id: "gosaas.gap-fills.common-features.manage-le-configurator-lookups"
name: "Manage Legal Entity Configurator Lookups (GoSaaS gap fill, card)"
description: "Task card: create a new standard-view lookup type with codes in the legal entity configurator module through the setup-task CSV import of XLE_MANAGE_APPLICATION_LOOKUP (Financials generic lookup package), reusing the manage-tax-lookup-codes recipe, and verify by REST (the export has no rows and does not show the new type). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 2, 2026-11-20. NOT official FSCR."
task_code: "XLE_MANAGE_APPLICATION_LOOKUP"
task_name: "Manage Legal Entity Configurator Lookups"
offering: "Common Features"
type: "import"
owner_team: "GoSaaS"
version: "0.1.0"
reuses: "common-features/manage-tax-lookup-codes (SKILL.md and scripts)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.apps-common.lookups"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "One setup-task CSV import that creates one new lookup type and its codes in the legal entity configurator module. May not be deletable."
---

# Manage Legal Entity Configurator Lookups (GoSaaS gap fill, card)

> **Added by GoSaaS, not part of official FSCR.** This is a short card. The full recipe, scripts, rules and placeholders are in `..\manage-tax-lookup-codes\SKILL.md` (call that folder `TAX`). Follow it step by step and apply only the differences below.
> `<TAX>` in commands = the full path of the folder `manage-tax-lookup-codes` next to this card's folder (its scripts are in `<TAX>/scripts`). `<FSCR>`, `<RUN>`, `<TYPE>` and the other placeholders are defined in TAX "Placeholders used below" (FSCR = the folder that directly holds `core\`, `shared\`, `pillars\`).
> **Order:** TAX Step 0 (incl. the Git Bash traps) -> Step 2 export **and unzip to `<RUN>/export_before/unz`** -> **this card's scope read** -> **this card's Step 3a (ModuleId; replaces TAX 3a)** -> TAX 3b -> Step 4 with this card's arguments -> 5 (approval rule applies) -> 6 -> 7A. This card changes only what the tables below say.
> Labels as in TAX: **VERIFIED** (live test 2026-11-20), **GUESS**.

## What differs from the tax lookup recipe
| TAX step | For this task |
|---|---|
| All FSCR export/import commands | `--task-code XLE_MANAGE_APPLICATION_LOOKUP`; import also `--task-name "Manage Legal Entity Configurator Lookups"`; zip name e.g. `le_lookup_new.zip` |
| Step 2 export | Same 5 files, **0 data rows** (headers only). VERIFIED. Still needed: its metadata XML goes into the package. |
| Step 2 scope | Metadata XML scope: `moduleType` = `APPLICATION`, `moduleKey` = the legal entity application key, `mode` = `search`. VERIFIED. Read the two values (you need them in Step 4): |

```bash
python -I -c "import re,sys; t=open(sys.argv[1],encoding='utf-8').read(); print(dict(re.findall(r'<ScopeValueBoAttributeId>(\w+)</ScopeValueBoAttributeId>\s*<ScopeValueBoAttributeValue>([^<]*)<', t)))" "<RUN>/export_before/unz/ASM_SETUP_CSV_METADATA.xml"
```

| TAX step | For this task |
|---|---|
| View | **standard** (`--view standard`, no reference group). VERIFIED: the seeded legal entity lookup types are found under `standardLookups`, none under `setEnabledLookups`. |
| Step 3a (replaced, do not skip) | No reference group. Instead get the **ModuleId** (the export has no rows to copy it from). List the seeded types whose name starts with the moduleKey, then read one: |

```bash
export MSYS_NO_PATHCONV=1   # Git Bash only
cd "<FSCR>"; python -B core/fusion-api/rest-api-client/scripts/fusion_rest_client.py /fscmRestApi/resources/11.13.18.05/standardLookups \
  --query "q=LookupType LIKE '<moduleKey>%'" --query onlyData=true --query limit=50 --query fields=LookupType,ModuleId \
  --no-open-browser --output "<RUN>/le_types.json"
python -B "<TAX>/scripts/read_generic_lookup.py" --fscr "<FSCR>" --info-of <one LookupType from le_types.json>
```
VERIFIED: all 15 seeded types listed shared one ModuleId (different from the tax module's). Use the `ModuleId=` value it prints. Do not copy a ModuleId from another task or environment.

| TAX step | For this task |
|---|---|
| Step 4 build | add `--view standard --module-id <ModuleId> --module-key <moduleKey> --module-type <moduleType>` (from the two reads above). VERIFIED |
| Step 5/6 import | Same success lines: `LookupTypeGeneric1` and `LookupGeneric1` each `0 rows of them failed`, `Total Objects Failed: 0`. VERIFIED (1 attempt, about 40 s) |
| Step 7A REST read | **This is the check.** `read_generic_lookup.py --view standard --type <TYPE> ... --expect-meaning ... --expect-code ...` (no `--expect-set`). Want `READBACK: PASS`. VERIFIED. Codes show `set -`: standard lookups have no set, although the builder prints `set COMMON` (the package key needs it). To check the module too: `read_generic_lookup.py --fscr <FSCR> --info-of <TYPE>` should print the ModuleId from Step 3a. VERIFIED |
| Step 7B export compare | **Do not rely on it.** VERIFIED: the after export still had 0 rows; the new type and code did not appear in this task's export (the compare prints FAIL for "expected codes not in the after export", with 0 removed and 0 changed). Optional: run it without `--require-codes` only to prove nothing else changed. |

## Rules specific to this task
1. **Do not add codes to the seeded legal entity types** in a test (for example legal entity types, registration codes, contact roles): they feed legal entity and registration screens for all users. This card creates a new test type in the same module. Adding codes to a seeded type is the real use of this task but is **not tested** (GUESS: code rows only, `ViewApplicationId` 0, seeded type not in the type file).
2. Everything else: TAX Rules and limits (new records only, `ChangeSinceLastRefresh=N`, names, records may stay for good).

## Worked example (VERIFIED, 2026-11-20). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 5 files, 0 rows; 41 s |
| ModuleId | read by REST from a seeded legal entity standard lookup type |
| Before-read | `GAPFILL_LE_T2`: HTTP 404 in all three views, PASS |
| New records | standard type `GAPFILL_LE_T2` "GAPFILL LE T2 Lookup"; code `GAPFILL_LE_A` "GAPFILL LE T2 Alpha" |
| Import | 1 attempt: type 1 row, code 1 row, 0 failed |
| REST read-back | found in standardLookups, level U, ModuleId = the seeded types' ModuleId, 1 code: PASS |
| Export after | still 0 rows (new type not in the task export) |
