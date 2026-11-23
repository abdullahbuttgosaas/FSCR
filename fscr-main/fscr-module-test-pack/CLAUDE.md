# fscr-module-test-pack

## Rules (always, before anything else)

1. **Only the test environment.** Never production. If you are not sure, stop and ask.
2. **Create only records that start with `FSCRT_` plus the person's own initials**, for example `FSCRT_AB_`.
   This includes Run Books, projects and business units. Use neutral test words, never real customer or brand names.
3. **Never edit or delete existing data.**
4. **Never print tokens, passwords or user names**: not in chat, files, logs or images. Never show the values in
   `core/auth/fusionEnv.properties`.
5. **Each person signs in with their own Oracle login.** You never type or ask for a password.
6. **At the end, stop and delete every server or process you started** (sign-in listener on port 8765, headless
   browsers, Python scripts) and check nothing is left running.
7. **Screenshots are minimal**: at most 4 PNG table images at 2x (coverage, plan result, the 6-task table, the final
   row values), each with a title, a clean table and a footer with the source file, with no tokens or user names
   visible. Make them only with `module-test-kit/scripts/make_images.py`.

## What this pack is

One download for testing how well Oracle's FSCR (Fusion Setup and Configuration Skills Registry) handles one module of
the FSCR Module Test Tracker. It holds:

- **A clean copy of the official FSCR repository** (github.com/oracle/fscr, the commit in `PACK_VERSION.txt`). Every FSCR
  file is unchanged; see `CHANGES.md`. For FSCR's own skills and routing, read `AGENTS.md` and `README.md`. To start FSCR
  work, use `router/implementation-router/SKILL.md`. For sign-in, use `core/getting-started/onboarding/SKILL.md`.
- **`module-test-kit/`**: the method (`PLAYBOOK.md`), scripts, prompts, the scope map for all tracker modules
  (`module_scope_map.csv`, `module_counts.csv`), the tracker format (`SHEET_FILL_GUIDE.md`), finished examples, and an
  optional patch.

Nothing in this pack needs any other folder or download.

## When the user says "test module X" (or "Test the module X, my initials are XX")

Follow `module-test-kit/PLAYBOOK.md` from Step 0 to Step 8, the same as `module-test-kit/prompts/module_test.md` with
`{MODULE}` = X and `{INITIALS}` = XX. If the initials are missing, ask for them before creating anything.
Work in `work/<Module>/`, and produce `evidence/<Module>/` with `tracker_row.md` ready to paste. The person uploads that
folder to Drive and sends Abdullah the link. Nobody edits the tracker; Abdullah updates it.

When the user asks to "verify" or "check" a finished module, follow `module-test-kit/prompts/verify.md`.

## Model

Use **Opus 5.5** (`claude-opus-5-5`) for module tests and checks.

## Python

FSCR and the kit scripts need Python 3.10 or newer (3.11 or 3.12 recommended), standard library only. On Windows, run
`python`; on Mac, `python3`.
