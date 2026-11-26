task_code: PO_MANAGE_PURCHASING_DESCRIPTIVE_FLEXFIELDS
task_name: Manage Purchasing Descriptive Flexfields
module: Purchasing
status: tested
filled_by: MZ
date: 26/11/2026
minutes_to_write: 16
minutes_to_test: 10
waiting_minutes: 8
fresh_claude_pass: Y
route: FSM_CSV (FSCR task-level export/import)
depends_on: PO_MANAGE_PURCHASING_VALUE_SETS (a test value set); an existing Purchasing DFF (PO_LINE_TYPES) whose row is sent unchanged
test_records: DFF PO_LINE_TYPES contexts FSCRT_MZ_GF_CTX1 (own), FSCRT_MZ_GF_CTXF (fresh), FSCRT_MZ_GF_CTXR (retest R), FSCRT_MZ_GF_CTX2R (retest 2R), each with one segment on ATTRIBUTE1
notes: own live test try 1 import 100004743436790 (refused: multirow N, display type LIST_OF_VALUES), try 2 100004744417669 (refused: translatable N), try 3 100004744422130 (3 rows, 0 failed); after-export 100004743454753; final fresh retest (2R) passed with no factual error. retest_after_wording_fix: done. tested on 26/11/2026 after the tester confirmed the environment is for testing only. IMPORTANT: the FSM import deploys the flexfield automatically (DeploymentDate moved from 04/04/2026 to each import time), so the 4 test contexts are live as context choices on the Purchasing Line Types DFF (context-sensitive; no other page or existing segment changed). Earlier (25/11) marked unsafe to test.
