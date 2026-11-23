# AutoInvoice Grouping Rules: sheet columns, request keys and Oracle's columns

Tabs in `page/sheet_definition.json` (2026-11-01). Every rule is checked by `run.py --plan` (`agr_rules.py`); the page
only reads types and required columns. How to fill them (the Corsair story: Corsair bills OEM customers Intel, AMD
and NVIDIA through AutoInvoice).

## Tab "AutoInvoice Grouping Rules" (one row per rule) -> `AR_AI_GROUPING_RULE`

| Column | Key | Oracle column | Rule | Corsair example |
|---|---|---|---|---|
| Name * | name | Name | 1-40 characters, not ORA_..., no outer spaces; existing name = skipped | CORSAIR OEM BY ORDER REFERENCE |
| Item Description | description | Description | max 80 | One invoice per OEM order reference for Intel, AMD and NVIDIA |
| From Date * | from_date | StartDate | YYYY-MM-DD; never filled in for you | 2026-11-01 |
| To Date | to_date | EndDate | on or after From Date | (empty) |
| (none) | | LineOrderingRuleName, ConsBillingUseFlag, AttributeCategory, Attribute1-15 | always empty | |

## Tab "Grouping Rule Classes" (one row per class, or per class + characteristic) -> `ORA_AR_AI_GRP_TXN_TYPE` and `ORA_AR_AI_GRP_TXN_REQUEST`

| Column | Key | Oracle column | Rule | Corsair example |
|---|---|---|---|---|
| Grouping Rule Name * | (join only) | AR_AI_GROUPING_RULE.Name | the rule's Name, exactly | CORSAIR OEM BY ORDER REFERENCE |
| Transaction Class * | transaction_class | Class11 (I / D / C) | Invoice, Debit Memo, Credit Memo; each once per rule | Invoice |
| Characteristic | characteristic | FromColumnName (one row under the class) | a name a rule in Oracle already uses; each once per class | L.INTERFACE_LINE_ATTRIBUTE1 (one of the seven ETIA-TEST's rules use) |

Rows with the same class make one class; each filled Characteristic adds one characteristic under it. Example: three
rows for CORSAIR OEM BY ORDER REFERENCE = Invoice + L.INTERFACE_LINE_ATTRIBUTE1, Debit Memo, Credit Memo.

Oracle's messages the folder turns into plain words: `agr_package.MESSAGES` (FSCR `ora_error_handling.md:11-12`,
`ora_input_validation.md:45`).
