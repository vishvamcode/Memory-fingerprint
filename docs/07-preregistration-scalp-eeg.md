# Pre-registration: EEG at Study Predicts Later Recall

Oct 22, 2026 · @Vishvam

## How to post this

The text below is ready to paste. Before posting, read it once and change anything that is not how you want to commit.

1. Go to [OSF Registries](https://osf.io/registries) and choose the template **"Preregistration of secondary data analysis"** (it is meant for analyses of data that already exist). [AsPredicted](https://aspredicted.org) also works but has short fixed questions, so the sections below would need cutting.
2. Paste each section below into the matching template field. Name yourself as author.
3. Attach two files from the project files: `memory-fingerprint/FROZEN_SHA256.txt` (checksums of the 16 code files as frozen today) and `the zip of the frozen code, memory-fingerprint-frozen-2026-10-22.zip (also in the project files)`. The checksum list itself has the SHA-256 `a8061d0731c009acd90a4c0ef5c11d79e4e5c120c5cf61daf227849fc9389ce0`.
4. Register (not just save a draft), then send me the link. I will not start the confirmatory run before that.

## Hypothesis and data

**Hypothesis.** Within a person, scalp EEG recorded while a word is studied improves held-out prediction of whether that word is later freely recalled, beyond a non-neural model, by at least 0.01 AUC on average.

**Data.** Penn Electrophysiology of Encoding and Retrieval Study (PEERS), experiment ltpFR, OpenNeuro ds004395 version 2.0.0 (doi:10.18112/openneuro.ds004395.v2.0.0), CC0. These are existing public data; no new data are collected.

**Prior contact with the data.** All ltpFR event files (behaviour only) were read to apply the selection rule and to compute word recallability. EEG files have been opened for the 3 pilot participants only (LTP063, LTP065, LTP066), all 20 sessions each, to build and check the pipeline. No EEG from any confirmatory participant has been opened. The pilot results are reported in the project's audit document and are not part of the confirmatory test.

## Sample

**Selection rule.** ltpFR participants recorded with EGI (`.edf` files), with at least 12 sessions and mean session recall strictly between 0.15 and 0.85. 149 participants meet it. In ascending ID order, the first 3 are the pilot and the next 20 are the confirmatory sample.

**Confirmatory sample (fixed):** LTP067, LTP069, LTP070, LTP073, LTP077, LTP079, LTP081, LTP082, LTP084, LTP085, LTP086, LTP087, LTP088, LTP089, LTP090, LTP091, LTP092, LTP093, LTP094, LTP095.

**Sample size.** 20 was set by computing cost (about 400 sessions), not by a formal power analysis. Three pilot participants are too few to estimate the spread of the effect. The equivalence rule below means a clear null is still an informative outcome.

**No replacement.** A participant is not swapped out for another. If a participant's data cannot be processed, they are reported as missing and the test runs on the rest.

## Variables, preprocessing and models

**Trials.** Every `WORD` event with `trial` ≥ 1 (practice lists excluded).

**Outcome.** 1 if the word's (`trial`, `item_num`) appears among `REC_WORD` events of the same session, else 0. The files have no recall column; this derivation is unit-tested against a real session.

**Non-neural predictors.** Serial position (one indicator per position); encoding task (`task` = −1 none, 0 size, 1 animacy; one indicator each); list number (linear, plus one indicator per list); session number (linear); number of earlier presentations of the word to this person; word length; word recallability = the word's recall rate across all other ltpFR participants, shrunk toward their mean with 5 pseudo-observations.

**EEG preprocessing (never sees the outcome).** Channel names normalised ("EEG E12" → E12, Cz → E129) and channel types taken from `channels.tsv`. Notch filter at 60, 120 and 180 Hz; high-pass 0.5 Hz. Bad channels: robust z of log-variance above 5, set to 0 after z-scoring. Average reference without bad channels. No ICA.

**EEG features.** Morlet power at 8 log-spaced frequencies (3.0, 5.1, 8.8, 15.0, 25.6, 43.8, 74.9, 128 Hz; cycles = frequency/2, at least 3), averaged 0.2 to 1.6 s after word onset, log-transformed and z-scored within session. Stored in a fixed E1 to E129 channel order; EOG channels and absent channels are 0 in the EEG set. The 4 EOG channels get the same features separately.

**Models (per participant).** All are L2 logistic regression with balanced class weights after standardisation, the penalty chosen from 10⁻⁴ to 1 (5 values) by inner cross-validation.

- *Non-neural:* non-neural predictors only.
- *EEG-only:* EEG features only.
- *Combined (primary):* stacked. Within the training sessions, out-of-fold EEG-only scores are computed; a logistic regression (C = 1) is fitted on the non-neural predictors plus the logit of that score. For the test session, the EEG model refitted on all training sessions supplies the score.
- *Robust combined:* as combined, but the EEG model uses only frequencies ≤ 30 Hz and drops the 25% of channels lowest on the head (z coordinate in `electrodes.tsv`).

## Validation, primary test and decision rules

**Validation.** Outer leave-one-session-out within each participant. For each test session, every training trial whose `item_num` appears in the test session is removed. Inner folds (penalty choice and stacking) use 5 session-grouped folds with the same word removal. Every trial is predicted once, by a model that saw neither that session nor that word.

**Outcome measure.** Per participant, AUC of the held-out probabilities pooled over sessions. ΔAUC = AUC(combined) − AUC(non-neural); ΔAUC robust uses the robust combined model.

**Primary test.** One-sided Wilcoxon signed-rank test of ΔAUC > 0 across the 20 participants, α = 0.05. Confidence intervals come from a hierarchical bootstrap (resample participants, then sessions within each; 10,000 draws; seed 20261021).

**Decision rules (applied by `stats.decide`, reported exactly as returned).**

| Verdict | Condition |
| --- | --- |
| Success | Wilcoxon p < 0.05, **and** 95% CI lower bound of mean ΔAUC > 0, **and** mean ΔAUC ≥ 0.01, **and** 95% CI lower bound of mean robust ΔAUC > 0 |
| Failure | 90% CI of mean ΔAUC lies entirely below 0.01. Flagged "present but negligible" if the 95% CI also excludes 0 |
| Ambiguous | Anything else |

The smallest effect of interest (0.01 AUC) was fixed on 21 October 2026, before any EEG was analysed.

## Controls, secondary analyses and exclusions

None of these can turn a non-success into a success. They decide how a success is interpreted, and all are reported whatever they show.

| Analysis | Comparison | Reading |
| --- | --- | --- |
| Eye-channel control | ΔAUC of a stacked model using only the 4 EOG channels' features | If mean EOG ΔAUC is at least the EEG ΔAUC, the EEG gain is not interpreted as neural |
| Previous-word control | On words at list position ≥ 2: stacked model with the word's own EEG vs with the previous word's EEG (same list), each against the non-neural model | Own minus previous tested one-sided (Wilcoxon). Equal gains are read as a slow brain state, not word-specific encoding |
| No-task lists | All models refitted on lists with `task` = −1 only | A gain that appears only in judgement lists is read as motor activity |
| Secondary 1: personal vs pooled | EEG-only AUC of the personal model vs a model trained on the other 19 participants | Two-sided Wilcoxon. Descriptive only: the two models differ in data size and word overlap |
| Secondary 2: memory strength | Among unrecalled words tested for recognition, does the EEG-only probability predict "old" with confidence 5, adjusting for the non-neural probability? | One logistic slope per person; one-sided Wilcoxon |

The two secondary p-values are Holm-corrected as a family. Per-person permutation tests (200 shuffles within session × serial position) are sanity checks only.

**Exclusions.** No trials are excluded for artefacts; bad channels are handled as above. A session is skipped only if its EEG file is not `.edf`, its `sample` column disagrees with `onset` × sampling rate by more than 1 sample, or a word falls too close to the file edge for a full epoch. Every skipped session is listed in the report.

## Changes made after the pilot, and code freeze

The design in the project's dataset selection document (21 October 2026) was changed after looking at **pilot data only**. Each change is listed with its reason.

| Change | Reason |
| --- | --- |
| Combined model stacked instead of one joint regression | With one shared penalty over about 1,000 EEG features, the joint model scored below the non-neural model alone |
| Inner folds also remove test words | Code audit: the inner folds could see the same word in training and checking |
| One indicator per list added to the baseline | Code audit: a non-linear fatigue curve could otherwise be credited to slow EEG drift |
| Recognition analysis uses EEG-only probability, adjusted for the non-neural one | Code audit: the combined probability alone lets non-neural predictors produce the effect |
| Eye-channel and previous-word controls; no-task-lists analysis coded | Audit: rule out ocular artefacts, slow brain state and key presses |
| Fixed E1 to E129 channel layout and name normalisation | Full pilot run: eye channels and channel names differ between sessions |

**Code freeze.** The analysis code is frozen as of 22 October 2026. SHA-256 checksums of all 16 code files are in the attached `FROZEN_SHA256.txt`. Any later change to the code or settings will be reported next to the result from the frozen code.
