# Memory Fingerprint: Roadmap After the First Test

Oct 23, 2026 · @Vishvam

## Where we stand

The first real test asked one narrow question: does scalp EEG, recorded while someone learns a word, help predict whether they will later remember it, beyond simple facts about the word and the list? The registered answer was **failure, "present but negligible"**: a real gain of about 0.005 AUC, below the 0.01 we said would matter.

**What this rules out.** Scalp EEG at learning, used this way, is not good enough on its own to be the basis of a useful memory tool.

**What it does not rule out.** The test also showed three things that keep the bigger idea alive:

- The small gain belongs to the **specific word** being learned, not to general alertness (the previous word's signal added nothing).
- The signal is **somewhat personal**: a model trained on the same person beat a shared model in 19 of 20 people.
- On its own, the brain signal guessed better than chance in 19 of 20 people. The information is there; it mostly overlaps with what the word facts already tell us.

The weak link may be the **sensor** (scalp EEG is blurry), the **moment** we looked at (learning, not recall), or the **question** ("will it be remembered?" instead of "which memory is this?"). Each sub-project below changes one of these.

## The full idea as a ladder

The research report broke the Personalized Neural Memory Signature into 8 claims, H1 to H8. Each one needs the ones below it. The table shows where each stands now and which sub-project in this roadmap tests it.

| Claim | Plain meaning | Status now | Tested by |
| --- | --- | --- | --- |
| H1 | Brain recordings carry information about what you are seeing | Established by others | (not needed) |
| H2 | A personal model can separate memory information from noise like eye movements | Partly shown in our test (word-specific, survives eye check) | SP1, SP3 |
| H3 | Remembered and forgotten items look different while learning | Real but tiny on scalp EEG (our test) | SP1, SP6 |
| H4 | A specific memory's pattern comes back when you recall it | Shown by others for categories and some items; untested by us | SP2 |
| H5 | A person's pattern stays recognisable across days and weeks | Not known | SP3 |
| H6 | A model can pick better reminders or predict recall | Not known | SP4, SP5 |
| H7 | A personal intervention improves memory | Early evidence from others (brain stimulation in epilepsy patients) | Only simulated (SP4) |
| H8 | Replaying a stored pattern brings back a specific memory | No human evidence | Out of reach with public data |

The heart of a "memory fingerprint" is H4 plus H5: a pattern specific to one memory, that comes back when you remember it, and that stays recognisable for that person over time. The first test only touched H2 and H3. Most of the sub-projects below aim higher up the ladder.

## Sub-project 1 (starting now): the same test with in-brain recordings

**Question.** Does the small gain grow when the sensors sit inside the brain instead of on the scalp?

**Why it matters.** If the gain becomes clearly larger than 0.01, the problem in the first test was the blurry sensor, not the idea. If it stays tiny even inside the brain, "will this word be remembered?" is simply mostly decided by things other than the learning moment, and the fingerprint idea should move to recall (SP2) and personal stability (SP3).

**The data, checked in the real files today.** OpenNeuro dataset ds004789 (version 3.1.0, licence CC0, no login), "Delayed Free Recall of Word Lists", collected by the University of Pennsylvania lab with hospitals across the US during the DARPA RAM programme. The volunteers were epilepsy patients who already had electrodes placed for their medical care.

- 280 participants listed. Sessions per person (counted from the folders): 113 have 1, 83 have 2, 55 have 3, 20 have 4, and 8 have 5 to 8. **83 people have 3 or more sessions.**
- Each session (example: sub-R1001P, session 0): one practice list, then 25 lists of 12 words, 300 words in all. After each list: a short arithmetic distraction, then free recall.
- The event files have no "remembered" column, exactly like PEERS. Recalled words are listed as `REC_WORD` events with the spoken word in `item_name`, so the same matching step works.
- Signals: bipolar recordings from strips on the brain surface (`ECOG`) and depth wires (`SEEG`); the example has 54 and 18 channels at 500 Hz, about 220 to 340 MB per session. Each electrode has a brain-region label, so we can later look at memory areas such as the hippocampus.
- Every person has a **different set of electrodes**. That is fine for personal models (the main test), but a shared model across people can only be built by brain region.
- There are **no eye sensors** recorded, so the eye check from the first test can't be repeated directly. Signals inside the brain are much less affected by eye movements, but this is a real gap and will be stated.

**Plan.**

1. Reuse the frozen pipeline with the fewest possible changes: new event reader (same columns as PEERS, different word list), per-person channel list instead of the fixed 129-sensor layout, same 8 frequencies, same stacked model, same non-neural model, same rule.
2. Same split: hide one whole session and its words, train on the rest. With 3 sessions per person, training uses 2 sessions (about 600 words), less than the 19 sessions per person in PEERS. That makes success harder, which is the honest direction.
3. Choose participants by a fixed rule before looking: everyone with 3 or more sessions, ordered by a fixed random seed; the first 3 are practice, the next 20 are the test.
4. Practice run on the 3, fix anything that breaks, then freeze the code again.
5. Register the plan as an addendum on your OSF project before the real run. Same success and failure rule (gain of at least 0.01).

**Two numbers to watch.** The brain-only score (how well the electrodes alone guess what will be remembered) and the gain over the word-facts model. If the brain-only score rises a lot compared with scalp EEG (0.53 to 0.61) but the gain still stays under 0.01, the brain signal and the word facts are telling us the same thing, which is itself a key finding.

**Effort.** About 25 GB of downloads, processed one session at a time; roughly a day of computing for 23 people.

## Other sub-projects

All of these use only a computer and public data. Each one is small enough to finish, can clearly fail, and moves one rung up the ladder.

### SP2: Does a memory's pattern come back when it is recalled? (H4)

- **Question:** in the second before someone says a word out loud during recall, does their brain activity look more like the activity from when they learned *that* word than like the activity for other words from the same list?
- **Why it matters most:** this is the closest public-data test of a true "memory fingerprint": a pattern tied to one specific memory that returns when the memory returns.
- **Data:** both datasets mark the moment each recalled word is spoken (`REC_WORD` events), so no new downloads beyond SP1 and the PEERS files.
- **Method:** compare the learning pattern of each recalled word with its own recall moment versus its list-mates' learning patterns ("encoding-retrieval similarity"). Controls: same comparison with shuffled word labels, and with the moment just after speaking (mouth movement).
- **Success:** own word clearly more similar than list-mates, in most people. **Failure:** no difference beyond the shuffled control.
- **Effort:** medium. Mostly new analysis code; features at recall need extracting.

### SP3: Does a person's memory pattern stay the same over weeks? (H5)

- **Question:** PEERS participants came back for 20 or more visits on separate days (the exact time span will be read from the files). Does a personal model trained on the early visits still work on the late visits, or does it fade?
- **Second question:** is each person's model distinct enough that you could tell who someone is from it, like a fingerprint?
- **Data:** the features we already extracted for 23 people. **No new downloads.**
- **Success:** performance stays flat over time, and the person can be identified well above chance. **Failure:** the model fades quickly, or everybody's model looks the same.
- **Effort:** small. Could run alongside SP1.

### SP4: Are there "good moments" to learn? (towards H6 and H7)

- **Question:** does brain activity just *before* a word appears predict whether it will be remembered? If so, a computer could time when to show important information.
- **Method:** same models, using the half second before each word. Then a simulation: if words had only been shown at predicted good moments, how many more would have been recalled?
- **Why:** this is the idea behind the closed-loop stimulation studies the report described, tested without touching anyone.
- **Success:** a pre-word gain of at least 0.01 and a simulated improvement in recall. **Effort:** small to medium, using SP1's code.

### SP5: Can a model pick the best reminder? (H6)

- **Question:** when someone gets stuck during recall, which word should a helper give as a hint to unlock the most other words?
- **Method:** a standard computer model of free recall learns each person's recall habits (for example, recalling neighbours from the list together). Test whether personal versions predict the next recalled word better than a shared one, and whether adding brain signals helps.
- **Why:** the report found helping memory with good cues much better supported than replaying brain patterns. This is the most practical path to a real tool.
- **Effort:** medium; mostly behaviour, so it can use all 149 eligible PEERS people.

### SP6: Does the first answer hold in new people? (H3, replication)

- Re-run the frozen first test on the second PEERS experiment (ltpFR2), as already planned in the dataset selection document. Quick to set up, about 12 to 15 hours of computing. Lower priority now, because the first answer was clear.

### SP7: How much data does a personal model need?

- Using the existing features, train on 1, 2, 4, 8 and 16 visits and see where performance stops improving. For any future tool this decides whether a few sessions of calibration are enough. **Effort:** small, no downloads.

## Suggested order

| When | Sub-project | Why then |
| --- | --- | --- |
| Now | **SP1** in-brain test | You asked for it, and it tells us whether the sensor was the weak link |
| Now, alongside | **SP3** stability and fingerprint, **SP7** data needed | No downloads; uses features we already have, so they run while SP1 downloads |
| Next | **SP2** pattern returns at recall | The real core of a memory fingerprint; builds on SP1's code and data |
| Then | **SP4** good moments, **SP5** best reminder | The first steps toward something that could help memory |
| Later | **SP6** replication | Useful but the first answer was already clear |

Each sub-project gets the same treatment as the first test: practice run, frozen code, a registered rule, then the real run, with results added to the plain-language guide and the progress log. I'll start SP1 and SP3 now and bring you the practice results before anything is registered.

## Early results (exploratory, 23 October)

These use the 23 scalp-EEG people already analysed. Nothing here was registered in advance, so treat each as a hint to test properly on new people.

**SP3, fingerprint.** For each person, a memory map (how each sensor and frequency differs between remembered and forgotten words) was built from their odd-numbered visits and compared with everyone's map from even-numbered visits. The person's own map was the best match in **13 of 23** people (chance: about 1 in 23). With the remembered/forgotten labels shuffled, the same method still picked the right person in about 5 of 23, so part of the match comes from things unrelated to memory (each person's sensors and noise). The real maps did clearly better than shuffled ones (p = 0.01).

**SP3, stability.** A brain-only model trained on a person's first 6 visits scored on average 0.02 AUC lower on later visits than a model trained on the 6 visits just before (20 of 23 people). So the signal drifts and a personal model would need updating. The visit dates in the files were not reliable enough to measure drift per day.

**SP7, data needed.** Brain-only AUC on a person's last 4 visits when trained on 1, 2, 4, 8 or 16 earlier visits: 0.52, 0.52, 0.55, 0.55, 0.56. Below about 4 visits the model is close to guessing; after that it improves slowly.

Files: `memory-fingerprint-sp3/` in the project folder.
