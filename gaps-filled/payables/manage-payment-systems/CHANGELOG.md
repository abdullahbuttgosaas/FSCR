# CHANGELOG - Manage Payment Systems

## 2026-11-25 (sitting 1, batch 02) - failed with proven cause
- Export (ProcessId 100004743427215): 8 CSVs; 31 payment systems (25 seeded, 6 user-created). Credential and
  URL columns exist in IBY_PAYMENT_SYSTEM.csv; they were never printed.
- Diagnosis log (each refused row created nothing; final export compare: added 0, removed/changed 0):
  1. try 1, ProcessId 100004743426216: Suffix FSCRT_AK_GF_PS1, BankName "FSCRT AK GF test bank" (made up),
     no dates -> "Row Identifier: BankId. Status: Error" (bank not found).
  2. try 2, ProcessId 100004743428155: BankName removed -> FND_CMN_CMPLT_FLDS "You must complete the
     required fields".
  3. try 3, ProcessId 100004743429062: StartDate/EndDate added (as on the working record) -> same.
  4. prerequisite check: bank "MM Bank" exists (REST cashBanks, read only). Round trip with that bank
     (ProcessId 100004743429083) -> same.
  5. full round trip of the working record MM1214 (all exported columns, new Suffix/Name, who-columns from
     SubmittedBy), ProcessId 100004743428187 -> same. PROOF that the exported columns are not enough to
     create a payment system.
- Next step: 10-character Suffix test (FSCRT_AK_2), then the task's CSV template export (read only) to find
  mandatory attributes; then retry. Fresh test not run (own test never passed).
