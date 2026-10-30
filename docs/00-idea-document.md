# Memory Fingerprint: Idea Document

Oct 30, 2026 · @Vishvam

## 1. The idea in one minute

**Summary.** A Memory Fingerprint is a small computer model, trained on one person's own brain recordings, that can tell from the brain signal whether that person is storing a memory well right now. Long term, it could help people with early memory problems by picking the best moments and the best reminders for them.

**Explain it like I'm 10.** Think of a camera with a little light that turns green when a photo comes out sharp. Your brain is the camera, and you can't tell yourself whether a memory came out sharp or blurry. The Memory Fingerprint is that little light. It is tuned to *your* brain only, the way a voice assistant learns your voice.

> Assumption, flagged once: you are a student heading toward a Master's or PhD, working alone with a laptop and public data. Sections 7, 8 and 10 are written for that.

### The problem

- People forget things they want to keep: names, appointments, where things are.
- For people with **mild cognitive impairment (MCI)**, which means memory problems bigger than normal ageing but not yet dementia, this gets worse over years. Some go on to **Alzheimer's disease**, the most common cause of dementia.
- Today's memory aids (notes, phone reminders) are "dumb". They don't know if you actually stored the memory or not.

### The solution

A **Personalized Neural Memory Signature (PNMS)**: a model of what *your* brain activity looks like when a memory is being stored well (this is called **encoding**) and when it is being pulled back up (this is called **retrieval**).

Analogy: every person has a different handwriting. A general model reads "average handwriting". A personal model learns *your* handwriting, so it reads you better.

### How it works, step by step

1. **Record.** A person learns a list of words while their brain activity is recorded. **EEG** (sensors on the scalp, like a swimming cap with wires) is the cheap kind. **iEEG** (electrodes placed inside the skull, only done in epilepsy patients for medical reasons) is the clean kind.
2. **Label.** Later, the person tries to recall the words. Each word gets a label: remembered or forgotten.
3. **Learn the pattern.** A computer model looks at the brain signal from the moment each word was shown and learns which patterns go with "remembered".
4. **Check it honestly.** Test the model on sessions and words it has never seen. Compare it with a model that uses *no brain data at all* (just things like word position and the person's habits). The brain model only counts if it beats that.
5. **Make it personal.** Train one model per person and show it beats one shared model for everyone.
6. **Use it (later, not yet).** Once the light works, use it to (a) spot good and bad moments to learn, and (b) pick the reminder that best brings a memory back.

### What the end product looks like

| Stage | What you'd have | Who uses it |
| --- | --- | --- |
| Research tool (now) | Open code that builds and tests a personal memory model from public recordings | Researchers |
| Better measure | A proven "memory-strength score" that works on clean in-brain recordings | Researchers, clinicians studying MCI |
| Assistant (far future, speculative) | A wearable that says "this didn't stick, let's review it" or picks the right cue for a forgotten name | People with MCI, with their doctor |

Important: step 6 and the wearable are **speculation**. Nothing we have done yet shows they work.

## 2. Why it matters

It matters because memory loss is common, getting more common as people live longer, and current tools can't see whether a memory actually stuck.

**Who it helps**

- **Researchers** get an honest, open test of a big question: is each person's "memory signal" different enough that a personal model is worth it?
- **People with MCI and their families**, in the long run, if a reliable signal could guide when to study or which reminder to use.
- **Clinicians** could one day get an objective measure of memory function instead of only paper-and-pencil tests.

**What problem it solves.** Right now you only find out a memory failed when you try to use it, and by then it's too late. A working signal would catch the failure at the moment it happens. Analogy: a smoke alarm beats finding out about a fire when the house is gone.

**Why now**

- **Big free datasets exist.** Thousands of hours of recordings of people learning word lists are public and free to reuse (PEERS scalp EEG, RAM in-brain recordings, both on OpenNeuro).
- **Free tools are good enough.** Python libraries like MNE and scikit-learn can do on a laptop what needed a lab ten years ago.
- **Brain stimulation studies have shown memory can be nudged.** Researchers have reported that stimulating at moments of poor encoding improved recall in epilepsy patients. This is real but early and small, which is exactly why a better personal signal would be useful.
- **Ageing populations.** Sweden and the EU have growing numbers of older adults, so memory support is a long-term health priority.

## 3. How feasible is it?

As a **measurement question** on public data, it is doable. As a **memory-helping product**, it is very hard and many years away. Our own scalp-EEG test already showed the signal is real but tiny.

| Side | Rating | Why |
| --- | --- | --- |
| Technical (research part) | Medium | Standard Python tools work; the hard part is avoiding fake results (see risks). |
| Technical (helping memory) | Hard | Needs a signal far stronger than what we found, plus a way to act on it. |
| Time | Medium | Each full test is about 1 to 2 weeks of computer time and writing. A paper is about 6 to 12 months. |
| Data | Easy now, hard later | Free public data is plenty for research. New data for a real product needs a lab, ethics approval and participants. |
| Cost | Easy | About 0 kr so far: a laptop or a cloud machine and free data. |

### Biggest risks and how to test each one cheaply

| Risk | What it means in plain words | Cheap test |
| --- | --- | --- |
| **The signal is too small** | Already true on scalp EEG: brain data added only 0.005 to a score where 0.01 was the smallest useful amount. | In-brain recordings (running now). If that is also tiny, the idea needs a new angle. |
| **Eye movements fake the signal** | Blinks and eye movement show up on scalp sensors. Analogy: a microphone picking up the fan instead of the speaker. | Done: an eye-only model gave about half the gain. In-brain data has almost no eye noise. |
| **It's mood, not memory** | The model may just detect "alert vs. tired", not memory of a specific word. | Done: the signal from the *previous* word didn't help, so it is word-specific. |
| **The fingerprint drifts** | Your brain pattern may change over weeks, so a model trained in January fails in March. | Done (early): recent-trained models beat early-trained ones. Next: measure how fast it drifts. |
| **Lab words ≠ real life** | Remembering "TABLE" in a list isn't remembering where you parked. | Look for public datasets with more natural memories (pictures, stories, places). |
| **Fooling ourselves** | Trying many analyses until one "works". | Already handled: rules were written down and frozen publicly (pre-registration) before each real test. |
| **Patients differ** | iEEG patients have epilepsy, and MCI brains differ from young students'. | Can't fix with public data alone. Flag it clearly; later, partner with a clinic. |

**Critical take.** The most likely outcome is that the "memory light" stays dim on scalp EEG. Its best chance is as a research measure on in-brain data, or as a tool for *choosing reminders* (retrieval), which has better support than *strengthening memories* during learning.

## 4. What's been done so far

The headline: one full, pre-registered test on 20 people's scalp EEG found a **real but too-small** memory signal, and a second test on in-brain recordings is running right now (30 October 2026).

### Two words you need

- **AUC** is a score for how well a model sorts "remembered" from "forgotten". 0.5 means coin-flip, 1.0 means perfect. Analogy: a weather forecaster who is right 55% of the time is barely better than guessing.
- **ΔAUC** ("delta AUC") is how much the score goes *up* when you add brain data to a model that has none. We decided in advance that 0.01 is the smallest gain worth caring about.

### Work completed

| Date | Step | Result |
| --- | --- | --- |
| 30 Oct 2026 | In-brain test (RAM iEEG, 20 patients) | Running; verdict not in yet. |
| 23 Oct 2026 | Roadmap of 7 sub-projects + early side tests | See "exploratory" below. |
| 23 Oct 2026 | In-brain plan written, code frozen, registered on OSF | [osf.io/xn4v9](https://osf.io/xn4v9) |
| 23 Oct 2026 | Real scalp-EEG test, 20 people | **Failed the pre-set bar** (details below). |
| 22 Oct 2026 | Pre-registration: rules written and frozen before looking | [osf.io/9ghzn](https://osf.io/9ghzn/overview) |
| 21 Oct 2026 | Self-audit of the code | No test data leaking into training; 7 problems fixed. |
| 21 Oct 2026 | Research report, dataset choice, code and pilot on 3 people | Pilot numbers were code checks only. |

### Methods used, in plain words

- **Data:** PEERS (scalp EEG, people learning word lists over about 20 sessions each) and RAM (in-brain recordings from epilepsy patients doing the same kind of task). Both are free on OpenNeuro.
- **Features:** for each word, the strength of brain rhythms at 8 speeds (3 to 128 cycles per second) in the 1.4 seconds after the word appears. Analogy: like splitting music into bass, mid and treble.
- **Model:** a simple, well-understood classifier (regularised logistic regression), trained per person.
- **Fair test:** always tested on sessions (and, for in-brain data, words) the model never saw.
- **Pre-registration:** the success/failure rule was public before the real run. Analogy: calling your shot in pool before you hit.

### Results of the real scalp-EEG test (20 people)

| What we checked | Number | What it means |
| --- | --- | --- |
| Average gain from brain data (ΔAUC) | **0.005** (95% range 0.002 to 0.009) | Real (p = 0.00005) but half the size we said would matter. |
| Verdict by our frozen rule | **Failure: present but negligible** | The signal exists, but it's too small to be useful. |
| Gain from eye sensors only | 0.0025 | About half the gain may be eye movement, not brain. |
| Gain using the previous word's signal | about 0 | The signal is about *that* word, not general alertness. |
| Personal model vs one shared model | Personal better in **19 of 20** people (AUC 0.562 vs 0.537) | Supports the "fingerprint" part of the idea. |

### Exploratory side tests (not pre-registered, treat as hints)

- **Can a model recognise whose brain it is?** Right person picked 13 of 23 times; chance-level control about 20%.
- **Does the fingerprint drift?** Models trained on recent sessions beat ones trained on early sessions in 20 of 23 people (by 0.021 AUC).
- **How much data is needed?** Training on 1, 2, 4, 8 and 16 sessions gave AUC 0.524, 0.523, 0.547, 0.552 and 0.561. More data helps slowly.

### What it proves, and what it doesn't

| Proves (on this data) | Does not prove |
| --- | --- |
| Scalp EEG carries a tiny, word-specific memory signal | That it's useful for anything practical |
| Personal models beat shared ones | That this works in MCI or Alzheimer's |
| Brain patterns are somewhat person-specific and drift over time | That we can *improve* memory with it |
| The method is honest (frozen rules, no leaks) | Anything about in-brain data yet |

## 5. Next steps

The top priority is to finish the in-brain test and report it honestly, because its answer decides which direction the rest of the project takes.

### Next 2 weeks

1. **Finish the in-brain test and report the verdict.** Done when: the frozen rule gives success, failure or ambiguous, and the result is posted next to the OSF registration.
2. **Make the OSF pages complete.** Done when: both registrations are public and the frozen code zip and checksum file are attached.
3. **Write a 2-page plain summary of both tests.** Done when: a friend with no science background can read it and explain the result back to you.
4. **Put the code on GitHub.** Done when: a public repo has the code, a README, and the tests pass on a fresh machine.

### Next 3 months

| Step | What it is | Done when |
| --- | --- | --- |
| **SP2: Does the pattern come back at recall?** | Check whether the brain pattern seen while learning a word reappears when the word is recalled. Analogy: humming a tune and seeing if the same notes come back. | Pre-registered, run on in-brain data, verdict reported. |
| **SP3: Fingerprint stability** | Measure properly how fast a person's pattern drifts over sessions. | A written result with a "half-life" estimate (how many weeks until the model is half as good). |
| **SP6: Replication on ltpFR2** | Re-run the scalp test on a second PEERS group. | Same frozen code, new people, verdict reported. |
| **Write-up** | Turn both tests into a short paper or preprint. | Posted on a preprint server (for example PsyArXiv or bioRxiv). |

### Next 12 months

| Step | Done when |
| --- | --- |
| **SP5: Best reminder.** Use the model to predict which cue (first letter, a related word, a picture) brings a forgotten word back. This is the most promising use. | A model that picks better cues than chance on held-out data, tested by a pre-set rule. |
| **SP4: Good moments to learn.** Find whether the brain state *before* a word predicts memory. | A pre-registered test with a clear verdict. |
| **More natural memories.** Find public data with pictures, places or stories. | A dataset chosen and a pilot run. |
| **A collaborator.** One lab with clinical or MCI data agrees to talk or co-supervise. | One meeting held, or a thesis project agreed. |
| **A poster or conference talk.** | Abstract accepted (see section 6). |

## 6. Using it for research

The strongest research angle is an honest **"how personal is the memory signal, and how big is it really?"** study, because a careful negative or small result with frozen rules is publishable and rare.

### Research questions it can answer

1. Does brain activity during learning predict later memory *beyond* simple non-brain information? (Scalp: yes but tiny. In-brain: pending.)
2. Does the gain grow with cleaner sensors (scalp vs in-brain)?
3. Is a personal model better than a shared one, and by how much?
4. How stable is a person's memory fingerprint over weeks? How fast does it drift?
5. Does the learning pattern come back during recall?
6. Can a personal model pick the best reminder for a forgotten item?
7. How much data per person do you need before a personal model is worth it?

### Paper, thesis and poster angles

| Angle | Format | Why it's attractive |
| --- | --- | --- |
| "A pre-registered test of personal memory models on scalp EEG: real but negligible" | Short paper or preprint | Pre-registered null-ish results are valued and uncommon. |
| "Scalp vs in-brain: does the memory signal grow with better sensors?" | Paper or Master's thesis | Direct comparison with the same rules on two datasets. |
| "How stable is a neural memory fingerprint?" | Conference poster | Simple, visual result (drift over sessions). |
| "How many sessions does a personal brain model need?" | Poster or methods note | Useful practical guidance for other researchers. |
| "Choosing the best cue from brain data" | PhD-proposal idea | Closest to a real-world use; links to MCI. |

Possible venues: the Cognitive Neuroscience Society meeting, the Society for Neuroscience meeting, the FENS Forum (Europe), and Swedish neuroscience meetings. Check each one's dates and deadlines on its own website, since they change every year.

### Datasets

| Dataset | What it is | Use |
| --- | --- | --- |
| [PEERS](https://openneuro.org/datasets/ds004395) (OpenNeuro ds004395) | Scalp EEG, word lists, many sessions per person. Free, CC0 licence (no restrictions). | Main scalp test, plus the ltpFR2 replication. |
| [RAM free recall](https://openneuro.org/datasets/ds004789) (OpenNeuro ds004789) | In-brain recordings from epilepsy patients, word lists. Free, CC0. | In-brain test (running), recall-pattern test. |
| Other OpenNeuro memory datasets | Search for "memory", "free recall", "episodic". | More natural memories (needs checking). |

### Tools and methods

- **Python** with **MNE-Python** (reads and cleans brain recordings) and **scikit-learn** (the models).
- **Time-frequency analysis:** splitting the signal into rhythms (like the bass/treble analogy).
- **Cross-validation:** testing on data the model never saw. Analogy: a teacher grading you on new questions, not the ones from the practice sheet.
- **Bootstrap:** resampling the people many times to see how sure we are. Analogy: re-shuffling a deck many times to see how often a hand comes up.
- **Pre-registration on OSF** (Open Science Framework): writing the rules publicly before the test.
- **A computer:** a laptop is fine for small runs; a cloud machine with 4+ cores and 16 GB memory for full runs.

## 7. Using it to build a portfolio

You already have more than most applicants: two frozen, pre-registered tests with honest results. The job now is to package them so a stranger can see that in 2 minutes.

| # | Piece | What it is | What it shows admissions or employers |
| --- | --- | --- | --- |
| 1 | **GitHub repo** "memory-fingerprint" | Clean code, README with one results figure, the tests, a "how to reproduce" section, link to OSF. | You can write real, tested research code. Reproducibility is a top skill in neuroscience and data science. |
| 2 | **Preprint** of the scalp + in-brain tests | 6 to 10 pages: question, frozen rules, results, limits. | You can run a study end-to-end and report a result that didn't go your way. That honesty stands out. |
| 3 | **Conference poster** | One page: "Is the memory signal personal? Scalp vs in-brain". | You can communicate science visually; posters are the normal first step for students. |
| 4 | **Plain-language blog post or explainer page** | The "memory light" story for non-scientists, with 2 or 3 pictures. | Science communication, which matters for grants and interviews. |
| 5 | **Interactive demo** (optional) | A small web page where you pick a person and see their model's score per word and how it drifts. | Data visualisation and product sense; useful for industry jobs. |

**Tip:** link all five to each other. The repo links the preprint; the preprint links the OSF registration; the poster has a QR code to the repo.

## 8. Who to contact and where to go

Your best first email in Sweden is the **Lund Memory Lab**, because it does EEG plus machine learning on memory formation, which is exactly your method. Worldwide, the **Kahana lab** made both datasets you used.

All entries below were checked online on 30 October 2026, unless marked *uncertain*. People move jobs, so re-check before you write.

### Sweden

| Who | Where | Why they're relevant | One-line hook |
| --- | --- | --- | --- |
| [Lund Memory Lab](https://psy.lu.se/en/research/neuro/lund-memory-lab) (contact: Prof. Mikael Johansson; also Inês Bramão, Roger Johansson) | Lund University, Dept. of Psychology | EEG with machine-learning decoding of memory formation and retrieval; EEG + eye-tracking. | "I ran a pre-registered test of personal EEG memory models on PEERS; about half the gain looked like eye signal, which your EEG + eye-tracking work could explain." |
| [Pawel Herman](https://www.kth.se/en/2.266/neurocomputational-mechanisms-of-memory-hebbian-plasticity-across-short-and-long-timescales-1.1403327) (with Anders Lansner) | KTH, Computational Science and Technology | Computational models of episodic and working memory; brain-signal analysis. | "I'd like to connect my data-driven memory signal results to a mechanistic memory model." |
| [Lars Nyberg](https://umu.se/en/staff/lars-nyberg) | Umeå University, UFBI (brain imaging centre) | Leading researcher on memory and the ageing brain. | "I'm testing how stable a person's memory signature is over time, which links to brain maintenance in ageing." |
| [Erika Jonsson Laukka group](https://ki.se/en/research/research-areas-centres-and-networks/research-groups/cognitive-aging-and-mental-health-erika-jonsson-laukka-group) | Karolinska Institutet, Aging Research Center (Stockholm) | Cognitive ageing and mental health in older adults. | "I'm building personal memory models and want to understand what matters for people at risk of MCI." |
| [Oskar Hansson](https://portal.research.lu.se/en/persons/oskar-hansson/) / [BioFINDER](https://clinicaltrials.gov/study/NCT01208675) | Lund University and Skåne University Hospital | Large Swedish study of early Alzheimer's and MCI. | "Could a personal memory-signal measure ever complement biomarkers in early MCI?" (Long shot, later stage.) |
| [Henrik Zetterberg](https://www.brightfocus.org/grantee/henrik-zetterberg-md-phd/) and Kaj Blennow | University of Gothenburg, Sahlgrenska Academy | World-leading Alzheimer's blood and fluid biomarkers. | Same as above; contact only once you have a clinical angle. |
| Uppsala and Chalmers | — | *Uncertain:* I found no group clearly matching "EEG memory decoding" there. Chalmers' biomedical engineering and Uppsala's psychology department are worth a browse. | — |

### Worldwide

| Who | Where | Why they're relevant | One-line hook |
| --- | --- | --- | --- |
| [Michael Kahana, Computational Memory Lab](https://memory.psych.upenn.edu/Michael_J._Kahana) | University of Pennsylvania, USA | Created PEERS and the RAM recordings you used; pioneers of predicting memory from brain signals. | "I ran a frozen, pre-registered test of personal models on PEERS and RAM; here's what I found and the code." |
| [Bernhard Staresina](https://www.psy.ox.ac.uk/people/bernhard-staresina) | University of Oxford, UK | Intracranial EEG of memory, encoding vs retrieval, memory reactivation and sleep. | "I'm testing whether the learning pattern comes back at recall in RAM iEEG data." |
| [Simon Hanslmayr lab](https://www.gla.ac.uk/schools/psychologyneuroscience/researchgroups/hanslmayr) | University of Glasgow, UK | Brain rhythms and memory with EEG, MEG, iEEG and stimulation. | "My memory signal uses brain rhythms from 3 to 128 Hz; I'd value your view on which ones should carry it." |
| [Nikolai Axmacher](https://www.neuro.psy.ruhr-uni-bochum.de/np/personen/nikolai-axmacher.html.en) | Ruhr University Bochum, Germany | Memory patterns ("engrams") and iEEG in humans. | "I'm measuring how stable a person's memory pattern is across sessions." |

### Short cold-email template

> **Subject:** Pre-registered test of personal EEG memory models: question about \[their topic\]
>
> Dear Prof. \[Name\],
>
> I'm \[your name\], a \[student status\] in \[city\]. I've been testing whether a personal model of brain activity can predict which words a person will remember, using the public PEERS and RAM datasets.
>
> In a pre-registered test on 20 people's scalp EEG, the brain signal added a real but very small gain (ΔAUC 0.005), and personal models beat a shared model in 19 of 20 people. Code and registration: \[GitHub link\], \[OSF link\].
>
> Your work on \[one specific paper or topic\] is very close to my next step, \[one sentence\]. Would you have 20 minutes for a call, or is there a thesis or internship route in your group?
>
> Best regards, \[Name\]

Tips: keep it under 150 words, name one of their papers you actually read, and attach nothing (links only).

## 9. How to scale it

Scale in four stages, and only move up when the stage below has a clear, honest result. Analogy: a food stall, then a restaurant, then a chain. Each step changes who you need and what can go wrong.

| Stage | What it looks like | What changes | Gate to move on |
| --- | --- | --- | --- |
| **1. Prototype (you are here)** | One person, a laptop or cloud machine, public data, frozen tests. | Nothing to manage except your own rigour. | In-brain verdict reported; one more sub-project (SP2 or SP3) done. |
| **2. Proper tool + benchmark** | A clean Python package anyone can install, plus a "memory-model benchmark": fixed datasets, fixed splits, a leaderboard of AUC gains. | You now support users: documentation, versioning, tests on new datasets. | Another person reproduces your results without your help. |
| **3. Open-source project or collaboration** | Other labs contribute datasets or models; you co-author with a group from section 8; possibly a thesis project. | Shared decisions, credit, data-sharing agreements. Research on people needs ethics approval (in Sweden, from the Swedish Ethical Review Authority) and GDPR rules for health data. | A lab with real (non-public) data agrees to run your pipeline. |
| **4. Bigger research programme** | Funded project testing personal memory models in older adults or MCI, possibly with a closed-loop helper (picks cues or timing). | Grants, a team, a clinic partner, medical-device rules (the EU Medical Device Regulation) if it ever gives health advice. | A pre-registered study in the target group shows a useful effect. |

**Honest note:** stage 4 needs a much stronger signal than we have on scalp EEG. If the in-brain test is also small, the best path to scale is stage 2 (the benchmark and tool), not a product.

## 10. How to make a business or money from it

Honest answer first: **there is no product to sell yet**, because the signal is too small. The realistic money right now is funded study (a paid PhD or research assistant job), not a company. Below are four routes, from most to least realistic for you today.

### Four routes

| Route | Who would pay | What they'd pay for | Path to first customer or funding | Realism now |
| --- | --- | --- | --- | --- |
| **1. Funded research position** | Universities, research councils (via a supervisor's grant) | Your skills: brain-data analysis, honest stats, reproducible code | Use sections 7 and 8: portfolio, then emails, then a PhD or RA post. A Swedish PhD is a paid job. | **High** |
| **2. Analysis consulting / freelance** | Small labs, EEG start-ups, students needing help | Cleaning and analysing EEG data, pre-registration, building pipelines | Offer a fixed-price "EEG pipeline check" to 5 labs or start-ups. | Medium |
| **3. Open-source tool + paid support** | Research labs, device makers | A trusted "personal memory model" toolkit and benchmark; training, custom features | Build users first (free), then offer workshops or support contracts. Slow. | Low to medium |
| **4. Memory-assist product (SaaS or device)** | Clinics, care providers, families, insurers | A tool that helps people with MCI remember (better cues, better timing) | Needs a much stronger signal, a clinical partner, ethics approval and CE-marking under EU medical device rules. Years away. | **Low** |

(SaaS = "software as a service": software people pay a monthly fee to use online, like Spotify for tools.)

### Swedish and EU funding options (checked 30 October 2026)

| Funder | What it is | Fit for you now |
| --- | --- | --- |
| [Vinnova – Innovative Startups 2026](https://www.vinnova.se/en/calls-for-proposals/innovative-startups/innovative-startups-2026) | Up to SEK 500,000 for a Swedish limited company (aktiebolag) under 10 years old. Call open 12 Oct 2026, closes **12 Jan 2027**, decision 23 Mar 2027. | Only if you have a company and a clear product idea. Not yet. |
| [Almi – Verification grant](https://www.almi.se/en/loan/verification-funds) | Up to about SEK 100,000 for companies; up to SEK 25,000 for private individuals with a Swedish personal number who plan to start a business. | Possible small test grant for route 2 or 3. |
| [LU Innovation (Lund University)](https://www.innovation.lu.se/en/student) | Free coaching for students; test grants up to SEK 20,000; LEAP summer grant SEK 40,000; incubator; help applying to Vinnova. | **Good first stop** if you are a Lund student. Other universities have similar offices (for example KTH Innovation, Chalmers Ventures, UU Innovation): check yours. |
| [Alzheimerfonden](https://www.alzheimerfonden.se/forskning/soek-anslag/) | Swedish Alzheimer's research foundation. Applicants must have a PhD, or be a PhD student past the half-time review. | Later, during a PhD. |
| Vetenskapsrådet (Swedish Research Council) | Main Swedish research grants, normally for researchers with a PhD. | Later, via a supervisor. |
| [EU Partnership for Brain Health (Horizon Europe)](https://www.thetransmitter.org/funding-opportunity/jtc2026-call-2-neurodegenerative-disorders-ep-brainhealth-call-2-europe-and-associated-countries/) | Joint calls for multi-country research groups on neurodegenerative disorders. The 2026 call is closed (full proposals were due 30 June 2026). | Only as part of a lab consortium. Watch for the next call. |
| Horizon Europe / Marie Skłodowska-Curie doctoral networks | EU-funded PhD positions in multi-country networks. | **Good fit:** apply *to* advertised PhD positions on EURAXESS. *Uncertain:* check current openings yourself. |

### Honest take

The most realistic route for you right now is **route 1, a funded Master's thesis project or PhD**, using this project as your calling card. Route 2 (small consulting) is a reasonable side option once the GitHub repo and preprint are public. Don't start a company or apply to Vinnova until a test shows a signal big enough to build on; starting one now would mean selling something that our own results say doesn't work yet.

## If I only do 3 things this month

If November 2026 only has room for three things, do these. Each one is small, finishable, and moves you toward a funded position.

- [ ] **1. Get the in-brain verdict and publish it honestly.** Let the running test finish, report the frozen-rule result (success, failure or ambiguous) next to the OSF registration, and check both OSF pages are public with the code zip and checksum attached. *Done when:* a stranger can open OSF and see the plan, the code and the result.
- [ ] **2. Put the project on GitHub with a one-page README.** Code, tests, one figure (scalp vs in-brain gain), links to OSF, and a 5-line plain summary at the top. *Done when:* a friend can clone it and run the tests.
- [ ] **3. Send 3 cold emails.** Lund Memory Lab, Pawel Herman at KTH, and the Kahana lab, using the template in section 8 with the GitHub and OSF links. Book an LU Innovation (or your own university's) coaching chat only if you want to explore the business side. *Done when:* 3 emails are sent and you've logged who replied.

**Not this month:** starting a company, applying to Vinnova, or buying any EEG hardware.

## Sources used

**Our own work (this project)**

- Scalp-EEG pre-registration: [osf.io/9ghzn](https://osf.io/9ghzn/overview)
- In-brain pre-registration: [osf.io/xn4v9](https://osf.io/xn4v9) (couldn't be opened from my computer; please confirm it's public)
- Project files: `memory-fingerprint/confirmatory/` (scalp results), `memory-fingerprint-sp3/` (fingerprint and drift side tests), `memory-fingerprint-ieeg/` (frozen in-brain code)

**Datasets**

- [PEERS, OpenNeuro ds004395](https://openneuro.org/datasets/ds004395)
- [RAM free recall, OpenNeuro ds004789](https://openneuro.org/datasets/ds004789)

**People and groups (opened 30 Oct 2026)**

- [Lund Memory Lab](https://psy.lu.se/en/research/neuro/lund-memory-lab)
- [KTH thesis page naming Pawel Herman and Anders Lansner](https://www.kth.se/en/2.266/neurocomputational-mechanisms-of-memory-hebbian-plasticity-across-short-and-long-timescales-1.1403327)
- [Lars Nyberg, Umeå University](https://umu.se/en/staff/lars-nyberg)
- [Erika Jonsson Laukka group, Karolinska Institutet](https://ki.se/en/research/research-areas-centres-and-networks/research-groups/cognitive-aging-and-mental-health-erika-jonsson-laukka-group) (from search results)
- [Oskar Hansson, Lund University](https://portal.research.lu.se/en/persons/oskar-hansson/) and [BioFINDER study](https://clinicaltrials.gov/study/NCT01208675) (from search results)
- [Henrik Zetterberg profile](https://www.brightfocus.org/grantee/henrik-zetterberg-md-phd/) (from search results)
- [Michael Kahana, Penn](https://memory.psych.upenn.edu/Michael_J._Kahana)
- [Bernhard Staresina, Oxford](https://www.psy.ox.ac.uk/people/bernhard-staresina)
- [Hanslmayr lab, Glasgow](https://www.gla.ac.uk/schools/psychologyneuroscience/researchgroups/hanslmayr)
- [Nikolai Axmacher, Bochum](https://www.neuro.psy.ruhr-uni-bochum.de/np/personen/nikolai-axmacher.html.en) (from search results)

**Funding (opened 30 Oct 2026)**

- [Vinnova Innovative Startups 2026](https://www.vinnova.se/en/calls-for-proposals/innovative-startups/innovative-startups-2026)
- [Almi verification grant](https://www.almi.se/en/loan/verification-funds)
- [LU Innovation for students](https://www.innovation.lu.se/en/student)
- [Alzheimerfonden grants](https://www.alzheimerfonden.se/forskning/soek-anslag/)
- [EP BrainHealth JTC2026 Call 2](https://www.thetransmitter.org/funding-opportunity/jtc2026-call-2-neurodegenerative-disorders-ep-brainhealth-call-2-europe-and-associated-countries/)

**From memory, not re-opened today (approximate)**

- Brain stimulation improving recall in epilepsy patients: Ezzyat et al., 2018, *Nature Communications*, "Closed-loop stimulation of temporal cortex rescues functional networks and improves memory".
