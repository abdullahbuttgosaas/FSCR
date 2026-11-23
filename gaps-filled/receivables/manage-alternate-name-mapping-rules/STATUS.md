task_code: ORA_MANAGE_ALTERNATE_NAME_MAPPING_RULES
task_name: Manage Alternate Name Mapping Rules
module: Receivables
status: tested
filled_by: GoSaaS (Runs 25, 27a-c)
date: 2026-11-16
minutes_to_write: unknown
minutes_to_test: 12
waiting_minutes: unknown
fresh_claude_pass: yes
route: REST
depends_on: none
test_records: FSCRT_R25 Payer A; others unknown; GAPFILL_AB_RT_ANM; GAPFILL_AB_RT_ANM2
notes: Copy of fscr-main/_gap_fills/alternate-name-mapping-rules. Live fill Run 25 = 9 min; skill writing (Run 27a) not timed; test 12 min of which about 8 were sign-in timeouts. Created by REST POST. v0.2.0 fixes after the Run 27b cold test were checked offline, not by a new fresh test. Re-tested 2026-11-24 after the wording fix: PASS.
