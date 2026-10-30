# Memory Fingerprint Project: Research Report

Oct 21, 2026 · @Vishvam

## 1. Executive summary

The first project should test one narrow claim: that a person-specific model of scalp EEG recorded while a word is studied predicts whether that word is later recalled, in recording sessions the model has never seen, and adds information beyond what the word itself, its list position and the person's behaviour already predict. That is the smallest test of the Personalized Neural Memory Signature (PNMS) idea that can genuinely fail, and it can be run on a laptop with open data.

**What is already known.** Neural recordings carry reliable stimulus information (H1 is established for fMRI, MEG, EEG and intracranial data). Encoding-period activity predicts later memory above chance (H3 is established, but effects are small on scalp EEG: participant-specific classifiers in the largest open EEG memory study reached a mean AUC of about 0.60 in held-out sessions, [Li, Pazdera & Kahana 2024](https://doi.org/10.1038/s41467-024-46926-0)). Content-specific reinstatement during retrieval has been shown with fMRI, MEG/EEG and single neurons (H4 is supported for categories and some individual items). Closed-loop intracranial stimulation timed by a memory decoder improved word-list recall modestly in epilepsy patients (H7 has early causal evidence). Recreating a specific human memory by replaying a stored pattern (H8) has no human evidence; the closest work is optogenetic engram reactivation in mice.

**What is not known.** Whether a compact, person-specific signature stays identifiable across weeks and contexts (H5), whether neural data improves cue selection beyond a cheap behavioural or AI model (H6), and whether any intervention can restore one particular memory rather than raise average performance.

**Recommended start.** Primary dataset: the Penn Electrophysiology of Encoding and Retrieval Study, experiment ltpFR (PEERS1-3), on OpenNeuro as [ds004395](https://openneuro.org/datasets/ds004395) (CC0, no registration, 237 ltpFR participants, median 20 sessions each, about 2.3 TB in total, roughly 10 GB per participant). Internal replication: the ltpFR2 participants in the same archive. External validation: the intracranial free-recall dataset [ds004789](https://openneuro.org/datasets/ds004789) (281 participants). A single-neuron recognition dataset ([DANDI:000004](https://dandiarchive.org/dandiset/000004/0.220126.1852), 6.2 GB) is the best cheap side project for the recognition and familiarity questions.

**Verdict in one line.** The PNMS idea is a reframing of well-developed lines of research (subsequent-memory decoding, reinstatement analysis, closed-loop memory stimulation), not a new mechanism. Its most defensible original contribution is rigour: showing, with strict confound control and session-level generalisation, how much person-specific neural information actually exists for a single remembered item, and whether it is enough to justify anything beyond a good external memory aid.

## 2. Honest scientific verdict

Two of the eight hypotheses are established, three are partly supported, and three are open or beyond current technology. Evidence for one does not carry over to the next: each step adds a new requirement (no stimulus at test, a later day, a causal effect, a specific memory).

| Hypothesis | Status of evidence | Kind of evidence | Testable with public data? | What would settle it |
| --- | --- | --- | --- | --- |
| H1. Neural data carry reproducible stimulus information | Established | Predictive (decoding), many labs, all modalities | Yes (THINGS-EEG, NSD, Wakeman-Henson, PEERS) | Already settled for categories and many single images; open only for fine detail on scalp EEG |
| H2. A personal model can separate item information from confounds | Partly supported | Predictive; depends heavily on design | Yes, partly | Show that neural features add predictive value over a model of stimulus, position, task and behaviour, in held-out sessions |
| H3. Remembered and forgotten items differ at encoding | Established at group level; weak per trial | Correlational and predictive (subsequent-memory effect) | Yes (PEERS, RAM, DANDI:000004) | Trial-level AUC on scalp EEG is about 0.6; the open question is how much of it survives confound control |
| H4. Item information returns at retrieval without the stimulus | Supported for categories; limited for single items | Correlational (reinstatement) | Partly (PEERS recall periods, RAM, NSD imagery) | Item-specific encoding-retrieval similarity above matched controls, at the single-trial level |
| H5. Representations stay identifiable across sessions and contexts | Unresolved for item-specific signatures | Mixed; drift is documented | Partly (PEERS has about 20 sessions per person, with repeated words) | Cross-session decoding of the same item, with the stimulus held out |
| H6. A model improves cue selection or predicts retrieval | Prediction: partly. Cue selection: untested in this form | Predictive | Prediction yes; cue selection needs a new experiment | A prospective study where model-chosen cues beat matched cues on recall |
| H7. A personal intervention improves retrieval or encoding | Early causal evidence, modest effects, invasive | Causal, small samples, epilepsy patients | No | Pre-registered, blinded, sham-controlled trials with replication |
| H8. Direct manipulation reinstates a specific memory | No human evidence; rodent optogenetics only | Causal in animals | No | Would need cell-level access in humans that no approved technology provides |

**The core idea is scientifically reasonable as a measurement question and speculative as an intervention.** The PNMS is best treated as a statistical model of the neural correlates of one item, valid for one person, one recording setup and one period of time. It is not a stored copy of the memory, and nothing in current evidence says that playing it back would restore the memory.

**The strategy most supported by evidence is retrieval facilitation, not pattern recreation.** Better cues, better timing, and better external records help people with partly intact memory today. Recreating a stored pattern assumes the original pattern is still the right target after consolidation, and that it can be written into the brain at the right resolution. Neither assumption is supported in humans.

## 3. Refined definition of the Personalized Neural Memory Signature

**Recommended technical definition.** A PNMS is a person-specific, probabilistic model that maps neural measurements recorded in a defined task context to (a) the identity or features of an experienced item and (b) the memory state of that item (encoded, recalled, recognised, familiar only), together with an estimate of its own uncertainty and of how its validity changes across sessions. It is defined relative to a recording setup, a task and a time window, and it is validated only by out-of-sample prediction.

**"Neural fingerprint" is misleading and should be dropped from technical writing.** A fingerprint is fixed, unique and readable from one sample. Memory-related activity is none of these: it changes with consolidation and every retrieval, overlaps between similar experiences, and is only partly visible to any one sensor. The term also already means something else in neuroimaging: "connectome fingerprinting" identifies people, not memories, from functional connectivity (Finn et al., 2015, *Nature Neuroscience*). Prefer "item-specific neural signature" or simply "person-specific memory decoder".

### Ten states that must not be confused

| State | What happens | Typical neural marker | What a decoder can claim |
| --- | --- | --- | --- |
| 1. Perceiving an image | Sensory and semantic processing of a present stimulus | Visual cortex responses from about 100 ms, category information by about 150-200 ms | Stimulus information, not memory |
| 2. Recognising a seen image | Matching the input to a stored trace | Old/new ERP effects; repetition suppression | Memory of exposure, possibly familiarity only |
| 3. Learning information about an image | Forming new associations | Hippocampal and prefrontal engagement | Associative encoding |
| 4. Successful episodic encoding | The experience is bound to its context and later retrievable | Subsequent-memory effects (theta decrease, high-frequency increase on EEG/iEEG) | A probability that the item will be remembered |
| 5. Consolidation | Stabilisation and reorganisation over hours to years, partly during sleep | Replay, sharp-wave ripples, spindle coupling | Usually invisible to the first project |
| 6. Cued retrieval | A cue reactivates the trace via pattern completion | Hippocampal activity, cortical reinstatement | Item reinstatement, if the cue is not the item itself |
| 7. Familiarity without recollection | A feeling of prior exposure without detail | Earlier frontal old/new effect; perirhinal involvement | Recognition without episodic detail |
| 8. Reinstatement | Partial return of the encoding pattern during retrieval | Encoding-retrieval similarity above chance | A correlate of retrieval, not proof of re-experience |
| 9. Artificial influence | Stimulation or feedback alters a memory process | Behavioural change in a controlled trial | Causal effect on performance, rarely on content |
| 10. Reconstruction after damage | Rebuilding information from external records or residual traces | None specific | External information, not recovered biology |

**Visual decoding versus memory decoding.** Visual decoding reads the stimulus that is present; it works without any memory at all. Memory decoding must show information about an item when the item is absent, or show that the neural response predicts a later memory outcome after the stimulus has been controlled. Most impressive "mind reading" results, including image reconstruction from fMRI, are visual decoding.

**Correlate versus cause.** A pattern that predicts recall may reflect attention, arousal or fatigue that also drive recall. Only an intervention that changes the pattern and then changes memory, with the alternatives controlled, shows a causal role. Even then it shows that the process matters, not that the pattern is the memory.

**Why one image gives different responses, and different images give similar ones.** Responses vary with attention, adaptation from earlier presentations, eye position, fatigue, arousal, impedance changes and noise. Different experiences overlap because the brain codes shared features (category, emotion, spatial layout) with shared populations, and because scalp sensors sum activity from very large areas.

**Hippocampus and cortex.** In indexing accounts, the hippocampus stores a sparse index that binds distributed cortical features; pattern separation (dentate gyrus) keeps similar episodes apart; pattern completion (CA3) lets a partial cue reactivate the full pattern. Cortex holds the content. Plasticity in both changes the trace over time, so the "signature" of an item is not fixed.

### Which form should the stored representation take?

| Form | Strength | Limitation | Use in first project |
| --- | --- | --- | --- |
| Static feature vector | Simple, works with linear models | Discards timing; assumes one fixed pattern | Yes, as the baseline (spectral power per channel) |
| Time-resolved trajectory | Captures when information appears | More parameters, needs more trials | Yes, as temporal generalisation |
| Probabilistic representation | Carries uncertainty, supports decisions | Needs calibration checks | Yes: report calibrated probabilities |
| Association graph | Mirrors how cues link memories | Needs many related items; hard to validate neurally | Later (Architecture B) |
| Population relationship model | Can capture network state | Hard to estimate from scalp EEG | Later |
| Dynamical-system model | Could guide when to stimulate | Data-hungry; identifiability problems | Later (Architecture C) |
| Combination | Most realistic | Most ways to overfit | Only after each part is validated alone |

The first project should store a regularised linear model on spectral features plus calibrated output probabilities. It is the form most likely to give an honest answer with the data available.

## 4. Current scientific evidence and key research precedents

The evidence is strongest for decoding what a person is perceiving, solid but small for predicting which items will be remembered, moderate for detecting reinstatement during retrieval, early and modest for improving memory with stimulation, and absent in humans for writing back a specific memory. Labels used below: **E** established (replicated across labs), **Em** emerging (shown, limited replication), **P** plausible extrapolation, **S** speculation. Full references, with which ones were opened during this review, are in the References section.

### A. Neural representations

| Finding | Population, method, n | Type | Replicated? | What it does not establish | Label |
| --- | --- | --- | --- | --- | --- |
| Object categories are decodable from distributed ventral temporal patterns (Haxby et al., 2001, *Science*) | Healthy adults, fMRI, n = 6 | Predictive | Yes, extensively | Memory; single-item identity | E |
| Category structure is shared between human and monkey IT, measured by representational similarity analysis (Kriegeskorte et al., 2008, *Neuron*) | Humans fMRI n = 4, monkeys single units | Correlational | Yes | Causal use of the code | E |
| Object information appears in MEG within about 100-150 ms and maps onto ventral stream stages (Cichy, Pantazis & Oliva, 2014, *Nat Neurosci*) | Healthy adults, MEG + fMRI, n = 16 | Predictive | Yes | Memory | E |
| Scalp EEG decodes object concepts in rapid presentation (THINGS-EEG; [Grootswagers et al., 2022, *Sci Data*](https://doi.org/10.1038/s41597-021-01102-7)) | Healthy adults, 64-ch EEG, n = 50, 22,248 images | Predictive | Yes (THINGS-EEG2) | Memory; individual-image decoding is weak per trial | E |
| fMRI responses to natural scenes support image reconstruction with generative models (Natural Scenes Dataset, [Allen et al., 2022, *Nat Neurosci*](https://doi.org/10.1038/s41593-021-00962-x); Takagi & Nishimoto, CVPR 2023) | 8 adults, 7T fMRI, 30-40 sessions each | Predictive | Yes, several groups | Reconstructions rely heavily on generative priors; this is perception, not recall | E/Em |
| Single human MTL neurons respond invariantly to specific people or objects (Quiroga et al., 2005, *Nature*) | Epilepsy patients, microwires, 8 patients | Correlational | Yes | That one neuron "stores" a memory | E |

### B. Memory mechanisms and memory-related signals

| Finding | Population, method, n | Type | Replicated? | What it does not establish | Label |
| --- | --- | --- | --- | --- | --- |
| Subsequent-memory effect: activity at encoding predicts later memory (Brewer et al., 1998; Wagner et al., 1998, *Science*; review Paller & Wagner, 2002, *Trends Cogn Sci*) | Healthy adults, fMRI | Correlational | Yes, hundreds of studies | That the measured region is necessary | E |
| Spectral subsequent-memory effects on scalp EEG and iEEG: broad theta decrease and high-frequency increase ([Long, Burke & Kahana, 2014, *NeuroImage* 84](https://doi.org/10.1016/j.neuroimage.2013.08.052)) | Scalp EEG n = 102 (PEERS); iEEG n = 93 | Correlational | Yes | Trial-level predictability; high-frequency scalp effects may contain muscle or saccade artefacts | E |
| Participant-specific EEG classifiers predict recall in held-out sessions, mean AUC 0.60 at encoding; retrieval classifiers separate correct recalls from intrusions, AUC 0.59 ([Li, Pazdera & Kahana, 2024, *Nat Commun* 15:2981](https://doi.org/10.1038/s41467-024-46926-0)) | PEERS ltpFR2, 88 analysed participants, about 22 sessions each | Predictive | Within the same lab | Contribution beyond item-level difficulty or a behavioural model was not the focus; no cross-subject comparison | Em |
| Category-specific cortical patterns reappear before free recall (Polyn et al., 2005, *Science*) | Healthy adults, fMRI, n = 9 | Correlational | Yes (many reinstatement studies; review Danker & Anderson, 2010) | Item-level content | E |
| Item-specific encoding-retrieval similarity in hippocampus and cortex (Staresina et al., 2012, *J Neurosci*; Ritchey et al., 2013, *Cereb Cortex*) | Healthy adults, fMRI | Correlational | Partly | Causality | Em |
| Reconstruction from memory runs in reverse order to perception (Linde-Domingo et al., 2019, *Nat Commun*) | Healthy adults, EEG | Predictive | Partly | Single-item retrieval on single trials | Em |
| Hippocampal neurons that fired to a clip fire again before it is freely recalled (Gelbard-Sagiv et al., 2008, *Science*) | Epilepsy patients, microwires, n = 13 | Correlational | Yes, conceptually | That recall needs those neurons | E/Em |
| Neurons signal memory strength and confidence during recognition ([Rutishauser et al., 2015, *Nat Neurosci*](https://doi.org/10.1038/nn.4041); open data [Faraut et al., 2018](https://doi.org/10.1038/sdata.2018.10)) | Epilepsy patients, MTL microwires, dozens of sessions | Correlational | Yes, same group and others | Recall without the stimulus | Em |
| Engram cells: reactivating cells tagged during learning drives recall-like behaviour; a false fear memory can be created (Liu et al., 2012, *Nature*; Ramirez et al., 2013, *Science*; review Josselyn & Tonegawa, 2020, *Science*) | Mice, optogenetics with activity-dependent labelling | Causal | Yes, many labs | Anything about human episodic memory content | E (rodents) |
| Retrograde amnesia and early Alzheimer-model memory loss can be retrieval failures: direct engram activation restores behaviour (Ryan et al., 2015, *Science*; Roy et al., 2016, *Nature*) | Mice | Causal | Partly | That the same holds in human Alzheimer's disease | Em (rodents) |
| Retrieved memories become labile and can be modified (reconsolidation; Nader, Schafe & LeDoux, 2000, *Nature*) | Rats | Causal | Yes, with boundary conditions and failures to replicate in some human paradigms | Clinical usefulness | E/Em |
| Pattern separation deficits with age and in amnestic MCI (Yassa & Stark, 2011, *Trends Neurosci*, review) | Humans, high-resolution fMRI and behaviour | Correlational | Yes | Specific mechanism of failure | E |
| False memories are easily induced and feel real (Roediger & McDermott, 1995) | Healthy adults, behaviour | Causal (manipulation) | Yes, very robust | — | E |
| Representations drift across days even when behaviour is stable (Ziv et al., 2013, *Nat Neurosci*; review Rule, O'Leary & Harvey, 2019) | Mice, calcium imaging | Observational | Yes | How much drift scalp EEG signatures show | E (rodents) |

### C. Recording and decoding

Recording technology sets a hard ceiling. Scalp EEG and MEG integrate activity over square centimetres of cortex and see hippocampus weakly; fMRI gives millimetre detail but measures slow blood flow; intracranial and single-neuron recordings are precise but exist only in clinical patients with electrodes placed for clinical reasons. High-frequency scalp EEG "gamma" can be produced by miniature eye movements (Yuval-Greenberg et al., 2008, *Neuron*) and muscle activity (Whitham et al., 2007, *Clin Neurophysiol*), which matters directly for memory decoders that use high frequencies. See Section 5 for the full comparison.

### D. Stimulation and intervention

| Finding | Population, method, n | Type | Replicated? | What it does not establish | Label |
| --- | --- | --- | --- | --- | --- |
| Entorhinal deep-brain stimulation during learning improved spatial memory (Suthana et al., 2012, *NEJM*) | Epilepsy patients, n = 7 (6 in the key test) | Causal | Contradicted by the next row | Generality | Em, contested |
| Entorhinal and hippocampal stimulation during encoding impaired memory ([Jacobs et al., 2016, *Neuron*](https://doi.org/10.1016/j.neuron.2016.10.062)) | Epilepsy patients, n = 49 | Causal | Yes | That all stimulation is harmful | E |
| Stimulation timed by a decoder during poor-encoding states improved recall (Ezzyat et al., 2017, *Curr Biol*; [Ezzyat et al., 2018, *Nat Commun*](https://doi.org/10.1038/s41467-017-02753-0)) | Epilepsy patients with intracranial electrodes; 2018 study about 25 patients | Causal | Same consortium; modest effect sizes | Restoration of a specific memory | Em |
| Multi-input multi-output (MIMO) model-based hippocampal stimulation improved recall (Hampson et al., 2018, *J Neural Eng*) | Epilepsy patients, small sample | Causal | Not independently | Mechanism; generality; specific memories | Em, needs replication |
| Theta-burst microstimulation in entorhinal area improved memory specificity (Titiz et al., 2017, *eLife*) | Epilepsy patients, small sample | Causal | Limited | Clinical value | Em |
| Repetitive TMS to a parietal site connected to hippocampus improved associative memory (Wang et al., 2014, *Science*) | Healthy adults, n = 16 | Causal | Partly, mixed replications | Specific memories; durability | Em |
| Rhythm-targeted transcranial alternating current stimulation improved working or long-term memory in older adults (Reinhart & Nguyen, 2019; Grover et al., 2022, *Nat Neurosci*) | Older adults, n in the tens per group | Causal | Not yet broadly | Episodic recall of specific items | Em |
| Sounds or odours replayed during sleep strengthen associated memories (targeted memory reactivation; Rasch et al., 2007, *Science*; meta-analysis Hu et al., 2020, *Psychol Bull*) | Healthy adults | Causal | Yes, with a modest pooled effect | Large clinical benefit | E/Em |
| Fornix deep-brain stimulation in mild Alzheimer's disease: phase II showed no overall cognitive benefit; possible benefit at 65 and older (Lozano et al., 2016, *J Alzheimers Dis*). The phase III-style ADvance II trial ([NCT03622905](https://clinicaltrials.gov/study/NCT03622905)) has a listed completion date of 19 Feb 2024 and [no reported results](https://fdaaa.trialstracker.net/trial/NCT03622905) as of this review | Mild AD, n = 42 in phase II | Causal (RCT) | — | Efficacy | Em, unresolved |
| Focused ultrasound can open the blood-brain barrier in hippocampus safely in small samples (Rezai et al., 2020, *PNAS*) | AD patients, n = 3 | Safety/feasibility | Early | Memory benefit | Em |
| Real-time fMRI neurofeedback trains sustained attention (deBettencourt et al., 2015, *Nat Neurosci*) | Healthy adults | Causal | Partly | Memory for specific items | Em |

### E. Clinical translation

Disease-modifying antibodies now exist but give modest slowing, not memory restoration: lecanemab slowed decline on CDR-SB by 0.45 points over 18 months versus placebo (van Dyck et al., 2023, *NEJM*), and the EU authorised it in April 2025 [only for ApoE ε4 non-carriers or heterozygotes with confirmed amyloid](https://nordiclifescience.org/eu-approves-leqembi-for-treatment-of-early-alzheimers-disease/). No memory-decoding or memory-stimulation device has regulatory approval for treating Alzheimer's disease. The best supported non-drug interventions for everyday memory remain external memory aids and goal-oriented cognitive rehabilitation (Section 17).

**Negative and contradictory findings to keep in view.** Entorhinal stimulation both helped (Suthana, 2012) and harmed (Jacobs, 2016) memory. Fornix DBS failed its primary endpoint. Scalp-EEG high-frequency effects can be artefacts. Engram results are almost entirely rodent fear and contextual memories. Image reconstructions owe much of their realism to generative priors rather than to the brain data.

## 5. Full technology comparison

For the next two years the useful pathway is open EEG/iEEG data plus simple, well-validated models, then (only if justified) a lab collaboration using EEG or MEG. Invasive and cell-specific methods belong to collaborators with clinical or animal programmes. Resolution figures are typical orders of magnitude, not device specifications.

Classification key: **C** computationally feasible today; **L** needs an equipped research lab; **Cl** approved clinical research only; **Pre** primarily preclinical; **F** speculative future.

### Recording

| Approach | What it measures | Spatial / temporal resolution | Access and cost | Main limitation for memory | Class | Fit for this project |
| --- | --- | --- | --- | --- | --- | --- |
| EEG / high-density EEG | Summed postsynaptic potentials at the scalp | Centimetres / milliseconds | Cheap; huge open datasets | Weak hippocampal access; artefacts from eyes and muscles | C (open data), L (new data) | Best first modality |
| MEG | Magnetic fields of the same currents | About 1 cm with source modelling / ms | Expensive facility; open data exist | Hippocampus still hard; head movement | C / L | Strong second modality (e.g. Wakeman-Henson) |
| fMRI (incl. 7T) | Blood-oxygen changes | 1-2 mm (7T below 1 mm) / seconds | Expensive; NSD and many open sets | Too slow for real-time item tracking; not portable | C / L | Best for representational questions, not for a device |
| fNIRS | Cortical blood oxygenation via light | 1-3 cm, surface only / seconds | Portable, moderate cost | Cannot see hippocampus; low information | L | Low |
| Intracranial EEG / ECoG | Local field potentials from implanted electrodes | Millimetres / ms | Only in clinical patients; large open data (RAM) | Electrode placement is clinical, not chosen; epilepsy confounds | C (open data), Cl | Validation dataset |
| Single neurons (microwires, Utah arrays) | Spiking of individual neurons | Single cells / sub-ms | Clinical research centres; open DANDI sets | Few neurons sampled; patient population | C (open data), Cl | Side project on recognition |
| Calcium imaging, two-photon | Activity of identified cells | Cellular / about 100 ms | Animal labs | Not used in humans | Pre | Background evidence only |
| Multimodal fusion (EEG-fMRI, MEG-fMRI) | Combines time and space | Best of both, with alignment errors | Labs; some open sets | Complexity; weak gains when one modality dominates | L | Later, only for a specific question |

### Modelling

| Approach | Strength | Limitation | Class | Fit |
| --- | --- | --- | --- | --- |
| Classical decoding (regularised logistic regression, LDA, shrinkage) | Robust with few trials; interpretable | Linear assumptions | C | First choice |
| Representational similarity analysis | Compares neural and model geometry; handles many items | Needs repeated items or a good model of items | C | Secondary analyses |
| Machine learning / deep learning (EEGNet-style CNNs, transformers) | Learns features | Overfits small data; harder to audit for shortcuts; repeated benchmarks show little gain over linear models on spectral features for memory prediction (e.g. Arora et al., 2018, *J Neural Eng*, iEEG) | C | Only as a comparison after the linear baseline |
| Generative models (diffusion, VAE) | Can reconstruct images or text from neural data | Priors produce plausible output with little brain information | C | Not for the first project |
| State-space / dynamical models | Track hidden brain states over time | Identifiability; data hunger | C | Later, for timing interventions |
| Personalised models with population priors (hierarchical, transfer) | Use other people's data to help one person | Need careful evaluation | C | Secondary question F |

### Influencing memory

| Approach | Mechanism | Evidence | Class | Fit |
| --- | --- | --- | --- | --- |
| Natural sensory cueing | Cues trigger pattern completion | Very strong (behavioural memory science) | C / L | High; central to Architecture B |
| Associative retrieval cues (people, places, times) | Uses the brain's own links | Strong | C / L | High |
| Neurofeedback | Train people to enter good encoding states | Early | L | Moderate |
| TMS / tACS / tDCS | Modulates cortical excitability or rhythms | Mixed, modest | L (with ethics approval) | Low for the first years |
| Closed-loop intracranial stimulation | Stimulate when a decoder detects poor encoding | Early causal, modest | Cl | Collaborator only |
| Existing clinical memory prostheses | None approved; research MIMO systems only | Early | Cl | Collaborator only |
| Focused ultrasound (neuromodulation or barrier opening) | Deep targets without surgery | Early safety data | Cl | Watch |
| Optogenetics, chemogenetics, activity-dependent labelling | Control of identified cells | Strong in rodents | Pre | Background only |
| Pharmacological or plasticity approaches | Modify encoding or consolidation (e.g. levetiracetam in aMCI hyperactivity, Bakker et al., 2012, *Neuron*) | Mixed | Cl | Outside scope |
| AI-assisted external memory | Lifelogging, retrieval of personal records, reminders | Strong for daily function | C | High: the benchmark any neural system must beat |
| Future high-resolution non-invasive interfaces | Not yet available | None | F | Monitor |

**Combinations worth having:** EEG plus eye tracking (to remove saccade confounds); EEG plus a strong behavioural model (to show neural added value); natural cues plus an AI memory assistant plus, later, a neural readout. **Combinations that mainly add cost:** fNIRS with EEG for hippocampal questions; deep learning on a few hundred trials per person; stimulation before a validated decoder exists.

## 6. Noise-control and experimental-design strategy

The central rule: never subtract a universal baseline and call the remainder "memory". Instead, model every known source of variance explicitly, and require the neural model to beat a non-neural model on held-out data. Memory information is whatever neural data predicts about memory that the stimulus, the task and the person's behaviour do not.

### Where the variance in a "childhood home" response comes from, and how to control it

| Source | How it leaks into a decoder | Control |
| --- | --- | --- |
| Visual properties (brightness, contrast, size, word length) | Bright or long items may also be more memorable | Match across conditions; enter as covariates; test decoders on new items |
| Attention and eye movements | Saccades produce scalp "gamma"; attentive trials are remembered better | Eye tracking where available; ICA for ocular artefacts; saccade-related regressors; compare low-frequency-only and full-spectrum models |
| Familiarity and prior exposure | Repeated items are both familiar and better remembered | Code number of previous exposures; hold out items, not just trials |
| Semantic content | Some words are easier to recall for everyone | Estimate item recallability from other participants only (never from the test person or test session) |
| Emotional significance | Emotion boosts memory and changes EEG | Keep it as a variable of interest; measure it; do not regress it out of the primary analysis |
| Associated memories | The construct of interest in later studies | Use designs where association strength is manipulated |
| Task | Different judgements change EEG and memory | Balance task across outcome; include task as a covariate |
| General cognitive state (fatigue, time on task) | Late-session trials are noisier and less remembered | Include list number, time in session; z-score features within session |
| Physiological variation (heart, breathing, sweat) | Slow drifts | High-pass filtering; within-session normalisation |
| Recording artefacts (bad channels, impedance changes, line noise) | Session-specific offsets confound session-level labels | Robust re-referencing; artefact rejection decided before looking at labels |

### Baselines: what to use and why

Use several, each for a different purpose. A **pre-stimulus baseline** removes slow drifts within a trial. **Within-session z-scoring** removes day-to-day differences in amplitude. **Matched control items** (same task, similar features, different memory outcome) are the real baseline for memory. **Resting-state recordings** are useful for characterising a person but not for subtraction, because rest is not a neutral version of the task. A **calibration set** of standard stimuli each session is valuable in prospective studies to measure drift.

### Statistical controls and what each one guards against

- **Matched conditions** remove differences you know about.
- **Nuisance regression** removes linear effects of measured confounds; apply it inside cross-validation folds.
- **Multivariate pattern analysis and RSA** test whether information is present without needing one region.
- **Regularisation** limits overfitting in high-dimensional features.
- **Cross-validation by session, item and participant** tests the generalisation you actually claim (Section 12).
- **Permutation tests** that shuffle labels within the same structure (within session, within list) give a valid null.
- **Negative controls**: decode the outcome from pre-stimulus baseline only, from shuffled item identities, and from the artefact channels only. Any of these succeeding means a shortcut.
- **Positive controls**: decode serial position or task type, which must work if the pipeline is correct.
- **Temporal generalisation** shows whether the same code holds over time or changes.
- **Added-value tests**: compare a behavioural-plus-stimulus model with the same model plus neural features, using a paired, out-of-sample metric.

**Keeping emotion and context.** Confound control should be limited to variables that are not part of the claim. If the claim is "neural activity predicts memory beyond what the item predicts", item features are controlled. If the claim is "emotional context drives memory", emotion must stay in. Write down in advance which variables are nuisance and which are of interest.

### How decoders cheat, and how to catch it

| Shortcut | Example | Detection |
| --- | --- | --- |
| Stimulus identity | Same word in train and test sessions | Group-aware splits by item |
| Timing | Recalled items cluster at list start (primacy) | Serial position in the baseline model; resampling within positions |
| Session label | Good sessions have both higher recall and different noise | Leave-one-session-out; within-session normalisation |
| Eye movements and muscle | High-frequency power tracks effort | Low-frequency-only model; frontal and temporal channel exclusion test |
| Labels in metadata | A column filled in only for remembered items | Inspect every column; build features only from the EEG |
| Preprocessing leakage | ICA or scaling fitted on all data | Fit inside folds, or use label-blind steps only |

### Full experimental design and what the first project needs

| Condition | Purpose | First computational project | Later prospective study |
| --- | --- | --- | --- |
| 1. Later remembered item | Positive class | Essential (PEERS recall) | Yes |
| 2. Matched later forgotten item | Negative class | Essential (matched by position, task, item recallability) | Yes |
| 3. Novel item | Separate novelty from memory | Approximated by first exposure of a word | Yes |
| 4. Familiar item | Prior exposure | Approximated by repeated words across sessions | Yes |
| 5. Intentional versus incidental learning | Strategy effects | Partly: PEERS ltpFR has no-task lists and size/animacy judgement lists, but all lists are followed by recall tests, so learning is never truly incidental | Yes |
| 6. Recognition versus recollection | Familiarity versus detail | Secondary: PEERS ltpFR has a recognition test with confidence | Yes (with remember/know) |
| 7. Encoding versus retrieval | Reinstatement | Secondary (recall periods) | Yes |
| 8. Relevant versus irrelevant cues | Cue selection (H6) | Not possible with free recall | Essential |
| 9. Baselines and controls | Validity | Essential | Essential |

## 7. Comparison of reactivation mechanisms

Retrieval facilitation (Strategy B) is better supported than direct pattern recreation (Strategy A) by every line of human evidence. Only cue-based methods have shown effects on *specific* memories in humans; every stimulation method so far has changed *average* performance.

| Route | Proposed mechanism | Evidence (type) | Achievable today | Main limitation | Decisive test | Specific memory or general performance? |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Natural sensory cueing | Partial input triggers hippocampal pattern completion | Strong (causal, behavioural) | Yes | Needs the right cue; cue may suggest false content | Recall accuracy with versus without cues, scored against verified records | Specific |
| 2. Model-optimised cues | Choose the cue most likely to succeed for this person | Untested in this form (cue effectiveness models exist in behaviour) | Computationally yes | Must beat a behavioural cue model | Randomised: model-chosen cue versus best behavioural cue | Specific |
| 3. Associative retrieval | Retrieve via linked people, places, times | Strong (behavioural) | Yes | Interference from related memories | Same as 1, with interference measures | Specific |
| 4. Neurofeedback | Train or wait for a good brain state, then present | Early (causal in attention, preliminary in memory) | Lab | Small effects; placebo effects | Sham-feedback controlled trial | General |
| 5. Non-invasive stimulation (TMS, tACS, tDCS) | Shift network excitability or rhythms | Mixed (causal, small) | Lab with approval | Low spatial precision | Pre-registered sham-controlled replication | General |
| 6. State-dependent closed-loop stimulation (non-invasive or sleep cueing) | Act when the brain is receptive, e.g. slow-wave up-states | Emerging (causal) | Lab | Timing precision | Phase-locked versus random timing | Can bias specific items when paired with a cue (targeted memory reactivation) |
| 7. Intracranial electrical stimulation | Alter hippocampal or cortical activity during encoding | Mixed: helps or harms depending on site and timing (causal) | Clinical research only | Invasive; patient population | Multi-site blinded trials | General so far |
| 8. Model-derived stimulation (MIMO-type) | Write a model-predicted pattern into hippocampus | Early (causal, small n) | Clinical research only | Very limited electrode coverage; replication | Independent replication with item-level outcomes | Claimed partly item-specific; unproven |
| 9. Optogenetic engram reactivation | Activate cells tagged at learning | Strong in rodents (causal) | Animal labs only | Requires genetic access to cells | Not applicable to humans now | Specific in rodents |
| 10. Emerging interfaces (focused ultrasound, high-density micro-ECoG) | Deeper or finer targeting | Early safety data | Clinical research | Spatial specificity still coarse for memories | Feasibility trials | Unknown |
| 11. Hybrid: natural cues + external records + neural feedback | Use neural readout only to time or choose cues | Not yet tested as a whole | Partly | Neural part may add nothing | Ablation: hybrid with and without neural input | Specific |
| 12. Future methods (cell-type-specific non-invasive modulation) | Plausible but undeveloped | None in humans | No | Physics and biology of delivery | — | Unknown (S) |

**Is exact pattern recreation necessary?** Probably not, and possibly harmful. Pattern completion means a partial cue is normally enough, provided the stored trace survives. Retrieval itself changes traces (reconsolidation), and representations drift, so the "original" pattern may no longer be the one that supports the memory. Engram studies reactivate cells, not recorded patterns, and they work because the cells are the trace. Scalp or electrode recordings sample a tiny, mixed fraction of the relevant activity; replaying that fraction is not the same as reactivating the trace.

**Distinguishing true retrieval from familiarity, suggestion and false memory.** Every intervention study must:

1. Score recall against an independent record (the stimulus list, photographs, diaries), never against the participant's confidence alone.
2. Include lure items and plausible but false details, and report false-alarm and intrusion rates alongside hits.
3. Separate recollection from familiarity with remember/know judgements or source-memory questions.
4. Use cues that do not contain the target information, and blind both participant and experimenter to condition.
5. Report confidence-accuracy calibration: an intervention that raises confidence more than accuracy is harmful.

## 8. Recommended computational proof of concept

**Project title:** *How much of a remembered word is in a person's EEG? Person-specific encoding decoders tested against a non-neural memory model across sessions.*

The proof of concept asks whether a person-specific EEG model of the encoding moment carries information about later recall that a strong non-neural model does not already have, when tested on whole sessions and words the model has not seen. It sits exactly on the weakest link between the vision and the evidence: if neural data cannot beat a behavioural model at predicting memory for words, there is little reason to expect it to select better cues for real-life memories, and the case for neural hardware in Architecture B weakens.

**Why this question rather than the alternatives (Part VI 6.3).**

| Candidate question | Verdict | Reason |
| --- | --- | --- |
| A. Decode images or categories | Not first | Already established (H1); answers nothing about memory |
| B. Predict later memory | Already shown on this data (Li et al., 2024) | A replication alone is weak; useful as a positive control |
| **C + G. Predict later memory beyond stimulus and behaviour** | **Primary** | Tests H2, H3 and part of H5 together; can fail; novel in its controls |
| D. Find encoding patterns again at retrieval | Phase 2 | Needs reliable item-level signals first |
| E. Generalise across sessions or stimuli | Built into the primary split | Leave-one-session-out with items held out |
| **F. Personal versus cross-participant model** | **Secondary 1** | Directly tests the "personalised" claim |
| H. Memory information without the stimulus | Phase 2 | Requires D |
| (Extra) Encoding signal predicts recognition for unrecalled words | **Secondary 2** | Separates memory strength from recall; uses PEERS recognition data |

**What a positive result would establish.** That scalp EEG at encoding contains person-specific information about later memory that is not explained by the word, its position, the encoding task, prior exposure or time in session, and that this information survives a change of day. **What it would not establish.** That the information is item-specific content (it is more likely a state signal such as attention), that it is causal, or that it would help anyone remember anything.

**What a negative result would establish.** That on scalp EEG, at the encoding moment, neural data adds little to a non-neural model. That would argue for building Architecture B around behaviour and AI first and for moving any neural work to higher-resolution data (iEEG, MEG).

## 9. Dataset comparison and selection

**Selection: PEERS ltpFR (OpenNeuro ds004395) as primary, PEERS ltpFR2 participants as internal replication, RAM FR1 intracranial (ds004789) as external validation.** Sizes and counts below were measured on 21 Oct 2026 by listing the public OpenNeuro and DANDI storage buckets directly, unless marked otherwise. Follow-up 1 (Stage 2 of this thread) re-checks these in detail.

| Dataset | Modality | Participants | Task and labels | Encoding + retrieval? | Repeated sessions | Size, format | Access | Tests | Cannot test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [PEERS, ds004395](https://openneuro.org/datasets/ds004395) (Kahana lab) | Scalp EEG, 129-ch EGI or 128-ch BioSemi | 364 in archive; ltpFR: 237 (median 20 sessions); ltpFR2: 127 (median 24); VFFR: 57 | Free recall of word lists; ltpFR adds size/animacy encoding tasks, final free recall and recognition with 1-5 confidence | Yes (study words, spoken recall onsets) | Yes, about 20 per person | 9.6 TB total; ltpFR 2.3 TB; about 0.5-0.7 GB per session; BIDS, EDF/BDF | CC0, no registration | H1 (weak), H2, H3, H5, F, G; recognition | Images, cue selection, causality |
| [RAM FR1, ds004789](https://openneuro.org/datasets/ds004789) | Intracranial EEG (depth + grid) | 281 | Delayed free recall of words | Yes | Some participants | 619 GB; BIDS, EDF | CC0 | Same as PEERS with much better signal; external validation | Healthy brains; consistent electrode placement |
| [RAM catFR1, ds004809](https://openneuro.org/datasets/ds004809) | Intracranial EEG | Not counted here | Categorised free recall | Yes | Some | Not measured | CC0 | Semantic clustering, category reinstatement | As above |
| [Human MTL single neurons, DANDI:000004](https://dandiarchive.org/dandiset/000004/0.220126.1852) ([Chandravadia et al., 2020](https://doi.org/10.1038/s41597-020-0415-9); [Faraut et al., 2018](https://doi.org/10.1038/sdata.2018.10)) | Single units, hippocampus and amygdala | 59 subjects (87 files) | Learning block with a category judgement on each image, then new/old recognition with confidence | Yes (learning and recognition, image present at both) | Some patients have two sessions | 6.2 GB; NWB | Open (DANDI) | H1, H3 (recognition), familiarity vs confidence | Recall without stimulus; scalp-level applicability |
| [Natural Scenes Dataset](https://registry.opendata.aws/nsd) ([Allen et al., 2022](https://doi.org/10.1038/s41593-021-00962-x)) | 7T fMRI | 8 | Continuous recognition of 9,000-10,000 scenes, 30-40 sessions | Recognition only (image present) | Yes | Very large (not stated on registry page); AWS S3, no account needed | Terms and conditions; Data Access Agreement form required for the Data Manual | H1, H5, recognition memory for images | Recall without stimulus; real-time use |
| [THINGS-EEG, ds003825](https://openneuro.org/datasets/ds003825) ([Grootswagers et al., 2022](https://doi.org/10.1038/s41597-021-01102-7)) | 64-ch EEG | 50 (51 folders listed) | Rapid presentation of 22,248 images, 1,854 concepts; fixation task | No memory test | No | 59 GB | CC0 | H1 at scale | Any memory hypothesis |
| [Wakeman-Henson faces, ds000117](https://openneuro.org/datasets/ds000117) | MEG + EEG + fMRI | 16 (18 folders listed) | Famous, unfamiliar, scrambled faces; first, immediate and delayed repeats | Repetition only | MEG and MRI sessions | 90 GB | CC0 | Familiarity (famous vs unfamiliar), repetition | Later memory outcome |
| [Movie-recall fMRI, ds004042](https://openneuro.org/datasets/ds004042/versions/1.0.0) ([Lee, Chen & Hasson, 2022](https://doi.org/10.1016/j.dib.2022.108788)) | 3T fMRI + transcribed recall | 20 | Watch 10 short films, then spoken free recall | Yes (no stimulus at recall) | No | Not measured | OpenNeuro (licence not checked) | H4 reinstatement at event level | Trial-level timing; EEG |
| [Audiovisual memory EEG, ds006142](https://doi.org/10.1038/s41597-025-06203-1) (Matran-Fernandez & Halder, 2025) | 64-ch EEG | 27 | Recognition of 10-s film clips seen in life (not in lab) | Retrieval only | No | 26 GB; video stimuli not included | OpenNeuro | Real-life recognition | Encoding; controlled exposure |

**Why PEERS ltpFR beats the alternatives for the first project.** It is the only open dataset that combines non-invasive recording, a clear later-memory label on every studied item, about 20 sessions per person (needed for a personal model tested across days), words that repeat across sessions and across people (needed to estimate item difficulty independently), a recognition test with confidence, and no access barrier. NSD is the richest representational dataset but recognition-only and heavy. RAM and DANDI:000004 have better signal but come from epilepsy patients and cannot support claims about a non-invasive system.

**Practical scale.** A single ltpFR participant is about 10 GB. The pipeline processes one session at a time and deletes the raw file after extracting features, so a laptop with 20 GB free and a normal connection can run 20 participants over several days. The behavioural event files for all 3,583 ltpFR sessions are small and can be downloaded in full.

**Already done on this dataset.** Li, Pazdera and Kahana (2024) trained participant-specific classifiers on PEERS ltpFR2 and reached a mean held-out-session AUC of 0.60 for later recall, resampling to balance serial position. The original contribution here is the explicit non-neural comparison model, held-out items, the personal-versus-pooled comparison and the recognition analysis, on ltpFR rather than ltpFR2.

## 10. Exact first research question and falsifiable hypothesis

**Primary research question.** Within individual participants, does scalp EEG recorded while a word is studied predict whether that word is later freely recalled, in a held-out session and for words not used in training, better than a non-neural model given the same trials?

**Primary hypothesis (H-primary).** Across participants, the held-out AUC of the combined model (non-neural predictors + EEG features) exceeds the held-out AUC of the non-neural model alone. The quantity tested is ΔAUC = AUC(combined) − AUC(non-neural), computed per participant.

| Element | Specification |
| --- | --- |
| Unit of observation | One studied word (a `WORD` event with `trial` ≥ 1) |
| Outcome label | Recalled = 1 if the same `item_num` appears as a `REC_WORD` event in the same session and `trial`; else 0. Derived, because the events file has no recall column (verified on sub-LTP063) |
| Non-neural predictors (fixed in advance) | Serial position (1-16, categorical); encoding `task` (−1 none, 0 size, 1 animacy); list number within session; session number; number of earlier presentations of this word to this participant; word length in letters; item recallability = recall rate of that `item_num` among other participants only |
| Neural predictors | Log power at 8 log-spaced frequencies from 3 to 128 Hz, averaged over 0.2-1.6 s after word onset, per EEG channel, z-scored within session |
| Models | L2-penalised logistic regression for both models; penalty chosen by inner cross-validation on training sessions only |
| Data split | Outer: leave-one-session-out within participant. Training trials whose `item_num` appears in the test session are dropped (item held out) |
| Primary metric | ΔAUC on held-out sessions, pooled within participant |
| Primary test | One-sided Wilcoxon signed-rank test of ΔAUC > 0 across participants, α = 0.05; 95% CI from a hierarchical bootstrap (participants, then sessions) |
| Smallest effect of interest | ΔAUC = 0.01 |
| Sample | 20 ltpFR participants with at least 12 sessions and overall recall between 15% and 85%, EGI recordings only (149 eligible), chosen in ascending ID order after excluding 3 pilot participants; the exact IDs are listed in the dataset selection document (rule fixed before any confirmatory EEG is analysed) |
| Positive controls | EEG decodes serial-position block (early vs late) and encoding task above chance; the raw EEG-only recall AUC is near the published 0.60 |
| Negative controls | Labels shuffled within session × serial position (200 permutations per participant); models trained on one participant and tested on another's shuffled labels |

**Decision rules, fixed before analysis.**

- **Success:** Wilcoxon p < 0.05 **and** bootstrap 95% CI lower bound > 0 **and** point estimate ≥ 0.01, **and** the effect remains (CI lower bound > 0) in the artefact-robust model (frequencies ≤ 30 Hz, face and neck channels removed).
- **Failure:** the 90% CI for mean ΔAUC lies entirely below 0.01 (equivalence test, two one-sided tests). Neural data at encoding adds no practically useful information on scalp EEG. If the 95% CI also excludes 0, report it as information that is present but too small to use.
- **Ambiguous:** any other pattern, including an effect that disappears in the artefact-robust model (likely muscle or eye movement), or a CI that spans both 0 and 0.01 (underpowered; extend to more participants by the same rule).

**Why 0.01.** Li et al. (2024) report a raw neural AUC of 0.60 on comparable data, that is 0.10 above chance. The smallest effect of interest is set at one tenth of that raw signal: below this, any practical use (choosing cues, timing interventions) would gain almost nothing, because a decision rule driven by a 0.51 AUC is barely better than coin flipping. The threshold is set here, before any data are analysed, and must be reported even if results look better or worse.

**Decoding versus generalisation.** A within-session random split would let session-level noise and repeated words inflate accuracy. Holding out whole sessions tests a different day; dropping test-session words from training tests new items. Only the second claim is relevant to a signature that must work later.

**Secondary questions** (Holm-corrected as a family of two).

1. **Personal versus pooled (F).** Compare the personal model's held-out AUC with a model trained on the other 19 participants and tested on the same sessions.
2. **Memory strength beyond recall.** Among words not recalled but later tested for recognition, does the combined model's predicted probability (from the held-out fold) predict a strong hit ("old" with confidence 5) versus any other response? (Confidence 4-5 was dropped while writing the code: the pilot participant's recognition was near ceiling, with a mean target confidence of 4.7.) Tested by participant-level logistic regression slopes.

## 11. Detailed analysis pipeline

The pipeline runs in fifteen steps; steps 1-6 never touch recall labels together with EEG, so preprocessing cannot leak outcome information.

1. **Obtain data and check the licence.** Download from the OpenNeuro S3 bucket without an account (`aws s3 cp --no-sign-request` or plain HTTPS). Record the dataset version (2.0.0, DOI 10.18112/openneuro.ds004395.v2.0.0) and the CC0 licence in the project log.
2. **Inspect structure.** List files per participant; read `dataset_description.json`, `participants.tsv`, the per-session `*_events.json` data dictionary, `*_eeg.json` and `*_channels.tsv`. Confirm the system (EGI or BioSemi), sampling rate and reference for each session.
3. **Verify identifiers, timing and labels.** For every session: check that `WORD` events have `trial` 1-16 (or fewer lists in some sessions), 16 words per list, unique `item_num` within the session; check `sample` against `onset` × sampling rate; derive the recall label by matching `REC_WORD` events on `trial` and `item_num`; flag unexpected values (one stray `recog_resp` value on a `WORD` row was found in sub-LTP063 and must be ignored).
4. **Explore behaviour.** Recall rate per session and serial position curve per participant; recall by encoding task; item recallability across participants. These are the inputs to the non-neural model and a sanity check against published PEERS behaviour.
5. **Preprocess EEG (label-blind).** Load the EDF/BDF with MNE-Python; set channel types from `channels.tsv`; notch at the 60 Hz line frequency and harmonics; high-pass at 0.5 Hz; re-reference to the average of good channels; mark bad channels by robust amplitude criteria fixed in advance. Do not use ICA in the first pass (it is a fitted step that complicates leakage control); add it only as a robustness check.
6. **Extract features.** Epoch −1.0 to +2.6 s around each `WORD` onset (the buffer avoids wavelet edge effects); compute Morlet wavelet power at 8 log-spaced frequencies between 3 and 128 Hz; log-transform; average 0.2-1.6 s; z-score each feature within session. Save one feature file per session, then delete the raw EEG file.
7. **Identify confounds.** Compute the non-neural predictors (Section 10) and correlate each with recall and with EEG features. Exposure count and item recallability use only behavioural files.
8. **Baseline models.** (a) Chance (AUC 0.5); (b) serial position only; (c) full non-neural model.
9. **First decoder.** L2 logistic regression on EEG features; then the combined model (non-neural + EEG). Class weights balanced; penalty from an inner leave-one-session-out loop.
10. **Held-out evaluation.** Outer leave-one-session-out; training excludes trials of words that appear in the test session. Collect predicted probabilities for every held-out trial.
11. **Negative controls.** Within-stratum label permutations; cross-participant label scrambling; pre-stimulus-only features reported separately (not as a null, because pre-stimulus states can genuinely predict memory).
12. **Uncertainty.** Hierarchical bootstrap of ΔAUC; per-participant permutation p-values; calibration (Brier score, reliability curve).
13. **Alternative models.** Shrinkage LDA; a small gradient-boosted tree model on the same features; optionally a compact convolutional network on raw epochs as an exploratory comparison only.
14. **Generalisation.** Personal versus pooled models; train on early sessions and test on late sessions to measure drift; ltpFR2 replication using the identical frozen code.
15. **Document and report.** Every run writes a JSON record (code version, parameters, participant list, metrics). Failed approaches are logged in `reports/negative_results.md`. Final report follows Section 12 and the paper outline in Section 22.

**Libraries.** MNE-Python for reading EDF/BDF, filtering and Morlet transforms (Gramfort et al., 2013); MNE-BIDS for BIDS paths; NumPy, SciPy, pandas; scikit-learn for models, grouped cross-validation and metrics; statsmodels for the secondary regressions; matplotlib for figures; pytest for tests. PyTorch only for the optional exploratory network.

## 12. Reproducibility and statistical validation plan

The plan has two layers: a frozen confirmatory analysis that is written, timestamped and tested on pilot data before the confirmatory participants are touched, and an exploratory layer that is clearly labelled as such.

**Pre-registration.** Write the Section 10 table into a pre-registration on OSF or AsPredicted (secondary data analysis template) after the pilot and before the confirmatory run. Record that the analyst has seen the Li et al. (2024) results and the pilot participants' data, but not the confirmatory participants' EEG.

**When to split by what.**

| Split | Tests | Use here |
| --- | --- | --- |
| Random trials | Nothing useful: neighbouring trials share state, words and noise | Never for claims |
| Within session, by list | Generalisation to new lists on the same day | Not used (state leakage) |
| By session | Generalisation to a new day | Primary outer loop |
| By item | Generalisation to new words | Combined with session split |
| By participant | Generalisation to new people | Pooled model (secondary 1) |
| By experiment (ltpFR to ltpFR2) | Generalisation to a new design and cohort | Phase 2 replication |

**Leakage checklist (each is a unit test in Stage 3 code).**

- Train and test sessions never overlap, and no test-session `item_num` appears in training.
- Scalers, penalty selection and any feature selection are fitted inside training folds only.
- Within-session z-scoring uses only that session's own EEG, never labels, so it is allowed on the test session.
- Item recallability for participant *p* is computed from other participants only.
- Exposure count uses only presentations that happened before the trial in time.
- No column of the events file other than the listed predictors enters any model.

**Class imbalance.** Recall rates of about 30-75% per session make accuracy misleading. Use AUC as primary, balanced class weights in training, and report balanced accuracy and Brier score as secondary.

**Multiple comparisons.** One primary test. Two secondary tests, Holm-corrected. Every other analysis is labelled exploratory and reported with effect sizes and intervals only.

**No test-set tuning.** Hyperparameters, frequency bands, time windows, channel exclusions and inclusion criteria are fixed on the 3 pilot participants. If they change after the confirmatory run, the change and both results are reported.

**Correlation is not causation.** Even a clean positive result shows that a neural state predicts memory, not that it causes it. The report must say so in the abstract.

**Reproducibility requirements.** Pinned environment file; a single command reproduces each figure from the downloaded data; random seeds fixed; dataset version recorded; code in a public repository with a licence; derived features (not raw data) shared where the CC0 licence allows; all failed approaches listed.

## 13. Software and computational requirements

An ordinary laptop is enough: 16 GB RAM, 4+ CPU cores, about 20 GB free disk while streaming one session at a time, and a stable connection (each participant is about 10 GB to download). No GPU is needed for the primary analysis.

| Item | Requirement | Note |
| --- | --- | --- |
| Python | 3.11 or 3.12 | Exact package versions are pinned in the Stage 3 code |
| Core packages | mne, mne-bids, numpy, scipy, pandas, scikit-learn, statsmodels, matplotlib, pytest | All installable with pip |
| Download | `aws` CLI with `--no-sign-request`, `openneuro-py`, DataLad, or plain HTTPS from `https://s3.amazonaws.com/openneuro.org/ds004395/...` | Plain HTTPS works without any account (checked on 21 Oct 2026) |
| Memory per session | About 1-2 GB peak while computing wavelets on 129 channels × 256 epochs | Compute in channel chunks if memory is tight |
| Time per session | Minutes on a laptop CPU (to be measured in the pilot) | 20 participants × 20 sessions is an overnight-to-weekend job |
| Storage of results | Feature files about 1 MB per session (256 trials × 129 channels × 8 frequencies, float32) | All features for 20 participants fit in under 1 GB |
| Version control | git + a public repository | Code only; no raw data |

**Not needed:** cloud computing, a GPU, institutional data agreements, or paid software.

## 14. Practical eight-week schedule

Eight weeks is realistic for a confirmatory result on 20 participants if about 10-15 hours a week are available; the internal replication on ltpFR2 adds roughly 3 more weeks.

| Week | Goal | Deliverable | Go / no-go check |
| --- | --- | --- | --- |
| 1 | Read Long et al. (2014) and Li et al. (2024); set up environment; download all ltpFR behavioural event files | Working environment; `inspect_events` report for all 237 participants | Recall labels derive cleanly for > 95% of sessions |
| 2 | Behavioural analysis: serial position curves, item recallability, exposure counts; non-neural model | Non-neural model AUCs per participant | Non-neural AUC clearly above 0.5 (it should be, from serial position alone) |
| 3 | EEG reading and preprocessing on 3 pilot participants; visual checks | Preprocessing report with example raw traces and bad channel counts | Event `sample` matches EEG timing; EGI and BioSemi files both load |
| 4 | Feature extraction and EEG-only decoder on pilot participants | Pilot AUCs; positive controls | EEG-only AUC above 0.5 and serial-position control works; otherwise debug before going on |
| 5 | Freeze the analysis; write and post the pre-registration; select the 20 confirmatory participants by the fixed rule | Pre-registration link; frozen code tag | Nothing in the plan changes after this week |
| 6 | Confirmatory run: features for 20 participants (overnight batches) | Feature files; run logs | All sessions processed or exclusions logged by the pre-set rules |
| 7 | Primary and secondary analyses; permutation tests; robustness models | Results tables and figures | Apply the pre-set success, failure and ambiguity rules exactly |
| 8 | Write the report; publish code; list negative results | Draft report and public repository | A supervisor or peer can reproduce one figure from scratch |

**Expected figures.** (1) Behavioural serial position curves and recall by task. (2) Per-participant AUC for non-neural, EEG-only and combined models. (3) ΔAUC per participant with the group bootstrap interval and the 0.01 line. (4) Personal versus pooled AUC. (5) Feature weights by frequency and scalp location (interpreted with care: weights are not activations; use Haufe et al., 2014 transformation). (6) Calibration curves. (7) Drift: AUC versus distance between training and test sessions.

**The first task for the next working session:** set up the environment from the Stage 3 code and run the event-inspection script on 3 participants. It needs no EEG download and checks every assumption the rest of the project depends on.

## 15. Starter implementation, based on verified dataset structure

The schema below was read from the real files of sub-LTP063 (all 20 sessions) on 21 Oct 2026; the full staged code with tests is delivered in Stage 3 (Follow-up 2) of this thread and lives in the project's shared files.

**Verified paths (BIDS).** `ds004395/sub-<ID>/ses-<N>/eeg/sub-<ID>_ses-<N>_task-ltpFR_eeg.edf` (EGI participants; BioSemi participants use `.bdf`), with `_events.tsv`, `_events.json`, `_channels.tsv`, `_eeg.json` and `_space-CapTrak_electrodes.tsv` alongside, and a behavioural copy at `ses-<N>/beh/sub-<ID>_ses-<N>_task-ltpFR_beh.tsv`. Sessions are numbered from `ses-0`.

**Verified event columns.** `onset, duration, trial_type, sample, stim_file, subject, experiment, session, trial, task, item_name, item_num, recog_resp, recog_conf, resp, color_r, color_g, color_b, case, font`.

**Verified `trial_type` values** (with meanings from `events.json`): `SESS_START`, `WORD`, `REC_START`, `REC_WORD`, `REC_WORD_VV`, `FFR_REC_WORD`, `FFR_REC_WORD_VV`, `RECOG_TARGET`, `RECOG_LURE`, `RECOG_RESP`, `RECOG_RESP_VV`, `RECOG_CONF`, `SLOW_MSG`, `REST_REWET`, `SESS_END`.

**Verified facts for sub-LTP063.** 20 sessions; sessions 0-6 and 14-19 have 16 lists × 16 words with 64 no-task words and 96 each of size and animacy judgements; sessions 7-13 have 12-14 lists with size and animacy only. Session recall rates ranged from 0.33 to 0.74. Final free recall occurred in some sessions only; recognition targets were present in all 20. EEG: EGI HydroCel, 125 EEG + 4 EOG channels, 500 Hz, Cz reference, 60 Hz line frequency. No `recalled` column exists: the label must be derived.

**Not yet verified, checked first in Stage 3:** that `sample` aligns with the EDF sample index; how BioSemi sessions differ; whether every recognition target is a word from the same session; how practice lists (`trial` ≤ 0) appear in other participants.

The first three code stages are: (1) `inspect_events.py` downloads only event files and prints a structured report; (2) `labels.py` derives recall and recognition labels with unit tests built on real rows; (3) `behaviour_model.py` fits the non-neural model. EEG code comes only after these pass.

## 16. Long-term system architectures

Each architecture adds one risky element to the one before; the bottleneck of A is signal quality, of B is proving that neural data adds value over AI alone, and of C is safety plus the lack of any method to write specific content.

| Dimension | A. Non-invasive neural decoding | B. Personalised memory assistance | C. Closed-loop memory prosthesis (future) |
| --- | --- | --- | --- |
| Inputs | EEG (later MEG) during perception, encoding, retrieval; stimulus and behaviour logs | Everything in A (optional), plus calendar, photos, location, conversation notes, caregiver input | Intracranial or future high-resolution recording; personal model; state detector |
| Outputs | Calibrated probabilities: item present, likely remembered, retrieval in progress | Ranked retrieval cues and reminders at the right time | Stimulation (or cue) delivered when the model predicts poor encoding or failed retrieval |
| Hardware | Research EEG (64-128 ch) or validated dry-electrode headset; eye tracker | Phone or tablet; optional wearable EEG | Implanted electrodes and stimulator (clinical device class), or future focused ultrasound |
| Software | Preprocessing, feature extraction, decoder, drift monitor | Personal knowledge graph, cue-ranking model, scheduling (spaced retrieval), user interface | Real-time decoder, safety interlocks, stimulation controller, audit log |
| Signal pipeline | Filtering, artefact handling, spectral and time features, within-session normalisation | Neural pipeline from A when present; text/image embeddings of personal records | Low-latency (tens of ms) spectral or spike features; closed-loop timing |
| Model | Regularised linear decoder with population prior; temporal generalisation | Behavioural memory model (e.g. recall probability from cue strength, spacing and recency) + optional neural term | State-space model of encoding states; policy for when to stimulate |
| Personalisation | Per-person decoder initialised from pooled model; recalibration each session | Personal cue-success history; preferences | Per-person electrode map, thresholds, stimulation parameters |
| Data storage | Encrypted features, not raw EEG, where possible | Highly sensitive personal records; local-first storage | Medical device records under clinical governance |
| Feedback | Researcher-facing only | User sees cues; caregiver dashboard (with consent) | Clinician-controlled; patient informed |
| Evaluation | Held-out-session AUC, calibration, drift | Randomised comparisons of recall and daily function, versus a non-neural version | Sham-controlled, blinded trials; safety endpoints |
| Failure modes | Artefact-driven decoding; drift; low information | Cues that suggest false memories; over-reliance; privacy breach | Seizures, infection, mood effects, false memories, device failure |
| Security | Neural data as GDPR special-category health data | Same, plus third-party data (other people in photos) | Medical device cybersecurity (MDR Annex I requirements) |
| Cost | Low with open data; moderate for new EEG studies | Low to moderate software cost | Very high; clinical programme |
| Readiness | Research-ready now | Non-neural version buildable now; neural version unproven | Not ready; needs scientific breakthroughs |
| Breakthroughs needed | Better non-invasive signal from hippocampus, or proof that cortical signals suffice | Evidence that neural input improves cue choice | Content-specific stimulation; long-term safety; proof of benefit on daily life |

**Components that can be developed independently:** the preprocessing and decoding library (A); the behavioural cue-ranking model and personal knowledge graph (B, no neural data needed); drift-monitoring and calibration tools (A and C); evaluation protocols for false-memory risk (B and C). The non-neural version of B is the right control arm for any later neural version.

&#91;embedded content: three architectures · bottlenecks and shared parts\]

The shared band can be built now with no neural hardware; the neural parts of B and all of C wait on the gates in Section 20.

## 17. Alzheimer's-related application and clinical limitations

The realistic first clinical use case is a non-neural, personalised cueing and reminder system for people with mild cognitive impairment or mild Alzheimer's disease and their care partners, tested against usual care in a randomised trial on everyday goals; neural measurement should be added only if it later proves to add value. This project is not, and should never be described as, a cure for Alzheimer's disease.

### What kind of memory problem is it?

| Problem | Typical stage | What might help | Role for neural decoding |
| --- | --- | --- | --- |
| Impaired formation of new memories | Early, prominent in amnestic MCI and AD | External records, errorless learning, spaced retrieval | Possibly detect poor encoding moments (research) |
| Impaired retrieval of information still stored | Early to moderate; varies | Personalised cues, associative prompts | Possibly predict which cue works (unproven) |
| Impaired recognition | Later | Simplified environments, familiar cues | Limited |
| Impaired contextual recollection (when, where) | Early | Time-stamped records, photo diaries | Limited |
| Changed memory networks (hyperactivity, disconnection) | Throughout | Drugs and stimulation under research | Biomarker research |
| Loss of the biological structures holding a memory | Advanced | Only external records; nothing can "restore" the memory | None |

The distinction matters: **improving memory performance** (more items recalled on average) is achievable with existing tools; **restoring a particular past memory** is possible only when the trace still exists and a cue can reach it. Rodent engram studies (Roy et al., 2016) suggest some early-stage "forgetting" may be retrieval failure, but this has not been shown in humans.

### Existing clinical evidence

- **Memory-network stimulation:** fornix DBS did not meet its primary endpoint in phase II (Lozano et al., 2016); the larger ADvance II trial lists completion on 19 Feb 2024 with [no results reported](https://fdaaa.trialstracker.net/trial/NCT03622905). Non-invasive stimulation trials in MCI and AD show mixed, mostly small effects. Focused ultrasound is at safety-study stage.
- **Drugs:** anti-amyloid antibodies slow decline modestly; lecanemab is [authorised in the EU since April 2025](https://nordiclifescience.org/eu-approves-leqembi-for-treatment-of-early-alzheimers-disease/) for early AD in ApoE ε4 non-carriers or heterozygotes.
- **Rehabilitation and aids:** goal-oriented cognitive rehabilitation improved attainment of personally chosen goals in early dementia (GREAT trial; Clare et al., 2019, *Health Technology Assessment* 23(10)); wearable-camera photo review helped autobiographical recall in case studies (Berry et al., 2007, *Neuropsychological Rehabilitation*).

### First clinical use case and outcomes

**Population:** amnestic MCI or mild AD with a care partner. **Intervention:** personal record capture plus model-chosen retrieval cues and spaced-retrieval practice for a small set of personally important items (names, routines, recent events). **Comparator:** the same app with fixed, non-personalised reminders. **Primary outcome:** Goal Attainment Scaling on personally chosen memory goals. **Secondary outcomes:** recall accuracy for trained items scored against records (with false-recall rate), a standardised everyday memory test, activities of daily living, quality of life (for example QoL-AD), care-partner burden, adverse events including distress and false memories.

### What must be shown before any therapeutic claim

1. **Computational:** neural features predict memory beyond behaviour in open data (this project), and the effect replicates in an independent dataset.
2. **Prospective non-invasive, healthy adults:** pre-registered study showing that neural-informed cue selection beats behavioural cue selection on verified recall, without raising false recall.
3. **Prospective, older adults and MCI:** the same effect holds with ageing-related signal changes; usability and acceptability.
4. **Approved clinical research:** randomised, blinded trial with clinically meaningful outcomes, safety monitoring, and a pre-specified analysis.

### Sweden and EU requirements

| Area | Requirement | When it applies |
| --- | --- | --- |
| Research ethics | Ethical review under the Swedish Ethical Review Act (2003:460), applications to the Swedish Ethical Review Authority (Etikprövningsmyndigheten) | Any new data collection with people, and research on sensitive personal data. Analysing anonymised open data usually falls outside, but confirm with your university before publishing |
| Data protection | GDPR (EU 2016/679), Article 9 special-category data (health, and neural data used to infer health); Swedish Data Protection Act (2018:218); supervisory authority IMY | Any identifiable neural or health data; data protection impact assessment for new studies |
| Medical devices | EU Medical Device Regulation 2017/745; software for diagnosis or therapy is usually class IIa or higher (Rule 11); Annex XVI covers non-medical brain-stimulation equipment | Any system with a medical purpose, and any brain-stimulation product |
| Clinical investigations | MDR Articles 62-82; in Sweden, application to the Swedish Medical Products Agency (Läkemedelsverket) plus ethics approval | Testing a device on patients |
| Artificial intelligence | EU AI Act (Regulation 2024/1689): AI that is, or is a safety component of, a medical device needing third-party conformity assessment is high-risk | Architecture B with medical claims; Architecture C |
| Medicines | EU Clinical Trials Regulation 536/2014 | Any pharmacological arm |

**Ethical issues specific to this project:** mental privacy (neural data can reveal more than intended); consent capacity in dementia (supported decision-making, care-partner involvement, ongoing consent); risk of implanting false memories through cues; over-reliance and loss of autonomy; equitable access; and honest communication about what the system cannot do.

## 18. Novelty and competitive landscape

The overall idea is mainly a new framing of existing research; the combination of a person-specific neural model with model-chosen natural retrieval cues, evaluated against a non-neural AI assistant, is partly novel and underexplored. Combining technologies does not by itself make the idea original.

| Component | Who already works on it (examples) | Status | Novelty left for this project |
| --- | --- | --- | --- |
| Decoding later memory from EEG/iEEG | Kahana lab, University of Pennsylvania (PEERS, RAM; Li et al., 2024); many subsequent-memory labs | Established | Rigorous added-value test against a non-neural model; held-out items; personal vs pooled |
| Reinstatement during retrieval | Many fMRI/MEG/EEG labs (e.g. Polyn, Norman, Staresina, Wimber, Hanslmayr groups) | Established for categories | Item-level, cross-session tests on open EEG |
| Memory engrams | Tonegawa, Josselyn and Frankland, Ramirez labs (rodents) | Established in rodents | None for a computational project |
| Closed-loop memory stimulation | DARPA Restoring Active Memory programme teams; Ezzyat, Kahana and colleagues; Nia Therapeutics (company founded from that work) | Early clinical research | None without clinical partners |
| Model-derived hippocampal prosthesis | Berger (USC), Hampson and Deadwyler (Wake Forest) | Early clinical research | None without clinical partners |
| Memory network DBS for AD | Functional Neuromodulation Ltd (ADvance trials), Lozano group | Phase II negative; phase III unreported | None |
| Sleep-based targeted memory reactivation | Paller, Rasch, and others | Established effect, modest size | Personalised cue choice for sleep cueing (later) |
| AI external memory and lifelogging | Academic lifelogging research (SenseCam lineage); consumer "memory" features in photo and note apps; AI assistants | Fast-moving commercial area | Evaluation for people with MCI, with false-memory safeguards |
| Neurotechnology for cognition, non-invasive | fNIRS and EEG headset companies; academic tACS groups | Mixed evidence | Little for this project |

**Possible academic contributions from the first project.**

1. A quantified estimate of how much person-specific EEG information about later recall remains after strict control of item, position, task and exposure, with an equivalence test if it is negligible.
2. A direct comparison of personal versus pooled encoding decoders on the same held-out sessions.
3. Evidence on whether encoding signals track memory strength beyond recall (recognition confidence for unrecalled words).
4. An open, tested, reusable pipeline for PEERS ltpFR.

**What needs professional IP assessment.** Any claim to a method that selects retrieval cues using neural predictions, or that times cue delivery to decoded brain states, could overlap with existing patents in closed-loop neuromodulation and brain-state classification. A patent attorney should run a freedom-to-operate and novelty search (for example in Espacenet and the USPTO databases) before any commercial step. Publishing first creates prior art that blocks others but also your own later patent, so decide on IP strategy before public disclosure if commercialisation is a goal. University IP rules (in Sweden, the "teacher's exemption" generally leaves ownership of research results with the researcher; check your institution's policy) also matter.

**Direct prosthesis versus narrower alternatives.** A direct memory prosthesis is at least a decade and a clinical programme away, with uncertain feasibility. Narrower outcomes that could help people sooner: a validated cue-ranking assistant for MCI (non-neural first), better sleep-cueing protocols, and open tools that tell researchers how much their memory decoders really know.

## 19. Red-team objections

The strongest objection is not that decoding fails but that it succeeds for the wrong reason: a memory decoder on scalp EEG may mostly read attention, fatigue or eye movements, which predict memory without containing it. Each objection below has a test; failure of a technology (scalp EEG) must not be confused with failure of the scientific idea (memory traces are partly readable).

| Objection | Test that could resolve it | Continue if | Change direction if | Abandon this pathway if |
| --- | --- | --- | --- | --- |
| Signatures are not stable | Train on early sessions, test on late; measure AUC versus session distance | AUC stays above the 0.01 margin across weeks | Strong decay: use frequent recalibration | No transfer even to the next session |
| Signals contain too little information | Primary ΔAUC test | ΔAUC ≥ 0.01, CI excludes 0 | Small but real: move to iEEG/MEG data | Equivalence test shows ΔAUC < 0.01 on scalp and on iEEG |
| Representation too distributed for the sensor | Compare scalp EEG (PEERS) with iEEG (RAM) on the same task | iEEG gains are large | Use scalp only for state, not content | Even iEEG adds nothing beyond behaviour |
| Similar experiences overlap | Item-level RSA: are same-word pairs more similar than different-word pairs across sessions? | Same-item similarity above matched controls | Work at category or state level | No item information anywhere |
| Different patterns support the same memory | Cross-session decoding of the same item | Some above-chance transfer | Model a distribution, not a pattern | — (expected to some degree) |
| Signature changes with consolidation and retrieval | Compare encoding and repeated-exposure patterns | Partial stability | Model drift explicitly | — |
| Decoded pattern is only a correlate | Requires intervention (not possible with open data) | — | State this limit in all claims | — |
| Stimulation cannot pick a specific memory | Item-level outcomes in published stimulation trials | Item-specific effects reported | Focus on cue-based methods | Consistently general effects only (current state) |
| The biological trace is lost | Not testable here | — | Use external records in AD use case | — |
| External aids do as well, more cheaply | Prospective comparison of B with and without neural input | Neural version clearly better | Drop neural input from B | Neural adds nothing in two adequately powered studies |
| Improvement comes from expectation, familiarity or strategy | Sham control, blinded cues, lures, remember/know | Effect survives all controls | Redesign controls | Effect disappears under blinding |
| Intervention creates false confidence or false memories | Measure false recall and confidence-accuracy calibration | No rise in false recall | Add safeguards | False recall rises reliably |
| Lab success, no clinical benefit | Real-life outcomes (goal attainment, daily function) | Meaningful change on these | Narrow to specific tasks | No real-life change despite lab gains |
| Decoder uses artefacts | Low-frequency-only model; face/neck channels removed; EOG regression | Effect survives | Report as state signal with caveats | Effect only in high frequencies at peripheral channels |

## 20. Five-year milestone roadmap

Phases 0-2 can be done alone with a computer in about the first year; everything after that depends on results, collaborators and funding, and no phase guarantees a working memory prosthesis. Timings are conditional estimates from today (October 2026).

&#91;embedded content: research roadmap · 7 phases, 5 gates\]

A failed gate stops that pathway, not the programme: a Gate 1 failure moves the neural question to intracranial data, and Architecture B continues without neural input.

| Phase | Objective and question | Methods and resources | Timeline | Deliverable | Main risks | Success criterion | Failure criterion | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0. Literature and hypothesis | Define terms; choose the question | This report; reading; supervisor feedback | Month 0-1 | Pre-registration draft | Scope creep | Question fixed and falsifiable | — | Proceed |
| 1. Computational feasibility | Does EEG add to a non-neural memory model? | PEERS ltpFR, laptop, open-source Python | Months 1-3 | Report, code, pre-registration | Artefact-driven effects; download time | Section 10 success rule | Section 10 failure rule | Success: Phase 2. Failure: test on iEEG (Phase 2) before dropping scalp EEG |
| 2. Independent validation | Does it replicate in ltpFR2 and in iEEG (RAM FR1)? Extend to reinstatement during recall | Same code, frozen; more compute time | Months 3-9 | Replication paper or preprint | Different designs complicate comparison | Same direction and CI excludes 0 in both | No replication | Replicated: seek a lab partner. Not: publish the negative result and refocus on B without neural input |
| 3. Prospective non-invasive study | Do model-chosen cues beat behavioural cues on verified recall? | University EEG lab, ethics approval (Etikprövningsmyndigheten), pre-registration, about 30-40 healthy adults (power analysis from Phase 1-2 effects) | Year 1.5-3 | Pre-registered study | Small effects; recruitment | Neural-informed cues improve recall, no rise in false recall | No benefit over behavioural cues | Benefit: Phase 4. None: stop neural cue selection |
| 4. Laboratory collaboration | Better signals (MEG, high-density EEG with eye tracking, iEEG partners) | Collaboration agreements; shared protocols | Year 2-4 | Joint studies | Dependence on partners | Larger, item-specific effects | No gain from better sensors | Continue only with clear gains |
| 5. Mechanistic research | Causal role of identified states (TMS, sleep cueing, iEEG stimulation by qualified teams) | Clinical or animal collaborators | Year 3-5+ | Causal evidence | Safety; ethics; small samples | Replicated causal effects | Null or harmful effects | Narrow or stop the intervention pathway |
| 6. Translational development | First clinical use case (Section 17) | Clinical partner, MDR pathway, Swedish Medical Products Agency | Year 4-5+ | Clinical investigation plan | Regulatory cost; uncertain benefit | Meaningful daily-life benefit with acceptable safety | No benefit over usual care | Only proceed on benefit and safety |

**Five-year vision, conditional on results:** a published, replicated estimate of what non-invasive and intracranial signals reveal about future memory; an open software toolkit; one pre-registered prospective study of cue selection; and, if justified, a clinical partnership testing a personalised memory assistant for MCI. A neural memory prosthesis is outside this five-year horizon.

## 21. The next five concrete actions

- [ ] **1. Set up the environment and inspect events for 3 participants** (one working session). Use the Stage 3 code; no EEG download needed.
- [ ] **2. Download all ltpFR behavioural event files** (about 550 MB, under an hour) and run the behavioural analysis: recall rates, serial position curves, item recallability.
- [ ] **3. Process one full EEG session end to end** for a pilot participant, confirming that event `sample` values line up with the EEG and that features look sensible.
- [ ] **4. Write the pre-registration** from Section 10, show it to a potential supervisor, and post it before touching confirmatory participants.
- [ ] **5. Contact a supervisor** (cognitive neuroscience or computational memory group at a Swedish university, e.g. through a master's thesis or research assistant route) with the Section 22 proposal and the pilot figures.

## 22. Project proposal for a university research supervisor

**Title.** How much of a remembered word is in a person's EEG? Person-specific encoding decoders tested against a non-neural memory model across sessions.

**Abstract.** Activity recorded while an item is studied predicts whether it will later be remembered, and person-specific EEG classifiers reach held-out-session AUCs of about 0.60 for free recall (Li, Pazdera & Kahana, 2024). It is unclear how much of this reflects information that a model of the word, its list position, the encoding task and prior exposure would already provide. Using the open PEERS ltpFR scalp-EEG dataset (OpenNeuro ds004395, CC0; 237 participants with a median of 20 sessions), I will test, in 20 pre-selected participants, whether adding spectral EEG features to a non-neural model improves held-out prediction of later recall, with whole sessions and test-session words excluded from training. The primary outcome is the per-participant change in AUC, with a pre-registered smallest effect of interest of 0.01 and an equivalence test for a negative result. Secondary analyses compare personal and pooled models and test whether encoding signals predict recognition confidence for unrecalled words. The study clarifies whether scalp EEG can support personalised memory-assistance systems, or whether such systems should rely on behavioural models.

**Background.** Subsequent-memory effects (Paller & Wagner, 2002), spectral EEG correlates of encoding (Long, Burke & Kahana, 2014), and closed-loop applications of memory decoders (Ezzyat et al., 2018) motivate person-specific memory models. Their practical value depends on information beyond what simpler predictors provide.

**Data and methods.** Secondary analysis of anonymised open data; no new participants. Preprocessing in MNE-Python; Morlet power at 8 frequencies (3-128 Hz) over 0.2-1.6 s after word onset; L2 logistic regression; nested leave-one-session-out cross-validation with item hold-out; hierarchical bootstrap and within-stratum permutation tests; robustness models excluding high frequencies and peripheral channels.

**Hypothesis and decision rules.** As in Section 10, fixed in a pre-registration before analysis of confirmatory participants.

**Expected outputs.** A preprint and conference abstract; open, tested code; a replication plan for PEERS ltpFR2 and the RAM intracranial dataset.

**Timeline.** Eight weeks for the primary study (Section 14), three further weeks for internal replication.

**Resources.** A laptop, open-source software, and supervision. No ethics application is expected for anonymised CC0 data, subject to the department's confirmation.

**What I need from a supervisor.** Feedback on the pre-registration, advice on the confound model, and a route to a later prospective EEG study if results justify it.

## References

Items marked ✓ were opened or checked against official storage during this review (21 Oct 2026). Other items are well-known published works cited from the scientific record; their details (especially DOIs) should be checked before they go into a paper. Several databases (PubMed, Crossref) blocked automated access during this review.

### Datasets

- ✓ Kahana MJ, Rudoler JH, Lohnas LJ, et al. Penn Electrophysiology of Encoding and Retrieval Study (PEERS). OpenNeuro ds004395 v2.0.0, CC0. [doi:10.18112/openneuro.ds004395.v2.0.0](https://doi.org/10.18112/openneuro.ds004395.v2.0.0)
- ✓ Delayed Free Recall of Word Lists (RAM FR1). OpenNeuro ds004789, CC0. [doi:10.18112/openneuro.ds004789.v3.1.0](https://doi.org/10.18112/openneuro.ds004789.v3.1.0)
- ✓ Categorized Free Recall (RAM catFR1). OpenNeuro ds004809, CC0. [doi:10.18112/openneuro.ds004809.v2.2.0](https://doi.org/10.18112/openneuro.ds004809.v2.2.0)
- ✓ Chandravadia N, Liang D, Schjetnan AGP, et al. (2020). A NWB-based dataset and processing pipeline of human single-neuron activity during a declarative memory task. *Sci Data* 7. [doi:10.1038/s41597-020-0415-9](https://doi.org/10.1038/s41597-020-0415-9); DANDI:000004 [doi:10.48324/dandi.000004/0.220126.1852](https://doi.org/10.48324/dandi.000004/0.220126.1852)
- Faraut MCM, Carlson AA, Sullivan S, et al. (2018). Dataset of human medial temporal lobe single neuron activity during declarative memory encoding and recognition. *Sci Data* 5:180010. [doi:10.1038/sdata.2018.10](https://doi.org/10.1038/sdata.2018.10)
- ✓ Allen EJ, St-Yves G, Wu Y, et al. (2022). A massive 7T fMRI dataset to bridge cognitive neuroscience and artificial intelligence. *Nat Neurosci* 25:116-126. [doi:10.1038/s41593-021-00962-x](https://doi.org/10.1038/s41593-021-00962-x); [AWS registry entry](https://registry.opendata.aws/nsd)
- ✓ Grootswagers T, Zhou I, Robinson AK, Hebart MN, Carlson TA (2022). Human EEG recordings for 1,854 concepts presented in rapid serial visual presentation streams. *Sci Data* 9:3. [doi:10.1038/s41597-021-01102-7](https://doi.org/10.1038/s41597-021-01102-7)
- ✓ Wakeman DG, Henson RN (2015). A multi-subject, multi-modal human neuroimaging dataset. *Sci Data* 2:150001. OpenNeuro ds000117.
- ✓ Lee H, Chen J, Hasson U (2022). A functional neuroimaging dataset acquired during naturalistic movie watching and narrated recall of a series of short cinematic films. *Data in Brief* 46:108788. [doi:10.1016/j.dib.2022.108788](https://doi.org/10.1016/j.dib.2022.108788)
- ✓ Matran-Fernandez A, Halder S (2025). An EEG dataset to study neural correlates of audiovisual long-term memory retrieval. *Sci Data* 12:1933. [doi:10.1038/s41597-025-06203-1](https://doi.org/10.1038/s41597-025-06203-1)

### Memory decoding and EEG

- ✓ Li Y, Pazdera JK, Kahana MJ (2024). EEG decoders track memory dynamics. *Nat Commun* 15:2981. [doi:10.1038/s41467-024-46926-0](https://doi.org/10.1038/s41467-024-46926-0)
- ✓ Long NM, Burke JF, Kahana MJ (2014). Subsequent memory effect in intracranial and scalp EEG. *NeuroImage* 84. [doi:10.1016/j.neuroimage.2013.08.052](https://doi.org/10.1016/j.neuroimage.2013.08.052)
- ✓ Aka A, et al. (2024). The Penn Electrophysiology of Encoding and Retrieval Study. *J Exp Psychol Learn Mem Cogn* (full author list and DOI to be checked).
- Paller KA, Wagner AD (2002). Observing the transformation of experience into memory. *Trends Cogn Sci* 6:93-102.
- Brewer JB, et al. (1998); Wagner AD, et al. (1998). *Science* 281:1185-1187 and 1188-1191.
- Arora A, et al. (2018). Comparison of logistic regression, support vector machines, and deep learning classifiers for predicting memory encoding success using human intracranial EEG recordings. *J Neural Eng* 15.
- Yuval-Greenberg S, et al. (2008). Transient induced gamma-band response in EEG as a manifestation of miniature saccades. *Neuron* 58:429-441.
- Whitham EM, et al. (2007). Scalp electrical recording during paralysis: quantitative evidence that EEG frequencies above 20 Hz are contaminated by EMG. *Clin Neurophysiol* 118:1877-1888.

### Representations and reinstatement

- Haxby JV, et al. (2001). *Science* 293:2425-2430. Kriegeskorte N, et al. (2008). *Neuron* 60:1126-1141. Kriegeskorte N, Mur M, Bandettini P (2008). Representational similarity analysis. *Front Syst Neurosci* 2:4.
- Cichy RM, Pantazis D, Oliva A (2014). *Nat Neurosci* 17:455-462. King JR, Dehaene S (2014). Characterizing the dynamics of mental representations: the temporal generalization method. *Trends Cogn Sci* 18:203-210.
- Takagi Y, Nishimoto S (2023). High-resolution image reconstruction with latent diffusion models from human brain activity. CVPR 2023.
- Quiroga RQ, et al. (2005). *Nature* 435:1102-1107. Gelbard-Sagiv H, et al. (2008). *Science* 322:96-101. Rutishauser U, et al. (2015). *Nat Neurosci* 18:1041-1050.
- Polyn SM, Natu VS, Cohen JD, Norman KA (2005). *Science* 310:1963-1966. Danker JF, Anderson JR (2010). *Psychol Bull* 136:87-102. Staresina BP, et al. (2012). *J Neurosci* 32:18150-18156. Ritchey M, et al. (2013). *Cereb Cortex* 23:2818-2828. Linde-Domingo J, et al. (2019). *Nat Commun* 10:179. Xue G, et al. (2010). *Science* 330:97-101.
- Finn ES, et al. (2015). Functional connectome fingerprinting. *Nat Neurosci* 18:1664-1671.

### Memory mechanisms

- Liu X, et al. (2012). *Nature* 484:381-385. Ramirez S, et al. (2013). *Science* 341:387-391. Ryan TJ, et al. (2015). *Science* 348:1007-1013. Roy DS, et al. (2016). *Nature* 531:508-512. Josselyn SA, Tonegawa S (2020). *Science* 367:eaaw4325.
- Nader K, Schafe GE, LeDoux JE (2000). *Nature* 406:722-726. Yassa MA, Stark CEL (2011). *Trends Neurosci* 34:515-525. Roediger HL, McDermott KB (1995). *J Exp Psychol Learn Mem Cogn* 21:803-814.
- Ziv Y, et al. (2013). *Nat Neurosci* 16:264-266. Rule ME, O'Leary T, Harvey CD (2019). Causes and consequences of representational drift. *Curr Opin Neurobiol* 58:141-147.

### Stimulation and intervention

- Suthana N, et al. (2012). *NEJM* 366:502-510. Jacobs J, et al. (2016). *Neuron* 92:983-990. Ezzyat Y, et al. (2017). *Curr Biol* 27:1251-1258. ✓ Ezzyat Y, et al. (2018). *Nat Commun* 9. [doi:10.1038/s41467-017-02753-0](https://doi.org/10.1038/s41467-017-02753-0)
- Hampson RE, et al. (2018). Developing a hippocampal neural prosthetic to facilitate human memory encoding and recall. *J Neural Eng* 15:036014. Titiz AS, et al. (2017). *eLife* 6:e29515.
- Wang JX, et al. (2014). *Science* 345:1054-1057. Reinhart RMG, Nguyen JA (2019). *Nat Neurosci* 22:820-827. Grover S, et al. (2022). *Nat Neurosci* 25:1237-1246.
- Rasch B, et al. (2007). *Science* 315:1426-1429. Hu X, Cheng LY, Chiu MH, Paller KA (2020). *Psychol Bull* 146:218-244.
- Lozano AM, et al. (2016). *J Alzheimers Dis* 54:777-787. ✓ ADvance II, [NCT03622905](https://clinicaltrials.gov/study/NCT03622905); [results status](https://fdaaa.trialstracker.net/trial/NCT03622905). Rezai AR, et al. (2020). *PNAS* 117:9180-9182. deBettencourt MT, et al. (2015). *Nat Neurosci* 18:470-475. Bakker A, et al. (2012). *Neuron* 74:467-474.

### Clinical

- van Dyck CH, et al. (2023). Lecanemab in early Alzheimer's disease. *NEJM* 388:9-21. ✓ [EU approval of Leqembi, April 2025](https://nordiclifescience.org/eu-approves-leqembi-for-treatment-of-early-alzheimers-disease/).
- Clare L, et al. (2019). Goal-oriented cognitive rehabilitation for early-stage Alzheimer's and related dementias: the GREAT RCT. *Health Technol Assess* 23(10). Berry E, et al. (2007). *Neuropsychol Rehabil* 17:582-601.

### Methods

- Kriegeskorte N, et al. (2009). Circular analysis in systems neuroscience. *Nat Neurosci* 12:535-540. Varoquaux G (2018). Cross-validation failure: small sample sizes lead to large error bars. *NeuroImage* 180:68-77. Haufe S, et al. (2014). On the interpretation of weight vectors of linear models in multivariate neuroimaging. *NeuroImage* 87:96-110. Gramfort A, et al. (2013). MEG and EEG data analysis with MNE-Python. *Front Neurosci* 7:267.
