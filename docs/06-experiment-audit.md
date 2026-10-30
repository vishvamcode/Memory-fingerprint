# Experiment Audit: What the First Experiment Shows

Oct 21, 2026 · @Vishvam

**Bottom line: the experiment has no result yet, so it supports none of the three claims.** Only the three pilot participants have been run, and the decision rule correctly calls that "ambiguous". The audit found no leakage into the test data. It did find seven problems that could have produced a false positive or a corrupted result, and all are now fixed and tested (38 tests pass). The next step is the pre-registered run on the 20 confirmatory participants, with the new eye-channel and previous-word controls.

The pilot gives one warning. Two of three people show no EEG gain. In the third, about half the gain is matched by eye channels alone, and half by the previous word's EEG. That pattern points to artefact and general brain state, not a word-specific memory trace. Three people cannot settle this; the controls will on 20.

Code and outputs: `memory-fingerprint/` in the project files (pilot outputs in `pilot_check_full/`). Earlier documents: [build guide](https://claude.ai/artifact/KRdGVd6qLmWrNFxrT8dkN8), [dataset selection](https://claude.ai/artifact/XHQcG4RNtexgBJyMUp3BPx).

## What was actually run

The only data run so far are the three **pilot** participants (LTP063, LTP065, LTP066), each with all 20 sessions (4,410 to 4,704 words per person), using the corrected code. Pilot participants were chosen in advance to tune the pipeline and are excluded from the confirmatory test. Permutations (20) and bootstrap draws (1,000) were reduced for speed.

| Participant | Recall rate | Non-neural AUC | EEG-only AUC (perm. p) | ΔAUC combined | ΔAUC robust | ΔAUC EOG-only | Δ own word | Δ previous word |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LTP063 | 0.53 | 0.635 | 0.506 (0.14) | −0.001 | −0.001 | +0.000 | +0.000 | −0.001 |
| LTP065 | 0.50 | 0.694 | 0.543 (0.05) | 0.000 | +0.003 | −0.001 | +0.001 | 0.000 |
| LTP066 | 0.63 | 0.662 | 0.666 (0.05) | **+0.041** | +0.042 | **+0.022** | +0.044 | **+0.023** |

Δ = AUC of the stacked model minus the non-neural AUC. The last two columns use words at list position 2 or later. A permutation p of 0.05 is the smallest possible with 20 permutations.

With three people the decision rule returns **ambiguous** (mean ΔAUC +0.013, 95% CI −0.002 to +0.038; Wilcoxon p = 0.63). That is the correct output for n = 3; it says nothing about the hypothesis.

The pattern is still instructive for the confirmatory run. Two of the three people show no EEG gain at all. The one clear gain (LTP066) is **half matched by the eye channels alone and half matched by the previous word's EEG**. LTP066 also had the noisiest recordings (median 8 bad channels per session, up to 19). This is exactly the case the new controls were built to catch: without them, LTP066 would read as a strong personal memory signal.

## Audit: leakage, splits, baselines, confounds, overfitting, statistics

I read every stage of the code against the questions below. **Sound** means I found no problem. **Fixed** means I found a real problem and changed the code; the fix has a unit test, and the full suite (38 tests) passes. **Open** means it is a limitation the design cannot remove, and it limits how the result can be read.

### Data leakage and splits

| Check | Verdict | Detail |
| --- | --- | --- |
| Test session in training | Sound | Outer leave-one-session-out; a unit test asserts no overlap. |
| Same word in training and test | Sound | Every training trial whose `item_num` occurs in the test session is dropped. A test where the label depends only on word identity, and the features encode word identity, stays at chance. |
| Item hold-out in the **inner** folds | **Fixed** | The penalty search and the stacked model's out-of-fold EEG scores used folds grouped by session but **not** by word. Inside the training set, inner-test words could appear in inner training. This did not leak into the outer test session, but it could make the inner EEG scores look better than the test-session score, so the stacked model over-trusted EEG and the penalty was chosen on a leaky criterion. Inner folds now drop inner-test words from inner training too (`models.inner_splits`, new test). |
| Preprocessing that sees labels | Sound | Filtering, bad-channel detection, re-referencing, wavelets and within-session z-scoring never read the recall column. Z-scoring uses the test session's own mean and SD, which is label-free and is the same for every model. |
| Item recallability | Sound | Computed from other participants only; a unit test checks that the person's own recalls never enter it. |
| Prior exposures | Sound | Counts earlier presentations of the word to this person, ordered by session and onset; uses no outcome. |
| Recall label | Sound | Derived by matching `REC_WORD` (trial, item\_num) to `WORD` rows; checked against the raw file (list 1 of sub-LTP063 ses-0). Intrusions and repeats cannot create false positives. |

**Fixed: the channel layout was not the same in every session.** Running all pilot sessions showed two problems that 4 to 5 sessions per person had hidden. First, the eye channels are E8, E25, E126 and E127 in most sessions but E8, **E26**, E126 and E127 in some (sub-LTP063 ses-1, ses-5 and ses-8). Second, some EDF files name channels "EEG E1" and "EOG E126", with the reference called "Cz" rather than E129 (sub-LTP063 ses-8, sub-LTP065 ses-7). Features had been stacked by position, so in the affected sessions some columns held a different electrode, and the renamed files crashed the extraction. Channel names are now normalised ("EEG E12" becomes E12, Cz becomes E129, the reference electrode in this cap). Every session's features are placed in one fixed E1 to E129 order before modelling, and a missing channel is set to 0. Two unit tests cover this.

### Baselines

| Check | Verdict | Detail |
| --- | --- | --- |
| Joint model let EEG features swamp behaviour | Fixed earlier | Found on the pilot during Follow-up 2; replaced by a stacked model. |
| Time on task | **Fixed** | List number entered only as a straight line. Recall can fall off non-linearly within a session (fatigue), and slow EEG drift (gel drying, impedance) can follow the same curve, so EEG could have been credited with a baseline effect. The baseline now also has one indicator per list. |
| Session number | Open | Can only enter as a straight line, because the held-out session's own level is never seen. Between-session swings in recall that the line misses add noise to both models equally. |
| Interaction of task with serial position | Open | Not modelled. A small part of any EEG gain could be this interaction, which EEG reflects through the key press. The no-task-lists control below addresses it. |

### Confounds that could make EEG look like memory

| Check | Verdict | Detail |
| --- | --- | --- |
| Eye movements and blinks | **Fixed (control added)** | Blinks and saccades during the word predict poorer encoding and show up in frontal low-frequency and high-frequency scalp power. The robust model (no peripheral channels, ≤ 30 Hz) only partly removes them. Stage 3 now also saves the same features from the 4 EOG channels, and Stage 4 fits an **EOG-only stacked model**. If EOG alone gains as much as EEG, the EEG gain cannot be called neural. |
| Key presses in size and animacy lists | **Fixed (control added)** | Motor activity overlaps the 0.2-1.6 s window, and response times are not in the files. This check was pre-specified but not coded. Stage 4 now has `--no-task-lists`, which refits everything on no-task lists only. |
| Muscle activity above 30 Hz | Sound | Covered by the robust condition in the success rule. |
| Attention or arousal state | Open | Any EEG gain may reflect a general "ready to learn" state rather than anything about the word. The design cannot separate these; see the next section. |

### Overfitting and forking paths

| Check | Verdict | Detail |
| --- | --- | --- |
| Hyperparameters chosen on test data | Sound | Penalty chosen inside training folds only. |
| Design changed after seeing data | Open, manageable | The stacked model, the list indicators and the two controls were added after looking at **pilot** data only. The pilot participants are excluded from the confirmatory sample. This is allowed only if the changes are written into the pre-registration before the confirmatory run. |
| Many models, one hypothesis | Sound | The primary test is one comparison (combined vs non-neural); EEG-only, EOG-only and no-task-lists are controls, not extra chances to succeed. |

### Statistics

| Check | Verdict | Detail |
| --- | --- | --- |
| Recognition secondary used the wrong predictor | **Fixed** | It regressed strong recognition on the **combined** model's probability. That probability includes serial position and word recallability, which on their own predict recognition, so the test could have "succeeded" with no neural contribution. It now uses the EEG-only probability with the non-neural probability as a covariate. |
| Unit of analysis | Sound | Words within a person are not independent, so the group test is across people (Wilcoxon) and the CI resamples people, then sessions. |
| Mean versus median | Open, minor | Success needs mean ΔAUC ≥ 0.01, while the Wilcoxon test is about the median. Both are reported; they could disagree with one outlying participant. |
| Bootstrap does not refit models | Open, minor | The CI is conditional on the fitted models. Refitting 10,000 times is not affordable; this can make the CI slightly too narrow. |
| Permutation null with fixed penalty | Open, minor | Already stated in the build guide; used only as a per-person sanity check. |
| Personal versus pooled comparison | Open | The pooled model has more training data and can see the test person's words in other people; the personal model sees fewer trials and never sees the test words. The comparison is biased in opposite directions and should be read as descriptive only. |

## Which claim the design can support

Of the three claims, the experiment can only ever test memory-outcome prediction, and it has not tested even that yet. The other two are outside what it measures, whatever the result.

| Claim | What it would need | Does this design test it? | Status |
| --- | --- | --- | --- |
| **Stimulus decoding** (EEG tells which word was shown) | A model that predicts word identity or word features from EEG, tested on new presentations | No. No model ever predicts which word was shown; word identity is deliberately held out so it cannot help | Not tested |
| **Memory-outcome prediction** (EEG at study predicts later recall) | Held-out prediction of recall beyond a non-neural baseline | Yes. This is the primary hypothesis | Not yet tested: pilot only, which is a code check |
| **Encoding-to-retrieval generalisation** (the study pattern comes back at recall) | EEG recorded during recall, and a model trained on study EEG tested on recall EEG | No. Only study-period EEG is used; recall periods are never epoched | Not tested |

Even a confirmatory success would show something narrower than a "memory fingerprint". It would show that the state of a person's brain while a word is studied carries information about whether it will be recalled. It would not show that the signal is specific to that word or experience: a general attention or readiness state would produce the same result. That is the classic subsequent-memory effect, measured more strictly than usual (held-out days, held-out words, a strong baseline).

## Demonstrated findings versus interpretations

Only the left column has been shown. Everything in the right column is a reading of it that the data do not yet force.

| Demonstrated (checked on real files or by tests) | Interpretation (not yet shown) |
| --- | --- |
| The pipeline runs end to end on 60 real sessions, and every split holds out both the test day and the test words (unit tests) | That the confirmatory sample will behave like the pilot |
| Recall is predictable without EEG: held-out AUC 0.64 to 0.69 from serial position, list, task, exposure and word recallability | That this baseline captures every non-neural cause of recall; it is linear and leaves out, for example, task × position effects |
| In 2 of 3 pilot participants, EEG at study adds nothing measurable (ΔAUC between −0.001 and +0.003) | That scalp EEG carries no memory information for most people; three people cannot show that |
| In 1 of 3 (LTP066), EEG adds 0.041 AUC; eye channels alone add 0.022, and the previous word's EEG adds 0.023 | That the remaining part of LTP066's gain is neural, word-specific encoding. It could still be artefact or state that the controls only partly capture |
| The data have quirks that would have silently corrupted results: varying eye-channel sets and channel names between sessions | Whether other PEERS participants have further quirks; the confirmatory run will check every session against the fixed layout |
| None of the following were measured: decoding which word was shown, or study-to-recall pattern reinstatement | Anything about stimulus decoding or encoding-to-retrieval generalisation |

**What this means for the memory fingerprint idea today.** Nothing in the data supports or rules it out yet. The pilot does raise one warning worth taking seriously: where a gain appears, much of it can be explained by eye activity and slow brain state rather than by the word being learned.

## The next experiment, and what would falsify the hypothesis

**Recommendation: run the pre-registered confirmatory test on the 20 held-out participants, with one added comparison: the word's own EEG against the previous word's EEG.** Nothing else gives as much information for the cost. It is the first time the hypothesis meets data it was not tuned on, and the added comparison is the cheapest way to tell "this word is being encoded" apart from "the person is in a good state".

**How the added comparison works.** For every word at list position 2 or later, fit the stacked model twice on the same trials. One version uses the non-neural predictors plus the score from the word's own EEG. The other uses the non-neural predictors plus the score from the previous word's EEG, recorded about 4 seconds earlier in the same list. Slow states such as attention, arousal or fatigue barely change in 4 seconds, so they predict recall equally well from either word. Processing of this particular word shows up only in its own EEG. This is now coded in Stage 4 and summarised in Stage 5; it needs no new data.

**Run order.** Pre-register (design, IDs, thresholds, the four controls); run Stages 3 to 6 on LTP067 to LTP095 (about 400 sessions; roughly 12 to 15 hours on 4 cores); report the verdict exactly as `stats.decide` returns it.

### What would falsify the current hypothesis

The hypothesis is that EEG at study improves held-out recall prediction by at least 0.01 AUC beyond the non-neural model. These outcomes count against it, decided in advance:

| Outcome on the 20 confirmatory participants | Reading |
| --- | --- |
| 90% CI of mean ΔAUC entirely below 0.01 | **Falsified.** EEG adds less than the smallest useful amount. If the 95% CI also excludes 0, report "present but negligible". |
| ΔAUC CI excludes 0 but the robust version (≤ 30 Hz, no edge channels) does not | Not supported. The gain probably comes from muscle or eye artefacts. |
| EOG-only gain is as large as the EEG gain | Not supported as a neural effect. The gain is plausibly ocular. |
| Previous-word EEG gains as much as own-word EEG | The hypothesis survives as stated, but the personalised-signature idea does not: the signal is a brain state, not a trace of the item. |
| Gain present on all lists but absent on no-task lists | The gain is probably motor activity from the key press. |

Only the first row falsifies the hypothesis as written. The other rows leave the number intact but remove the reason it would matter for a memory fingerprint, so they should be reported with the same weight.
