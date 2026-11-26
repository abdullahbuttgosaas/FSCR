task_code: ORA_PO_CONFIGURE_ELECTRONIC_SIGNATURE
task_name: Configure Electronic Signature for Procurement Documents
module: Procurement
status: written
filled_by: AB
date: 2026-11-27
minutes_to_write: 6
minutes_to_test: 1
waiting_minutes: 1
fresh_claude_pass: n/a (unsafe to test: needs provider credentials an agent must not enter)
route: FSM CSV (ORA_ZCA_ESIGNATURE_SETUP) - read-only export only; setup by a person on the screen
depends_on: a DocuSign or Adobe Sign account and its credentials (entered by a person)
test_records: none (export only: 23 columns, 0 rows; re-checked 2026-11-27)
notes: Batch 02 (written). Re-judged in batch 07 (sitting 4, 2026-11-27) against the 'new prefix record is not unsafe' rule: the reason still holds. Fresh read-only export: ORA_ZCA_ESIGNATURE_SETUP.csv 0 rows, columns UserName, Password, ConfirmPassword, AccountId, AdobeSignRefreshToken, APIKey, EndpointUrl, OauthUrl. A row is not a stand-alone test record: it is the environment's one e-signature setup (EsignatureSetupCode) that turns on signing for every user's procurement documents, and it cannot be loaded without provider credentials, which an agent must never enter (fake ones would break signing and cannot be validated). No safe way: no own test record and no test-and-restore (nothing to restore to; no delete by CSV). Safe when: a person with a provider sandbox account loads it on an environment we own. Not screen-only (the CSV route exists).
