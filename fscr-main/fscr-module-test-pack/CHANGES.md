# Changes compared with the official FSCR repository

Official repository: https://github.com/oracle/fscr, commit `2801695703b909891753790b60a694d2b270724e` (see PACK_VERSION.txt).

## 1. Settings that point at an existing Run Book (step 0b)

Every tracked settings file (`.properties`, `.yaml`, `.json` configs) was searched for a Run Book ID, run ID or
journey ID with a value.

| File | Setting | Official value | Value in this pack | Change |
|---|---|---|---|---|
| `core/data-loader/config/env.properties` | `runID` | empty | empty | none needed |

No other tracked setting points at a Run Book. **No FSCR file was changed.** All 6,087 FSCR files are
byte-identical to the commit. Before every load, still check that `runID` is empty or holds **your own** Run Book.
Never load into someone else's Run Book.

## 2. How this pack differs from the copy we tested with

Our working copy, unpacked on 28/10/2026, differed from the commit in exactly these 3 files. The pack ships the
**official originals** of all 3:

| File | Our working copy | In this pack |
|---|---|---|
| `pillars/erp/financials/customer-billing/manage-receivables-payment-terms/scripts/payment_terms_fsm_package.py` | patched on 28/10/2026 (fixed object-order check removed) | official original. The patch is optional, in `module-test-kit/patches/` |
| `core/auth/fusionEnv.properties` | filled in with our environment, Client ID and scopes | official template (placeholders, empty scopes). Each person fills in their own |
| `core/data-loader/config/env.properties` | `runID` set to one of our Run Books | official original (`runID` empty) |

The comparison was done file by file on git blob hashes: 6,087 tracked files, 3 different, 0 missing.
The working copy also had files git does not track (2 `__pycache__` folders and a draft project folder).
None of them were copied.

## 3. Files added on top of the repository

- `CLAUDE.md`: what the pack is, the rules, and what to do on "test module X"
- `SETUP.md`: one-page setup for a new person
- `README_PACK.md`: three lines. It is not named `README.md`, so the official FSCR `README.md` stays untouched
- `PACK_VERSION.txt`, `CHANGES.md`: this file
- `module-test-kit/`: playbook, scripts, prompts, tracker guide, scope map, examples, optional patch

## 4. Build checks

- The kit and the added files scan clean with `secret_scan.py`. Nothing in them points to folders outside the pack.
- The official FSCR files are byte-identical to the commit, so nothing was removed from them. The scanner does flag
  Oracle's own content: code that handles tokens, a password prompt, Oracle help-site links, a placeholder e-mail,
  and 3 machine paths of Oracle's authors (2 under `pillars/hcm/*/best-practice-rules/*/source-integrity.json`,
  1 in `pillars/hcm/hcm-tool/approval-rules/configure-rules/ora-resource/ora_reference_lookups.md`).
  These are public in oracle/fscr and contain nothing of ours.
- Scripts tested on Run 35 (Purchasing) data: the plan numbers match that run (3 of 4 sourced links in order,
  2 of 4 unverified out of order).

## Build time log

| Start | Finish | Minutes |
|---|---|---:|
| 17/11/2026 16:05 | 17/11/2026 16:35 | 30 |

The start is approximate: it is when the build was approved after the git question, before the clone at 16:08.
