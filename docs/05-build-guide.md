# First Experiment: Build Guide

Oct 21, 2026 · @Vishvam

The first experiment is built as seven small stages in a Python package, `pnms`. Each stage is runnable on its own, and 35 unit tests run without downloading anything. The code is in the project's shared files at `memory-fingerprint/`, with a README that repeats the commands below. Start by installing it, running the tests, and running Stage 0 and Stage 1. Those need no EEG download and check every assumption the later stages rely on.

The experiment tests the hypothesis fixed in the [dataset selection document](https://claude.ai/artifact/XHQcG4RNtexgBJyMUp3BPx): within a person, EEG at study improves held-out prediction of later recall over a non-neural model by at least 0.01 AUC. No column name, file path or event code in the code was assumed. Each one was read from the real PEERS files, and the tests use a real session (sub-LTP063 ses-0, CC0) as a fixture.

## Environment setup and folder structure

Python 3.11 or newer, with the exact package versions pinned in `pyproject.toml` (mne 1.13.2, numpy 2.5.4, scipy 1.18.1, pandas 3.0.6, scikit-learn 1.9.1, statsmodels 0.15.0, matplotlib 3.11.2, edfio 0.4.18; pytest 9.1.1 for tests). These are the versions the tests passed with.

```bash
cd memory-fingerprint
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[test]"
pytest -q                          # expect: 35 passed
```

By default, data go to `./data` and results to `./derivatives`. Set `PNMS_DATA` and `PNMS_DERIV` to put them elsewhere, for example on an external disk.

```
memory-fingerprint/
  pyproject.toml            pinned dependencies
  README.md                 commands for every stage
  src/pnms/
    config.py               every fixed setting: selection rule, participant IDs, frequencies, window, SESOI
    download.py             S3 listing and size-verified downloads, no account
    events.py               schema checks; recall and recognition labels
    behaviour.py            non-neural predictors; item recallability from other people only
    eeg_features.py         label-blind preprocessing and log Morlet power
    models.py               leave-one-session-out with item hold-out; stacked combined model; permutation null; pooled model
    stats.py                Wilcoxon, hierarchical bootstrap, decision rules, Holm
  scripts/
    s00_select_participants.py   s01_inspect_events.py   s02_build_behaviour.py
    s03_extract_features.py      s04_fit_models.py       s05_group_stats.py   s06_pooled_model.py
  tests/
    fixtures/               real CC0 files from sub-LTP063 ses-0 (events, channels, electrodes)
    test_events.py  test_behaviour.py  test_models.py  test_stats.py  test_features.py
```

## The seven stages

Run them in order and read each output before going on. Stages 0-2 never touch EEG; Stage 3 never sees labels. That ordering makes leakage between preprocessing and outcome impossible by construction.

| Stage | Command | What it does | How it is tested |
| --- | --- | --- | --- |
| 0. Select participants | `python scripts/s00_select_participants.py` | Lists the bucket, downloads all 3,583 ltpFR event files (about 2 minutes on the test machine), applies the rule (≥ 12 sessions, recall 0.15-0.85, EGI only) and **stops with an error** if the result differs from the IDs fixed in `config.py` | `test_select_participants_rule`: synthetic participants that fail each criterion |
| 1. Inspect | `python scripts/s01_inspect_events.py LTP063` | Prints per session: number of lists and words, recall rate, recognition coverage, encoding-task counts, sampling rate, EEG file size, and whether `sample` = `onset` × rate | Run it and read it: this is the "show me the schema first" step |
| 2. Behaviour | `python scripts/s02_build_behaviour.py` | Builds one row per studied word with the recall label and the non-neural predictors; fits the non-neural model with the same split as later | `test_events.py` checks labels against values read from the raw file (list 1: exactly HELICOPTER, OBOE, DISHWASHER, KNIFE, SUPPER, PIE, CAKE recalled; 109 of 256 in the session). `test_behaviour.py` checks exposure counts and that item recallability never uses the participant's own data |
| 3. EEG features | `python scripts/s03_extract_features.py LTP063 --jobs 4` | Per session: download, notch 60/120/180 Hz, high-pass 0.5 Hz, mark bad channels (robust z of log-variance > 5), average reference, epoch −1 to 2.6 s, log Morlet power at 8 frequencies averaged 0.2-1.6 s, z-score within session, save, delete the EDF | `test_features.py`: a synthetic 9 Hz burst is recovered on the right channel and frequency; bad-channel detector; peripheral-channel rule on the real electrode layout |
| 4. Models | `python scripts/s04_fit_models.py LTP063 --jobs 4` | Non-neural, EEG-only, combined, and artefact-robust combined models; within-stratum permutation null for EEG | `test_models.py`: no session or item overlap; finds planted signal; chance on noise; **item identity cannot leak** even when labels are a pure function of the word |
| 5. Group statistics | `python scripts/s05_group_stats.py` | Wilcoxon test, hierarchical bootstrap, the pre-registered verdict, recognition secondary, figure | `test_stats.py`: each verdict (success, failure, present-but-negligible, ambiguous) is produced by the inputs that should produce it |
| 6. Personal vs pooled | `python scripts/s06_pooled_model.py` | EEG model trained on the other participants, compared with the personal model | Uses the tested functions above |

**Order of work.** Run every stage on the three pilot participants (LTP063, LTP065, LTP066) first. Fix anything that looks wrong, then freeze `config.py`, post the pre-registration, and only then run Stages 3-6 on the 20 confirmatory participants.

## Preprocessing, baseline, validation, metrics and tests

The primary comparison is the combined model against the non-neural model, on the same held-out trials, inside each person.

**Preprocessing (label-blind, per session).** Channel types from `channels.tsv` (E8, E25, E126, E127 are EOG). Notch at 60, 120 and 180 Hz because the files list a 60 Hz power line. High-pass 0.5 Hz. Bad channels: log-variance more than 5 robust z-units from the median; set to zero after z-scoring so every session has the same feature layout. Average reference without bad channels. No ICA in the primary analysis, because a fitted decomposition makes leakage harder to rule out; it can be added as a robustness check.

**Features.** Log Morlet power at 3.0, 5.1, 8.8, 15.0, 25.6, 43.8, 74.9 and 128 Hz (cycles = frequency / 2, minimum 3), averaged 0.2-1.6 s after word onset, for 125 EEG channels: 1,000 features per word, z-scored within session.

**Baseline (non-neural) model.** Serial position (one-hot, 16), encoding task (one-hot, 3), list number, session number, prior exposures of this word to this person, word length, and item recallability. Recallability is the word's recall rate across all other ltpFR participants, shrunk toward their mean with 5 pseudo-observations.

**Decoder.** Standardise, then L2 logistic regression with balanced class weights. The combined models are stacked: the EEG model's out-of-fold score, computed inside the training sessions only, enters a small logistic regression next to the behavioural predictors. The penalty C is chosen from 10⁻⁴ to 1 (5 values) by 5-fold grouped cross-validation over the training sessions only.

**Validation.** Outer leave-one-session-out. For each test session, every training trial whose word appears in the test session is removed. Every trial is predicted exactly once, by a model that never saw that day or that word.

| Quantity | Definition | Used for |
| --- | --- | --- |
| AUC | Area under the ROC curve of held-out probabilities, pooled over sessions within a person | All models |
| ΔAUC | AUC(combined) − AUC(non-neural) | Primary outcome |
| ΔAUC robust | Same, with EEG restricted to ≤ 30 Hz and the 25% lowest channels on the cap removed | Artefact check in the success rule |
| Permutation p | Share of 200 label shuffles (within session × serial position) with AUC ≥ observed, EEG-only model | Per-person sanity check |
| Wilcoxon p | One-sided signed-rank test of ΔAUC > 0 across 20 people | Primary test |
| Bootstrap CI | Resample people, then sessions within people; 10,000 draws | 95% CI (success), 90% CI (equivalence) |
| Verdict | Success, failure (with a present-but-negligible flag), or ambiguous, computed by `stats.decide` | The answer |
| Recognition slope | Logistic slope of strong hit on held-out probability, among unrecalled tested words | Secondary 2 |
| Personal − pooled AUC | EEG-only, same trials | Secondary 1 |

## Expected figures and tables

Stage 5 draws the first two figures automatically (`derivatives/group/<sample>_auc.png`); the rest are short additions once the confirmatory run is done.

1. Held-out AUC per participant for the non-neural, EEG-only and combined models (Stage 5, left panel).
2. ΔAUC per participant with the 95% bootstrap band, the zero line and the 0.01 line, titled with the verdict (Stage 5, right panel).
3. Serial position curve and recall by encoding task, from the Stage 2 word tables.
4. Personal versus pooled AUC (Stage 6 JSON).
5. Mean coefficient patterns by frequency and scalp position, transformed to activation patterns (Haufe et al., 2014) before interpretation.
6. Calibration curve of held-out probabilities.
7. AUC against distance between training and test sessions (drift).

**Table 1** lists, per participant: number of sessions and words, recall rate, the four model AUCs, ΔAUC, robust ΔAUC and permutation p. It is written to `derivatives/group/<sample>_report.json`.

## Pipeline check on pilot data

**These numbers are a code check, not a result.** They come from the three pilot participants only (LTP063, LTP065, LTP066), using 4 to 5 sessions each instead of their full 20, with 20 permutations and 200 bootstrap draws instead of 200 and 10,000. Pilot participants are kept out of the confirmatory analysis, so nothing here counts for or against the hypothesis.

| Participant | Sessions | Non-neural AUC | EEG-only AUC (perm. p) | Combined AUC | ΔAUC | Robust ΔAUC |
| --- | --- | --- | --- | --- | --- | --- |
| LTP063 | 5 | 0.631 | 0.539 (0.048) | 0.660 | +0.029 | +0.029 |
| LTP065 | 4 | 0.708 | 0.508 (0.571) | 0.707 | −0.001 | −0.009 |
| LTP066 | 4 | 0.594 | 0.518 (0.238) | 0.582 | −0.012 | −0.014 |

With three people the decision rule returns "ambiguous" (95% CI −0.011 to +0.024), which is what it should do with this little data.

**What the check established**

- Every stage runs end to end on real files: download, schema checks, label derivation, feature extraction, all four models, permutation null, group statistics and figure. The outputs are in `memory-fingerprint/pilot_check/`.
- EEG-only decoding with 4 to 5 sessions is close to chance (0.51 to 0.54). That is not surprising with so little training data per person; the confirmatory run uses every session (at least 12 per participant).
- Bad-channel detection flagged about 5 to 12 channels per session. E129 (the Cz reference, flat by construction) is always flagged and zeroed, which causes a harmless NaN warning during extraction.

**Design change made because of the pilot, before any confirmatory data were touched**

The first version of the combined model put the 24 behavioural predictors and the 1,000 EEG features into one penalised regression. On the pilot it scored *below* the non-neural model (ΔAUC −0.050, −0.125 and −0.023), because a penalty strong enough to tame 1,000 noisy EEG features also shrinks the behavioural predictors. The combined model is now **stacked**: inside each training set the EEG model's out-of-fold score is computed, and a small logistic regression combines that one score with the behavioural predictors. The test session is never seen at any step. Two new unit tests check that pure-noise EEG does not pull the combined model clearly below the non-neural one, and that planted EEG signal is picked up. 35 tests now pass.

Write this change into the pre-registration, with the note that pilot data alone prompted it.

**Before the confirmatory run**

1. Optionally run Stage 3 on all pilot sessions (about 100 s per session, roughly 1.7 hours for the three pilot participants) and rerun Stages 4 and 5 to see realistic pilot numbers.
2. Freeze `config.py` and the code, record file checksums, and post the pre-registration.
3. Only then run Stages 3 to 6 on the 20 confirmatory participants (about 400 sessions, roughly 11 to 12 hours on 4 cores).

## Limitations and what to do next

The code answers one question well and leaves several known gaps, listed here so they are not discovered in review.

- **BioSemi participants are excluded** because no `.bdf` file has been opened yet. Before the ltpFR2 replication (where 56 of 127 participants are BioSemi), open one `.bdf` session with Stage 1 and a modified Stage 3 and check channel names and `sample` alignment.
- **Motor activity in judgement lists.** People press keys while the word is on screen in size and animacy lists, and response times are not in the event files. A pre-specified robustness check is to rerun Stage 4 on no-task lists only (`task` = −1).
- **The pooled model shares words across people.** The personal model holds test words out; the pooled model cannot do so without discarding most of the pool. This is stated in `s06_pooled_model.py`.
- **Permutation null uses fixed penalties** chosen on the real labels, for speed. Without re-tuning on shuffled labels the null can be slightly too narrow, so per-person permutation p-values may be a little small. They are a sanity check only; the primary test does not use them.
- **Run time.** The model stage refits about 500 regressions per model per person; use `--jobs` equal to your CPU cores. The permutation null is the slowest part; `--perms 20` is enough while piloting.
- **No source localisation**: electrode positions in the dataset are a generic cap layout, as the README states.

**Next steps for you.**

- [ ] Install, run `pytest -q`, then Stages 0-2 (no EEG download).
- [ ] Run Stages 3-5 on the three pilot participants; read every output and log anything surprising.
- [ ] Freeze `config.py` and post the pre-registration (OSF or AsPredicted).
- [ ] Run Stages 3-6 on the 20 confirmatory participants and report the verdict exactly as `stats.decide` returns it.
