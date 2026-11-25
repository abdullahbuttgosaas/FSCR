# CHANGELOG: view-accounting-configuration-summary (GoSaaS gap fill, not official FSCR)

## 0.1.0, 2026-11-25 (batch 05, AB with Claude)
- Read-only export: Read-only export GL_VIEW_ACCOUNTING_CONFIGURATION_SUMMARY: 11 files (GL_LEDGER 49, GL_PRIMARY_LEDGER 65, ORA_GL_LEDGER_RELATIONSHIP 17, ORA_GL_JOURNAL_CONFIG_DETAIL 47, ORA_LEGAL_ENTITY_BAL_SEG_VAL_DEF 38, ...). REST ledgersLOV and chartOfAccountsLOV.
- Live (AB): ledgersLOV 1 row (PRIMARY, USD, calendar, COA number); view: primary + 1 secondary (SUBLEDGER), 2 legal entities CONFIRMED, 3 balancing segment values. READ-BACK PASS.
- Fresh test PASS on MG Primary ledger (2 secondary + 1 ALC ledger, 1 LE). Wrong sentence found and fixed. Re-test R on AKLedger IN: PASS (ALC GBP JOURNAL level, 1 LE CONFIRMED, BSV 02).
- Tester notes not applied (suggestions): 'unzipped folder' wording, Name1 vs TargetLedgerName, say to copy ChartOfAccountsId from the first call.

## Test records created
- none created (view task); looked up existing ledgers: live 28Ledger US, fresh test MG Primary ledger, re-test AKLedger IN
