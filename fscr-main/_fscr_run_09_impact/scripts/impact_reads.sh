#!/usr/bin/env bash
# Run 09: read-only REST reads for the 3 impact cases (GET only, via rget.py reused from Run 08).
# One line per read; a non-200 means "could not check by this route" and is reported, not retried.
R9="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_09_impact"; cd "$R9" || exit 1
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
G="python scripts/rget.py"; F=/fscmRestApi/resources/11.13.18.05; O=evidence/rest; mkdir -p $O
PT=FSCRT_2P10N30F1; OT=FSCRT_SO_TRAIL_DEALER_F01; BUN="FSCRT_Brindle Harbor Marine Supply F01"; BUID=300000394664009
r(){ n=$1; shift; echo -n "$n: "; $G "$@" --out $O/$n.json | head -3; }
# Case 1: payment term
r pt_invoices      $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "q=PaymentTerms='$PT'" --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms,BusinessUnit
r pt_orders        $F/salesOrdersForOrderHub --all --query onlyData=true --query limit=500 --query "q=PaymentTerms='$PT'" --query fields=HeaderId,OrderNumber,PaymentTerms
# Case 2: order type lookup code
r ot_orders        $F/salesOrdersForOrderHub --all --query onlyData=true --query limit=500 --query "q=TransactionTypeCode='$OT'" --query fields=HeaderId,OrderNumber,TransactionTypeCode
r ot_lookup_now    $F/standardLookups/ORA_DOO_ORDER_TYPES/child/lookupCodes --query onlyData=true --query "q=LookupCode='$OT'"
# Case 3: business unit
r bu_pricelists    $F/priceLists --all --query onlyData=true --query limit=500 --query "q=BusinessUnitId=$BUID" --query fields=PriceListId,PriceListName,StatusCode,BusinessUnit
r bu_setassign     $F/setIdAssignmentsBusinessUnit --all --query onlyData=true --query limit=500 --query "q=DeterminantValue=$BUID"
r bu_datasec       $F/dataSecurities --all --query onlyData=true --query limit=500 --query "q=SecurityContextValue='$BUN'"
r bu_invoices      $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "q=BusinessUnit='$BUN'" --query fields=CustomerTransactionId,TransactionNumber,BusinessUnit
r bu_orders        $F/salesOrdersForOrderHub --all --query onlyData=true --query limit=500 --query "q=BusinessUnitId=$BUID" --query fields=HeaderId,OrderNumber,BusinessUnitId
r bu_lov           $F/finBusinessUnitsLOV --query onlyData=true --query "q=BusinessUnitId=$BUID"
# Second pass (filters the first pass could not use): invoiceSearch finder; PaymentTermsCode on orders.
r pt_invoices2     $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;PaymentTerms=$PT" --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms,BusinessUnit
r pt_invoices_d25  $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;PaymentTerms=FSCRT_D25B75AF1" --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms
r pt_orders2       $F/salesOrdersForOrderHub --all --query onlyData=true --query limit=500 --query "q=PaymentTerms='$PT'" --query fields=HeaderId,OrderNumber,PaymentTerms
r bu_invoices2     $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;BusinessUnit=$BUN" --query fields=CustomerTransactionId,TransactionNumber,BusinessUnit
r bu_orders_req    $F/salesOrdersForOrderHub --all --query onlyData=true --query limit=500 --query "q=RequestingBusinessUnitId=$BUID" --query fields=HeaderId,OrderNumber
# Third pass: invoice finder needs a customer/source/date; read invoices of the 4 FSCRT accounts and source FSCRT_TS1;
# total visible invoice and order counts.
r inv_total        $F/receivablesInvoices --query onlyData=true --query limit=1 --query totalResults=true --query fields=CustomerTransactionId
for a in 22050 22051 22052 22053; do
r inv_cust_$a      $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;BillToCustomerNumber=$a" --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms,BusinessUnit
done
r inv_src_ts1      $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query "finder=invoiceSearch;TransactionSource=FSCRT_TS1" --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms,BusinessUnit

r inv_all          $F/receivablesInvoices --all --query onlyData=true --query limit=500 --query fields=CustomerTransactionId,TransactionNumber,PaymentTerms,BusinessUnit,TransactionType,TransactionSource,BillToCustomerName
