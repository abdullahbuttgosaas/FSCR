#!/bin/bash
# Thin wrapper: calls FSCR's own core REST client (fusion_rest_client.py) with Git-Bash path conversion disabled.
# Usage: fr.sh <endpoint> [client args...]
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
cd "/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_01/fscr-work" || exit 1
python core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --no-open-browser "$@"
