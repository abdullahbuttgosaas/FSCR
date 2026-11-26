# CHANGELOG: Manage Planning Profile Options

Task code: ORA_MSC_MANAGE_PLANNING_PROFILE_OPTIONS · filled by IR · 24/11/2026 · route FSM CSV

## Test records and ProcessIds

| Record | Who | Import ProcessId | Result |
|---|---|---|---|
| FSCRT_IR_GF_PO1 | own live test | 100004742419023 | read back (1 option + 3 levels + 1 value added, 0 changed) |
| FSCRT_IR_GF_POF | fresh test 1 | 100004742421074 | PASS, read back |
| FSCRT_IR_GF_POR | fresh retest after wording fix 1 | 100004742423051 | PASS, read back |
| FSCRT_IR_GF_POR2 | fresh retest after wording fix 2 | 100004742422229 | PASS, read back |
| FSCRT_IR_GF_POR3 | fresh retest after wording fix 3 | 100004742419116 | PASS, read back |
| FSCRT_IR_GF_POR4 | fresh retest after wording fix 4 | 100004742422357 | PASS, read back; no errors reported |

Earlier, in the module test (18/11/2026): FSCRT_IR_PLAN_TEST through FSCR's Data Loader, requests 4467369 / FSM 4467371.

## Fixes

0. Before any test: "all rows share one ApplicationId/ModuleId pair" was wrong (two ModuleId values); now "take the
   most-used ModuleId".
1. After fresh test 1 (errors): "the import log counts only the top object" was wrong (the log says 5 rows processed);
   stated row counts drifted (removed); `StatusCode: (unknown)` not explained. Added `<PREFIX>`, compare script and an
   after-export command.
2. After retest R (error): the export prints an environment-named file name. All FSCR script output now goes to
   `<RUN>/logs`; added `scripts/inspect_export.py` (counts exclude earlier FSCRT_ test rows).
3. After retest R2 (misleading sentence): `<RUN>` said "the scripts create it", but the logs folder must exist first.
   Fixed; added the expected count of `Completed successfully`, a clean-up command, and a 401/403 check.
4. After retest R3, carried over from the attachment-categories R2 failure: the import grep could not show failures;
   now `scripts/import_result.py` with a "what to do on ERRORS" step. The example column said "use it unless told
   otherwise" for values with other initials and a fixed date; now "format only". Read-back export now checks the ZIP
   was written. `compare_exports.py` no longer prints PASS when nothing was added.

## Tester notes left as suggestions (not applied; they would need another retest and are not errors)

- Give a count-only way to list the import folder (the "2 files" wording was dropped instead).
- Say that a `1 x In progress` line from `import_result.py` is normal on success.
- Give a way to tell whose `python.exe` is running (match the run folder in the command line).
- Say what to do if two ModuleId counts tie.
- Say that the Export step's `mkdir -p` creates `<RUN>`; say "if `export written` does not print, run the 401/403 grep".
