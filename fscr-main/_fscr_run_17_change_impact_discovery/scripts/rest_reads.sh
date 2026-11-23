#!/usr/bin/env bash
# Run 17: read-only REST reads (GET only, via rget.py reused from Run 09). A non-200 is reported, not retried.
R="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_17_change_impact_discovery"; cd "$R" || exit 1
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
G="python scripts/rget.py"; F=/fscmRestApi/resources/11.13.18.05; O=evidence/rest; mkdir -p $O
r(){ n=$1; shift; echo -n "$n: "; $G "$@" --out $O/$n.json | head -3; }
# Order types
r ot_lookup_type   $F/standardLookups --query onlyData=true --query "q=LookupType='ORA_DOO_ORDER_TYPES'"
r ot_lookup_codes  $F/standardLookups/ORA_DOO_ORDER_TYPES/child/lookupCodes --all --query onlyData=true --query limit=500
r so_total         $F/salesOrdersForOrderHub --query onlyData=true --query limit=500 --query totalResults=true --query fields=HeaderId,OrderNumber,TransactionTypeCode,SourceTransactionSystem,BusinessUnitName
# Price lists
r pl_all           $F/priceLists --all --query onlyData=true --query limit=500
r ps_strategies    $F/pricingStrategies --all --query onlyData=true --query limit=500
r ps_strategy_pl   $F/pricingStrategies --all --query onlyData=true --query limit=500 --query expand=priceLists
r cpd_definitions  $F/customerPricingDefinitions --all --query onlyData=true --query limit=500
r pricing_segments $F/pricingSegments --all --query onlyData=true --query limit=500
# Source systems and external systems
r src_systems      $F/tradingCommunityOrgSourceSystems --all --query onlyData=true --query limit=500
r hz_src_systems   $F/sourceSystems --all --query onlyData=true --query limit=500
