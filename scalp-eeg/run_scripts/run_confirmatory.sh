#!/bin/sh
# Confirmatory run, registered at https://osf.io/9ghzn (frozen code, checksums verified first).
set -e
S=/tmp/claude-0/-home-claude/027d4b7c-f2cc-5790-bcb7-09ba6a5870a7/scratchpad
cd $S/run
export PNMS_DATA=$PWD/data PNMS_DERIV=$PWD/derivatives
PY="$S/venv/bin/python -W ignore"
M=$S/mf/scripts
echo "START $(date -u +%FT%TZ)"
(cd $S/mf && sha256sum -c ../FROZEN_SHA256.txt)
IDS="LTP067 LTP069 LTP070 LTP073 LTP077 LTP079 LTP081 LTP082 LTP084 LTP085 LTP086 LTP087 LTP088 LTP089 LTP090 LTP091 LTP092 LTP093 LTP094 LTP095"
$PY $M/s02_build_behaviour.py $IDS
for s in $IDS; do
  echo "=== $s extract $(date -u +%FT%TZ)"
  $PY $M/s03_extract_features.py $s --jobs 4
  echo "=== $s models $(date -u +%FT%TZ)"
  $PY $M/s04_fit_models.py $s --jobs 4
  $PY $M/s04_fit_models.py $s --jobs 4 --perms 0 --no-task-lists
done
echo "=== group $(date -u +%FT%TZ)"
$PY $M/s05_group_stats.py
$PY $M/s06_pooled_model.py
echo "END $(date -u +%FT%TZ)"
