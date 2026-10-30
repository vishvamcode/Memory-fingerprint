# Memory Fingerprint: The Plain-Language Guide

Oct 22, 2026 · @Vishvam

## The short version

You had an idea: every memory might leave a personal "fingerprint" in brain activity, and one day we might use it to help people remember. We have not tested that big idea yet. We picked one small first question that can actually be checked with a computer and free public data: **can brain signals recorded while someone learns a word tell us whether they will remember that word later?**

We found a good free dataset, wrote and tested the analysis code, and tried it on 3 people. Those 3 people were only a practice run, to make sure the code works. The real test on 20 new people starts once you publish your plan online (a "pre-registration"), so nobody can say we changed the rules after seeing the answer.

This guide explains all of that from zero. No brain science knowledge needed. Technical words are explained in the word list at the end.

## Your idea, and the first question we are testing

**Your big idea.** When you experience something, your brain produces a pattern of activity. Maybe that pattern is personal, like a fingerprint. If we could read it, we might one day tell when a memory is being stored or recalled, and help people whose memory is failing, for example people with early Alzheimer's disease. You called this a Personalized Neural Memory Signature.

**Why we did not test the big idea directly.** It is really several claims stacked on top of each other:

1. Brain activity while learning says something about whether you will remember.
2. That activity is specific to *the thing* you are learning, not just to your mood or alertness.
3. The same pattern comes back when you remember it later.
4. It is personal: your pattern differs from other people's.
5. We could use it to help memory.

Each claim only makes sense if the ones before it are true. So we start with claim 1, the foundation. If claim 1 fails with the tools we have, there is no point building the others on top of it.

**The first question, exactly.** We show a person a word. While they look at it, we record their brain signals. Later, we check whether they remembered the word. *Do the brain signals help predict remembering, better than a smart guess made without any brain signals?*

The "smart guess without brain signals" part matters a lot. Some words are just easier to remember, and the first and last words of a list are remembered more often. A computer can predict memory quite well from those facts alone. Brain signals only count as useful if they add something on top.

## The basics you need

**Brain signals.** Your brain has billions of nerve cells that talk using tiny electrical pulses. When many of them fire together, the electricity is strong enough to measure through the skull, on the skin of your head.

**EEG (electroencephalography).** A cap with many small sensors ("electrodes") sits on the head and records that electricity. Our data use caps with 129 sensors. EEG is cheap, safe and non-invasive (no surgery). Its weakness: the skull blurs the signal, so it is like listening to a stadium from outside. You hear the crowd's roar, not single conversations.

**Brain waves (frequencies).** EEG signals go up and down in rhythms. Slow rhythms (a few per second) and fast ones (dozens per second) tend to reflect different things, such as attention, relaxation or effort. We measure how strong each rhythm is at each sensor. That gives 8 rhythms × 129 sensors, about 1,000 numbers per word.

**Memory.** Scientists split memory into stages: storing something (encoding), keeping it, and getting it back (retrieval). Our question is about encoding: does the brain's activity while storing a word predict whether it can be retrieved later? Researchers have studied this for decades and call it the *subsequent memory effect*. On average across many people, it exists. What is less clear is whether it is strong and reliable enough inside one single person to be useful.

**Why this is hard.** EEG also picks up things that are not brain activity:

- **Eyes.** Blinks and eye movements make big electrical signals, much bigger than the brain's.
- **Muscles.** Clenching the jaw or tensing the forehead shows up as fast "noise".
- **Movement.** Pressing a button creates its own signal.

All of these can be linked to memory by accident. For example, if you blink while a word is on screen, you might miss it and forget it. Then a computer could "predict memory from EEG" when it is really just detecting blinks. A big part of our work is catching tricks like this.

## The data, and why we did not need a lab

You have a computer but no lab, scanner or volunteers. So we used data that other scientists recorded and shared freely.

**The dataset: PEERS** (Penn Electrophysiology of Encoding and Retrieval Study), from the University of Pennsylvania. It is stored on a free public website called OpenNeuro and is free for anyone to use for anything (licence "CC0"). It is huge: 9.6 terabytes in total. We only download one recording at a time and delete it after use.

**What happened in the study.** Volunteers came back to the lab many times (usually about 20 visits, called *sessions*). In each session:

1. They saw 16 lists of 16 words, one word at a time, while wearing the EEG cap.
2. For some lists they had to judge each word ("is it big?" or "is it alive?") by pressing a key. For others they just read.
3. After each list they said out loud every word they could remember. This is called **free recall**.
4. At the end, they did a recognition test: "did you see this word today?" with a confidence rating from 1 to 5.

So for every word we have the brain signals while it was shown, and whether it was later remembered. That is exactly what our question needs.

**Why this dataset and not others.** We compared about eight public datasets. Most had no memory test at all, or too few people, or brain recordings from surgery patients (not useful for an everyday, non-invasive tool). PEERS has many visits per person, which matters because your idea is about *personal* signatures. We later want to double-check results on two other datasets from the same family, one of them recorded inside the brain during epilepsy surgery.

**Who we analyse.** We set a fair rule in advance: at least 12 visits, the standard EEG cap, and memory that is neither almost perfect nor almost zero. 149 people pass. The first 3 are our practice ("pilot") group; the next 20 are the real test group.

## How the experiment works, step by step

We do the same thing for each person separately, because your idea is about *personal* signatures.

&#91;embedded content: the experiment for one person · 6 steps\]

**Steps 1 to 3: turn recordings into numbers.** For each visit we download the recording, clean it (remove the 60 Hz hum from the American power grid, slow drifts, and sensors that were broken that day), and then, for every word, measure how strong each brain rhythm was at each sensor while the word was on screen. Each word becomes a list of about 1,000 numbers.

**Step 4: hide one visit.** This is the most important rule. To test a prediction honestly, the computer must predict things it has never seen, like a student taking an exam with new questions. So we hide one visit completely. Words repeat across visits for the same person, so we also remove every other appearance of the hidden visit's words from training. Otherwise the computer could memorise "this person always forgets the word OBOE" instead of reading the brain.

**Step 5: two competing models.** A *model* here is a formula the computer learns from examples. The **without-brain model** only knows facts about the word: its position in the list, how long it is, how easy it is for *other* people, whether the person judged it, how many times they had seen it before. The **with-brain model** knows the same facts plus the brain numbers.

**Step 6: score both, then repeat.** Both models guess how likely each hidden word is to be remembered, and we check against what really happened. We repeat for every visit, so every word is guessed exactly once by models that never saw it.

**The score: AUC.** Think of it as: "if I pick one remembered word and one forgotten word at random, how often does the model rank the remembered one higher?" 0.5 is a coin flip; 1.0 is perfect. The without-brain model already reaches about 0.64 to 0.69. Our key number is the **gain**: with-brain score minus without-brain score. We decided in advance that a gain smaller than 0.01 is too small to matter.

**From 20 people to one answer.** We compute the gain for each of the 20 test people, then ask: is it reliably above zero across people, and is the average at least 0.01? Statistics tell us how sure we can be, given that 20 people is not many.

## How we stop ourselves from fooling ourselves

In this kind of research, the easiest mistake is a result that looks exciting but comes from a flaw. So most of the work is building checks. Here are the main ones, in plain words.

| Trap | What it means | Our protection |
| --- | --- | --- |
| **Peeking at the answers** ("data leakage") | The computer sees, during training, something it is later tested on | Hide a whole visit, and remove its words from training too. Automatic tests prove this holds |
| **A weak opponent** | Beating a lazy guess proves little | The without-brain model is strong: list position, word difficulty, task, past exposure, fatigue across the session |
| **Eye blinks and eye movements** | The "brain" signal is really the eyes | A separate model uses only the 4 eye sensors. If the eyes alone do as well, we don't call it brain activity |
| **Muscles** | Fast signals from jaw and forehead | A "robust" version drops fast rhythms and the sensors near the edge of the cap. The result must survive there too |
| **Button presses** | Pressing a key while the word is shown | Repeat the analysis using only lists where nobody pressed anything |
| **General mood instead of the word** | Being alert helps all words, not this word | Compare the word's own brain signals with those of the *previous* word, 4 seconds earlier. Mood barely changes in 4 seconds; word processing does |
| **Moving the goalposts** | Changing the rules after seeing results | Write the rules down and publish them first (pre-registration). Freeze the code with digital fingerprints (checksums) |
| **Lucky practice** | Tuning things on the same people you test | 3 practice people for tuning; 20 different people for the real test |

**What "pre-registration" means.** You publish a dated, public description of exactly what you will do and what result counts as success or failure, before doing it. Afterwards, anyone can check that you followed it. It is the strongest way to show you did not adjust the analysis until you got the answer you wanted.

**Our success and failure rules, written in advance.**

- **Success:** across the 20 people, the gain is clearly above zero, averages at least 0.01, and stays above zero in the muscle-proof version.
- **Failure:** we can be confident the true average gain is below 0.01. Then brain signals add less than anything useful.
- **Ambiguous:** anything in between. We would say so honestly.

## Problems we hit, and how we fixed them

None of these are failures. Finding them before the real test is exactly what the practice run is for.

| Problem | In plain words | Fix |
| --- | --- | --- |
| No "remembered" column in the data | The files list the words shown and the words said aloud, but nothing marks which were remembered | We match each shown word to the words spoken after its list. Tested against a real recording |
| Some websites blocked from our computer | The main OpenNeuro website and some article databases refused the connection | We found the same files on OpenNeuro's public storage. For articles, we only cite ones we could check, and say which |
| A broken reference sensor | One sensor (the reference point on top of the head) is always flat, which caused a maths error | Mark it as broken every time; its numbers are set to zero |
| A sorting bug | When some sensors were broken, the computer quietly dropped them and the remaining numbers shifted places | Keep every sensor in place and zero out the broken ones. Added a test |
| Brain numbers drowned the word facts | With 1,000 brain numbers and 39 word facts in one formula, the formula got worse than the word facts alone | Two-step ("stacked") model: first turn the brain numbers into one score, then combine that score with the word facts |
| A subtle peek during tuning | While choosing settings, the computer could see the same word in its practice and check sets | Remove shared words in every inner step too |
| Fatigue mistaken for brain signal | People remember less as a session goes on, and EEG slowly drifts as the gel dries. The two could be confused | The without-brain model now knows exactly which list each word was in |
| The memory-strength test was rigged in our favour | It used a score that already contained word facts, so it could "work" without any brain signal | It now uses only the brain score, after allowing for the word facts |
| Sensor names changed between visits | In some recordings the eye sensor was #26 instead of #25, and names were spelled "EEG E1" instead of "E1". Numbers were landing in the wrong columns, and one recording crashed | Rename everything to one standard and place every sensor in one fixed order |
| A crash would stop the whole run | One odd recording could halt everything | Odd recordings are now skipped and listed, as the plan says |

The last two only appeared when we ran all 20 visits per person. With only 4 visits, they were hidden. That is why the full practice run was worth the extra hours.

## The answer from the real test (23 October)

**The verdict: failure, with a real but tiny effect.** We ran the frozen code on the 20 test people. The rule we wrote before the test says a gain only counts if it is at least 0.01. The average gain from adding brain signals was **0.005**, and the likely range the rule uses was 0.003 to 0.008. That whole range sits below 0.01, so the rule says **failure**. Because the range also stays above zero, the rule adds the label **"present but negligible"**: the effect is real, just too small to matter by the standard we set in advance.

**In everyday terms.** Without brain signals, the computer guesses which words a person will remember with a score of about 0.64 to 0.69 (0.5 is a coin flip). Adding brain signals moved that by about half of one hundredth on average. 17 of the 20 people had some gain, but only 2 reached 0.01, and for one of those two the eye sensors alone gave the same gain.

**What the checks showed.**

- **Eyes:** the eye sensors alone gave about half the gain (0.0025 of 0.005). The brain sensors still did a little better than eyes alone, so not all of it is eye movement.
- **This word, not general alertness:** brain signals from the *previous* word added nothing (−0.0001), while signals from the word itself added 0.005. So the small gain is tied to learning that particular word. The practice run had hinted the opposite; with 20 people it did not hold.
- **Cleaner signals only** (slow waves only, edge sensors removed, to cut out muscle noise): the gain was smaller but still above zero (likely range 0.002 to 0.006).
- **Leaving out the lists where people pressed a button for each word** (to rule out hand movements): average gain 0.008, still below 0.01. This was a side check, not part of the rule.

**Side questions** (two of them, with the usual correction for asking more than one question):

- **Is the brain signal personal?** A brain model trained on the person themself beat one trained on other people in 19 of 20 people (score 0.56 against 0.54 on average). This is the first small sign in real data for the "personal" part of your idea.
- **Does it also track how well a word is recognised later?** Yes, the brain signal added a little here too, beyond the word facts (clear statistically, small in size).

On its own, the brain signal guessed better than chance for 19 of the 20 people (scores 0.53 to 0.61). So the brain signal does carry memory information; it just overlaps a lot with what the simple word facts already tell us.

**Things that differed from the plan.** 5 visits had duplicate time stamps in their records and were skipped automatically. That skip reason was not in the registered list, so it is reported openly as a deviation. 4 people simply had fewer than 20 visits in the dataset (12 to 19).

**What it means for your idea.** Scalp EEG during learning holds real information about which words will be remembered. That information belongs to the specific word and is somewhat personal. But on top of simple facts about the word and the list, it adds too little to be useful on its own. This is the "Failure" case described below, written before the test: it points toward better signals (recordings from inside the brain) or toward helping memory with cues and reminders.

**What could come next (your choice).**

1. Repeat on the in-brain recordings dataset, where signals are much cleaner. This tests whether the small effect grows with better sensors.
2. Repeat on the second PEERS experiment, to check that today's answer holds in new people.
3. Write up this result as it stands. A pre-registered "no" with a precise size is a useful, publishable result.

All numbers and files are in the project folder `memory-fingerprint/confirmatory/`.

## Before the real test: what we knew on 22 October

**What we know.**

- The analysis works from start to finish on 60 real recordings, and the automatic tests (38 of them) pass.
- Without any brain signals, a computer predicts which words someone will remember quite well (score 0.64 to 0.69, where 0.5 is a coin flip).

**What the practice run hinted (only 3 people, so treat as a hint, not a finding).**

- For 2 of the 3 people, brain signals added nothing.
- For the third, they added a clear gain (0.041). But about half of it could also be got from the eye sensors alone, and about half from the brain signals of the *previous* word. That suggests some of it is eye movements and general alertness rather than the brain storing that particular word.

**What we do not know yet.** Whether brain signals help for most people. Whether any help comes from storing the specific word. Anything about whether memories come back as the same pattern, or are personal like a fingerprint. Those are the later steps of your idea, and nothing so far tests them.

**What happens next.**

1. **You:** read the pre-registration draft, post it on OSF, and send me the link.
2. **Me:** run the analysis on the 20 test people (about 12 to 15 hours of computing).
3. **Me:** report the answer exactly as the pre-written rules give it, including all the checks for eyes, muscles, button presses and alertness.

**How to read the answer when it comes.**

- *Success and the checks pass:* brain signals at learning carry real memory information for individuals. Your idea's foundation holds. The next experiment would test whether the signal is specific to the item and comes back during recall.
- *Success, but the eyes or the previous word do as well:* the number is real, but it is probably not a memory trace. The fingerprint idea would need better signals (for example the in-brain recordings dataset).
- *Failure:* scalp EEG adds too little to matter. That is still a useful, publishable answer. It would point toward better sensors, or toward helping memory through cues and reminders, which the original report found much better supported.

## Word list

| Term | Plain meaning |
| --- | --- |
| AUC | A score for predictions: 0.5 = coin flip, 1.0 = perfect. It asks how often a remembered word is ranked above a forgotten one |
| Artefact | A signal in the recording that is not brain activity (eyes, muscles, movement) |
| Baseline / without-brain model | The best prediction we can make using facts about the word only, no brain data |
| Bootstrap | A way to estimate uncertainty by re-running the calculation many times on reshuffled samples of the data |
| Checksum | A digital fingerprint of a file. If even one character changes, the fingerprint changes |
| Confidence interval (CI) | A range that probably contains the true value. Narrow = we are fairly sure |
| Cross-validation | Training on part of the data and testing on the part that was hidden |
| Data leakage | When information from the test data sneaks into training, making results look better than they are |
| EEG | Recording the brain's electrical activity with sensors on the scalp |
| Electrode / sensor | One of the 129 small contacts on the EEG cap |
| Encoding | Storing something in memory |
| EOG | Sensors placed near the eyes to record eye movements and blinks |
| Free recall | Saying aloud every word you remember, in any order |
| Frequency / rhythm | How fast a brain signal goes up and down, in cycles per second (Hz) |
| Hypothesis | A precise statement that a test can prove wrong |
| Model | A formula a computer learns from examples, used to make predictions |
| OpenNeuro | A free public website where scientists share brain recordings |
| OSF | Open Science Framework, a free website where researchers publish pre-registrations |
| PEERS | The memory study whose recordings we use (University of Pennsylvania) |
| Pilot | A practice run on a few people to check the method, not counted in the result |
| Pre-registration | Publishing your plan and success rules before running the test |
| Retrieval | Getting a memory back |
| Session / visit | One day's recording in the lab |
| SESOI (0.01) | The smallest gain we decided in advance would matter |
| Stacked model | A two-step model: brain data first become one score, which is then combined with word facts |
| Subsequent memory effect | The known finding that brain activity during learning differs, on average, for things later remembered |
| Wilcoxon test | A standard statistical test of whether values across people are reliably above zero |
