# CHANGELOG: Manage Shipping Cost Types

## 26/11/2026 (sitting 1, batch 01)
- Read-only export: WSH_SHIPMENT_CHARGE_TYPE.csv (empty before; rows written in full); 0 rows before.
- Try 1 ProcessId 100004744432773: JBO-27014 Attribute Amount is required; row refused, nothing created. Fix: Amount 10 (and ObjectVersionNumber 1).
- Own test record FSCRT_HF_GF_SCT1: ProcessId 100004743455953, completed with 0 failed objects; after-export 1 rows, only FSCRT_HF_GF_SCT1 added, existing changed 0.
- Skill written (VERIFIED parts from the live test).
- Fresh test F (FSCRT_HF_GF_SCT1F, ProcessId 100004744433483): PASS. Reported unclear wording, fixed: what to do when a sign-in is cached; the process log is one line with literal \r\n and names the environment and submitter (new helper check_import_log.py); export/import file names start with the environment name; how to find the export zip; what "no row" looks like with --grep; ProcessId vs Request ID; --token-cache auto on the REST command; counts in the worked example change over time; compare script now lists only codes.
- Fresh test R (FSCRT_HF_GF_SCT1R, ProcessId 100004744435209): PASS. Reported: a garbled sentence (the \r\n escape rendered as a line break); "only" before the CSV name although the package also holds ASM_SETUP_CSV_METADATA.xml; --grep matches part of a name; which process log file to use. All fixed.
- Fresh test R2 (FSCRT_HF_GF_SCT2R, ProcessId 100004744435268): PASS, no wrong sentence reported.
- Batch 02 wording fix applied here too (privacy note: scripts print "Wrote <path>" lines with the environment name). Fresh test R3 (FSCRT_HF_GF_SCT3R, ProcessId 100004743458601): PASS, no wrong sentence reported.
- Tester suggestions not applied (not errors): the "0 rows before" note is historical; --grep with no match prints only header and count.
