# Batch 24 result: Common Features (AB), geography interface, tax geographies, GL messages, cross-validation rules, balancing segments

GoSaaS work, not official FSCR. AB with Claude, 2026-11-26/27 (eleventh Common Features sitting, first batch). No test record was created: the only live tries (geography interface) read 0 rows. Work folder outside the repo.

## Time log
| Start | Finish | Minutes | Note |
|---|---|---:|---|
| 23:50 | 23:54 | 4 | Tracker rebuilt, 6 open tasks picked; sign-in (waiting) |
| 23:54 | 00:05 | 11 | Geography: object metadata, columns, upload, 3 activity tries, read back (0 rows read) |
| 00:05 | 00:10 | 5 | Geography content-name lookup; decision written (unsafe), same rule as Run Geography Loader |
| 00:10 | 00:22 | 12 | Skills (5), Oracle docs for cross-validation rules import, cards |

## Results
| # | Task | Status | Working min | Waiting min | Proof |
|---|---|---|---:|---:|---|
| 1 | Load Geography Interface Data | written (unsafe) | 13 | 3 | route seen live; 3 tries read 0 rows; master geography is shared, no delete |
| 2 | Manage Tax Geographies | written (unsafe) | 4 | 0 | no own record; changes existing countries' tax use |
| 3 | Manage Messages for General Ledger | **failed** | 4 | 0 | same blocker as Manage Messages: upload process job path not published |
| 4 | Manage Cross-Validation Rules | written (unsafe) | 5 | 1 | FBDI route (Oracle docs); rules block combinations on the shared chart; Replace mode deletes |
| 5 | Manage Associated Balancing Segments | written (unsafe) | 4 | 0 | only file route builds a whole ledger setup (permanent) |
| | **Total** | **4 written, 1 failed** | **30** | **4** | |

## Problems and findings
1. **Geography interface:** Import Management object `GeographyInterface` and its columns are real; `erpintegrations uploadFileToUCM` (account `crm$/geography$/import$`) returns a numeric DocumentId, but `importActivities` DataFiles need the content name (`UCMFA0...`). Inline `InputFileContent` is refused; `UCMFA0`+DocumentId pointed at another document; the numeric id gave `ERROR`. No row was read in any try, so nothing was created.
2. **Rule slip:** batch 21 had already judged geography loads unsafe (shared, no delete). The three tries above should not have been run; they created nothing. The card says so, and the task is now written (unsafe) like Run Geography Loader.
3. **Cross-validation rules:** Oracle's FBDI *Cross-Validation Rules Import* (interface `GL_CROSS_VALIDATION_RULES_INT`) has Increment and Replace modes; Replace deletes every rule not in the file. Written unsafe: no own test chart of accounts here.
4. **GL messages:** same object and next step as Manage Messages (batch 23).

## What is left
See `MODULE_RESULT.md`.
