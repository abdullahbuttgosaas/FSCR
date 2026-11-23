# _patches: our changes to Oracle's FSCR files

The Oracle FSCR repo copies are not in git (class C, see `.gitignore`). These are the only Oracle files we changed, so they are kept here.

Base: `https://github.com/oracle/fscr`, commit **2801695** (`2801695703b909891753790b60a694d2b270724e`, "FSCR 26D Release").

| File here | Replaces this Oracle file (path inside an FSCR copy) | What |
|---|---|---|
| `payment_terms_fsm_package.py` | `pillars\erp\financials\customer-billing\manage-receivables-payment-terms\scripts\payment_terms_fsm_package.py` | Our fix: the payment terms package no longer demands one fixed business-object order (it varies by pod, e.g. LINE, TERM, TRANSLATION, DISCOUNT); instead the template and the baseline export must declare the same order. Identical in all 22 run copies that have it (SHA-256 `49fbabeb…2b27`; Oracle's original is `285f7102…9e91`). |
| `payment_terms_fsm_package.py.patch` | same file | The same change as a diff (Oracle original -> ours), 10 lines added, 13 removed. |
| `fusionEnv.properties.example` | `core\auth\fusionEnv.properties` | Key names only. The filled file holds the ETIA-TEST sign-in settings and is a secret: fill it by hand from `fscr-signin-values.txt`, never commit it. |

Not kept: `core\data-loader\config\env.properties` (we only set a `runID` value there).

To apply in a fresh clone of oracle/fscr at 2801695: copy `payment_terms_fsm_package.py` over the Oracle path above, or run `git apply` with the `.patch` (its paths name `fscr-official-clone/...` and `_patches/...`, so edit the two header lines first, or just copy the file).
