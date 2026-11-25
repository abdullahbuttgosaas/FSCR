# CHANGELOG: manage-data-access-for-users (GoSaaS gap fill)

- 2026-11-25, batch 10 (AB with Claude). Read-only export and dataSecurities reads/describe verified (9 contexts seen). Status written (unsafe to test).
- 2026-11-25, batch 11 (AB with Claude). Re-opened (new unsafe rule). Live tries 1 and 2 refused (role code only; user without the role), nothing created; role added to own test user; try 3 created and read back (Userrf filter; UserName filter returns 0). Skill rewritten as tested. Fresh test (U2F, DAS3F): PASS.
- Tester suggestions not applied (no wrong sentence): say how to rebuild plan.json for an existing test user before create-implementation-users Step 5 (run its Step 2 again, any example.com mail); page the 500-row read with offset or filter by RoleCommonName; rows of other testers on a shared test user are normal; no REST check that a data access set exists (a POST with an unknown value is refused, GUESS); POST answers also hold the server address (keep in RUN).
