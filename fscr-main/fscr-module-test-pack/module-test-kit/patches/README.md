# Optional patches

These are NOT applied. The FSCR files in this pack are the official originals from git. Use a patch only if
you hit the exact error it fixes, and say so in your RESULT.md ("with a patch").

## payment_terms_object_order.patch

- **File it changes:** `pillars/erp/financials/customer-billing/manage-receivables-payment-terms/scripts/payment_terms_fsm_package.py`
- **What it fixes:** the official script stops with `payment_terms_object_order_mismatch` when the Oracle
  environment lists the Payment Terms objects in a different order than the script expects. The script expects
  TERM, TRANSLATION, DISCOUNT, LINE; the test environment returned LINE, TERM, TRANSLATION, DISCOUNT.
  The patch removes that fixed-order check. It keeps one check: the template and the baseline export must list
  the objects in the same order.
- **Where it came from:** Run 01 (28/10/2026), Receivables payment terms. With the patch, the load ran end to end
  and the reconcile found 0 mismatches. The original script was not tried again after that.
- **When to use it:** only when you test Receivables Payment Terms and you get `payment_terms_object_order_mismatch`.
- **How to apply it** (from the top folder of the pack; undo with `git apply -R`, or unzip the pack again):

  ```bash
  git apply module-test-kit/patches/payment_terms_object_order.patch
  ```

  No git installed? Ask Claude: "apply module-test-kit/patches/payment_terms_object_order.patch by hand".
