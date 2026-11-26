# Changelog: Configure Electronic Signature for Procurement Documents

- 2026-11-25, batch-02 (AB with Claude). Skill written from the read-only export and live tries. Export only: 2 files, ORA_ZCA_ESIGNATURE_SETUP.csv 23 columns, 0 rows. No import (credentials).
- Test records: none (export only: 23 columns, 0 rows).
- Fresh test: n/a (no import: needs provider credentials an agent must not enter).

- 2026-11-27, batch-07 (AB with Claude, sitting 4). Status: written.
- Test records: none (export only: 23 columns, 0 rows; re-checked 2026-11-27)
- Fresh test: n/a (unsafe to test: needs provider credentials an agent must not enter)
- Notes: Batch 02 (written). Re-judged in batch 07 (sitting 4, 2026-11-27) against the 'new prefix record is not unsafe' rule: the reason still holds. Fresh read-only export: ORA_ZCA_ESIGNATURE_SETUP.csv 0 rows, columns UserName, Password, ConfirmPassword, AccountId, AdobeSignRefreshToken, APIKey, EndpointUrl, OauthUrl. A row is not a stand-alone test record: it is the environment's one e-signature setup (EsignatureSetupCode) that turns on signing for every user's procurement documents, and it cannot be loaded without provider credentials, which an agent must never enter (fake ones would break signing and cannot be validated). No safe way: no own test record and no test-and-restore (nothing to restore to; no delete by CSV). Safe when: a person with a provider sandbox account loads it on an environment we own. Not screen-only (the CSV route exists).
