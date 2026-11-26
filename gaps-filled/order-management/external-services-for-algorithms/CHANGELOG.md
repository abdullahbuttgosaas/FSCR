# CHANGELOG - Manage External Service Details for Algorithms (ORA_QP_MANAGE_EXT_SERVICES_FOR_ALGORITHMS)

## 2026-11-26 (sitting 1, batch 02)
- Skill written from the live export and Oracle errors; own test: Empty export (rows written in full). Try 1 refused (ProcessId 100004743456587): JBO-27014 TargetSystemId required. Try 2 refused (100004744433377): JBO-25072 LOV_OrigSystemName no match for code OPS. Try 3 with the system name loaded (100004744434324, 1 row, 0 failed); export before 100004744422916, after 100004744433467: 1 new row, 0 existing changed; REST GET returned it. The CSV has no URL/credential columns.
- Fresh test F: FSCRT_AK_GF_WSF: export 100004744435248, systems export 100004744434687, import 100004744436265, after-export 100004743457015: 1 new row, 0 changed; REST OK. PASS, no wrong sentence.
- Tester F suggestions (not applied): the "export can be empty" note no longer holds once test rows exist; REST shows InvocationMode as meaning but ResponseProcessPartialMode as code; mention the .txt next to the ZIP.
