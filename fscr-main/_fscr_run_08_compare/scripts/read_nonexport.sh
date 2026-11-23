#!/usr/bin/env bash
# Run 08: read-only reads for the areas FSCR cannot export (adapted from Run 03 snapshot.sh, same scripts).
# Price lists: rget.py (Claude's GET-only reader; FSCR has no price-list read route).
# Org customers: enumeration of FSCRT organizations with rget.py (hubOrganizations), then FSCR's own
# customer_soap_read (via fscr_cust_read2.py) for each account and its location.  Usage: read_nonexport.sh <label>
set -u
L="$1"; R8="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_08_compare"; cd "$R8" || exit 1
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
G="python scripts/rget.py"; F=/fscmRestApi/resources/11.13.18.05; O="actual/$L/raw"
mkdir -p "$O"
$G $F/priceLists --all --query onlyData=true --query limit=500 --query "q=PriceListName LIKE 'FSCRT%'" --query expand=accessSets --out $O/priceLists_fscrt.json
$G /crmRestApi/resources/11.13.18.05/hubOrganizations --all --query onlyData=true --query limit=500 --query "q=OrganizationName LIKE 'FSCRT%'" --query expand=Address --out $O/hubOrganizations_fscrt.json
for a in 22050:300000394607181 22051:300000394607188; do
  python scripts/fscr_cust_read2.py $O/acct_${a%%:*}.json customer-account account_id=${a##*:}
  loc=$(grep -o 'LocationId>[0-9]*<' $O/acct_${a%%:*}.json | head -1 | tr -dc 0-9)
  [ -n "$loc" ] && python scripts/fscr_cust_read2.py $O/loc_${a%%:*}.json location location_id=$loc
done
