# _gap_fills

**Everything in this folder was written by us (GoSaaS) and is not official FSCR.** Nothing here edits, moves or deletes an FSCR file. Each skill uses FSCR's scripts in place and sends its output to a separate run folder.

| Gap | Area | How it was filled | Run | Date | Tested by a fresh chat |
|---|---|---|---|---|---|
| Manage Journal Categories (`GL_MANAGE_JOURNAL_CATEGORIES`) | ERP, General Ledger | FSCR's generic export and import scripts plus a CSV layout taken from a read-only ETIA-TEST export and Oracle docs; skill in `journal-categories\SKILL.md` with 3 helper scripts (2 offline, 1 read-only REST GET); changes in `journal-categories\CHANGELOG.md` | Run 24 (created 3 FSCRT_ categories in ETIA-TEST); skill written in Run 26a; tested in Run 26b; fixed in Run 26c | 2026-11-15 | Yes, Run 26b: worked using only the skill, 1 attempt, about 4 minutes; wording fixed in Run 26c |
| Manage Alternate Name Mapping Rules (`ORA_MANAGE_ALTERNATE_NAME_MAPPING_RULES`) | Receivables (ERP, Customer Payments) | REST POST found in Oracle docs (`alternateNameMappingRules`); Run 25 sent it with its own small script, the skill uses FSCR's generic REST client (run for this resource in Run 27b); skill in `alternate-name-mapping-rules\SKILL.md` with 1 offline helper script; changes in `alternate-name-mapping-rules\CHANGELOG.md` | Run 25 (created 2 FSCRT_ rules in ETIA-TEST); skill written in Run 27a; tested in Run 27b (created 2 more); fixed in Run 27c | 2026-11-16 | Yes, Run 27b: worked using only the skill, 2 records, first attempt; wording fixed in Run 27c |
