task_code: ORA_OKC_MANAGE_CONTRACT_TERMS_DESCRIPTIVE_FLEXFIELDS
task_name: Manage Contract Terms Descriptive Flexfields
module: Procurement
status: tested
filled_by: AB
date: 2026-11-27
minutes_to_write: 5
minutes_to_test: 6
waiting_minutes: 4
fresh_claude_pass: yes (GAPFILL_AB_B7_CCX2F + CSG2F, ProcessId 100004743464090, compare PASS, no wrong sentence)
route: FSM CSV (flexfield package, module OKC); parent row by REST descriptiveFlexfields when the export is empty; builders from common-features/manage-applcore-dffs
depends_on: none (flexfield OKC_ARTICLES_DESCFLEX is seeded)
test_records: own context GAPFILL_AB_B7_CCX1 (disabled) + segment GAPFILL_AB_B7_CSG1 on ATTRIBUTE11 (ProcessId 100004743464073); fresh GAPFILL_AB_B7_CCX2F + GAPFILL_AB_B7_CSG2F on ATTRIBUTE12 (100004743464090)
notes: Batch 07 (sitting 4). Re-opened from written (unsafe): the 2026-11-25 reason ('needs a shared flexfield deployment') was wrong. A DISABLED context loads with no deployment and the flexfield stays DEPLOYED (same as the 3 tested Common Features DFF tasks). Before: export 13 CSVs all 0 rows (Case A), parent read by REST (ProtectedFlag N). After own load: check_dff_rows PASS (only the 2 own rows touched, parent changed 0), EnabledFlag N, DEPLOYED before and after. Fresh (Case B) compare PASS. Suggestions NOT applied: mark ATTRIBUTE12 VERIFIED by name; say Case B prints no parent-source line; list the ZIP rows before import; add the fresh run to the worked example. Where it shows: Manage Contract Terms Descriptive Flexfields > Clause flexfield > contexts (disabled).
