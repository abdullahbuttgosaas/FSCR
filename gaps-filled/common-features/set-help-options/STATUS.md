task_code: ATK_CONFIGURE_HELP_SETTINGS
task_name: Set Help Options
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 6
minutes_to_test: 4
waiting_minutes: 4
fresh_claude_pass: yes (re-test R after a wording fix)
route: FSM CSV (ATK_KRH_CONFIG: the single config row re-imported with one flag changed, content files header only; helper set-help-options/scripts/one_value_package.py); export compare read-back; test-and-restore
depends_on: none
test_records: OracleUnivEnabled N->Y (100004743427336) and back to N (100004743428382); fresh F N->Y->N (100004744404768, 100004743428451); re-test R N->Y->N (100004744404906, 100004743428470)
notes: Batch 13. Test-and-restore under the sitting-4 rule (old value known, one flag, back within 3 minutes). Before vs after compare {} each time; topic and title counts unchanged. Fresh test PASS; wording fixed (process log holds the result; export check line; retry folder; Creation filter); re-test PASS.
