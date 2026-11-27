# Changelog: Manage Attribute Lists

- 2026-11-27, Sourcing batch 02 (AB with Claude, sitting 1). Skill written from the read-only export and the own live test.
- Own test: export empty, rows written in full. Try 1 (ProcessId 100004743465828) refused: JBO-27014 AuctionHeaderId required in SourcingRequirementSectionEO and SourcingRequirementAndAttributeEO, 4 objects failed; export proved nothing created. Diagnosis: list rows are not tied to a negotiation, Oracle's placeholder id is -1. Try 2 with AuctionHeaderId=-1 and LineNumber=-1: 4 objects, 0 failed; export shows 1 list (ACTIVE, LINE), 1 group (GENERAL), 1 attribute (TXT, OPTIONAL), 0 scores.
- fresh F (v1.0.0): GAPFILL_AB_S2_ATL2F (ProcessId 100004743466110) PASS.
- Suggestions NOT applied (no wrong sentence; each would need a re-test): add <text> (the description) to the placeholders; let Step 1's count script also count the metadata XML; add echo rc after the export and import. Suggestions NOT applied: a one-line command for the LIST-exists check after Step 1; a payload check that the ZIP holds only new rows.
