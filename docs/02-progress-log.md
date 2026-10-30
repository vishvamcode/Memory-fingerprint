# Memory Fingerprint: Progress Log

Oct 22, 2026 · @Vishvam

A record of everything done on the project since 21 October 2026, in order, with the reason for each step. For explanations of the science, see the plain-language guide.

## Log, from the beginning

| # | When | What was done | Why |
| --- | --- | --- | --- |
| 1 | 21 Oct | You sent the master prompt: analyse the "Personalized Neural Memory Signature" idea across neuroscience, AI, ethics and practicality, with 8 hypotheses (H1 to H8) and a 22-section report. You set strict rules: never invent citations, results, file names or data formats; only a computer and public data; ethics for Sweden and the EU | To get an honest, evidence-based picture before building anything |
| 2 | 21 Oct | Wrote the 22-section research report. Verdict: the idea is plausible as a *measurement* question, not yet as a way to *help* memory. Helping memory with better reminders is far better supported than replaying brain patterns | To separate what is known from what is hoped, and choose a realistic first step |
| 3 | 21 Oct | You asked for Follow-up 1: choose the best public dataset and one testable hypothesis. I compared about 8 datasets by opening their actual files, not just reading descriptions | Your rule: verify, don't assume |
| 4 | 21 Oct | Chose PEERS (scalp EEG, many visits per person, every word has a memory outcome). Found that the files have no "remembered" column; worked out how to derive it. Picked two backup datasets for later checking | It was the only open dataset with non-invasive EEG, a memory test for every item, and many visits per person |
| 5 | 21 Oct | Fixed the hypothesis: brain signals during learning improve prediction of later recall by at least 0.01 AUC, tested on unseen visits and unseen words. Fixed success and failure rules and the 3 practice + 20 test participants | A claim that can clearly be proven wrong, decided before looking at results |
| 6 | 21 Oct | You asked for Follow-up 2: build the first experiment. Wrote the analysis code in 7 stages, each with automatic tests that use a real recording | So every step can be checked on its own, and by anyone |
| 7 | 21 Oct | Practice run on 3 people, 4 to 5 visits each. Found that the combined model was worse than the without-brain model. Switched to a two-step ("stacked") model. Delivered the build guide | The practice run exists to find problems like this |
| 8 | 21 Oct | You asked for Follow-up 3: audit the experiment as a sceptic. Read every stage looking for leakage, weak baselines, confounds, overfitting and statistical mistakes | To catch flaws before the real test, not after |
| 9 | 21 Oct | Fixed 5 problems found in the audit: a peek during tuning, fatigue not in the baseline, a rigged memory-strength test, and missing controls for eyes and button presses. Added the previous-word test | Each could have produced a false "success" |
| 10 | 21 Oct | Ran the practice on all 20 visits per person (about 4 hours of computing). Found sensor names and eye-sensor positions change between visits; fixed by using one fixed sensor order | Only visible with all visits; would have silently corrupted results |
| 11 | 21 Oct | Delivered the audit. Verdict: no result yet (practice only). Hint from practice: brain gain in 1 of 3 people, about half explained by eyes and general alertness | So you know exactly what can and cannot be claimed |
| 12 | 22 Oct | You chose to pre-register before the real test. Wrote the pre-registration draft, froze the code (checksums + zip), and made odd recordings skip instead of crash | So the real test's rules are public and fixed before it runs |
| 13 | 22 Oct | You asked for this log and a plain-language guide | To catch up on everything in simple terms |
| 14 | 22 Oct | Wrote copy-paste answers for every OSF form field. You registered the plan publicly at osf.io/9ghzn | The rules are now public and dated before any test data were analysed |
| 15 | 22 Oct, 13:19 UTC | Checked the code against the frozen fingerprints (16 of 16 files match) and started the real test on the 20 confirmatory participants | This is the step the whole project has been building toward |
| 16 | 22 to 23 Oct | The computer running the test restarted twice. Each time I checked the code still matched the frozen fingerprints and continued from where it stopped | So the result comes from exactly the registered code |
| 17 | 23 Oct, 11:22 UTC | All 20 test participants finished. 5 visits were skipped because their timing records had duplicate entries. This skip reason was not in the registration, so it is reported as a deviation | An honest record of anything that differs from the plan |
| 18 | 23 Oct | Verdict by the frozen rule: FAILURE, flagged "present but negligible". Brain signals add a real but tiny gain (average +0.005 AUC, likely range 0.002 to 0.009), below the 0.01 we set in advance as the smallest gain that matters | This is the answer the registration committed us to |
| 19 | 23 Oct | Extra checks: about half the gain is matched by the eye sensors alone; the gain belongs to the word being learned (the previous word's signal adds nothing); a personal brain model beats a one-size-fits-all model in 19 of 20 people | Helps decide what is worth trying next |
| 20 | 23 Oct | You asked to keep going toward the full idea. Wrote a roadmap of 7 sub-projects and started sub-project 1: the same test with electrodes inside the brain (RAM dataset, 280 epilepsy patients). Found that every visit reuses the same 300 words, so the test now also hides groups of words | To find out whether the blurry scalp sensor was the weak link |
| 21 | 23 Oct | Practice run on 3 in-brain participants found and fixed 3 code problems. Wrote the pre-registration addendum and froze the new code (35 tests pass) | Same honest process as the first test: rules fixed before the real data are analysed |
| 22 | 23 Oct | Exploratory fingerprint check on the 23 scalp-EEG people: each person's memory pattern from half their visits picked them out from the other half in 13 of 23 cases (chance about 1 in 23). Models trained on early visits worked a bit worse later than models trained on recent visits | First look at whether the signal is personal and stable (sub-project 3); must be confirmed on new people |

## Key decisions and why

| Decision | Why | What we gave up |
| --- | --- | --- |
| Test only the first building block of the idea (learning-time signals predict memory) | The later claims (word-specific, comes back at recall, personal, can help memory) all depend on it | The exciting parts of the idea wait until the foundation is checked |
| Scalp EEG data, not brain scans or surgery recordings | It is the only kind a future everyday tool could use; it is free and well documented | Blurrier signal than recordings inside the brain |
| PEERS ltpFR as main dataset | Many visits per person, memory outcome for every word, free, no login | Very large files; only one visit can be processed at a time |
| Strong without-brain comparison model | Beating a weak guess proves nothing | Makes success harder |
| Hide whole visits and their words | The fairest test of whether a personal model works on a new day | Less training data per model |
| 0.01 AUC as the smallest gain that matters | Set before any results, so it can't be bent later | A real but tiny effect counts as failure |
| 3 practice people, 20 test people, chosen by a fixed rule | Practice can be used for tuning without spoiling the real test | 20 is set by computing time, not a power calculation |
| Stacked (two-step) model | The single combined model let brain numbers drown out the word facts | Slightly more complex method |
| Controls for eyes, muscles, button presses and alertness | These are the classic ways EEG "predicts memory" for the wrong reason | More computing time |
| Pre-register before the real test | Makes any result, positive or negative, believable | A short wait while you post it |

## Documents and files

| Item | What it is | Read it if |
| --- | --- | --- |
| [Plain-language guide](https://claude.ai/artifact/TLwaj192zVZHueW84k7TYC) | The whole project explained from zero | Start here |
| [Research report](https://claude.ai/artifact/MA1xcVnxzcqpLzUePKmddj) | The 22-section analysis of the full idea | You want the big picture and the science behind it |
| [Dataset selection](https://claude.ai/artifact/XHQcG4RNtexgBJyMUp3BPx) | Why PEERS, what was checked in the real files, the hypothesis | You want to know why this data |
| [Build guide](https://claude.ai/artifact/KRdGVd6qLmWrNFxrT8dkN8) | How to install and run the code, stage by stage | You want to run it yourself |
| [Experiment audit](https://claude.ai/artifact/8FSuFnTX7y5RagWP2p3hkZ) | The sceptical review: problems, fixes, what can be claimed | You want to know how trustworthy it is |
| [Pre-registration draft](https://claude.ai/artifact/QDR6hWpyKKaB38xBwLxiBN) | The public plan to post on OSF | Before posting it |
| `memory-fingerprint/` (project files) | The analysis code, 38 automatic tests, README | Running or checking the code |
| `memory-fingerprint/pilot_check_full/` | Practice-run results for 3 people | You want the practice numbers |
| `memory-fingerprint-frozen-2026-10-22.zip` and `FROZEN_SHA256.txt` | The frozen code and its digital fingerprints | Attaching to the pre-registration |

## Open items

- [x] **You:** post the pre-registration on OSF (done 22 Oct: osf.io/9ghzn)
- [x] **Me:** once I have the link, run the 20 test participants (about 12 to 15 hours)
- [x] **Me:** report the verdict exactly as the pre-written rules give it, with all controls, and add it to this log
- [ ] **Later, after the verdict:** repeat on the second PEERS experiment and the in-brain dataset, as planned in the dataset selection document

The sensor-name problem (log row 10) may hide other surprises in the test participants' files. The code now checks every visit and lists any it had to skip, so nothing gets dropped without a record.
