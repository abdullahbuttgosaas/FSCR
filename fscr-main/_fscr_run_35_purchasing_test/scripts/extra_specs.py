# Run 35 specs added after the exports arrived (exec'd by build_packages35.py). Only new FSCRT_ rows.
UN = "FSCRT_R35_UN"
SPEC["PO_MANAGE_UN_NUMBERS"] = ({
  "PO_UN_NUMBER.csv": [dict(UnNumberCode=UN, UnNumber=UN, Description="FSCR Run 35 test UN number", HazardClassCode=HC)],
  "PO_UN_NUMBER_TRANSLATION.csv": [{"PO_UN_NUMBER.UnNumberCode": UN, "UnNumber": UN, "Description": "FSCR Run 35 test UN number", "Language": "US", "SourceLang": "US"}]},
  [UN])
# Category DFF: a NEW context FSCRT_R35_CTX with one segment on ATTRIBUTE6 (not used by the global segments 1,2,4,5).
# Value set FSCRT_R34_VS was created by Run 34 (an FSCRT_ record). The existing flexfield row is NOT included.
DFF, APP, CTX = "EGP_CATEGORY_DFF", "10011", "FSCRT_R35_CTX"
K = {"FND_APP_DESCRIPTIVE_FLEXFIELD.DescriptiveFlexfieldCode": DFF, "FND_APP_DESCRIPTIVE_FLEXFIELD.ApplicationId": APP}
SPEC["EGP_MANAGE_CATEGORY_ATTRIBUTES"] = ({
  "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.csv": [dict(K, ContextCode=CTX, ContextIdentifier="FSCRT_R35_CTX", Name="FSCRT_R35 Context",
        Description="FSCR Run 35 test context", EnabledFlag="Y", MultirowFlag="N", AdvancedQueryFlag="N", TranslatableFlag="N")],
  "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_SEGMENT.csv": [{**K, "ORA_FND_APP_DESCRIPTIVE_FLEXFIELD_CONTEXT.ContextCode": CTX, "SegmentCode": "FSCRT_R35_SEG",
        "SegmentIdentifier": "FSCRT_R35_SEG", "ColumnName": "ATTRIBUTE6", "Name": "FSCRT_R35 Segment", "Description": "FSCR Run 35 test segment",
        "Prompt": "FSCRT_R35 Segment", "ShortPrompt": "FSCRT_R35", "SequenceNumber": "10", "EnabledFlag": "Y", "DisplayType": "TEXT_BOX",
        "DisplayWidth": "30", "RequiredFlag": "N", "ReadOnlyFlag": "N", "BIEnabledFlag": "N", "IndexedFlag": "N", "ShowValueDescription": "N",
        "ValueSetCode": "FSCRT_R34_VS"}]},
  [CTX, "FSCRT_R35_SEG"])
# EPP lookups: a NEW user lookup type in the External Purchase Prices module (ModuleId read from standardLookups REST, ORA_SCH_EPP_* types).
LK = "FSCRT_R35_EPP_LKP"
SPEC["ORA_MANAGE_EXTERNAL_PURCHASE_PRICES_LOOKUPS"] = ({
  "FND_APP_STANDARD_LOOKUP.csv": [dict(LookupType=LK, Meaning="FSCRT_R35 EPP Lookup", Description="FSCR Run 35 test lookup type",
        ModuleId="B862754B98C2262DE0533380F50A6DA9", CustomizationLevel="U", RestAccessSecured="SECURE")],  # attempt 2: Run 30 value; attempt 1 hit ORA-01400
  "ORA_FND_APP_STANDARD_LOOKUP_CODE.csv": [{"FND_APP_STANDARD_LOOKUP.LookupType": LK, "LookupCode": "FSCRT_A", "Meaning": "FSCRT_R35 Value A",
        "Description": "FSCR Run 35 test code", "EnabledFlag": "Y", "StartDateActive": "2026/01/01", "DisplaySequence": "1"}]},
  [LK, "FSCRT_A"])
