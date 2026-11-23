#!/usr/bin/env bash
# Run FSCR's own REST client from the Run 03 working copy, GET only.
# Why: Git Bash rewrites /fscmRestApi/... arguments (Run 01 finding F1); MSYS_NO_PATHCONV=1 stops it.
case " $* " in *" --method "*) echo "READ_ONLY: fr2.sh refuses --method (GET only)"; exit 2;; esac
export MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
cd "/e/GoSaaS/Configuration Automation v2.1/fscr-main/_fscr_run_08_compare/fscr-work8" || exit 1
python core/fusion-api/rest-api-client/scripts/fusion_rest_client.py --no-open-browser "$@"
