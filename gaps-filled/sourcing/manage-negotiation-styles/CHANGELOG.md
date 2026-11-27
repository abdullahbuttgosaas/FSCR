# Changelog: Manage Negotiation Styles

- 2026-11-27, Sourcing batch 02 (AB with Claude, sitting 1). Skill written from the read-only export and the own live test.
- Own test: clone of Standard_Negotiation (clone_rows.py, new helper): 1 style + 1 translation + 3 document types + 3 translations; import 2 objects, 0 failed; export 5 -> 6 styles, 15 -> 18 document-type rows; compare PASS; ACTIVE, SystemFlag N, 3 document types enabled.
- fresh F (v1.0.0): GAPFILL_AB_S2_STY2F (ProcessId 100004744442096) PASS.
- Suggestions NOT applied (no wrong sentence; each would need a re-test): add <text> (the description) to the placeholders; let Step 1's count script also count the metadata XML; add echo rc after the export and import. Suggestion NOT applied: print the source style's document types in Step 4.
