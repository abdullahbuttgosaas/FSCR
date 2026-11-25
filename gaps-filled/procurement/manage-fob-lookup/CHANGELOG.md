# Changelog: Manage FOB Lookup

- 2026-11-25, batch-05 (AB with Claude, sitting 3; task released from the demo reserve and filled for the demo). Skill written from the read-only export, the REST read of type FOB and the tested Contract Clause Types pattern.
- Own test: code GAPFILL_AB_B5_FOB1 (ProcessId 100004744393796): 2 rows processed, 0 failed; REST read-back PASS; after-export holds type + 2 codes.
- Fresh round F: code GAPFILL_AB_B5_FOB2F NOT created: connection dropped before a ProcessId ("Remote end closed connection without response"); REST and export prove nothing changed. Wrong/missing sentence reported: no rule for a drop with no ProcessId. Fixed: new shell-section rule, Step 3 empty-grep note and safe look at import.out, Step 4 runs also after a failed import, worked-example note.
- Fresh round R: code GAPFILL_AB_B5_FOB3R (ProcessId 100004744397138) PASS, export compare PASS, no wrong sentence. Status tested.
- Suggestions not applied: Step 1 safe row-count/code list one-liner; after-export command in full; MEANING-unique check command; no "|" in MEANING/DESC; unattended run must stop on 401/403.
