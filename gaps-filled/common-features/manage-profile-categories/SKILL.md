---
skill_id: "gosaas.gap-fills.common-features.manage-profile-categories"
name: "Manage Profile Categories (GoSaaS gap fill)"
description: "Create a new profile category with option links for task FND_MANAGE_PROFILE_CATEGORIES. Same FSM package (FND_APP_PROFILE_CATEGORY) as manage-appcore-profile-categories; card over that skill. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 1, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_PROFILE_CATEGORIES"
task_name: "Manage Profile Categories"
dataloader_import_mode: "FSM"
type: "import"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "gosaas common-features/manage-appcore-profile-categories (full recipe)"
  - "a profile option to link (for a test: your own option made with gosaas common-features/manage-profile-options)"
side_effects:
  - "Starts one setup-task CSV import that creates one new profile category and its option links. It may not be deletable; plan as if it stays."
---

# Manage Profile Categories (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** This is a short card. Read and follow `../manage-appcore-profile-categories/SKILL.md` (the "full skill") from start to end; its placeholders, rules and steps apply. Only the differences are written here. Labels: **VERIFIED** (live test 2026-11-23) · **GUESS**.

## When to use
- Someone asks to create a **new** profile category for task `FND_MANAGE_PROFILE_CATEGORIES` ("Manage Profile Categories").
- Same limits as the full skill: new records only, no options added to seeded categories, in a test link only your own option.

- **FSCR:** the same FSCR root as the full skill. If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.

## Differences from the full skill
1. **Task code and name** in the export (Step 2), the export after (Step 6) and the import (Step 5): `--task-code FND_MANAGE_PROFILE_CATEGORIES`, and for the import `--task-name "Manage Profile Categories"`.
2. **Export:** the same 3 files and columns as the full skill (VERIFIED, about 25 to 40 s). Its scope in `ASM_SETUP_CSV_METADATA.xml` has only `mode=search` (no module key), but the content was the same as the Applications Core task (seeded categories plus earlier test categories). VERIFIED
3. **ModuleId:** as in the full skill Step 3: read it from the seeded `YES_NO` lookup, never from the export. VERIFIED: a category made this way appears in this task's after-export.
4. Everything else (build, import success line `ProfileCategorySD.xml ... 2 rows were processed. 0 ... failed`, compare with one `--expect` per added row) is unchanged. VERIFIED
5. **Concurrent runs:** this task shares its package with the full skill's task, so a category imported by someone else between your two exports shows up as an extra added row. Judge it as the full skill's Step 6 says (your `--expect` rows added, removed 0, changed 0).

## Worked example (VERIFIED, 2026-11-23). Do not reuse these names; they now exist.
| Step | Result |
|---|---|
| Export before | 3 categories, 1,575 option links; 27 s |
| New records | category `GAPFILL_AB_PC2` + link to option `GAPFILL_AB_PO1`, sequence 1 |
| Import | 1 attempt, 39 s: 2 rows processed, 0 failed |
| Export after + compare | 4 categories, 1,576 links; added 1 + 1, removed 0, changed 0: PASS |
