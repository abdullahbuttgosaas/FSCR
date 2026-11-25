task_code: ORA_PO_CONFIGURE_ELECTRONIC_SIGNATURE
task_name: Configure Electronic Signature for Procurement Documents
module: Procurement
status: written
filled_by: AB
date: 2026-11-25
minutes_to_write: 5
minutes_to_test: 1
waiting_minutes: 1
fresh_claude_pass: n/a (unsafe to test: needs provider credentials an agent must not enter)
route: FSM CSV (ORA_ZCA_ESIGNATURE_SETUP) - read-only export only; setup by a person on the screen
depends_on: a DocuSign or Adobe Sign account and its credentials (entered by a person)
test_records: none (export only: 23 columns, 0 rows)
notes: Batch 02. Written, unsafe to test (credentials): the only row holds UserName, Password, AccountId, refresh token, API key; an agent must not type or store these, and fake values on the one shared row would break signing. Skill = masked read-only export + hand-over steps. Not screen-only (the CSV route exists) but the credentials rule blocks an agent test.
