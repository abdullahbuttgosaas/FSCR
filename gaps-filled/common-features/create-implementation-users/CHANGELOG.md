# CHANGELOG: create-implementation-users (GoSaaS gap fill)

- 2026-11-25, batch 09 (AB with Claude). Pointer skill to FSCR core/getting-started/implementation-users with shared-environment rules. Preflight not run (blocked by tool permissions). Status written (unsafe to test).
- 2026-11-25, batch 11 (AB with Claude). Re-opened (new unsafe rule). Skill rewritten as a tested skill: plan with roles emptied, preflight, create, optional Step 5 (roles for own test user), read-back. Own test GAPFILL_AB_B11_U1: created, no roles; then 3 roles (PATCH 'error' false alarm). Fresh test U2F: PASS. Wording fixed (Steps 1, 3, 4, 6). Re-test U3R: PASS.
- Tester suggestions not applied: say the leftover plan fields (requiredRolesForAllowedActivities, validationChecklist) are harmless; Prerequisite 1 points forward to Step 3; write the full Step 4 command; Step 1 sign-in can be skipped with a working cached token; worked-example 'fresh test' row points here.
