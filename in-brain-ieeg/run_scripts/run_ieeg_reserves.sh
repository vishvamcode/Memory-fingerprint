#!/bin/bash
# Registered replacement rule: next IDs in the same shuffled order until 6 replacements succeed.
cd /tmp/claude-0/-home-claude/027d4b7c-f2cc-5790-bcb7-09ba6a5870a7/scratchpad/mf_ieeg
export PNMS_DATA=/tmp/claude-0/-home-claude/027d4b7c-f2cc-5790-bcb7-09ba6a5870a7/scratchpad/runi/data PNMS_DERIV=/tmp/claude-0/-home-claude/027d4b7c-f2cc-5790-bcb7-09ba6a5870a7/scratchpad/runi/derivatives PYTHONPATH=src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
PY="/tmp/claude-0/-home-claude/027d4b7c-f2cc-5790-bcb7-09ba6a5870a7/scratchpad/venv/bin/python -W ignore"
ORDER="R1067P R1092J R1309M R1147P R1195E R1384J R1308T R1441T R1385E R1347D R1065J R1193T"
NEED=6; GOT=0
for p in $ORDER; do
  [ $GOT -ge $NEED ] && break
  if [ ! -f $PNMS_DERIV/models/sub-${p}_results.json ]; then
    echo "=== $p $(date -u +%FT%TZ)"
    [ -f $PNMS_DERIV/behaviour/sub-${p}_words.csv ] || $PY scripts/s02_build_behaviour.py $p
    $PY scripts/s03_extract_features.py $p --jobs 4
    $PY scripts/s04_fit_models.py $p --jobs 4 --perms 200
  fi
  [ -f $PNMS_DERIV/models/sub-${p}_results.json ] && { GOT=$((GOT+1)); echo "REPLACEMENT_OK $p ($GOT/$NEED)"; }
done
echo END $(date -u +%FT%TZ)
