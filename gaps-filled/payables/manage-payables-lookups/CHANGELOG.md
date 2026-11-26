# CHANGELOG - Manage Payables Lookups

## 2026-11-25 (sitting 1, batch 01)
- Own test, PAY GROUP / FSCRT_AK_GF_PG1 (each try refused the row; nothing created, confirmed by the
  after-export which shows only the final row):
  - try 1, ProcessId 100004744396738: code + US translation row -> JBO-25026/JBO-25027 "LookupGenericTranslation
    cannot be loaded". Diagnosis: translation row clashes for a new code.
  - try 2, ProcessId 100004744403973: same + CreatedBy/LastUpdatedBy from SubmittedBy (lesson) -> same error.
  - try 3, ProcessId 100004744397542: translation row removed -> JBO-27014 "Attribute ChangeSinceLastRefresh ...
    is required" (base and translation EO).
  - fix after the column compare with a working code (KR_EMP has ChangeSinceLastRefresh N),
    ProcessId 100004744404058: ChangeSinceLastRefresh=N -> 1 row processed, 0 failed.
  - Export compare: codes 12 -> 13, translations 12 -> 13 (US row created automatically), removed/changed 0.
- REST: genericLookups returns the type (CustomizationLevel E, ModuleId read live); its child lookupCodes
  returned 0 items even for existing codes, so the export compare is the read-back. commonLookups,
  setEnabledLookups, standardLookups do not hold PAY GROUP.
- Fresh test F: FSCRT_AK_GF_PG1F, ProcessId 100004744404109, PASS on the first try (13 -> 14). No errors.
- Own read-back: final export lists PG1 and PG1F; first vs final: codes +2, translations +2, removed/changed 0.
- Tester suggestions not applied: move the code check into Export; give a Meaning max length; say the REST
  type values are safe to print; list the strings to look for in the log; say Description may differ.
