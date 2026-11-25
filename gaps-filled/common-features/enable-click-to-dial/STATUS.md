task_code: MCT_ENABLE_CLICK_TO_DIAL
task_name: Enable Click to Dial
module: Common Features
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 2
waiting_minutes: 0
fresh_claude_pass: yes (re-test R after a wording fix)
route: REST profileOptions/HZ_ENABLE_CLICK_TO_DIAL/child/siteProfileOptionValues/SITE PATCH (SITE is the only enabled level); REST read-back; test-and-restore. CSV export holds 0 rows (seeded option and value left out)
depends_on: none
test_records: SITE N->Y->N own (3 s); fresh F N->Y->N (4 s); re-test R N->Y->N (5 s)
notes: Batch 13. Option found from the export metadata scope (HZ_ENABLE_CLICK_TO_DIAL). Test-and-restore under the sitting-4 rule. Fresh test PASS; wording fixed (one ready block writing both body files, print only 2 fields, stop if no SITE row, Prerequisites before Step 1); re-test PASS. Tester suggestions not applied (no wrong sentence): full read loop for Step 2 with field printing; set shell variables once at the top of the Step 3 block; mkdir RUN in the block.
