---
skill_id: "gosaas.gap-fills.common-features.manage-geography-lookups"
name: "Manage Geography Lookups (GoSaaS gap fill, card)"
description: "Task card: create a new standard lookup type with codes in the geography lookups module through the setup-task CSV import of HZ_MANAGE_GEOGRAPHY_LOOKUPS, reusing the manage-standard-lookups recipe, and verify by REST (the export has no rows). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 1, 2026-11-20. NOT official FSCR."
task_code: "HZ_MANAGE_GEOGRAPHY_LOOKUPS"
task_name: "Manage Geography Lookups"
offering: "Common Features"
type: "import"
owner_team: "GoSaaS"
version: "0.1.0"
reuses: "common-features/manage-standard-lookups (SKILL.md and scripts)"
depends_on:
  - "core.auth.fusion-oauth-authentication"
  - "core.fusion-api.apps-common.lookups"
  - "shared.setup-export.task-level-export"
  - "shared.setup-import.task-level-import"
side_effects:
  - "One setup-task CSV import that creates one new lookup type and its codes in the geography module. May not be deletable."
---

# Manage Geography Lookups (GoSaaS gap fill, card)

> **Added by GoSaaS, not part of official FSCR.** This is a short card. The full recipe, scripts, rules and placeholders are in `..\manage-standard-lookups\SKILL.md` (call that folder `STD`). Follow it step by step and apply only the differences below.
> `<STD>` in commands = the full path of the folder `manage-standard-lookups` next to this card's folder. Do all STD steps (0 sign-in check, 2 export **and unzip to `<RUN>/export_before/unz`**, 3 before-read, 4 build, 5 import, 6A read-back); this card only changes what the tables below say.
> Labels as in STD: **VERIFIED** (live test 2026-11-20), **GUESS**.

## What differs from the standard lookups recipe
| STD step | For this task |
|---|---|
| All FSCR export/import commands | `--task-code HZ_MANAGE_GEOGRAPHY_LOOKUPS`; import also `--task-name "Manage Geography Lookups"` |
| Step 2 export | Expect the same 3 files with **0 data rows** (header only). VERIFIED. The export is still needed: its metadata XML goes into the package. |
| Step 2 scope | The metadata XML scope is a fixed list of seeded geography lookup types (`ScopeValueBoAttributeId` = `lookupType`, values such as `HZ_GEOGRAPHY_USAGE`, `HZ_GEO_DATA_PROVIDER`), mode `edit`. VERIFIED |
| Step 4 ModuleId | The export has no rows, so the builder cannot copy a ModuleId. Read it by REST from one seeded type named in that scope, then pass it: |

```bash
# list the scope lookup types (read-only, offline)
python -I -c "import re,sys; print(sorted(set(re.findall(r'<ScopeValueBoAttributeValue>([A-Z0-9_]+)<', open(sys.argv[1],encoding='utf-8').read())) - {'edit','search'}))" "<RUN>/export_before/unz/ASM_SETUP_CSV_METADATA.xml"
# read the ModuleId of one of them (FSCR generic lookups REST read)
python -B "<STD>/scripts/read_lookup.py" --fscr "<FSCR>" --module-of <one scope type>
# build with that value
python -I "<STD>/scripts/build_lookup_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --prefix <PREFIX> --module-id <ModuleId printed above> \
  --type "<TYPE>|<meaning>|<description>" --code "<CODE1>|<meaning 1>|<description 1>" --zip-name geo_lookup_new.zip
```
VERIFIED: three seeded scope types returned the same ModuleId; the new type was created with it.

| STD step | For this task |
|---|---|
| Step 5 import | Success line is the same: `Business object: Application Standard Lookup ... A total of N rows were processed. 0 rows of them failed` (N = 1 + codes). VERIFIED (2 rows, about 25 s) |
| Step 6A REST read | **This is the check.** Same `read_lookup.py` command; want `READBACK: PASS`. VERIFIED |
| Step 6B export compare | **Skip.** The task export holds no rows (GUESS: it lists only the scoped seeded types, so a new type will not appear in it either). |

## Rules specific to this task
1. **Do not add codes to the seeded geography types** (`HZ_GEO_...`, `HZ_GEOGRAPHY_USAGE`) in a test: the import would have to carry the seeded parent row, and the codes would show to every user of geography setup. This card creates a new test type in the same module instead. Adding codes to a seeded type is a real use of this task but is **not tested** here (GUESS: same package, type row copied unchanged from a REST read, code rows added).
2. Everything else: STD Rules and limits.

## Worked example (VERIFIED, 2026-11-20). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 3 files, 0 rows; 25 s |
| ModuleId | read from `HZ_GEOGRAPHY_USAGE` by REST |
| Before-read | `GAPFILL_GEO_T2`: HTTP 404, PASS |
| New records | type `GAPFILL_GEO_T2` "GAPFILL GEO T2 Lookup"; code `GAPFILL_GEO_A` "GAPFILL GEO T2 Alpha" |
| Import | 1 attempt, 24 s: 2 rows processed, 0 failed |
| REST read-back | found, ModuleId = geography module, 1 code: PASS |
