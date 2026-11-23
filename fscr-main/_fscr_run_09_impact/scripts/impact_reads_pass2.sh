#!/usr/bin/env bash
# Run 09: read-only REST reads for the 3 impact cases (GET only, via rget.py reused from Run 08).
# One line per read; a non-200 means "could not check by this route" and is reported, not retried.
R9="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_09_impact"; cd "$R9" || exit 1
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
G="python scripts/rget.py"; F=/fscmRestApi/resources/11.13.18.05; O=evidence/rest; mkdir -p $O
PT=FSCRT_2P10N30F1; OT=FSCRT_SO_TRAIL_DEALER_F01; BUN="FSCRT_Brindle Harbor Marine Supply F01"; BUID=300000394664009
r(){ n=$1; shift; echo -n "$n: "; $G "$@" --out $O/$n.json | head -3; }
# Case 1: payment term
# Second pass (filters the first pass could not use): invoiceSearch finder; PaymentTermsCode on orders.
r pt_invoices2     $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;PaymentTerms=$PT" --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms,BusinessUnit
r pt_invoices_d25  $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;PaymentTerms=FSCRT_D25B75AF1" --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms
r pt_orders2       $F/salesOrdersForOrderHub --all --query onlyData=true --query limit=500 --query "q=PaymentTerms='$PT'" --query fields=HeaderId,OrderNumber,PaymentTerms
r bu_invoices2     $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;BusinessUnit=$BUN" --query fields=CustomerTransactionId,TransactionNumber,BusinessUnit
r bu_orders_req    $F/salesOrdersForOrderHub --all --query onlyData=true --query limit=500 --query "q=RequestingBusinessUnitId=$BUID" --query fields=HeaderId,OrderNumber
