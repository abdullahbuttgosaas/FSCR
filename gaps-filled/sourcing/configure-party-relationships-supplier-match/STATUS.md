task_code: ORA_POZ_CONFIGURE_PARTY_RELATIONSHIPS_FOR_SUPPLIER_MATCH
task_name: Configure Party Relationships for Supplier Match
module: Sourcing and Supplier Management
status: tested
filled_by: AB
date: 2026-11-28
minutes_to_write: 12
minutes_to_test: 9
waiting_minutes: 8
fresh_claude_pass: yes (fresh F PASS, re-test R PASS on v1.0.1; no false sentence left)
route: FSM CSV (ORA_SUPPLIER_MATCH_PARTY_RELATIONSHIP, one column RelationshipType); prerequisite type by FSM CSV task HZ_MANAGE_RELATIONSHIP_TYPES, read back by CRM REST relationshipTypes (read only)
depends_on: HZ_MANAGE_RELATIONSHIP_TYPES (a NEW own organization-to-organization relationship type that no party uses; the supplier match list is shared and has no delete)
test_records: relationship type tries 1-4 refused (100004743466577 Name required; 100004743464742 CreatedByModule required, left role lookup RM_USER_ROLE1795806916146 "GAPFILL AB test partners"; 100004743464751 duplicate of that lookup; 100004743466610 subject = object plural, left role lookup RM_USER_ROLE1795807067987 "GAPFILL AB S3 RT1 partners"); type GAPFILL_AB_S3_RT1 (100004744441598, try 5) + list row GAPFILL_AB_S3_RT1 (100004743464762, own test); type GAPFILL_AB_S3_RT2F (100004743466695) + list row (100004744442300, fresh F (v1.0.0)); type GAPFILL_AB_S3_RT3R (100004743466917) + list row (100004743464856, re-test R (v1.0.1))
notes: Sourcing batch 03 (sitting 2). Adding a seeded type would change supplier matching for everyone with no CSV undo, so the safe way is an own relationship type. The type took 5 tries (failure protocol; each cause proved: Name = role texts, CreatedByModule HZ_RM_UI, leftover role lookup from a refused try, subject and object plurals must differ). The supplier match import passed first try; list 0 -> 1, only our type. Fresh F PASS; tester found the sentence "export holds 0 type rows before and after" false (its export listed type rows): v1.0.1 reworded (the export lists only types made by this route and can lag), re-test R PASS with no false sentence. 2 orphan role lookups from refused tries stay (own texts, harmless). Suggestions NOT applied: print the builder's expected counts in P2; print CSV row counts in P1; say one run adds one RM_USER_ROLE lookup; say earlier test types will be in the list.
