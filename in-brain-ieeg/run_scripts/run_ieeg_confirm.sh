#!/bin/bash
cd /tmp/claude-0/-home-claude/027d4b7c-f2cc-5790-bcb7-09ba6a5870a7/scratchpad/mf_ieeg
export PNMS_DATA=/tmp/claude-0/-home-claude/027d4b7c-f2cc-5790-bcb7-09ba6a5870a7/scratchpad/runi/data PNMS_DERIV=/tmp/claude-0/-home-claude/027d4b7c-f2cc-5790-bcb7-09ba6a5870a7/scratchpad/runi/derivatives PYTHONPATH=src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="/tmp/claude-0/-home-claude/027d4b7c-f2cc-5790-bcb7-09ba6a5870a7/scratchpad/venv/bin/python -W ignore"
for p in R1077T R1068J R1311T R1123C R1151E R1334T R1111M R1292E R1377M R1145J R1222M R1121M R1158T R1350D R1217T R1243T R1345D R1060M R1125T R1391T; do
  [ -f $PNMS_DERIV/models/sub-${p}_results.json ] && { echo "=== $p done already"; continue; }
  echo "=== $p $(date -u +%FT%TZ)"
  $PY scripts/s03_extract_features.py $p --jobs 4
  $PY scripts/s04_fit_models.py $p --jobs 4 --perms 200
done
echo GROUPSTAGE $(date -u +%FT%TZ)
echo END $(date -u +%FT%TZ)
