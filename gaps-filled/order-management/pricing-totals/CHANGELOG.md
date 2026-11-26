# CHANGELOG - Manage Pricing Totals (ORA_QP_MANAGE_PRICING_TOTALS_DEFINITIONS)

## 2026-11-26 (sitting 1, batch 02)
- Skill written from the live export and Oracle errors; own test: Try 1 FSCRT_AK_GF_TO1 refused (ProcessId 100004744431339): QP_CMN_INVALID_CODE "code in uppercase, up to 30 characters, no spaces". Diagnosis: only difference from working codes is the digit. Try 2 FSCRT_AK_GF_TOA: import 100004744433010 (1 row, 0 failed); export before 100004743455521, after 100004744431379: 1 new row, 0 existing changed; TO1 absent (0 rows).
- Fresh test F: FSCRT_AK_GF_TOF: export 100004744434619, import 100004743456918, after-export 100004744433751: 1 new row, 0 changed. PASS, no wrong sentence.
- Tester F suggestions (not applied): say where the import ProcessId is printed (read_import_log.py prints it); mention the .txt file next to the export ZIP; optional --find check on the after-export.
