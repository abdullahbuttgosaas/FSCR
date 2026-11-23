---
skill_id: "gosaas.gap-fills.common-features.manage-admin-profile-values"
name: "Manage Applications Core Administrator Profile Values (GoSaaS gap fill)"
description: "Set a SITE-level value on your own test profile option through FSCR's setup-task CSV import (same FND_APP_PROFILE_OPTION package as manage-profile-options), then read it back by REST (profileOptions/<name>/child/siteProfileOptionValues). Card over manage-profile-options. Added by GoSaaS, not part of official FSCR."
origin: "GoSaaS gap fill, batch 2 part 1, 2026-11-23. Written and tested live on one test environment. NOT official FSCR."
layer: "pillar"
pillar: "ERP"
offering: "Common Features"
task_code: "FND_MANAGE_APPLICATIONS_CORE_ADMINISTRATOR_PROFILE_VALUES"
task_name: "Manage Applications Core Administrator Profile Values"
dataloader_import_mode: "FSM"
type: "import"
owner_team: "GoSaaS"
version: "0.1.0"
depends_on:
  - "gosaas common-features/manage-profile-options (full recipe, and the test option itself)"
  - "gosaas common-features/manage-profile-options/scripts/copy_parent_rows.py"
  - "gosaas common-features/manage-docseq-categories/scripts (generic helpers)"
side_effects:
  - "Starts one setup-task CSV import that creates a SITE value for one profile option. A site value is effective at once for every user of the environment: use it only on an option that no code reads (your own test option)."
---

# Manage Applications Core Administrator Profile Values (GoSaaS gap fill)

> **Added by GoSaaS, not part of official FSCR.** This is a short card. Read and follow `../manage-profile-options/SKILL.md` (the "full skill"): its placeholders, Step 0 (safe run), Step 1 (sign-in) and Step 5 (log reading) apply unchanged. Only the differences are written here.
> FSCR's own `core/fusion-api/apps-common/profile-options` skill can also set values by REST (POST/PATCH `siteProfileOptionValues`), but it names no task code and needs its own approval gate; this card uses the task's FSM CSV package so the result is the setup-task route. Labels: **VERIFIED** (live test 2026-11-23) · **GUESS**.

## When to use
- Someone asks to set a profile option **value** for task `FND_MANAGE_APPLICATIONS_CORE_ADMINISTRATOR_PROFILE_VALUES`.
- **Test rule:** set values only on **your own test option** (a `PREFIX` option made with the full skill, which no code reads). Setting a value on a seeded or shared option changes the behaviour of the environment for everyone: that is the real business use, but it is **not tested** here and needs the person's explicit approval of option, level and value.
- Only a **new** value (the option has no value yet at that level). Changing an existing value is an update: not covered.

- **FSCR:** the same FSCR root as the full skill. If there are several copies, use the one the person names; copies set up for the same environment share the saved sign-in.

## Extra placeholders
```text
OPTION = existing profile option to set, starting with PREFIX (made with ../manage-profile-options)
VALUE  = the value text, e.g. GAPFILL_<INITIALS>_V1
LEVEL  = SITE (tested). LevelValue for SITE is the word SITE.
SK     = <GAPS>/common-features/manage-profile-options/scripts
```

## Steps (differences from the full skill)
1. **Export** (full skill Step 2: export, unzip to `<RUN>/export_before/unz`, inspect) with `--task-code FND_MANAGE_APPLICATIONS_CORE_ADMINISTRATOR_PROFILE_VALUES`. Same 4 files and scope as the profile options task. VERIFIED. The full skill's Step 3 (module id) is **not** needed here. Check that OPTION is in the export with its SITE level enabled, and note its ApplicationId:
   ```bash
   python -I "<H>/inspect_export.py" "<RUN>/export_before/unz" --file FND_APP_PROFILE_OPTION.csv --cols ProfileOptionName,ApplicationId --where ProfileOptionName=<OPTION>
   python -I "<H>/inspect_export.py" "<RUN>/export_before/unz" --file ORA_FND_APP_PROFILE_OPTION_LEVEL.csv --cols FND_APP_PROFILE_OPTION.ProfileOptionName,LevelName,EnabledFlag --where FND_APP_PROFILE_OPTION.ProfileOptionName=<OPTION>
   ```
   Want one option row, and `SITE | Y` in the level rows. If not, **stop**.
2. **Before-read** (no module id needed):
   ```bash
   timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions/<OPTION>/child/siteProfileOptionValues \
     --fields LevelValue,ProfileOptionValue --out "<RUN>/readback_before.json" --expect-absent
   ```
   Want `0 row(s)`, `READBACK: PASS`. If a value already exists, **stop** (this card only creates).
3. **Build:** the value row, then the parent option row copied **unchanged** from the export (VERIFIED: without the parent row the import says `A total of 0 rows were processed` and creates nothing, because the package is hierarchical):
   ```bash
   python -I "<H>/build_fsm_package.py" --export-dir "<RUN>/export_before/unz" --out-dir "<RUN>/payload" \
     --zip-name profile_value_new.zip --prefix <PREFIX> \
     --key "FND_APP_PROFILE_OPTION.csv=ProfileOptionName,ApplicationId" \
     --key "ORA_FND_APP_PROFILE_OPTION_LEVEL.csv=FND_APP_PROFILE_OPTION.ProfileOptionName,FND_APP_PROFILE_OPTION.ApplicationId,LevelName" \
     --key "FND_APP_PROFILE_VALUE.csv=FND_APP_PROFILE_OPTION.ProfileOptionName,FND_APP_PROFILE_OPTION.ApplicationId,LevelName,LevelValue" \
     --prefix-col "FND_APP_PROFILE_VALUE.csv=FND_APP_PROFILE_OPTION.ProfileOptionName" \
     --row "FND_APP_PROFILE_VALUE.csv|FND_APP_PROFILE_OPTION.ProfileOptionName=<OPTION>|FND_APP_PROFILE_OPTION.ApplicationId=<option's ApplicationId>|LevelName=SITE|LevelValue=SITE|ProfileOptionValue=<VALUE>"
   python -I "<SK>/copy_parent_rows.py" --export-dir "<RUN>/export_before/unz" --payload-dir "<RUN>/payload" \
     --zip-name profile_value_new.zip --file FND_APP_PROFILE_OPTION.csv \
     --where ProfileOptionName=<OPTION> --where ApplicationId=<option's ApplicationId> --prefix <PREFIX>
   ```
   The second command re-zips `profile_value_new.zip`; import that ZIP. It refuses an option that does not start with PREFIX.
4. **Import** (full skill Step 5) with `--task-code FND_MANAGE_APPLICATIONS_CORE_ADMINISTRATOR_PROFILE_VALUES --task-name "Manage Applications Core Administrator Profile Values" --zip-file "<RUN>/payload/profile_value_new.zip"`. Success: `ProfileOptionSD.xml ... A total of 2 rows were processed. 0 rows of them failed`, `Total Objects Failed: 0` (parent + value = 2; the log may also say `Total Objects Processed: 1`, which is normal). The script itself may print `StatusCode: (unknown)`: normal, the log is the result. VERIFIED, about 25 to 40 s. `0 rows were processed` = nothing created (see 3).
5. **Read back** (REST is the proof):
   ```bash
   timeout 120 python -B "<H>/rest_read.py" --fscr "<FSCR>" --resource profileOptions/<OPTION>/child/siteProfileOptionValues \
     --fields LevelValue,ProfileOptionValue --out "<RUN>/readback_after.json" \
     --expect "LevelValue=SITE,ProfileOptionValue=<VALUE>" --expect-count 1
   ```
   `READBACK: PASS` = one site value equal to VALUE. VERIFIED. Always pass `--fields` (the full row holds user names).
   Optional export compare (full skill Step 6B, this task code): expect only `--expect "FND_APP_PROFILE_VALUE.csv=<OPTION>,<appid>,SITE,SITE"`. GUESS: the copied parent row is reported unchanged, or as changed only in its audit columns.

## Rules and limits
1. Only on your own test option; no seeded options (When to use).
2. Create only; never change or remove an existing value. This skill never deletes.
3. Not tested: PRODUCT and USER levels (USER needs the user GUID as LevelValue, see FSCR `references/profile-options.md`), options with SQL validation.
4. Tested on one environment (release 11.13.26.10.0).

## Worked example (VERIFIED, 2026-11-23). Do not reuse; the value now exists.
| Step | Result |
|---|---|
| Option | `GAPFILL_AB_PO1` (made with the full skill), application 0, site level enabled |
| Before-read | 0 site values, PASS |
| Import attempt 1 | value row only: `0 rows were processed`, nothing created |
| Import attempt 2 | value row + unchanged parent row: 2 rows processed, 0 failed, 25 s |
| REST read-back | 1 row, `LevelValue=SITE`, `ProfileOptionValue=GAPFILL_AB_V1`: PASS |
