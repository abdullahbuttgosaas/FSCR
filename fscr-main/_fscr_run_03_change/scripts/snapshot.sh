#!/usr/bin/env bash
# Read-only whole-area snapshot for Run 03 (before/after side-effect diff). Usage: snapshot.sh <before|after>
# Price lists and customers have no FSCR export, so REST/SOAP reads cover them; FSCR's customer reader is used
# for the 4 FSCRT accounts. Lookups and order types are also read by REST in addition to the FSCR export.
set -u
S="$1"; R3="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_03_change"; cd "$R3" || exit 1
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
G="python scripts/rget.py"; F=/fscmRestApi/resources/11.13.18.05; O="evidence/$S"
mkdir -p "$O"
$G $F/priceLists --all --query onlyData=true --query limit=500 --query expand=accessSets --out $O/priceLists_all.json
$G $F/standardLookups --all --query onlyData=true --query limit=500 --query "q=LookupType LIKE 'FSCRT%'" --query expand=lookupCodes --out $O/standardLookups_fscrt.json
$G $F/standardLookups/ORA_DOO_ORDER_TYPES/child/lookupCodes --all --query onlyData=true --query limit=500 --out $O/order_types_all.json
$G $F/finBusinessUnitsLOV --all --query onlyData=true --query limit=500 --out $O/finBusinessUnitsLOV.json
$G $F/customerAccountSitesLOV --all --query onlyData=true --query limit=500 --out $O/customerAccountSitesLOV_all.json
$G /crmRestApi/resources/11.13.18.05/hubOrganizations --all --query onlyData=true --query limit=500 --query "q=OrganizationName LIKE 'FSCRT%'" --query expand=Address --out $O/hubOrganizations_fscrt.json
$G /crmRestApi/resources/11.13.18.05/hubPersons --all --query onlyData=true --query limit=500 --query "q=FirstName LIKE 'FSCRT%'" --query expand=Address --out $O/hubPersons_fscrt.json
for a in 22050:300000394607181 22051:300000394607188 22052:300000394612201 22053:300000394593177; do
  python scripts/fscr_cust_read2.py $O/acct_${a%%:*}.json customer-account account_id=${a##*:}
done
