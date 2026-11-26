# CHANGELOG: Manage Supply Orchestration Attachment Categories

Task code: ORA_DOS_MANAGE_SUPPLY_ORCHESTRATION_ATTACHMENT_CATEGORIES · filled by IR · 24/11/2026 · route FSM CSV

## Test records and ProcessIds

| Record | Who | Import ProcessId | Result |
|---|---|---|---|
| FSCRT_IR_GF_AC1 | own live test | 100004742420025 | read back (added 1, changed 0) |
| FSCRT_IR_GF_ACF | fresh test 1 | 100004742420054 | PASS, read back |
| FSCRT_IR_GF_ACR | fresh retest after wording fix 1 | 100004742419063 | PASS, read back |
| FSCRT_IR_GF_ACR2 | fresh retest after wording fix 2 | 100004742419086 | FAIL: FND_CORE_RCRD_VAL, display name already used; 0 rows created (after-export compare: added 0, changed 0) |
| FSCRT_IR_GF_ACR3 | fresh retest after wording fix 3 | 100004742420131 | PASS, read back; 3 errors reported |
| FSCRT_IR_GF_ACR4 | fresh retest after wording fix 4 | 100004742423164 | PASS, read back; 2 errors reported |
| FSCRT_IR_GF_ACR5 | fresh retest after wording fix 5 | 100004742421147 | PASS, read back; no errors reported (final) |

Earlier, in the module test (18/11/2026): FSCRT_IR_ATT_CAT through FSCR's Data Loader, requests 4467368 / FSM 4467372.

## Fixes

1. After fresh test 1 (errors reported): the CHANGELOG reference pointed nowhere; the worked example described the Data
   Loader route, not the import script the skill uses; the export ZIP's name was not explained (it starts with the
   environment name: use a glob); the ProcessId line and the misleading `StatusCode: (unknown)` were not explained.
   Added `<PREFIX>`, a compare script (`scripts/compare_exports.py`) and an after-export command.
2. After retest R (suggestion that was really an error, same as the profile-options tester's error): the scripts print
   environment-named file names. All FSCR script output now goes to `<RUN>/logs`; added `scripts/inspect_export.py`
   to read codes and counts without printing rows.
3. After retest R2 (FAIL): the display name must be unique (Oracle FND_CORE_RCRD_VAL); the example display name made
   every second run fail. Display name is now `<CATEGORY> category` and is checked free before the import. The
   ModuleId cross-check was false (the lookup's ModuleId is not among the predefined categories); removed.
   `compare_exports.py` printed PASS when nothing was added; it now prints FAIL. The import grep could not see
   failures; added `scripts/import_result.py` and a "what to do on ERRORS" step. `<RUN>` must be created first.

4. After retest R3 (PASS, 3 errors): the REST step printed the raw response (now redirected to `<RUN>/logs`, and a
   one-line Python prints only the item count and ModuleId); the 30-character limits conflicted (code is now at most
   21 characters, so code + ` category` fits in 30); the expected `import_result.py` lines did not match the real
   output (now described as seen).
5. After retest R4 (PASS, 2 errors): `MSYS_NO_PATHCONV=1` also stops path conversion, so the REST step's `--output`
   path went to a wrong folder in Git Bash (the tester removed it). The step now redirects stdout instead (VERIFIED with
   a Git Bash path). "Every value you write must contain the prefix" was too broad: `fsm_package.py` needs it in at
   least one value per row and the prefix must start with FSCRT_.

## Tester notes left as suggestions

- Add a note that inline Python in a Git Bash heredoc loses backslashes (only matters if a reader writes their own helper).
- Say `mkdir -p "<RUN>/logs"` once only (it is in the table and in the Export block).
- Add a safe way to see where a script wrote its output when the 401/403 check finds nothing.
- Add a one-line length check for the code and display name.
- Say that the export's row count includes earlier FSCRT_ test rows; give the empty tasklist text; say `<RUN>` must be
  a new, empty folder for each run; say the order of the `rows processed` lines can vary (R5 notes).
