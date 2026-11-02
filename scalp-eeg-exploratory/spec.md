# spec.md: Exploratory bridge analyses for the scalp EEG project (E1, E2, E5)

Written 2 Nov 2026 (Run 2, deliverable D8). This file tells Claude Code what to build.
It is a plan, not results. Read all of it before writing code.

## 0. Status, and the rules that follow from it

- The confirmatory analysis is **finished and locked**. It was pre-registered at
  osf.io/9ghzn on 22 Oct 2026 and run on 23 Oct 2026. The frozen-rule verdict was
  **failure, present but negligible** (mean ΔAUC 0.005, 95% CI 0.002 to 0.009).
- **Never edit anything under `scalp-eeg/`.** That is the frozen code (checksums in
  `scalp-eeg/FROZEN_SHA256.txt`). This work lives in `scalp-eeg-exploratory/` and
  imports the frozen package read-only.
- Everything here is **exploratory**. No result from this folder may be described as
  confirmatory, and none of it changes the registered verdict.
- **Order of operations (do not skip a step):**
  1. Post the exploratory addendum (Run 2 page, D7) on OSF as a dated, public file
     **before** step 3. Record its URL in `config.py` as `ADDENDUM_URL`.
  2. Build and test the code on the **pilot** participants only (LTP063, LTP065, LTP066).
  3. Freeze: write `FROZEN_SHA256.txt` for this folder, commit, tag `exploratory-freeze-1`.
  4. Run on the 20 confirmatory participants (their confirmatory results are already
     public, so this sample is "unblinded"; that is why this stage is exploratory).
  5. Only if an exploratory effect looks worth confirming: write a new pre-registration
     for a **fresh** sample (section 7) before touching that sample's EEG.

## 1. Inspect before you build (never assume a schema)

Run these checks and save their printout to `reports/inspection.md` before writing any
analysis code. Stop and report to the user if any check fails.

| Check | How | Expected (seen in fixture `sub-LTP063_ses-0_task-ltpFR_events.tsv`; confirm on every pilot session) |
| --- | --- | --- |
| Event columns | read the header of each `events.tsv` | `onset duration trial_type sample stim_file subject experiment session trial task item_name item_num recog_resp recog_conf resp ...` |
| Event types | `value_counts()` of `trial_type` | `WORD`, `REC_START`, `REC_WORD`, `RECOG_TARGET`, `RECOG_LURE`, `RECOG_RESP`, `RECOG_CONF`, `FFR_REC_WORD`, `*_VV` variants |
| Word timing | differences of `WORD` onsets inside a list | about 4.0 s (3.8 to 4.2 s in the fixture); `duration` is `n/a`, so word **offset is not in the file**: do not assume a display duration |
| Recognition test | `RECOG_TARGET` rows: is every `item_num` a studied `WORD` of the same session? | fixture: 160 of 160 targets are studied words |
| Recognition EEG inside the recording | for every `RECOG_TARGET`, `sample + 1.6 × sfreq` < number of samples in the EDF | must hold; otherwise list and skip that trial |
| Sampling rate and sample/onset agreement | `raw.info['sfreq']`; `sample` vs `onset × sfreq` | fixture: 500 Hz, agreement within 1 sample |
| Sessions with recognition | count `RECOG_TARGET` per session | report the count per session; E5 uses only sessions that have them |
| Duplicate event samples | `sample` duplicates among the epoched events | the frozen run skipped 5 sessions for this; apply the same skip rule and list them |

## 2. Data handling and compute

- Data: OpenNeuro ds004395 v2.0.0 via `pnms.download` (S3, no login). Reuse the frozen
  `pnms.events`, `pnms.behaviour`, `pnms.eeg_features.load_raw` and `preprocess`. Do
  not reimplement them.
- The frozen run's per-trial held-out predictions (`derivatives/models/*_heldout.npz`)
  did not survive the old container. Stage X0 below regenerates them with the frozen
  `s04_fit_models.py`, unchanged, and checks that every participant's AUCs match
  `scalp-eeg/confirmatory/models/*_results.json` to 4 decimals. If they do not match,
  stop and report.
- **One pass per session**: download the EDF once, compute everything E1 and E5 need,
  save small `.npz` files, delete the EDF. Budget: about 400 sessions, roughly 0.6 GB
  and 2 to 3 minutes each on 4 cores, so about 15 to 20 hours. Make every stage
  restartable (skip sessions whose output exists).
- Cloud containers can be reclaimed when idle. Keep a foreground, harness-tracked job
  alive while long runs go, or run on the user's own machine.

## 3. Stages

| Stage | Script | Input | Output |
| --- | --- | --- | --- |
| X0 | `x0_regenerate_heldout.py` | frozen features (re-extracted with frozen `s03`) | `derivatives/models/sub-*_heldout.npz`, `reports/x0_match.md` |
| X1 | `x1_extract_session.py SUB` | EDF + events | `derivatives/x/sub-SUB/ses-N.npz` with arrays listed below |
| X2 | `x2_e1_online.py` | X1 + behaviour tables | `results/e1_*.json`, figures F-E1a/b |
| X3 | `x3_e2_policy.py` | X0 held-out predictions | `results/e2_*.json`, figures F-E2a/b |
| X4 | `x4_e5_reinstatement.py` | X1 | `results/e5_*.json`, figures F-E5a/b |
| X5 | `x5_report.py` | all results | `reports/exploratory_report.md` |

X1 saves per session: `power_causal` (words × channels × 8 freqs × T end-times),
`power_recog` (recognition targets × channels × 8 freqs, window 0.2 to 1.6 s after the
`RECOG_TARGET` onset, same preprocessing and z-scoring as encoding), item numbers,
list numbers, serial positions, and the skip log.

## 4. Analyses

### E1. Pseudo-online decoding (bridge to closed loop)

- **Question.** How early after word onset, using only data recorded up to that moment,
  can EEG predict later recall? Could a real-time system act within the ~4 s before the
  next word?
- **Causal features.** For end-times t = 0.0, 0.1, ..., 1.6 s after word onset, and one
  pre-stimulus window ending at t = 0 (state before the word), compute log power at the
  8 registered frequencies from a window [t − w, t] only, where w = max(0.5 s,
  3 cycles of the frequency). Use a one-sided (causal) estimate: multitaper or Welch
  power on that window, never a centred wavelet whose support extends past t.
  Same channel set, bad-channel rule and within-session z-score as the frozen code,
  except that the z-score uses training sessions' mean and SD only (a real-time system
  cannot see the test session's statistics).
- **Model.** Same EEG-only and stacked combined models, same leave-one-session-out with
  test-word removal, same penalty grid. Fit one model per end-time t.
- **Outputs.** Per participant and t: EEG-only AUC, ΔAUC over the non-neural model.
  Group: mean and hierarchical-bootstrap 95% CI per t.
- **Summary numbers.** (a) Earliest t at which the group 95% CI of EEG-only AUC stays
  above 0.5 for all later t. (b) Same for ΔAUC. (c) Pre-stimulus window AUC.
  (d) Same curve for the 4 EOG channels (eye control).
- **Reading.** If (b) never clears 0, EEG adds nothing usable in real time beyond what
  the list position already tells you. Say so.

### E2. Simulated closed-loop policy (no new data)

- **Question.** If a system re-presented the words it flags as "likely forgotten", how
  many extra words would be recalled, and how much of that comes from EEG?
- **Policies**, each choosing k words per list (k = 1, 2, 3):
  random; lowest non-neural probability; lowest combined probability; lowest EEG-only
  probability; oracle (actually forgotten words).
- **Benefit model (assumption, stated as such).** A re-presented word that would have
  been forgotten becomes recalled with probability b; a word that would have been
  recalled gains nothing. Sweep b = 0.1, 0.2, 0.3, 0.5. No value of b is taken from the
  literature in this plan; report all.
- **Outputs.** Expected extra words recalled per list for each policy, k and b, with
  hierarchical-bootstrap CIs. Key number: combined policy minus non-neural policy.
- **Theory curve.** Under a binormal model with the observed recall rate, compute the
  extra recall per list as a function of classifier AUC (0.5 to 0.9). Mark the scalp
  EEG-only AUC, the in-brain EEG-only AUC (0.570, from the RAM run) and Ezzyat 2018's
  AUC 0.61. This curve is the blueprint: it tells a future experiment what AUC it needs.

### E5. Item-level fingerprint: encoding–recognition similarity

- **Data check first.** ltpFR has EEG during free recall (`REC_WORD`, vocal onset) and
  during the recognition test (`RECOG_TARGET`, word onset). Use recognition: it has a
  clean word onset, every studied word is shown once, and the window matches encoding.
  Do not use free-recall epochs (onsets are vocal responses, with speech artefacts).
- **Measure.** For each studied word w with a recognition trial: pattern vector =
  channels × frequencies features (z-scored within session). Encoding–retrieval
  similarity ERS(w) = Pearson r between w's encoding vector and w's recognition vector.
  Baseline = mean r between w's encoding vector and the recognition vectors of other
  words from the **same list**. Item-specific ERS = ERS(w) − baseline.
- **Tests (exploratory).** (1) Mean item-specific ERS > 0 across participants (one-sample
  Wilcoxon). (2) Within person, does item-specific ERS differ between words recognised
  with high confidence and words missed? (3) Does it differ between recalled and
  not-recalled words? (4) Eye control: the same analysis on the 4 EOG channels only.
- **Caveat to report.** Recalled words were also retrieved during free recall, before
  the recognition test. A difference between recalled and forgotten words can come from
  that extra retrieval, not from encoding.

### Not done, and why

- **E3 personal vs universal code** was already run as registered Secondary 1:
  personal model beat the pooled model in 19 of 20 people (Holm p = .0002). Report it;
  do not rerun it under a new name.
- **E4 spectral vs time-domain (ERP)** is deferred: worthwhile, but it is a feature
  comparison rather than a bridge, and the run is already about 20 hours. It can reuse
  X1 data later if time allows.

## 5. Tests (pytest, no download, run before every commit)

- Causal window test: changing the signal after t must not change features at t.
- Recognition matching: every `RECOG_TARGET` maps to exactly one studied `WORD` in the
  fixture; lures never map.
- ERS baseline uses only same-list, other-item vectors.
- E2 with an oracle predictor gives the maximum gain; a random predictor's expected
  gain equals k × b × forgetting rate (within simulation error).
- X0 reproduces the frozen AUCs on the pilot participants.
- Frozen-code hash check: `scalp-eeg/` files match `FROZEN_SHA256.txt`.

## 6. Reproducibility checklist

- [ ] Exploratory addendum posted on OSF before stage X1 on any confirmatory participant (URL in `config.py`)
- [ ] `scalp-eeg/` unchanged (hash check passes)
- [ ] Python and package versions pinned in `pyproject.toml`; `pip freeze` saved to `reports/`
- [ ] All random seeds fixed and listed (bootstrap seed 20261021; E2 simulation seed 20261102)
- [ ] Every skipped session and trial listed with its reason
- [ ] Inspection report saved before analysis
- [ ] X0 match report shows frozen AUCs reproduced
- [ ] Code frozen and tagged before the confirmatory-sample run
- [ ] Every figure generated by a script from saved results, not by hand
- [ ] Any change after the freeze listed next to its result

## 7. If something looks real: confirm it on fresh data

The selection rule gives 149 eligible ltpFR participants. Only 23 have had their EEG
opened (3 pilot + 20 confirmatory). The next 20 IDs in ascending order are untouched.
A promising exploratory effect (for example, item-specific ERS > 0) can get its own
pre-registration with a fixed test, a smallest effect of interest and frozen code, then
be run once on those 20. Do not open their EEG before that registration is public.

## 8. Figures

| ID | Content |
| --- | --- |
| F-E1a | Group EEG-only AUC and ΔAUC against causal end-time t, with 95% CI bands; EOG curve dashed |
| F-E1b | Per-participant earliest reliable t (dot plot) |
| F-E2a | Extra words recalled per list by policy (bars), k = 2, b = 0.3, with CIs; other k and b in the supplement |
| F-E2b | Theory curve: extra recall against AUC, with scalp, in-brain and Ezzyat 2018 AUCs marked |
| F-E5a | Item-specific ERS per participant (dots) with group mean and CI; EOG version beside it |
| F-E5b | Item-specific ERS by recognition confidence and by recall status |
