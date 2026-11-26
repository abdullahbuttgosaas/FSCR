# Manage UN Numbers (PO_MANAGE_UN_NUMBERS): create a UN number by FSM CSV

## What it is and when to use
A UN number identifies a hazardous material for shipping and can point to a hazard class. Use this skill to
create a NEW UN number through FSCR's setup task CSV import. FSCR has no skill for this task.
Route: FSM setup CSV (task `PO_MANAGE_UN_NUMBERS`, CSV supported: Y). VERIFIED.
No REST resource (`unNumbers`, `unNumbersLOV` describe: not found). VERIFIED.

## Placeholders
See `../purchasing-common/COMMON_STEPS.md` (`<RUN>`, `<PREFIX>`, `$S`). Plus:
- `<CODE>`: the new UN number code, `<PREFIX>` + short name, upper case, e.g. `FSCRT_AB_GF_UN1`.
- `<HAZARD_CLASS_CODE>`: an existing hazard class code (optional link).
- `<DESCRIPTION>`: free text.

## Sign-in
As in COMMON_STEPS.md.

## Prerequisites
1. Optional: a hazard class for the link. Check it exists in a read-only export of `PO_MANAGE_HAZARD_CLASSES`
   (`python3 $S/inspect_export.py <zip> --match <HAZARD_CLASS_CODE>` shows the row). If you need a new one, create
   it first with `../hazard-classes/SKILL.md` in its own sub-folder `<RUN>/hc` (your own test class only; never use
   someone else's record for a test). Then run this skill in `<RUN>/un`: from here on, `<RUN>` in COMMON_STEPS and below means `<RUN>/un`. Without a link, leave `HazardClassCode` empty: existing UN numbers without a class load that way. VERIFIED.

## Export
COMMON_STEPS step 1 with `<TASK_CODE>` = `PO_MANAGE_UN_NUMBERS`. Two CSVs: `PO_UN_NUMBER.csv` and
`PO_UN_NUMBER_TRANSLATION.csv` (linked by `PO_UN_NUMBER.UnNumberCode`). VERIFIED.

## Build rows
`<RUN>/rows.json`. VERIFIED:
```json
{"PO_UN_NUMBER.csv": [{"UnNumberCode": "<CODE>", "UnNumber": "<CODE>", "Description": "<DESCRIPTION>",
   "HazardClassCode": "<HAZARD_CLASS_CODE>"}],
 "PO_UN_NUMBER_TRANSLATION.csv": [{"PO_UN_NUMBER.UnNumberCode": "<CODE>", "Language": "US", "SourceLang": "US",
   "UnNumber": "<CODE>", "Description": "<DESCRIPTION>"}]}
```
- `HazardClassCode` is the hazard class CODE (not its name). VERIFIED.
- Leave CreatedBy, LastUpdatedBy, InactiveDate and Attribute* empty. VERIFIED.
Then COMMON_STEPS step 2.

## Import
COMMON_STEPS step 3. Expected log: "Business object: Purchasing UN Number. Status: Completed successfully ... 1 rows
were processed. 0 rows of them failed". VERIFIED.

## Read back
COMMON_STEPS step 4: `PO_UN_NUMBER.csv` and `PO_UN_NUMBER_TRANSLATION.csv` each `added 1 ['<CODE>']`, existing
changed 0. Check the link: `python3 $S/inspect_export.py <RUN>/after/*.zip --match <CODE>` shows
`HazardClassCode` = `<HAZARD_CLASS_CODE>`. VERIFIED.

## Rules and limits
- New codes only (the code is the key).
- A wrong `HazardClassCode`: GUESS that the row is refused; confirm with step 4 before trying again.

## Worked example
`FSCRT_MZ_GF_UN1` linked to hazard class `FSCRT_MZ_GF_HC1`: import ProcessId 100004742441905 (1 processed, 0 failed);
after-export ProcessId 100004742441914: rows 5 -> 6, translations 5 -> 6, existing changed 0. VERIFIED.
