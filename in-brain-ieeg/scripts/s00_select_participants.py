"""Stage 0: download every FR1 event file and apply the participant selection rule.

Downloads only the small event files (no iEEG). Eligible = at least
config.MIN_SESSIONS sessions that have both an events file and a bipolar EDF, with
mean recall inside config.RECALL_RANGE. Eligible IDs (ascending) are shuffled with
config.SELECTION_SEED; the first N_PILOT are the pilot and the next N_CONFIRMATORY
the confirmatory sample. If config.PILOT_IDS is filled in, the script checks that
the rule still reproduces it.

    python scripts/s00_select_participants.py
"""
import json
import re
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd

from pnms import config
from pnms.download import fetch, list_files
from pnms.events import SchemaError, load_events, study_table


def main():
    files = list_files(f"{config.DATASET_ID}/sub-")
    events = [f for f in files if re.search(rf"/ieeg/.*task-{config.TASK}_events\.tsv$", f.key)]
    edf = {re.search(r"sub-(\w+?)_ses-(\d+)_", f.key).groups() for f in files
           if re.search(rf"/ieeg/.*task-{config.TASK}_acq-{config.ACQ}_ieeg\.edf$", f.key)}
    print(f"{len(events)} {config.TASK} event files, {len(edf)} sessions with a {config.ACQ} EDF")

    with ThreadPoolExecutor(16) as pool:
        paths = list(pool.map(fetch, events))

    rows = []
    for p in paths:
        sub, ses = re.search(r"sub-(\w+?)_ses-(\d+)_", p.name).groups()
        try:
            w = study_table(load_events(p))
            rows.append(dict(sub=sub, ses=int(ses), task=config.TASK, n_words=len(w), recall=w["recalled"].mean(),
                             has_edf=(sub, ses) in edf, status="ok"))
        except SchemaError as err:
            rows.append(dict(sub=sub, ses=int(ses), task=config.TASK, n_words=0, recall=np.nan,
                             has_edf=(sub, ses) in edf, status=f"schema: {err}"))
    summary = pd.DataFrame(rows).sort_values(["sub", "ses"])
    config.DERIV_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(config.DERIV_DIR / "session_summary.csv", index=False)
    print(summary["status"].value_counts().to_string())

    s = summary[(summary["status"] == "ok") & summary["has_edf"]]
    agg = s.groupby("sub").agg(n=("ses", "size"), rec=("recall", "mean"))
    lo, hi = config.RECALL_RANGE
    eligible = sorted(agg[(agg["n"] >= config.MIN_SESSIONS) & (agg["rec"] > lo) & (agg["rec"] < hi)].index)
    order = [str(x) for x in np.random.default_rng(config.SELECTION_SEED).permutation(eligible)]
    pilot, confirm = order[:config.N_PILOT], order[config.N_PILOT:config.N_PILOT + config.N_CONFIRMATORY]
    print(f"eligible participants: {len(eligible)}")
    print("pilot:", [str(x) for x in pilot])
    print("confirmatory:", [str(x) for x in confirm])
    (config.DERIV_DIR / "selection.json").write_text(json.dumps(
        {"eligible": eligible, "pilot": pilot, "confirmatory": confirm}, indent=1))
    if config.PILOT_IDS and (tuple(pilot) != config.PILOT_IDS or tuple(confirm) != config.CONFIRMATORY_IDS):
        raise SystemExit("Selection differs from the IDs fixed in config.py. Stop and investigate.")


if __name__ == "__main__":
    main()
