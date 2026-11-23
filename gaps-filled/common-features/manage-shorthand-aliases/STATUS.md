task_code: ORA_GL_MANAGE_SHORTHAND_ALIASES
task_name: Manage Shorthand Aliases
module: Common Features
status: tested
filled_by: AB
date: 2026-11-24
minutes_to_write: 5
minutes_to_test: 3
waiting_minutes: 9
fresh_claude_pass: yes
route: FSM CSV
depends_on: none
test_records: GAPFILL_AB_P3_SA1 (live), GAPFILL_AB_P3_SA2F (fresh test); both disabled (EnabledFlag=N), on an existing COA instance, same segments as the template alias
notes: Batch 3 part 3. Template row from an existing alias on the same COA instance; ShorthandAliasCode given without the internal number prefix screen aliases carry, and Oracle stored it as given. No REST searched; export compare is the proof. Fresh test PASS, no deviation; notes not applied. Oracle waiting shared with the other two Part 3 tasks (run in parallel).
