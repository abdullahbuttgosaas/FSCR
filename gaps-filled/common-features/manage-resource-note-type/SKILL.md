---
skill_id: "gosaas.gap-fills.common-features.manage-resource-note-type"
name: "Manage Resource Note Type (GoSaaS gap fill, card)"
description: "Task card: create a new note type lookup (type + note type codes) in the note type module through the setup-task CSV import of HZ_MANAGE_RESOURCE_NOTE_TYPE, reusing the manage-standard-lookups recipe, and verify by REST (the export has no rows). New records only. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 1 part 1, 2026-11-20. NOT official FSCR."
task_code: "HZ_MANAGE_RESOURCE_NOTE_TYPE"
task_name: "Manage Resource Note Type"
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
  - "One setup-task CSV import that creates one new lookup type and its codes in the note type module. May not be deletable."
---

# Manage Resource Note Type (GoSaaS gap fill, card)

> **Added by GoSaaS, not part of official FSCR.** Short card. The full recipe, scripts, rules and placeholders are in `..\manage-standard-lookups\SKILL.md` (call that folder `STD`). Follow it step by step with the differences below.
> `<STD>` in commands = the full path of the folder `manage-standard-lookups` next to this card's folder. Do all STD steps (0 sign-in check, 2 export **and unzip to `<RUN>/export_before/unz`**, 3 before-read, 4 build, 5 import, 6A read-back); this card only changes what the tables below say.
> Labels as in STD: **VERIFIED** (live test 2026-11-20), **GUESS**.

## What this setup is
Note types (for example "General", "Call") classify notes written on resources, customers and other objects. In Oracle they are the codes of the seeded standard lookup type `ZMM_NOTE_TYPE`. VERIFIED: the task export's scope names exactly `lookupType = ZMM_NOTE_TYPE`, mode `edit`, and its files are the standard lookup package. Mapping note types to objects is a separate task (`HZ_MANAGE_RESOURCE_NOTE_TYPE_MAPPING`).

## What differs from the standard lookups recipe
| STD step | For this task |
|---|---|
| All FSCR export/import commands | `--task-code HZ_MANAGE_RESOURCE_NOTE_TYPE`; import also `--task-name "Manage Resource Note Type"` |
| Step 2 export | Same 3 files, **0 data rows**. VERIFIED. Still needed for the metadata XML. |
| Step 4 ModuleId | Not in the export. Read it from the seeded note type lookup, then pass it to the builder: |

```bash
python -B "<STD>/scripts/read_lookup.py" --fscr "<FSCR>" --module-of ZMM_NOTE_TYPE
python -I "<STD>/scripts/build_lookup_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
  --prefix <PREFIX> --module-id <ModuleId printed above> \
  --type "<TYPE>|<meaning>|<description>" --code "<NOTE_CODE>|<note type meaning>|<description>" --zip-name note_type_new.zip
```

| STD step | For this task |
|---|---|
| Step 5 import | Same success lines (`Application Standard Lookup ... A total of N rows were processed. 0 rows of them failed`, N = 1 + codes). VERIFIED (2 rows, 22 s) |
| Step 6A REST read | **This is the check.** Same `read_lookup.py` command; want `READBACK: PASS`. VERIFIED |
| Step 6B export compare | **Skip** (export has no rows). |

## Rules specific to this task
1. **Test with a new type, not inside `ZMM_NOTE_TYPE`.** A code added to `ZMM_NOTE_TYPE` becomes a note type for every user and probably cannot be deleted, and the import would have to carry the seeded parent row. The person who owns this skill chose (2026-11-20) to test with a new test type in the same module instead. So the tested part of this card proves the package, module and import route, not a visible new note type.
2. **Real use (adding a note type to `ZMM_NOTE_TYPE`) is not tested.** GUESS: build the package by hand with the `ZMM_NOTE_TYPE` type row copied unchanged from a REST read (Meaning, Description, ModuleId, CustomizationLevel, RestAccessSecured) and only the new code rows; get explicit approval first, because it changes what users see. Or use FSCR's lookups skill (REST `POST .../standardLookups/ZMM_NOTE_TYPE/child/lookupCodes`), also untested here.
3. Everything else: STD Rules and limits.

## Worked example (VERIFIED, 2026-11-20). Do not reuse these names.
| Step | Result |
|---|---|
| Export before | 3 files, 0 rows; scope `ZMM_NOTE_TYPE`; 23 s |
| ModuleId | read from `ZMM_NOTE_TYPE` by REST |
| Before-read | `GAPFILL_NOTE_T3`: HTTP 404, PASS |
| New records | type `GAPFILL_NOTE_T3` "GAPFILL Note Type T3"; code `GAPFILL_NOTE_A` "GAPFILL Note Type T3 A" |
| Import | 1 attempt, 22 s: 2 rows processed, 0 failed |
| REST read-back | found, ModuleId = note type module, 1 code: PASS |
