task_code: PO_MANAGE_FOB_LOOKUP
task_name: Manage FOB Lookup
module: Procurement
status: tested
filled_by: AB
date: 2026-11-25
minutes_to_write: 4
minutes_to_test: 12
waiting_minutes: 5
fresh_claude_pass: yes (round F broke on a network drop with no ProcessId, nothing created; wording fixed; round R PASS, no wrong sentence)
route: FSM CSV (standard lookup package, type FOB) + REST standardLookups read-back
depends_on: none (seeded extensible type FOB)
test_records: code GAPFILL_AB_B5_FOB1 on FOB (ProcessId 100004744393796); fresh GAPFILL_AB_B5_FOB2F NOT created (connection dropped before a ProcessId; REST and export prove nothing changed); re-test code GAPFILL_AB_B5_FOB3R (100004744397138)
notes: Batch 05 (sitting 3, demo task released from DEMO_RESERVE.md, filled for the demo). Export empty at first (scope FOB); type row copied unchanged from REST (lookup_type_row.py). Own test PASS: 2 rows processed, 0 failed; REST: 1 code added, type and its 1 seeded code unchanged (type LastUpdateDate same). Fresh round F: import broke with "Remote end closed connection without response" before a ProcessId; tester did not re-import; skill had no rule for this case -> added (poll REST 10 min, prove with export, retry needs approval) + Step 4 also after a failed import + empty-grep note. Round R PASS. Suggestions NOT applied (would need another re-test): give a safe row-count/code list one-liner in Step 1; write the after-export command out in full in Step 4; a command for the MEANING-unique check; say MEANING/DESC must not contain "|"; say an unattended run must stop (not open a browser) on 401/403. Where it shows: Setup and Maintenance > Procurement > Procurement Foundation > Manage FOB Lookup (type FOB).
