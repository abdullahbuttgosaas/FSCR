#!/usr/bin/env bash
# Run 08: FSCR's own REST client (fusion_rest_client.py) for the ONLY three writes this run allows.
# Whitelist: PATCH FSCRT_PADDLING (drift + revert) and POST one new code FSCRT_CAMPING_F08 into
# FSCRT_OUTDOOR_ACTIVITY_F01. Never DELETE/PUT; no retry. Usage: frw.sh <drift|revert|extra> <out-name>
# (response written to evidence/<out-name>).
set -u
R8="/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_08_compare"
R8W="E:/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_08_compare"
T=/fscmRestApi/resources/11.13.18.05/standardLookups/FSCRT_OUTDOOR_ACTIVITY_F01/child/lookupCodes
case "$1" in
  drift)  M=PATCH; P="$T/FSCRT_PADDLING"; B=drift_paddling.json;;
  revert) M=PATCH; P="$T/FSCRT_PADDLING"; B=revert_paddling.json;;
  extra)  M=POST;  P="$T";                B=extra_camping.json;;
  *) echo "NOT_WHITELISTED: $1"; exit 2;;
esac
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
cd "$R8/fscr-work8" || exit 1
echo "$(date '+%H:%M:%S') $M $P body=$(cat "$R8/payloads/$B")"
python core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --no-open-browser --method "$M" \
  --body-file "$R8W/payloads/$B" --output "$R8W/evidence/$2" "$P"
echo "exit $? $(date '+%H:%M:%S')"
