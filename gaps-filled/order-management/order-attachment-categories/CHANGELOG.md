# CHANGELOG - Manage Order Attachment Categories (DOO_MANAGE_ORCHESTRATION_ATTACHMENT_CATEGORIES)

## 2026-11-26 (sitting 1, batch 02)
- Skill written from the live export and Oracle errors; own test: Empty export (rows written in full). Try 1 refused (ProcessId 100004744436010): JBO-27014 UserName (category display name) required. Try 2 loaded (100004744435085) but the category had no ModuleId, so it is not in the DOO-scoped export (FSCRT_AK_GF_AC1 exists outside the module). Try 3 FSCRT_AK_GF_AC2 with ModuleId read live by REST: import 100004744435115 (2 rows, 0 failed); export before 100004744432568, after 100004744434550: 2 new rows, 0 existing changed.
- Fresh test F: FSCRT_AK_GF_ACF: export 100004743456843, import 100004744433698, after-export 100004744433765: 2 new rows, 0 changed. PASS, no wrong sentence.
- Tester F suggestions (not applied): example value for <NAME>; before-export may already hold test rows; one-line ModuleId extraction.
