# Memory fingerprint: first experiment (PEERS ltpFR)

Does a person's scalp EEG, recorded while they study a word, predict whether they
will later recall it, **beyond** what a non-neural model already predicts, in a
session and for words the model has never seen?

Data: Penn Electrophysiology of Encoding and Retrieval Study, OpenNeuro
[ds004395](https://openneuro.org/datasets/ds004395) v2.0.0, CC0, no login.
Full rationale: the research report and the dataset selection document in this project.

## Setup

```bash
python3.12 -m venv .venv && source .venv/bin/activate     # Python 3.11+ works
pip install -e ".[test]"                                   # pinned versions in pyproject.toml
pytest -q                                                  # 38 tests, about 2 minutes, no download
```

Data and outputs go to `./data` and `./derivatives` unless you set
`PNMS_DATA` and `PNMS_DERIV`.

## Stages (run in order, read each output before moving on)

| Stage | Command | Downloads | What it checks or produces |
| --- | --- | --- | --- |
| 0 | `python scripts/s00_select_participants.py` | ~3,600 event files (~550 MB) | Applies the selection rule; stops if it does not reproduce the IDs in `config.py` |
| 1 | `python scripts/s01_inspect_events.py LTP063` | small sidecars | Per-session report: lists, recall rate, recognition, sampling rate, sample/onset alignment |
| 2 | `python scripts/s02_build_behaviour.py` | none | Word tables with labels and non-neural predictors; non-neural held-out AUC |
| 3 | `python scripts/s03_extract_features.py LTP063 --jobs 4` | ~0.6 GB per session, deleted after use | Log Morlet power per word, saved per session; restartable |
| 4 | `python scripts/s04_fit_models.py LTP063 --jobs 4` | none | Held-out AUC for non-neural, EEG, combined and artefact-robust models; permutation null |
| 5 | `python scripts/s05_group_stats.py [--pilot]` | none | Primary test, bootstrap CI, decision (success / failure / ambiguous), recognition secondary, figure |
| 6 | `python scripts/s06_pooled_model.py [--pilot]` | none | Personal versus pooled EEG decoders |

Work on the **pilot** participants (LTP063, LTP065, LTP066) until everything runs and
looks sensible. Then freeze `config.py`, post the pre-registration, and only then run
stages 3-6 on the 20 confirmatory participants.

## Resources measured on a 4-core test machine

- One session: about 85 s for loading, filtering, epoching and wavelets; peak memory about 6 GB.
- One EEG file: 0.5-0.7 GB; deleted after features are saved unless `--keep-raw`.
- Features: well under 1 MB per session.

## Layout

```
src/pnms/config.py        every fixed setting (selection rule, IDs, frequencies, window, SESOI)
src/pnms/download.py      S3 listing and verified downloads (no account needed)
src/pnms/events.py        schema checks, recall/recognition label derivation
src/pnms/behaviour.py     non-neural predictors, item recallability from other people only
src/pnms/eeg_features.py  label-blind preprocessing and spectral features
src/pnms/models.py        leave-one-session-out with item hold-out, stacked combined model, permutation null
src/pnms/stats.py         Wilcoxon, hierarchical bootstrap, decision rules, Holm
scripts/                  the stages above
tests/                    unit tests; fixtures are real CC0 files from sub-LTP063 ses-0
```

## Verified facts this code relies on

Checked on the real files on 21 Oct 2026 (see the dataset selection document):
event columns `onset, trial_type, sample, trial, item_name, item_num, task, recog_resp, recog_conf`;
no `recalled` column (labels derived from `REC_WORD` rows); recognition answers stored on
`RECOG_TARGET` rows; `sample` = `onset` x 500 Hz; EGI files have 125 EEG + 4 EOG channels.
BioSemi (`.bdf`) participants are excluded from the first run because their files have not
been checked yet.
