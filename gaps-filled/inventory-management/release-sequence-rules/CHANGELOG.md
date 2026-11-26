# CHANGELOG: Manage Release Sequence Rules

## 26/11/2026 (sitting 1, batch 01)
- Read-only export: WSH_PICK_SEQUENCE_RULE.csv, WSH_PICK_SEQUENCE_RULE_TRANSLATION.csv; 8 rows before.
- Try 1 ProcessId 100004743455865: JBO-26041 at the insert into WSH_PICK_SEQUENCE_RULES_B (ObjectVersionNumber left empty); nothing created (after-export shows only the try-2 row). Fix: ObjectVersionNumber 1, as on every existing row.
- Own test record FSCRT_HF_GF_RSR1: ProcessId 100004744434147, completed with 0 failed objects; after-export 9 rows, only FSCRT_HF_GF_RSR1 added, existing changed 0.
- Skill written (VERIFIED parts from the live test).
- Fresh test F (FSCRT_HF_GF_RSR1F, ProcessId 100004744434457): PASS. Reported unclear wording, fixed: what to do when a sign-in is cached; the process log is one line with literal \r\n and names the environment and submitter (new helper check_import_log.py); export/import file names start with the environment name; how to find the export zip; what "no row" looks like with --grep; ProcessId vs Request ID; --token-cache auto on the REST command; counts in the worked example change over time; compare script now lists only codes.
- Fresh test R (FSCRT_HF_GF_RSR1R, ProcessId 100004744433597): PASS. Reported: a garbled sentence (the \r\n escape rendered as a line break); "only" before the CSV name although the package also holds ASM_SETUP_CSV_METADATA.xml; --grep matches part of a name; which process log file to use. All fixed.
- Fresh test R2 (FSCRT_HF_GF_RSR2R, ProcessId 100004744436226): PASS, no wrong sentence reported.
- Batch 02 wording fix applied here too (privacy note: scripts print "Wrote <path>" lines with the environment name). Fresh test R3 (FSCRT_HF_GF_RSR3R, ProcessId 100004744435524): PASS, no wrong sentence reported.
- Tester suggestions not applied (not errors): placeholder says max 30 while Rules says GUESS 30; inspect_export prints a sample of 3 rows only; ObjectVersionNumber value is not shown by inspect_export.
