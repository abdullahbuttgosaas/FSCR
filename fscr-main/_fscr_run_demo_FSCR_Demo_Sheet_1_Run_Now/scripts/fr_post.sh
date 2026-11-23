#!/usr/bin/env bash
# Demo run: POST-only wrapper around FSCR's own REST client (fusion_rest_client.py) in fscr-work-demo.
# Refuses any body that names Corsair/Intel/AMD/NVIDIA (user rule) and any endpoint outside the approved three.
# Usage: fr_post.sh <endpoint> <body.json> <response_out.json>
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
ep="$1"; body="$2"; out="$3"
case "$ep" in
  /fscmRestApi/resources/11.13.18.05/standardLookups|\
  /fscmRestApi/resources/11.13.18.05/standardLookups/FSCRT_DEMO_ROUTE_TIER_F11/child/lookupCodes|\
  /fscmRestApi/resources/11.13.18.05/standardLookups/ORA_DOO_ORDER_TYPES/child/lookupCodes) ;;
  *) echo "REFUSED: endpoint not approved"; exit 2;;
esac
if grep -qiE "corsair|intel|amd|nvidia" "$body"; then echo "REFUSED: blocked brand name in body"; exit 2; fi
W="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_demo_FSCR_Demo_Sheet_1_Run_Now/fscr-work-demo"
cd "$W" || exit 1
python core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --no-open-browser --method POST --header "Content-Type=application/json" --body-file "$body" --output "$out" "$ep"
echo "rc=$? $(date +%T)"
