# Memory Fingerprint

Can a model trained on **one person's own brain recordings** tell whether a memory is being stored well? This repository holds every step of an open, pre-registered attempt to find out, using only a computer and free public data.

The long-term idea is a *Personalized Neural Memory Signature* (PNMS): a personal model of what your brain activity looks like when a memory is stored or recalled, which one day might help people with memory problems (for example mild cognitive impairment). That long-term use is **speculation**. What is here is the measurement work that has to come first.

## Results so far

| Test | Data | Status | Verdict by the frozen rule |
| --- | --- | --- | --- |
| Scalp EEG at study predicts later recall | PEERS ltpFR, 20 people ([OpenNeuro ds004395](https://openneuro.org/datasets/ds004395)) | Done 23 Oct 2026, pre-registered at [osf.io/9ghzn](https://osf.io/9ghzn/overview) | **Failure: present but negligible** |
| Same test with electrodes inside the brain | RAM FR1 iEEG, 20 people ([OpenNeuro ds004789](https://openneuro.org/datasets/ds004789)) | Running, addendum registered at [osf.io/xn4v9](https://osf.io/xn4v9) | Pending |
| Is the signal personal and stable? (exploratory) | Same 23 PEERS people | Done 23 Oct 2026, not pre-registered | Hints only |

**Scalp EEG, in numbers.** The score used is AUC (0.5 = coin flip, 1.0 = perfect). Adding brain data to a strong non-brain model raised it by a mean ΔAUC of **0.005** (95% CI 0.002 to 0.009; one-sided Wilcoxon p = 5×10⁻⁵). The pre-set smallest useful gain was 0.01, so the effect is real but too small. Other checks:

- Eye channels alone gave about half the gain (0.0025).
- The previous word's EEG gave about 0, so the gain is tied to the word being studied.
- A personal model beat a model pooled across other people in 19 of 20 people (AUC 0.562 vs 0.537; Holm-corrected p = 0.0002).
- Deviation from the plan: 5 sessions were skipped for duplicate event times.

**Exploratory (treat as hints).**

- A person's memory map from half their sessions picked them out from the other half in 13 of 23 cases. A shuffled-label control did this about 20% of the time.
- Models trained on recent sessions beat models trained on early sessions in 20 of 23 people (by 0.021 AUC), so the signal drifts over time.
- Training on 1, 2, 4, 8 and 16 sessions gave AUC 0.524, 0.523, 0.547, 0.552 and 0.561.

## What is in this repository

```
docs/                      every write-up, as Markdown, in reading order
  00-idea-document.md        the whole idea in plain words: feasibility, next steps, contacts, funding
  01-plain-language-guide.md the project explained from zero
  02-progress-log.md         every step, in order, with the reason for it
  03-research-report.md      the original 22-section research report (hypotheses H1 to H8)
  04-dataset-selection.md    why PEERS, what was checked in the real files
  05-build-guide.md          how the first experiment's code works
  06-experiment-audit.md     a sceptical audit of the first experiment
  07-preregistration-scalp-eeg.md
  08-roadmap.md              seven sub-projects after the first test
  09-preregistration-addendum-ieeg.md
scalp-eeg/                 first experiment code (Python package `pnms`), tests, results
  confirmatory/              the real 20-person results, per-person model outputs, log
  pilot_check*/              practice-run outputs (code checks, not results)
  FROZEN_SHA256.txt          checksums of the code as frozen on 22 Oct 2026
in-brain-ieeg/             the same test adapted to intracranial recordings, frozen 23 Oct 2026
exploratory-sp3/           fingerprint, stability and data-needed side tests
frozen/                    the exact zips attached to the OSF registrations
```

The code inside `scalp-eeg/` and `in-brain-ieeg/` is the frozen code, byte for byte, and can be checked against each folder's `FROZEN_SHA256.txt`. The docs were written as live documents and contain links to their private originals; the Markdown copies here are complete.

## Reproduce it

Each code folder is its own installable package. Python 3.11 or newer is needed, and the exact versions are pinned in `pyproject.toml`.

```bash
cd scalp-eeg            # or in-brain-ieeg
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
pytest -q               # no download needed
```

Then follow the stages in that folder's `README.md`. The data are downloaded from OpenNeuro's public storage with no account. One session is processed at a time and the raw file is deleted afterwards, so you do not need terabytes of disk. A full 20-person run takes roughly 10 to 15 hours on 4 CPU cores. `run_scripts/` holds the exact shell scripts used for the real runs; their paths point to the machine they ran on.

## Ground rules this project follows

- Never invent citations, results, file paths, column names or dataset schemas: every one was read from the real files.
- Only public data and open-source tools. No new data collection.
- Freeze the code and register the success rule publicly **before** each real test, and report the verdict exactly as the rule gives it.
- Any change after a freeze is reported next to the frozen result.
- Ethics and regulation are considered for Sweden and the EU.

## Licence

The code is released under the MIT licence (see `LICENSE`). The datasets belong to their authors and are CC0 on OpenNeuro.
