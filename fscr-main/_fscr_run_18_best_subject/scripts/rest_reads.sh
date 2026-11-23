#!/usr/bin/env bash
# Run 18: read-only REST reads (GET only, via rget.py reused from Run 09/17). A non-200 is reported, not retried.
R="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_18_best_subject"; cd "$R" || exit 1
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
G="python scripts/rget.py"; F=/fscmRestApi/resources/11.13.18.05; O=evidence/rest; mkdir -p $O
r(){ n=$1; shift; echo -n "$n: "; $G "$@" --out $O/$n.json | head -3; }
r bu_lov          $F/finBusinessUnitsLOV --all --query onlyData=true --query limit=500
r ref_sets        $F/setIdSetsLOV --all --query onlyData=true --query limit=500
r currencies      $F/currenciesLOV --all --query onlyData=true --query limit=500
r ledgers         $F/ledgersLOV --all --query onlyData=true --query limit=500
r price_lists     $F/priceLists --all --query onlyData=true --query limit=500 --query fields=PriceListId,PriceListName,BusinessUnitId,BusinessUnit,CurrencyCode,StatusCode
r data_access     $F/dataSecurities --all --query onlyData=true --query limit=500
r set_assign_bu   $F/setIdAssignmentsBusinessUnit --all --query onlyData=true --query limit=500
r legal_entities  $F/legalEntitiesLOV --all --query onlyData=true --query limit=500
