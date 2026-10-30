# In-Brain Test: Pre-registration Addendum

Oct 23, 2026 · @Vishvam

## What this is

This is an addendum to the registered first experiment ([osf.io/9ghzn](https://osf.io/9ghzn)). It applies the same question, the same models and the same decision rule to a second, independent dataset: recordings from electrodes inside the brain (intracranial EEG). It is written after a practice run on 3 participants, which was used only to find and fix code problems, and before any of the 20 test participants' brain recordings have been downloaded or analysed. (Their event files, which contain only the word lists and which words were recalled, were used to apply the selection rule and to fit the non-neural model; no brain data were involved.)

**How to post it.** On your OSF project, add this text as a new registration or as a dated file in the project (for example "addendum-ieeg-2026-10-23.pdf"), together with the frozen code zip and its checksum file. Make it public before the test run starts.

## Question, hypothesis and data

**Question.** Does intracranial EEG recorded while a person studies a word improve the prediction of whether they will later recall it, beyond a non-neural model, for sessions and words the model has never seen?

**Hypothesis (same as the first experiment).** Per participant, ΔAUC = AUC(stacked combined model) − AUC(non-neural model) is at least 0.01 (the smallest effect of interest) on average across the 20 test participants.

**Motivation.** The scalp EEG experiment ended in "failure, present but negligible" (mean ΔAUC 0.005). This addendum tests whether the gain becomes meaningful with sensors inside the brain.

**Data.** OpenNeuro ds004789, version 3.1.0 (doi:10.18112/openneuro.ds004789.v3.1.0), "Delayed Free Recall of Word Lists", licence CC0, task FR1, the `acq-bipolar` recordings. Each full session has 25 lists of 12 words (300 words), an arithmetic distractor, and free recall. Recall labels are derived by matching `REC_WORD` events to words studied in the same list, as the files have no recall column.

**Selection rule.** Eligible: at least 3 FR1 sessions that each have an events file passing the schema checks and a bipolar EDF, and mean recall strictly between 0.15 and 0.85. The eligible IDs, sorted, are shuffled with seed 20261023; the first 3 are the practice sample and the next 20 the test sample. Applied on 23 Oct 2026: 553 FR1 event files, 523 sessions with a bipolar EDF, 5 sessions failing the schema check (a word shown twice), **60 eligible participants**.

- **Practice:** R1066P, R1168T, R1108J
- **Test:** R1077T, R1068J, R1311T, R1123C, R1151E, R1334T, R1111M, R1292E, R1377M, R1145J, R1222M, R1121M, R1158T, R1350D, R1217T, R1243T, R1345D, R1060M, R1125T, R1391T

## What stays the same, and what changes

**Unchanged from the registered experiment:** the 8 frequencies (3 to 128 Hz, log-spaced Morlet wavelets), the 0.2 to 1.6 s feature window after word onset, within-session z-scoring, the non-neural model and its predictors (serial position, list number and list indicators, session number, prior exposures, word length, item recallability from other participants), L2 logistic regression with the same penalty grid, the stacked combined model, the 200-permutation null, the neighbour test, the hierarchical bootstrap and the decision rule.

| Change | Reason |
| --- | --- |
| **Split: one session × one word group held out.** Words are divided into 4 fixed groups (seeded). The test set is one session × one group; training uses other sessions and other groups only. Inner folds follow the same rule. | Every FR1 session shows the same 300 words, so holding out a session and removing its words from training would leave no training data. This keeps the registered principle: no test word and no test session in training. |
| **Channels:** each person's bipolar channels that are present in all of their sessions; no fixed layout and no average reference. | Electrodes differ between people; bipolar recordings are already re-referenced (dataset README). |
| **Robust model:** frequencies up to 30 Hz only. | There are no face or neck channels to remove. |
| **Not possible here:** the eye-channel control, the no-task-list refit, the recognition analysis, and the personal-vs-pooled comparison. | No EOG channels; FR1 has no encoding task and no recognition test; electrode positions differ between people. |
| **Sampling-rate check:** a session is skipped if its Nyquist frequency is not above 128 Hz. | The highest analysis frequency must be measurable. |
| **Timing:** epochs use the `sample` column, checked to lie inside the recording and to agree with `onset` within 1 s. | Verified on sub-R1001P ses-0: `onset` is offset from the recording and drifts by up to 0.2 s; word-locked evoked responses are larger with `sample`. |
| **Inner folds smaller than 20 words are not used for penalty tuning** (they still provide out-of-fold scores for the stacked model). | Found in the practice run: short sessions (11 lists) made folds of about 10 words, sometimes with no recalled word, so their AUC was undefined. |
| **Feature extraction in chunks of 16 channels.** | A practice extraction ran out of memory. The computed values are identical. |

## Decision rule, controls and skip rules

**Decision rule (unchanged, implemented in `stats.decide`).** Hierarchical bootstrap of mean ΔAUC (participants, then sessions within participants; 10,000 draws; seed 20261021).

- **Success** if all hold: one-sided Wilcoxon signed-rank p < .05 for ΔAUC > 0; 95% CI lower bound > 0; mean ΔAUC ≥ 0.01; and the robust model's 95% CI lower bound > 0.
- **Failure** if the 90% CI of mean ΔAUC lies entirely below 0.01. Labelled "present but negligible" if the 95% CI also excludes 0.
- **Ambiguous** otherwise.

**Controls and descriptive results (no change to the verdict).** Permutation null for the brain-only model (200 label shuffles within session × serial position); neighbour test (own word's vs previous word's brain signal, serial position ≥ 2), compared with a one-sided Wilcoxon test; brain-only AUCs reported next to the scalp EEG experiment's 0.53 to 0.61.

**Skip rules.** A session is skipped and logged if: the events file fails the schema checks; any file is missing or unreadable; the timing check fails; an epoch falls outside the recording; or the sampling rate is too low. A participant left with fewer than 3 usable sessions is replaced by the next ID in the same shuffled order (reserves, in order: R1067P, R1092J, R1309M, R1147P, R1195E). Every skip and replacement will be listed next to the result.

**Practice run (3 participants, code checks only, not evidence).** It found three code problems, all fixed before this addendum: undefined tuning folds in short sessions, missing out-of-fold scores after that fix, and an out-of-memory crash. Its numbers are not part of the test and are not reported as results.

**Frozen code (23 Oct 2026).** `memory-fingerprint-ieeg-frozen-2026-10-23.zip` with `FROZEN_SHA256.txt` (SHA-256 of 24 files; SHA-256 of the list itself: 373dd7380ef316380bd6064446f1d86b6ab6376c502476f7dce7aa5b40e6b700). All 35 automatic tests pass. Any change after freezing will be reported next to the frozen result.
