#!/usr/bin/env bash
# Run 09: read-only REST reads for the 3 impact cases (GET only, via rget.py reused from Run 08).
# One line per read; a non-200 means "could not check by this route" and is reported, not retried.
R9="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_09_impact"; cd "$R9" || exit 1
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
G="python scripts/rget.py"; F=/fscmRestApi/resources/11.13.18.05; O=evidence/rest; mkdir -p $O
PT=FSCRT_2P10N30F1; OT=FSCRT_SO_TRAIL_DEALER_F01; BUN="FSCRT_Brindle Harbor Marine Supply F01"; BUID=300000394664009
r(){ n=$1; shift; echo -n "$n: "; $G "$@" --out $O/$n.json | head -3; }
# Case 1: payment term
# Third pass: invoice finder needs a customer/source/date; read invoices of the 4 FSCRT accounts and source FSCRT_TS1;
# total visible invoice and order counts.
r inv_total        $F/receivablesInvoices --query onlyData=true --query limit=1 --query totalResults=true --query fields=CustomerTransactionId
for a in 22050 22051 22052 22053; do
r inv_cust_$a      $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;BillToCustomerNumber=$a" --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms,BusinessUnit
done
r inv_src_ts1      $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;TransactionSource=FSCRT_TS1" --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms,BusinessUnit
