# Memory fingerprint: sub-project 1, intracranial EEG (RAM FR1)

Same question as the first experiment (registered at osf.io/9ghzn): does brain activity
recorded while a person studies a word predict whether they will later recall it,
beyond a non-neural model, for sessions and words the model has never seen? Here with
electrodes inside the brain: OpenNeuro ds004789 v3.1.0 (CC0), task FR1, bipolar files.

What differs from the scalp-EEG code and why is listed in the pre-registration addendum.
The main change: every FR1 session shows the same 300 words, so the test set is one
session x one of 4 fixed word groups, and training uses other sessions and other groups.

## Setup

    python3 -m venv .venv && source .venv/bin/activate
    pip install -e ".[test]"
    pytest -q            # 35 tests, about 10 minutes; no download

Set PNMS_DATA and PNMS_DERIV for the data and output folders.

## Stages

| Stage | Command | What it does |
| --- | --- | --- |
| 0 | `python scripts/s00_select_participants.py` | downloads the FR1 event files, applies the selection rule, checks the fixed IDs |
| 2 | `python scripts/s02_build_behaviour.py` | word tables, recall labels, non-neural model |
| 3 | `python scripts/s03_extract_features.py R1077T --jobs 2` | log Morlet power per word and channel, one session at a time |
| 4 | `python scripts/s04_fit_models.py R1077T --jobs 2` | non-neural, brain-only, combined and robust models; permutation null; neighbour test |
| 5 | `python scripts/s05_group_stats.py [--replace OLD=NEW]` | group statistics and the registered verdict |

There is no stage 1 (inspection) or stage 6 (pooled model) in this version.
