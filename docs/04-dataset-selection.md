# Dataset Selection: First Memory Experiment

Oct 21, 2026 · @Vishvam

**Decision: start with PEERS ltpFR (OpenNeuro ds004395), replicate on the PEERS ltpFR2 participants, and validate externally on RAM FR1 intracranial recordings (OpenNeuro ds004789).** All three are CC0, need no registration, and were checked file by file on 21 Oct 2026. The single hypothesis to test first: *within a person, scalp EEG recorded while a word is studied improves held-out prediction of whether that word is later recalled, beyond a non-neural model of the word, its list position, the encoding task and prior exposure, by at least 0.01 AUC.*

This document extends Sections 9-10 of the [research report](https://claude.ai/artifact/MA1xcVnxzcqpLzUePKmddj) with what was found by opening the actual files. No new data collection and no equipment are needed.

## Candidates compared on verified facts

Only PEERS combines non-invasive EEG, a later-memory label on every studied item, many sessions per person, and open access. "How verified" says what was actually opened.

| Dataset | Modality | Usable participants | Memory outcome per item | Sessions per person | Size | Access | How verified | Laptop? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **PEERS ltpFR** (ds004395) | Scalp EEG, EGI 129-ch (231) or BioSemi 128-ch (9) | 237 total; 149 with ≥ 12 sessions and mean recall 15-85% | Free recall (derived), final free recall, recognition with 1-5 confidence | Median 20 | 2.3 TB total; 0.5-0.7 GB per session | CC0, no login | All 3,583 event files downloaded and parsed; one EEG file loaded and processed | Yes, one session at a time |
| **PEERS ltpFR2** (same archive) | Scalp EEG, EGI (71) or BioSemi (56) | 127 total; 96 eligible by the same rule | Delayed free recall (derived) | Median 24 | 5.5 TB total | CC0, no login | All 2,441 event files parsed | Yes, slower (576 words per session) |
| **RAM FR1** (ds004789) | Intracranial EEG, monopolar and bipolar EDF | 281 | Delayed free recall (derived from `REC_WORD`) | Usually 1-4 | 619 GB total; about 0.2-0.4 GB per session file | CC0, no login | Dataset description, README and one events file opened | Yes |
| **DANDI:000004** (Chandravadia et al., 2020) | MTL single units (NWB) | 59 subjects, 87 files | New/old recognition with confidence; learning-phase category judgement | 1-2 | 6.2 GB | Open | One 55 MB NWB file opened: 33 units, 150 trials (50 learn, 100 recognition) | Yes, easily |
| **Natural Scenes Dataset** | 7T fMRI | 8 | Continuous recognition: `ISOLD`, `ISCORRECT`, `MEMORYRECENT`, `MEMORYFIRST` per trial | 30-40 | Very large | Public S3 bucket; terms and conditions plus access form for the manual | Bucket listed; `responses.tsv` header read for subj01 | Partly (betas only) |
| **THINGS-EEG** (ds003825) | Scalp EEG, 64-ch | 50 | None (fixation task) | 1 | 59 GB | CC0 | Description and README | Yes |
| **Wakeman-Henson** (ds000117) | MEG + EEG + fMRI | 16 | Repetition only (no memory test) | 1 MEG | 90 GB | CC0 | README | Yes |
| **Audiovisual memory EEG** (ds006142) | Scalp EEG, 64-ch | 27 | Recognition of film clips seen outside the lab | 1 | 26 GB | OpenNeuro; videos not shared | Paper and file listing | Yes |
| **Movie recall fMRI** (ds004042) | 3T fMRI | 20 | Spoken recall of films (event level) | 1 | Not measured | OpenNeuro | Paper | Partly |

**What disqualifies the others as the primary dataset.** THINGS-EEG and Wakeman-Henson have no later-memory outcome. NSD is the best image-memory resource but is recognition-only, has 8 people, and is heavy. DANDI:000004 and RAM come from epilepsy patients with clinically placed electrodes, so they cannot support claims about a non-invasive system; they are excellent validation sets. The audiovisual EEG set has no controlled encoding phase.

## What was checked in the real PEERS files

Everything the hypothesis needs exists in the files, but the recall label must be derived and the two PEERS experiments use different column layouts.

| Check | Result | Consequence |
| --- | --- | --- |
| Access | Plain HTTPS from `https://s3.amazonaws.com/openneuro.org/ds004395/...` works with no account; version 2.0.0, CC0 | Download scripts need no credentials |
| Size | 62,640 files, 9.6 TB in total; ltpFR EEG 2.3 TB across 3,583 sessions | Stream one session at a time; keep only features |
| Event file layouts | Four layouts. ltpFR files have a `task` column (some also have `answer`, `test_x/y/z` from the maths distractor). ltpFR2 files have `list` and no `task`. One file has a minimal layout | Code must read columns by name and check which exist, never by position |
| Recall label | No `recalled` column. Derived by matching each `WORD` (`trial`, `item_num`) to `REC_WORD` rows in the same session | Label derivation is a tested function, not a column lookup |
| Encoding tasks (ltpFR) | `task` = −1 (no task), 0 (size), 1 (animacy). Example participant: 64 / 96 / 96 words per 16-list session | Task enters the non-neural model |
| Lists and words | ltpFR median 16 lists × 16 words = 256 words per session; ltpFR2 median 24 × 24 = 576. No duplicate `item_num` within any session; no missing or negative `item_num` on study words | Items repeat across sessions only, so item hold-out is by session |
| Mean recall | ltpFR 0.594, ltpFR2 0.495 (mean over sessions) | Classes are reasonably balanced |
| Recognition | Every `RECOG_TARGET` item is a word studied in the same session (100% across all ltpFR sessions) | Recognition outcomes can be linked to encoding trials |
| Timing | For sub-LTP063 ses-0, `sample` equals `onset` × 500 Hz to within 10⁻¹⁰ s, and all samples lie inside the EEG record | Epochs can use the `sample` column directly |
| EEG file | EDF, 129 channels (`E1`-`E129`), 125 EEG + 4 EOG (`E8`, `E25`, `E126`, `E127`), 500 Hz, Cz reference, 60 Hz mains, 5,206 s long, no embedded annotations | Channel types must be set from `channels.tsv` |
| Compute | Loading, notch and high-pass filtering, re-referencing, epoching 256 words and Morlet power at 8 frequencies took 83 s on 4 CPU cores | 20 participants × 20 sessions is about 9-10 hours of computing plus download |
| Download speed | One 672 MB EDF downloaded in 27 s from this test machine | Home connections will be slower; plan overnight batches |

**Not yet checked:** BioSemi `.bdf` sessions (9 ltpFR participants) and whether their `sample` column uses the same convention. The selection rule can exclude BioSemi participants from the first run to remove this risk, at the cost of 9 people.

## Why PEERS ltpFR, and the validation datasets

ltpFR is preferred over ltpFR2 as the primary set because it has the encoding-task manipulation and the recognition test, it is less than half the size, and the closest published decoder study (Li, Pazdera & Kahana, 2024) used ltpFR2, so ltpFR gives a fresh test rather than a re-run.

| Criterion | PEERS ltpFR | Why it matters |
| --- | --- | --- |
| Relevance to memory | Every studied word has a later recall outcome; recognition with confidence for a subset | Tests H2, H3, part of H5 |
| Clear labels | Derivable exactly from event files; checked across all sessions | Avoids hand-coded labels |
| Data quality | Research-grade 129-ch EEG, highly practised participants | Fewer behavioural confounds |
| Reproducibility | CC0, versioned DOI, BIDS | Others can rerun everything |
| Accessibility | No login, no agreement | Start today |
| Computing | About 80 s per session on 4 cores | Laptop-scale |
| Individual feasibility | One person can run 20 participants in a week | Fits the 8-week plan |
| Original analysis | Non-neural comparison model, held-out items, personal vs pooled, recognition | Adds something to the literature |

**Validation, in order.**

1. **PEERS ltpFR2** (internal replication): new participants, longer lists, delayed recall, half recorded on BioSemi. Same frozen code, adapted only for the column layout.
2. **RAM FR1, ds004789** (external validation): same task family with intracranial electrodes. Shows whether better signal raises ΔAUC, which tells you whether a negative scalp result is a sensor limit or a real absence of information.
3. **DANDI:000004** (optional side project): tests whether single neurons separate later-recognised from forgotten images, the closest open analogue of an item-level signature.

**If ltpFR proves too heavy on your machine:** run the pilot on the 3 smallest eligible participants, or limit each participant to the first 12 sessions. Both are fixed rules that keep the analysis honest.

## The falsifiable hypothesis, fully specified

**H-primary.** For participants in PEERS ltpFR, the mean per-participant difference in held-out AUC between a combined model (non-neural predictors + EEG) and the non-neural model alone is at least 0.01, with a 95% bootstrap CI above 0.

| Element | Specification |
| --- | --- |
| Eligible participants | ltpFR, EGI recordings (`.edf`), ≥ 12 sessions, mean session recall between 0.15 and 0.85: **149 people** |
| Pilot (used to fix all settings) | First 3 eligible IDs: LTP063, LTP065, LTP066 |
| Confirmatory sample | Next 20 eligible IDs: LTP067, LTP069, LTP070, LTP073, LTP077, LTP079, LTP081, LTP082, LTP084, LTP085, LTP086, LTP087, LTP088, LTP089, LTP090, LTP091, LTP092, LTP093, LTP094, LTP095 |
| Trials | `WORD` rows with `trial` ≥ 1 |
| Outcome | 1 if the word's (`trial`, `item_num`) appears among `REC_WORD` rows in the same session, else 0 |
| Non-neural predictors | Serial position within list (1-16, one-hot); `task` (−1/0/1, one-hot); list number; session number; prior exposures of this `item_num` to this person; word length of `item_name`; item recallability from other participants |
| EEG predictors | Log Morlet power at 8 frequencies (3.0, 5.1, 8.8, 15.0, 25.6, 43.8, 74.9, 128 Hz) × 125 EEG channels, averaged 0.2-1.6 s after onset, z-scored within session |
| Model | L2 logistic regression, balanced class weights, penalty chosen by inner 5-fold cross-validation grouped by session. The combined model is stacked: the EEG model's out-of-fold score (computed within the training sessions) enters a small logistic regression next to the non-neural predictors. This replaced a single joint model after the pilot showed that one shared penalty over 1,024 features suppressed the non-neural predictors; no confirmatory data had been opened. |
| Split | Outer leave-one-session-out; training trials whose `item_num` occurs in the test session are removed |
| Metric | AUC on held-out sessions, pooled within participant; ΔAUC = combined − non-neural |
| Test | One-sided Wilcoxon signed-rank across 20 participants, α = 0.05; hierarchical bootstrap 95% CI; 200 within-stratum permutations per participant as a sanity null |
| Success | p < 0.05, CI lower bound > 0, mean ΔAUC ≥ 0.01, and the CI still excludes 0 when only ≤ 30 Hz power and non-peripheral channels are used |
| Failure | 90% CI for mean ΔAUC entirely below 0.01 (equivalence); flagged "present but negligible" if the 95% CI also excludes 0 |
| Ambiguous | Anything else; report it as such and extend by the next eligible IDs only if this extension is pre-registered |

The 0.01 threshold, the frequencies, the time window and the sample were fixed here, before any EEG from the confirmatory participants has been opened. Behavioural files of all participants were parsed to apply the selection rule; that is allowed because the rule uses only session counts and recall rates.

## What the result would establish about the original idea

A success shows that a person-specific, non-invasive signal at the moment of learning carries memory information that behaviour and stimulus do not, and that this information survives a change of day and of words. That is the minimum a PNMS needs before it is worth building anything on top of it.

| Outcome | Says about the PNMS idea | Does not say | Next step |
| --- | --- | --- | --- |
| Success | H2 and H3 hold on scalp EEG at a useful size; a personal model carries information across sessions (partial H5) | That the information is item content rather than an attention or state signal; anything about H4, H6-H8 | Replicate on ltpFR2 and RAM; then test item-specific content (same word across sessions) and reinstatement during recall |
| Failure (equivalence) | Scalp EEG at encoding adds no useful memory information beyond a non-neural model | That memory is unreadable in principle; intracranial signals may still carry it | Run the same test on RAM FR1; build Architecture B on behavioural models |
| Ambiguous: effect only with high frequencies at peripheral channels | The decoder is probably reading muscle or eye activity | — | Add EOG regression and a stricter artefact pipeline; treat as unresolved |
| Failure, flagged present but negligible | Information exists but is too small to use | — | Look for larger effects with better sensors before any application |

Whatever the outcome, it is a publishable, citable answer, because the question was fixed before the data were analysed.

## Known data quirks and risks

- **Stray values:** some `WORD` rows carry a `recog_resp` value (for example one row in sub-LTP063 ses-0) although that column belongs to the recognition phase. Only the listed columns may enter models.
- **Practice lists:** `trial` ≤ 0 marks practice; these rows are excluded.
- **Sessions with fewer lists:** some sessions have 12-14 lists instead of 16; list number enters the non-neural model.
- **Judgement responses during the window:** in size/animacy lists people press a key while the word is on screen, so motor activity overlaps the 0.2-1.6 s window. Response times are not in the event files. Task is controlled; a no-task-lists-only analysis is a pre-specified robustness check.
- **Item repetition across sessions:** each person sees words from a 1,638-word pool several times over 20 sessions, which is why test-session words are removed from training.
- **Generic electrode positions:** the README states positions are a generic cap layout, not measured per person. Do not do source localisation on these files.
- **Two missing downloads** occurred during bulk fetching and succeeded on retry; scripts must retry and verify file sizes.
- **High-frequency artefacts:** scalp power above about 30 Hz can reflect muscle and miniature eye movements, hence the artefact-robust success condition.

## Sources

Opened or listed on 21 Oct 2026:

- PEERS, OpenNeuro ds004395 v2.0.0: [dataset page](https://openneuro.org/datasets/ds004395), files read from `https://s3.amazonaws.com/openneuro.org/ds004395/` (README, CHANGES, participants.tsv, dataset\_description.json, all event files, one EDF).
- RAM FR1, OpenNeuro ds004789: [dataset page](https://openneuro.org/datasets/ds004789); README and sub-R1001P events read.
- DANDI:000004 version 0.220126.1852: [dataset page](https://dandiarchive.org/dandiset/000004/0.220126.1852); metadata and one NWB file read.
- Natural Scenes Dataset: [AWS registry](https://registry.opendata.aws/nsd); bucket listing and subj01 `responses.tsv` header read.
- THINGS-EEG ds003825, Wakeman-Henson ds000117, ds006142, ds004042: descriptions and file listings.
- [Li, Pazdera & Kahana (2024), *Nat Commun* 15:2981](https://doi.org/10.1038/s41467-024-46926-0).
- [Long, Burke & Kahana (2014), *NeuroImage* 84](https://doi.org/10.1016/j.neuroimage.2013.08.052).
- [Chandravadia et al. (2020), *Sci Data*](https://doi.org/10.1038/s41597-020-0415-9).
