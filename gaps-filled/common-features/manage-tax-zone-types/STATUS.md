task_code: ZX_MANAGE_TAX_ZONE_TYPES
task_name: Manage Tax Zone Types
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 24
minutes_to_test: 8
waiting_minutes: 14
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_TF2_ZT2 (round trip); GAPFILL_AB_TF2_ZT3 (fixed row); GAPFILL_AB_TF2_ZT4F (fresh test); GAPFILL_AB_TF2_ZT5R (re-test); reference GAPFILL_AB_TF_ZT1 made on the screen by AB. Earlier tries (GAPFILL_AB_ZT1 x3, GAPFILL_AB_TF_ZT1/ZT2, GAPFILL_AB_TF Zone Type 3) were refused and not created.
notes: Failed 6 times in batch 2 and batch taxfix (JBO-26041 on HZ_GEOGRAPHY_TYPES_B). Batch taxfix2 2026-11-24: round trip of the screen-made zone type's own export imported fine (ProcessId 100004741416084), so not an Oracle defect and not access. Byte compare with our builder's row: only CreatedBy and LastUpdatedBy differed (ours empty). Filled with the export's SubmittedBy (new helper scripts/zone_type_rows.py): imported first try (ProcessId 100004742412123), compare PASS. Fresh test PASS (ZT4F, ProcessId 100004742411691); wording fixed (log filter hides user name, dropped-export folder, name style); re-test PASS (ZT5R, ProcessId 100004742412240), no wording change after it. Country limit option (--limit-like) not tested.
