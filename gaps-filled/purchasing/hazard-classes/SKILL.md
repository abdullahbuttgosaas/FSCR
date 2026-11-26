# Manage Hazard Classes (PO_MANAGE_HAZARD_CLASSES): create a hazard class by FSM CSV

## What it is and when to use
A hazard class (for example Explosive, Flammable) classifies hazardous materials on items and purchasing documents.
Use this skill to create a NEW hazard class through FSCR's setup task CSV import. FSCR has no skill for this task.
Route: FSM setup CSV (task `PO_MANAGE_HAZARD_CLASSES`, CSV export/import supported: Y). VERIFIED.
There is no REST resource for hazard classes (`hazardClasses` and `hazardClassesLOV` describe: not found). VERIFIED.

## Placeholders
See `../purchasing-common/COMMON_STEPS.md` (`<RUN>`, `<PREFIX>`, `$S`). Plus:
- `<CODE>`: the new hazard class code, `<PREFIX>` + a short name, upper case, e.g. `FSCRT_AB_GF_HC1`.
- `<DESCRIPTION>`: free text.

## Sign-in
As in COMMON_STEPS.md.

## Prerequisites
1. None. A hazard class is a stand-alone record. VERIFIED.

## Export
COMMON_STEPS step 1 with `<TASK_CODE>` = `PO_MANAGE_HAZARD_CLASSES`. The package has 2 CSVs: `PO_HAZARD_CLASS.csv`
(one row per class) and `PO_HAZARD_CLASS_TRANSLATION.csv` (one row per class and language). VERIFIED.

## Build rows
`<RUN>/rows.json` (both CSVs are needed: the class and its US translation row). VERIFIED:
```json
{"PO_HAZARD_CLASS.csv": [{"HazardClassCode": "<CODE>", "HazardClass": "<CODE>", "Description": "<DESCRIPTION>"}],
 "PO_HAZARD_CLASS_TRANSLATION.csv": [{"PO_HAZARD_CLASS.HazardClassCode": "<CODE>", "HazardClass": "<CODE>",
   "Description": "<DESCRIPTION>", "Language": "US", "SourceLang": "US"}]}
```
- Leave CreatedBy, CreationDate, LastUpdate* empty. VERIFIED (accepted empty).
- `HazardClass` is the displayed name; using the code keeps it unique. Use another language row only if that
  language is installed (GUESS).
Then COMMON_STEPS step 2.

## Import
COMMON_STEPS step 3. Expected log: "Business object: Purchasing Hazard Class. Status: Completed successfully ...
A total of 1 rows were processed. 0 rows of them failed". VERIFIED.

## Read back
COMMON_STEPS step 4. Expected: `PO_HAZARD_CLASS.csv` and `PO_HAZARD_CLASS_TRANSLATION.csv` each `added 1 ['<CODE>']`,
`existing removed or changed 0`. VERIFIED.

## Rules and limits
- New codes only; an existing code in the package would update that class (FSM merges by key). Do not do that.
- InactiveDate empty = active. VERIFIED.
- Length limit of HazardClassCode: not hit at 15 characters (GUESS: the column allows more).
- UN numbers can reference a hazard class: create the class first (see `../un-numbers/SKILL.md`).

## Worked example
Code `FSCRT_MZ_GF_HC1`: import ProcessId 100004743405677 (1 processed, 0 failed); after-export ProcessId
100004743404738: hazard class rows 5 -> 6, translation rows 5 -> 6, existing changed 0. VERIFIED.
