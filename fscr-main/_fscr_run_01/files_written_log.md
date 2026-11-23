# Files written in this run (all under _fscr_run_01)
| File | Size | Why |
|---|---|---|
| ./exp_bu_template.log | 1093 bytes | |
| ./exp_pt_data.log | 1044 bytes | |
| ./exp_pt_template.log | 1062 bytes | |
| ./files_written_log.md | 89 bytes | |
| ./identified-task-mapping-run01.json | 5145 bytes | |
| ./input_records.md | 7569 bytes | |
| ./ledger.csv | 15596 bytes | |
| ./ledger.md | 9738 bytes | |
| ./ledger_rows/m1_m2_m3.json | 8700 bytes | |
| ./ledger_rows/m4_m5.json | 6257 bytes | |
| ./ledger_rows/m6_m7_m8.json | 7910 bytes | |
| ./login_01.log | 733 bytes | |
| ./mapping.csv | 2116 bytes | |
| ./payloads/customers.json | 8998 bytes | |
| ./payloads/lc_freight.json | 82 bytes | |
| ./payloads/lc_hiking.json | 93 bytes | |
| ./payloads/lc_paddling.json | 148 bytes | |
| ./payloads/lc_standard.json | 84 bytes | |
| ./payloads/lt1.json | 203 bytes | |
| ./payloads/lt2.json | 248 bytes | |
| ./payloads/ot_trail.json | 158 bytes | |
| ./payloads/ot_warranty.json | 147 bytes | |
| ./payloads/pl1.json | 437 bytes | |
| ./payloads/pl1_buname.json | 482 bytes | |
| ./repo_hashes_start.md5 | 870566 bytes | |
| ./RUN_REPORT.md | 27097 bytes | |
| ./run_times.txt | 142 bytes | |
| ./scripts/build_bu_package.py | 2031 bytes | |
| ./scripts/customers_soap.py | 11093 bytes | |
| ./scripts/fr.sh | 398 bytes | |
| ./scripts/fscr_customer_read.py | 940 bytes | |
| ./scripts/ledger_add.py | 623 bytes | |
| ./scripts/rest_diag.py | 2213 bytes | |
| ./scripts/taskhook_lifecycle.py | 2213 bytes | |
| ./scripts/token_lifetime.py | 567 bytes | |
| ./scripts/token_status.py | 816 bytes | |
| ./scripts/verify_customers.py | 5842 bytes | |
| ./scripts/verify_lookups.py | 1982 bytes | |
| ./scripts/xsd_dump.py | 1120 bytes | |
| ./step2_task_skill_map.md | 5812 bytes | |
| ./step3_dependencies_and_order.md | 3876 bytes | |
| evidence/ (165 files) | 3104631 bytes | Oracle responses, FSM logs, read-backs |
| fscr-work/ | full FSCR copy (86 MB) + new project fscrt-run01-om-setup | All FSCR execution (decision D7) |
- 2026-11-03 06:18 payloads/pl2.json: request body for price list 2 (Brindle, EUR), prepared and not sent; Line Type and Calculation Method left out so Oracle applies its defaults.
- 2026-11-03 06:44 follow-up: RUN_REPORT.md, ledger.md, ledger.csv, mapping.csv updated; ledger_rows/m2_followup.json, evidence/pricelists/*, login_02.log written.
- 2026-11-03 07:10 follow-up 2: payloads/pl_approve.json; evidence/pricelists/{describe,pl1_approve_a1,pl2_approve_a1,readback_after_approve}.json; evidence/pt_limit/* (read-only describes); evidence/corrections_backup/ (pre-correction copies of RUN_REPORT.md, ledger.md, ledger.csv, mapping.csv); scripts/fix_report_followup2.py and scripts/fix_ledgers_followup2.py (one-off correction scripts); RUN_REPORT.md, ledger.md, ledger.csv, mapping.csv corrected.
