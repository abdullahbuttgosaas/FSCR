# Changelog

One line per session: date, machine, what changed. Newest at the bottom.

- 2026-11-23, PC (DESKTOP-TJ1S90V), baseline commit: repo created; class A + B files tracked (gaps-filled, runs 1–38 reports/results/evidence/exports, kit, Configuration Automation, context notes); Oracle copies, secrets and junk ignored; memory files, `.example` templates and `_patches\` added.
- 2026-11-24, PC (DESKTOP-TJ1S90V): gap filling batches 2 (9 of 10 tested) and 3 (7 of 10 tested), batch 1 re-test (10 of 10 pass; journal categories and alternate name mapping skills made portable); 28 gaps tested in total (Common Features 26, GL 1, Receivables 1); tax chain (Zone Types, Statuses, Rates, Rules) failed and parked with screen-only; CLAUDE.md added; CONTEXT.md sections 9, 11, 12 updated; index rebuilt.
- 2026-11-24, PC (DESKTOP-TJ1S90V): tax chain fixed: Tax Statuses, Rates, Rules tested (cause: missing GCO option row, now Step 7 of manage-tax-regimes) and Tax Zone Types tested (cause: empty CreatedBy/LastUpdatedBy; new helper zone_type_rows.py); 32 gaps tested, 0 failed; Security read-only re-check with boss_scope (6 of 6 read OK, loads blocked by rmc_scope, Risk Administrator role and safety); CONTEXT.md sections 8, 9, 11, 12 updated; index rebuilt.
