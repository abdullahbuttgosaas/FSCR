# CHANGELOG: manage-bu-data-access-for-users (GoSaaS gap fill)

- 2026-11-25, batch 10 (AB with Claude). Skill written (shares rules with manage-data-access-for-users). Status written (unsafe to test).
- 2026-11-25, batch 11 (AB with Claude). Re-opened (new unsafe rule). Own grant created and read back. Skill rewritten as tested. Fresh test (U2F, Buyer, GoSaaS): PASS.
- Tester suggestions not applied (no wrong sentence): say how to rebuild plan.json for an existing test user before create-implementation-users Step 5 (run its Step 2 again, any example.com mail); page the 500-row read with offset or filter by RoleCommonName; rows of other testers on a shared test user are normal; no REST check that a data access set exists (a POST with an unknown value is refused, GUESS); POST answers also hold the server address (keep in RUN). Step 5 snippet could also reset abstractRoles.
