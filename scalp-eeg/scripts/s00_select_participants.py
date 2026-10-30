"""Stage 0: download every ltpFR event file and apply the participant selection rule.

Downloads about 3,600 small files (roughly 550 MB). No EEG is downloaded.
Prints the eligible IDs and checks them against config.PILOT_IDS / CONFIRMATORY_IDS.

    python scripts/s00_select_participants.py
"""
import re
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from pnms import config
from pnms.behaviour import select_participants
from pnms.download import fetch, list_files
from pnms.events import load_events, study_table


def main():
    files = list_files(f"{config.DATASET_ID}/sub-")
    events = [f for f in files if re.search(rf"/eeg/.*task-{config.TASK}_events\.tsv$", f.key)]
    eeg = [f for f in files if re.search(rf"/eeg/.*task-{config.TASK}_eeg\.(edf|bdf)$", f.key)]
    print(f"{len(events)} ltpFR event files, {len(eeg)} ltpFR EEG files")

    with ThreadPoolExecutor(16) as pool:
        paths = list(pool.map(fetch, events))

    rows = []
    for p in paths:
        m = re.search(r"sub-(\w+?)_ses-(\d+)_task-(\w+?)_events", p.name)
        w = study_table(load_events(p))
        rows.append(dict(sub=m[1], ses=int(m[2]), task=m[3], n_words=len(w), recall=w["recalled"].mean()))
    summary = pd.DataFrame(rows)
    config.DERIV_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(config.DERIV_DIR / "session_summary.csv", index=False)

    ext = {}
    for f in eeg:
        sub = re.search(r"sub-(\w+?)/", f.key)[1]
        ext.setdefault(sub, set()).add(f.key.rsplit(".", 1)[1])
    edf_only = {s for s, e in ext.items() if e == {config.EEG_EXTENSION.strip('.')}}

    eligible = select_participants(summary, edf_only)
    print(f"eligible participants: {len(eligible)}")
    pilot, confirm = eligible[:config.N_PILOT], eligible[config.N_PILOT:config.N_PILOT + config.N_CONFIRMATORY]
    print("pilot:", pilot)
    print("confirmatory:", confirm)
    if tuple(pilot) != config.PILOT_IDS or tuple(confirm) != config.CONFIRMATORY_IDS:
        raise SystemExit("Selection differs from the IDs fixed in config.py. Stop and investigate "
                         "(dataset version change?) before running any EEG analysis.")
    print("Selection matches the pre-registered IDs.")


if __name__ == "__main__":
    main()
