# CHANGELOG - Manage Pricing Results Presentations (ORA_QP_MANAGE_PRICING_RESULTS_PRESENTATIONS)

## 2026-11-26 (sitting 1, batch 02)
- Skill written from the live export; own test: FSCRT_AK_GF_RP1: export 100004743456353, import 100004743455639 (1 row, 0 failed), after-export 100004744432691: 1 new row, 0 existing changed.
- Fresh test F: FSCRT_AK_GF_RPF: export 100004744436170, import 100004744434702, after-export 100004743456951: 1 new row, 0 changed. PASS; tester reported 1 wrong sentence (column list named CreatedBy/LastUpdatedBy, which this export does not have).
- Fix: column list corrected (no CreatedBy/LastUpdatedBy); note that "Pricing Results Presentation Template ... already processed" is normal.
- Re-test R: FSCRT_AK_GF_RPR: export 100004744436316, import 100004744433813, after-export 100004744433890: 1 new row, 0 changed. PASS, no wrong step.
- Suggestions not applied (all testers): mention the .txt file export_task.sh writes next to the ZIP; say the Submitted By value is masked by read_import_log.py.
